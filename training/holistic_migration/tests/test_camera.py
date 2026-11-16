"""No camera/GUI/MediaPipe access; exercise the production wire boundary."""
import io
import json
import struct
import time
import os
from pathlib import Path
import subprocess
import tempfile
from dataclasses import replace
import unittest

from training.holistic_migration import camera


def handshake(**changes):
    value = dict(protocol=1, width=1280, height=720, pixel_format="BGRA",
                 frame_bytes=1280 * 720 * 4,
                 device_type="AVCaptureDeviceTypeBuiltInWideAngleCamera",
                 continuity=False, device_sha256="a" * 64)
    value.update(changes)
    return value


class HandshakeTests(unittest.TestCase):
    def test_actual_bgra_dimensions_and_builtin_identity_are_admitted(self):
        value = handshake(width=640, height=480, frame_bytes=640 * 480 * 4)
        self.assertEqual(camera.validate_handshake(value), value)

    def test_ambiguous_or_nonbuiltin_metadata_is_rejected(self):
        for changes in [dict(device_type="AVCaptureDeviceTypeContinuityCamera"),
                        dict(device_type="external"), dict(continuity=True),
                        dict(continuity=0), dict(device_sha256=""),
                        dict(device_sha256="g" * 64), dict(width=True),
                        dict(width=8192), dict(height=0), dict(protocol=True),
                        dict(pixel_format="RGB"), dict(frame_bytes=1)]:
            with self.subTest(changes=changes), self.assertRaises(ValueError):
                camera.validate_handshake(handshake(**changes))
        with self.assertRaises(ValueError):
            camera.validate_handshake({})


class PacketTests(unittest.TestCase):
    def reader(self, data, chunk=3):
        stream = io.BytesIO(data)
        return camera.PacketReader(lambda n, deadline: stream.read(min(n, chunk)))

    def test_partial_reads_actual_handshake_and_exact_frame(self):
        meta = handshake(width=2, height=1, frame_bytes=8)
        wire = json.dumps(meta).encode() + b"\n" + struct.pack(">dI", 12.0, 8) + b"12345678"
        reader = self.reader(wire)
        self.assertEqual(reader.handshake(time.monotonic() + 1), meta)
        self.assertEqual(reader.frame(time.monotonic() + 1), (12, b"12345678"))
        with self.assertRaises(EOFError):
            reader.frame(time.monotonic() + 1)

    def test_short_oversized_and_invalid_timestamps_fail_closed(self):
        for data in [b"", b"x" * 11, struct.pack(">dI", 0.0, 9),
                     struct.pack(">dI", 0.0, 8) + b"short",
                     struct.pack(">dI", float("nan"), 8) + b"12345678",
                     struct.pack(">dI", float("inf"), 8) + b"12345678",
                     struct.pack(">dI", -1.0, 8) + b"12345678",
                     struct.pack(">dI", 0.5, 8) + b"12345678"]:
            with self.subTest(data=data):
                reader = self.reader(data)
                reader.metadata = handshake(width=2, height=1, frame_bytes=8)
                with self.assertRaises((ValueError, EOFError)):
                    reader.frame(time.monotonic() + 1)

    def test_repeated_or_regressing_timestamp_and_startup_limits(self):
        for timestamp in (10, 9):
            reader = self.reader(struct.pack(">dI", timestamp, 8) + b"12345678")
            reader.metadata = handshake(width=2, height=1, frame_bytes=8)
            reader.last_timestamp = 10
            with self.assertRaises(ValueError):
                reader.frame(time.monotonic() + 1)
        for data in (b"x" * 4097, b"{}\n", b"not json\n", b"{\"width\":1,\"width\":2}\n"):
            with self.subTest(data=data[:30]), self.assertRaises((ValueError, EOFError)):
                self.reader(data).handshake(time.monotonic() + 1)
        with self.assertRaises(TimeoutError):
            self.reader(b"anything").handshake(time.monotonic() - 1)


class NativeBindingTests(unittest.TestCase):
    def test_exact_source_compiles_and_pure_native_checks_need_no_camera(self):
        root = Path.home() / ".hermes/cache/scratch"
        with tempfile.TemporaryDirectory(dir=root, prefix="task-b-native-test-") as directory:
            binding = camera.build_helper(Path(directory))
            camera.verify_binding(binding)
            receipt = json.loads(binding.receipt.read_text())
            self.assertEqual(receipt["source"], str(Path(camera.__file__).with_suffix(".swift")))
            self.assertEqual(receipt["command"][0], "/usr/bin/swiftc")
            self.assertIn("-module-cache-path", receipt["command"])
            self.assertTrue(Path(receipt["tmpdir"]).is_relative_to(root))
            result = subprocess.run([str(binding.binary), "--self-test"],
                                    capture_output=True, timeout=10, check=True)
            self.assertEqual(json.loads(result.stdout), {
                "status": "ok", "checks": ["selection", "row-padding", "framing", "reconfiguration", "timestamps"],
                "camera_access": False})
            with self.assertRaises(ValueError):
                camera.verify_binding(replace(binding, source_sha256="0" * 64))
            binding.binary.write_bytes(b"tampered")
            with self.assertRaises(ValueError):
                camera.verify_binding(binding)

    def test_build_rejects_relative_or_repository_directory_before_compiler(self):
        for directory in (Path("relative"), Path(camera.__file__).parent):
            with self.subTest(directory=directory), self.assertRaises(ValueError):
                camera.build_helper(directory, runner=lambda *a, **k: self.fail("compiler called"))


class BuildFailureTests(unittest.TestCase):
    def test_compiler_timeout_keeps_partial_stdout_stderr_and_command(self):
        root=Path.home()/".hermes/cache/scratch"
        with tempfile.TemporaryDirectory(dir=root,prefix="task-b-build-failure-") as folder:
            def timeout(command, **kwargs):
                raise subprocess.TimeoutExpired(command, 120, output=b"partial compiler stdout",stderr=b"partial compiler stderr")
            with self.assertRaises(RuntimeError):
                camera.build_helper(Path(folder),runner=timeout)
            build=next(Path(folder).glob("native-*"))
            self.assertEqual((build/"compile.stdout").read_bytes(),b"partial compiler stdout")
            self.assertEqual((build/"compile.stderr").read_bytes(),b"partial compiler stderr")
            attempt=json.loads((build/"compile.json").read_text())
            self.assertEqual(attempt["terminal"],"timeout")
            self.assertEqual(attempt["command"][0],"/usr/bin/swiftc")
            self.assertFalse((build/"binding.json").exists())


class CaptureTests(unittest.TestCase):
    def factory(self, code):
        import sys
        def spawn(*args, **kwargs):
            return subprocess.Popen([sys.executable, "-E", "-B", "-c", code], **kwargs)
        return spawn

    def capture(self, code, **options):
        from unittest.mock import patch
        with patch.object(camera, "verify_binding"):
            return camera.OwnedCapture(type("Binding", (), {"binary": Path("/unused")})(),
                                       duration=2, popen=self.factory(code),
                                       startup_timeout=.3, frame_timeout=.4, **options)

    def test_latest_only_queue_and_owned_child_cleanup(self):
        meta = handshake(width=2, height=1, frame_bytes=8)
        code = ("import sys,time,struct,json; "
                f"sys.stdout.buffer.write({json.dumps(meta).encode()!r}+b'\\n'); "
                "sys.stdout.buffer.flush(); "
                "[(sys.stdout.buffer.write(struct.pack('>dI',float(i),8)+bytes([i])*8),"
                "sys.stdout.buffer.flush()) for i in range(1,21)]; time.sleep(10)")
        capture = self.capture(code)
        child = capture.process
        try:
            deadline = time.monotonic() + .3
            while capture.received < 20 and time.monotonic() < deadline:
                time.sleep(.005)
            self.assertEqual(capture.next_frame(time.monotonic()+.2), (20, bytes([20])*8))
            self.assertEqual(capture.dropped, 19)
            with self.assertRaises(TimeoutError):
                capture.next_frame(time.monotonic()+.01)
        finally:
            capture.close(); capture.close()
        self.assertIsNotNone(child.poll())
        self.assertFalse(capture.reader_thread.is_alive())
        self.assertFalse(capture.stderr_thread.is_alive())

    def test_startup_eof_timeout_and_stderr_are_preserved(self):
        for code in ("import sys;sys.stderr.write('specific failure');sys.exit(7)",
                     "import time;time.sleep(10)"):
            with self.subTest(code=code):
                children = []
                spawn = self.factory(code)
                def factory(*args, **kwargs):
                    child = spawn(*args, **kwargs); children.append(child); return child
                from unittest.mock import patch
                with patch.object(camera, "verify_binding"), self.assertRaises(camera.CaptureError) as caught:
                    camera.OwnedCapture(type("Binding", (), {"binary": Path("/unused")})(),
                                        duration=2, popen=factory, startup_timeout=.05)
                self.assertIsNotNone(children[0].poll())
                if "specific" in code:
                    self.assertIn("specific failure", str(caught.exception))
                    self.assertIn("exit=7", str(caught.exception))

    def test_frame_failure_stderr_cap_and_terminate_kill_escalation(self):
        meta = handshake(width=2, height=1, frame_bytes=8)
        code = ("import sys,time,signal;signal.signal(signal.SIGTERM,signal.SIG_IGN);"
                "sys.stderr.buffer.write(b'x'*100000);sys.stderr.buffer.flush();"
                f"sys.stdout.buffer.write({json.dumps(meta).encode()!r}+b'\\n');"
                "sys.stdout.buffer.flush();time.sleep(10)")
        capture = self.capture(code, shutdown_timeout=.05)
        try:
            with self.assertRaises(camera.CaptureError):
                capture.next_frame(time.monotonic()+1)
        finally:
            capture.close()
        self.assertEqual(capture.process.returncode, -9)
        self.assertLessEqual(len(capture.stderr_tail), 16384)
        self.assertTrue(capture.stderr_tail)

    def test_binding_is_checked_before_process_spawn(self):
        from unittest.mock import patch
        with patch.object(camera, "verify_binding", side_effect=ValueError("tamper")):
            with self.assertRaises(ValueError):
                camera.OwnedCapture(None, duration=2,
                                    popen=lambda *a, **k: self.fail("spawned"))


class ConstructorRollbackTests(unittest.TestCase):
    """Fault actual acquisition seams around a real owned binary-pipe child."""

    def thread_start_fault(self, failed_thread):
        import threading
        from unittest.mock import patch

        metadata = handshake(width=2, height=1, frame_bytes=8)
        code = ("import os,time; "
                f"os.write(1,{json.dumps(metadata).encode()!r}+b'\\n'); "
                "time.sleep(10)")
        children, threads = [], []
        spawn = CaptureTests().factory(code)
        marker = RuntimeError("primary thread acquisition sentinel")
        original_start = threading.Thread.start

        def popen(*args, **kwargs):
            child = spawn(*args, **kwargs)
            children.append(child)
            return child

        def start(thread):
            threads.append(thread)
            if thread.name == failed_thread:
                raise marker
            return original_start(thread)

        error = None
        before = time.monotonic()
        try:
            with patch.object(camera, "verify_binding"), patch.object(threading.Thread, "start", start):
                try:
                    camera.OwnedCapture(type("Binding", (), {"binary": Path("/unused")})(),
                                        duration=1, popen=popen, startup_timeout=2,
                                        frame_timeout=2, shutdown_timeout=.05)
                except BaseException as caught:
                    error = caught
            self.assertEqual(len(children), 1)
            self.assertIn(failed_thread, [thread.name for thread in threads])
            self.assertLess(time.monotonic() - before, 2)
            self.assertIsNotNone(children[0].poll(), "owned child must be reaped")
            self.assertTrue(error is marker or getattr(error, "__cause__", None) is marker,
                            f"acquisition must remain primary, got {error!r}")
            self.assertTrue(children[0].stdout.closed)
            self.assertTrue(children[0].stderr.closed)
            self.assertTrue(all(not thread.is_alive() for thread in threads))
        finally:
            for child in children:
                if child.poll() is None:
                    child.kill(); child.wait(timeout=2)
                for pipe in (child.stdout, child.stderr):
                    if not pipe.closed:
                        pipe.close()
            for thread in threads:
                if thread.ident is not None:
                    thread.join(timeout=2)

    def test_stderr_thread_start_failure_rolls_back_owned_resources(self):
        self.thread_start_fault("owned-camera-stderr")

    def test_acquisition_error_survives_join_and_pipe_rollback_failures_then_retries(self):
        import contextlib
        import threading
        from unittest.mock import patch

        metadata = handshake(width=2, height=1, frame_bytes=8)
        code = ("import os,time; "
                f"os.write(1,{json.dumps(metadata).encode()!r}+b'\\n'); time.sleep(10)")
        spawn = CaptureTests().factory(code)
        primary = RuntimeError("frame thread acquisition sentinel")
        join_error = RuntimeError("stderr rollback join sentinel")
        pipe_error = OSError("stdout rollback close sentinel")
        children, attempts = [], []
        original_start = threading.Thread.start
        capture = camera.OwnedCapture.__new__(camera.OwnedCapture)

        try:
            with contextlib.ExitStack() as faults:
                def popen(*args, **kwargs):
                    child = spawn(*args, **kwargs)
                    children.append(child)
                    assert child.stdout is not None
                    original_close = child.stdout.close
                    def close_stdout():
                        attempts.append("stdout.close")
                        if attempts.count("stdout.close") == 1:
                            raise pipe_error
                        return original_close()
                    faults.enter_context(patch.object(child.stdout, "close", close_stdout))
                    return child

                def start(thread):
                    if thread.name == "owned-camera-frames":
                        attempts.append("frames.start")
                        raise primary
                    original_start(thread)
                    original_join = thread.join
                    def join(**kwargs):
                        attempts.append("stderr.join")
                        if attempts.count("stderr.join") == 1:
                            raise join_error
                        return original_join(**kwargs)
                    faults.enter_context(patch.object(thread, "join", join))

                with patch.object(camera, "verify_binding"), patch.object(threading.Thread, "start", start):
                    with self.assertRaises(camera.CaptureError) as caught:
                        capture.__init__(type("Binding", (), {"binary": Path("/unused")})(),
                                         duration=1, popen=popen, startup_timeout=2,
                                         frame_timeout=2, shutdown_timeout=.05)
                self.assertEqual(attempts, ["frames.start", "stderr.join", "stdout.close"])
                self.assertIs(caught.exception.__cause__, primary)
                notes = "\n".join(getattr(caught.exception, "__notes__", ()))
                self.assertIn(str(join_error), notes)
                self.assertIn(str(pipe_error), notes)
                self.assertIsNotNone(children[0].poll())
                self.assertTrue(children[0].stderr.closed)
                self.assertFalse(children[0].stdout.closed)
                self.assertFalse(capture._closed)
                capture.close()
                self.assertEqual(attempts.count("stdout.close"), 2)
                self.assertEqual(attempts.count("stderr.join"), 2)
                self.assertTrue(children[0].stdout.closed)
                self.assertTrue(capture._closed)
                capture.close()
                self.assertFalse(capture.stderr_thread.is_alive())
        finally:
            for child in children:
                if child.poll() is None:
                    child.kill(); child.wait(timeout=2)
                for pipe in (child.stdout, child.stderr):
                    if not pipe.closed:
                        pipe.close()
            if capture.stderr_thread is not None and capture.stderr_thread.ident is not None:
                capture.stderr_thread.join(timeout=2)

    def test_frame_thread_start_failure_rolls_back_owned_resources(self):
        self.thread_start_fault("owned-camera-frames")


class TeardownRetryTests(unittest.TestCase):
    def live_capture(self):
        metadata = handshake(width=2, height=1, frame_bytes=8)
        code = ("import os,time; "
                f"os.write(1,{json.dumps(metadata).encode()!r}+b'\\n'); "
                "time.sleep(10)")
        return CaptureTests().capture(code, shutdown_timeout=.05)

    def release_fixture(self, capture):
        # Harness fallback is outside the product assertions and fault patches.
        if capture.process.poll() is None:
            capture.process.kill(); capture.process.wait(timeout=2)
        for pipe in (capture.process.stdout, capture.process.stderr):
            if not pipe.closed:
                pipe.close()
        for thread in (capture.reader_thread, capture.stderr_thread):
            if thread is not None and thread.ident is not None:
                thread.join(timeout=2)

    def test_join_timeout_is_reported_and_remains_retryable_until_thread_stops(self):
        import threading
        from unittest.mock import patch
        entered, release = threading.Event(), threading.Event()
        original_frames = camera.OwnedCapture._frames

        def held_frames(capture):
            entered.set()
            release.wait(2)
            original_frames(capture)

        with patch.object(camera.OwnedCapture, "_frames", held_frames):
            capture = self.live_capture()
        try:
            self.assertTrue(entered.wait(2))
            before = time.monotonic()
            with self.assertRaises(TimeoutError) as caught:
                capture.close()
            self.assertIn("owned-camera-frames", str(caught.exception))
            self.assertLess(time.monotonic() - before, 1)
            self.assertTrue(capture.reader_thread.is_alive())
            self.assertFalse(capture.stderr_thread.is_alive())
            self.assertIsNotNone(capture.process.poll())
            self.assertTrue(capture.process.stdout.closed)
            self.assertTrue(capture.process.stderr.closed)
            self.assertFalse(capture._closed)
            release.set()
            capture.close()
            self.assertTrue(capture._closed)
            self.assertFalse(capture.reader_thread.is_alive())
            capture.close()
        finally:
            release.set()
            self.release_fixture(capture)

    def test_stdout_close_failure_still_closes_stderr_and_retries_incomplete_pipe(self):
        from unittest.mock import patch
        capture = self.live_capture()
        marker = OSError("stdout close teardown sentinel")
        stdout_close = capture.process.stdout.close
        stderr_close = capture.process.stderr.close
        attempts = []

        def close_stdout():
            attempts.append("stdout.close")
            if len(attempts) == 1:
                raise marker
            return stdout_close()

        before = time.monotonic()
        try:
            with patch.object(capture.process.stdout, "close", close_stdout), \
                 patch.object(capture.process.stderr, "close", wraps=stderr_close) as later_close:
                with self.assertRaises(OSError) as caught:
                    capture.close()
                self.assertIs(caught.exception, marker)
                self.assertEqual(later_close.call_count, 1, "one pipe must not abort the next")
                self.assertFalse(capture.process.stdout.closed)
                self.assertTrue(capture.process.stderr.closed)
                self.assertIsNotNone(capture.process.poll())
                self.assertFalse(capture._closed)
                capture.close()
                self.assertEqual(len(attempts), 2, "retry must revisit the incomplete close")
                self.assertEqual(later_close.call_count, 1, "completed pipes need not close again")
                self.assertTrue(capture.process.stdout.closed)
                self.assertTrue(capture._closed)
                capture.close()
                self.assertEqual(len(attempts), 2)
            self.assertFalse(capture.reader_thread.is_alive())
            self.assertFalse(capture.stderr_thread.is_alive())
            self.assertLess(time.monotonic() - before, 2)
        finally:
            self.release_fixture(capture)

    def test_join_failure_attempts_later_join_and_both_pipes_then_allows_retry(self):
        from unittest.mock import patch
        capture = self.live_capture()
        marker = RuntimeError("reader join teardown sentinel")
        stderr_join = capture.stderr_thread.join
        before = time.monotonic()
        try:
            with patch.object(capture.reader_thread, "join", side_effect=marker), \
                 patch.object(capture.stderr_thread, "join", wraps=stderr_join) as later_join:
                with self.assertRaises(RuntimeError) as caught:
                    capture.close()
                self.assertIs(caught.exception, marker)
                self.assertEqual(later_join.call_count, 1, "one join must not abort the next")
                self.assertTrue(capture.process.stdout.closed)
                self.assertTrue(capture.process.stderr.closed)
                self.assertIsNotNone(capture.process.poll())
                self.assertFalse(capture._closed, "incomplete cleanup must remain retryable")
            capture.close()
            self.assertTrue(capture._closed)
            self.assertFalse(capture.reader_thread.is_alive())
            self.assertFalse(capture.stderr_thread.is_alive())
            with patch.object(capture.process, "wait", side_effect=AssertionError("already closed")):
                capture.close()
            self.assertLess(time.monotonic() - before, 2)
        finally:
            self.release_fixture(capture)


if __name__ == "__main__":
    unittest.main()
