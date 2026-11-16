"""Default tests do not open hardware, windows or MediaPipe."""
import contextlib
import io
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from training.holistic_migration import camera, webcam


class AdmissionTests(unittest.TestCase):
    def test_invalid_duration_precedes_paths_and_runtime(self):
        for duration in ("nan", "inf", "-inf", "0", "-1", "301"):
            with self.subTest(duration=duration), patch.object(Path, "is_file", side_effect=AssertionError("path accessed")):
                with contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit) as error:
                    webcam.main(["--duration", duration, "--model", "/absent.task",
                                 "--build-dir", "/absent-build"])
                self.assertEqual(error.exception.code, 2)

    def test_paths_and_report_overwrite_rejected_before_build(self):
        root = Path.home()/".hermes/cache/scratch"
        with tempfile.TemporaryDirectory(dir=root, prefix="task-b-options-") as folder:
            directory = Path(folder)
            model = directory/"official.task"; model.write_bytes(b"fixture")
            report = directory/"run.json"; report.write_text("preserve")
            for changes in (dict(model=Path("relative.task")), dict(model=directory/"missing.task"),
                            dict(build_dir=Path("relative")), dict(build_dir=Path(webcam.__file__).parent),
                            dict(report=report), dict(report=directory/"missing"/"run.json")):
                args = dict(model=model, build_dir=directory/"build", duration=60., report=None)
                args.update(changes)
                with self.subTest(changes=changes), self.assertRaises(ValueError):
                    webcam.validate_options(webcam.Options(**args))
            options = webcam.validate_options(webcam.Options(model, directory/"build", 60., None))
            self.assertEqual(options.duration, 60)
            self.assertEqual(report.read_text(), "preserve")


class PixelsAndOverlayTests(unittest.TestCase):
    def test_actual_bgra_conversion_resize_and_no_input_mirror(self):
        import cv2
        import numpy as np
        meta = dict(width=2, height=1, frame_bytes=8)
        rgb = webcam.prepare_rgb(bytes([0,0,255,255, 255,0,0,255]), meta, cv2)
        self.assertEqual(rgb.shape, (360,640,3))
        self.assertEqual(rgb.dtype, np.uint8)
        np.testing.assert_array_equal(rgb[100,0], [255,0,0])
        np.testing.assert_array_equal(rgb[100,-1], [0,0,255])
        with self.assertRaises(ValueError):
            webcam.prepare_rgb(b"short", meta, cv2)

    def test_missing_components_real_counts_masks_connections_and_readable_text(self):
        import cv2
        import numpy as np
        from training.holistic_migration.features import RawFrame, pack_frame
        class RecordingCV:
            def __init__(self): self.calls=[]
            def __getattr__(self, name): return getattr(cv2, name)
            def line(self, image, *args): self.calls.append("line"); return cv2.line(image, *args)
            def flip(self, image, code): self.calls.append("flip"); return cv2.flip(image, code)
            def putText(self, image, text, *args):
                self.calls.append(text); return cv2.putText(image, text, *args)
        rgb = np.zeros((360,640,3),np.uint8); rgb[:,0]=[255,0,0]
        original = rgb.copy()
        meta=dict(width=1280,height=720)
        missing=RawFrame(1,None,None,None)
        cv=RecordingCV()
        output=webcam.render(rgb,missing,pack_frame(missing),meta,
                             dict(elapsed=1.,fps=2.,detector_ms=3.,packing_ms=.1),True,cv)
        self.assertEqual(output.shape,(360,640,3))
        np.testing.assert_array_equal(rgb,original)
        self.assertNotIn("line",cv.calls)
        self.assertTrue(any("face=0" in text for text in cv.calls))
        self.assertTrue(any("masks L/R/P=0/0/0" in text for text in cv.calls))
        self.assertLess(cv.calls.index("flip"),next(i for i,t in enumerate(cv.calls) if "TRACKING ONLY" in t))
        self.assertTrue(any("1280x720" in t and "640x360" in t for t in cv.calls))
        pose=np.ones((33,4))*.5; pose[:,3]=1; pose[11,0]=.3;pose[12,0]=.7
        frame=RawFrame(2,pose,np.ones((21,3))*.5,None,np.ones((478,3))*.5)
        cv=RecordingCV()
        webcam.render(rgb,frame,pack_frame(frame),meta,
                      dict(elapsed=1.,fps=2.,detector_ms=3.,packing_ms=.1),False,cv)
        self.assertIn("line",cv.calls)
        self.assertTrue(any("face=478" in t and "SDK L=21 R=0" in t for t in cv.calls))
        self.assertTrue(any("masks L/R/P=1/0/1" in t for t in cv.calls))
        self.assertNotIn("flip",cv.calls)


class PreviewLoopTests(unittest.TestCase):
    def fixture(self, folder, *, keys=(ord('q'),), visible=True, failure=None,
                cleanup_failure=False, malformed=False, report=True):
        import cv2
        import numpy as np
        from types import SimpleNamespace
        from training.holistic_migration.features import RawFrame, pack_frame
        events=[]
        class Clock:
            value=0.
            def __call__(self): self.value+=.005; return self.value
        clock=Clock()
        class Capture:
            metadata=dict(protocol=1,width=2,height=1,frame_bytes=8,pixel_format="BGRA",
                          device_type=camera.BUILTIN_TYPE,continuity=malformed,device_sha256="a"*64)
            received=0;dropped=0;stderr_tail=b"";process=SimpleNamespace(returncode=-15)
            def next_frame(self, deadline):
                if failure == "capture": raise camera.CaptureError("source failed")
                self.received+=1
                return self.received,bytes([0,0,255,255,255,0,0,255])
            def raise_if_failed(self): pass
            def close(self):
                events.append("capture.close")
                if cleanup_failure: raise RuntimeError("cleanup failure")
        capture=Capture()
        class Detector:
            def detect(self,rgb,timestamp):
                events.append("detect")
                self_rgb=rgb.copy()
                np.testing.assert_array_equal(self_rgb[200,0],[255,0,0])
                if failure == "detector": raise RuntimeError("detector failure")
                return RawFrame(timestamp,None,None,None)
            def close(self): events.append("detector.close")
        class CV:
            def __getattr__(self,name): return getattr(cv2,name)
            def namedWindow(self,*args): events.append("window")
            def imshow(self,*args): events.append("show")
            def waitKey(self,*args): return next(self.keys,-1)
            def getWindowProperty(self,*args): return 1. if visible else 0.
            def destroyWindow(self,*args): events.append("window.close")
        cv=CV();cv.keys=iter(keys)
        source=Path(webcam.__file__).with_suffix(".swift")
        binding=SimpleNamespace(source_sha256="b"*64,binary_sha256="c"*64,
                                receipt=folder/"binding.json")
        def detector(model): events.append("detector");return Detector()
        def capture_factory(*args,**kwargs): events.append("capture");return capture
        runtime=SimpleNamespace(build=lambda path: binding,capture=capture_factory,
                                detector=detector,pack=pack_frame,cv=cv,clock=clock,
                                detector_version="synthetic-boundary",gui_version=cv2.__version__)
        model=folder/"official.task";model.write_bytes(b"synthetic model path only")
        options=webcam.Options(model,folder/"build",.3,folder/"operational.json" if report else None)
        return options,runtime,events

    def test_quit_escape_window_close_and_deadline_release_all(self):
        from training.holistic_migration import camera
        root=Path.home()/".hermes/cache/scratch"
        for keys,visible,terminal in [((ord('q'),),True,"quit"),((27,),True,"quit"),
                                      ((),False,"window_closed"),((),True,"deadline"),
                                      ((ord('m'),ord('q')),True,"quit")]:
            with self.subTest(terminal=terminal,keys=keys), tempfile.TemporaryDirectory(dir=root,prefix="task-b-loop-") as name:
                options,runtime,events=self.fixture(Path(name),keys=keys,visible=visible)
                summary=webcam.run_preview(options,runtime=runtime)
                self.assertEqual(summary["terminal"],terminal)
                self.assertFalse(summary["live_acceptance"])
                self.assertEqual(summary["counts"]["pose_frames"],0)
                self.assertGreater(summary["counts"]["processed"],0)
                self.assertEqual(summary["counts"]["mirror_toggles"],int(ord('m') in keys))
                self.assertEqual(events[-3:],["capture.close","detector.close","window.close"])
                self.assertLess(events.index("capture"),events.index("detector"))
                import json
                saved=json.loads(options.report.read_text())
                self.assertEqual(saved,summary)
                self.assertNotIn("landmarks",saved)
                self.assertNotIn("frames",saved)
                self.assertNotIn("specific failure",options.report.read_text())
                with self.assertRaises(ValueError): webcam.run_preview(options,runtime=runtime)

    def test_errors_cleanup_fault_and_handshake_admission_before_detector(self):
        root=Path.home()/".hermes/cache/scratch"
        for kwargs in (dict(failure="capture"),dict(failure="detector"),
                       dict(cleanup_failure=True),dict(malformed=True)):
            with self.subTest(kwargs=kwargs), tempfile.TemporaryDirectory(dir=root,prefix="task-b-loop-") as name:
                options,runtime,events=self.fixture(Path(name),**kwargs)
                with self.assertRaises((RuntimeError,ValueError)):
                    webcam.run_preview(options,runtime=runtime)
                self.assertIn("capture.close",events)
                if kwargs.get("malformed"):
                    self.assertNotIn("detector",events)
                else:
                    self.assertIn("detector.close",events);self.assertIn("window.close",events)
                import json
                summary=json.loads(options.report.read_text())
                self.assertIn(summary["terminal"],("error","cleanup_error"))
                self.assertFalse(summary["live_acceptance"])

    def test_additional_failure_stages_keep_disposition_and_teardown(self):
        import json
        root=Path.home()/".hermes/cache/scratch"
        for stage in ("build","detector_constructor","packing","window_create","display",
                      "detector_close","window_close","interrupt","no_frame"):
            with self.subTest(stage=stage),tempfile.TemporaryDirectory(dir=root,prefix="task-b-fault-") as name:
                options,runtime,events=self.fixture(Path(name))
                marker=RuntimeError("private failure sentinel")
                def fail(*a,**k): raise marker
                if stage=="build": runtime.build=fail
                elif stage=="detector_constructor": runtime.detector=fail
                elif stage=="packing": runtime.pack=fail
                elif stage=="window_create": runtime.cv.namedWindow=fail
                elif stage=="display": runtime.cv.imshow=fail
                elif stage=="window_close": runtime.cv.destroyWindow=fail
                elif stage=="detector_close":
                    original=runtime.detector
                    def detector(model):
                        instance=original(model);instance.close=fail;return instance
                    runtime.detector=detector
                elif stage in ("interrupt","no_frame"):
                    original=runtime.capture
                    def capture(*a,**k):
                        instance=original(*a,**k)
                        def next_frame(deadline):
                            if stage=="interrupt": raise KeyboardInterrupt()
                            raise TimeoutError()
                        instance.next_frame=next_frame;return instance
                    runtime.capture=capture
                if stage=="no_frame":
                    result=webcam.run_preview(options,runtime=runtime)
                    self.assertEqual(result["terminal"],"quit")
                    self.assertEqual(result["counts"]["processed"],0)
                else:
                    with self.assertRaises((RuntimeError,KeyboardInterrupt)):
                        webcam.run_preview(options,runtime=runtime)
                summary=json.loads(options.report.read_text())
                self.assertNotIn("private failure sentinel",options.report.read_text())
                self.assertFalse(summary["live_acceptance"])
                if stage!="build": self.assertIn("capture.close",events)
                if stage not in ("build","detector_constructor","detector_close"):
                    self.assertIn("detector.close",events)
                if stage in ("packing","display","detector_close","interrupt","no_frame","window_create"):
                    self.assertIn("window.close",events)

    def test_default_runtime_binds_actual_shared_detector_and_packer_without_loading_sdk(self):
        import builtins
        from training.holistic_migration.detector import HolisticDetector
        from training.holistic_migration.features import pack_frame
        original=builtins.__import__
        def guarded(name,*args,**kwargs):
            if name in ("mediapipe","tensorflow"):
                raise AssertionError("native dependency imported before detector admission")
            return original(name,*args,**kwargs)
        with patch("builtins.__import__",side_effect=guarded):
            runtime=webcam.load_runtime()
        self.assertIs(runtime.detector,HolisticDetector)
        self.assertIs(runtime.pack,pack_frame)
        self.assertIs(runtime.capture,camera.OwnedCapture)
        self.assertIs(runtime.build,camera.build_helper)

    def test_no_implicit_report_and_main_uses_same_runner(self):
        root=Path.home()/".hermes/cache/scratch"
        with tempfile.TemporaryDirectory(dir=root,prefix="task-b-loop-") as name:
            options,runtime,events=self.fixture(Path(name),report=False)
            with patch.object(webcam,"load_runtime",return_value=runtime):
                result=webcam.main(["--model",str(options.model),"--build-dir",str(options.build_dir),"--duration",".3"])
            self.assertEqual(result["terminal"],"quit")
            self.assertEqual(sorted(p.name for p in Path(name).iterdir()),["official.task"])


class SourceReconciliationTests(unittest.TestCase):
    """Run the real pipe reader/queue/close; only model and GUI are inert."""

    def preview_case(self, end, *, fault=True, primary=None, defer_reader=False):
        import json
        import os
        import subprocess
        import sys
        import threading
        import time
        from types import SimpleNamespace
        from training.holistic_migration.features import RawFrame

        child_code = """import os,sys,json,struct
os.write(1,json.dumps(json.loads(sys.argv[2])).encode()+b'\\n')
os.write(1,struct.pack('>dI',0.,8)+bytes([0,0,255,255,255,0,0,255]))
os.read(int(sys.argv[1]),1)
os.write(2,b'synthetic source diagnostic sentinel\\n')
sys.exit(7)
"""
        with tempfile.TemporaryDirectory(dir=camera.SCRATCH, prefix="task-b-reconcile-") as name:
            options, runtime, events = PreviewLoopTests().fixture(
                Path(name), keys=(27,) if end == "escape" else
                ((ord("q"),) if end == "quit" else ()), visible=end != "window_closed")
            gate_read, gate_write = os.pipe()
            captures, processes = [], []
            binding = SimpleNamespace(binary=Path(sys.executable), source_sha256="b"*64,
                                      binary_sha256="c"*64, receipt=Path(name)/"binding.json")
            metadata = dict(protocol=1,width=2,height=1,frame_bytes=8,pixel_format="BGRA",
                            device_type=camera.BUILTIN_TYPE,continuity=False,device_sha256="a"*64)
            runtime.build = lambda path: binding
            reader_blocked = threading.Event()
            original_frame = camera.PacketReader.frame

            def gated_frame(reader, deadline):
                if defer_reader and reader.last_timestamp is not None:
                    reader_blocked.set()
                    self.assertTrue(reader.read.__self__.stop.wait(2), "owned shutdown must release reader")
                return original_frame(reader, deadline)

            def spawn(command, **kwargs):
                process = subprocess.Popen([sys.executable,"-E","-B","-c",child_code,
                                            str(gate_read),json.dumps(metadata)],
                                           pass_fds=(gate_read,), **kwargs)
                processes.append(process)
                return process

            def capture_factory(binding, **kwargs):
                kwargs.update(startup_timeout=2.,frame_timeout=2.)
                with patch.object(camera,"verify_binding"):
                    capture = camera.OwnedCapture(binding,popen=spawn,**kwargs)
                captures.append(capture)
                until = time.monotonic()+2
                with capture.condition:
                    while capture.pending is None and capture.error is None and time.monotonic()<until:
                        capture.condition.wait(.02)
                self.assertIsNotNone(capture.pending, "fixture frame must be admitted before loop")
                self.assertIsNone(capture.error)
                if defer_reader:
                    self.assertTrue(reader_blocked.wait(2))
                return capture

            owner = self
            class Detector:
                def detect(self, rgb, timestamp):
                    capture = captures[0]
                    if fault:
                        os.write(gate_write,b"x")
                        owner.assertEqual(capture.process.wait(timeout=2),7)
                        if defer_reader:
                            owner.assertIsNone(capture.error, "exit must precede reader publication")
                        else:
                            until = time.monotonic()+2
                            with capture.condition:
                                while capture.error is None and time.monotonic()<until:
                                    capture.condition.wait(.02)
                            owner.assertIsInstance(capture.error,EOFError)
                    if end == "deadline":
                        runtime.clock.value = 10.
                    if primary is not None:
                        raise primary
                    return RawFrame(timestamp,None,None,None)
                def close(self): events.append("detector.close")

            runtime.capture = capture_factory
            runtime.detector = lambda model: Detector()
            error = None
            stderr = io.StringIO()
            try:
                with contextlib.redirect_stderr(stderr), patch.object(camera.PacketReader,"frame",gated_frame):
                    try:
                        summary = webcam.run_preview(options,runtime=runtime)
                    except BaseException as caught:
                        error = caught
                        summary = json.loads(options.report.read_text())
                capture = captures[0]
                self.assertIsNotNone(capture.process.poll())
                self.assertTrue(capture.process.stdout.closed)
                self.assertTrue(capture.process.stderr.closed)
                self.assertFalse(capture.reader_thread.is_alive())
                self.assertFalse(capture.stderr_thread.is_alive())
                self.assertIn("detector.close",events)
                self.assertIn("window.close",events)
                self.assertEqual(summary["counts"]["processed"],0 if primary else 1)
                self.assertFalse(summary["live_acceptance"])
                self.assertNotIn("sentinel",options.report.read_text())
                self.assertEqual(summary.get("source_failure"),fault)
                if fault:
                    self.assertEqual(summary["native_exit"],7)
                    self.assertIn("synthetic source diagnostic sentinel",stderr.getvalue())
                    if primary is not None:
                        self.assertIs(error,primary)
                    else:
                        self.assertIsInstance(error,camera.CaptureError)
                        self.assertIs(error.__cause__,capture.error)
                        self.assertIn("unexpected native exit" if defer_reader else
                                      "unexpected native pipe EOF",str(error))
                    self.assertEqual(summary["terminal"],"error")
                else:
                    self.assertIsNone(error)
                    self.assertIsNone(capture.error)
                    self.assertEqual(summary["terminal"],"deadline" if end == "deadline" else "quit")
                    self.assertEqual(summary["native_exit"],-15)
            finally:
                os.close(gate_read); os.close(gate_write)
                for process in processes:
                    if process.poll() is None:
                        process.kill(); process.wait(timeout=2)
                    for pipe in (process.stdout,process.stderr):
                        if not pipe.closed:
                            pipe.close()

    def test_observed_source_failure_then_quit(self):
        self.preview_case("quit")

    def test_observed_source_failure_then_escape(self):
        self.preview_case("escape")

    def test_observed_source_failure_then_window_close(self):
        self.preview_case("window_closed")

    def test_observed_source_failure_then_deadline(self):
        self.preview_case("deadline")

    def test_healthy_quit_deliberately_terminates_owned_child(self):
        self.preview_case("quit",fault=False)

    def test_healthy_deadline_deliberately_terminates_owned_child(self):
        self.preview_case("deadline",fault=False)

    def test_unexpected_child_exit_before_reader_publishes_error(self):
        self.preview_case("quit",defer_reader=True)


class FinalizationPrecedenceTests(unittest.TestCase):
    """Inject output faults through the real runner, never hardware or SDK."""

    def scenario(self, kind="source", *, report_faults=(), stderr_fault=False, report=True):
        from types import SimpleNamespace

        # The output streams alone are synthetic; run_preview owns finalization.
        with tempfile.TemporaryDirectory(dir=camera.SCRATCH, prefix="task-b-finalize-") as name:
            options, runtime, events = PreviewLoopTests().fixture(Path(name), report=report)
            cause = EOFError("private original cause sentinel")
            primary = (camera.CaptureError("private source sentinel") if kind == "source" else
                       RuntimeError("private detector sentinel") if kind == "detector" else
                       RuntimeError("private cleanup sentinel") if kind == "cleanup" else None)
            if primary is not None:
                primary.__cause__ = cause
            faults = {stage: OSError("private output sentinel " + stage) for stage in report_faults}
            stderr_error = OSError("private stderr sentinel") if stderr_fault else None
            for error in [*faults.values(), *([stderr_error] if stderr_error else [])]:
                error.__cause__ = RuntimeError("private secondary cause sentinel")
            secondary_causes = {id(error): error.__cause__ for error in
                                [*faults.values(), *([stderr_error] if stderr_error else [])]}
            calls = []

            class Report:
                payload = ""
                closed = False
                def write(self, text):
                    calls.append("report.write")
                    if "write" in faults:
                        self.payload = text[:20]  # Retain a partial failed artifact.
                        raise faults["write"]
                    self.payload = text
                def flush(self):
                    calls.append("report.flush")
                    if "flush" in faults: raise faults["flush"]
                def close(self):
                    calls.append("report.close")
                    if "close" in faults: raise faults["close"]
                    self.closed = True

            class Stderr(io.StringIO):
                def write(self, text):
                    calls.append("diagnostic.stderr")
                    if stderr_error is not None: raise stderr_error
                    return super().write(text)

            stream, stderr = Report(), Stderr()
            original_capture = runtime.capture
            def capture(*args, **kwargs):
                instance = original_capture(*args, **kwargs)
                instance.stderr_tail = b"private native diagnostic sentinel\n"
                if kind == "source":
                    def failed(*args, **kwargs):
                        calls.append("source.failure")
                        raise primary
                    instance.next_frame = instance.raise_if_failed = failed
                elif kind == "cleanup":
                    original_close = instance.close
                    def failed_close():
                        original_close()
                        calls.append("cleanup.failure")
                        assert primary is not None
                        raise primary
                    instance.close = failed_close
                return instance
            runtime.capture = capture
            if kind == "detector":
                original_detector = runtime.detector
                def detector(*args, **kwargs):
                    instance = original_detector(*args, **kwargs)
                    def failed(*args, **kwargs):
                        calls.append("detector.failure")
                        raise primary
                    instance.detect = failed
                    return instance
                runtime.detector = detector
            original_open, original_dumps = Path.open, webcam.json.dumps
            def open_report(path, *args, **kwargs):
                if path == options.report:
                    self.assertEqual(args, ("x",))
                    return stream
                return original_open(path, *args, **kwargs)
            def dumps(value, *args, **kwargs):
                calls.append("report.serialize")
                if "serialize" in faults: raise faults["serialize"]
                return original_dumps(value, *args, **kwargs)
            raised = result = None
            with contextlib.ExitStack() as stack:
                stack.enter_context(patch.object(Path, "open", open_report))
                stack.enter_context(patch.object(webcam.json, "dumps", dumps))
                stack.enter_context(contextlib.redirect_stderr(stderr))
                try:
                    result = webcam.run_preview(options, runtime=runtime)
                except BaseException as error:
                    raised = error
            self.assertTrue(all(event in events for event in
                                ("capture.close", "detector.close", "window.close")), events)
            if kind in ("source", "detector", "cleanup"):
                self.assertIn(kind + ".failure", calls, "primary injection must be reached")
            return SimpleNamespace(primary=primary, cause=cause, faults=faults,
                                   secondary_causes=secondary_causes,
                                   stderr_error=stderr_error, raised=raised, result=result,
                                   stream=stream, calls=calls, stderr=stderr.getvalue())

    def assert_primary(self, case):
        self.assertIs(case.raised, case.primary)
        self.assertIs(case.raised.__cause__, case.cause)
        self.assertIsNone(case.result)
        self.assertIn("report.close", case.calls)

    def assert_secondary(self, case, stage, error):
        diagnostics = getattr(case.raised, "finalization_errors", ())
        self.assertTrue(any(item[0] == stage and item[1] is error for item in diagnostics), diagnostics)
        self.assertIs(error.__cause__, case.secondary_causes[id(error)])
        self.assertTrue(any(stage in note and type(error).__name__ in note
                            for note in case.raised.__notes__))
        self.assertNotIn("sentinel", "\n".join(case.raised.__notes__))

    def test_source_primary_survives_report_serialization(self):
        case = self.scenario(report_faults=("serialize",))
        self.assert_primary(case)
        self.assert_secondary(case, "report.serialize", case.faults["serialize"])
        self.assertTrue(case.stream.closed)
        self.assertNotIn("report.write", case.calls)
        self.assertNotIn("report.flush", case.calls)
        self.assertEqual(case.stream.payload, "")

    def test_source_primary_survives_report_flush(self):
        case = self.scenario(report_faults=("flush",))
        self.assert_primary(case)
        self.assert_secondary(case, "report.flush", case.faults["flush"])
        self.assertTrue(case.stream.closed)
        self.assertLess(case.calls.index("report.flush"), case.calls.index("report.close"))
        self.assertNotIn("sentinel", case.stream.payload)

    def test_source_primary_survives_report_close(self):
        case = self.scenario(report_faults=("close",))
        self.assert_primary(case)
        self.assert_secondary(case, "report.close", case.faults["close"])
        self.assertFalse(case.stream.closed)
        self.assertEqual(case.calls.count("report.close"), 1)
        self.assertIn("report.flush", case.calls)
        self.assertNotIn("sentinel", case.stream.payload)

    def test_source_primary_survives_report_write(self):
        case = self.scenario(report_faults=("write",))
        self.assert_primary(case)
        self.assert_secondary(case, "report.write", case.faults["write"])
        self.assertTrue(case.stream.closed)
        self.assertNotIn("report.flush", case.calls)
        self.assertTrue(case.stream.payload)
        self.assertNotIn("sentinel", case.stream.payload)

    def test_source_primary_survives_diagnostic_stderr_and_closes_report(self):
        import json
        case = self.scenario(stderr_fault=True)
        self.assert_primary(case)
        self.assert_secondary(case, "diagnostic.stderr", case.stderr_error)
        self.assertTrue(case.stream.closed)
        self.assertLess(case.calls.index("diagnostic.stderr"), case.calls.index("report.close"))
        saved = json.loads(case.stream.payload)
        self.assertEqual(saved["terminal"], "error")
        self.assertTrue(saved["source_failure"])
        self.assertNotIn("sentinel", case.stream.payload)

    def test_prior_cleanup_failure_is_not_replaced_by_diagnostic_stderr(self):
        import json
        case = self.scenario("cleanup", stderr_fault=True)
        self.assert_primary(case)
        self.assert_secondary(case, "diagnostic.stderr", case.stderr_error)
        self.assertTrue(case.stream.closed)
        saved = json.loads(case.stream.payload)
        self.assertEqual(saved["terminal"], "cleanup_error")
        self.assertEqual(saved["counts"]["cleanup_errors"], 1)
        self.assertNotIn("sentinel", case.stream.payload)

    def test_diagnostic_stderr_siblings_and_later_report_faults(self):
        import json
        for kind in ("source", "detector", "healthy"):
            for stage in (None, "serialize", "write", "flush", "close"):
                with self.subTest(kind=kind, stage=stage):
                    faults = () if stage is None else (stage,)
                    case = self.scenario(kind, report_faults=faults, stderr_fault=True)
                    self.assertIsNone(case.result)
                    self.assertIn("report.close", case.calls)
                    self.assertEqual(case.stream.closed, stage != "close")
                    if kind == "healthy":
                        self.assertIs(case.raised, case.stderr_error)
                        self.assertIsInstance(case.raised.__cause__, RuntimeError)
                    else:
                        self.assert_primary(case)
                        self.assert_secondary(case, "diagnostic.stderr", case.stderr_error)
                    if stage is not None:
                        self.assert_secondary(case, "report." + stage, case.faults[stage])
                    if stage is None:
                        self.assertEqual(json.loads(case.stream.payload)["terminal"], "error")
                    self.assertNotIn("sentinel", case.stream.payload)

    def test_diagnostic_and_two_report_faults_retain_order(self):
        for kind in ("source", "detector", "healthy"):
            with self.subTest(kind=kind):
                case = self.scenario(kind, report_faults=("write", "close"), stderr_fault=True)
                expected = (("report.write", case.faults["write"]),
                            ("report.close", case.faults["close"]))
                if kind == "healthy":
                    self.assertIs(case.raised, case.stderr_error)
                else:
                    self.assert_primary(case)
                    expected = (("diagnostic.stderr", case.stderr_error),) + expected
                self.assertEqual(case.raised.finalization_errors, expected)
                self.assertFalse(case.stream.closed)
                self.assertEqual(case.calls.count("report.close"), 1)
                self.assertNotIn("report.flush", case.calls)
                self.assertNotIn("sentinel", case.stream.payload)

    def test_diagnostic_failure_without_report_preserves_precedence(self):
        for kind in ("source", "detector", "healthy"):
            with self.subTest(kind=kind):
                case = self.scenario(kind, stderr_fault=True, report=False)
                self.assertFalse(any(call.startswith("report.") for call in case.calls))
                self.assertIsNone(case.result)
                if kind == "healthy":
                    self.assertIs(case.raised, case.stderr_error)
                else:
                    self.assertIs(case.raised, case.primary)
                    self.assertIs(case.raised.__cause__, case.cause)
                    self.assert_secondary(case, "diagnostic.stderr", case.stderr_error)

    def test_detector_primary_survives_each_report_fault(self):
        for stage in ("serialize", "write", "flush", "close"):
            with self.subTest(stage=stage):
                case = self.scenario("detector", report_faults=(stage,))
                self.assert_primary(case)
                self.assert_secondary(case, "report." + stage, case.faults[stage])
                self.assertEqual(case.stream.closed, stage != "close")
                self.assertNotIn("sentinel", case.stream.payload)

    def test_first_report_fault_stays_primary(self):
        for stage in ("serialize", "write", "flush", "close"):
            with self.subTest(stage=stage):
                case = self.scenario("healthy", report_faults=(stage,))
                self.assertIs(case.raised, case.faults[stage])
                self.assertIsInstance(case.raised.__cause__, RuntimeError)
                self.assertIsNone(case.result)
                self.assertIn("report.close", case.calls)
                self.assertEqual(case.stream.closed, stage != "close")
                self.assertNotIn("sentinel", case.stream.payload)

    def test_first_report_fault_survives_later_close_fault(self):
        for stage in ("serialize", "write", "flush"):
            with self.subTest(stage=stage):
                case = self.scenario("healthy", report_faults=(stage, "close"))
                self.assertIs(case.raised, case.faults[stage])
                self.assertIsInstance(case.raised.__cause__, RuntimeError)
                self.assert_secondary(case, "report.close", case.faults["close"])
                self.assertIsNone(case.result)
                self.assertFalse(case.stream.closed)
                self.assertEqual(case.calls.count("report.close"), 1)
                self.assertNotIn("sentinel", case.stream.payload)

    def test_source_and_detector_retain_both_report_faults_in_order(self):
        for kind in ("source", "detector"):
            for stage in ("serialize", "write", "flush"):
                with self.subTest(kind=kind, stage=stage):
                    case = self.scenario(kind, report_faults=(stage, "close"))
                    self.assert_primary(case)
                    self.assertEqual(case.raised.finalization_errors,
                                     (("report." + stage, case.faults[stage]),
                                      ("report.close", case.faults["close"])))
                    self.assert_secondary(case, "report." + stage, case.faults[stage])
                    self.assert_secondary(case, "report.close", case.faults["close"])
                    self.assertFalse(case.stream.closed)
                    self.assertEqual(case.calls.count("report.close"), 1)
                    self.assertNotIn("sentinel", case.stream.payload)

    def test_healthy_report_and_primary_without_output_fault_controls(self):
        import json
        for kind in ("healthy", "source", "detector"):
            with self.subTest(kind=kind):
                case = self.scenario(kind)
                self.assertTrue(case.stream.closed)
                self.assertEqual([call for call in case.calls if call.startswith("report.")],
                                 ["report.serialize", "report.write", "report.flush", "report.close"])
                saved = json.loads(case.stream.payload)
                self.assertFalse(saved["live_acceptance"])
                self.assertNotIn("sentinel", case.stream.payload)
                if kind == "healthy":
                    self.assertIsNone(case.raised)
                    self.assertEqual(case.result, saved)
                    self.assertEqual(saved["terminal"], "quit")
                else:
                    self.assert_primary(case)
                    self.assertEqual(saved["terminal"], "error")
                    self.assertEqual(saved["source_failure"], kind == "source")
                    self.assertFalse(getattr(case.raised, "finalization_errors", ()))


if __name__ == "__main__":
    unittest.main()
