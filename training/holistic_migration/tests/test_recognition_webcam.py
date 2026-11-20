"""No hardware acquisition: injectable GUI/runtime and strict preflight."""
import importlib.util
import json
from pathlib import Path
from types import SimpleNamespace
import unittest
from unittest.mock import patch
import numpy as np
from training.holistic_migration.features import RawFrame
from .test_recognition import frame, raised


def new_audit(test):
    import os
    import tempfile
    parent=Path(os.environ.get('KUMPAS_TEST_AUDIT_ROOT',str(Path.home()/'.hermes/cache/scratch')))
    parent.mkdir(parents=True,exist_ok=True)
    temporary=tempfile.TemporaryDirectory(dir=parent)
    test.addCleanup(temporary.cleanup)
    return Path(temporary.name)/'run'


class ViewerTests(unittest.TestCase):
    def module(self):
        self.assertIsNotNone(importlib.util.find_spec('training.holistic_migration.recognition_webcam'),
                             'viewer CLI missing')
        from training.holistic_migration import recognition_webcam
        return recognition_webcam

    def test_preflight_before_runtime_and_fixed_assets(self):
        w = self.module()
        for duration in [0, -1, float('nan'), float('inf'), 901, True]:
            with self.subTest(duration=duration), self.assertRaises(ValueError):
                w.validate_options(w.Options(duration=duration, diagnostic_uncalibrated=True))
        with self.assertRaises(ValueError): w.validate_options(w.Options())
        labels, identities = w.verify_assets(w.Options(diagnostic_uncalibrated=True))
        self.assertEqual(len(labels), 50); self.assertEqual(labels[0], 'GOOD MORNING')
        self.assertEqual(len(identities), 5)
        with self.assertRaises((ValueError, FileNotFoundError)):
            w.verify_assets(w.Options(diagnostic_uncalibrated=True, classifier=Path('/missing')))

    def fake_runtime(self, w, keys, hand_at, model, rendered, events, stall=lambda ms: False):
        """Integer-millisecond 15 Hz clock; hand_at(n) scripts the n-th admitted observation;
        stall(ms) makes the camera deliver no frame at that time."""
        clock=[0]; seen=[0]
        class CV:
            WINDOW_NORMAL = 0; WND_PROP_VISIBLE = 0
            def namedWindow(self, *a): events.append('window')
            def resizeWindow(self, *a): pass
            def imshow(self, name, image): rendered.append(image)
            def waitKey(self, *a): clock[0] += 67; return keys.pop(0)
            def getWindowProperty(self, *a): return 1
            def destroyWindow(self, *a): events.append('destroy')
        class Capture:
            metadata = dict(protocol=1, device_type=w.camera.BUILTIN_TYPE, continuity=False,
                            device_sha256='a'*64, pixel_format='BGRA', width=1, height=1, frame_bytes=4)
            def next_frame(self, deadline):
                if stall(clock[0]): raise TimeoutError()
                return clock[0], b'\0'*4
            def raise_if_failed(self): pass
            def close(self): events.append('capture.close')
        class Detector:
            def detect(self, rgb, t):
                seen[0] += 1
                return frame(t, hand=hand_at(seen[0]))
            def close(self): events.append('detector.close')
        return SimpleNamespace(cv=CV(), clock=lambda: clock[0]/1000, build=lambda p: None,
                               capture=lambda *a, **k: Capture(), detector=lambda p: Detector(), model=model)

    def test_hand_in_then_out_saves_exactly_one_attempt_and_cleans_up(self):
        from training.holistic_migration.verify_recognition import check_run
        w = self.module(); events = []; shown = []
        def model(x, training):
            self.assertGreater(len(shown), 2); events.append('infer')
            return np.full((1,50), .02)
        rt = self.fake_runtime(w, [-1]*40 + [ord('q')], lambda n: 6 <= n <= 17, model, shown, events)
        audit = new_audit(self)
        with patch.object(w, 'prepare_rgb', return_value=np.zeros((360,640,3),np.uint8)), \
             patch.object(w, 'render_view', side_effect=lambda *a: (a[2].state, bool(a[2].presentation), a[3])):
            result = w.run_viewer(w.Options(diagnostic_uncalibrated=True, audit_dir=audit), runtime=rt)
        states = [state for state, _, _ in shown]
        self.assertEqual([s for i, s in enumerate(states) if i == 0 or states[i-1] != s],
                         ['WAITING_FOR_HAND', 'CAPTURING', 'RESULT'])
        # The result is saved before it is first drawn: RESULT frames always carry saved rows.
        self.assertTrue(all(rows for state, rows, _ in shown if state == 'RESULT'))
        # FPS counts admitted observations from the first one, not from camera startup.
        for _, _, fps in shown[1:]: self.assertAlmostEqual(fps, 1000/67, places=6)
        self.assertEqual(events.count('infer'), 1); self.assertEqual(check_run(audit), 1)
        self.assertEqual((result['attempts'], result['submissions'], result['terminal']), (1, 1, 'quit'))
        self.assertEqual(events[-3:], ['capture.close','detector.close','destroy'])
        self.assertNotIn('GOOD MORNING', json.dumps(result))
        self.assertNotIn('result', result); self.assertNotIn('frames', result)
        # Repeat the actual automatic path, but deny audit publication.
        controllers=[]; original=w.PresenceCapture
        def controller(model):
            value=original(model); controllers.append(value); return value
        rt = self.fake_runtime(w, [-1]*40 + [ord('q')], lambda n: 6 <= n <= 17, model, [], [])
        with patch.object(w,'PresenceCapture',side_effect=controller), \
             patch.object(w.AuditRun,'save',side_effect=OSError('audit denied')), \
             patch.object(w,'prepare_rgb',return_value=np.zeros((360,640,3),np.uint8)), \
             patch.object(w,'render_view',side_effect=lambda *a:a[2].state):
            with self.assertRaisesRegex(OSError,'audit denied'):
                w.run_viewer(w.Options(diagnostic_uncalibrated=True,audit_dir=new_audit(self)),runtime=rt)
        self.assertIsNone(controllers[0].result); self.assertEqual(controllers[0].frames,[])

    def test_camera_stall_cancels_attempt_before_space(self):
        """Reviewer probe V1: SPACE after a >250 ms stall must not score the stale attempt."""
        import os
        w = self.module(); calls = []
        keys = [-1]*20 + [ord(' ')] + [-1]*5 + [ord('q')]
        rt = self.fake_runtime(w, keys, lambda n: n > 5, lambda x, training: calls.append(1),
                               [], [], stall=lambda ms: 1005 <= ms <= 1340)
        audit = new_audit(self)
        with patch.object(w, 'prepare_rgb', return_value=np.zeros((360,640,3),np.uint8)), \
             patch.object(w, 'render_view', side_effect=lambda *a: a[2].state):
            result = w.run_viewer(w.Options(diagnostic_uncalibrated=True, audit_dir=audit), runtime=rt)
        self.assertEqual(calls, [])
        self.assertEqual((result['attempts'], result['submissions'], result['state']), (1, 0, 'WAITING_FOR_HAND'))
        self.assertEqual([n for n in os.listdir(audit) if n.startswith('attempt-')], [])

    def test_space_ends_attempt_and_r_m_q_controls(self):
        from training.holistic_migration.verify_recognition import check_run
        w = self.module(); rendered = []; calls = []
        keys = [-1]*12 + [ord(' ')] + [-1]*5 + [ord('r')] + [-1]*3 + [ord('m')] + [-1]*2 + [ord('q')]
        def model(x, training):
            calls.append(1); return np.full((1,50), .02)
        rt = self.fake_runtime(w, keys, lambda n: n > 5, model, rendered, [])
        audit = new_audit(self)
        with patch.object(w, 'prepare_rgb', return_value=np.zeros((360,640,3),np.uint8)), \
             patch.object(w, 'render_view', side_effect=lambda *a: (a[2].state, a[2].result is not None, a[4], bool(a[2].presentation))):
            result = w.run_viewer(w.Options(diagnostic_uncalibrated=True, audit_dir=audit), runtime=rt)
        states = [state for state, _, _, _ in rendered]
        self.assertEqual(check_run(audit), 1)  # the SPACE-ended attempt was saved
        self.assertTrue(all(rows for state, _, _, rows in rendered if state == 'RESULT'))
        self.assertEqual(len(calls), 1)  # SPACE scored once; hands held in view never start another attempt
        self.assertEqual((result['attempts'], result['submissions'], result['terminal']), (1, 1, 'quit'))
        self.assertNotIn('CAPTURING', states[states.index('RESULT'):])
        self.assertEqual(rendered[-1][:2], ('WAITING_FOR_HAND', False))  # R cleared the result
        self.assertEqual((rendered[0][2], rendered[-1][2]), (True, False))  # M toggled display mirror


    def test_source_failure_beats_quit_and_cleanup_fault_and_status_has_no_history(self):
        import tempfile
        w = self.module(); events = []; failed = [False]
        scratch = Path.home()/'.hermes/cache/scratch'
        with tempfile.TemporaryDirectory(dir=scratch) as directory:
            status_path = Path(directory)/'status.json'
            class Capture:
                metadata = dict(protocol=1,device_type=w.camera.BUILTIN_TYPE,continuity=False,
                                device_sha256='a'*64,pixel_format='BGRA',width=1,height=1,frame_bytes=4)
                def next_frame(self, deadline): raise TimeoutError()
                def raise_if_failed(self):
                    if failed[0]: raise w.camera.CaptureError('source failed')
                def close(self): events.append('capture.close'); raise RuntimeError('cleanup')
            class Detector:
                def close(self): events.append('detector.close')
            class CV:
                WINDOW_NORMAL=0; WND_PROP_VISIBLE=0
                def namedWindow(self,*a): pass
                def resizeWindow(self,*a): pass
                def waitKey(self,*a):
                    self_status=json.loads(status_path.read_text())
                    assert self_status['terminal']=='starting'
                    failed[0]=True; return ord('q')
                def destroyWindow(self,*a): events.append('destroy')
            runtime=SimpleNamespace(cv=CV(),clock=lambda:0.,model=None,build=lambda p:None,
                                    capture=lambda *a,**k:Capture(),detector=lambda p:Detector())
            with self.assertRaisesRegex(w.camera.CaptureError,'source failed'):
                w.run_viewer(w.Options(diagnostic_uncalibrated=True,status=status_path,audit_dir=new_audit(self)),runtime=runtime)
            result=json.loads(status_path.read_text())
            self.assertTrue(result['source_failure']); self.assertEqual(result['terminal'],'error')
            self.assertEqual(events,['capture.close','detector.close','destroy'])
            self.assertEqual(set(result), {'schema','mode','live_ready','terminal','state','processed',
                                          'submissions','attempts','identities','source_failure'})

    def test_real_renderer_is_bounded_without_camera(self):
        import cv2
        from training.holistic_migration.recognition import PresenceCapture, presentation_rows
        w=self.module(); labels,_=w.verify_assets(w.Options(diagnostic_uncalibrated=True))
        c=PresenceCapture(None); c.result=np.full(50,.02); c.presentation=presentation_rows(c.result,labels)
        image=w.render_view(np.zeros((360,640,3),np.uint8),frame(0),c,15.,True,cv2)
        self.assertEqual(image.shape,(720,1280,3)); self.assertEqual(image.dtype,np.uint8)


if __name__ == '__main__': unittest.main()


class Top3RendererTests(unittest.TestCase):
    def test_actual_puttext_exact_three_matches_saved_rows(self):
        import cv2
        from training.holistic_migration import recognition_webcam as w
        from training.holistic_migration.recognition import presentation_rows, PresenceCapture
        labels=[str(i) for i in range(50)]
        c=PresenceCapture(None); c.result=np.full(50,.02)
        c.presentation=presentation_rows(c.result,labels)
        text=[]
        with patch.object(cv2,'putText',side_effect=lambda image,s,*a: text.append(s) or image):
            w.render_view(np.zeros((360,640,3),np.uint8),raised(0),c,15.,True,cv2)
        actual=[s for s in text if s[:1] in '123' and '. ' in s]
        import tempfile
        from training.holistic_migration.verify_recognition import AuditRun
        with tempfile.TemporaryDirectory(dir=Path.home()/'.hermes/cache/scratch') as directory:
            audit=AuditRun(Path(directory)/'run',labels,dict(classifier='a'*64,features='b'*64,labels='c'*64))
            target=audit.save(c.result,c.presentation)
            saved=json.loads(target.read_text())['top3']
        self.assertEqual(actual,[row['display_text'] for row in saved])
        self.assertFalse(any('ALL 50' in s or 'Prompt-label score' in s for s in text))


class ReferenceLayoutTests(unittest.TestCase):
    """Reference-video layout: full camera frame, one status line, bottom-left state text."""
    def drawn(self, c, mirrored=True):
        import cv2
        from training.holistic_migration import recognition_webcam as w
        text=[]
        with patch.object(cv2,'putText',side_effect=lambda image,s,*a: text.append(s) or image):
            image=w.render_view(np.zeros((360,640,3),np.uint8),frame(0),c,15.,mirrored,cv2)
        self.assertEqual((image.shape,image.dtype),((720,1280,3),np.uint8))
        return text

    def test_status_line_and_uncalibrated_label(self):
        from training.holistic_migration.recognition import PresenceCapture
        text=self.drawn(PresenceCapture(None))
        self.assertIn('FPS 15.0  mirror ON  q quit  m mirror  r reset  space end',text)
        self.assertTrue(any('UNCALIBRATED' in s for s in text))
        self.assertIn('FPS 15.0  mirror OFF  q quit  m mirror  r reset  space end',
                      self.drawn(PresenceCapture(None),mirrored=False))

    def test_prompt_rec_timer_reason_and_result_rows(self):
        from training.holistic_migration.recognition import PresenceCapture, presentation_rows
        c=PresenceCapture(lambda *a,**k: np.full((1,50),.02))
        self.assertIn('Lower your hands; keep face and shoulders in view',self.drawn(c))
        for i in range(5): c.observe(frame(i*67,hand=False))
        self.assertIn('Raise your hands to sign',self.drawn(c))
        c.observe(frame(5*67)); c.observe(frame(6*67))
        for i in range(7,12): c.observe(frame(i*67,hand=False))
        self.assertTrue(any(s.startswith('Not scored') and 'too_few_observations' in s for s in self.drawn(c)))
        for i in range(12,22): c.observe(frame(i*67))
        self.assertIn('REC 0.6 s',self.drawn(c))  # (21-12)*67 ms of capture so far
        for i in range(22,27): c.observe(frame(i*67,hand=False))
        c.presentation=presentation_rows(c.result,[str(i) for i in range(50)])
        text=self.drawn(c)
        self.assertEqual([s for s in text if s[:3] in ('1. ','2. ','3. ')],
                         [row['display_text'] for row in c.presentation])
        self.assertFalse(any(s.startswith(('REC','Raise','Lower','Not scored')) for s in text))

    def test_landmarks_drawn_before_mirroring_and_hidden_pose_skipped(self):
        import cv2
        from training.holistic_migration import recognition_webcam as w
        from training.holistic_migration.recognition import PresenceCapture
        hand=np.zeros((21,3)); hand[:,0]=.1; hand[:,1]=np.linspace(.4,.6,21)
        for mirrored,(low,high) in ((False,(100,160)),(True,(1120,1180))):
            with self.subTest(mirrored=mirrored):
                image=w.render_view(np.zeros((360,640,3),np.uint8),RawFrame(0,None,hand,None,None),
                                    PresenceCapture(None),15.,mirrored,cv2)
                columns=np.flatnonzero(image[200:500].any(axis=(0,2)))
                self.assertTrue(low <= columns.min() and columns.max() <= high, (columns.min(), columns.max()))
        pose=np.zeros((33,4)); pose[:,0]=np.linspace(.3,.7,33); pose[:,1]=.5; pose[:,3]=.4
        image=w.render_view(np.zeros((360,640,3),np.uint8),RawFrame(0,pose,None,None,None),
                            PresenceCapture(None),15.,False,cv2)
        self.assertFalse(image[300:420].any())  # pose points below visibility .5 are not drawn
