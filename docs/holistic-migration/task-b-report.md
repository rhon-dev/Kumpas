# Task B — built-in-only Mac preview implementation

## Scope and starting evidence

- Owner-authorized Task B only; parent acceptance `task-a-acceptance.json` is present. Preserve its six SHA-256-bound source files. No live preview/camera capture, dataset extraction, classifier fitting, app/phone work, dependency installation, commits or pushes in this child.
- Read the Task B brief, AGENTS/PRD/phase gates, migration plan, FEATURES and actual Task A interfaces. The migration authorization is bounded; it does not close historical research/device gates.
- Ownership: only `camera.swift`, `camera.py`, `webcam.py`, `tests/test_camera.py`, `tests/test_webcam.py` under `training/holistic_migration/`, and this report.
- Baseline HEAD: `4d901693642af5f572455b2c75ba095b0ec65c7f`; original tracked diff initially empty. Existing migration files are untracked parent work.
- Existing combined Python: `/Users/ahronjanl.rafaelahron.0804icloudcom/.kumpas-venvs/rv2-holistic-tf-20261101/bin/python` (3.11.15). `/usr/bin/swiftc --version`: Apple Swift 6.4, arm64-apple-macosx26.0.

## Verification method

Strict cohesive vertical RED→GREEN slices, using the combined Python with `-E -B`. Tests use production parsers and injected camera/detector/GUI boundaries: no real camera, window or MediaPipe loading. Native pure selection/packing self-tests and compilation are allowed; live launch is reserved for the parent. Each slice below records actual commands and outputs promptly. Build/module cache/TMPDIR and test temporary files remain in owned external scratch/data paths. No live pixels or landmark arrays are persisted.

## Incremental execution

Implementation not started. Planned vertical boundaries: handshake admission; packet framing; exact native build binding; owned child lifecycle/latest-only delivery; preview argument admission; RGB/display/overlay; bounded loop/report; native pure self-tests and complete regression verification.

## Acceptance limits

Software tests/compile/self-tests cannot establish camera permission, human tracking, SDK anatomical handedness, gesture accuracy, sustained target FPS or owner live readiness. Parent must launch the visible built-in preview separately. Zero-human/heartbeat sessions are not live acceptance.
### Slice 1 RED — handshake contract (module not implemented)

```sh
/Users/ahronjanl.rafaelahron.0804icloudcom/.kumpas-venvs/rv2-holistic-tf-20261101/bin/python -E -B -m unittest training.holistic_migration.tests.test_camera -v
```

Exit 1:
```text
test_camera (unittest.loader._FailedTest.test_camera) ... ERROR

======================================================================
ERROR: test_camera (unittest.loader._FailedTest.test_camera)
----------------------------------------------------------------------
ImportError: Failed to import test module: test_camera
Traceback (most recent call last):
  File "/opt/homebrew/Cellar/python@3.11/3.11.15/Frameworks/Python.framework/Versions/3.11/lib/python3.11/unittest/loader.py", line 162, in loadTestsFromName
    module = __import__(module_name)
             ^^^^^^^^^^^^^^^^^^^^^^^
  File "/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration/training/holistic_migration/tests/test_camera.py", line 5, in <module>
    from training.holistic_migration import camera
ImportError: cannot import name 'camera' from 'training.holistic_migration' (/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration/training/holistic_migration/__init__.py)


----------------------------------------------------------------------
Ran 1 test in 0.000s

FAILED (errors=1)
```

### Slice 1 GREEN — handshake contract (report formatting fixed)

```sh
/Users/ahronjanl.rafaelahron.0804icloudcom/.kumpas-venvs/rv2-holistic-tf-20261101/bin/python -E -B -m unittest training.holistic_migration.tests.test_camera -v
```

Exit 0:
```text
test_actual_bgra_dimensions_and_builtin_identity_are_admitted (training.holistic_migration.tests.test_camera.HandshakeTests.test_actual_bgra_dimensions_and_builtin_identity_are_admitted) ... ok
test_ambiguous_or_nonbuiltin_metadata_is_rejected (training.holistic_migration.tests.test_camera.HandshakeTests.test_ambiguous_or_nonbuiltin_metadata_is_rejected) ... ok

----------------------------------------------------------------------
Ran 2 tests in 0.001s

OK
```

### Slice 2 RED — bounded handshake/packet parsing

```sh
/Users/ahronjanl.rafaelahron.0804icloudcom/.kumpas-venvs/rv2-holistic-tf-20261101/bin/python -E -B -m unittest training.holistic_migration.tests.test_camera.PacketTests -v
```

Exit 1:
```text
test_partial_reads_actual_handshake_and_exact_frame (training.holistic_migration.tests.test_camera.PacketTests.test_partial_reads_actual_handshake_and_exact_frame) ... ERROR
test_repeated_or_regressing_timestamp_and_startup_limits (training.holistic_migration.tests.test_camera.PacketTests.test_repeated_or_regressing_timestamp_and_startup_limits) ... ERROR
test_short_oversized_and_invalid_timestamps_fail_closed (training.holistic_migration.tests.test_camera.PacketTests.test_short_oversized_and_invalid_timestamps_fail_closed) ... 
  test_short_oversized_and_invalid_timestamps_fail_closed (training.holistic_migration.tests.test_camera.PacketTests.test_short_oversized_and_invalid_timestamps_fail_closed) (data=b'') ... ERROR
  test_short_oversized_and_invalid_timestamps_fail_closed (training.holistic_migration.tests.test_camera.PacketTests.test_short_oversized_and_invalid_timestamps_fail_closed) (data=b'xxxxxxxxxxx') ... ERROR
  test_short_oversized_and_invalid_timestamps_fail_closed (training.holistic_migration.tests.test_camera.PacketTests.test_short_oversized_and_invalid_timestamps_fail_closed) (data=b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\t') ... ERROR
  test_short_oversized_and_invalid_timestamps_fail_closed (training.holistic_migration.tests.test_camera.PacketTests.test_short_oversized_and_invalid_timestamps_fail_closed) (data=b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x08short') ... ERROR
  test_short_oversized_and_invalid_timestamps_fail_closed (training.holistic_migration.tests.test_camera.PacketTests.test_short_oversized_and_invalid_timestamps_fail_closed) (data=b'\x7f\xf8\x00\x00\x00\x00\x00\x00\x00\x00\x00\x0812345678') ... ERROR
  test_short_oversized_and_invalid_timestamps_fail_closed (training.holistic_migration.tests.test_camera.PacketTests.test_short_oversized_and_invalid_timestamps_fail_closed) (data=b'\x7f\xf0\x00\x00\x00\x00\x00\x00\x00\x00\x00\x0812345678') ... ERROR
  test_short_oversized_and_invalid_timestamps_fail_closed (training.holistic_migration.tests.test_camera.PacketTests.test_short_oversized_and_invalid_timestamps_fail_closed) (data=b'\xbf\xf0\x00\x00\x00\x00\x00\x00\x00\x00\x00\x0812345678') ... ERROR
  test_short_oversized_and_invalid_timestamps_fail_closed (training.holistic_migration.tests.test_camera.PacketTests.test_short_oversized_and_invalid_timestamps_fail_closed) (data=b'?\xe0\x00\x00\x00\x00\x00\x00\x00\x00\x00\x0812345678') ... ERROR

======================================================================
ERROR: test_partial_reads_actual_handshake_and_exact_frame (training.holistic_migration.tests.test_camera.PacketTests.test_partial_reads_actual_handshake_and_exact_frame)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration/training/holistic_migration/tests/test_camera.py", line 46, in test_partial_reads_actual_handshake_and_exact_frame
    reader = self.reader(wire)
             ^^^^^^^^^^^^^^^^^
  File "/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration/training/holistic_migration/tests/test_camera.py", line 41, in reader
    return camera.PacketReader(lambda n, deadline: stream.read(min(n, chunk)))
           ^^^^^^^^^^^^^^^^^^^
AttributeError: module 'training.holistic_migration.camera' has no attribute 'PacketReader'

======================================================================
ERROR: test_repeated_or_regressing_timestamp_and_startup_limits (training.holistic_migration.tests.test_camera.PacketTests.test_repeated_or_regressing_timestamp_and_startup_limits)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration/training/holistic_migration/tests/test_camera.py", line 67, in test_repeated_or_regressing_timestamp_and_startup_limits
    reader = self.reader(struct.pack(">dI", timestamp, 8) + b"12345678")
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration/training/holistic_migration/tests/test_camera.py", line 41, in reader
    return camera.PacketReader(lambda n, deadline: stream.read(min(n, chunk)))
           ^^^^^^^^^^^^^^^^^^^
AttributeError: module 'training.holistic_migration.camera' has no attribute 'PacketReader'

======================================================================
ERROR: test_short_oversized_and_invalid_timestamps_fail_closed (training.holistic_migration.tests.test_camera.PacketTests.test_short_oversized_and_invalid_timestamps_fail_closed) (data=b'')
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration/training/holistic_migration/tests/test_camera.py", line 60, in test_short_oversized_and_invalid_timestamps_fail_closed
    reader = self.reader(data)
             ^^^^^^^^^^^^^^^^^
  File "/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration/training/holistic_migration/tests/test_camera.py", line 41, in reader
    return camera.PacketReader(lambda n, deadline: stream.read(min(n, chunk)))
           ^^^^^^^^^^^^^^^^^^^
AttributeError: module 'training.holistic_migration.camera' has no attribute 'PacketReader'

======================================================================
ERROR: test_short_oversized_and_invalid_timestamps_fail_closed (training.holistic_migration.tests.test_camera.PacketTests.test_short_oversized_and_invalid_timestamps_fail_closed) (data=b'xxxxxxxxxxx')
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration/training/holistic_migration/tests/test_camera.py", line 60, in test_short_oversized_and_invalid_timestamps_fail_closed
    reader = self.reader(data)
             ^^^^^^^^^^^^^^^^^
  File "/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration/training/holistic_migration/tests/test_camera.py", line 41, in reader
    return camera.PacketReader(lambda n, deadline: stream.read(min(n, chunk)))
           ^^^^^^^^^^^^^^^^^^^
AttributeError: module 'training.holistic_migration.camera' has no attribute 'PacketReader'

======================================================================
ERROR: test_short_oversized_and_invalid_timestamps_fail_closed (training.holistic_migration.tests.test_camera.PacketTests.test_short_oversized_and_invalid_timestamps_fail_closed) (data=b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\t')
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration/training/holistic_migration/tests/test_camera.py", line 60, in test_short_oversized_and_invalid_timestamps_fail_closed
    reader = self.reader(data)
             ^^^^^^^^^^^^^^^^^
  File "/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration/training/holistic_migration/tests/test_camera.py", line 41, in reader
    return camera.PacketReader(lambda n, deadline: stream.read(min(n, chunk)))
           ^^^^^^^^^^^^^^^^^^^
AttributeError: module 'training.holistic_migration.camera' has no attribute 'PacketReader'

======================================================================
ERROR: test_short_oversized_and_invalid_timestamps_fail_closed (training.holistic_migration.tests.test_camera.PacketTests.test_short_oversized_and_invalid_timestamps_fail_closed) (data=b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x08short')
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration/training/holistic_migration/tests/test_camera.py", line 60, in test_short_oversized_and_invalid_timestamps_fail_closed
    reader = self.reader(data)
             ^^^^^^^^^^^^^^^^^
  File "/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration/training/holistic_migration/tests/test_camera.py", line 41, in reader
    return camera.PacketReader(lambda n, deadline: stream.read(min(n, chunk)))
           ^^^^^^^^^^^^^^^^^^^
AttributeError: module 'training.holistic_migration.camera' has no attribute 'PacketReader'

======================================================================
ERROR: test_short_oversized_and_invalid_timestamps_fail_closed (training.holistic_migration.tests.test_camera.PacketTests.test_short_oversized_and_invalid_timestamps_fail_closed) (data=b'\x7f\xf8\x00\x00\x00\x00\x00\x00\x00\x00\x00\x0812345678')
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration/training/holistic_migration/tests/test_camera.py", line 60, in test_short_oversized_and_invalid_timestamps_fail_closed
    reader = self.reader(data)
             ^^^^^^^^^^^^^^^^^
  File "/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration/training/holistic_migration/tests/test_camera.py", line 41, in reader
    return camera.PacketReader(lambda n, deadline: stream.read(min(n, chunk)))
           ^^^^^^^^^^^^^^^^^^^
AttributeError: module 'training.holistic_migration.camera' has no attribute 'PacketReader'

======================================================================
ERROR: test_short_oversized_and_invalid_timestamps_fail_closed (training.holistic_migration.tests.test_camera.PacketTests.test_short_oversized_and_invalid_timestamps_fail_closed) (data=b'\x7f\xf0\x00\x00\x00\x00\x00\x00\x00\x00\x00\x0812345678')
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration/training/holistic_migration/tests/test_camera.py", line 60, in test_short_oversized_and_invalid_timestamps_fail_closed
    reader = self.reader(data)
             ^^^^^^^^^^^^^^^^^
  File "/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration/training/holistic_migration/tests/test_camera.py", line 41, in reader
    return camera.PacketReader(lambda n, deadline: stream.read(min(n, chunk)))
           ^^^^^^^^^^^^^^^^^^^
AttributeError: module 'training.holistic_migration.camera' has no attribute 'PacketReader'

======================================================================
ERROR: test_short_oversized_and_invalid_timestamps_fail_closed (training.holistic_migration.tests.test_camera.PacketTests.test_short_oversized_and_invalid_timestamps_fail_closed) (data=b'\xbf\xf0\x00\x00\x00\x00\x00\x00\x00\x00\x00\x0812345678')
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration/training/holistic_migration/tests/test_camera.py", line 60, in test_short_oversized_and_invalid_timestamps_fail_closed
    reader = self.reader(data)
             ^^^^^^^^^^^^^^^^^
  File "/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration/training/holistic_migration/tests/test_camera.py", line 41, in reader
    return camera.PacketReader(lambda n, deadline: stream.read(min(n, chunk)))
           ^^^^^^^^^^^^^^^^^^^
AttributeError: module 'training.holistic_migration.camera' has no attribute 'PacketReader'

======================================================================
ERROR: test_short_oversized_and_invalid_timestamps_fail_closed (training.holistic_migration.tests.test_camera.PacketTests.test_short_oversized_and_invalid_timestamps_fail_closed) (data=b'?\xe0\x00\x00\x00\x00\x00\x00\x00\x00\x00\x0812345678')
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration/training/holistic_migration/tests/test_camera.py", line 60, in test_short_oversized_and_invalid_timestamps_fail_closed
    reader = self.reader(data)
             ^^^^^^^^^^^^^^^^^
  File "/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration/training/holistic_migration/tests/test_camera.py", line 41, in reader
    return camera.PacketReader(lambda n, deadline: stream.read(min(n, chunk)))
           ^^^^^^^^^^^^^^^^^^^
AttributeError: module 'training.holistic_migration.camera' has no attribute 'PacketReader'

----------------------------------------------------------------------
Ran 3 tests in 0.003s

FAILED (errors=10)
```

### Slice 2 GREEN — framing/EOF/timestamps/startup limits

```sh
/Users/ahronjanl.rafaelahron.0804icloudcom/.kumpas-venvs/rv2-holistic-tf-20261101/bin/python -E -B -m unittest training.holistic_migration.tests.test_camera -v
```

Exit 0:
```text
test_actual_bgra_dimensions_and_builtin_identity_are_admitted (training.holistic_migration.tests.test_camera.HandshakeTests.test_actual_bgra_dimensions_and_builtin_identity_are_admitted) ... ok
test_ambiguous_or_nonbuiltin_metadata_is_rejected (training.holistic_migration.tests.test_camera.HandshakeTests.test_ambiguous_or_nonbuiltin_metadata_is_rejected) ... ok
test_partial_reads_actual_handshake_and_exact_frame (training.holistic_migration.tests.test_camera.PacketTests.test_partial_reads_actual_handshake_and_exact_frame) ... ok
test_repeated_or_regressing_timestamp_and_startup_limits (training.holistic_migration.tests.test_camera.PacketTests.test_repeated_or_regressing_timestamp_and_startup_limits) ... ok
test_short_oversized_and_invalid_timestamps_fail_closed (training.holistic_migration.tests.test_camera.PacketTests.test_short_oversized_and_invalid_timestamps_fail_closed) ... ok

----------------------------------------------------------------------
Ran 5 tests in 0.009s

OK
```

## Recovery — 2026-11-13 03:43 PST

Resuming only unfinished Task B. The prior worker landed the strict handshake and `>dI` packet parser plus five passing parser tests and two unimplemented native-binding tests. These files are retained, not replaced. No `camera.swift`, `webcam.py` or `test_webcam.py` has landed. Task A acceptance and sources are not reopened or edited. HEAD remains `4d901693642af5f572455b2c75ba095b0ec65c7f`. The earlier rate-limit estimate is past; no current provider/configuration change is needed. This child will compile and run camera-free native tests only; the parent owns live camera/GUI launch. The first resumed execution is the existing native-binding RED, before implementation. All following command stdout/stderr and exits are retained below, including failed attempts.

### Slice 3 existing native-binding RED

```sh
TMPDIR=/Users/ahronjanl.rafaelahron.0804icloudcom/.hermes/cache/scratch /Users/ahronjanl.rafaelahron.0804icloudcom/.kumpas-venvs/rv2-holistic-tf-20261101/bin/python -E -B -m unittest training.holistic_migration.tests.test_camera.NativeBindingTests -v
```

Exit: 1

stdout:
```text

```
stderr:
```text
test_build_rejects_relative_or_repository_directory_before_compiler (training.holistic_migration.tests.test_camera.NativeBindingTests.test_build_rejects_relative_or_repository_directory_before_compiler) ... 
  test_build_rejects_relative_or_repository_directory_before_compiler (training.holistic_migration.tests.test_camera.NativeBindingTests.test_build_rejects_relative_or_repository_directory_before_compiler) (directory=PosixPath('relative')) ... ERROR
  test_build_rejects_relative_or_repository_directory_before_compiler (training.holistic_migration.tests.test_camera.NativeBindingTests.test_build_rejects_relative_or_repository_directory_before_compiler) (directory=PosixPath('/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration/training/holistic_migration')) ... ERROR
test_exact_source_compiles_and_pure_native_checks_need_no_camera (training.holistic_migration.tests.test_camera.NativeBindingTests.test_exact_source_compiles_and_pure_native_checks_need_no_camera) ... ERROR

======================================================================
ERROR: test_build_rejects_relative_or_repository_directory_before_compiler (training.holistic_migration.tests.test_camera.NativeBindingTests.test_build_rejects_relative_or_repository_directory_before_compiler) (directory=PosixPath('relative'))
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration/training/holistic_migration/tests/test_camera.py", line 109, in test_build_rejects_relative_or_repository_directory_before_compiler
    camera.build_helper(directory, runner=lambda *a, **k: self.fail("compiler called"))
    ^^^^^^^^^^^^^^^^^^^
AttributeError: module 'training.holistic_migration.camera' has no attribute 'build_helper'

======================================================================
ERROR: test_build_rejects_relative_or_repository_directory_before_compiler (training.holistic_migration.tests.test_camera.NativeBindingTests.test_build_rejects_relative_or_repository_directory_before_compiler) (directory=PosixPath('/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration/training/holistic_migration'))
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration/training/holistic_migration/tests/test_camera.py", line 109, in test_build_rejects_relative_or_repository_directory_before_compiler
    camera.build_helper(directory, runner=lambda *a, **k: self.fail("compiler called"))
    ^^^^^^^^^^^^^^^^^^^
AttributeError: module 'training.holistic_migration.camera' has no attribute 'build_helper'

======================================================================
ERROR: test_exact_source_compiles_and_pure_native_checks_need_no_camera (training.holistic_migration.tests.test_camera.NativeBindingTests.test_exact_source_compiles_and_pure_native_checks_need_no_camera)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration/training/holistic_migration/tests/test_camera.py", line 88, in test_exact_source_compiles_and_pure_native_checks_need_no_camera
    binding = camera.build_helper(Path(directory))
              ^^^^^^^^^^^^^^^^^^^
AttributeError: module 'training.holistic_migration.camera' has no attribute 'build_helper'

----------------------------------------------------------------------
Ran 2 tests in 0.001s

FAILED (errors=3)

```

### Slice 3 first native compilation attempt

```sh
TMPDIR=/Users/ahronjanl.rafaelahron.0804icloudcom/.hermes/cache/scratch /Users/ahronjanl.rafaelahron.0804icloudcom/.kumpas-venvs/rv2-holistic-tf-20261101/bin/python -E -B -m unittest training.holistic_migration.tests.test_camera.NativeBindingTests -v
```

Exit: 1

stdout:
```text

```
stderr:
```text
test_build_rejects_relative_or_repository_directory_before_compiler (training.holistic_migration.tests.test_camera.NativeBindingTests.test_build_rejects_relative_or_repository_directory_before_compiler) ... ok
test_exact_source_compiles_and_pure_native_checks_need_no_camera (training.holistic_migration.tests.test_camera.NativeBindingTests.test_exact_source_compiles_and_pure_native_checks_need_no_camera) ... ERROR

======================================================================
ERROR: test_exact_source_compiles_and_pure_native_checks_need_no_camera (training.holistic_migration.tests.test_camera.NativeBindingTests.test_exact_source_compiles_and_pure_native_checks_need_no_camera)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration/training/holistic_migration/tests/test_camera.py", line 88, in test_exact_source_compiles_and_pure_native_checks_need_no_camera
    binding = camera.build_helper(Path(directory))
              ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration/training/holistic_migration/camera.py", line 150, in build_helper
    raise RuntimeError(f"Swift compilation exit {result.returncode}; {build / 'compile.stderr'}: "
RuntimeError: Swift compilation exit 1; /Users/ahronjanl.rafaelahron.0804icloudcom/.hermes/cache/scratch/task-b-native-test-69rnd1vg/native-2f7646e7dc8b45998750e91ccf7aecba/compile.stderr: /Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration/training/holistic_migration/camera.swift:29:29: error: the compiler is unable to type-check this expression in reasonable time; try breaking up the expression into distinct sub-expressions
 27 |     }
 28 |     var data = Data(capacity: width * height * 4)
 29 |     for row in 0..<height { data.append(source.bindMemory(to: UInt8.self)[row * stride..<row * stride + width * 4]) }
    |                             `- error: the compiler is unable to type-check this expression in reasonable time; try breaking up the expression into distinct sub-expressions
 30 |     return data
 31 | }

/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration/training/holistic_migration/camera.swift:63:21: error: call can throw, but it is executed in a non-throwing autoclosure
 61 |     let external = Descriptor(type: "external", continuity: false, identity: "other")
 62 |     let continuity = Descriptor(type: builtinType, continuity: true, identity: "phone")
 63 |     try require(try selectDevice([external, valid, continuity]) == 1, "selection-exact-index")
    |                     `- error: call can throw, but it is executed in a non-throwing autoclosure
 64 |     for candidates in [[], [external], [continuity], [valid, valid],
 65 |                        [Descriptor(type: builtinType, continuity: false, identity: "")]] {


----------------------------------------------------------------------
Ran 2 tests in 17.387s

FAILED (errors=1)

```

### Slice 3 GREEN — real Swift compilation, pure checks, source/binary tamper rejection

```sh
TMPDIR=/Users/ahronjanl.rafaelahron.0804icloudcom/.hermes/cache/scratch /Users/ahronjanl.rafaelahron.0804icloudcom/.kumpas-venvs/rv2-holistic-tf-20261101/bin/python -E -B -m unittest training.holistic_migration.tests.test_camera -v
```

Exit: 0

stdout:
```text

```
stderr:
```text
test_actual_bgra_dimensions_and_builtin_identity_are_admitted (training.holistic_migration.tests.test_camera.HandshakeTests.test_actual_bgra_dimensions_and_builtin_identity_are_admitted) ... ok
test_ambiguous_or_nonbuiltin_metadata_is_rejected (training.holistic_migration.tests.test_camera.HandshakeTests.test_ambiguous_or_nonbuiltin_metadata_is_rejected) ... ok
test_build_rejects_relative_or_repository_directory_before_compiler (training.holistic_migration.tests.test_camera.NativeBindingTests.test_build_rejects_relative_or_repository_directory_before_compiler) ... ok
test_exact_source_compiles_and_pure_native_checks_need_no_camera (training.holistic_migration.tests.test_camera.NativeBindingTests.test_exact_source_compiles_and_pure_native_checks_need_no_camera) ... ok
test_partial_reads_actual_handshake_and_exact_frame (training.holistic_migration.tests.test_camera.PacketTests.test_partial_reads_actual_handshake_and_exact_frame) ... ok
test_repeated_or_regressing_timestamp_and_startup_limits (training.holistic_migration.tests.test_camera.PacketTests.test_repeated_or_regressing_timestamp_and_startup_limits) ... ok
test_short_oversized_and_invalid_timestamps_fail_closed (training.holistic_migration.tests.test_camera.PacketTests.test_short_oversized_and_invalid_timestamps_fail_closed) ... ok

----------------------------------------------------------------------
Ran 7 tests in 3.016s

OK

```

### Slice 4 RED — owned bounded child and latest-only frames

```sh
TMPDIR=/Users/ahronjanl.rafaelahron.0804icloudcom/.hermes/cache/scratch /Users/ahronjanl.rafaelahron.0804icloudcom/.kumpas-venvs/rv2-holistic-tf-20261101/bin/python -E -B -m unittest training.holistic_migration.tests.test_camera.CaptureTests -v
```

Exit: 1

stdout:
```text

```
stderr:
```text
test_binding_is_checked_before_process_spawn (training.holistic_migration.tests.test_camera.CaptureTests.test_binding_is_checked_before_process_spawn) ... ERROR
test_frame_failure_stderr_cap_and_terminate_kill_escalation (training.holistic_migration.tests.test_camera.CaptureTests.test_frame_failure_stderr_cap_and_terminate_kill_escalation) ... ERROR
test_latest_only_queue_and_owned_child_cleanup (training.holistic_migration.tests.test_camera.CaptureTests.test_latest_only_queue_and_owned_child_cleanup) ... ERROR
test_startup_eof_timeout_and_stderr_are_preserved (training.holistic_migration.tests.test_camera.CaptureTests.test_startup_eof_timeout_and_stderr_are_preserved) ... 
  test_startup_eof_timeout_and_stderr_are_preserved (training.holistic_migration.tests.test_camera.CaptureTests.test_startup_eof_timeout_and_stderr_are_preserved) (code="import sys;sys.stderr.write('specific failure');sys.exit(7)") ... ERROR
  test_startup_eof_timeout_and_stderr_are_preserved (training.holistic_migration.tests.test_camera.CaptureTests.test_startup_eof_timeout_and_stderr_are_preserved) (code='import time;time.sleep(10)') ... ERROR

======================================================================
ERROR: test_binding_is_checked_before_process_spawn (training.holistic_migration.tests.test_camera.CaptureTests.test_binding_is_checked_before_process_spawn)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration/training/holistic_migration/tests/test_camera.py", line 186, in test_binding_is_checked_before_process_spawn
    camera.OwnedCapture(None, duration=2,
    ^^^^^^^^^^^^^^^^^^^
AttributeError: module 'training.holistic_migration.camera' has no attribute 'OwnedCapture'

======================================================================
ERROR: test_frame_failure_stderr_cap_and_terminate_kill_escalation (training.holistic_migration.tests.test_camera.CaptureTests.test_frame_failure_stderr_cap_and_terminate_kill_escalation)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration/training/holistic_migration/tests/test_camera.py", line 172, in test_frame_failure_stderr_cap_and_terminate_kill_escalation
    capture = self.capture(code, shutdown_timeout=.05)
              ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration/training/holistic_migration/tests/test_camera.py", line 122, in capture
    return camera.OwnedCapture(type("Binding", (), {"binary": Path("/unused")})(),
           ^^^^^^^^^^^^^^^^^^^
AttributeError: module 'training.holistic_migration.camera' has no attribute 'OwnedCapture'

======================================================================
ERROR: test_latest_only_queue_and_owned_child_cleanup (training.holistic_migration.tests.test_camera.CaptureTests.test_latest_only_queue_and_owned_child_cleanup)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration/training/holistic_migration/tests/test_camera.py", line 133, in test_latest_only_queue_and_owned_child_cleanup
    capture = self.capture(code)
              ^^^^^^^^^^^^^^^^^^
  File "/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration/training/holistic_migration/tests/test_camera.py", line 122, in capture
    return camera.OwnedCapture(type("Binding", (), {"binary": Path("/unused")})(),
           ^^^^^^^^^^^^^^^^^^^
AttributeError: module 'training.holistic_migration.camera' has no attribute 'OwnedCapture'

======================================================================
ERROR: test_startup_eof_timeout_and_stderr_are_preserved (training.holistic_migration.tests.test_camera.CaptureTests.test_startup_eof_timeout_and_stderr_are_preserved) (code="import sys;sys.stderr.write('specific failure');sys.exit(7)")
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration/training/holistic_migration/tests/test_camera.py", line 158, in test_startup_eof_timeout_and_stderr_are_preserved
    with patch.object(camera, "verify_binding"), self.assertRaises(camera.CaptureError) as caught:
                                                                   ^^^^^^^^^^^^^^^^^^^
AttributeError: module 'training.holistic_migration.camera' has no attribute 'CaptureError'

======================================================================
ERROR: test_startup_eof_timeout_and_stderr_are_preserved (training.holistic_migration.tests.test_camera.CaptureTests.test_startup_eof_timeout_and_stderr_are_preserved) (code='import time;time.sleep(10)')
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration/training/holistic_migration/tests/test_camera.py", line 158, in test_startup_eof_timeout_and_stderr_are_preserved
    with patch.object(camera, "verify_binding"), self.assertRaises(camera.CaptureError) as caught:
                                                                   ^^^^^^^^^^^^^^^^^^^
AttributeError: module 'training.holistic_migration.camera' has no attribute 'CaptureError'

----------------------------------------------------------------------
Ran 4 tests in 0.065s

FAILED (errors=5)

```

### Slice 4 GREEN — real synthetic pipe children, deadlines, stderr cap and kill

```sh
TMPDIR=/Users/ahronjanl.rafaelahron.0804icloudcom/.hermes/cache/scratch /Users/ahronjanl.rafaelahron.0804icloudcom/.kumpas-venvs/rv2-holistic-tf-20261101/bin/python -E -B -m unittest training.holistic_migration.tests.test_camera.CaptureTests -v
```

Exit: 0

stdout:
```text

```
stderr:
```text
test_binding_is_checked_before_process_spawn (training.holistic_migration.tests.test_camera.CaptureTests.test_binding_is_checked_before_process_spawn) ... ok
test_frame_failure_stderr_cap_and_terminate_kill_escalation (training.holistic_migration.tests.test_camera.CaptureTests.test_frame_failure_stderr_cap_and_terminate_kill_escalation) ... ok
test_latest_only_queue_and_owned_child_cleanup (training.holistic_migration.tests.test_camera.CaptureTests.test_latest_only_queue_and_owned_child_cleanup) ... ok
test_startup_eof_timeout_and_stderr_are_preserved (training.holistic_migration.tests.test_camera.CaptureTests.test_startup_eof_timeout_and_stderr_are_preserved) ... ok

----------------------------------------------------------------------
Ran 4 tests in 0.675s

OK

```

### Slice 5 RED — preview argument admission before dependencies

```sh
TMPDIR=/Users/ahronjanl.rafaelahron.0804icloudcom/.hermes/cache/scratch /Users/ahronjanl.rafaelahron.0804icloudcom/.kumpas-venvs/rv2-holistic-tf-20261101/bin/python -E -B -m unittest training.holistic_migration.tests.test_webcam.AdmissionTests -v
```

Exit: 1

stdout:
```text

```
stderr:
```text
test_webcam (unittest.loader._FailedTest.test_webcam) ... ERROR

======================================================================
ERROR: test_webcam (unittest.loader._FailedTest.test_webcam)
----------------------------------------------------------------------
ImportError: Failed to import test module: test_webcam
Traceback (most recent call last):
  File "/opt/homebrew/Cellar/python@3.11/3.11.15/Frameworks/Python.framework/Versions/3.11/lib/python3.11/unittest/loader.py", line 162, in loadTestsFromName
    module = __import__(module_name)
             ^^^^^^^^^^^^^^^^^^^^^^^
  File "/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration/training/holistic_migration/tests/test_webcam.py", line 9, in <module>
    from training.holistic_migration import webcam
ImportError: cannot import name 'webcam' from 'training.holistic_migration' (/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration/training/holistic_migration/__init__.py)


----------------------------------------------------------------------
Ran 1 test in 0.000s

FAILED (errors=1)

```

### Slice 5 GREEN — preflight does not import detector/OpenCV or access invalid paths

```sh
TMPDIR=/Users/ahronjanl.rafaelahron.0804icloudcom/.hermes/cache/scratch /Users/ahronjanl.rafaelahron.0804icloudcom/.kumpas-venvs/rv2-holistic-tf-20261101/bin/python -E -B -m unittest training.holistic_migration.tests.test_webcam.AdmissionTests -v
```

Exit: 0

stdout:
```text

```
stderr:
```text
test_invalid_duration_precedes_paths_and_runtime (training.holistic_migration.tests.test_webcam.AdmissionTests.test_invalid_duration_precedes_paths_and_runtime) ... ok
test_paths_and_report_overwrite_rejected_before_build (training.holistic_migration.tests.test_webcam.AdmissionTests.test_paths_and_report_overwrite_rejected_before_build) ... ok

----------------------------------------------------------------------
Ran 2 tests in 0.003s

OK

```

### Slice 6 RED — actual pixel conversion and mirrored-display-only overlay

```sh
TMPDIR=/Users/ahronjanl.rafaelahron.0804icloudcom/.hermes/cache/scratch /Users/ahronjanl.rafaelahron.0804icloudcom/.kumpas-venvs/rv2-holistic-tf-20261101/bin/python -E -B -m unittest training.holistic_migration.tests.test_webcam.PixelsAndOverlayTests -v
```

Exit: 1

stdout:
```text

```
stderr:
```text
test_actual_bgra_conversion_resize_and_no_input_mirror (training.holistic_migration.tests.test_webcam.PixelsAndOverlayTests.test_actual_bgra_conversion_resize_and_no_input_mirror) ... ERROR
test_missing_components_real_counts_masks_connections_and_readable_text (training.holistic_migration.tests.test_webcam.PixelsAndOverlayTests.test_missing_components_real_counts_masks_connections_and_readable_text) ... ERROR

======================================================================
ERROR: test_actual_bgra_conversion_resize_and_no_input_mirror (training.holistic_migration.tests.test_webcam.PixelsAndOverlayTests.test_actual_bgra_conversion_resize_and_no_input_mirror)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration/training/holistic_migration/tests/test_webcam.py", line 44, in test_actual_bgra_conversion_resize_and_no_input_mirror
    rgb = webcam.prepare_rgb(bytes([0,0,255,255, 255,0,0,255]), meta, cv2)
          ^^^^^^^^^^^^^^^^^^
AttributeError: module 'training.holistic_migration.webcam' has no attribute 'prepare_rgb'

======================================================================
ERROR: test_missing_components_real_counts_masks_connections_and_readable_text (training.holistic_migration.tests.test_webcam.PixelsAndOverlayTests.test_missing_components_real_counts_masks_connections_and_readable_text)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration/training/holistic_migration/tests/test_webcam.py", line 68, in test_missing_components_real_counts_masks_connections_and_readable_text
    output=webcam.render(rgb,missing,pack_frame(missing),meta,
           ^^^^^^^^^^^^^
AttributeError: module 'training.holistic_migration.webcam' has no attribute 'render'

----------------------------------------------------------------------
Ran 2 tests in 0.757s

FAILED (errors=2)

```

### Slice 6 GREEN — real OpenCV in-memory resize/drawing (no window)

```sh
TMPDIR=/Users/ahronjanl.rafaelahron.0804icloudcom/.hermes/cache/scratch /Users/ahronjanl.rafaelahron.0804icloudcom/.kumpas-venvs/rv2-holistic-tf-20261101/bin/python -E -B -m unittest training.holistic_migration.tests.test_webcam.PixelsAndOverlayTests -v
```

Exit: 0

stdout:
```text

```
stderr:
```text
test_actual_bgra_conversion_resize_and_no_input_mirror (training.holistic_migration.tests.test_webcam.PixelsAndOverlayTests.test_actual_bgra_conversion_resize_and_no_input_mirror) ... ok
test_missing_components_real_counts_masks_connections_and_readable_text (training.holistic_migration.tests.test_webcam.PixelsAndOverlayTests.test_missing_components_real_counts_masks_connections_and_readable_text) ... ok

----------------------------------------------------------------------
Ran 2 tests in 0.451s

OK

```

### Slice 7 RED — shared preview loop, controls, failure cleanup and exclusive operational report

```sh
TMPDIR=/Users/ahronjanl.rafaelahron.0804icloudcom/.hermes/cache/scratch /Users/ahronjanl.rafaelahron.0804icloudcom/.kumpas-venvs/rv2-holistic-tf-20261101/bin/python -E -B -m unittest training.holistic_migration.tests.test_webcam.PreviewLoopTests -v
```

Exit: 1

stdout:
```text

```
stderr:
```text
test_errors_cleanup_fault_and_handshake_admission_before_detector (training.holistic_migration.tests.test_webcam.PreviewLoopTests.test_errors_cleanup_fault_and_handshake_admission_before_detector) ... 
  test_errors_cleanup_fault_and_handshake_admission_before_detector (training.holistic_migration.tests.test_webcam.PreviewLoopTests.test_errors_cleanup_fault_and_handshake_admission_before_detector) (kwargs={'failure': 'capture'}) ... ERROR
  test_errors_cleanup_fault_and_handshake_admission_before_detector (training.holistic_migration.tests.test_webcam.PreviewLoopTests.test_errors_cleanup_fault_and_handshake_admission_before_detector) (kwargs={'failure': 'detector'}) ... ERROR
  test_errors_cleanup_fault_and_handshake_admission_before_detector (training.holistic_migration.tests.test_webcam.PreviewLoopTests.test_errors_cleanup_fault_and_handshake_admission_before_detector) (kwargs={'cleanup_failure': True}) ... ERROR
  test_errors_cleanup_fault_and_handshake_admission_before_detector (training.holistic_migration.tests.test_webcam.PreviewLoopTests.test_errors_cleanup_fault_and_handshake_admission_before_detector) (kwargs={'malformed': True}) ... ERROR
test_no_implicit_report_and_main_uses_same_runner (training.holistic_migration.tests.test_webcam.PreviewLoopTests.test_no_implicit_report_and_main_uses_same_runner) ... ERROR
test_quit_escape_window_close_and_deadline_release_all (training.holistic_migration.tests.test_webcam.PreviewLoopTests.test_quit_escape_window_close_and_deadline_release_all) ... 
  test_quit_escape_window_close_and_deadline_release_all (training.holistic_migration.tests.test_webcam.PreviewLoopTests.test_quit_escape_window_close_and_deadline_release_all) (terminal='quit', keys=(113,)) ... ERROR
  test_quit_escape_window_close_and_deadline_release_all (training.holistic_migration.tests.test_webcam.PreviewLoopTests.test_quit_escape_window_close_and_deadline_release_all) (terminal='quit', keys=(27,)) ... ERROR
  test_quit_escape_window_close_and_deadline_release_all (training.holistic_migration.tests.test_webcam.PreviewLoopTests.test_quit_escape_window_close_and_deadline_release_all) (terminal='window_closed', keys=()) ... ERROR
  test_quit_escape_window_close_and_deadline_release_all (training.holistic_migration.tests.test_webcam.PreviewLoopTests.test_quit_escape_window_close_and_deadline_release_all) (terminal='deadline', keys=()) ... ERROR
  test_quit_escape_window_close_and_deadline_release_all (training.holistic_migration.tests.test_webcam.PreviewLoopTests.test_quit_escape_window_close_and_deadline_release_all) (terminal='quit', keys=(109, 113)) ... ERROR

======================================================================
ERROR: test_errors_cleanup_fault_and_handshake_admission_before_detector (training.holistic_migration.tests.test_webcam.PreviewLoopTests.test_errors_cleanup_fault_and_handshake_admission_before_detector) (kwargs={'failure': 'capture'})
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration/training/holistic_migration/tests/test_webcam.py", line 171, in test_errors_cleanup_fault_and_handshake_admission_before_detector
    webcam.run_preview(options,runtime=runtime)
    ^^^^^^^^^^^^^^^^^^
AttributeError: module 'training.holistic_migration.webcam' has no attribute 'run_preview'

======================================================================
ERROR: test_errors_cleanup_fault_and_handshake_admission_before_detector (training.holistic_migration.tests.test_webcam.PreviewLoopTests.test_errors_cleanup_fault_and_handshake_admission_before_detector) (kwargs={'failure': 'detector'})
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration/training/holistic_migration/tests/test_webcam.py", line 171, in test_errors_cleanup_fault_and_handshake_admission_before_detector
    webcam.run_preview(options,runtime=runtime)
    ^^^^^^^^^^^^^^^^^^
AttributeError: module 'training.holistic_migration.webcam' has no attribute 'run_preview'

======================================================================
ERROR: test_errors_cleanup_fault_and_handshake_admission_before_detector (training.holistic_migration.tests.test_webcam.PreviewLoopTests.test_errors_cleanup_fault_and_handshake_admission_before_detector) (kwargs={'cleanup_failure': True})
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration/training/holistic_migration/tests/test_webcam.py", line 171, in test_errors_cleanup_fault_and_handshake_admission_before_detector
    webcam.run_preview(options,runtime=runtime)
    ^^^^^^^^^^^^^^^^^^
AttributeError: module 'training.holistic_migration.webcam' has no attribute 'run_preview'

======================================================================
ERROR: test_errors_cleanup_fault_and_handshake_admission_before_detector (training.holistic_migration.tests.test_webcam.PreviewLoopTests.test_errors_cleanup_fault_and_handshake_admission_before_detector) (kwargs={'malformed': True})
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration/training/holistic_migration/tests/test_webcam.py", line 171, in test_errors_cleanup_fault_and_handshake_admission_before_detector
    webcam.run_preview(options,runtime=runtime)
    ^^^^^^^^^^^^^^^^^^
AttributeError: module 'training.holistic_migration.webcam' has no attribute 'run_preview'

======================================================================
ERROR: test_no_implicit_report_and_main_uses_same_runner (training.holistic_migration.tests.test_webcam.PreviewLoopTests.test_no_implicit_report_and_main_uses_same_runner)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration/training/holistic_migration/tests/test_webcam.py", line 186, in test_no_implicit_report_and_main_uses_same_runner
    with patch.object(webcam,"load_runtime",return_value=runtime):
  File "/opt/homebrew/Cellar/python@3.11/3.11.15/Frameworks/Python.framework/Versions/3.11/lib/python3.11/unittest/mock.py", line 1446, in __enter__
    original, local = self.get_original()
                      ^^^^^^^^^^^^^^^^^^^
  File "/opt/homebrew/Cellar/python@3.11/3.11.15/Frameworks/Python.framework/Versions/3.11/lib/python3.11/unittest/mock.py", line 1419, in get_original
    raise AttributeError(
AttributeError: <module 'training.holistic_migration.webcam' from '/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration/training/holistic_migration/webcam.py'> does not have the attribute 'load_runtime'

======================================================================
ERROR: test_quit_escape_window_close_and_deadline_release_all (training.holistic_migration.tests.test_webcam.PreviewLoopTests.test_quit_escape_window_close_and_deadline_release_all) (terminal='quit', keys=(113,))
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration/training/holistic_migration/tests/test_webcam.py", line 148, in test_quit_escape_window_close_and_deadline_release_all
    summary=webcam.run_preview(options,runtime=runtime)
            ^^^^^^^^^^^^^^^^^^
AttributeError: module 'training.holistic_migration.webcam' has no attribute 'run_preview'

======================================================================
ERROR: test_quit_escape_window_close_and_deadline_release_all (training.holistic_migration.tests.test_webcam.PreviewLoopTests.test_quit_escape_window_close_and_deadline_release_all) (terminal='quit', keys=(27,))
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration/training/holistic_migration/tests/test_webcam.py", line 148, in test_quit_escape_window_close_and_deadline_release_all
    summary=webcam.run_preview(options,runtime=runtime)
            ^^^^^^^^^^^^^^^^^^
AttributeError: module 'training.holistic_migration.webcam' has no attribute 'run_preview'

======================================================================
ERROR: test_quit_escape_window_close_and_deadline_release_all (training.holistic_migration.tests.test_webcam.PreviewLoopTests.test_quit_escape_window_close_and_deadline_release_all) (terminal='window_closed', keys=())
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration/training/holistic_migration/tests/test_webcam.py", line 148, in test_quit_escape_window_close_and_deadline_release_all
    summary=webcam.run_preview(options,runtime=runtime)
            ^^^^^^^^^^^^^^^^^^
AttributeError: module 'training.holistic_migration.webcam' has no attribute 'run_preview'

======================================================================
ERROR: test_quit_escape_window_close_and_deadline_release_all (training.holistic_migration.tests.test_webcam.PreviewLoopTests.test_quit_escape_window_close_and_deadline_release_all) (terminal='deadline', keys=())
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration/training/holistic_migration/tests/test_webcam.py", line 148, in test_quit_escape_window_close_and_deadline_release_all
    summary=webcam.run_preview(options,runtime=runtime)
            ^^^^^^^^^^^^^^^^^^
AttributeError: module 'training.holistic_migration.webcam' has no attribute 'run_preview'

======================================================================
ERROR: test_quit_escape_window_close_and_deadline_release_all (training.holistic_migration.tests.test_webcam.PreviewLoopTests.test_quit_escape_window_close_and_deadline_release_all) (terminal='quit', keys=(109, 113))
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration/training/holistic_migration/tests/test_webcam.py", line 148, in test_quit_escape_window_close_and_deadline_release_all
    summary=webcam.run_preview(options,runtime=runtime)
            ^^^^^^^^^^^^^^^^^^
AttributeError: module 'training.holistic_migration.webcam' has no attribute 'run_preview'

----------------------------------------------------------------------
Ran 3 tests in 0.391s

FAILED (errors=10)

```

### Slice 7 GREEN — shared packing, controls, cleanup and report; full webcam suite

```sh
TMPDIR=/Users/ahronjanl.rafaelahron.0804icloudcom/.hermes/cache/scratch /Users/ahronjanl.rafaelahron.0804icloudcom/.kumpas-venvs/rv2-holistic-tf-20261101/bin/python -E -B -m unittest training.holistic_migration.tests.test_webcam -v
```

Exit: 0

stdout:
```text

```
stderr:
```text
test_invalid_duration_precedes_paths_and_runtime (training.holistic_migration.tests.test_webcam.AdmissionTests.test_invalid_duration_precedes_paths_and_runtime) ... ok
test_paths_and_report_overwrite_rejected_before_build (training.holistic_migration.tests.test_webcam.AdmissionTests.test_paths_and_report_overwrite_rejected_before_build) ... ok
test_actual_bgra_conversion_resize_and_no_input_mirror (training.holistic_migration.tests.test_webcam.PixelsAndOverlayTests.test_actual_bgra_conversion_resize_and_no_input_mirror) ... ok
test_missing_components_real_counts_masks_connections_and_readable_text (training.holistic_migration.tests.test_webcam.PixelsAndOverlayTests.test_missing_components_real_counts_masks_connections_and_readable_text) ... ok
test_errors_cleanup_fault_and_handshake_admission_before_detector (training.holistic_migration.tests.test_webcam.PreviewLoopTests.test_errors_cleanup_fault_and_handshake_admission_before_detector) ... ok
test_no_implicit_report_and_main_uses_same_runner (training.holistic_migration.tests.test_webcam.PreviewLoopTests.test_no_implicit_report_and_main_uses_same_runner) ... ok
test_quit_escape_window_close_and_deadline_release_all (training.holistic_migration.tests.test_webcam.PreviewLoopTests.test_quit_escape_window_close_and_deadline_release_all) ... ok

----------------------------------------------------------------------
Ran 7 tests in 0.465s

OK

```

### First full new-package regression suite

```sh
TMPDIR=/Users/ahronjanl.rafaelahron.0804icloudcom/.hermes/cache/scratch /Users/ahronjanl.rafaelahron.0804icloudcom/.kumpas-venvs/rv2-holistic-tf-20261101/bin/python -E -B -m unittest discover -s training/holistic_migration/tests -v
```

Exit: 0

stdout:
```text

```
stderr:
```text
test_binding_is_checked_before_process_spawn (test_camera.CaptureTests.test_binding_is_checked_before_process_spawn) ... ok
test_frame_failure_stderr_cap_and_terminate_kill_escalation (test_camera.CaptureTests.test_frame_failure_stderr_cap_and_terminate_kill_escalation) ... ok
test_latest_only_queue_and_owned_child_cleanup (test_camera.CaptureTests.test_latest_only_queue_and_owned_child_cleanup) ... ok
test_startup_eof_timeout_and_stderr_are_preserved (test_camera.CaptureTests.test_startup_eof_timeout_and_stderr_are_preserved) ... ok
test_actual_bgra_dimensions_and_builtin_identity_are_admitted (test_camera.HandshakeTests.test_actual_bgra_dimensions_and_builtin_identity_are_admitted) ... ok
test_ambiguous_or_nonbuiltin_metadata_is_rejected (test_camera.HandshakeTests.test_ambiguous_or_nonbuiltin_metadata_is_rejected) ... ok
test_build_rejects_relative_or_repository_directory_before_compiler (test_camera.NativeBindingTests.test_build_rejects_relative_or_repository_directory_before_compiler) ... ok
test_exact_source_compiles_and_pure_native_checks_need_no_camera (test_camera.NativeBindingTests.test_exact_source_compiles_and_pure_native_checks_need_no_camera) ... ok
test_partial_reads_actual_handshake_and_exact_frame (test_camera.PacketTests.test_partial_reads_actual_handshake_and_exact_frame) ... ok
test_repeated_or_regressing_timestamp_and_startup_limits (test_camera.PacketTests.test_repeated_or_regressing_timestamp_and_startup_limits) ... ok
test_short_oversized_and_invalid_timestamps_fail_closed (test_camera.PacketTests.test_short_oversized_and_invalid_timestamps_fail_closed) ... ok
test_construction_uses_tasks_video_cpu_and_disabled_optional_outputs (test_detector.DetectorPreflightTests.test_construction_uses_tasks_video_cpu_and_disabled_optional_outputs) ... ok
test_context_manager_closes_once_on_body_exception_and_is_not_reusable (test_detector.DetectorPreflightTests.test_context_manager_closes_once_on_body_exception_and_is_not_reusable) ... ok
test_conversion_failure_inside_context_releases_tracker (test_detector.DetectorPreflightTests.test_conversion_failure_inside_context_releases_tracker) ... ok
test_detect_feeds_unmirrored_rgb_to_video_and_returns_converted_frame (test_detector.DetectorPreflightTests.test_detect_feeds_unmirrored_rgb_to_video_and_returns_converted_frame) ... ok
test_invalid_api_rgb_or_timestamp_is_rejected_before_any_native_call (test_detector.DetectorPreflightTests.test_invalid_api_rgb_or_timestamp_is_rejected_before_any_native_call) ... ok
test_invalid_model_path_rejected_before_any_mediapipe_import (test_detector.DetectorPreflightTests.test_invalid_model_path_rejected_before_any_mediapipe_import) ... ok
test_native_failure_consumes_timestamp_and_context_still_closes (test_detector.DetectorPreflightTests.test_native_failure_consumes_timestamp_and_context_still_closes) ... ok
test_native_failure_inside_context_releases_tracker (test_detector.DetectorPreflightTests.test_native_failure_inside_context_releases_tracker) ... ok
test_noncontiguous_rgb_keeps_channel_order_and_observations (test_detector.DetectorPreflightTests.test_noncontiguous_rgb_keeps_channel_order_and_observations) ... ok
test_package_imports_are_lazy_without_mediapipe_or_tensorflow (test_detector.DetectorPreflightTests.test_package_imports_are_lazy_without_mediapipe_or_tensorflow) ... ok
test_timestamps_strictly_increase_per_instance_and_new_instance_resets (test_detector.DetectorPreflightTests.test_timestamps_strictly_increase_per_instance_and_new_instance_resets) ... ok
test_conversion_timestamp_is_exact_nonnegative_builtin_int (test_detector.ResultConversionTests.test_conversion_timestamp_is_exact_nonnegative_builtin_int) ... ok
test_empty_components_are_none_and_one_handed_results_remain_distinct (test_detector.ResultConversionTests.test_empty_components_are_none_and_one_handed_results_remain_distinct) ... ok
test_missing_or_none_pose_visibility_is_zero_not_fabricated_confidence (test_detector.ResultConversionTests.test_missing_or_none_pose_visibility_is_zero_not_fabricated_confidence) ... ok
test_nonfinite_or_nonnumeric_sdk_coordinates_raise_clear_value_error (test_detector.ResultConversionTests.test_nonfinite_or_nonnumeric_sdk_coordinates_raise_clear_value_error) ... ok
test_reads_flat_normalized_landmarks_not_world_coordinates (test_detector.ResultConversionTests.test_reads_flat_normalized_landmarks_not_world_coordinates) ... ok
test_requires_exact_pose_hand_counts_and_flat_sdk_shape (test_detector.ResultConversionTests.test_requires_exact_pose_hand_counts_and_flat_sdk_shape) ... ok
test_component_shapes_and_real_numeric_ndarrays_are_required (test_features.PackFrameTests.test_component_shapes_and_real_numeric_ndarrays_are_required) ... ok
test_does_not_mutate_or_alias_readonly_inputs_and_excludes_face (test_features.PackFrameTests.test_does_not_mutate_or_alias_readonly_inputs_and_excludes_face) ... ok
test_exact_layout_float32_row_major (test_features.PackFrameTests.test_exact_layout_float32_row_major) ... ok
test_finite_input_with_nonfinite_normalized_output_raises (test_features.PackFrameTests.test_finite_input_with_nonfinite_normalized_output_raises) ... ok
test_individual_missing_hands_keep_zero_block_and_other_hand (test_features.PackFrameTests.test_individual_missing_hands_keep_zero_block_and_other_hand) ... ok
test_integer_arrays_normalize_in_float_without_truncation (test_features.PackFrameTests.test_integer_arrays_normalize_in_float_without_truncation) ... ok
test_large_but_finite_shoulder_width_is_not_lost_to_squaring_overflow (test_features.PackFrameTests.test_large_but_finite_shoulder_width_is_not_lost_to_squaring_overflow) ... ok
test_low_visibility_pose_points_are_entirely_zeroed (test_features.PackFrameTests.test_low_visibility_pose_points_are_entirely_zeroed) ... ok
test_missing_pose_is_invalid_even_with_observed_hands (test_features.PackFrameTests.test_missing_pose_is_invalid_even_with_observed_hands) ... ok
test_nonfinite_raw_arrays_raise_even_when_pose_is_unusable (test_features.PackFrameTests.test_nonfinite_raw_arrays_raise_even_when_pose_is_unusable) ... ok
test_plain_numeric_arrays_and_strided_readonly_views_keep_packed_behavior (test_features.PackFrameTests.test_plain_numeric_arrays_and_strided_readonly_views_keep_packed_behavior) ... ok
test_raw_timestamp_requires_nonnegative_exact_builtin_int (test_features.PackFrameTests.test_raw_timestamp_requires_nonnegative_exact_builtin_int) ... ok
test_semantic_ndarray_subclasses_are_rejected_before_array_semantics (test_features.PackFrameTests.test_semantic_ndarray_subclasses_are_rejected_before_array_semantics) ... ok
test_translation_positive_scale_and_distinct_depth_origins (test_features.PackFrameTests.test_translation_positive_scale_and_distinct_depth_origins) ... ok
test_unreliable_shoulders_invalidate_without_hip_requirement (test_features.PackFrameTests.test_unreliable_shoulders_invalidate_without_hip_requirement) ... ok
test_valid_idle_observation_has_pose_and_no_hand_masks (test_features.PackFrameTests.test_valid_idle_observation_has_pose_and_no_hand_masks) ... ok
test_raw_frame_is_frozen_with_optional_face (test_features.RawFrameTests.test_raw_frame_is_frozen_with_optional_face) ... ok
test_default_resampling_is_nearest_time_with_earlier_ties (test_features.ResampleFramesTests.test_default_resampling_is_nearest_time_with_earlier_ties) ... ok
test_large_timestamp_origin_does_not_lose_nearest_ties (test_features.ResampleFramesTests.test_large_timestamp_origin_does_not_lose_nearest_ties) ... ok
test_missing_hands_and_idle_are_preserved_as_observations (test_features.ResampleFramesTests.test_missing_hands_and_idle_are_preserved_as_observations) ... ok
test_requires_two_actual_observations_and_exact_integer_steps (test_features.ResampleFramesTests.test_requires_two_actual_observations_and_exact_integer_steps) ... ok
test_timestamps_must_be_strictly_increasing_without_sorting (test_features.ResampleFramesTests.test_timestamps_must_be_strictly_increasing_without_sorting) ... ok
test_unusable_observation_breaks_sequence_even_when_not_sampled (test_features.ResampleFramesTests.test_unusable_observation_breaks_sequence_even_when_not_sampled) ... ok
test_invalid_duration_precedes_paths_and_runtime (test_webcam.AdmissionTests.test_invalid_duration_precedes_paths_and_runtime) ... ok
test_paths_and_report_overwrite_rejected_before_build (test_webcam.AdmissionTests.test_paths_and_report_overwrite_rejected_before_build) ... ok
test_actual_bgra_conversion_resize_and_no_input_mirror (test_webcam.PixelsAndOverlayTests.test_actual_bgra_conversion_resize_and_no_input_mirror) ... ok
test_missing_components_real_counts_masks_connections_and_readable_text (test_webcam.PixelsAndOverlayTests.test_missing_components_real_counts_masks_connections_and_readable_text) ... ok
test_errors_cleanup_fault_and_handshake_admission_before_detector (test_webcam.PreviewLoopTests.test_errors_cleanup_fault_and_handshake_admission_before_detector) ... ok
test_no_implicit_report_and_main_uses_same_runner (test_webcam.PreviewLoopTests.test_no_implicit_report_and_main_uses_same_runner) ... ok
test_quit_escape_window_close_and_deadline_release_all (test_webcam.PreviewLoopTests.test_quit_escape_window_close_and_deadline_release_all) ... ok

----------------------------------------------------------------------
Ran 58 tests in 5.073s

OK

```

### Actual CLI nonfinite admission (expected exit 2, no compile/camera/GUI)

```sh
TMPDIR=/Users/ahronjanl.rafaelahron.0804icloudcom/.hermes/cache/scratch /Users/ahronjanl.rafaelahron.0804icloudcom/.kumpas-venvs/rv2-holistic-tf-20261101/bin/python -E -B -m training.holistic_migration.webcam --model /nonexistent.task --build-dir /not-used --duration nan
```

Exit: 2

stdout:
```text

```
stderr:
```text
usage: webcam.py [-h] --model MODEL --build-dir BUILD_DIR
                 [--duration DURATION] [--report REPORT]
webcam.py: error: duration must be finite and in (0, 300] seconds

```

### Neighboring original training regression suite

```sh
TMPDIR=/Users/ahronjanl.rafaelahron.0804icloudcom/.hermes/cache/scratch /Users/ahronjanl.rafaelahron.0804icloudcom/.kumpas-venvs/rv2-holistic-tf-20261101/bin/python -E -B -m unittest discover -s training/tests -v
```

Exit: 0

stdout:
```text

```
stderr:
```text
test_conflicting_manifest_refuses_evaluation_before_loading_model (test_evaluate_frozen.FrozenEvaluationTests.test_conflicting_manifest_refuses_evaluation_before_loading_model) ... ok
test_missing_freeze_refuses_evaluation_before_loading_model (test_evaluate_frozen.FrozenEvaluationTests.test_missing_freeze_refuses_evaluation_before_loading_model) ... ok
test_no_automatic_selection_by_test_score (test_evaluate_frozen.FrozenEvaluationTests.test_no_automatic_selection_by_test_score) ... ok
test_report_labels_test_reuse_and_signer_uncertainty (test_evaluate_frozen.FrozenEvaluationTests.test_report_labels_test_reuse_and_signer_uncertainty) ... ok
test_duplicate_clip_name_is_rejected (test_evaluation_protocol.EvaluationProtocolTests.test_duplicate_clip_name_is_rejected) ... ok
test_mismatched_clip_count_is_rejected (test_evaluation_protocol.EvaluationProtocolTests.test_mismatched_clip_count_is_rejected) ... ok
test_original_clips_split_before_augmentation (test_evaluation_protocol.EvaluationProtocolTests.test_original_clips_split_before_augmentation) ... ok
test_original_train_test_clip_overlap_is_rejected (test_evaluation_protocol.EvaluationProtocolTests.test_original_train_test_clip_overlap_is_rejected) ... ok
test_source_digest_change_is_rejected (test_evaluation_protocol.EvaluationProtocolTests.test_source_digest_change_is_rejected) ... ok
test_binding_every_role_hash_symlink_and_array_refusal (test_experiment_runner.RunnerTests.test_binding_every_role_hash_symlink_and_array_refusal) ... ok
test_budget_exact_integer_matrix_and_variant_order_schema (test_experiment_runner.RunnerTests.test_budget_exact_integer_matrix_and_variant_order_schema) ... ok
test_cancel_before_start_and_invalid_clock_or_cancel_signal (test_experiment_runner.RunnerTests.test_cancel_before_start_and_invalid_clock_or_cancel_signal) ... ok
test_cli_prepares_and_synthetic_demo_only (test_experiment_runner.RunnerTests.test_cli_prepares_and_synthetic_demo_only) ... ok
test_cli_training_arbitrary_command_invalid_and_safe_errors (test_experiment_runner.RunnerTests.test_cli_training_arbitrary_command_invalid_and_safe_errors) ... ok
test_config_schema_authorization_numeric_and_selection (test_experiment_runner.RunnerTests.test_config_schema_authorization_numeric_and_selection) ... ok
test_explicit_unchanged_no_face_model_and_structured_labels (test_experiment_runner.RunnerTests.test_explicit_unchanged_no_face_model_and_structured_labels) ... ok
test_final_readback_fault_never_leaves_a_success_receipt (test_experiment_runner.RunnerTests.test_final_readback_fault_never_leaves_a_success_receipt) ... ok
test_manifest_tamper_and_log_symlink_refused (test_experiment_runner.RunnerTests.test_manifest_tamper_and_log_symlink_refused) ... ok
test_prepare_exclusive_binding_and_immutable_snapshot (test_experiment_runner.RunnerTests.test_prepare_exclusive_binding_and_immutable_snapshot) ... ok
test_prepare_protocol_semantics_rebound_hashes (test_experiment_runner.RunnerTests.test_prepare_protocol_semantics_rebound_hashes) ... ok
test_prepare_refuses_unsafe_roots_and_changed_bindings (test_experiment_runner.RunnerTests.test_prepare_refuses_unsafe_roots_and_changed_bindings) ... ok
test_protocol_original_clip_count_and_fraction_contract_rebound (test_experiment_runner.RunnerTests.test_protocol_original_clip_count_and_fraction_contract_rebound) ... ok
test_publication_collision_and_fsync_failure_preserve_old_bytes (test_experiment_runner.RunnerTests.test_publication_collision_and_fsync_failure_preserve_old_bytes) ... ok
test_publication_interface_refuses_arbitrary_artifact_paths (test_experiment_runner.RunnerTests.test_publication_interface_refuses_arbitrary_artifact_paths) ... ok
test_selection_accuracy_then_macro_f1 (test_experiment_runner.RunnerTests.test_selection_accuracy_then_macro_f1) ... ok
test_strict_json_duplicate_and_nonfinite_rejected (test_experiment_runner.RunnerTests.test_strict_json_duplicate_and_nonfinite_rejected) ... ok
test_synthetic_input_and_manifest_change_fail_before_executor (test_experiment_runner.RunnerTests.test_synthetic_input_and_manifest_change_fail_before_executor) ... ok
test_synthetic_order_ties_immutable_request_and_no_retry (test_experiment_runner.RunnerTests.test_synthetic_order_ties_immutable_request_and_no_retry) ... ok
test_synthetic_output_tamper_has_no_success_receipt (test_experiment_runner.RunnerTests.test_synthetic_output_tamper_has_no_success_receipt) ... ok
test_synthetic_stop_conditions_and_safe_incomplete_logs (test_experiment_runner.RunnerTests.test_synthetic_stop_conditions_and_safe_incomplete_logs) ... ok
test_synthetic_stop_exception_text_never_echoed (test_experiment_runner.RunnerTests.test_synthetic_stop_exception_text_never_echoed) ... ok
test_accepts_only_frozen_checkpoint_from_validated_protocol (test_export_frozen.FrozenExportTests.test_accepts_only_frozen_checkpoint_from_validated_protocol) ... ok
test_frozen_export_preserves_validation_predictions_and_hashes (test_export_frozen.FrozenExportTests.test_frozen_export_preserves_validation_predictions_and_hashes) ... /Users/ahronjanl.rafaelahron.0804icloudcom/.kumpas-venvs/rv2-holistic-tf-20261101/lib/python3.11/site-packages/keras/src/backend/tensorflow/core.py:172: DeprecationWarning: __array__ implementation doesn't accept a copy keyword, so passing copy=False failed. __array__ must implement 'dtype' and 'copy' keyword arguments.
  return np.array(x)
WARNING: All log messages before absl::InitializeLog() is called are written to STDERR
I0000 00:00:1794513151.172793  805617 devices.cc:76] Number of eligible GPUs (core count >= 8, compute capability >= 0.0): 0 (Note: TensorFlow was not compiled with CUDA or ROCm support)
WARNING: All log messages before absl::InitializeLog() is called are written to STDERR
I0000 00:00:1794513151.173876  805617 single_machine.cc:374] Starting new session
WARNING:absl:Please consider providing the trackable_obj argument in the from_concrete_functions. Providing without the trackable_obj argument is deprecated and it will use the deprecated conversion path.
I0000 00:00:1794513151.204535  805617 devices.cc:76] Number of eligible GPUs (core count >= 8, compute capability >= 0.0): 0 (Note: TensorFlow was not compiled with CUDA or ROCm support)
I0000 00:00:1794513151.204591  805617 single_machine.cc:374] Starting new session
W0000 00:00:1794513151.220503  805617 tf_tfl_flatbuffer_helpers.cc:365] Ignored output_format.
W0000 00:00:1794513151.220516  805617 tf_tfl_flatbuffer_helpers.cc:368] Ignored drop_control_dependency.
2026-11-13 03:52:31.334737: I tensorflow/compiler/mlir/lite/flatbuffer_export.cc:4061] Estimated count of arithmetic ops: 0.031 M  ops, equivalently 0.016 M  MACs
/Users/ahronjanl.rafaelahron.0804icloudcom/.kumpas-venvs/rv2-holistic-tf-20261101/lib/python3.11/site-packages/tensorflow/lite/python/interpreter.py:457: UserWarning:     Warning: tf.lite.Interpreter is deprecated and is scheduled for deletion in
    TF 2.20. Please use the LiteRT interpreter from the ai_edge_litert package.
    See the [migration guide](https://ai.google.dev/edge/litert/migration)
    for details.
    
  warnings.warn(_INTERPRETER_DELETION_WARNING)
INFO: Created TensorFlow Lite XNNPACK delegate for CPU.
ok
test_rejects_checkpoint_changed_after_freeze (test_export_frozen.FrozenExportTests.test_rejects_checkpoint_changed_after_freeze) ... ok
test_rejects_other_protocol_manifest (test_export_frozen.FrozenExportTests.test_rejects_other_protocol_manifest) ... ok
test_load_explicit_unaugmented_validation (test_training_protocol.TrainingProtocolTests.test_load_explicit_unaugmented_validation) ... ok
test_selection_uses_validation_not_historical_test (test_training_protocol.TrainingProtocolTests.test_selection_uses_validation_not_historical_test) ... ok
test_source_tampering_prevents_training (test_training_protocol.TrainingProtocolTests.test_source_tampering_prevents_training) ... ok
test_backend_uses_inference_only_then_existing_candidate_and_checks_shapes (test_validation_campaign.BackendTests.test_backend_uses_inference_only_then_existing_candidate_and_checks_shapes) ... ok
test_metric_boundary_rejects_non_numeric_and_nonfinite_before_ranking (test_validation_campaign.CampaignTests.test_metric_boundary_rejects_non_numeric_and_nonfinite_before_ranking) ... ok
test_cli_requires_bound_strict_config_and_fixed_safe_errors (test_validation_campaign.CliTests.test_cli_requires_bound_strict_config_and_fixed_safe_errors) ... ok
test_diagnostics_all_classes_counts_and_conversion_drift (test_validation_campaign.DiagnosticTests.test_diagnostics_all_classes_counts_and_conversion_drift) ... ok
test_campaign_publishes_only_verified_outputs_and_retains_failures (test_validation_campaign.InputTests.test_campaign_publishes_only_verified_outputs_and_retains_failures) ... ok
test_campaign_refuses_existing_escape_symlink_and_invalid_input_without_success (test_validation_campaign.InputTests.test_campaign_refuses_existing_escape_symlink_and_invalid_input_without_success) ... ok
test_identity_graph_rejects_tampering_and_malformed_metadata (test_validation_campaign.InputTests.test_identity_graph_rejects_tampering_and_malformed_metadata) ... ok
test_metadata_rejects_nonfinite_and_binds_frames_sampling_and_missingness (test_validation_campaign.InputTests.test_metadata_rejects_nonfinite_and_binds_frames_sampling_and_missingness) ... ok
test_protocol_counts_require_exact_integers_with_rebound_hashes (test_validation_campaign.InputTests.test_protocol_counts_require_exact_integers_with_rebound_hashes) ... ok
test_reject_shape_compatible_validation_tampering_even_when_current_hash_rebound (test_validation_campaign.InputTests.test_reject_shape_compatible_validation_tampering_even_when_current_hash_rebound) ... ok
test_selection_identity_policy_types_rejected_with_rebound_hashes (test_validation_campaign.InputTests.test_selection_identity_policy_types_rejected_with_rebound_hashes) ... ok
test_probability_boundary_rejects_shape_type_and_nonfinite (test_validation_campaign.ProbabilityTests.test_probability_boundary_rejects_shape_type_and_nonfinite) ... ok
test_dataless_sources_fail_before_a_blocking_content_read (test_validation_campaign.ResidencyTests.test_dataless_sources_fail_before_a_blocking_content_read) ... ok

----------------------------------------------------------------------
Ran 51 tests in 9.516s

OK

```

### Slice 8 RED — compiler timeout must preserve partial attempt evidence

```sh
TMPDIR=/Users/ahronjanl.rafaelahron.0804icloudcom/.hermes/cache/scratch /Users/ahronjanl.rafaelahron.0804icloudcom/.kumpas-venvs/rv2-holistic-tf-20261101/bin/python -E -B -m unittest training.holistic_migration.tests.test_camera.BuildFailureTests -v
```

Exit: 1

stdout:
```text

```
stderr:
```text
test_compiler_timeout_keeps_partial_stdout_stderr_and_command (training.holistic_migration.tests.test_camera.BuildFailureTests.test_compiler_timeout_keeps_partial_stdout_stderr_and_command) ... ERROR

======================================================================
ERROR: test_compiler_timeout_keeps_partial_stdout_stderr_and_command (training.holistic_migration.tests.test_camera.BuildFailureTests.test_compiler_timeout_keeps_partial_stdout_stderr_and_command)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration/training/holistic_migration/tests/test_camera.py", line 119, in test_compiler_timeout_keeps_partial_stdout_stderr_and_command
    camera.build_helper(Path(folder),runner=timeout)
  File "/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration/training/holistic_migration/camera.py", line 146, in build_helper
    result = runner(command, env=env, capture_output=True, timeout=120, check=False)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration/training/holistic_migration/tests/test_camera.py", line 117, in timeout
    raise subprocess.TimeoutExpired(command, 120, output=b"partial compiler stdout",stderr=b"partial compiler stderr")
subprocess.TimeoutExpired: Command '['/usr/bin/swiftc', '-O', '-module-cache-path', '/Users/ahronjanl.rafaelahron.0804icloudcom/.hermes/cache/scratch/task-b-swift-module-cache', '/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration/training/holistic_migration/camera.swift', '-o', '/Users/ahronjanl.rafaelahron.0804icloudcom/.hermes/cache/scratch/task-b-build-failure-kle7pv0z/native-3f6896dd01cb4623abb2539ae950f11b/builtin-camera']' timed out after 120 seconds

----------------------------------------------------------------------
Ran 1 test in 0.002s

FAILED (errors=1)

```

### Slice 8 GREEN — preserved compiler timeout stdout/stderr/command and no success binding

```sh
TMPDIR=/Users/ahronjanl.rafaelahron.0804icloudcom/.hermes/cache/scratch /Users/ahronjanl.rafaelahron.0804icloudcom/.kumpas-venvs/rv2-holistic-tf-20261101/bin/python -E -B -m unittest training.holistic_migration.tests.test_camera.BuildFailureTests -v
```

Exit: 0

stdout:
```text

```
stderr:
```text
test_compiler_timeout_keeps_partial_stdout_stderr_and_command (training.holistic_migration.tests.test_camera.BuildFailureTests.test_compiler_timeout_keeps_partial_stdout_stderr_and_command) ... ok

----------------------------------------------------------------------
Ran 1 test in 0.001s

OK

```

### Additional boundary coverage (not historical RED)

Added constructor/build/packing/window/display/close/interrupt/no-frame fault coverage and an identity check that the default runtime uses the actual Task A detector and packer without importing MediaPipe/TensorFlow. These exercise already implemented behavior and are explicitly coverage-only GREEN, not invented earlier RED evidence.

### Coverage-only boundary fault matrix and actual shared callable identities

```sh
TMPDIR=/Users/ahronjanl.rafaelahron.0804icloudcom/.hermes/cache/scratch /Users/ahronjanl.rafaelahron.0804icloudcom/.kumpas-venvs/rv2-holistic-tf-20261101/bin/python -E -B -m unittest training.holistic_migration.tests.test_webcam.PreviewLoopTests -v
```

Exit: 0

stdout:
```text

```
stderr:
```text
test_additional_failure_stages_keep_disposition_and_teardown (training.holistic_migration.tests.test_webcam.PreviewLoopTests.test_additional_failure_stages_keep_disposition_and_teardown) ... ok
test_default_runtime_binds_actual_shared_detector_and_packer_without_loading_sdk (training.holistic_migration.tests.test_webcam.PreviewLoopTests.test_default_runtime_binds_actual_shared_detector_and_packer_without_loading_sdk) ... ok
test_errors_cleanup_fault_and_handshake_admission_before_detector (training.holistic_migration.tests.test_webcam.PreviewLoopTests.test_errors_cleanup_fault_and_handshake_admission_before_detector) ... ok
test_no_implicit_report_and_main_uses_same_runner (training.holistic_migration.tests.test_webcam.PreviewLoopTests.test_no_implicit_report_and_main_uses_same_runner) ... ok
test_quit_escape_window_close_and_deadline_release_all (training.holistic_migration.tests.test_webcam.PreviewLoopTests.test_quit_escape_window_close_and_deadline_release_all) ... ok

----------------------------------------------------------------------
Ran 5 tests in 0.498s

OK

```

### Retained external native build and real camera-free self-test

```sh
TMPDIR=/Users/ahronjanl.rafaelahron.0804icloudcom/.hermes/cache/scratch /Users/ahronjanl.rafaelahron.0804icloudcom/.kumpas-venvs/rv2-holistic-tf-20261101/bin/python -E -B -c 'from pathlib import Path
import subprocess
from training.holistic_migration import camera
binding = camera.build_helper(Path.home()/'"'"'KumpasBuilds/holistic-migration-data/task-b-native-build'"'"')
camera.verify_binding(binding)
print('"'"'BINDING RECEIPT:'"'"')
print(binding.receipt.read_text())
print('"'"'COMPILER STDOUT:'"'"')
print((binding.binary.parent/'"'"'compile.stdout'"'"').read_text())
print('"'"'COMPILER STDERR:'"'"')
print((binding.binary.parent/'"'"'compile.stderr'"'"').read_text())
print('"'"'COMPILE ATTEMPT:'"'"')
print((binding.binary.parent/'"'"'compile.json'"'"').read_text())
result = subprocess.run([str(binding.binary),'"'"'--self-test'"'"'],capture_output=True,text=True,timeout=10)
print('"'"'NATIVE SELF-TEST STDOUT:'"'"')
print(result.stdout)
print('"'"'NATIVE SELF-TEST STDERR:'"'"')
print(result.stderr)
print('"'"'NATIVE SELF-TEST EXIT:'"'"', result.returncode)
raise SystemExit(result.returncode)
'
```

Exit: 0

stdout:
```text
BINDING RECEIPT:
{"binary": "/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/task-b-native-build/native-16d9dd53c9914b48a305427364c8e9a0/builtin-camera", "binary_sha256": "d39e09d1696622081e5c511019fa6bba4445133ba6fafee4e7af4db35d4c6e83", "command": ["/usr/bin/swiftc", "-O", "-module-cache-path", "/Users/ahronjanl.rafaelahron.0804icloudcom/.hermes/cache/scratch/task-b-swift-module-cache", "/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration/training/holistic_migration/camera.swift", "-o", "/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/task-b-native-build/native-16d9dd53c9914b48a305427364c8e9a0/builtin-camera"], "schema": 1, "source": "/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration/training/holistic_migration/camera.swift", "source_sha256": "4837c7723ef484fcc05856be62240e3aaf85e6a685c5ff79d6709840b6701825", "tmpdir": "/Users/ahronjanl.rafaelahron.0804icloudcom/.hermes/cache/scratch"}

COMPILER STDOUT:

COMPILER STDERR:

COMPILE ATTEMPT:
{"command": ["/usr/bin/swiftc", "-O", "-module-cache-path", "/Users/ahronjanl.rafaelahron.0804icloudcom/.hermes/cache/scratch/task-b-swift-module-cache", "/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration/training/holistic_migration/camera.swift", "-o", "/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/task-b-native-build/native-16d9dd53c9914b48a305427364c8e9a0/builtin-camera"], "exit": 0, "source_sha256": "4837c7723ef484fcc05856be62240e3aaf85e6a685c5ff79d6709840b6701825", "terminal": "completed", "tmpdir": "/Users/ahronjanl.rafaelahron.0804icloudcom/.hermes/cache/scratch"}

NATIVE SELF-TEST STDOUT:
{"camera_access":false,"checks":["selection","row-padding","framing","reconfiguration","timestamps"],"status":"ok"}

NATIVE SELF-TEST STDERR:

NATIVE SELF-TEST EXIT: 0

```
stderr:
```text

```

### Final full new-package verification

```sh
TMPDIR=/Users/ahronjanl.rafaelahron.0804icloudcom/.hermes/cache/scratch /Users/ahronjanl.rafaelahron.0804icloudcom/.kumpas-venvs/rv2-holistic-tf-20261101/bin/python -E -B -m unittest discover -s training/holistic_migration/tests -v
```

Exit: 0

stdout:
```text

```
stderr:
```text
test_compiler_timeout_keeps_partial_stdout_stderr_and_command (test_camera.BuildFailureTests.test_compiler_timeout_keeps_partial_stdout_stderr_and_command) ... ok
test_binding_is_checked_before_process_spawn (test_camera.CaptureTests.test_binding_is_checked_before_process_spawn) ... ok
test_frame_failure_stderr_cap_and_terminate_kill_escalation (test_camera.CaptureTests.test_frame_failure_stderr_cap_and_terminate_kill_escalation) ... ok
test_latest_only_queue_and_owned_child_cleanup (test_camera.CaptureTests.test_latest_only_queue_and_owned_child_cleanup) ... ok
test_startup_eof_timeout_and_stderr_are_preserved (test_camera.CaptureTests.test_startup_eof_timeout_and_stderr_are_preserved) ... ok
test_actual_bgra_dimensions_and_builtin_identity_are_admitted (test_camera.HandshakeTests.test_actual_bgra_dimensions_and_builtin_identity_are_admitted) ... ok
test_ambiguous_or_nonbuiltin_metadata_is_rejected (test_camera.HandshakeTests.test_ambiguous_or_nonbuiltin_metadata_is_rejected) ... ok
test_build_rejects_relative_or_repository_directory_before_compiler (test_camera.NativeBindingTests.test_build_rejects_relative_or_repository_directory_before_compiler) ... ok
test_exact_source_compiles_and_pure_native_checks_need_no_camera (test_camera.NativeBindingTests.test_exact_source_compiles_and_pure_native_checks_need_no_camera) ... ok
test_partial_reads_actual_handshake_and_exact_frame (test_camera.PacketTests.test_partial_reads_actual_handshake_and_exact_frame) ... ok
test_repeated_or_regressing_timestamp_and_startup_limits (test_camera.PacketTests.test_repeated_or_regressing_timestamp_and_startup_limits) ... ok
test_short_oversized_and_invalid_timestamps_fail_closed (test_camera.PacketTests.test_short_oversized_and_invalid_timestamps_fail_closed) ... ok
test_construction_uses_tasks_video_cpu_and_disabled_optional_outputs (test_detector.DetectorPreflightTests.test_construction_uses_tasks_video_cpu_and_disabled_optional_outputs) ... ok
test_context_manager_closes_once_on_body_exception_and_is_not_reusable (test_detector.DetectorPreflightTests.test_context_manager_closes_once_on_body_exception_and_is_not_reusable) ... ok
test_conversion_failure_inside_context_releases_tracker (test_detector.DetectorPreflightTests.test_conversion_failure_inside_context_releases_tracker) ... ok
test_detect_feeds_unmirrored_rgb_to_video_and_returns_converted_frame (test_detector.DetectorPreflightTests.test_detect_feeds_unmirrored_rgb_to_video_and_returns_converted_frame) ... ok
test_invalid_api_rgb_or_timestamp_is_rejected_before_any_native_call (test_detector.DetectorPreflightTests.test_invalid_api_rgb_or_timestamp_is_rejected_before_any_native_call) ... ok
test_invalid_model_path_rejected_before_any_mediapipe_import (test_detector.DetectorPreflightTests.test_invalid_model_path_rejected_before_any_mediapipe_import) ... ok
test_native_failure_consumes_timestamp_and_context_still_closes (test_detector.DetectorPreflightTests.test_native_failure_consumes_timestamp_and_context_still_closes) ... ok
test_native_failure_inside_context_releases_tracker (test_detector.DetectorPreflightTests.test_native_failure_inside_context_releases_tracker) ... ok
test_noncontiguous_rgb_keeps_channel_order_and_observations (test_detector.DetectorPreflightTests.test_noncontiguous_rgb_keeps_channel_order_and_observations) ... ok
test_package_imports_are_lazy_without_mediapipe_or_tensorflow (test_detector.DetectorPreflightTests.test_package_imports_are_lazy_without_mediapipe_or_tensorflow) ... ok
test_timestamps_strictly_increase_per_instance_and_new_instance_resets (test_detector.DetectorPreflightTests.test_timestamps_strictly_increase_per_instance_and_new_instance_resets) ... ok
test_conversion_timestamp_is_exact_nonnegative_builtin_int (test_detector.ResultConversionTests.test_conversion_timestamp_is_exact_nonnegative_builtin_int) ... ok
test_empty_components_are_none_and_one_handed_results_remain_distinct (test_detector.ResultConversionTests.test_empty_components_are_none_and_one_handed_results_remain_distinct) ... ok
test_missing_or_none_pose_visibility_is_zero_not_fabricated_confidence (test_detector.ResultConversionTests.test_missing_or_none_pose_visibility_is_zero_not_fabricated_confidence) ... ok
test_nonfinite_or_nonnumeric_sdk_coordinates_raise_clear_value_error (test_detector.ResultConversionTests.test_nonfinite_or_nonnumeric_sdk_coordinates_raise_clear_value_error) ... ok
test_reads_flat_normalized_landmarks_not_world_coordinates (test_detector.ResultConversionTests.test_reads_flat_normalized_landmarks_not_world_coordinates) ... ok
test_requires_exact_pose_hand_counts_and_flat_sdk_shape (test_detector.ResultConversionTests.test_requires_exact_pose_hand_counts_and_flat_sdk_shape) ... ok
test_component_shapes_and_real_numeric_ndarrays_are_required (test_features.PackFrameTests.test_component_shapes_and_real_numeric_ndarrays_are_required) ... ok
test_does_not_mutate_or_alias_readonly_inputs_and_excludes_face (test_features.PackFrameTests.test_does_not_mutate_or_alias_readonly_inputs_and_excludes_face) ... ok
test_exact_layout_float32_row_major (test_features.PackFrameTests.test_exact_layout_float32_row_major) ... ok
test_finite_input_with_nonfinite_normalized_output_raises (test_features.PackFrameTests.test_finite_input_with_nonfinite_normalized_output_raises) ... ok
test_individual_missing_hands_keep_zero_block_and_other_hand (test_features.PackFrameTests.test_individual_missing_hands_keep_zero_block_and_other_hand) ... ok
test_integer_arrays_normalize_in_float_without_truncation (test_features.PackFrameTests.test_integer_arrays_normalize_in_float_without_truncation) ... ok
test_large_but_finite_shoulder_width_is_not_lost_to_squaring_overflow (test_features.PackFrameTests.test_large_but_finite_shoulder_width_is_not_lost_to_squaring_overflow) ... ok
test_low_visibility_pose_points_are_entirely_zeroed (test_features.PackFrameTests.test_low_visibility_pose_points_are_entirely_zeroed) ... ok
test_missing_pose_is_invalid_even_with_observed_hands (test_features.PackFrameTests.test_missing_pose_is_invalid_even_with_observed_hands) ... ok
test_nonfinite_raw_arrays_raise_even_when_pose_is_unusable (test_features.PackFrameTests.test_nonfinite_raw_arrays_raise_even_when_pose_is_unusable) ... ok
test_plain_numeric_arrays_and_strided_readonly_views_keep_packed_behavior (test_features.PackFrameTests.test_plain_numeric_arrays_and_strided_readonly_views_keep_packed_behavior) ... ok
test_raw_timestamp_requires_nonnegative_exact_builtin_int (test_features.PackFrameTests.test_raw_timestamp_requires_nonnegative_exact_builtin_int) ... ok
test_semantic_ndarray_subclasses_are_rejected_before_array_semantics (test_features.PackFrameTests.test_semantic_ndarray_subclasses_are_rejected_before_array_semantics) ... ok
test_translation_positive_scale_and_distinct_depth_origins (test_features.PackFrameTests.test_translation_positive_scale_and_distinct_depth_origins) ... ok
test_unreliable_shoulders_invalidate_without_hip_requirement (test_features.PackFrameTests.test_unreliable_shoulders_invalidate_without_hip_requirement) ... ok
test_valid_idle_observation_has_pose_and_no_hand_masks (test_features.PackFrameTests.test_valid_idle_observation_has_pose_and_no_hand_masks) ... ok
test_raw_frame_is_frozen_with_optional_face (test_features.RawFrameTests.test_raw_frame_is_frozen_with_optional_face) ... ok
test_default_resampling_is_nearest_time_with_earlier_ties (test_features.ResampleFramesTests.test_default_resampling_is_nearest_time_with_earlier_ties) ... ok
test_large_timestamp_origin_does_not_lose_nearest_ties (test_features.ResampleFramesTests.test_large_timestamp_origin_does_not_lose_nearest_ties) ... ok
test_missing_hands_and_idle_are_preserved_as_observations (test_features.ResampleFramesTests.test_missing_hands_and_idle_are_preserved_as_observations) ... ok
test_requires_two_actual_observations_and_exact_integer_steps (test_features.ResampleFramesTests.test_requires_two_actual_observations_and_exact_integer_steps) ... ok
test_timestamps_must_be_strictly_increasing_without_sorting (test_features.ResampleFramesTests.test_timestamps_must_be_strictly_increasing_without_sorting) ... ok
test_unusable_observation_breaks_sequence_even_when_not_sampled (test_features.ResampleFramesTests.test_unusable_observation_breaks_sequence_even_when_not_sampled) ... ok
test_invalid_duration_precedes_paths_and_runtime (test_webcam.AdmissionTests.test_invalid_duration_precedes_paths_and_runtime) ... ok
test_paths_and_report_overwrite_rejected_before_build (test_webcam.AdmissionTests.test_paths_and_report_overwrite_rejected_before_build) ... ok
test_actual_bgra_conversion_resize_and_no_input_mirror (test_webcam.PixelsAndOverlayTests.test_actual_bgra_conversion_resize_and_no_input_mirror) ... ok
test_missing_components_real_counts_masks_connections_and_readable_text (test_webcam.PixelsAndOverlayTests.test_missing_components_real_counts_masks_connections_and_readable_text) ... ok
test_additional_failure_stages_keep_disposition_and_teardown (test_webcam.PreviewLoopTests.test_additional_failure_stages_keep_disposition_and_teardown) ... ok
test_default_runtime_binds_actual_shared_detector_and_packer_without_loading_sdk (test_webcam.PreviewLoopTests.test_default_runtime_binds_actual_shared_detector_and_packer_without_loading_sdk) ... ok
test_errors_cleanup_fault_and_handshake_admission_before_detector (test_webcam.PreviewLoopTests.test_errors_cleanup_fault_and_handshake_admission_before_detector) ... ok
test_no_implicit_report_and_main_uses_same_runner (test_webcam.PreviewLoopTests.test_no_implicit_report_and_main_uses_same_runner) ... ok
test_quit_escape_window_close_and_deadline_release_all (test_webcam.PreviewLoopTests.test_quit_escape_window_close_and_deadline_release_all) ... ok

----------------------------------------------------------------------
Ran 61 tests in 4.642s

OK

```

### Final neighboring original training verification

```sh
TMPDIR=/Users/ahronjanl.rafaelahron.0804icloudcom/.hermes/cache/scratch /Users/ahronjanl.rafaelahron.0804icloudcom/.kumpas-venvs/rv2-holistic-tf-20261101/bin/python -E -B -m unittest discover -s training/tests -v
```

Exit: 0

stdout:
```text

```
stderr:
```text
test_conflicting_manifest_refuses_evaluation_before_loading_model (test_evaluate_frozen.FrozenEvaluationTests.test_conflicting_manifest_refuses_evaluation_before_loading_model) ... ok
test_missing_freeze_refuses_evaluation_before_loading_model (test_evaluate_frozen.FrozenEvaluationTests.test_missing_freeze_refuses_evaluation_before_loading_model) ... ok
test_no_automatic_selection_by_test_score (test_evaluate_frozen.FrozenEvaluationTests.test_no_automatic_selection_by_test_score) ... ok
test_report_labels_test_reuse_and_signer_uncertainty (test_evaluate_frozen.FrozenEvaluationTests.test_report_labels_test_reuse_and_signer_uncertainty) ... ok
test_duplicate_clip_name_is_rejected (test_evaluation_protocol.EvaluationProtocolTests.test_duplicate_clip_name_is_rejected) ... ok
test_mismatched_clip_count_is_rejected (test_evaluation_protocol.EvaluationProtocolTests.test_mismatched_clip_count_is_rejected) ... ok
test_original_clips_split_before_augmentation (test_evaluation_protocol.EvaluationProtocolTests.test_original_clips_split_before_augmentation) ... ok
test_original_train_test_clip_overlap_is_rejected (test_evaluation_protocol.EvaluationProtocolTests.test_original_train_test_clip_overlap_is_rejected) ... ok
test_source_digest_change_is_rejected (test_evaluation_protocol.EvaluationProtocolTests.test_source_digest_change_is_rejected) ... ok
test_binding_every_role_hash_symlink_and_array_refusal (test_experiment_runner.RunnerTests.test_binding_every_role_hash_symlink_and_array_refusal) ... ok
test_budget_exact_integer_matrix_and_variant_order_schema (test_experiment_runner.RunnerTests.test_budget_exact_integer_matrix_and_variant_order_schema) ... ok
test_cancel_before_start_and_invalid_clock_or_cancel_signal (test_experiment_runner.RunnerTests.test_cancel_before_start_and_invalid_clock_or_cancel_signal) ... ok
test_cli_prepares_and_synthetic_demo_only (test_experiment_runner.RunnerTests.test_cli_prepares_and_synthetic_demo_only) ... ok
test_cli_training_arbitrary_command_invalid_and_safe_errors (test_experiment_runner.RunnerTests.test_cli_training_arbitrary_command_invalid_and_safe_errors) ... ok
test_config_schema_authorization_numeric_and_selection (test_experiment_runner.RunnerTests.test_config_schema_authorization_numeric_and_selection) ... ok
test_explicit_unchanged_no_face_model_and_structured_labels (test_experiment_runner.RunnerTests.test_explicit_unchanged_no_face_model_and_structured_labels) ... ok
test_final_readback_fault_never_leaves_a_success_receipt (test_experiment_runner.RunnerTests.test_final_readback_fault_never_leaves_a_success_receipt) ... ok
test_manifest_tamper_and_log_symlink_refused (test_experiment_runner.RunnerTests.test_manifest_tamper_and_log_symlink_refused) ... ok
test_prepare_exclusive_binding_and_immutable_snapshot (test_experiment_runner.RunnerTests.test_prepare_exclusive_binding_and_immutable_snapshot) ... ok
test_prepare_protocol_semantics_rebound_hashes (test_experiment_runner.RunnerTests.test_prepare_protocol_semantics_rebound_hashes) ... ok
test_prepare_refuses_unsafe_roots_and_changed_bindings (test_experiment_runner.RunnerTests.test_prepare_refuses_unsafe_roots_and_changed_bindings) ... ok
test_protocol_original_clip_count_and_fraction_contract_rebound (test_experiment_runner.RunnerTests.test_protocol_original_clip_count_and_fraction_contract_rebound) ... ok
test_publication_collision_and_fsync_failure_preserve_old_bytes (test_experiment_runner.RunnerTests.test_publication_collision_and_fsync_failure_preserve_old_bytes) ... ok
test_publication_interface_refuses_arbitrary_artifact_paths (test_experiment_runner.RunnerTests.test_publication_interface_refuses_arbitrary_artifact_paths) ... ok
test_selection_accuracy_then_macro_f1 (test_experiment_runner.RunnerTests.test_selection_accuracy_then_macro_f1) ... ok
test_strict_json_duplicate_and_nonfinite_rejected (test_experiment_runner.RunnerTests.test_strict_json_duplicate_and_nonfinite_rejected) ... ok
test_synthetic_input_and_manifest_change_fail_before_executor (test_experiment_runner.RunnerTests.test_synthetic_input_and_manifest_change_fail_before_executor) ... ok
test_synthetic_order_ties_immutable_request_and_no_retry (test_experiment_runner.RunnerTests.test_synthetic_order_ties_immutable_request_and_no_retry) ... ok
test_synthetic_output_tamper_has_no_success_receipt (test_experiment_runner.RunnerTests.test_synthetic_output_tamper_has_no_success_receipt) ... ok
test_synthetic_stop_conditions_and_safe_incomplete_logs (test_experiment_runner.RunnerTests.test_synthetic_stop_conditions_and_safe_incomplete_logs) ... ok
test_synthetic_stop_exception_text_never_echoed (test_experiment_runner.RunnerTests.test_synthetic_stop_exception_text_never_echoed) ... ok
test_accepts_only_frozen_checkpoint_from_validated_protocol (test_export_frozen.FrozenExportTests.test_accepts_only_frozen_checkpoint_from_validated_protocol) ... ok
test_frozen_export_preserves_validation_predictions_and_hashes (test_export_frozen.FrozenExportTests.test_frozen_export_preserves_validation_predictions_and_hashes) ... /Users/ahronjanl.rafaelahron.0804icloudcom/.kumpas-venvs/rv2-holistic-tf-20261101/lib/python3.11/site-packages/keras/src/backend/tensorflow/core.py:172: DeprecationWarning: __array__ implementation doesn't accept a copy keyword, so passing copy=False failed. __array__ must implement 'dtype' and 'copy' keyword arguments.
  return np.array(x)
WARNING: All log messages before absl::InitializeLog() is called are written to STDERR
I0000 00:00:1794513387.673673  808232 devices.cc:76] Number of eligible GPUs (core count >= 8, compute capability >= 0.0): 0 (Note: TensorFlow was not compiled with CUDA or ROCm support)
WARNING: All log messages before absl::InitializeLog() is called are written to STDERR
I0000 00:00:1794513387.674756  808232 single_machine.cc:374] Starting new session
WARNING:absl:Please consider providing the trackable_obj argument in the from_concrete_functions. Providing without the trackable_obj argument is deprecated and it will use the deprecated conversion path.
I0000 00:00:1794513387.706326  808232 devices.cc:76] Number of eligible GPUs (core count >= 8, compute capability >= 0.0): 0 (Note: TensorFlow was not compiled with CUDA or ROCm support)
I0000 00:00:1794513387.706383  808232 single_machine.cc:374] Starting new session
W0000 00:00:1794513387.723336  808232 tf_tfl_flatbuffer_helpers.cc:365] Ignored output_format.
W0000 00:00:1794513387.723347  808232 tf_tfl_flatbuffer_helpers.cc:368] Ignored drop_control_dependency.
2026-11-13 03:56:27.838320: I tensorflow/compiler/mlir/lite/flatbuffer_export.cc:4061] Estimated count of arithmetic ops: 0.031 M  ops, equivalently 0.016 M  MACs
/Users/ahronjanl.rafaelahron.0804icloudcom/.kumpas-venvs/rv2-holistic-tf-20261101/lib/python3.11/site-packages/tensorflow/lite/python/interpreter.py:457: UserWarning:     Warning: tf.lite.Interpreter is deprecated and is scheduled for deletion in
    TF 2.20. Please use the LiteRT interpreter from the ai_edge_litert package.
    See the [migration guide](https://ai.google.dev/edge/litert/migration)
    for details.
    
  warnings.warn(_INTERPRETER_DELETION_WARNING)
INFO: Created TensorFlow Lite XNNPACK delegate for CPU.
ok
test_rejects_checkpoint_changed_after_freeze (test_export_frozen.FrozenExportTests.test_rejects_checkpoint_changed_after_freeze) ... ok
test_rejects_other_protocol_manifest (test_export_frozen.FrozenExportTests.test_rejects_other_protocol_manifest) ... ok
test_load_explicit_unaugmented_validation (test_training_protocol.TrainingProtocolTests.test_load_explicit_unaugmented_validation) ... ok
test_selection_uses_validation_not_historical_test (test_training_protocol.TrainingProtocolTests.test_selection_uses_validation_not_historical_test) ... ok
test_source_tampering_prevents_training (test_training_protocol.TrainingProtocolTests.test_source_tampering_prevents_training) ... ok
test_backend_uses_inference_only_then_existing_candidate_and_checks_shapes (test_validation_campaign.BackendTests.test_backend_uses_inference_only_then_existing_candidate_and_checks_shapes) ... ok
test_metric_boundary_rejects_non_numeric_and_nonfinite_before_ranking (test_validation_campaign.CampaignTests.test_metric_boundary_rejects_non_numeric_and_nonfinite_before_ranking) ... ok
test_cli_requires_bound_strict_config_and_fixed_safe_errors (test_validation_campaign.CliTests.test_cli_requires_bound_strict_config_and_fixed_safe_errors) ... ok
test_diagnostics_all_classes_counts_and_conversion_drift (test_validation_campaign.DiagnosticTests.test_diagnostics_all_classes_counts_and_conversion_drift) ... ok
test_campaign_publishes_only_verified_outputs_and_retains_failures (test_validation_campaign.InputTests.test_campaign_publishes_only_verified_outputs_and_retains_failures) ... ok
test_campaign_refuses_existing_escape_symlink_and_invalid_input_without_success (test_validation_campaign.InputTests.test_campaign_refuses_existing_escape_symlink_and_invalid_input_without_success) ... ok
test_identity_graph_rejects_tampering_and_malformed_metadata (test_validation_campaign.InputTests.test_identity_graph_rejects_tampering_and_malformed_metadata) ... ok
test_metadata_rejects_nonfinite_and_binds_frames_sampling_and_missingness (test_validation_campaign.InputTests.test_metadata_rejects_nonfinite_and_binds_frames_sampling_and_missingness) ... ok
test_protocol_counts_require_exact_integers_with_rebound_hashes (test_validation_campaign.InputTests.test_protocol_counts_require_exact_integers_with_rebound_hashes) ... ok
test_reject_shape_compatible_validation_tampering_even_when_current_hash_rebound (test_validation_campaign.InputTests.test_reject_shape_compatible_validation_tampering_even_when_current_hash_rebound) ... ok
test_selection_identity_policy_types_rejected_with_rebound_hashes (test_validation_campaign.InputTests.test_selection_identity_policy_types_rejected_with_rebound_hashes) ... ok
test_probability_boundary_rejects_shape_type_and_nonfinite (test_validation_campaign.ProbabilityTests.test_probability_boundary_rejects_shape_type_and_nonfinite) ... ok
test_dataless_sources_fail_before_a_blocking_content_read (test_validation_campaign.ResidencyTests.test_dataless_sources_fail_before_a_blocking_content_read) ... ok

----------------------------------------------------------------------
Ran 51 tests in 8.992s

OK

```

### Final CLI help (no camera/GUI)

```sh
TMPDIR=/Users/ahronjanl.rafaelahron.0804icloudcom/.hermes/cache/scratch /Users/ahronjanl.rafaelahron.0804icloudcom/.kumpas-venvs/rv2-holistic-tf-20261101/bin/python -E -B -m training.holistic_migration.webcam --help
```

Exit: 0

stdout:
```text
usage: webcam.py [-h] --model MODEL --build-dir BUILD_DIR
                 [--duration DURATION] [--report REPORT]

Built-in MacBook only; tracking, not sign recognition

options:
  -h, --help            show this help message and exit
  --model MODEL
  --build-dir BUILD_DIR
  --duration DURATION
  --report REPORT       optional exclusive operational JSON, never frames or
                        landmarks

```
stderr:
```text

```

### Final tracked-original diff (must remain empty)

```sh
TMPDIR=/Users/ahronjanl.rafaelahron.0804icloudcom/.hermes/cache/scratch git diff --stat
```

Exit: 0

stdout:
```text

```
stderr:
```text

```

### Final branch identity

```sh
TMPDIR=/Users/ahronjanl.rafaelahron.0804icloudcom/.hermes/cache/scratch git branch --show-current
```

Exit: 0

stdout:
```text
holistic-migration

```
stderr:
```text

```

### Final HEAD identity

```sh
TMPDIR=/Users/ahronjanl.rafaelahron.0804icloudcom/.hermes/cache/scratch git rev-parse HEAD
```

Exit: 0

stdout:
```text
4d901693642af5f572455b2c75ba095b0ec65c7f

```
stderr:
```text

```

### Final local timestamp

```sh
TMPDIR=/Users/ahronjanl.rafaelahron.0804icloudcom/.hermes/cache/scratch date '+%Y-%m-%d %H:%M:%S %Z'
```

Exit: 0

stdout:
```text
2026-11-13 03:56:30 PST

```
stderr:
```text

```

## Handoff — 2026-11-13 03:56 PST

**Task B implementation is ready for parent review/live launch; no live acceptance is claimed.**

- Preserved the landed handshake/PacketReader and original tests. Recovery started by executing the two existing native-binding tests: exit1, three missing-`build_helper` errors. No earlier RED was invented.
- Added native pure descriptor selection, padded-row BGRA packing, real big-endian `>dI` framing, reconfiguration rejection and strictly increasing integral-millisecond timestamp assertions. `--self-test` executes those production helpers and emits success only after their assertions; it does not enumerate/open a camera. The native capture branch discovers built-in-wide-angle devices only, filters Continuity, requires one eligible object and opens that exact object. Metadata-only `--discover` creates no capture session (not executed by this child).
- Added exact owned-source compilation, unique external build outputs, SHA-256 source/binary receipt and launch-time recheck. Compiler stdout/stderr/command/exit or timeout are retained separately. Module cache and TMPDIR remain under runtime scratch. The first real Swift attempt failed on a complex row-slice expression and a throwing autoclosure; both errors are retained above and fixed. The retained final compilation and self-test both exited0 with empty stderr.
- Added startup/frame deadlines, exact owned-child terminate/wait/kill cleanup, bounded16KiB stderr tail, and a one-pending-frame latest-only reader. Real synthetic subprocess tests prove EOF/timeout diagnostics, tail retention, queue overwrites, thread exit and SIGKILL escalation without camera access.
- Added actual-BGRA-to-unmirrored-RGB conversion and explicit640×360 processing, observed pose/hand connections, true face count, SDK-side labels, candidate masks, timing/FPS text and display-only mirroring. Controls: q/Escape exit, m toggles display mirror; window close/deadline/error/interrupt release all acquired resources even when a preceding close fails.
- The default runtime uses the actual shared `HolisticDetector`/`pack_frame`; it has no sign-classifier path. Invalid finite/bounded duration and invalid paths are rejected before runtime/compilation/camera work. Optional `--report` is exclusive and whitelists run/source/detector/native identities plus timing/counts/disposition; no default report, raw frames, video, landmark arrays or recognized strings are written. Every report has `live_acceptance:false`, including zero-person and zero-frame sessions.

### Final executed results

| Verification | Actual outcome |
|---|---|
| `python -E -B -m unittest discover -s training/holistic_migration/tests -v` | 61 tests, exit0; no skips/failures/errors |
| `python -E -B -m unittest discover -s training/tests -v` | 51 tests, exit0; existing Keras/TensorFlow/TFLite runtime/deprecation warnings retained above |
| Retained `/usr/bin/swiftc -O -module-cache-path ... camera.swift -o .../builtin-camera` | exit0; empty compiler stderr |
| Retained native `--self-test` | exit0; status=ok; selection/row-padding/framing/reconfiguration/timestamps; camera_access=false |
| Real CLI `--duration nan` | expected exit2 before invalid model/build access |
| Real CLI `--help` | exit0; no runtime launch |
| `git diff --stat` | empty: original tracked files unchanged |
| Branch/HEAD | `holistic-migration`, `4d901693642af5f572455b2c75ba095b0ec65c7f` |

Retained native receipt: `~/KumpasBuilds/holistic-migration-data/task-b-native-build/native-16d9dd53c9914b48a305427364c8e9a0/binding.json`. Compiler attempt/stdout/stderr and binary are alongside it. Swift source SHA-256: `4837c7723ef484fcc05856be62240e3aaf85e6a685c5ff79d6709840b6701825`; binary SHA-256: `d39e09d1696622081e5c511019fa6bba4445133ba6fafee4e7af4db35d4c6e83`. A preview invocation always compiles a new uniquely owned current-source build rather than trusting this binary by filename.

### Exact parent preview CLI — NOT executed by this child

```sh
cd /Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration
/Users/ahronjanl.rafaelahron.0804icloudcom/.kumpas-venvs/rv2-holistic-tf-20261101/bin/python -E -B -m training.holistic_migration.webcam \
  --model /Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/holistic_landmarker.task \
  --build-dir /Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/task-b-native-build \
  --duration 60
```

For an operational report, the parent may append `--report /absolute/external/new-name.json`; the parent directory must already exist and the file must not exist. Retain launcher stderr separately when running live; native errors are not mixed into binary stdout or retained in report fields.

### Remaining concerns and scope limits

- Parent must separately verify macOS permission, actual built-in frames, visible window/overlay, representative human tracking and bounded exit. The helper fails closed if the launching application is not already authorized for camera access; no permission prompts, TCC edits or live capture were exercised by this child.
- Pipe/startup/frame waits and loop admission are bounded, as is native requested capture duration. Synchronous MediaPipe constructor/inference and OS GUI calls are trusted native calls, not forcibly preemptible inside this Python process; this is not an adversarial-hang watchdog guarantee.
- Digest receipts bind current local files under the trusted local filesystem/compiler model; they are not independent hardware attestation or protection against a malicious concurrent local source/binary substitution. SDK left/right remain unvalidated anatomy.
- No measured live FPS, gesture accuracy, owner readiness, classifier/training, mobile or study gate is closed. Unit-boundary GREEN and native pure checks are not a live tracking pass. A fatal native Python/MediaPipe process abort can leave an explicitly requested reserved report incomplete; it must not be interpreted as success.
- Only the original six Task B owned source/test/report paths were changed. Task A acceptance JSON and Task A sources were not edited or re-audited. No installs, provider/config edits, camera/GUI launch, app/phone operations, commits or pushes occurred.


<!-- Task B recovery ledger -->


## Authorized bounded fix1 recovery — 2026-11-13T05:28:58.216169+08:00

Only L01/MR01 and L02 are being repaired, in vertical behavioral RED→GREEN slices. Task C implementer handoff is complete; its delivery remains historical. Current protection authority: `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-c-review-17292f00faaf47d2b96d74d43b8d3a7b/task-b-fix-protection.json`; all 20 protected paths match before repair. Only camera.py, webcam.py, their two owned tests and this append-only report are writable in-repository. No Swift/A/C/feature-contract edits, installs, model fitting, hardware/GUI launch, configuration changes, commits or pushes are authorized. Owner deferred webcam acceptance; parent retains re-review and acceptance.

Reviewed pre-append report SHA-256: `597e9e5c86747fbe20e0b362fbfd363937e7dc4fbf7449edcbe630269a30ea28`. Exact reviewed preimages and corrected parent harness are retained in `~/KumpasBuilds/holistic-migration-data/evidence/task-b-before-fix-8830ecffa4174cd98b6ecc4c7b1c3ea0/snapshot-index.json`. Historical parent corrected RED (6 tests, 5 failures, 0 errors) is not substituted for the current worker RED, which will execute before production edits. The initial synchronization-defective harness history is unchanged.

### fix1 current-parent-red

```sh
TMPDIR=/Users/ahronjanl.rafaelahron.0804icloudcom/.hermes/cache/scratch /Users/ahronjanl.rafaelahron.0804icloudcom/.kumpas-venvs/rv2-holistic-tf-20261101/bin/python -E -B /Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-b-before-fix-8830ecffa4174cd98b6ecc4c7b1c3ea0/parent_fault_regressions.py
```

Exit: 1; elapsed 0.459s. Full combined stdout/stderr: `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-b-fix1-31c5788ed4d844a2b6dc404eff56a039/current-parent-red.log` (SHA-256 `fc70368253478061e3868fc3aa3b044e86688bf7b4aa153ed800d52a01b1ace6`). Per-command source hashes and exact invocation: `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-b-fix1-31c5788ed4d844a2b6dc404eff56a039/commands.json`.

```text
test_frame_thread_start_failure_closes_pipes_and_preserves_primary (__main__.ReviewFaultRegressions.test_frame_thread_start_failure_closes_pipes_and_preserves_primary) ... FAIL
test_healthy_quit_is_not_a_source_failure (__main__.ReviewFaultRegressions.test_healthy_quit_is_not_a_source_failure) ... ok
test_source_failure_during_processing_then_deadline (__main__.ReviewFaultRegressions.test_source_failure_during_processing_then_deadline) ... FAIL
test_source_failure_during_processing_then_quit (__main__.ReviewFaultRegressions.test_source_failure_during_processing_then_quit) ... FAIL
test_source_failure_during_processing_then_window_close (__main__.ReviewFaultRegressions.test_source_failure_during_processing_then_window_close) ... FAIL
test_stderr_thread_start_failure_closes_pipes_and_preserves_primary (__main__.ReviewFaultRegressions.test_stderr_thread_start_failure_closes_pipes_and_preserves_primary) ... FAIL

======================================================================
FAIL: test_frame_thread_start_failure_closes_pipes_and_preserves_primary (__main__.ReviewFaultRegressions.test_frame_thread_start_failure_closes_pipes_and_preserves_primary)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-b-before-fix-8830ecffa4174cd98b6ecc4c7b1c3ea0/parent_fault_regressions.py", line 201, in test_frame_thread_start_failure_closes_pipes_and_preserves_primary
    self.thread_case("owned-camera-frames")
  File "/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-b-before-fix-8830ecffa4174cd98b6ecc4c7b1c3ea0/parent_fault_regressions.py", line 194, in thread_case
    self.assertTrue(observed["primary_preserved"] and observed["stdout_closed"] and
AssertionError: False is not true : {'kind': 'synthetic_thread_start_fault', 'failed_thread': 'owned-camera-frames', 'raised': 'RuntimeError', 'message': 'cannot join thread before it is started', 'primary_preserved': False, 'child_reaped': True, 'stdout_closed': False, 'stderr_closed': False}

======================================================================
FAIL: test_source_failure_during_processing_then_deadline (__main__.ReviewFaultRegressions.test_source_failure_during_processing_then_deadline)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-b-before-fix-8830ecffa4174cd98b6ecc4c7b1c3ea0/parent_fault_regressions.py", line 146, in test_source_failure_during_processing_then_deadline
    self.preview_case("deadline",True)
  File "/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-b-before-fix-8830ecffa4174cd98b6ecc4c7b1c3ea0/parent_fault_regressions.py", line 132, in preview_case
    self.assertTrue(error is not None and summary["terminal"] not in
AssertionError: False is not true : {'kind': 'synthetic_preview_fault', 'end_condition': 'deadline', 'terminal': 'deadline', 'native_exit': 7, 'reader_error': 'EOFError', 'returned_normally': True, 'processed': 1, 'raised': None, 'child_reaped': True, 'stdout_closed': True, 'stderr_closed': True, 'detector_closed': True, 'window_closed': True}

======================================================================
FAIL: test_source_failure_during_processing_then_quit (__main__.ReviewFaultRegressions.test_source_failure_during_processing_then_quit)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-b-before-fix-8830ecffa4174cd98b6ecc4c7b1c3ea0/parent_fault_regressions.py", line 140, in test_source_failure_during_processing_then_quit
    self.preview_case("quit",True)
  File "/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-b-before-fix-8830ecffa4174cd98b6ecc4c7b1c3ea0/parent_fault_regressions.py", line 132, in preview_case
    self.assertTrue(error is not None and summary["terminal"] not in
AssertionError: False is not true : {'kind': 'synthetic_preview_fault', 'end_condition': 'quit', 'terminal': 'quit', 'native_exit': 7, 'reader_error': 'EOFError', 'returned_normally': True, 'processed': 1, 'raised': None, 'child_reaped': True, 'stdout_closed': True, 'stderr_closed': True, 'detector_closed': True, 'window_closed': True}

======================================================================
FAIL: test_source_failure_during_processing_then_window_close (__main__.ReviewFaultRegressions.test_source_failure_during_processing_then_window_close)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-b-before-fix-8830ecffa4174cd98b6ecc4c7b1c3ea0/parent_fault_regressions.py", line 143, in test_source_failure_during_processing_then_window_close
    self.preview_case("window_closed",True)
  File "/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-b-before-fix-8830ecffa4174cd98b6ecc4c7b1c3ea0/parent_fault_regressions.py", line 132, in preview_case
    self.assertTrue(error is not None and summary["terminal"] not in
AssertionError: False is not true : {'kind': 'synthetic_preview_fault', 'end_condition': 'window_closed', 'terminal': 'window_closed', 'native_exit': 7, 'reader_error': 'EOFError', 'returned_normally': True, 'processed': 1, 'raised': None, 'child_reaped': True, 'stdout_closed': True, 'stderr_closed': True, 'detector_closed': True, 'window_closed': True}

======================================================================
FAIL: test_stderr_thread_start_failure_closes_pipes_and_preserves_primary (__main__.ReviewFaultRegressions.test_stderr_thread_start_failure_closes_pipes_and_preserves_primary)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-b-before-fix-8830ecffa4174cd98b6ecc4c7b1c3ea0/parent_fault_regressions.py", line 198, in test_stderr_thread_start_failure_closes_pipes_and_preserves_primary
    self.thread_case("owned-camera-stderr")
  File "/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-b-before-fix-8830ecffa4174cd98b6ecc4c7b1c3ea0/parent_fault_regressions.py", line 194, in thread_case
    self.assertTrue(observed["primary_preserved"] and observed["stdout_closed"] and
AssertionError: False is not true : {'kind': 'synthetic_thread_start_fault', 'failed_thread': 'owned-camera-stderr', 'raised': 'RuntimeError', 'message': 'cannot join thread before it is started', 'primary_preserved': False, 'child_reaped': True, 'stdout_closed': False, 'stderr_closed': False}

----------------------------------------------------------------------
Ran 6 tests in 0.246s

FAILED (failures=5)
PARENT_FAULT_RECEIPT /Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-b-before-fix-8830ecffa4174cd98b6ecc4c7b1c3ea0/parent-regression-runs/709112839aca4b5c935ad711b29817a5/observations.json

```

### fix1 slice1a-owned-terminal-red

```sh
TMPDIR=/Users/ahronjanl.rafaelahron.0804icloudcom/.hermes/cache/scratch /Users/ahronjanl.rafaelahron.0804icloudcom/.kumpas-venvs/rv2-holistic-tf-20261101/bin/python -E -B -m pytest -p no:cacheprovider training/holistic_migration/tests/test_webcam.py::SourceReconciliationTests -v
```

Exit: 1; elapsed 1.052s. Full combined stdout/stderr: `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-b-fix1-31c5788ed4d844a2b6dc404eff56a039/slice1a-owned-terminal-red.log` (SHA-256 `b7d332f7f693a41aa1da395cf3792d9593db920ba33c5f98bf55c77d91a194ef`). Per-command source hashes and exact invocation: `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-b-fix1-31c5788ed4d844a2b6dc404eff56a039/commands.json`.

```text
============================= test session starts ==============================
platform darwin -- Python 3.11.15, pytest-9.2.0, pluggy-1.7.0 -- /Users/ahronjanl.rafaelahron.0804icloudcom/.kumpas-venvs/rv2-holistic-tf-20261101/bin/python
rootdir: /Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration
collecting ... collected 6 items

training/holistic_migration/tests/test_webcam.py::SourceReconciliationTests::test_healthy_deadline_deliberately_terminates_owned_child PASSED [ 16%]
training/holistic_migration/tests/test_webcam.py::SourceReconciliationTests::test_healthy_quit_deliberately_terminates_owned_child PASSED [ 33%]
training/holistic_migration/tests/test_webcam.py::SourceReconciliationTests::test_observed_source_failure_then_deadline FAILED [ 50%]
training/holistic_migration/tests/test_webcam.py::SourceReconciliationTests::test_observed_source_failure_then_escape FAILED [ 66%]
training/holistic_migration/tests/test_webcam.py::SourceReconciliationTests::test_observed_source_failure_then_quit FAILED [ 83%]
training/holistic_migration/tests/test_webcam.py::SourceReconciliationTests::test_observed_source_failure_then_window_close FAILED [100%]

=================================== FAILURES ===================================
_____ SourceReconciliationTests.test_observed_source_failure_then_deadline _____

self = <holistic_migration.tests.test_webcam.SourceReconciliationTests testMethod=test_observed_source_failure_then_deadline>

    def test_observed_source_failure_then_deadline(self):
>       self.preview_case("deadline")

training/holistic_migration/tests/test_webcam.py:379: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
training/holistic_migration/tests/test_webcam.py:351: in preview_case
    self.assertIsInstance(error,camera.CaptureError)
E   AssertionError: None is not an instance of <class 'training.holistic_migration.camera.CaptureError'>
______ SourceReconciliationTests.test_observed_source_failure_then_escape ______

self = <holistic_migration.tests.test_webcam.SourceReconciliationTests testMethod=test_observed_source_failure_then_escape>

    def test_observed_source_failure_then_escape(self):
>       self.preview_case("escape")

training/holistic_migration/tests/test_webcam.py:373: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
training/holistic_migration/tests/test_webcam.py:351: in preview_case
    self.assertIsInstance(error,camera.CaptureError)
E   AssertionError: None is not an instance of <class 'training.holistic_migration.camera.CaptureError'>
_______ SourceReconciliationTests.test_observed_source_failure_then_quit _______

self = <holistic_migration.tests.test_webcam.SourceReconciliationTests testMethod=test_observed_source_failure_then_quit>

    def test_observed_source_failure_then_quit(self):
>       self.preview_case("quit")

training/holistic_migration/tests/test_webcam.py:370: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
training/holistic_migration/tests/test_webcam.py:351: in preview_case
    self.assertIsInstance(error,camera.CaptureError)
E   AssertionError: None is not an instance of <class 'training.holistic_migration.camera.CaptureError'>
___ SourceReconciliationTests.test_observed_source_failure_then_window_close ___

self = <holistic_migration.tests.test_webcam.SourceReconciliationTests testMethod=test_observed_source_failure_then_window_close>

    def test_observed_source_failure_then_window_close(self):
>       self.preview_case("window_closed")

training/holistic_migration/tests/test_webcam.py:376: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
training/holistic_migration/tests/test_webcam.py:351: in preview_case
    self.assertIsInstance(error,camera.CaptureError)
E   AssertionError: None is not an instance of <class 'training.holistic_migration.camera.CaptureError'>
=========================== short test summary info ============================
FAILED training/holistic_migration/tests/test_webcam.py::SourceReconciliationTests::test_observed_source_failure_then_deadline
FAILED training/holistic_migration/tests/test_webcam.py::SourceReconciliationTests::test_observed_source_failure_then_escape
FAILED training/holistic_migration/tests/test_webcam.py::SourceReconciliationTests::test_observed_source_failure_then_quit
FAILED training/holistic_migration/tests/test_webcam.py::SourceReconciliationTests::test_observed_source_failure_then_window_close
========================= 4 failed, 2 passed in 0.69s ==========================

```

Slice1a diagnosis: the reader already retained EOFError during current-frame processing, but only next_frame promoted it to CaptureError. Normal terminal paths bypassed that call. Current production-seam RED has 4 expected disposition failures, 2 healthy-control passes, no harness errors; every fault reached exit7/EOF and cleanup before the failing outcome assertion.

### fix1 slice1a-owned-terminal-green

```sh
TMPDIR=/Users/ahronjanl.rafaelahron.0804icloudcom/.hermes/cache/scratch /Users/ahronjanl.rafaelahron.0804icloudcom/.kumpas-venvs/rv2-holistic-tf-20261101/bin/python -E -B -m pytest -p no:cacheprovider training/holistic_migration/tests/test_webcam.py -v
```

Exit: 0; elapsed 0.887s. Full combined stdout/stderr: `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-b-fix1-31c5788ed4d844a2b6dc404eff56a039/slice1a-owned-terminal-green.log` (SHA-256 `6e474a9bb6457df04e029d3b98955d3670f074968398006ff3931913a5c8850c`). Per-command source hashes and exact invocation: `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-b-fix1-31c5788ed4d844a2b6dc404eff56a039/commands.json`.

```text
============================= test session starts ==============================
platform darwin -- Python 3.11.15, pytest-9.2.0, pluggy-1.7.0 -- /Users/ahronjanl.rafaelahron.0804icloudcom/.kumpas-venvs/rv2-holistic-tf-20261101/bin/python
rootdir: /Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration
collecting ... collected 15 items

training/holistic_migration/tests/test_webcam.py::AdmissionTests::test_invalid_duration_precedes_paths_and_runtime 
training/holistic_migration/tests/test_webcam.py::AdmissionTests::test_invalid_duration_precedes_paths_and_runtime PASSED [  6%]
training/holistic_migration/tests/test_webcam.py::AdmissionTests::test_paths_and_report_overwrite_rejected_before_build 
training/holistic_migration/tests/test_webcam.py::AdmissionTests::test_paths_and_report_overwrite_rejected_before_build PASSED [ 13%]
training/holistic_migration/tests/test_webcam.py::PixelsAndOverlayTests::test_actual_bgra_conversion_resize_and_no_input_mirror PASSED [ 20%]
training/holistic_migration/tests/test_webcam.py::PixelsAndOverlayTests::test_missing_components_real_counts_masks_connections_and_readable_text PASSED [ 26%]
training/holistic_migration/tests/test_webcam.py::PreviewLoopTests::test_additional_failure_stages_keep_disposition_and_teardown 
training/holistic_migration/tests/test_webcam.py::PreviewLoopTests::test_additional_failure_stages_keep_disposition_and_teardown PASSED [ 33%]
training/holistic_migration/tests/test_webcam.py::PreviewLoopTests::test_default_runtime_binds_actual_shared_detector_and_packer_without_loading_sdk PASSED [ 40%]
training/holistic_migration/tests/test_webcam.py::PreviewLoopTests::test_errors_cleanup_fault_and_handshake_admission_before_detector 
training/holistic_migration/tests/test_webcam.py::PreviewLoopTests::test_errors_cleanup_fault_and_handshake_admission_before_detector PASSED [ 46%]
training/holistic_migration/tests/test_webcam.py::PreviewLoopTests::test_no_implicit_report_and_main_uses_same_runner PASSED [ 53%]
training/holistic_migration/tests/test_webcam.py::PreviewLoopTests::test_quit_escape_window_close_and_deadline_release_all 
training/holistic_migration/tests/test_webcam.py::PreviewLoopTests::test_quit_escape_window_close_and_deadline_release_all PASSED [ 60%]
training/holistic_migration/tests/test_webcam.py::SourceReconciliationTests::test_healthy_deadline_deliberately_terminates_owned_child PASSED [ 66%]
training/holistic_migration/tests/test_webcam.py::SourceReconciliationTests::test_healthy_quit_deliberately_terminates_owned_child PASSED [ 73%]
training/holistic_migration/tests/test_webcam.py::SourceReconciliationTests::test_observed_source_failure_then_deadline PASSED [ 80%]
training/holistic_migration/tests/test_webcam.py::SourceReconciliationTests::test_observed_source_failure_then_escape PASSED [ 86%]
training/holistic_migration/tests/test_webcam.py::SourceReconciliationTests::test_observed_source_failure_then_quit PASSED [ 93%]
training/holistic_migration/tests/test_webcam.py::SourceReconciliationTests::test_observed_source_failure_then_window_close PASSED [100%]

==================== 15 passed, 30 subtests passed in 0.52s ====================

```

### fix1 slice1b-unpublished-exit-red

```sh
TMPDIR=/Users/ahronjanl.rafaelahron.0804icloudcom/.hermes/cache/scratch /Users/ahronjanl.rafaelahron.0804icloudcom/.kumpas-venvs/rv2-holistic-tf-20261101/bin/python -E -B -m pytest -p no:cacheprovider training/holistic_migration/tests/test_webcam.py::SourceReconciliationTests::test_unexpected_child_exit_before_reader_publishes_error -v
```

Exit: 1; elapsed 0.952s. Full combined stdout/stderr: `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-b-fix1-31c5788ed4d844a2b6dc404eff56a039/slice1b-unpublished-exit-red.log` (SHA-256 `1626e144d991834275cf21b63888e3f5f651d2ff064ce5ebae89ebebd1603ae4`). Per-command source hashes and exact invocation: `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-b-fix1-31c5788ed4d844a2b6dc404eff56a039/commands.json`.

```text
============================= test session starts ==============================
platform darwin -- Python 3.11.15, pytest-9.2.0, pluggy-1.7.0 -- /Users/ahronjanl.rafaelahron.0804icloudcom/.kumpas-venvs/rv2-holistic-tf-20261101/bin/python
rootdir: /Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration
collecting ... collected 1 item

training/holistic_migration/tests/test_webcam.py::SourceReconciliationTests::test_unexpected_child_exit_before_reader_publishes_error FAILED [100%]

=================================== FAILURES ===================================
_ SourceReconciliationTests.test_unexpected_child_exit_before_reader_publishes_error _

self = <holistic_migration.tests.test_webcam.SourceReconciliationTests testMethod=test_unexpected_child_exit_before_reader_publishes_error>

    def test_unexpected_child_exit_before_reader_publishes_error(self):
>       self.preview_case("quit",defer_reader=True)

training/holistic_migration/tests/test_webcam.py:405: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
training/holistic_migration/tests/test_webcam.py:360: in preview_case
    self.assertEqual(summary.get("source_failure"),fault)
E   AssertionError: False != True
=========================== short test summary info ============================
FAILED training/holistic_migration/tests/test_webcam.py::SourceReconciliationTests::test_unexpected_child_exit_before_reader_publishes_error
============================== 1 failed in 0.49s ===============================

```

### fix1 slice1b-unpublished-exit-green

```sh
TMPDIR=/Users/ahronjanl.rafaelahron.0804icloudcom/.hermes/cache/scratch /Users/ahronjanl.rafaelahron.0804icloudcom/.kumpas-venvs/rv2-holistic-tf-20261101/bin/python -E -B -m pytest -p no:cacheprovider training/holistic_migration/tests/test_webcam.py::SourceReconciliationTests -v
```

Exit: 0; elapsed 1.282s. Full combined stdout/stderr: `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-b-fix1-31c5788ed4d844a2b6dc404eff56a039/slice1b-unpublished-exit-green.log` (SHA-256 `1890c0d3da92abd3ef5371a7bef35dd6ce1618a34a8e39174acaf10d019daba6`). Per-command source hashes and exact invocation: `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-b-fix1-31c5788ed4d844a2b6dc404eff56a039/commands.json`.

```text
============================= test session starts ==============================
platform darwin -- Python 3.11.15, pytest-9.2.0, pluggy-1.7.0 -- /Users/ahronjanl.rafaelahron.0804icloudcom/.kumpas-venvs/rv2-holistic-tf-20261101/bin/python
rootdir: /Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration
collecting ... collected 7 items

training/holistic_migration/tests/test_webcam.py::SourceReconciliationTests::test_healthy_deadline_deliberately_terminates_owned_child PASSED [ 14%]
training/holistic_migration/tests/test_webcam.py::SourceReconciliationTests::test_healthy_quit_deliberately_terminates_owned_child PASSED [ 28%]
training/holistic_migration/tests/test_webcam.py::SourceReconciliationTests::test_observed_source_failure_then_deadline PASSED [ 42%]
training/holistic_migration/tests/test_webcam.py::SourceReconciliationTests::test_observed_source_failure_then_escape PASSED [ 57%]
training/holistic_migration/tests/test_webcam.py::SourceReconciliationTests::test_observed_source_failure_then_quit PASSED [ 71%]
training/holistic_migration/tests/test_webcam.py::SourceReconciliationTests::test_observed_source_failure_then_window_close PASSED [ 85%]
training/holistic_migration/tests/test_webcam.py::SourceReconciliationTests::test_unexpected_child_exit_before_reader_publishes_error PASSED [100%]

============================== 7 passed in 0.77s ===============================

```


## L02-only continuation recovery — 2026-11-13T10:57:37.324033+08:00

Resumed the actual landed L01 source and seven SourceReconciliationTests without replaying or reverting that repair. Parent resume receipts: `~/KumpasBuilds/holistic-migration-data/evidence/resume-20261113-731418e16ea04e1e84ae4898404ac9bc/verification.json` (7 passed; corrected parent harness 6 cases with only the 2 L02 failures). Prior recovery/RED/GREEN above is preserved verbatim. Fresh immutable continuation preimages: `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-b-l02-resume-20261113-e79f7bd38c3141fa8d4c78a309234a7d/snapshot-index.json`; report pre-append SHA-256 `97d15a129576776aa3a68873deae05dd510c6db76893d308a6c170dbea5d7c79`. All 20 protected A/C/Swift/contract hashes match before this continuation (`protection-before.json`). Only camera.py/test_camera.py and append-only reporting are expected to change for L02; webcam.py/test_webcam.py remain the landed L01 control. No hardware/GUI/model fitting, installs, commits/pushes or provider/configuration changes. Current actual L02 RED will be executed before any production edit; exact commands/exits/logs/source hashes will be appended immediately per vertical slice.


### L02 continuation slice2a-stderr-start-red

```sh
TMPDIR=/Users/ahronjanl.rafaelahron.0804icloudcom/.hermes/cache/scratch /Users/ahronjanl.rafaelahron.0804icloudcom/.kumpas-venvs/rv2-holistic-tf-20261101/bin/python -E -B -m pytest -p no:cacheprovider training/holistic_migration/tests/test_camera.py::ConstructorRollbackTests::test_stderr_thread_start_failure_rolls_back_owned_resources -v
```

Actual exit: 1; elapsed: 0.474s; timeout: False. Full stdout/stderr: `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-b-l02-resume-20261113-e79f7bd38c3141fa8d4c78a309234a7d/slice2a-stderr-start-red.log` (SHA-256 `d9e1348d49ae9260f4678baa8dc56f759e4fbe0cf4575843d83d85e9ea1ab011`). Exact command, before-run source hashes and 20 protected matches: `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-b-l02-resume-20261113-e79f7bd38c3141fa8d4c78a309234a7d/slice2a-stderr-start-red.json`.

```text
============================= test session starts ==============================
platform darwin -- Python 3.11.15, pytest-9.2.0, pluggy-1.7.0 -- /Users/ahronjanl.rafaelahron.0804icloudcom/.kumpas-venvs/rv2-holistic-tf-20261101/bin/python
rootdir: /Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration
collecting ... collected 1 item

training/holistic_migration/tests/test_camera.py::ConstructorRollbackTests::test_stderr_thread_start_failure_rolls_back_owned_resources FAILED [100%]

=================================== FAILURES ===================================
_ ConstructorRollbackTests.test_stderr_thread_start_failure_rolls_back_owned_resources _

self = <holistic_migration.tests.test_camera.ConstructorRollbackTests testMethod=test_stderr_thread_start_failure_rolls_back_owned_resources>

    def test_stderr_thread_start_failure_rolls_back_owned_resources(self):
>       self.thread_start_fault("owned-camera-stderr")

training/holistic_migration/tests/test_camera.py:265: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
training/holistic_migration/tests/test_camera.py:248: in thread_start_fault
    self.assertTrue(error is marker or getattr(error, "__cause__", None) is marker,
E   AssertionError: False is not true : acquisition must remain primary, got RuntimeError('cannot join thread before it is started')
=========================== short test summary info ============================
FAILED training/holistic_migration/tests/test_camera.py::ConstructorRollbackTests::test_stderr_thread_start_failure_rolls_back_owned_resources
============================== 1 failed in 0.07s ===============================

```


### L02 continuation slice2a-stderr-start-green

```sh
TMPDIR=/Users/ahronjanl.rafaelahron.0804icloudcom/.hermes/cache/scratch /Users/ahronjanl.rafaelahron.0804icloudcom/.kumpas-venvs/rv2-holistic-tf-20261101/bin/python -E -B -m pytest -p no:cacheprovider training/holistic_migration/tests/test_camera.py::ConstructorRollbackTests::test_stderr_thread_start_failure_rolls_back_owned_resources -v
```

Actual exit: 0; elapsed: 0.431s; timeout: False. Full stdout/stderr: `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-b-l02-resume-20261113-e79f7bd38c3141fa8d4c78a309234a7d/slice2a-stderr-start-green.log` (SHA-256 `3280e7706684462e75687fd562968bab1040813d6b8c063550d4e91dacc60579`). Exact command, before-run source hashes and 20 protected matches: `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-b-l02-resume-20261113-e79f7bd38c3141fa8d4c78a309234a7d/slice2a-stderr-start-green.json`.

```text
============================= test session starts ==============================
platform darwin -- Python 3.11.15, pytest-9.2.0, pluggy-1.7.0 -- /Users/ahronjanl.rafaelahron.0804icloudcom/.kumpas-venvs/rv2-holistic-tf-20261101/bin/python
rootdir: /Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration
collecting ... collected 1 item

training/holistic_migration/tests/test_camera.py::ConstructorRollbackTests::test_stderr_thread_start_failure_rolls_back_owned_resources PASSED [100%]

============================== 1 passed in 0.05s ===============================

```


### L02 continuation slice2b-frame-start-coverage-green

```sh
TMPDIR=/Users/ahronjanl.rafaelahron.0804icloudcom/.hermes/cache/scratch /Users/ahronjanl.rafaelahron.0804icloudcom/.kumpas-venvs/rv2-holistic-tf-20261101/bin/python -E -B -m pytest -p no:cacheprovider training/holistic_migration/tests/test_camera.py::ConstructorRollbackTests -v
```

Actual exit: 0; elapsed: 0.526s; timeout: False. Full stdout/stderr: `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-b-l02-resume-20261113-e79f7bd38c3141fa8d4c78a309234a7d/slice2b-frame-start-coverage-green.log` (SHA-256 `13c782f361f0023080fa9b25e16da74576800d16910016c9eeaf0a3a69843cdb`). Exact command, before-run source hashes and 20 protected matches: `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-b-l02-resume-20261113-e79f7bd38c3141fa8d4c78a309234a7d/slice2b-frame-start-coverage-green.json`.

```text
============================= test session starts ==============================
platform darwin -- Python 3.11.15, pytest-9.2.0, pluggy-1.7.0 -- /Users/ahronjanl.rafaelahron.0804icloudcom/.kumpas-venvs/rv2-holistic-tf-20261101/bin/python
rootdir: /Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration
collecting ... collected 2 items

training/holistic_migration/tests/test_camera.py::ConstructorRollbackTests::test_frame_thread_start_failure_rolls_back_owned_resources PASSED [ 50%]
training/holistic_migration/tests/test_camera.py::ConstructorRollbackTests::test_stderr_thread_start_failure_rolls_back_owned_resources PASSED [100%]

============================== 2 passed in 0.08s ===============================

```


### L02 continuation slice2c-join-retry-red

```sh
TMPDIR=/Users/ahronjanl.rafaelahron.0804icloudcom/.hermes/cache/scratch /Users/ahronjanl.rafaelahron.0804icloudcom/.kumpas-venvs/rv2-holistic-tf-20261101/bin/python -E -B -m pytest -p no:cacheprovider training/holistic_migration/tests/test_camera.py::TeardownRetryTests::test_join_failure_attempts_later_join_and_both_pipes_then_allows_retry -v
```

Actual exit: 1; elapsed: 0.370s; timeout: False. Full stdout/stderr: `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-b-l02-resume-20261113-e79f7bd38c3141fa8d4c78a309234a7d/slice2c-join-retry-red.log` (SHA-256 `80ba8724625a3e9fba74fd3b326f7c40303bb3829312fac449214e80c0bd00b7`). Exact command, before-run source hashes and 20 protected matches: `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-b-l02-resume-20261113-e79f7bd38c3141fa8d4c78a309234a7d/slice2c-join-retry-red.json`.

```text
============================= test session starts ==============================
platform darwin -- Python 3.11.15, pytest-9.2.0, pluggy-1.7.0 -- /Users/ahronjanl.rafaelahron.0804icloudcom/.kumpas-venvs/rv2-holistic-tf-20261101/bin/python
rootdir: /Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration
collecting ... collected 1 item

training/holistic_migration/tests/test_camera.py::TeardownRetryTests::test_join_failure_attempts_later_join_and_both_pipes_then_allows_retry FAILED [100%]

=================================== FAILURES ===================================
_ TeardownRetryTests.test_join_failure_attempts_later_join_and_both_pipes_then_allows_retry _

self = <holistic_migration.tests.test_camera.TeardownRetryTests testMethod=test_join_failure_attempts_later_join_and_both_pipes_then_allows_retry>

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
>               self.assertEqual(later_join.call_count, 1, "one join must not abort the next")
E               AssertionError: 0 != 1 : one join must not abort the next

training/holistic_migration/tests/test_camera.py:302: AssertionError
=========================== short test summary info ============================
FAILED training/holistic_migration/tests/test_camera.py::TeardownRetryTests::test_join_failure_attempts_later_join_and_both_pipes_then_allows_retry
============================== 1 failed in 0.07s ===============================

```


### L02 continuation slice2c-join-retry-green

```sh
TMPDIR=/Users/ahronjanl.rafaelahron.0804icloudcom/.hermes/cache/scratch /Users/ahronjanl.rafaelahron.0804icloudcom/.kumpas-venvs/rv2-holistic-tf-20261101/bin/python -E -B -m pytest -p no:cacheprovider training/holistic_migration/tests/test_camera.py::TeardownRetryTests -v
```

Actual exit: 0; elapsed: 0.385s; timeout: False. Full stdout/stderr: `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-b-l02-resume-20261113-e79f7bd38c3141fa8d4c78a309234a7d/slice2c-join-retry-green.log` (SHA-256 `67bf218c923163a404cfe42dec5c50257730606187af581ec45ec9b8e20116fb`). Exact command, before-run source hashes and 20 protected matches: `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-b-l02-resume-20261113-e79f7bd38c3141fa8d4c78a309234a7d/slice2c-join-retry-green.json`.

```text
============================= test session starts ==============================
platform darwin -- Python 3.11.15, pytest-9.2.0, pluggy-1.7.0 -- /Users/ahronjanl.rafaelahron.0804icloudcom/.kumpas-venvs/rv2-holistic-tf-20261101/bin/python
rootdir: /Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration
collecting ... collected 1 item

training/holistic_migration/tests/test_camera.py::TeardownRetryTests::test_join_failure_attempts_later_join_and_both_pipes_then_allows_retry PASSED [100%]

============================== 1 passed in 0.06s ===============================

```


### L02 continuation slice2d-pipe-retry-red

```sh
TMPDIR=/Users/ahronjanl.rafaelahron.0804icloudcom/.hermes/cache/scratch /Users/ahronjanl.rafaelahron.0804icloudcom/.kumpas-venvs/rv2-holistic-tf-20261101/bin/python -E -B -m pytest -p no:cacheprovider training/holistic_migration/tests/test_camera.py::TeardownRetryTests::test_stdout_close_failure_still_closes_stderr_and_retries_incomplete_pipe -v
```

Actual exit: 1; elapsed: 0.427s; timeout: False. Full stdout/stderr: `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-b-l02-resume-20261113-e79f7bd38c3141fa8d4c78a309234a7d/slice2d-pipe-retry-red.log` (SHA-256 `798b739e66777f3c0c5e72d7331501f00c88cabae60065a1ec54d99423e15387`). Exact command, before-run source hashes and 20 protected matches: `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-b-l02-resume-20261113-e79f7bd38c3141fa8d4c78a309234a7d/slice2d-pipe-retry-red.json`.

```text
============================= test session starts ==============================
platform darwin -- Python 3.11.15, pytest-9.2.0, pluggy-1.7.0 -- /Users/ahronjanl.rafaelahron.0804icloudcom/.kumpas-venvs/rv2-holistic-tf-20261101/bin/python
rootdir: /Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration
collecting ... collected 1 item

training/holistic_migration/tests/test_camera.py::TeardownRetryTests::test_stdout_close_failure_still_closes_stderr_and_retries_incomplete_pipe FAILED [100%]

=================================== FAILURES ===================================
_ TeardownRetryTests.test_stdout_close_failure_still_closes_stderr_and_retries_incomplete_pipe _

self = <holistic_migration.tests.test_camera.TeardownRetryTests testMethod=test_stdout_close_failure_still_closes_stderr_and_retries_incomplete_pipe>

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
>               self.assertEqual(later_close.call_count, 1, "one pipe must not abort the next")
E               AssertionError: 0 != 1 : one pipe must not abort the next

training/holistic_migration/tests/test_camera.py:311: AssertionError
=========================== short test summary info ============================
FAILED training/holistic_migration/tests/test_camera.py::TeardownRetryTests::test_stdout_close_failure_still_closes_stderr_and_retries_incomplete_pipe
============================== 1 failed in 0.08s ===============================

```


### L02 continuation slice2d-pipe-retry-green

```sh
TMPDIR=/Users/ahronjanl.rafaelahron.0804icloudcom/.hermes/cache/scratch /Users/ahronjanl.rafaelahron.0804icloudcom/.kumpas-venvs/rv2-holistic-tf-20261101/bin/python -E -B -m pytest -p no:cacheprovider training/holistic_migration/tests/test_camera.py::TeardownRetryTests -v
```

Actual exit: 0; elapsed: 0.428s; timeout: False. Full stdout/stderr: `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-b-l02-resume-20261113-e79f7bd38c3141fa8d4c78a309234a7d/slice2d-pipe-retry-green.log` (SHA-256 `2dbe69f757e36b2795132b44a7aecb5d392c011f49df1199c40901f841a1a3f9`). Exact command, before-run source hashes and 20 protected matches: `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-b-l02-resume-20261113-e79f7bd38c3141fa8d4c78a309234a7d/slice2d-pipe-retry-green.json`.

```text
============================= test session starts ==============================
platform darwin -- Python 3.11.15, pytest-9.2.0, pluggy-1.7.0 -- /Users/ahronjanl.rafaelahron.0804icloudcom/.kumpas-venvs/rv2-holistic-tf-20261101/bin/python
rootdir: /Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration
collecting ... collected 2 items

training/holistic_migration/tests/test_camera.py::TeardownRetryTests::test_join_failure_attempts_later_join_and_both_pipes_then_allows_retry PASSED [ 50%]
training/holistic_migration/tests/test_camera.py::TeardownRetryTests::test_stdout_close_failure_still_closes_stderr_and_retries_incomplete_pipe PASSED [100%]

============================== 2 passed in 0.09s ===============================

```


### L02 continuation slice2e-primary-rollback-red

```sh
TMPDIR=/Users/ahronjanl.rafaelahron.0804icloudcom/.hermes/cache/scratch /Users/ahronjanl.rafaelahron.0804icloudcom/.kumpas-venvs/rv2-holistic-tf-20261101/bin/python -E -B -m pytest -p no:cacheprovider training/holistic_migration/tests/test_camera.py::ConstructorRollbackTests::test_acquisition_error_survives_join_and_pipe_rollback_failures_then_retries -v
```

Actual exit: 1; elapsed: 0.502s; timeout: False. Full stdout/stderr: `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-b-l02-resume-20261113-e79f7bd38c3141fa8d4c78a309234a7d/slice2e-primary-rollback-red.log` (SHA-256 `faab68137addfbe4d553d6b733eb4914d134e7440e65d3007f4f69007d058e43`). Exact command, before-run source hashes and 20 protected matches: `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-b-l02-resume-20261113-e79f7bd38c3141fa8d4c78a309234a7d/slice2e-primary-rollback-red.json`.

```text
============================= test session starts ==============================
platform darwin -- Python 3.11.15, pytest-9.2.0, pluggy-1.7.0 -- /Users/ahronjanl.rafaelahron.0804icloudcom/.kumpas-venvs/rv2-holistic-tf-20261101/bin/python
rootdir: /Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration
collecting ... collected 1 item

training/holistic_migration/tests/test_camera.py::ConstructorRollbackTests::test_acquisition_error_survives_join_and_pipe_rollback_failures_then_retries FAILED [100%]

=================================== FAILURES ===================================
_ ConstructorRollbackTests.test_acquisition_error_survives_join_and_pipe_rollback_failures_then_retries _

thread = <Thread(owned-camera-frames, initial daemon)>

    def start(thread):
        if thread.name == "owned-camera-frames":
            attempts.append("frames.start")
>           raise primary
E           RuntimeError: frame thread acquisition sentinel

training/holistic_migration/tests/test_camera.py:300: RuntimeError

During handling of the above exception, another exception occurred:

self = <holistic_migration.tests.test_camera.ConstructorRollbackTests testMethod=test_acquisition_error_survives_join_and_pipe_rollback_failures_then_retries>

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
>                       capture.__init__(type("Binding", (), {"binary": Path("/unused")})(),
                                         duration=1, popen=popen, startup_timeout=2,
                                         frame_timeout=2, shutdown_timeout=.05)

training/holistic_migration/tests/test_camera.py:312: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
training/holistic_migration/camera.py:248: in __init__
    self.close()
training/holistic_migration/camera.py:351: in close
    raise teardown_errors[0]
training/holistic_migration/camera.py:341: in close
    thread.join(timeout=self.shutdown_timeout + .1)
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

    def join(**kwargs):
        attempts.append("stderr.join")
        if attempts.count("stderr.join") == 1:
>           raise join_error
E           RuntimeError: stderr rollback join sentinel

training/holistic_migration/tests/test_camera.py:306: RuntimeError
=========================== short test summary info ============================
FAILED training/holistic_migration/tests/test_camera.py::ConstructorRollbackTests::test_acquisition_error_survives_join_and_pipe_rollback_failures_then_retries
============================== 1 failed in 0.09s ===============================

```


### L02 continuation slice2e-primary-rollback-green

```sh
TMPDIR=/Users/ahronjanl.rafaelahron.0804icloudcom/.hermes/cache/scratch /Users/ahronjanl.rafaelahron.0804icloudcom/.kumpas-venvs/rv2-holistic-tf-20261101/bin/python -E -B -m pytest -p no:cacheprovider training/holistic_migration/tests/test_camera.py::ConstructorRollbackTests training/holistic_migration/tests/test_camera.py::TeardownRetryTests -v
```

Actual exit: 0; elapsed: 0.493s; timeout: False. Full stdout/stderr: `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-b-l02-resume-20261113-e79f7bd38c3141fa8d4c78a309234a7d/slice2e-primary-rollback-green.log` (SHA-256 `a097932e7b039e6333b25bdcf304c2b2e53f03811bff55f5790db6a3f29736e5`). Exact command, before-run source hashes and 20 protected matches: `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-b-l02-resume-20261113-e79f7bd38c3141fa8d4c78a309234a7d/slice2e-primary-rollback-green.json`.

```text
============================= test session starts ==============================
platform darwin -- Python 3.11.15, pytest-9.2.0, pluggy-1.7.0 -- /Users/ahronjanl.rafaelahron.0804icloudcom/.kumpas-venvs/rv2-holistic-tf-20261101/bin/python
rootdir: /Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration
collecting ... collected 5 items

training/holistic_migration/tests/test_camera.py::ConstructorRollbackTests::test_acquisition_error_survives_join_and_pipe_rollback_failures_then_retries PASSED [ 20%]
training/holistic_migration/tests/test_camera.py::ConstructorRollbackTests::test_frame_thread_start_failure_rolls_back_owned_resources PASSED [ 40%]
training/holistic_migration/tests/test_camera.py::ConstructorRollbackTests::test_stderr_thread_start_failure_rolls_back_owned_resources PASSED [ 60%]
training/holistic_migration/tests/test_camera.py::TeardownRetryTests::test_join_failure_attempts_later_join_and_both_pipes_then_allows_retry PASSED [ 80%]
training/holistic_migration/tests/test_camera.py::TeardownRetryTests::test_stdout_close_failure_still_closes_stderr_and_retries_incomplete_pipe PASSED [100%]

============================== 5 passed in 0.16s ===============================

```


### L02 continuation slice2f-live-join-timeout-red

```sh
TMPDIR=/Users/ahronjanl.rafaelahron.0804icloudcom/.hermes/cache/scratch /Users/ahronjanl.rafaelahron.0804icloudcom/.kumpas-venvs/rv2-holistic-tf-20261101/bin/python -E -B -m pytest -p no:cacheprovider training/holistic_migration/tests/test_camera.py::TeardownRetryTests::test_join_timeout_is_reported_and_remains_retryable_until_thread_stops -v
```

Actual exit: 1; elapsed: 0.662s; timeout: False. Full stdout/stderr: `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-b-l02-resume-20261113-e79f7bd38c3141fa8d4c78a309234a7d/slice2f-live-join-timeout-red.log` (SHA-256 `9bf14ee21f45f49ee57233a1fc33a7d2909b6075fe42ce7ead018fcf4d1fa7e4`). Exact command, before-run source hashes and 20 protected matches: `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-b-l02-resume-20261113-e79f7bd38c3141fa8d4c78a309234a7d/slice2f-live-join-timeout-red.json`.

```text
============================= test session starts ==============================
platform darwin -- Python 3.11.15, pytest-9.2.0, pluggy-1.7.0 -- /Users/ahronjanl.rafaelahron.0804icloudcom/.kumpas-venvs/rv2-holistic-tf-20261101/bin/python
rootdir: /Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration
collecting ... collected 1 item

training/holistic_migration/tests/test_camera.py::TeardownRetryTests::test_join_timeout_is_reported_and_remains_retryable_until_thread_stops FAILED [100%]

=================================== FAILURES ===================================
_ TeardownRetryTests.test_join_timeout_is_reported_and_remains_retryable_until_thread_stops _

self = <holistic_migration.tests.test_camera.TeardownRetryTests testMethod=test_join_timeout_is_reported_and_remains_retryable_until_thread_stops>

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
>           with self.assertRaises(TimeoutError) as caught:
E           AssertionError: TimeoutError not raised

training/holistic_migration/tests/test_camera.py:380: AssertionError
=========================== short test summary info ============================
FAILED training/holistic_migration/tests/test_camera.py::TeardownRetryTests::test_join_timeout_is_reported_and_remains_retryable_until_thread_stops
============================== 1 failed in 0.25s ===============================

```


### L02 continuation slice2f-live-join-timeout-green

```sh
TMPDIR=/Users/ahronjanl.rafaelahron.0804icloudcom/.hermes/cache/scratch /Users/ahronjanl.rafaelahron.0804icloudcom/.kumpas-venvs/rv2-holistic-tf-20261101/bin/python -E -B -m pytest -p no:cacheprovider training/holistic_migration/tests/test_camera.py::ConstructorRollbackTests training/holistic_migration/tests/test_camera.py::TeardownRetryTests -v
```

Actual exit: 0; elapsed: 0.662s; timeout: False. Full stdout/stderr: `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-b-l02-resume-20261113-e79f7bd38c3141fa8d4c78a309234a7d/slice2f-live-join-timeout-green.log` (SHA-256 `aa38463755b907f988a449f15b32807721a546537c3f8b23121bf1381ef0f177`). Exact command, before-run source hashes and 20 protected matches: `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-b-l02-resume-20261113-e79f7bd38c3141fa8d4c78a309234a7d/slice2f-live-join-timeout-green.json`.

```text
============================= test session starts ==============================
platform darwin -- Python 3.11.15, pytest-9.2.0, pluggy-1.7.0 -- /Users/ahronjanl.rafaelahron.0804icloudcom/.kumpas-venvs/rv2-holistic-tf-20261101/bin/python
rootdir: /Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration
collecting ... collected 6 items

training/holistic_migration/tests/test_camera.py::ConstructorRollbackTests::test_acquisition_error_survives_join_and_pipe_rollback_failures_then_retries PASSED [ 16%]
training/holistic_migration/tests/test_camera.py::ConstructorRollbackTests::test_frame_thread_start_failure_rolls_back_owned_resources PASSED [ 33%]
training/holistic_migration/tests/test_camera.py::ConstructorRollbackTests::test_stderr_thread_start_failure_rolls_back_owned_resources PASSED [ 50%]
training/holistic_migration/tests/test_camera.py::TeardownRetryTests::test_join_failure_attempts_later_join_and_both_pipes_then_allows_retry PASSED [ 66%]
training/holistic_migration/tests/test_camera.py::TeardownRetryTests::test_join_timeout_is_reported_and_remains_retryable_until_thread_stops PASSED [ 83%]
training/holistic_migration/tests/test_camera.py::TeardownRetryTests::test_stdout_close_failure_still_closes_stderr_and_retries_incomplete_pipe PASSED [100%]

============================== 6 passed in 0.34s ===============================

```


### L02 continuation parent-corrected-six-green

```sh
TMPDIR=/Users/ahronjanl.rafaelahron.0804icloudcom/.hermes/cache/scratch /Users/ahronjanl.rafaelahron.0804icloudcom/.kumpas-venvs/rv2-holistic-tf-20261101/bin/python -E -B /Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-b-before-fix-8830ecffa4174cd98b6ecc4c7b1c3ea0/parent_fault_regressions.py
```

Actual exit: 0; elapsed: 0.777s; timeout: False. Full stdout/stderr: `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-b-l02-resume-20261113-e79f7bd38c3141fa8d4c78a309234a7d/parent-corrected-six-green.log` (SHA-256 `ca787dcbd133294b8b3c78f305a28479508c8ee96e514c48d08162a858b6ee2c`). Exact command, before-run source hashes and 20 protected matches: `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-b-l02-resume-20261113-e79f7bd38c3141fa8d4c78a309234a7d/parent-corrected-six-green.json`.

```text
test_frame_thread_start_failure_closes_pipes_and_preserves_primary (__main__.ReviewFaultRegressions.test_frame_thread_start_failure_closes_pipes_and_preserves_primary) ... ok
test_healthy_quit_is_not_a_source_failure (__main__.ReviewFaultRegressions.test_healthy_quit_is_not_a_source_failure) ... ok
test_source_failure_during_processing_then_deadline (__main__.ReviewFaultRegressions.test_source_failure_during_processing_then_deadline) ... ok
test_source_failure_during_processing_then_quit (__main__.ReviewFaultRegressions.test_source_failure_during_processing_then_quit) ... ok
test_source_failure_during_processing_then_window_close (__main__.ReviewFaultRegressions.test_source_failure_during_processing_then_window_close) ... ok
test_stderr_thread_start_failure_closes_pipes_and_preserves_primary (__main__.ReviewFaultRegressions.test_stderr_thread_start_failure_closes_pipes_and_preserves_primary) ... ok

----------------------------------------------------------------------
Ran 6 tests in 0.446s

OK
PARENT_FAULT_RECEIPT /Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-b-before-fix-8830ecffa4174cd98b6ecc4c7b1c3ea0/parent-regression-runs/07b64cec7e7e49ec83e23be4f20f1eca/observations.json

```


### L02 continuation preserved-source-reconciliation-green

```sh
TMPDIR=/Users/ahronjanl.rafaelahron.0804icloudcom/.hermes/cache/scratch /Users/ahronjanl.rafaelahron.0804icloudcom/.kumpas-venvs/rv2-holistic-tf-20261101/bin/python -E -B -m pytest -p no:cacheprovider training/holistic_migration/tests/test_webcam.py::SourceReconciliationTests -v
```

Actual exit: 0; elapsed: 0.828s; timeout: False. Full stdout/stderr: `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-b-l02-resume-20261113-e79f7bd38c3141fa8d4c78a309234a7d/preserved-source-reconciliation-green.log` (SHA-256 `9d449f602b8393a83674ece02f4d3136422b07b06efc9ebe470b3087da094176`). Exact command, before-run source hashes and 20 protected matches: `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-b-l02-resume-20261113-e79f7bd38c3141fa8d4c78a309234a7d/preserved-source-reconciliation-green.json`.

```text
============================= test session starts ==============================
platform darwin -- Python 3.11.15, pytest-9.2.0, pluggy-1.7.0 -- /Users/ahronjanl.rafaelahron.0804icloudcom/.kumpas-venvs/rv2-holistic-tf-20261101/bin/python
rootdir: /Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration
collecting ... collected 7 items

training/holistic_migration/tests/test_webcam.py::SourceReconciliationTests::test_healthy_deadline_deliberately_terminates_owned_child PASSED [ 14%]
training/holistic_migration/tests/test_webcam.py::SourceReconciliationTests::test_healthy_quit_deliberately_terminates_owned_child PASSED [ 28%]
training/holistic_migration/tests/test_webcam.py::SourceReconciliationTests::test_observed_source_failure_then_deadline PASSED [ 42%]
training/holistic_migration/tests/test_webcam.py::SourceReconciliationTests::test_observed_source_failure_then_escape PASSED [ 57%]
training/holistic_migration/tests/test_webcam.py::SourceReconciliationTests::test_observed_source_failure_then_quit PASSED [ 71%]
training/holistic_migration/tests/test_webcam.py::SourceReconciliationTests::test_observed_source_failure_then_window_close PASSED [ 85%]
training/holistic_migration/tests/test_webcam.py::SourceReconciliationTests::test_unexpected_child_exit_before_reader_publishes_error PASSED [100%]

============================== 7 passed in 0.47s ===============================

```


### L02 continuation named-camera-webcam-green

```sh
TMPDIR=/Users/ahronjanl.rafaelahron.0804icloudcom/.hermes/cache/scratch /Users/ahronjanl.rafaelahron.0804icloudcom/.kumpas-venvs/rv2-holistic-tf-20261101/bin/python -E -B -m pytest -p no:cacheprovider training/holistic_migration/tests/test_camera.py training/holistic_migration/tests/test_webcam.py -v
```

Actual exit: 0; elapsed: 6.349s; timeout: False. Full stdout/stderr: `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-b-l02-resume-20261113-e79f7bd38c3141fa8d4c78a309234a7d/named-camera-webcam-green.log` (SHA-256 `5ed5c7753284f4f179455e1596418e8c5b8e0f2f9d086ef96b79bc66ef149320`). Exact command, before-run source hashes and 20 protected matches: `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-b-l02-resume-20261113-e79f7bd38c3141fa8d4c78a309234a7d/named-camera-webcam-green.json`.

```text
============================= test session starts ==============================
platform darwin -- Python 3.11.15, pytest-9.2.0, pluggy-1.7.0 -- /Users/ahronjanl.rafaelahron.0804icloudcom/.kumpas-venvs/rv2-holistic-tf-20261101/bin/python
rootdir: /Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration
collecting ... collected 34 items

training/holistic_migration/tests/test_camera.py::HandshakeTests::test_actual_bgra_dimensions_and_builtin_identity_are_admitted PASSED [  2%]
training/holistic_migration/tests/test_camera.py::HandshakeTests::test_ambiguous_or_nonbuiltin_metadata_is_rejected 
training/holistic_migration/tests/test_camera.py::HandshakeTests::test_ambiguous_or_nonbuiltin_metadata_is_rejected PASSED [  5%]
training/holistic_migration/tests/test_camera.py::PacketTests::test_partial_reads_actual_handshake_and_exact_frame PASSED [  8%]
training/holistic_migration/tests/test_camera.py::PacketTests::test_repeated_or_regressing_timestamp_and_startup_limits 
training/holistic_migration/tests/test_camera.py::PacketTests::test_repeated_or_regressing_timestamp_and_startup_limits PASSED [ 11%]
training/holistic_migration/tests/test_camera.py::PacketTests::test_short_oversized_and_invalid_timestamps_fail_closed 
training/holistic_migration/tests/test_camera.py::PacketTests::test_short_oversized_and_invalid_timestamps_fail_closed PASSED [ 14%]
training/holistic_migration/tests/test_camera.py::NativeBindingTests::test_build_rejects_relative_or_repository_directory_before_compiler 
training/holistic_migration/tests/test_camera.py::NativeBindingTests::test_build_rejects_relative_or_repository_directory_before_compiler PASSED [ 17%]
training/holistic_migration/tests/test_camera.py::NativeBindingTests::test_exact_source_compiles_and_pure_native_checks_need_no_camera PASSED [ 20%]
training/holistic_migration/tests/test_camera.py::BuildFailureTests::test_compiler_timeout_keeps_partial_stdout_stderr_and_command PASSED [ 23%]
training/holistic_migration/tests/test_camera.py::CaptureTests::test_binding_is_checked_before_process_spawn PASSED [ 26%]
training/holistic_migration/tests/test_camera.py::CaptureTests::test_frame_failure_stderr_cap_and_terminate_kill_escalation PASSED [ 29%]
training/holistic_migration/tests/test_camera.py::CaptureTests::test_latest_only_queue_and_owned_child_cleanup PASSED [ 32%]
training/holistic_migration/tests/test_camera.py::CaptureTests::test_startup_eof_timeout_and_stderr_are_preserved 
training/holistic_migration/tests/test_camera.py::CaptureTests::test_startup_eof_timeout_and_stderr_are_preserved PASSED [ 35%]
training/holistic_migration/tests/test_camera.py::ConstructorRollbackTests::test_acquisition_error_survives_join_and_pipe_rollback_failures_then_retries PASSED [ 38%]
training/holistic_migration/tests/test_camera.py::ConstructorRollbackTests::test_frame_thread_start_failure_rolls_back_owned_resources PASSED [ 41%]
training/holistic_migration/tests/test_camera.py::ConstructorRollbackTests::test_stderr_thread_start_failure_rolls_back_owned_resources PASSED [ 44%]
training/holistic_migration/tests/test_camera.py::TeardownRetryTests::test_join_failure_attempts_later_join_and_both_pipes_then_allows_retry PASSED [ 47%]
training/holistic_migration/tests/test_camera.py::TeardownRetryTests::test_join_timeout_is_reported_and_remains_retryable_until_thread_stops PASSED [ 50%]
training/holistic_migration/tests/test_camera.py::TeardownRetryTests::test_stdout_close_failure_still_closes_stderr_and_retries_incomplete_pipe PASSED [ 52%]
training/holistic_migration/tests/test_webcam.py::AdmissionTests::test_invalid_duration_precedes_paths_and_runtime 
training/holistic_migration/tests/test_webcam.py::AdmissionTests::test_invalid_duration_precedes_paths_and_runtime PASSED [ 55%]
training/holistic_migration/tests/test_webcam.py::AdmissionTests::test_paths_and_report_overwrite_rejected_before_build 
training/holistic_migration/tests/test_webcam.py::AdmissionTests::test_paths_and_report_overwrite_rejected_before_build PASSED [ 58%]
training/holistic_migration/tests/test_webcam.py::PixelsAndOverlayTests::test_actual_bgra_conversion_resize_and_no_input_mirror PASSED [ 61%]
training/holistic_migration/tests/test_webcam.py::PixelsAndOverlayTests::test_missing_components_real_counts_masks_connections_and_readable_text PASSED [ 64%]
training/holistic_migration/tests/test_webcam.py::PreviewLoopTests::test_additional_failure_stages_keep_disposition_and_teardown 
training/holistic_migration/tests/test_webcam.py::PreviewLoopTests::test_additional_failure_stages_keep_disposition_and_teardown PASSED [ 67%]
training/holistic_migration/tests/test_webcam.py::PreviewLoopTests::test_default_runtime_binds_actual_shared_detector_and_packer_without_loading_sdk PASSED [ 70%]
training/holistic_migration/tests/test_webcam.py::PreviewLoopTests::test_errors_cleanup_fault_and_handshake_admission_before_detector 
training/holistic_migration/tests/test_webcam.py::PreviewLoopTests::test_errors_cleanup_fault_and_handshake_admission_before_detector PASSED [ 73%]
training/holistic_migration/tests/test_webcam.py::PreviewLoopTests::test_no_implicit_report_and_main_uses_same_runner PASSED [ 76%]
training/holistic_migration/tests/test_webcam.py::PreviewLoopTests::test_quit_escape_window_close_and_deadline_release_all 
training/holistic_migration/tests/test_webcam.py::PreviewLoopTests::test_quit_escape_window_close_and_deadline_release_all PASSED [ 79%]
training/holistic_migration/tests/test_webcam.py::SourceReconciliationTests::test_healthy_deadline_deliberately_terminates_owned_child PASSED [ 82%]
training/holistic_migration/tests/test_webcam.py::SourceReconciliationTests::test_healthy_quit_deliberately_terminates_owned_child PASSED [ 85%]
training/holistic_migration/tests/test_webcam.py::SourceReconciliationTests::test_observed_source_failure_then_deadline PASSED [ 88%]
training/holistic_migration/tests/test_webcam.py::SourceReconciliationTests::test_observed_source_failure_then_escape PASSED [ 91%]
training/holistic_migration/tests/test_webcam.py::SourceReconciliationTests::test_observed_source_failure_then_quit PASSED [ 94%]
training/holistic_migration/tests/test_webcam.py::SourceReconciliationTests::test_observed_source_failure_then_window_close PASSED [ 97%]
training/holistic_migration/tests/test_webcam.py::SourceReconciliationTests::test_unexpected_child_exit_before_reader_publishes_error PASSED [100%]

==================== 34 passed, 58 subtests passed in 6.02s ====================

```


### L02 continuation full-migration-pytest-green

```sh
TMPDIR=/Users/ahronjanl.rafaelahron.0804icloudcom/.hermes/cache/scratch /bin/sh -c 'export TMPDIR="$HOME/.hermes/cache/scratch"; PY="$HOME/.kumpas-venvs/rv2-holistic-tf-20261101/bin/python"; "$PY" -E -B -m pytest -p no:cacheprovider training/holistic_migration/tests -v'
```

Actual exit: 0; elapsed: 50.334s; timeout: False. Full stdout/stderr: `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-b-l02-resume-20261113-e79f7bd38c3141fa8d4c78a309234a7d/full-migration-pytest-green.log` (SHA-256 `5c97858a1b569529d30ec073396e958b8da4311fd157f3471fdfbc76e3eb1518`). Exact command, before-run source hashes and 20 protected matches: `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-b-l02-resume-20261113-e79f7bd38c3141fa8d4c78a309234a7d/full-migration-pytest-green.json`.

```text
============================= test session starts ==============================
platform darwin -- Python 3.11.15, pytest-9.2.0, pluggy-1.7.0 -- /Users/ahronjanl.rafaelahron.0804icloudcom/.kumpas-venvs/rv2-holistic-tf-20261101/bin/python
rootdir: /Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration
collecting ... collected 199 items

training/holistic_migration/tests/test_camera.py::HandshakeTests::test_actual_bgra_dimensions_and_builtin_identity_are_admitted PASSED [  0%]
training/holistic_migration/tests/test_camera.py::HandshakeTests::test_ambiguous_or_nonbuiltin_metadata_is_rejected 
training/holistic_migration/tests/test_camera.py::HandshakeTests::test_ambiguous_or_nonbuiltin_metadata_is_rejected PASSED [  1%]
training/holistic_migration/tests/test_camera.py::PacketTests::test_partial_reads_actual_handshake_and_exact_frame PASSED [  1%]
training/holistic_migration/tests/test_camera.py::PacketTests::test_repeated_or_regressing_timestamp_and_startup_limits 
training/holistic_migration/tests/test_camera.py::PacketTests::test_repeated_or_regressing_timestamp_and_startup_limits PASSED [  2%]
training/holistic_migration/tests/test_camera.py::PacketTests::test_short_oversized_and_invalid_timestamps_fail_closed 
training/holistic_migration/tests/test_camera.py::PacketTests::test_short_oversized_and_invalid_timestamps_fail_closed PASSED [  2%]
training/holistic_migration/tests/test_camera.py::NativeBindingTests::test_build_rejects_relative_or_repository_directory_before_compiler 
training/holistic_migration/tests/test_camera.py::NativeBindingTests::test_build_rejects_relative_or_repository_directory_before_compiler PASSED [  3%]
training/holistic_migration/tests/test_camera.py::NativeBindingTests::test_exact_source_compiles_and_pure_native_checks_need_no_camera PASSED [  3%]
training/holistic_migration/tests/test_camera.py::BuildFailureTests::test_compiler_timeout_keeps_partial_stdout_stderr_and_command PASSED [  4%]
training/holistic_migration/tests/test_camera.py::CaptureTests::test_binding_is_checked_before_process_spawn PASSED [  4%]
training/holistic_migration/tests/test_camera.py::CaptureTests::test_frame_failure_stderr_cap_and_terminate_kill_escalation PASSED [  5%]
training/holistic_migration/tests/test_camera.py::CaptureTests::test_latest_only_queue_and_owned_child_cleanup PASSED [  5%]
training/holistic_migration/tests/test_camera.py::CaptureTests::test_startup_eof_timeout_and_stderr_are_preserved 
training/holistic_migration/tests/test_camera.py::CaptureTests::test_startup_eof_timeout_and_stderr_are_preserved PASSED [  6%]
training/holistic_migration/tests/test_camera.py::ConstructorRollbackTests::test_acquisition_error_survives_join_and_pipe_rollback_failures_then_retries PASSED [  6%]
training/holistic_migration/tests/test_camera.py::ConstructorRollbackTests::test_frame_thread_start_failure_rolls_back_owned_resources PASSED [  7%]
training/holistic_migration/tests/test_camera.py::ConstructorRollbackTests::test_stderr_thread_start_failure_rolls_back_owned_resources PASSED [  7%]
training/holistic_migration/tests/test_camera.py::TeardownRetryTests::test_join_failure_attempts_later_join_and_both_pipes_then_allows_retry PASSED [  8%]
training/holistic_migration/tests/test_camera.py::TeardownRetryTests::test_join_timeout_is_reported_and_remains_retryable_until_thread_stops PASSED [  8%]
training/holistic_migration/tests/test_camera.py::TeardownRetryTests::test_stdout_close_failure_still_closes_stderr_and_retries_incomplete_pipe PASSED [  9%]
training/holistic_migration/tests/test_dataset.py::test_raw_codec_roundtrip_exact_none_and_variable_face PASSED [  9%]
training/holistic_migration/tests/test_dataset.py::test_raw_codec_rejects_corruption_even_rebound_digest[offset] PASSED [ 10%]
training/holistic_migration/tests/test_dataset.py::test_raw_codec_rejects_corruption_even_rebound_digest[float_timestamp] PASSED [ 10%]
training/holistic_migration/tests/test_dataset.py::test_raw_codec_rejects_corruption_even_rebound_digest[bool_presence] PASSED [ 11%]
training/holistic_migration/tests/test_dataset.py::test_raw_codec_rejects_corruption_even_rebound_digest[absent_block] PASSED [ 11%]
training/holistic_migration/tests/test_dataset.py::test_raw_codec_rejects_corruption_even_rebound_digest[absent_face] PASSED [ 12%]
training/holistic_migration/tests/test_dataset.py::test_raw_codec_rejects_corruption_even_rebound_digest[nonfinite] PASSED [ 12%]
training/holistic_migration/tests/test_dataset.py::test_raw_codec_rejects_corruption_even_rebound_digest[object] PASSED [ 13%]
training/holistic_migration/tests/test_dataset.py::test_raw_codec_rejects_corruption_even_rebound_digest[extra] PASSED [ 13%]
training/holistic_migration/tests/test_dataset.py::test_raw_codec_rejects_corruption_even_rebound_digest[duplicate_time] PASSED [ 14%]
training/holistic_migration/tests/test_dataset.py::test_raw_codec_rejects_corruption_even_rebound_digest[digest] PASSED [ 14%]
training/holistic_migration/tests/test_dataset.py::test_raw_writer_rejects_masked_and_nonmonotonic PASSED [ 15%]
training/holistic_migration/tests/test_dataset.py::test_public_preflight_validates_complete_synthetic_graph PASSED [ 15%]
training/holistic_migration/tests/test_dataset.py::test_public_preflight_rebound_tampering[schema_bool-schema_version] PASSED [ 16%]
training/holistic_migration/tests/test_dataset.py::test_public_preflight_rebound_tampering[dense_float-dense_id] PASSED [ 16%]
training/holistic_migration/tests/test_dataset.py::test_public_preflight_rebound_tampering[bytes_bool-video_bytes] PASSED [ 17%]
training/holistic_migration/tests/test_dataset.py::test_public_preflight_rebound_tampering[count_float-count] PASSED [ 17%]
training/holistic_migration/tests/test_dataset.py::test_public_preflight_rebound_tampering[decode_float-decoded_frames] PASSED [ 18%]
training/holistic_migration/tests/test_dataset.py::test_public_preflight_rebound_tampering[duplicate-duplicate] PASSED [ 18%]
training/holistic_migration/tests/test_dataset.py::test_public_preflight_rebound_tampering[traversal-clip_id] PASSED [ 19%]
training/holistic_migration/tests/test_dataset.py::test_public_preflight_rebound_tampering[bad_token-source_token] PASSED [ 19%]
training/holistic_migration/tests/test_dataset.py::test_public_preflight_rebound_tampering[test_to_fit-official] PASSED [ 20%]
training/holistic_migration/tests/test_dataset.py::test_public_preflight_rebound_tampering[identity-identity] PASSED [ 20%]
training/holistic_migration/tests/test_dataset.py::test_public_preflight_rebound_tampering[archive-archive] PASSED [ 21%]
training/holistic_migration/tests/test_dataset.py::test_public_preflight_rebound_tampering[decode_count-source_count] PASSED [ 21%]
training/holistic_migration/tests/test_dataset.py::test_public_preflight_rebound_tampering[pixel_duplicate-duplicate] PASSED [ 22%]
training/holistic_migration/tests/test_dataset.py::test_public_preflight_rebound_tampering[upstream_count-count] PASSED [ 22%]
training/holistic_migration/tests/test_dataset.py::test_public_preflight_rebound_tampering[class_order-class] PASSED [ 23%]
training/holistic_migration/tests/test_dataset.py::test_public_preflight_rebound_tampering[class_bool-class] PASSED [ 23%]
training/holistic_migration/tests/test_dataset.py::test_public_preflight_rebound_tampering[partition-partition] PASSED [ 24%]
training/holistic_migration/tests/test_dataset.py::test_public_preflight_path_and_byte_boundaries[existing-exists] PASSED [ 24%]
training/holistic_migration/tests/test_dataset.py::test_public_preflight_path_and_byte_boundaries[inside_raw-overlap] PASSED [ 25%]
training/holistic_migration/tests/test_dataset.py::test_public_preflight_path_and_byte_boundaries[inside_repo-repository] PASSED [ 25%]
training/holistic_migration/tests/test_dataset.py::test_public_preflight_path_and_byte_boundaries[ancestor-overlap] PASSED [ 26%]
training/holistic_migration/tests/test_dataset.py::test_public_preflight_path_and_byte_boundaries[symlink-symlink] PASSED [ 26%]
training/holistic_migration/tests/test_dataset.py::test_public_preflight_path_and_byte_boundaries[raw_symlink-symlink] PASSED [ 27%]
training/holistic_migration/tests/test_dataset.py::test_public_preflight_path_and_byte_boundaries[relative-absolute] PASSED [ 27%]
training/holistic_migration/tests/test_dataset.py::test_public_preflight_path_and_byte_boundaries[dataless-DATALESS] PASSED [ 28%]
training/holistic_migration/tests/test_dataset.py::test_public_preflight_path_and_byte_boundaries[stale-digest] PASSED [ 28%]
training/holistic_migration/tests/test_dataset.py::test_canonical_bundle_production_flow_exact_ids_and_tensors PASSED [ 29%]
training/holistic_migration/tests/test_dataset.py::test_bundle_rejects_incomplete_tampered_campaign_public_path[diagnostic] PASSED [ 29%]
training/holistic_migration/tests/test_dataset.py::test_bundle_rejects_incomplete_tampered_campaign_public_path[disguised_diagnostic] PASSED [ 30%]
training/holistic_migration/tests/test_dataset.py::test_bundle_rejects_incomplete_tampered_campaign_public_path[raw_byte] PASSED [ 30%]
training/holistic_migration/tests/test_dataset.py::test_bundle_rejects_incomplete_tampered_campaign_public_path[ledger_byte] PASSED [ 31%]
training/holistic_migration/tests/test_dataset.py::test_bundle_rejects_incomplete_tampered_campaign_public_path[row_missing] PASSED [ 31%]
training/holistic_migration/tests/test_dataset.py::test_bundle_rejects_incomplete_tampered_campaign_public_path[row_duplicate] PASSED [ 32%]
training/holistic_migration/tests/test_dataset.py::test_bundle_rejects_incomplete_tampered_campaign_public_path[row_identity] PASSED [ 32%]
training/holistic_migration/tests/test_dataset.py::test_bundle_rejects_incomplete_tampered_campaign_public_path[raw_traversal] PASSED [ 33%]
training/holistic_migration/tests/test_dataset.py::test_bundle_rejects_incomplete_tampered_campaign_public_path[raw_symlink] PASSED [ 33%]
training/holistic_migration/tests/test_dataset.py::test_bundle_rejects_incomplete_tampered_campaign_public_path[count_float] PASSED [ 34%]
training/holistic_migration/tests/test_dataset.py::test_bundle_rejects_incomplete_tampered_campaign_public_path[raw_digest] PASSED [ 34%]
training/holistic_migration/tests/test_dataset.py::test_bundle_rejects_incomplete_tampered_campaign_public_path[capture] PASSED [ 35%]
training/holistic_migration/tests/test_dataset.py::test_bundle_rejects_incomplete_tampered_campaign_public_path[existing] PASSED [ 35%]
training/holistic_migration/tests/test_dataset.py::test_bundle_rejects_incomplete_tampered_campaign_public_path[current_contract] PASSED [ 36%]
training/holistic_migration/tests/test_dataset.py::test_bundle_requires_all_class_support_retains_failed_denominators[fit] PASSED [ 36%]
training/holistic_migration/tests/test_dataset.py::test_bundle_requires_all_class_support_retains_failed_denominators[validation] PASSED [ 37%]
training/holistic_migration/tests/test_dataset.py::test_bundle_reports_all_test_ineligibility_without_zero_examples PASSED [ 37%]
training/holistic_migration/tests/test_dataset.py::test_bundle_final_readback_rejects_midbuild_tamper[X_fit.npy] PASSED [ 38%]
training/holistic_migration/tests/test_dataset.py::test_bundle_final_readback_rejects_midbuild_tamper[X_validation.npy] PASSED [ 38%]
training/holistic_migration/tests/test_dataset.py::test_bundle_final_readback_rejects_midbuild_tamper[eligibility.json] PASSED [ 39%]
training/holistic_migration/tests/test_dataset.py::test_bundle_final_readback_rejects_midbuild_tamper[campaign_raw] PASSED [ 39%]
training/holistic_migration/tests/test_dataset.py::test_bundle_cli_help_success_failure_and_no_native_imports PASSED [ 40%]
training/holistic_migration/tests/test_dataset.py::test_codec_rejects_loss_or_unsafe_read[unrepresentable_face] PASSED [ 40%]
training/holistic_migration/tests/test_dataset.py::test_codec_rejects_loss_or_unsafe_read[timestamp_range] PASSED [ 41%]
training/holistic_migration/tests/test_dataset.py::test_codec_rejects_loss_or_unsafe_read[symlink_read] PASSED [ 41%]
training/holistic_migration/tests/test_dataset.py::test_rebound_capture_equal_float_count_is_not_integer PASSED [ 42%]
training/holistic_migration/tests/test_dataset.py::test_failed_manifest_readback_never_leaves_completed_publication[data_manifest.json] PASSED [ 42%]
training/holistic_migration/tests/test_dataset.py::test_failed_manifest_readback_never_leaves_completed_publication[extraction_manifest.json] PASSED [ 43%]
training/holistic_migration/tests/test_dataset.py::test_contract_cannot_silently_drop_missing_source_inputs PASSED [ 43%]
training/holistic_migration/tests/test_dataset.py::test_graph_receipt_hashes_runtime_and_contract_canonically PASSED [ 44%]
training/holistic_migration/tests/test_dataset.py::test_public_preflight_requires_upstream_official_counts PASSED [ 44%]
training/holistic_migration/tests/test_detector.py::DetectorPreflightTests::test_construction_uses_tasks_video_cpu_and_disabled_optional_outputs PASSED [ 45%]
training/holistic_migration/tests/test_detector.py::DetectorPreflightTests::test_context_manager_closes_once_on_body_exception_and_is_not_reusable PASSED [ 45%]
training/holistic_migration/tests/test_detector.py::DetectorPreflightTests::test_conversion_failure_inside_context_releases_tracker PASSED [ 46%]
training/holistic_migration/tests/test_detector.py::DetectorPreflightTests::test_detect_feeds_unmirrored_rgb_to_video_and_returns_converted_frame PASSED [ 46%]
training/holistic_migration/tests/test_detector.py::DetectorPreflightTests::test_invalid_api_rgb_or_timestamp_is_rejected_before_any_native_call 
training/holistic_migration/tests/test_detector.py::DetectorPreflightTests::test_invalid_api_rgb_or_timestamp_is_rejected_before_any_native_call PASSED [ 47%]
training/holistic_migration/tests/test_detector.py::DetectorPreflightTests::test_invalid_model_path_rejected_before_any_mediapipe_import 
training/holistic_migration/tests/test_detector.py::DetectorPreflightTests::test_invalid_model_path_rejected_before_any_mediapipe_import PASSED [ 47%]
training/holistic_migration/tests/test_detector.py::DetectorPreflightTests::test_native_failure_consumes_timestamp_and_context_still_closes PASSED [ 48%]
training/holistic_migration/tests/test_detector.py::DetectorPreflightTests::test_native_failure_inside_context_releases_tracker PASSED [ 48%]
training/holistic_migration/tests/test_detector.py::DetectorPreflightTests::test_noncontiguous_rgb_keeps_channel_order_and_observations PASSED [ 49%]
training/holistic_migration/tests/test_detector.py::DetectorPreflightTests::test_package_imports_are_lazy_without_mediapipe_or_tensorflow PASSED [ 49%]
training/holistic_migration/tests/test_detector.py::DetectorPreflightTests::test_timestamps_strictly_increase_per_instance_and_new_instance_resets 
training/holistic_migration/tests/test_detector.py::DetectorPreflightTests::test_timestamps_strictly_increase_per_instance_and_new_instance_resets PASSED [ 50%]
training/holistic_migration/tests/test_detector.py::ResultConversionTests::test_conversion_timestamp_is_exact_nonnegative_builtin_int 
training/holistic_migration/tests/test_detector.py::ResultConversionTests::test_conversion_timestamp_is_exact_nonnegative_builtin_int PASSED [ 50%]
training/holistic_migration/tests/test_detector.py::ResultConversionTests::test_empty_components_are_none_and_one_handed_results_remain_distinct 
training/holistic_migration/tests/test_detector.py::ResultConversionTests::test_empty_components_are_none_and_one_handed_results_remain_distinct PASSED [ 51%]
training/holistic_migration/tests/test_detector.py::ResultConversionTests::test_missing_or_none_pose_visibility_is_zero_not_fabricated_confidence PASSED [ 51%]
training/holistic_migration/tests/test_detector.py::ResultConversionTests::test_nonfinite_or_nonnumeric_sdk_coordinates_raise_clear_value_error 
training/holistic_migration/tests/test_detector.py::ResultConversionTests::test_nonfinite_or_nonnumeric_sdk_coordinates_raise_clear_value_error PASSED [ 52%]
training/holistic_migration/tests/test_detector.py::ResultConversionTests::test_reads_flat_normalized_landmarks_not_world_coordinates PASSED [ 52%]
training/holistic_migration/tests/test_detector.py::ResultConversionTests::test_requires_exact_pose_hand_counts_and_flat_sdk_shape 
training/holistic_migration/tests/test_detector.py::ResultConversionTests::test_requires_exact_pose_hand_counts_and_flat_sdk_shape PASSED [ 53%]
training/holistic_migration/tests/test_extract.py::test_extraction_complete_production_path_synthetic PASSED [ 53%]
training/holistic_migration/tests/test_extract.py::test_diagnostic_selects_literal_first_fit_only_before_inference PASSED [ 54%]
training/holistic_migration/tests/test_extract.py::test_extraction_failure_ledger_all_declared_cleanup_no_completion[nan-timestamp_error] PASSED [ 54%]
training/holistic_migration/tests/test_extract.py::test_extraction_failure_ledger_all_declared_cleanup_no_completion[negative-timestamp_error] PASSED [ 55%]
training/holistic_migration/tests/test_extract.py::test_extraction_failure_ledger_all_declared_cleanup_no_completion[duplicate-timestamp_error] PASSED [ 55%]
training/holistic_migration/tests/test_extract.py::test_extraction_failure_ledger_all_declared_cleanup_no_completion[pixel-decode_error] PASSED [ 56%]
training/holistic_migration/tests/test_extract.py::test_extraction_failure_ledger_all_declared_cleanup_no_completion[short-decode_error] PASSED [ 56%]
training/holistic_migration/tests/test_extract.py::test_extraction_failure_ledger_all_declared_cleanup_no_completion[detection-detection_error] PASSED [ 57%]
training/holistic_migration/tests/test_extract.py::test_extraction_failure_ledger_all_declared_cleanup_no_completion[source-source_error] PASSED [ 57%]
training/holistic_migration/tests/test_extract.py::test_extraction_public_preflight_before_runtime_factories PASSED [ 58%]
training/holistic_migration/tests/test_extract.py::test_video_timestamp_rejects_invalid_without_rounding_it_away[True] PASSED [ 58%]
training/holistic_migration/tests/test_extract.py::test_video_timestamp_rejects_invalid_without_rounding_it_away[nan] PASSED [ 59%]
training/holistic_migration/tests/test_extract.py::test_video_timestamp_rejects_invalid_without_rounding_it_away[inf] PASSED [ 59%]
training/holistic_migration/tests/test_extract.py::test_video_timestamp_rejects_invalid_without_rounding_it_away[-0.001] PASSED [ 60%]
training/holistic_migration/tests/test_extract.py::test_video_timestamp_rejects_invalid_without_rounding_it_away[12] PASSED [ 60%]
training/holistic_migration/tests/test_extract.py::test_extraction_cli_help_and_invalid_preflight_in_real_process PASSED [ 61%]
training/holistic_migration/tests/test_extract.py::test_extraction_main_preflight_failure_never_imports_native PASSED [ 61%]
training/holistic_migration/tests/test_extract.py::test_real_entry_rejects_nonfrozen_synthetic_inputs_before_native_or_output PASSED [ 62%]
training/holistic_migration/tests/test_features.py::PackFrameTests::test_component_shapes_and_real_numeric_ndarrays_are_required 
training/holistic_migration/tests/test_features.py::PackFrameTests::test_component_shapes_and_real_numeric_ndarrays_are_required PASSED [ 62%]
training/holistic_migration/tests/test_features.py::PackFrameTests::test_does_not_mutate_or_alias_readonly_inputs_and_excludes_face 
training/holistic_migration/tests/test_features.py::PackFrameTests::test_does_not_mutate_or_alias_readonly_inputs_and_excludes_face PASSED [ 63%]
training/holistic_migration/tests/test_features.py::PackFrameTests::test_exact_layout_float32_row_major PASSED [ 63%]
training/holistic_migration/tests/test_features.py::PackFrameTests::test_finite_input_with_nonfinite_normalized_output_raises 
training/holistic_migration/tests/test_features.py::PackFrameTests::test_finite_input_with_nonfinite_normalized_output_raises PASSED [ 64%]
training/holistic_migration/tests/test_features.py::PackFrameTests::test_individual_missing_hands_keep_zero_block_and_other_hand 
training/holistic_migration/tests/test_features.py::PackFrameTests::test_individual_missing_hands_keep_zero_block_and_other_hand PASSED [ 64%]
training/holistic_migration/tests/test_features.py::PackFrameTests::test_integer_arrays_normalize_in_float_without_truncation PASSED [ 65%]
training/holistic_migration/tests/test_features.py::PackFrameTests::test_large_but_finite_shoulder_width_is_not_lost_to_squaring_overflow PASSED [ 65%]
training/holistic_migration/tests/test_features.py::PackFrameTests::test_low_visibility_pose_points_are_entirely_zeroed PASSED [ 66%]
training/holistic_migration/tests/test_features.py::PackFrameTests::test_missing_pose_is_invalid_even_with_observed_hands PASSED [ 66%]
training/holistic_migration/tests/test_features.py::PackFrameTests::test_nonfinite_raw_arrays_raise_even_when_pose_is_unusable 
training/holistic_migration/tests/test_features.py::PackFrameTests::test_nonfinite_raw_arrays_raise_even_when_pose_is_unusable PASSED [ 67%]
training/holistic_migration/tests/test_features.py::PackFrameTests::test_plain_numeric_arrays_and_strided_readonly_views_keep_packed_behavior 
training/holistic_migration/tests/test_features.py::PackFrameTests::test_plain_numeric_arrays_and_strided_readonly_views_keep_packed_behavior PASSED [ 67%]
training/holistic_migration/tests/test_features.py::PackFrameTests::test_raw_timestamp_requires_nonnegative_exact_builtin_int 
training/holistic_migration/tests/test_features.py::PackFrameTests::test_raw_timestamp_requires_nonnegative_exact_builtin_int PASSED [ 68%]
training/holistic_migration/tests/test_features.py::PackFrameTests::test_semantic_ndarray_subclasses_are_rejected_before_array_semantics 
training/holistic_migration/tests/test_features.py::PackFrameTests::test_semantic_ndarray_subclasses_are_rejected_before_array_semantics PASSED [ 68%]
training/holistic_migration/tests/test_features.py::PackFrameTests::test_translation_positive_scale_and_distinct_depth_origins PASSED [ 69%]
training/holistic_migration/tests/test_features.py::PackFrameTests::test_unreliable_shoulders_invalidate_without_hip_requirement 
training/holistic_migration/tests/test_features.py::PackFrameTests::test_unreliable_shoulders_invalidate_without_hip_requirement PASSED [ 69%]
training/holistic_migration/tests/test_features.py::PackFrameTests::test_valid_idle_observation_has_pose_and_no_hand_masks PASSED [ 70%]
training/holistic_migration/tests/test_features.py::ResampleFramesTests::test_default_resampling_is_nearest_time_with_earlier_ties PASSED [ 70%]
training/holistic_migration/tests/test_features.py::ResampleFramesTests::test_large_timestamp_origin_does_not_lose_nearest_ties PASSED [ 71%]
training/holistic_migration/tests/test_features.py::ResampleFramesTests::test_missing_hands_and_idle_are_preserved_as_observations PASSED [ 71%]
training/holistic_migration/tests/test_features.py::ResampleFramesTests::test_requires_two_actual_observations_and_exact_integer_steps 
training/holistic_migration/tests/test_features.py::ResampleFramesTests::test_requires_two_actual_observations_and_exact_integer_steps PASSED [ 72%]
training/holistic_migration/tests/test_features.py::ResampleFramesTests::test_timestamps_must_be_strictly_increasing_without_sorting 
training/holistic_migration/tests/test_features.py::ResampleFramesTests::test_timestamps_must_be_strictly_increasing_without_sorting PASSED [ 72%]
training/holistic_migration/tests/test_features.py::ResampleFramesTests::test_unusable_observation_breaks_sequence_even_when_not_sampled 
training/holistic_migration/tests/test_features.py::ResampleFramesTests::test_unusable_observation_breaks_sequence_even_when_not_sampled PASSED [ 73%]
training/holistic_migration/tests/test_features.py::RawFrameTests::test_raw_frame_is_frozen_with_optional_face PASSED [ 73%]
training/holistic_migration/tests/test_sequence.py::test_clock_first_and_due_slot PASSED [ 74%]
training/holistic_migration/tests/test_sequence.py::test_clock_quantization[30] PASSED [ 74%]
training/holistic_migration/tests/test_sequence.py::test_clock_quantization[60] PASSED [ 75%]
training/holistic_migration/tests/test_sequence.py::test_clock_validates_skipped_inputs_without_mutation[True] PASSED [ 75%]
training/holistic_migration/tests/test_sequence.py::test_clock_validates_skipped_inputs_without_mutation[2.0] PASSED [ 76%]
training/holistic_migration/tests/test_sequence.py::test_clock_validates_skipped_inputs_without_mutation[-1] PASSED [ 76%]
training/holistic_migration/tests/test_sequence.py::test_clock_validates_skipped_inputs_without_mutation[0] PASSED [ 77%]
training/holistic_migration/tests/test_sequence.py::test_clock_validates_skipped_inputs_without_mutation[1] PASSED [ 77%]
training/holistic_migration/tests/test_sequence.py::test_clock_long_gap_has_no_fabrication PASSED [ 78%]
training/holistic_migration/tests/test_sequence.py::test_capture_positive_exact_accepted_resampling PASSED [ 78%]
training/holistic_migration/tests/test_sequence.py::test_capture_trims_only_ends_and_keeps_internal_missing_hands PASSED [ 79%]
training/holistic_migration/tests/test_sequence.py::test_capture_fixed_coverage_reasons[empty-no_hands] PASSED [ 79%]
training/holistic_migration/tests/test_sequence.py::test_capture_fixed_coverage_reasons[handless-no_hands] PASSED [ 80%]
training/holistic_migration/tests/test_sequence.py::test_capture_fixed_coverage_reasons[few-too_few_observations] PASSED [ 80%]
training/holistic_migration/tests/test_sequence.py::test_capture_fixed_coverage_reasons[few_hands-too_few_hand_observations] PASSED [ 81%]
training/holistic_migration/tests/test_sequence.py::test_capture_fixed_coverage_reasons[short-too_short] PASSED [ 81%]
training/holistic_migration/tests/test_sequence.py::test_capture_fixed_coverage_reasons[long-too_long] PASSED [ 82%]
training/holistic_migration/tests/test_sequence.py::test_capture_fixed_coverage_reasons[gap-observation_gap] PASSED [ 82%]
training/holistic_migration/tests/test_sequence.py::test_capture_fixed_coverage_reasons[pose-invalid_pose] PASSED [ 83%]
training/holistic_migration/tests/test_sequence.py::test_capture_gap_boundary[250-True] PASSED [ 83%]
training/holistic_migration/tests/test_sequence.py::test_capture_gap_boundary[251-False] PASSED [ 84%]
training/holistic_migration/tests/test_sequence.py::test_capture_inclusive_duration[400] PASSED [ 84%]
training/holistic_migration/tests/test_sequence.py::test_capture_inclusive_duration[5000] PASSED [ 85%]
training/holistic_migration/tests/test_sequence.py::test_capture_validates_all_even_trimmed_rows[bool_timestamp] PASSED [ 85%]
training/holistic_migration/tests/test_sequence.py::test_capture_validates_all_even_trimmed_rows[float_timestamp] PASSED [ 86%]
training/holistic_migration/tests/test_sequence.py::test_capture_validates_all_even_trimmed_rows[duplicate] PASSED [ 86%]
training/holistic_migration/tests/test_sequence.py::test_capture_validates_all_even_trimmed_rows[nonfinite] PASSED [ 87%]
training/holistic_migration/tests/test_sequence.py::test_capture_validates_all_even_trimmed_rows[shape] PASSED [ 87%]
training/holistic_migration/tests/test_sequence.py::test_capture_validates_all_even_trimmed_rows[masked] PASSED [ 88%]
training/holistic_migration/tests/test_sequence.py::test_capture_validates_all_even_trimmed_rows[matrix] PASSED [ 88%]
training/holistic_migration/tests/test_sequence.py::test_plain_rgb_resize_uses_area_and_preserves_rgb PASSED [ 89%]
training/holistic_migration/tests/test_sequence.py::test_image_rejects_semantic_or_invalid_arrays[image0] PASSED [ 89%]
training/holistic_migration/tests/test_sequence.py::test_image_rejects_semantic_or_invalid_arrays[image1] PASSED [ 90%]
training/holistic_migration/tests/test_sequence.py::test_image_rejects_semantic_or_invalid_arrays[image2] PASSED [ 90%]
training/holistic_migration/tests/test_sequence.py::test_image_rejects_semantic_or_invalid_arrays[image3] PASSED [ 91%]
training/holistic_migration/tests/test_sequence.py::test_capture_reports_source_denominator_even_when_no_bounded_interval PASSED [ 91%]
training/holistic_migration/tests/test_webcam.py::AdmissionTests::test_invalid_duration_precedes_paths_and_runtime 
training/holistic_migration/tests/test_webcam.py::AdmissionTests::test_invalid_duration_precedes_paths_and_runtime PASSED [ 92%]
training/holistic_migration/tests/test_webcam.py::AdmissionTests::test_paths_and_report_overwrite_rejected_before_build 
training/holistic_migration/tests/test_webcam.py::AdmissionTests::test_paths_and_report_overwrite_rejected_before_build PASSED [ 92%]
training/holistic_migration/tests/test_webcam.py::PixelsAndOverlayTests::test_actual_bgra_conversion_resize_and_no_input_mirror PASSED [ 93%]
training/holistic_migration/tests/test_webcam.py::PixelsAndOverlayTests::test_missing_components_real_counts_masks_connections_and_readable_text PASSED [ 93%]
training/holistic_migration/tests/test_webcam.py::PreviewLoopTests::test_additional_failure_stages_keep_disposition_and_teardown 
training/holistic_migration/tests/test_webcam.py::PreviewLoopTests::test_additional_failure_stages_keep_disposition_and_teardown PASSED [ 94%]
training/holistic_migration/tests/test_webcam.py::PreviewLoopTests::test_default_runtime_binds_actual_shared_detector_and_packer_without_loading_sdk PASSED [ 94%]
training/holistic_migration/tests/test_webcam.py::PreviewLoopTests::test_errors_cleanup_fault_and_handshake_admission_before_detector 
training/holistic_migration/tests/test_webcam.py::PreviewLoopTests::test_errors_cleanup_fault_and_handshake_admission_before_detector PASSED [ 95%]
training/holistic_migration/tests/test_webcam.py::PreviewLoopTests::test_no_implicit_report_and_main_uses_same_runner PASSED [ 95%]
training/holistic_migration/tests/test_webcam.py::PreviewLoopTests::test_quit_escape_window_close_and_deadline_release_all 
training/holistic_migration/tests/test_webcam.py::PreviewLoopTests::test_quit_escape_window_close_and_deadline_release_all PASSED [ 96%]
training/holistic_migration/tests/test_webcam.py::SourceReconciliationTests::test_healthy_deadline_deliberately_terminates_owned_child PASSED [ 96%]
training/holistic_migration/tests/test_webcam.py::SourceReconciliationTests::test_healthy_quit_deliberately_terminates_owned_child PASSED [ 97%]
training/holistic_migration/tests/test_webcam.py::SourceReconciliationTests::test_observed_source_failure_then_deadline PASSED [ 97%]
training/holistic_migration/tests/test_webcam.py::SourceReconciliationTests::test_observed_source_failure_then_escape PASSED [ 98%]
training/holistic_migration/tests/test_webcam.py::SourceReconciliationTests::test_observed_source_failure_then_quit PASSED [ 98%]
training/holistic_migration/tests/test_webcam.py::SourceReconciliationTests::test_observed_source_failure_then_window_close PASSED [ 99%]
training/holistic_migration/tests/test_webcam.py::SourceReconciliationTests::test_unexpected_child_exit_before_reader_publishes_error PASSED [100%]

================== 199 passed, 252 subtests passed in 49.52s ===================

```


### L02 continuation full-original-pytest-green

```sh
TMPDIR=/Users/ahronjanl.rafaelahron.0804icloudcom/.hermes/cache/scratch /bin/sh -c 'export TMPDIR="$HOME/.hermes/cache/scratch"; PY="$HOME/.kumpas-venvs/rv2-holistic-tf-20261101/bin/python"; "$PY" -E -B -m pytest -p no:cacheprovider training/tests -v'
```

Actual exit: 0; elapsed: 10.742s; timeout: False. Full stdout/stderr: `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-b-l02-resume-20261113-e79f7bd38c3141fa8d4c78a309234a7d/full-original-pytest-green.log` (SHA-256 `4b975e0cf7133b622fbf0503a5fc5e5bc01dd8fbc2d819e80ac108b190ab882b`). Exact command, before-run source hashes and 20 protected matches: `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-b-l02-resume-20261113-e79f7bd38c3141fa8d4c78a309234a7d/full-original-pytest-green.json`.

```text
============================= test session starts ==============================
platform darwin -- Python 3.11.15, pytest-9.2.0, pluggy-1.7.0 -- /Users/ahronjanl.rafaelahron.0804icloudcom/.kumpas-venvs/rv2-holistic-tf-20261101/bin/python
rootdir: /Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration
collecting ... collected 51 items

training/tests/test_evaluate_frozen.py::FrozenEvaluationTests::test_conflicting_manifest_refuses_evaluation_before_loading_model PASSED [  1%]
training/tests/test_evaluate_frozen.py::FrozenEvaluationTests::test_missing_freeze_refuses_evaluation_before_loading_model PASSED [  3%]
training/tests/test_evaluate_frozen.py::FrozenEvaluationTests::test_no_automatic_selection_by_test_score PASSED [  5%]
training/tests/test_evaluate_frozen.py::FrozenEvaluationTests::test_report_labels_test_reuse_and_signer_uncertainty PASSED [  7%]
training/tests/test_evaluation_protocol.py::EvaluationProtocolTests::test_duplicate_clip_name_is_rejected PASSED [  9%]
training/tests/test_evaluation_protocol.py::EvaluationProtocolTests::test_mismatched_clip_count_is_rejected PASSED [ 11%]
training/tests/test_evaluation_protocol.py::EvaluationProtocolTests::test_original_clips_split_before_augmentation PASSED [ 13%]
training/tests/test_evaluation_protocol.py::EvaluationProtocolTests::test_original_train_test_clip_overlap_is_rejected PASSED [ 15%]
training/tests/test_evaluation_protocol.py::EvaluationProtocolTests::test_source_digest_change_is_rejected PASSED [ 17%]
training/tests/test_experiment_runner.py::RunnerTests::test_binding_every_role_hash_symlink_and_array_refusal 
training/tests/test_experiment_runner.py::RunnerTests::test_binding_every_role_hash_symlink_and_array_refusal PASSED [ 19%]
training/tests/test_experiment_runner.py::RunnerTests::test_budget_exact_integer_matrix_and_variant_order_schema 
training/tests/test_experiment_runner.py::RunnerTests::test_budget_exact_integer_matrix_and_variant_order_schema PASSED [ 21%]
training/tests/test_experiment_runner.py::RunnerTests::test_cancel_before_start_and_invalid_clock_or_cancel_signal PASSED [ 23%]
training/tests/test_experiment_runner.py::RunnerTests::test_cli_prepares_and_synthetic_demo_only PASSED [ 25%]
training/tests/test_experiment_runner.py::RunnerTests::test_cli_training_arbitrary_command_invalid_and_safe_errors PASSED [ 27%]
training/tests/test_experiment_runner.py::RunnerTests::test_config_schema_authorization_numeric_and_selection 
training/tests/test_experiment_runner.py::RunnerTests::test_config_schema_authorization_numeric_and_selection PASSED [ 29%]
training/tests/test_experiment_runner.py::RunnerTests::test_explicit_unchanged_no_face_model_and_structured_labels 
training/tests/test_experiment_runner.py::RunnerTests::test_explicit_unchanged_no_face_model_and_structured_labels PASSED [ 31%]
training/tests/test_experiment_runner.py::RunnerTests::test_final_readback_fault_never_leaves_a_success_receipt PASSED [ 33%]
training/tests/test_experiment_runner.py::RunnerTests::test_manifest_tamper_and_log_symlink_refused PASSED [ 35%]
training/tests/test_experiment_runner.py::RunnerTests::test_prepare_exclusive_binding_and_immutable_snapshot PASSED [ 37%]
training/tests/test_experiment_runner.py::RunnerTests::test_prepare_protocol_semantics_rebound_hashes 
training/tests/test_experiment_runner.py::RunnerTests::test_prepare_protocol_semantics_rebound_hashes PASSED [ 39%]
training/tests/test_experiment_runner.py::RunnerTests::test_prepare_refuses_unsafe_roots_and_changed_bindings 
training/tests/test_experiment_runner.py::RunnerTests::test_prepare_refuses_unsafe_roots_and_changed_bindings PASSED [ 41%]
training/tests/test_experiment_runner.py::RunnerTests::test_protocol_original_clip_count_and_fraction_contract_rebound 
training/tests/test_experiment_runner.py::RunnerTests::test_protocol_original_clip_count_and_fraction_contract_rebound PASSED [ 43%]
training/tests/test_experiment_runner.py::RunnerTests::test_publication_collision_and_fsync_failure_preserve_old_bytes PASSED [ 45%]
training/tests/test_experiment_runner.py::RunnerTests::test_publication_interface_refuses_arbitrary_artifact_paths 
training/tests/test_experiment_runner.py::RunnerTests::test_publication_interface_refuses_arbitrary_artifact_paths PASSED [ 47%]
training/tests/test_experiment_runner.py::RunnerTests::test_selection_accuracy_then_macro_f1 PASSED [ 49%]
training/tests/test_experiment_runner.py::RunnerTests::test_strict_json_duplicate_and_nonfinite_rejected 
training/tests/test_experiment_runner.py::RunnerTests::test_strict_json_duplicate_and_nonfinite_rejected PASSED [ 50%]
training/tests/test_experiment_runner.py::RunnerTests::test_synthetic_input_and_manifest_change_fail_before_executor PASSED [ 52%]
training/tests/test_experiment_runner.py::RunnerTests::test_synthetic_order_ties_immutable_request_and_no_retry PASSED [ 54%]
training/tests/test_experiment_runner.py::RunnerTests::test_synthetic_output_tamper_has_no_success_receipt PASSED [ 56%]
training/tests/test_experiment_runner.py::RunnerTests::test_synthetic_stop_conditions_and_safe_incomplete_logs 
training/tests/test_experiment_runner.py::RunnerTests::test_synthetic_stop_conditions_and_safe_incomplete_logs PASSED [ 58%]
training/tests/test_experiment_runner.py::RunnerTests::test_synthetic_stop_exception_text_never_echoed PASSED [ 60%]
training/tests/test_export_frozen.py::FrozenExportTests::test_accepts_only_frozen_checkpoint_from_validated_protocol PASSED [ 62%]
training/tests/test_export_frozen.py::FrozenExportTests::test_frozen_export_preserves_validation_predictions_and_hashes PASSED [ 64%]
training/tests/test_export_frozen.py::FrozenExportTests::test_rejects_checkpoint_changed_after_freeze PASSED [ 66%]
training/tests/test_export_frozen.py::FrozenExportTests::test_rejects_other_protocol_manifest PASSED [ 68%]
training/tests/test_training_protocol.py::TrainingProtocolTests::test_load_explicit_unaugmented_validation PASSED [ 70%]
training/tests/test_training_protocol.py::TrainingProtocolTests::test_selection_uses_validation_not_historical_test PASSED [ 72%]
training/tests/test_training_protocol.py::TrainingProtocolTests::test_source_tampering_prevents_training PASSED [ 74%]
training/tests/test_validation_campaign.py::CampaignTests::test_metric_boundary_rejects_non_numeric_and_nonfinite_before_ranking 
training/tests/test_validation_campaign.py::CampaignTests::test_metric_boundary_rejects_non_numeric_and_nonfinite_before_ranking PASSED [ 76%]
training/tests/test_validation_campaign.py::InputTests::test_campaign_publishes_only_verified_outputs_and_retains_failures PASSED [ 78%]
training/tests/test_validation_campaign.py::InputTests::test_campaign_refuses_existing_escape_symlink_and_invalid_input_without_success 
training/tests/test_validation_campaign.py::InputTests::test_campaign_refuses_existing_escape_symlink_and_invalid_input_without_success PASSED [ 80%]
training/tests/test_validation_campaign.py::InputTests::test_identity_graph_rejects_tampering_and_malformed_metadata 
training/tests/test_validation_campaign.py::InputTests::test_identity_graph_rejects_tampering_and_malformed_metadata PASSED [ 82%]
training/tests/test_validation_campaign.py::InputTests::test_metadata_rejects_nonfinite_and_binds_frames_sampling_and_missingness PASSED [ 84%]
training/tests/test_validation_campaign.py::InputTests::test_protocol_counts_require_exact_integers_with_rebound_hashes 
training/tests/test_validation_campaign.py::InputTests::test_protocol_counts_require_exact_integers_with_rebound_hashes PASSED [ 86%]
training/tests/test_validation_campaign.py::InputTests::test_reject_shape_compatible_validation_tampering_even_when_current_hash_rebound PASSED [ 88%]
training/tests/test_validation_campaign.py::InputTests::test_selection_identity_policy_types_rejected_with_rebound_hashes 
training/tests/test_validation_campaign.py::InputTests::test_selection_identity_policy_types_rejected_with_rebound_hashes PASSED [ 90%]
training/tests/test_validation_campaign.py::BackendTests::test_backend_uses_inference_only_then_existing_candidate_and_checks_shapes PASSED [ 92%]
training/tests/test_validation_campaign.py::ResidencyTests::test_dataless_sources_fail_before_a_blocking_content_read PASSED [ 94%]
training/tests/test_validation_campaign.py::CliTests::test_cli_requires_bound_strict_config_and_fixed_safe_errors PASSED [ 96%]
training/tests/test_validation_campaign.py::DiagnosticTests::test_diagnostics_all_classes_counts_and_conversion_drift PASSED [ 98%]
training/tests/test_validation_campaign.py::ProbabilityTests::test_probability_boundary_rejects_shape_type_and_nonfinite 
training/tests/test_validation_campaign.py::ProbabilityTests::test_probability_boundary_rejects_shape_type_and_nonfinite PASSED [100%]

=============================== warnings summary ===============================
training/tests/test_export_frozen.py::FrozenExportTests::test_frozen_export_preserves_validation_predictions_and_hashes
training/tests/test_export_frozen.py::FrozenExportTests::test_frozen_export_preserves_validation_predictions_and_hashes
  /Users/ahronjanl.rafaelahron.0804icloudcom/.kumpas-venvs/rv2-holistic-tf-20261101/lib/python3.11/site-packages/keras/src/backend/tensorflow/core.py:172: DeprecationWarning: __array__ implementation doesn't accept a copy keyword, so passing copy=False failed. __array__ must implement 'dtype' and 'copy' keyword arguments.
    return np.array(x)

training/tests/test_export_frozen.py::FrozenExportTests::test_frozen_export_preserves_validation_predictions_and_hashes
  /Users/ahronjanl.rafaelahron.0804icloudcom/.kumpas-venvs/rv2-holistic-tf-20261101/lib/python3.11/site-packages/tensorflow/lite/python/interpreter.py:457: UserWarning:     Warning: tf.lite.Interpreter is deprecated and is scheduled for deletion in
      TF 2.20. Please use the LiteRT interpreter from the ai_edge_litert package.
      See the [migration guide](https://ai.google.dev/edge/litert/migration)
      for details.
      
    warnings.warn(_INTERPRETER_DELETION_WARNING)

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
============= 51 passed, 3 warnings, 289 subtests passed in 9.87s ==============

```


## L02 continuation delivered for parent re-review — 2026-11-13T11:10:25.426379+08:00

L02 is implemented and actually exercised. Successful thread acquisition is recognized by the real Thread identity, so an unstarted thread is not joined. Constructor rollback retains the original acquisition exception as CaptureError's explicit cause, with rollback diagnostics retained as exception notes. Teardown attempts both joins and both owned pipes despite earlier join/pipe faults, reports all observed teardown faults, and sets _closed only after successful completion. An incomplete or timed-out join and a failed pipe close remain retryable; already-closed pipes are skipped, and successful close is idempotent. The existing bounded owned-child terminate/wait/kill/wait path is unchanged and its existing synthetic SIGTERM-ignore escalation test passes.

### Actual vertical TDD ledger

- slice2a: one actual stderr-thread acquisition RED (primary was replaced by an unstarted join RuntimeError), then GREEN after the common successful-start guard.
- slice2b: the separately added frame-thread-start case was **coverage-only GREEN** after that shared guard; no independent new RED is claimed. Both starts were also independently verified by the corrected parent six-case harness.
- slice2c: actual RED because a reader join fault prevented the stderr join; GREEN after continuing later cleanup and leaving unsuccessful teardown retryable.
- slice2d: actual RED because stdout.close failure prevented stderr.close; GREEN after isolating pipe failures, retrying the incomplete pipe, and not re-closing completed pipes.
- slice2e: actual RED because simultaneous rollback join/pipe faults replaced the original frame-thread acquisition failure; GREEN retaining the primary cause, both secondary diagnostics, all later pipe cleanup, and a successful retry of the same partially constructed production capture.
- slice2f: actual RED because a real still-live joined thread was marked closed without reporting timeout; GREEN reporting the bounded join timeout, closing both pipes, then completing retry after the held thread is released.

Each RED/GREEN above already has its actual command, exit, complete log and before-run source hashes appended immediately in the preceding sections. No RED was fabricated or substituted from a reconstructed output. SourceReconciliationTests and L01 production code were retained, not redone.

### Final verification on delivered source

| Command scope | Actual result |
|---|---|
| Corrected parent harness, fresh run directory | 6 passed, 0 failures/errors, exit 0 |
| Current SourceReconciliationTests | 7 passed, exit 0 |
| Named test_camera.py + test_webcam.py | 34 passed, 58 subtests passed, exit 0 |
| Exact brief pytest migration command | 199 passed, 252 subtests passed, exit 0; includes all 125 Task C function cases |
| Exact brief pytest original command | 51 passed, 289 subtests passed, 3 retained Keras/TFLite deprecation warnings, exit 0 |

All required commands use the existing combined interpreter with -E -B and scratch TMPDIR. No skips or missing C test collection were accepted. The named/full runs include real native pure compilation/self-test with camera_access=false; no capture hardware, GUI launch or model fitting was performed.

Continuation-owned changed existing repository files are only camera.py, tests/test_camera.py and this append-only report. webcam.py and tests/test_webcam.py exactly match the landed-L01 continuation preimages. All 20 protected A/C/Swift/contract paths still match their authority receipt. The whole before/after inventory has no removals or other changed existing files. One concurrent unowned addition, docs/holistic-migration/task-c-review-recovery-1.json, was observed and left untouched; it is not a B deliverable. Original tracked diff and index diff remain empty; branch/HEAD are holistic-migration/4d901693642af5f572455b2c75ba095b0ec65c7f. The entire pre-continuation report byte prefix remains exact.

Evidence root: `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-b-l02-resume-20261113-e79f7bd38c3141fa8d4c78a309234a7d`. Immutable preimages: `snapshot-index.json`. Exact commands/log hashes: per-run JSON/log files and final `handoff.json`. Full C collection proof: `full-pytest-task-c-cases.json`. Current protection: `protection-after.json`. Frozen four-source/test postimages are under `postimages/`; external handoff binds the final report hash without a self-referential report hash.

Delivered source hashes:

- `training/holistic_migration/camera.py`: `bf1f77ce2b67e8611f659f3a6589a10937a8c78753849232b920819a7197a2c4`
- `training/holistic_migration/webcam.py`: `23c03f6220330fd90ebe8a1b19db52d86ef3eb5e27b35fae29580182e4216389`
- `training/holistic_migration/tests/test_camera.py`: `6136d9da96210997be89448b687e42df841797a0cc1dceb34d79192ce48bab55`
- `training/holistic_migration/tests/test_webcam.py`: `696eecf639021cd545782be5ad0a3e5504fe33e60b113bceebb6cbd2c5311400`

No installs, commits, pushes, provider/model configuration changes, camera/GUI capture, participant processing or A/C/Swift/contract edits occurred in this continuation. No blocking test failure remains. Parent independent affected-scope re-review/acceptance is still required; live/human webcam acceptance remains deferred and is not claimed. Persistent OS/resource failures are surfaced and remain retryable, not a guarantee that an unreleasable resource can be forced closed.


## B fix2 L03/MR02 recovery — 2026-11-13T11:59:06.945098+08:00

Authorized second bounded B repair only: webcam.py, test_webcam.py and this append-only report. All 7 exact preimages in `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-b-before-fix2-1447c3d21f7e4d5aa834c7a89a64cd47/snapshot-index.json` and 102 historical artifact hashes verified before writes. All 22 fresh protected A/C/camera/Swift/contract paths match `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-c-fix1-parent-b-review2/task-b-fix2-protection.json`. Original tracked/index diffs are empty, branch holistic-migration. Parent's actual 13-case RED (7 failures, 0 errors) is preserved, not overwritten or claimed as owned RED. Exclusive execution/evidence root: `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-b-fix2-97f6bace91c342ef8a558ae2ed0b9498`.

Root cause: report serialization/write/flush/close escape finally before raise primary; native-tail stderr has the same precedence escape and skips report close. Strict vertical sequence: source/report write first, then remaining report/first-error controls; diagnostic-stderr separately. No camera/GUI/SDK or dataset inference, fitting, installs, commits, pushes or configuration changes are authorized. Human webcam acceptance stays deferred.

### fix2 actual source-report-write-red — 2026-11-13T12:00:12.994137+08:00

Command (repository root; TMPDIR=/Users/ahronjanl.rafaelahron.0804icloudcom/.hermes/cache/scratch):

```sh
/Users/ahronjanl.rafaelahron.0804icloudcom/.kumpas-venvs/rv2-holistic-tf-20261101/bin/python -E -B -m pytest -p no:cacheprovider training/holistic_migration/tests/test_webcam.py::FinalizationPrecedenceTests::test_source_primary_survives_report_write -v
```

Actual exit: **1** (expected 1). Source hashes: `{"training/holistic_migration/tests/test_webcam.py": "3fcb23e7af2f46538f6220376d2b7b501e4412a795a50796374e2021dda816bf", "training/holistic_migration/webcam.py": "23c03f6220330fd90ebe8a1b19db52d86ef3eb5e27b35fae29580182e4216389"}`. Complete log: `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-b-fix2-97f6bace91c342ef8a558ae2ed0b9498/source-report-write-red/output.log` (SHA-256 `3b51a26bfd5e9ac734462b9c5693f7742fbdf53919ba7aefad82bbf05cd90f2f`); receipt: `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-b-fix2-97f6bace91c342ef8a558ae2ed0b9498/source-report-write-red/receipt.json`.

```text
============================== 1 failed in 0.51s ===============================
```


## B fix2 L03/MR02 resumed unfinished partial — 2026-11-13T19:25:50.018169+08:00

This continues the second and last automatic B repair; interruption is not a new repair cycle. Recovery authority: `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/resume-b2-c-review-20261113T192137/snapshot-index.json`. All three current partial preimages match that snapshot, including retained unused finalization helper and the owned source/write RED test. Prior report prefix is preserved verbatim. Fresh verification before edits: all22 protected A/C/camera/Swift paths match `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-c-fix1-parent-b-review2/task-b-fix2-protection.json`; branch holistic-migration and original tracked/index diffs are empty. L01/L02 remain closed and untouched. No current provider block is established and no provider changes are authorized. Exclusive evidence root: `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-b-fix2-resume-20261113T192550-77535f667c5548a182636529233020e8`. Strict vertical continuation starts with the existing owned source/write behavioral RED, then minimal repair, report sibling coverage, and a separate diagnostic-stderr RED/GREEN tracer. No camera/GUI/real inference/fitting/install/commit/push/configuration operations.


### fix2 continuation source-report-write-red — 2026-11-13T19:25:50.018417+08:00

Fresh owned behavioral RED from the preserved partial test before repairing any call site.

```sh
TMPDIR=/Users/ahronjanl.rafaelahron.0804icloudcom/.hermes/cache/scratch /Users/ahronjanl.rafaelahron.0804icloudcom/.kumpas-venvs/rv2-holistic-tf-20261101/bin/python -E -B -m pytest -p no:cacheprovider training/holistic_migration/tests/test_webcam.py::FinalizationPrecedenceTests::test_source_primary_survives_report_write -v
```

Actual exit **1**; FAILED training/holistic_migration/tests/test_webcam.py::FinalizationPrecedenceTests::test_source_primary_survives_report_write | ============================== 1 failed in 0.47s ===============================

Full log: `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-b-fix2-resume-20261113T192550-77535f667c5548a182636529233020e8/source-report-write-red/output.log`; SHA-256 `bc8e91e17f726358f9381b8f41c61276d1cc4910bc6400d8f2197492585b95d7`. Exact source bindings and command receipt: `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-b-fix2-resume-20261113T192550-77535f667c5548a182636529233020e8/source-report-write-red/receipt.json`.


### fix2 continuation source-report-write-green — 2026-11-13T19:26:03.300335+08:00

Minimal write catch now retains the original CaptureError/EOF cause, attached write exception/cause and safe stage/type note; acquired report close is attempted. Serialization/flush/close not yet repaired.

```sh
TMPDIR=/Users/ahronjanl.rafaelahron.0804icloudcom/.hermes/cache/scratch /Users/ahronjanl.rafaelahron.0804icloudcom/.kumpas-venvs/rv2-holistic-tf-20261101/bin/python -E -B -m pytest -p no:cacheprovider training/holistic_migration/tests/test_webcam.py::FinalizationPrecedenceTests::test_source_primary_survives_report_write -v
```

Actual exit **0**; ============================== 1 passed in 0.40s ===============================

Full log: `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-b-fix2-resume-20261113T192550-77535f667c5548a182636529233020e8/source-report-write-green/output.log`; SHA-256 `27530e00d21ecf9ecf4b4acf10b78775bc116545d550e600cefc08ac2e3f55e2`. Exact source bindings and command receipt: `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-b-fix2-resume-20261113T192550-77535f667c5548a182636529233020e8/source-report-write-green/receipt.json`.


### fix2 continuation source-report-serialize-red — 2026-11-13T19:26:17.478650+08:00

Next vertical tracer: serialization fault must not replace an existing source primary; closure still required.

```sh
TMPDIR=/Users/ahronjanl.rafaelahron.0804icloudcom/.hermes/cache/scratch /Users/ahronjanl.rafaelahron.0804icloudcom/.kumpas-venvs/rv2-holistic-tf-20261101/bin/python -E -B -m pytest -p no:cacheprovider training/holistic_migration/tests/test_webcam.py::FinalizationPrecedenceTests::test_source_primary_survives_report_serialization -v
```

Actual exit **1**; FAILED training/holistic_migration/tests/test_webcam.py::FinalizationPrecedenceTests::test_source_primary_survives_report_serialization | ============================== 1 failed in 0.42s ===============================

Full log: `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-b-fix2-resume-20261113T192550-77535f667c5548a182636529233020e8/source-report-serialize-red/output.log`; SHA-256 `21e0a5a0cb22e812169ddd10dd788e12719aaac192de39228e5a903c3e5bde63`. Exact source bindings and command receipt: `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-b-fix2-resume-20261113T192550-77535f667c5548a182636529233020e8/source-report-serialize-red/receipt.json`.


### fix2 continuation source-report-serialize-green — 2026-11-13T19:26:33.014633+08:00

Serialization catch preserves the source object/cause and secondary diagnostics; write tracer remains GREEN.

```sh
TMPDIR=/Users/ahronjanl.rafaelahron.0804icloudcom/.hermes/cache/scratch /Users/ahronjanl.rafaelahron.0804icloudcom/.kumpas-venvs/rv2-holistic-tf-20261101/bin/python -E -B -m pytest -p no:cacheprovider training/holistic_migration/tests/test_webcam.py::FinalizationPrecedenceTests -v
```

Actual exit **0**; ============================== 2 passed in 0.42s ===============================

Full log: `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-b-fix2-resume-20261113T192550-77535f667c5548a182636529233020e8/source-report-serialize-green/output.log`; SHA-256 `6c17adc9485b4a85357e12f14b6254cba1991f01b56bad0a36001b19af17f80c`. Exact source bindings and command receipt: `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-b-fix2-resume-20261113T192550-77535f667c5548a182636529233020e8/source-report-serialize-green/receipt.json`.


### fix2 continuation source-report-flush-red — 2026-11-13T19:26:46.299069+08:00

Next vertical tracer: flush fault after a full write replaces the source primary before repair.

```sh
TMPDIR=/Users/ahronjanl.rafaelahron.0804icloudcom/.hermes/cache/scratch /Users/ahronjanl.rafaelahron.0804icloudcom/.kumpas-venvs/rv2-holistic-tf-20261101/bin/python -E -B -m pytest -p no:cacheprovider training/holistic_migration/tests/test_webcam.py::FinalizationPrecedenceTests::test_source_primary_survives_report_flush -v
```

Actual exit **1**; FAILED training/holistic_migration/tests/test_webcam.py::FinalizationPrecedenceTests::test_source_primary_survives_report_flush | ============================== 1 failed in 0.25s ===============================

Full log: `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-b-fix2-resume-20261113T192550-77535f667c5548a182636529233020e8/source-report-flush-red/output.log`; SHA-256 `793dd8656cbde37589f84b58d00268152acd16a9a89e99d60828bfe020898d2d`. Exact source bindings and command receipt: `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-b-fix2-resume-20261113T192550-77535f667c5548a182636529233020e8/source-report-flush-red/receipt.json`.


### fix2 continuation source-report-flush-green — 2026-11-13T19:27:00.014239+08:00

Minimal flush catch retains primary identity/cause; prior serialization/write tracers stay GREEN.

```sh
TMPDIR=/Users/ahronjanl.rafaelahron.0804icloudcom/.hermes/cache/scratch /Users/ahronjanl.rafaelahron.0804icloudcom/.kumpas-venvs/rv2-holistic-tf-20261101/bin/python -E -B -m pytest -p no:cacheprovider training/holistic_migration/tests/test_webcam.py::FinalizationPrecedenceTests -v
```

Actual exit **0**; ============================== 3 passed in 0.42s ===============================

Full log: `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-b-fix2-resume-20261113T192550-77535f667c5548a182636529233020e8/source-report-flush-green/output.log`; SHA-256 `120081ffaa3e46e2d116d75ad4950e2f41424af68a846e74d289fbcabc12f725`. Exact source bindings and command receipt: `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-b-fix2-resume-20261113T192550-77535f667c5548a182636529233020e8/source-report-flush-green/receipt.json`.


### fix2 continuation source-report-close-red — 2026-11-13T19:27:16.178281+08:00

Next vertical tracer: close failure is still raised instead of the source primary; no successful-close claim is permitted.

```sh
TMPDIR=/Users/ahronjanl.rafaelahron.0804icloudcom/.hermes/cache/scratch /Users/ahronjanl.rafaelahron.0804icloudcom/.kumpas-venvs/rv2-holistic-tf-20261101/bin/python -E -B -m pytest -p no:cacheprovider training/holistic_migration/tests/test_webcam.py::FinalizationPrecedenceTests::test_source_primary_survives_report_close -v
```

Actual exit **1**; FAILED training/holistic_migration/tests/test_webcam.py::FinalizationPrecedenceTests::test_source_primary_survives_report_close | ============================== 1 failed in 0.43s ===============================

Full log: `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-b-fix2-resume-20261113T192550-77535f667c5548a182636529233020e8/source-report-close-red/output.log`; SHA-256 `092d9786a55e478f1ffa665912d7cd36c9c787326ea26046cf7a17f1f922ba1f`. Exact source bindings and command receipt: `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-b-fix2-resume-20261113T192550-77535f667c5548a182636529233020e8/source-report-close-red/receipt.json`.


### fix2 continuation source-report-close-green — 2026-11-13T19:27:34.862511+08:00

Close catch preserves source identity/EOF cause and attaches the actual close error. The faulting stream remains unclosed and no successful return occurs.

```sh
TMPDIR=/Users/ahronjanl.rafaelahron.0804icloudcom/.hermes/cache/scratch /Users/ahronjanl.rafaelahron.0804icloudcom/.kumpas-venvs/rv2-holistic-tf-20261101/bin/python -E -B -m pytest -p no:cacheprovider training/holistic_migration/tests/test_webcam.py::FinalizationPrecedenceTests -v
```

Actual exit **0**; ============================== 4 passed in 0.45s ===============================

Full log: `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-b-fix2-resume-20261113T192550-77535f667c5548a182636529233020e8/source-report-close-green/output.log`; SHA-256 `7a8c4e6746f4f5f9f7c2bab695a05e7c5451e703b030942dd79fa03d8e870eb2`. Exact source bindings and command receipt: `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-b-fix2-resume-20261113T192550-77535f667c5548a182636529233020e8/source-report-close-green/receipt.json`.


### fix2 continuation report-sibling-controls-coverage-green — 2026-11-13T19:28:14.252284+08:00

Coverage-only GREEN: detector siblings, healthy first-error controls, first serialization/write/flush error followed by close error, dual secondary errors, and healthy/no-output-fault controls already work after the four source tracers. These variants are not claimed as additional behavioral RED.

```sh
TMPDIR=/Users/ahronjanl.rafaelahron.0804icloudcom/.hermes/cache/scratch /Users/ahronjanl.rafaelahron.0804icloudcom/.kumpas-venvs/rv2-holistic-tf-20261101/bin/python -E -B -m pytest -p no:cacheprovider training/holistic_migration/tests/test_webcam.py::FinalizationPrecedenceTests -v
```

Actual exit **0**; ==================== 9 passed, 20 subtests passed in 0.52s =====================

Full log: `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-b-fix2-resume-20261113T192550-77535f667c5548a182636529233020e8/report-sibling-controls-coverage-green/output.log`; SHA-256 `7f009ddbd14f09ab8f1dc0cdb155086706137bdb5b56971d1093ac4a93e5e75c`. Exact source bindings and command receipt: `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-b-fix2-resume-20261113T192550-77535f667c5548a182636529233020e8/report-sibling-controls-coverage-green/receipt.json`.


### fix2 continuation diagnostic-stderr-source-red — 2026-11-13T19:28:31.855999+08:00

Separate L03a diagnostic-stderr tracer: stderr failure still replaces source primary and skips report close. Capture/detector/window hooks already ran; no native child leak is asserted.

```sh
TMPDIR=/Users/ahronjanl.rafaelahron.0804icloudcom/.hermes/cache/scratch /Users/ahronjanl.rafaelahron.0804icloudcom/.kumpas-venvs/rv2-holistic-tf-20261101/bin/python -E -B -m pytest -p no:cacheprovider training/holistic_migration/tests/test_webcam.py::FinalizationPrecedenceTests::test_source_primary_survives_diagnostic_stderr_and_closes_report -v
```

Actual exit **1**; FAILED training/holistic_migration/tests/test_webcam.py::FinalizationPrecedenceTests::test_source_primary_survives_diagnostic_stderr_and_closes_report | ============================== 1 failed in 0.43s ===============================

Full log: `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-b-fix2-resume-20261113T192550-77535f667c5548a182636529233020e8/diagnostic-stderr-source-red/output.log`; SHA-256 `47112164a8d5d3f8917783cc0db67fa74521ff3e01d9d7d34fd3ca574c0fa1a6`. Exact source bindings and command receipt: `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-b-fix2-resume-20261113T192550-77535f667c5548a182636529233020e8/diagnostic-stderr-source-red/receipt.json`.


### fix2 continuation diagnostic-stderr-source-green — 2026-11-13T19:28:48.992923+08:00

Diagnostic catch retains original source/EOF cause, safely attaches stderr failure and continues into acquired report serialization/write/flush/close; previous report tracers stay GREEN.

```sh
TMPDIR=/Users/ahronjanl.rafaelahron.0804icloudcom/.hermes/cache/scratch /Users/ahronjanl.rafaelahron.0804icloudcom/.kumpas-venvs/rv2-holistic-tf-20261101/bin/python -E -B -m pytest -p no:cacheprovider training/holistic_migration/tests/test_webcam.py::FinalizationPrecedenceTests -v
```

Actual exit **0**; ==================== 10 passed, 20 subtests passed in 0.50s ====================

Full log: `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-b-fix2-resume-20261113T192550-77535f667c5548a182636529233020e8/diagnostic-stderr-source-green/output.log`; SHA-256 `dfeca9f1e750ae143fdecaed6c1ba49eb870abb07e181433415217e5014a9761`. Exact source bindings and command receipt: `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-b-fix2-resume-20261113T192550-77535f667c5548a182636529233020e8/diagnostic-stderr-source-green/receipt.json`.


### fix2 continuation diagnostic-sibling-controls-coverage-green — 2026-11-13T19:29:23.820864+08:00

Coverage-only GREEN after the diagnostic tracer: source/detector/healthy stderr failures, no-report paths, every later report stage, and simultaneous write+close faults retain ordered actual secondary objects without private strings in JSON.

```sh
TMPDIR=/Users/ahronjanl.rafaelahron.0804icloudcom/.hermes/cache/scratch /Users/ahronjanl.rafaelahron.0804icloudcom/.kumpas-venvs/rv2-holistic-tf-20261101/bin/python -E -B -m pytest -p no:cacheprovider training/holistic_migration/tests/test_webcam.py::FinalizationPrecedenceTests -v
```

Actual exit **0**; ==================== 13 passed, 41 subtests passed in 0.53s ====================

Full log: `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-b-fix2-resume-20261113T192550-77535f667c5548a182636529233020e8/diagnostic-sibling-controls-coverage-green/output.log`; SHA-256 `96946116de1ef3171cdfb901693d5e07899f3f3ae77b450959ab5938a38e4630`. Exact source bindings and command receipt: `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-b-fix2-resume-20261113T192550-77535f667c5548a182636529233020e8/diagnostic-sibling-controls-coverage-green/receipt.json`.


### fix2 continuation prior-cleanup-diagnostic-precedence-red — 2026-11-13T19:29:54.108610+08:00

Same L03 diagnostic precedence class, not a reopened L02 teardown repair: the already-collected cleanup error must be promoted before later stderr I/O can become primary. No camera.py changes.

```sh
TMPDIR=/Users/ahronjanl.rafaelahron.0804icloudcom/.hermes/cache/scratch /Users/ahronjanl.rafaelahron.0804icloudcom/.kumpas-venvs/rv2-holistic-tf-20261101/bin/python -E -B -m pytest -p no:cacheprovider training/holistic_migration/tests/test_webcam.py::FinalizationPrecedenceTests::test_prior_cleanup_failure_is_not_replaced_by_diagnostic_stderr -v
```

Actual exit **1**; FAILED training/holistic_migration/tests/test_webcam.py::FinalizationPrecedenceTests::test_prior_cleanup_failure_is_not_replaced_by_diagnostic_stderr | ============================== 1 failed in 0.51s ===============================

Full log: `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-b-fix2-resume-20261113T192550-77535f667c5548a182636529233020e8/prior-cleanup-diagnostic-precedence-red/output.log`; SHA-256 `d9e1533c5b0340907911f0dd757007b693884e384ae0d30b326588743d8acbc0`. Exact source bindings and command receipt: `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-b-fix2-resume-20261113T192550-77535f667c5548a182636529233020e8/prior-cleanup-diagnostic-precedence-red/receipt.json`.


### fix2 continuation prior-cleanup-diagnostic-precedence-green — 2026-11-13T19:30:12.948535+08:00

Minimal ordering correction: previously collected cleanup failure is chosen before diagnostic output. Existing source reconciliation still precedes cleanup disposition and is unchanged; report and diagnostic tracers remain GREEN.

```sh
TMPDIR=/Users/ahronjanl.rafaelahron.0804icloudcom/.hermes/cache/scratch /Users/ahronjanl.rafaelahron.0804icloudcom/.kumpas-venvs/rv2-holistic-tf-20261101/bin/python -E -B -m pytest -p no:cacheprovider training/holistic_migration/tests/test_webcam.py::FinalizationPrecedenceTests -v
```

Actual exit **0**; ==================== 14 passed, 41 subtests passed in 0.53s ====================

Full log: `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-b-fix2-resume-20261113T192550-77535f667c5548a182636529233020e8/prior-cleanup-diagnostic-precedence-green/output.log`; SHA-256 `249b70838e98f7a067c029742272a82aa9f12934d97b66a19bdf9926582f89d4`. Exact source bindings and command receipt: `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-b-fix2-resume-20261113T192550-77535f667c5548a182636529233020e8/prior-cleanup-diagnostic-precedence-green/receipt.json`.


### fix2 continuation finalization-refactor-green — 2026-11-13T19:30:57.330654+08:00

Post-GREEN refactor only: flatten the three report stages into a fixed-stage try/except/finally; strengthen actual secondary-cause identity and safe-note assertions. No new behavior or lifecycle refactor. Transient editor nullable/unbound diagnostics were fixed with an assertion and pre-try stage initialization.

```sh
TMPDIR=/Users/ahronjanl.rafaelahron.0804icloudcom/.hermes/cache/scratch /Users/ahronjanl.rafaelahron.0804icloudcom/.kumpas-venvs/rv2-holistic-tf-20261101/bin/python -E -B -m pytest -p no:cacheprovider training/holistic_migration/tests/test_webcam.py::FinalizationPrecedenceTests -v
```

Actual exit **0**; ==================== 14 passed, 41 subtests passed in 0.55s ====================

Full log: `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-b-fix2-resume-20261113T192550-77535f667c5548a182636529233020e8/finalization-refactor-green/output.log`; SHA-256 `22b5c846a1bf2eb4fede7fb9a797a51d4712e0643501ac49806e7da0e87f64dd`. Exact source bindings and command receipt: `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-b-fix2-resume-20261113T192550-77535f667c5548a182636529233020e8/finalization-refactor-green/receipt.json`.


### fix2 continuation original-parent13-green — 2026-11-13T19:31:13.181215+08:00

Fresh byte-identical copy of the named original13-case parent precedence harness; its historical RED is retained separately.

```sh
TMPDIR=/Users/ahronjanl.rafaelahron.0804icloudcom/.hermes/cache/scratch /Users/ahronjanl.rafaelahron.0804icloudcom/.kumpas-venvs/rv2-holistic-tf-20261101/bin/python -E -B /Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-b-fix2-resume-20261113T192550-77535f667c5548a182636529233020e8/original-parent13/parent_report_red.py
```

Actual exit **0**; Ran 13 tests in 0.437s | OK | PRIMARY_REPORT_RECEIPT /Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-b-fix2-resume-20261113T192550-77535f667c5548a182636529233020e8/original-parent13/parent_report_red.result.json

Full log: `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-b-fix2-resume-20261113T192550-77535f667c5548a182636529233020e8/original-parent13-green/output.log`; SHA-256 `a8fe8c2bebae582a8a566b4a2bf746e6e0c1d5ac2eca4d2c29a9c80b3ef7b879`. Exact source bindings and command receipt: `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-b-fix2-resume-20261113T192550-77535f667c5548a182636529233020e8/original-parent13-green/receipt.json`.


### fix2 continuation original-parent6-green — 2026-11-13T19:31:13.181315+08:00

Fresh byte-identical copy of the named original6-case corrected parent source/constructor harness; this is regression verification only, not restarted L01/L02 repair.

```sh
TMPDIR=/Users/ahronjanl.rafaelahron.0804icloudcom/.hermes/cache/scratch /Users/ahronjanl.rafaelahron.0804icloudcom/.kumpas-venvs/rv2-holistic-tf-20261101/bin/python -E -B /Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-b-fix2-resume-20261113T192550-77535f667c5548a182636529233020e8/original-parent6/parent_fault_regressions.py
```

Actual exit **0**; Ran 6 tests in 0.387s | OK | PARENT_FAULT_RECEIPT /Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-b-fix2-resume-20261113T192550-77535f667c5548a182636529233020e8/original-parent6/parent-regression-runs/d04e272a278340d0b11d4ada07d85235/observations.json

Full log: `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-b-fix2-resume-20261113T192550-77535f667c5548a182636529233020e8/original-parent6-green/output.log`; SHA-256 `6b7ebb8cad7ef3cdd6fc04e1ffe4a5ac7d0c4f83f858e4ea83936493be4ff4d0`. Exact source bindings and command receipt: `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-b-fix2-resume-20261113T192550-77535f667c5548a182636529233020e8/original-parent6-green/receipt.json`.


### fix2 continuation source-reconciliation-green — 2026-11-13T19:31:38.009924+08:00

Required current production OwnedCapture binary-pipe reconciliation: q/Escape/window-close/deadline, healthy q/deadline and unexpected exit before reader publication. Synthetic detector and inert GUI only.

```sh
TMPDIR=/Users/ahronjanl.rafaelahron.0804icloudcom/.hermes/cache/scratch /Users/ahronjanl.rafaelahron.0804icloudcom/.kumpas-venvs/rv2-holistic-tf-20261101/bin/python -E -B -m pytest -p no:cacheprovider training/holistic_migration/tests/test_webcam.py::SourceReconciliationTests -v --junitxml=/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-b-fix2-resume-20261113T192550-77535f667c5548a182636529233020e8/source-reconciliation-green/results.xml
```

Actual exit **0**; ============================== 7 passed in 0.73s ===============================

Full log: `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-b-fix2-resume-20261113T192550-77535f667c5548a182636529233020e8/source-reconciliation-green/output.log`; SHA-256 `ff967fcbe6f3a69653083c7cad602574e648b9657a4cb2d67815c86770196fc0`. Exact source bindings and command receipt: `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-b-fix2-resume-20261113T192550-77535f667c5548a182636529233020e8/source-reconciliation-green/receipt.json`.


### fix2 continuation named-camera-webcam-green — 2026-11-13T19:31:39.104384+08:00

Required named current B suite including fixed L03 and unchanged camera/L01/L02 coverage. Native compilation and pure --self-test only; no discovery/camera session or real GUI/inference.

```sh
TMPDIR=/Users/ahronjanl.rafaelahron.0804icloudcom/.hermes/cache/scratch /Users/ahronjanl.rafaelahron.0804icloudcom/.kumpas-venvs/rv2-holistic-tf-20261101/bin/python -E -B -m pytest -p no:cacheprovider training/holistic_migration/tests/test_camera.py training/holistic_migration/tests/test_webcam.py -v --junitxml=/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-b-fix2-resume-20261113T192550-77535f667c5548a182636529233020e8/named-camera-webcam-green/results.xml
```

Actual exit **0**; ==================== 48 passed, 99 subtests passed in 5.64s ====================

Full log: `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-b-fix2-resume-20261113T192550-77535f667c5548a182636529233020e8/named-camera-webcam-green/output.log`; SHA-256 `3858ae6f7818095fd5f167f6b5b131d73c745cd3903313001e0b5a28f5ba0c00`. Exact source bindings and command receipt: `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-b-fix2-resume-20261113T192550-77535f667c5548a182636529233020e8/named-camera-webcam-green/receipt.json`.


### fix2 continuation full-original-pytest-green — 2026-11-13T19:31:59.471005+08:00

Required current full original training regression suite. Includes its existing initialized synthetic TensorFlow export/parity fixture, not fitting or real dataset/candidate inference. Original sources remain untouched.

```sh
TMPDIR=/Users/ahronjanl.rafaelahron.0804icloudcom/.hermes/cache/scratch /Users/ahronjanl.rafaelahron.0804icloudcom/.kumpas-venvs/rv2-holistic-tf-20261101/bin/python -E -B -m pytest -p no:cacheprovider training/tests -v --junitxml=/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-b-fix2-resume-20261113T192550-77535f667c5548a182636529233020e8/full-original-pytest-green/results.xml
```

Actual exit **0**;   /Users/ahronjanl.rafaelahron.0804icloudcom/.kumpas-venvs/rv2-holistic-tf-20261101/lib/python3.11/site-packages/keras/src/backend/tensorflow/core.py:172: DeprecationWarning: __array__ implementation doesn't accept a copy keyword, so passing copy=False failed. __array__ must implement 'dtype' and 'copy' keyword arguments. | ============= 51 passed, 3 warnings, 289 subtests passed in 11.40s =============

Full log: `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-b-fix2-resume-20261113T192550-77535f667c5548a182636529233020e8/full-original-pytest-green/output.log`; SHA-256 `b346147e8278c71cbcffcf28bba2cfcd62fd10c12146dac41ff17fe4644954ed`. Exact source bindings and command receipt: `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-b-fix2-resume-20261113T192550-77535f667c5548a182636529233020e8/full-original-pytest-green/receipt.json`.


### fix2 continuation full-migration-pytest-green — 2026-11-13T19:31:59.470677+08:00

Required current full migration suite, including all pytest function tests from delivered C; not unittest-only discovery. Native checks are pure and detector interfaces use synthetic SDK fixtures.

```sh
TMPDIR=/Users/ahronjanl.rafaelahron.0804icloudcom/.hermes/cache/scratch /Users/ahronjanl.rafaelahron.0804icloudcom/.kumpas-venvs/rv2-holistic-tf-20261101/bin/python -E -B -m pytest -p no:cacheprovider training/holistic_migration/tests -v --junitxml=/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-b-fix2-resume-20261113T192550-77535f667c5548a182636529233020e8/full-migration-pytest-green/results.xml
```

Actual exit **0**; ================== 285 passed, 293 subtests passed in 43.63s ===================

Full log: `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-b-fix2-resume-20261113T192550-77535f667c5548a182636529233020e8/full-migration-pytest-green/output.log`; SHA-256 `a09305391cda9a4c44d5b50526650b14c78df9b18f7a2f569ff10b78b12d4423`. Exact source bindings and command receipt: `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-b-fix2-resume-20261113T192550-77535f667c5548a182636529233020e8/full-migration-pytest-green/receipt.json`.


## B fix2 L03/MR02 delivered continuation — 2026-11-13T19:36:11.678391+08:00

### Outcome and exact scope

The unfinished second/last automatic repair is delivered for parent independent affected-scope specification and quality re-review; this is not parent acceptance and not a new repair cycle. Only `training/holistic_migration/webcam.py`, `training/holistic_migration/tests/test_webcam.py` and this report appendix changed from the supplied partial recovery. The retained helper/test were preserved and completed. L01/L02 source was not restarted or changed. Continuation source delta against the recovery partial: webcam18 added/6 removed lines; tests185 added/3 removed lines.

Finalization now retains the exact earlier primary and its cause through report serialization/write/flush/close and native diagnostic stderr failures. Actual secondary exceptions and causes remain attached in ordered `(fixed_stage, exception)` tuples on `primary.finalization_errors`; notes contain stage/type only, never arbitrary exception messages. Structured operational JSON receives no arbitrary error text or secondary exception objects. When output I/O is first, its exact exception remains primary through later close errors and the runner raises rather than returning successfully. Previously collected cleanup errors are selected before diagnostic stderr, so later diagnostic I/O cannot replace them. Acquired report close is attempted once after serialization/write/flush or stderr failure; a failed close remains failed, without retry, overwrite or publication-success claim. A pre-close session payload is not a successful-report receipt; partial failed artifacts are preserved.

### Strict vertical evidence

Six actual one-case behavioral RED→GREEN tracers were executed in order: source/write, source/serialization, source/flush, source/close, source/diagnostic-stderr, prior-cleanup/diagnostic-stderr. Every RED exited1 on the intended primary-identity assertion, not a harness error. Each minimal corresponding implementation then passed before the next failing tracer was added. Already-passing detector/healthy/multiple-output/no-report variants are explicitly coverage-only GREEN, not additional RED. Post-GREEN refactor flattened only the report stage catches; stronger safe-note and secondary-cause identity assertions passed. Complete command/log/source-hash ledger: `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-b-fix2-resume-20261113T192550-77535f667c5548a182636529233020e8/commands.json` (21 actual commands). All17 source/test byte versions referenced by those receipts are retained in `executed-source-versions/`; reconstructed after execution from the exact preimage/current bytes and recorded edits, and every complete version matches the actually executed receipt SHA-256. Reconstruction is not another execution.

### Fresh required verification

| Scope | Framework cases passed | Subtests passed | Warnings | Exit |
|---|---:|---:|---:|---:|
| Owned finalization precedence | 14 | 41 | 0 | 0 |
| Original parent13 precedence harness, byte-identical fresh copy | 13 | n/a | 0 | 0 |
| Original parent6 source/constructor harness, byte-identical fresh copy | 6 | n/a | 0 | 0 |
| SourceReconciliationTests, real production synthetic binary pipes | 7 | 0 | 0 | 0 |
| Named camera/webcam suite | 48 | 99 | 0 | 0 |
| Current full migration pytest suite | 285 | 293 | 0 | 0 |
| Current full original training pytest suite | 51 | 289 | 3 | 0 |

All final verification has zero failures/errors/skips. Counts overlap and are not summed. XML testcase elements independently match7/48/285/51 framework cases; pytest XML tests attributes additionally include subtests, so those larger attributes are not case totals. Full migration includes all delivered C pytest-function tests (dataset143, extract18, sequence36), not unittest-only discovery. The original suite retains its baseline warnings: two Keras NumPy-copy deprecations and one TFLite Interpreter deprecation; no dependency changes were made to conceal them. Its existing initialized synthetic TensorFlow export/parity fixture is not fitting or real dataset/candidate inference.

### Preservation, immutable handoff and remaining gates

All22 protected hashes match before/after, all102 previously retained historical artifact hashes still match, and every7 original before-fix2 snapshot bytes still match. The exact supplied partial report prefix (SHA-256 `519b82fd73bc4b765278f5708d7e7bddb53b7880edd402ccf0a0b6823f233698`) remains verbatim, including historical failed/interrupted work. Original tracked/index diffs are empty; branch/HEAD remain `holistic-migration` / `4d901693642af5f572455b2c75ba095b0ec65c7f`. No C source/report or review artifact was written by this worker.

Current webcam SHA-256 `f484a43d36dec7acd9d3cbdf30d231154fe8079aede571822c72e6991bd17e7c`; test SHA-256 `c077161772a1d08c16ad7028ef4cd126ae51ccda3c729a030f59ad318c899231`. Full frozen postimages, recovery-relative diffs, exact commands/logs/XML, original harness receipts, protection/history checks and source-version bindings are in `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-b-fix2-resume-20261113T192550-77535f667c5548a182636529233020e8`. Immutable external handoff entry: `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-b-fix2-resume-20261113T192550-77535f667c5548a182636529233020e8/handoff.json`; its returned SHA-256 binds this report postimage and all retained artifacts without a circular self-hash.

Remaining bounded gates: parent must match the exact delivered hashes and obtain independent affected webcam/test/report-appendix specification and quality re-review. Carry unchanged camera.py/test_camera.py and Swift coverage only by the exact protected hashes; prior whole-package CHANGES REQUIRED is not silently turned into approval. The separate C reviewer/acceptance is independent of these current regression results. No automatic third fix cycle is authorized if blocking findings remain. Human webcam/GUI tracking, anatomy/handedness, recognition/performance, training/model/data and phone/research/participant gates remain deferred or outside this repair. No camera/GUI/real model or dataset inference/fitting/install/commit/push/provider or configuration changes occurred.
