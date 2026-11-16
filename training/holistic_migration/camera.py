"""Strict built-in AVFoundation pipe boundary; imports never access a camera."""
import re
import json
import math
import struct
import time


def _unique_object(pairs):
    value = {}
    for key, item in pairs:
        if key in value:
            raise ValueError("duplicate handshake key")
        value[key] = item
    return value


class PacketReader:
    """read(n, absolute_deadline) must be bounded; no buffering beyond one frame."""

    def __init__(self, read):
        self.read = read
        self.metadata = None
        self.last_timestamp = None

    def exact(self, size, deadline):
        data = bytearray()
        while len(data) < size:
            if time.monotonic() >= deadline:
                raise TimeoutError("native pipe deadline exceeded")
            chunk = self.read(size - len(data), deadline)
            if not chunk:
                raise EOFError("unexpected native pipe EOF")
            if len(chunk) > size - len(data):
                raise ValueError("pipe reader exceeded requested size")
            data.extend(chunk)
        return bytes(data)

    def handshake(self, deadline):
        line = bytearray()
        while len(line) < 4096:
            byte = self.exact(1, deadline)
            if byte == b"\n":
                try:
                    value = json.loads(line, object_pairs_hook=_unique_object)
                except (UnicodeError, json.JSONDecodeError) as error:
                    raise ValueError("malformed handshake JSON") from error
                self.metadata = validate_handshake(value)
                return self.metadata
            line.extend(byte)
        raise ValueError("oversized native handshake")

    def frame(self, deadline):
        if self.metadata is None:
            raise ValueError("handshake required before frames")
        timestamp, size = struct.unpack(">dI", self.exact(12, deadline))
        if (not math.isfinite(timestamp) or not 0 <= timestamp <= 2**53
                or not timestamp.is_integer()
                or (self.last_timestamp is not None and timestamp <= self.last_timestamp)):
            raise ValueError("nonfinite/nonintegral/regressing native timestamp")
        if size != self.metadata["frame_bytes"]:
            raise ValueError("native frame length/reconfiguration rejected")
        payload = self.exact(size, deadline)
        self.last_timestamp = int(timestamp)
        return int(timestamp), payload

BUILTIN_TYPE = "AVCaptureDeviceTypeBuiltInWideAngleCamera"
MAX_FRAME_BYTES = 4096 * 2160 * 4


def validate_handshake(value):
    """Admit actual tightly packed BGRA metadata before any detector work."""
    if not isinstance(value, dict):
        raise ValueError("handshake must be an object")
    if (type(value.get("protocol")) is not int or value["protocol"] != 1
            or value.get("device_type") != BUILTIN_TYPE
            or value.get("continuity") is not False
            or not isinstance(value.get("device_sha256"), str)
            or re.fullmatch(r"[0-9a-f]{64}", value["device_sha256"]) is None
            or value.get("pixel_format") != "BGRA"):
        raise ValueError("unsupported protocol, camera identity or pixel format")
    width, height, size = (value.get(k) for k in ("width", "height", "frame_bytes"))
    if (any(type(x) is not int for x in (width, height, size))
            or not 1 <= width <= 4096 or not 1 <= height <= 2160
            or size != width * height * 4 or size > MAX_FRAME_BYTES):
        raise ValueError("unsupported actual dimensions/BGRA size")
    return dict(value)


# Only build artifacts and digest receipts are persisted, never frame data.
import hashlib
import os
from pathlib import Path
import subprocess
import uuid
from dataclasses import dataclass

SCRATCH = Path.home() / ".hermes/cache/scratch"
REPOSITORY = Path(__file__).resolve().parents[2]


def external_directory(path):
    if not isinstance(path, Path) or not path.is_absolute():
        raise ValueError("build directory must be an absolute external Path")
    resolved = path.resolve()
    forbidden = (REPOSITORY, Path.home() / "Documents", Path.home() / "Desktop",
                 Path.home() / "Library/Mobile Documents")
    if any(resolved == root or resolved.is_relative_to(root) for root in forbidden):
        raise ValueError("build directory must be outside repository/cloud directories")
    if resolved.exists() and not resolved.is_dir():
        raise ValueError("build directory is not a directory")
    return resolved


def digest(path):
    hasher = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


@dataclass(frozen=True)
class NativeBinding:
    source: Path
    binary: Path
    receipt: Path
    source_sha256: str
    binary_sha256: str


def build_helper(build_dir, runner=subprocess.run):
    root = external_directory(build_dir)
    source = Path(__file__).with_suffix(".swift").resolve()
    source_hash = digest(source)
    build = root / ("native-" + uuid.uuid4().hex)
    build.mkdir(parents=True, exist_ok=False)
    SCRATCH.mkdir(parents=True, exist_ok=True)
    cache = SCRATCH / "task-b-swift-module-cache"
    cache.mkdir(exist_ok=True)
    binary = build / "builtin-camera"
    command = ["/usr/bin/swiftc", "-O", "-module-cache-path", str(cache),
               str(source), "-o", str(binary)]
    env = os.environ.copy()
    env["TMPDIR"] = str(SCRATCH)
    attempt = dict(command=command, tmpdir=str(SCRATCH), source_sha256=source_hash,
                   terminal="interrupted", exit=None)
    stdout = stderr = b""
    try:
        result = runner(command, env=env, capture_output=True, timeout=120, check=False)
        stdout, stderr = result.stdout, result.stderr
        attempt.update(terminal="completed", exit=result.returncode)
    except subprocess.TimeoutExpired as error:
        stdout, stderr = error.stdout or b"", error.stderr or b""
        attempt["terminal"] = "timeout"
        raise RuntimeError(f"Swift compilation timed out; attempt retained in {build}") from error
    except OSError as error:
        attempt["terminal"] = "spawn_error"
        stderr = str(error).encode(errors="replace")
        raise
    finally:
        (build / "compile.stdout").write_bytes(stdout)
        (build / "compile.stderr").write_bytes(stderr)
        (build / "compile.json").write_text(json.dumps(attempt, sort_keys=True) + "\n")
    if result.returncode != 0:
        raise RuntimeError(f"Swift compilation exit {result.returncode}; {build / 'compile.stderr'}: "
                           + result.stderr.decode(errors="replace")[-8192:])
    if digest(source) != source_hash:
        raise ValueError("native source changed during compilation")
    binary_hash = digest(binary)
    receipt = build / "binding.json"
    receipt.write_text(json.dumps(dict(schema=1, source=str(source), source_sha256=source_hash,
                                      binary=str(binary), binary_sha256=binary_hash,
                                      command=command, tmpdir=str(SCRATCH)), sort_keys=True) + "\n")
    binding = NativeBinding(source, binary, receipt, source_hash, binary_hash)
    verify_binding(binding)
    return binding


def verify_binding(binding):
    source = Path(__file__).with_suffix(".swift").resolve()
    try:
        receipt = json.loads(binding.receipt.read_text())
        if (binding.source != source or binding.binary.is_symlink()
                or binding.receipt.is_symlink() or not os.access(binding.binary, os.X_OK)
                or digest(source) != binding.source_sha256
                or digest(binding.binary) != binding.binary_sha256
                or receipt.get("source") != str(source)
                or receipt.get("binary") != str(binding.binary)
                or receipt.get("source_sha256") != binding.source_sha256
                or receipt.get("binary_sha256") != binding.binary_sha256
                or receipt.get("schema") != 1
                or receipt.get("command", [None])[0] != "/usr/bin/swiftc"
                or str(source) not in receipt["command"]):
            raise ValueError("native source/binary binding mismatch")
        external_directory(binding.binary.parent)
    except (OSError, KeyError, TypeError, json.JSONDecodeError) as error:
        raise ValueError("invalid native binding receipt") from error
    return binding


import select
import threading


class CaptureError(RuntimeError):
    """A bounded native source failed; diagnostics exclude frame stdout."""


class OwnedCapture:
    """Exactly one child, one pending frame, bounded stderr; no auto-restart."""

    def __init__(self, binding, *, duration, startup_timeout=10.0, frame_timeout=3.0,
                 shutdown_timeout=.75, popen=subprocess.Popen):
        for name, value, maximum in (("duration", duration, 300),
                                     ("startup_timeout", startup_timeout, 30),
                                     ("frame_timeout", frame_timeout, 30),
                                     ("shutdown_timeout", shutdown_timeout, 5)):
            if isinstance(value, bool) or not math.isfinite(value) or not 0 < value <= maximum:
                raise ValueError(f"invalid {name}")
        verify_binding(binding)
        self.frame_timeout = frame_timeout
        self.shutdown_timeout = shutdown_timeout
        self.condition = threading.Condition()
        self.stop = threading.Event()
        self.pending = None
        self.error = None
        self.received = self.dropped = 0
        self.stderr_tail = b""
        self.reader_thread = self.stderr_thread = None
        self._exit_before_shutdown = None
        self._closed = False
        env = os.environ.copy()
        env["TMPDIR"] = str(SCRATCH)
        self.process = popen([str(binding.binary), "--capture", str(duration)],
                             stdin=subprocess.DEVNULL, stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE, bufsize=0, env=env)
        try:
            self.stderr_thread = threading.Thread(target=self._drain_stderr, daemon=True,
                                                  name="owned-camera-stderr")
            self.stderr_thread.start()
            self.reader = PacketReader(self._read)
            self.metadata = self.reader.handshake(time.monotonic() + startup_timeout)
            self.reader_thread = threading.Thread(target=self._frames, daemon=True,
                                                  name="owned-camera-frames")
            self.reader_thread.start()
        except BaseException as error:
            rollback_error = None
            try:
                self.close()
            except BaseException as failure:
                rollback_error = failure
            failure = CaptureError(self.diagnostic(error))
            if rollback_error is not None:
                failure.add_note(f"owned capture rollback: {type(rollback_error).__name__}: {rollback_error}")
                for note in getattr(rollback_error, "__notes__", ()):
                    failure.add_note(note)
            raise failure from error

    def _read(self, size, deadline):
        while not self.stop.is_set():
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                raise TimeoutError("native pipe deadline exceeded")
            ready, _, _ = select.select([self.process.stdout], [], [], min(remaining, .05))
            if ready:
                return os.read(self.process.stdout.fileno(), size)
        raise EOFError("owned source closed")

    def _drain_stderr(self):
        try:
            while True:
                chunk = os.read(self.process.stderr.fileno(), 4096)
                if not chunk:
                    break
                self.stderr_tail = (self.stderr_tail + chunk)[-16384:]
        except (OSError, ValueError):
            pass

    def _frames(self):
        try:
            while not self.stop.is_set():
                frame = self.reader.frame(time.monotonic() + self.frame_timeout)
                with self.condition:
                    self.received += 1
                    if self.pending is not None:
                        self.dropped += 1
                    self.pending = frame
                    self.condition.notify_all()
        except BaseException as error:
            with self.condition:
                if not self.stop.is_set():
                    self.error = error
                self.condition.notify_all()

    def diagnostic(self, error):
        return (f"{type(error).__name__}: {error}; native exit={self.process.poll()}; stderr tail="
                + self.stderr_tail.decode(errors="replace"))

    def next_frame(self, deadline):
        with self.condition:
            while self.pending is None and self.error is None and not self.stop.is_set():
                remaining = deadline - time.monotonic()
                if remaining <= 0:
                    raise TimeoutError("preview frame wait deadline exceeded")
                self.condition.wait(min(remaining, .05))
            if self.error is not None:
                raise CaptureError(self.diagnostic(self.error)) from self.error
            if self.stop.is_set():
                raise CaptureError("owned source closed")
            frame, self.pending = self.pending, None
            return frame

    def raise_if_failed(self):
        """Reconcile fatal source errors even when no further frame is requested."""
        if self.error is not None:
            raise CaptureError(self.diagnostic(self.error)) from self.error
        native_exit = self._exit_before_shutdown if self.stop.is_set() else self.process.poll()
        if native_exit is not None:
            raise CaptureError(self.diagnostic(
                RuntimeError(f"unexpected native exit before owned shutdown ({native_exit})")))

    def close(self):
        if self._closed:
            return
        teardown_errors = []
        with self.condition:
            # Freeze the source state before our own terminate/kill can change it.
            if not self.stop.is_set():
                self._exit_before_shutdown = self.process.poll()
                self.stop.set()
            self.pending = None
            self.condition.notify_all()
        try:
            if self.process.poll() is None:
                try:
                    self.process.terminate()
                except ProcessLookupError:
                    pass
            try:
                self.process.wait(timeout=self.shutdown_timeout)
            except subprocess.TimeoutExpired:
                self.process.kill()
                self.process.wait(timeout=self.shutdown_timeout)
        finally:
            for thread in (self.reader_thread, self.stderr_thread):
                # A constructed Thread is not acquired until it actually starts.
                if thread is not None and thread.ident is not None:
                    try:
                        thread.join(timeout=self.shutdown_timeout + .1)
                        if thread.is_alive():
                            raise TimeoutError(f"owned capture thread did not stop: {thread.name}")
                    except BaseException as error:
                        teardown_errors.append(error)
            for pipe in (self.process.stdout, self.process.stderr):
                if pipe is not None and not pipe.closed:
                    try:
                        pipe.close()
                    except BaseException as error:
                        teardown_errors.append(error)
        if teardown_errors:
            primary = teardown_errors[0]
            for error in teardown_errors[1:]:
                primary.add_note(f"additional owned capture teardown: {type(error).__name__}: {error}")
            raise primary
        self._closed = True

    def __enter__(self):
        return self

    def __exit__(self, *exception):
        self.close()
        return False
