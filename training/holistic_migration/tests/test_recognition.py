"""Synthetic-only manual capture contract tests; no camera or real model."""
import importlib.util
import unittest
import numpy as np
from training.holistic_migration.features import RawFrame


def frame(t, pose=True, face=True, hand=True):
    p = np.zeros((33, 4)); p[:, 3] = 1; p[11, 0] = .3; p[12, 0] = .7
    return RawFrame(t, p if pose else None, np.zeros((21, 3)) if hand else None,
                    None, np.zeros((478, 3)) if face else None)


class CaptureTests(unittest.TestCase):
    def test_explicit_enable_and_one_submission_per_manual_attempt(self):
        self.assertIsNotNone(importlib.util.find_spec('training.holistic_migration.recognition'),
                             'manual capture implementation is missing')
        from training.holistic_migration.recognition import ManualCapture
        calls = []
        def model(x, training):
            self.assertFalse(training); self.assertEqual(x.shape, (1, 30, 1588))
            self.assertEqual(x.dtype, np.float32); calls.append(x)
            return np.full((1, 50), .02, np.float32)
        c = ManualCapture(model)
        for t in range(0, 1000, 67): c.observe(frame(t))
        c.space(1000); self.assertEqual(c.state, 'TRACKING'); self.assertEqual(calls, [])
        c.enable(); c.space(1001)
        for t in range(1005, 1700, 67): c.observe(frame(t))
        c.space(1701); self.assertEqual(len(calls), 1)
        self.assertEqual(c.result.shape, (50,)); self.assertEqual(c.frames, [])
        for t in range(1800, 2200, 67): c.observe(frame(t))
        self.assertEqual(len(calls), 1)
        c.space(2201); self.assertIsNone(c.result)
        for t in range(2210, 2900, 67): c.observe(frame(t))
        c.space(2901); self.assertEqual(len(calls), 2)

    def test_invalid_tracking_gap_timeout_cancel_prompt_never_splice(self):
        from training.holistic_migration.recognition import ManualCapture
        for bad, reason in [(frame(700, pose=False), 'invalid_pose'),
                            (frame(700, face=False), 'invalid_face'),
                            (frame(1000), 'observation_gap'), (frame(6000), 'too_long')]:
            with self.subTest(reason=reason):
                c = ManualCapture(lambda *a, **k: self.fail('invalid capture inferred'))
                c.enable(); c.space(0)
                for t in range(0, 650, 67): c.observe(frame(t))
                c.observe(bad)
                self.assertEqual(c.state, reason); self.assertEqual(c.frames, [])
        c = ManualCapture(None); c.enable(); c.space(0); c.observe(frame(0))
        c.cancel(); self.assertEqual(c.state, 'READY'); self.assertEqual(c.frames, [])
        c.space(0); c.observe(frame(0)); c.next_prompt(1)
        self.assertEqual(c.prompt, 1); self.assertEqual(c.frames, [])
        c.next_prompt(-1); self.assertEqual(c.prompt, 0)
        c.next_prompt(-1); self.assertEqual(c.prompt, 49)
        c.space(0); c.observe(frame(0)); c.space(100)
        self.assertEqual(c.state, 'too_few_observations')
        c.space(200); c.expire(5201); self.assertEqual(c.state, 'too_long')

    def test_finish_after_observation_gap_cancels_without_inference(self):
        from training.holistic_migration.recognition import ManualCapture
        c = ManualCapture(lambda *a, **k: self.fail('stale finish inferred'))
        c.enable(); c.space(0)
        for t in range(0, 700, 67): c.observe(frame(t))
        c.space(1000)
        self.assertEqual(c.state, 'observation_gap'); self.assertEqual(c.frames, [])

    def test_result_has_separate_finite_timings(self):
        from training.holistic_migration.recognition import ManualCapture
        c = ManualCapture(lambda *a, **k: np.full((1,50), .02))
        c.enable(); c.space(0)
        for t in range(0, 700, 67): c.observe(frame(t))
        c.space(710)
        self.assertTrue(hasattr(c, 'inference_ms'), 'inference timing missing')
        self.assertGreaterEqual(c.inference_ms, 0)
        self.assertGreaterEqual(c.decision_ms, c.inference_ms)
        self.assertEqual(c.collection_ms, 710)

    def test_invalid_probabilities_fail_closed(self):
        from training.holistic_migration.recognition import ManualCapture
        for value in [np.zeros((1, 49)), np.full((1, 50), np.nan),
                      np.full((1, 50), -.02), np.full((1, 50), .04)]:
            with self.subTest(shape=value.shape):
                c = ManualCapture(lambda *a, **k: value); c.enable(); c.space(0)
                for t in range(0, 700, 67): c.observe(frame(t))
                with self.assertRaises(ValueError): c.space(701)
                self.assertIsNone(c.result); self.assertEqual(c.frames, [])


if __name__ == '__main__': unittest.main()


class RaisedTests(unittest.TestCase):
    def test_three_raise_frames_then_exactly_thirty_observations(self):
        from training.holistic_migration import recognition as r
        self.assertTrue(hasattr(r, 'RaisedCapture'), 'automatic capture missing')
        calls = []
        def model(x, training):
            self.assertFalse(training)
            self.assertEqual(x.shape, (1,30,1588)); self.assertEqual(x.dtype, np.float32)
            self.assertTrue(np.isfinite(x).all()); calls.append(x.copy())
            return np.full((1,50), .02)
        c = r.RaisedCapture(model)
        for i in range(2): c.observe(raised(i*67))
        self.assertEqual(c.state, 'WAITING_FOR_HAND'); self.assertEqual(c.frames, [])
        c.observe(raised(134)); self.assertEqual(c.state, 'CAPTURING')
        self.assertEqual(len(c.frames), 1)
        for i in range(3,31): c.observe(raised(i*67))
        self.assertEqual(calls, []); self.assertEqual(len(c.frames), 29)
        c.observe(raised(31*67)); self.assertEqual(len(calls), 1)
        self.assertEqual(c.state, 'RESULT'); self.assertEqual(c.frames, [])
        from training.holistic_migration.face_features import prepare_capture
        np.testing.assert_array_equal(calls[0][0], prepare_capture([raised(i*67) for i in range(2,32)]).tensor)
        for i in range(32,65): c.observe(raised(i*67))
        self.assertEqual(len(calls), 1)


def raised(t, y=-.1, right=False, both=False):
    f = frame(t)
    f.left_hand[0,1] = y
    if both: return RawFrame(t, f.pose, f.left_hand, f.left_hand.copy(), f.face)
    return RawFrame(t, f.pose, None if right else f.left_hand,
                    f.left_hand if right else None, f.face)


class RaisedResetTests(unittest.TestCase):
    def test_tracking_faults_and_regression_clear_without_inference(self):
        from training.holistic_migration.recognition import RaisedCapture
        from dataclasses import replace
        for bad in [frame(201, pose=False), frame(201, face=False), frame(201, hand=False),
                    raised(500), raised(100), replace(raised(201), timestamp_ms=float('nan')),
                    replace(raised(201), face=np.full((478,3),np.nan))]:
            c=RaisedCapture(lambda *a,**k: self.fail('fault inferred'))
            for i in range(3): c.observe(raised(i*67))
            c.observe(bad)
            self.assertEqual(c.state,'WAITING_FOR_HAND'); self.assertEqual(c.frames, [])
            self.assertIsNone(c.result); self.assertEqual(c.raised_count,0)

    def test_lowering_rearms_but_missing_hands_do_not(self):
        from training.holistic_migration.recognition import RaisedCapture
        c=RaisedCapture(lambda *a,**k:np.full((1,50),.02))
        for i in range(32): c.observe(raised(i*67, right=True))
        self.assertEqual(c.submissions,1)
        for i in range(32,35): c.observe(frame(i*67,hand=False))
        for i in range(35,70): c.observe(raised(i*67))
        self.assertEqual(c.submissions,1)
        for i in range(70,73): c.observe(raised(i*67,y=.1))
        for i in range(73,75): c.observe(raised(i*67,both=True))
        c.observe(raised(75*67,both=True))
        self.assertEqual(c.state,'CAPTURING'); self.assertIsNone(c.result)
        self.assertEqual(len(c.frames),1)

    def test_threshold_flicker_and_gap_restart_debounce(self):
        from training.holistic_migration.recognition import RaisedCapture
        c=RaisedCapture(None)
        for i,y in enumerate([-.02,-.021,-.021,.1,-.021,-.021]): c.observe(raised(i*67,y=y))
        self.assertEqual(c.state,'WAITING_FOR_HAND')
        c.observe(raised(900)); self.assertEqual(c.raised_count,0)
        for i in range(3): c.observe(raised(967+i*67))
        self.assertEqual(c.state,'CAPTURING')
        c.cancel(); self.assertEqual(c.state,'WAITING_FOR_HAND')
        self.assertEqual(c.frames,[])


class PresentationTests(unittest.TestCase):
    def test_exact_top3_original_scores_stable_ties_decimal_text(self):
        from training.holistic_migration import recognition as r
        self.assertTrue(hasattr(r,'presentation_rows'),'top3 presentation missing')
        labels=[str(i) for i in range(50)]; p=np.zeros(50)
        p[9]=.50; p[2]=.25; p[4]=.25
        rows=r.presentation_rows(p,labels)
        self.assertEqual([a['index'] for a in rows],[9,2,4])
        self.assertEqual([a['score'] for a in rows],[.5,.25,.25])
        self.assertEqual([a['display_text'] for a in rows],['1. 9: 0.50','2. 2: 0.25','3. 4: 0.25'])


class SeamTests(unittest.TestCase):
    def test_controller_calls_shared_parity_seam(self):
        from unittest.mock import patch
        from training.holistic_migration import recognition as r
        from training.holistic_migration.verify_recognition import prepare_tensor
        with patch.object(r,'prepare_tensor', wraps=prepare_tensor,create=True) as prepare:
            c=r.RaisedCapture(lambda *a,**k:np.full((1,50),.02))
            for i in range(32): c.observe(raised(i*67))
            self.assertEqual(prepare.call_count,1)


class LoweringBoundaryTests(unittest.TestCase):
    def test_deadband_is_not_confirmed_lowering(self):
        from training.holistic_migration.recognition import RaisedCapture
        c=RaisedCapture(lambda *a,**k:np.full((1,50),.02))
        for i in range(32): c.observe(raised(i*67))
        for i in range(32,35): c.observe(raised(i*67,y=-.01))
        for i in range(35,70): c.observe(raised(i*67))
        self.assertEqual(c.submissions,1)


class RaisedCoverageTests(unittest.TestCase):
    def test_admitted_fifteen_hz_only_and_one_hand_variants(self):
        from training.holistic_migration.recognition import RaisedCapture
        from training.holistic_migration.sequence import ObservationClock
        for side in [dict(),dict(right=True),dict(both=True)]:
            c=RaisedCapture(lambda *a,**k:np.full((1,50),.02)); clock=ObservationClock()
            admitted=[]
            for t in range(0,2300,10):
                if clock.admit(t):
                    admitted.append(t); c.observe(raised(t,**side))
            self.assertEqual(c.submissions,1)
            self.assertEqual(c.collection_ms,admitted[31]-admitted[2])
            self.assertGreaterEqual(c.collection_ms,1900)

    def test_bad_model_and_prompt_cancel_fail_closed(self):
        from training.holistic_migration.recognition import RaisedCapture
        for value in [np.zeros((1,49)),np.full((1,50),np.nan),np.full((1,50),-.1),np.full((1,50),.04)]:
            c=RaisedCapture(lambda *a,**k:value)
            with self.assertRaises(ValueError):
                for i in range(32): c.observe(raised(i*67))
            self.assertIsNone(c.result); self.assertEqual(c.frames,[])
            self.assertEqual(c.state,'WAITING_FOR_HAND')
        c=RaisedCapture(None)
        for i in range(5): c.observe(raised(i*67))
        c.next_prompt(-1); self.assertEqual(c.prompt,49)
        self.assertEqual(c.frames,[]); self.assertEqual(c.raised_count,0)


class ResultLifetimeTests(unittest.TestCase):
    def test_held_result_is_not_a_five_second_timer_and_cancel_clears_rows(self):
        from training.holistic_migration.recognition import RaisedCapture
        c=RaisedCapture(lambda *a,**k:np.full((1,50),.02))
        for i in range(32): c.observe(raised(i*67))
        for i in range(32,100):
            c.expire(i*67); c.observe(raised(i*67))
        self.assertEqual(c.state,'RESULT'); self.assertEqual(c.submissions,1)
        c.presentation=[{'display_text':'old'}]
        c.cancel(); self.assertEqual(c.presentation,[])


class RepeatDebounceTests(unittest.TestCase):
    def test_every_rearmed_attempt_requires_three_new_raise_observations(self):
        from training.holistic_migration.recognition import RaisedCapture
        c=RaisedCapture(lambda *a,**k:np.full((1,50),.02))
        for i in range(32): c.observe(raised(i*67))
        for i in range(32,35): c.observe(raised(i*67,y=.1))
        for i in range(35,37): c.observe(raised(i*67))
        self.assertEqual(c.state,'RESULT'); self.assertEqual(c.frames,[])
        c.observe(raised(37*67))
        self.assertEqual(c.state,'CAPTURING'); self.assertEqual(len(c.frames),1)
        self.assertIsNone(c.result)


def hand_free(t, **kwargs):
    return frame(t, hand=False, **kwargs)


def scored(x, training):
    return np.full((1,50), .02)


class PresenceCaptureTests(unittest.TestCase):
    """Owner-approved reference behavior. Out of view means five consecutive valid hand-free
    observations (~0.33 s at 15 Hz). Hands out of view arm; a hand entering view starts an
    attempt; hands out of view again score it once."""

    def test_hands_out_of_view_never_call_model(self):
        from training.holistic_migration.recognition import PresenceCapture
        c=PresenceCapture(lambda *a,**k: self.fail('idle inferred'))
        for i in range(60): c.observe(hand_free(i*67))
        self.assertEqual((c.state,c.attempts,c.submissions),('WAITING_FOR_HAND',0,0))

    def test_hand_entering_view_starts_capture(self):
        from training.holistic_migration.recognition import PresenceCapture
        c=PresenceCapture(None)
        for i in range(5): c.observe(hand_free(i*67))
        c.observe(frame(5*67))
        self.assertEqual((c.state,c.attempts,len(c.frames)),('CAPTURING',1,1))

    def test_arming_needs_five_hand_free_observations(self):
        from training.holistic_migration.recognition import PresenceCapture
        c=PresenceCapture(None)
        for i in range(4): c.observe(hand_free(i*67))
        c.observe(frame(4*67))  # back in view after four hand-free observations: not armed
        self.assertEqual((c.state,c.attempts,c.armed),('WAITING_FOR_HAND',0,False))
        for i in range(5,10): c.observe(hand_free(i*67))
        c.observe(frame(10*67))
        self.assertEqual((c.state,c.attempts),('CAPTURING',1))

    def test_hands_visible_at_launch_must_leave_view_first(self):
        from training.holistic_migration.recognition import PresenceCapture
        c=PresenceCapture(None)
        for i in range(10): c.observe(frame(i*67))
        self.assertEqual((c.state,c.attempts,c.armed),('WAITING_FOR_HAND',0,False))
        for i in range(10,15): c.observe(hand_free(i*67))
        c.observe(frame(15*67))
        self.assertEqual(c.state,'CAPTURING')

    def test_five_hand_free_observations_score_once_with_training_tensor(self):
        from unittest.mock import patch
        from training.holistic_migration import recognition as r
        from training.holistic_migration.face_features import prepare_capture
        calls=[]
        def model(x, training):
            self.assertFalse(training); self.assertEqual(x.shape,(1,30,1588))
            calls.append(x.copy()); return np.full((1,50),.02)
        stream=([hand_free(i*67) for i in range(5)]+[frame(i*67) for i in range(5,15)]
                +[hand_free(i*67) for i in range(15,20)])
        with patch.object(r,'prepare_tensor',wraps=r.prepare_tensor) as seam:
            c=r.PresenceCapture(model)
            for f in stream[:-1]: c.observe(f)
            self.assertEqual(calls,[])  # four hand-free observations do not end the attempt
            c.observe(stream[-1])
        self.assertEqual((len(calls),seam.call_count,c.state),(1,1,'RESULT'))
        # Same hand-bounded trimming a whole training clip receives.
        np.testing.assert_array_equal(calls[0][0],prepare_capture(stream).tensor)
        for i in range(20,44): c.observe(hand_free(i*67))
        self.assertEqual((len(calls),c.state),(1,'RESULT'))

    def test_next_attempt_needs_no_click_after_hands_leave(self):
        from training.holistic_migration.recognition import PresenceCapture
        c=PresenceCapture(scored)
        for i in range(5): c.observe(hand_free(i*67))
        for i in range(5,15): c.observe(frame(i*67))
        for i in range(15,20): c.observe(hand_free(i*67))
        self.assertEqual(c.state,'RESULT')
        c.observe(frame(20*67))  # immediate re-entry: same sign or another one
        self.assertEqual((c.state,c.attempts),('CAPTURING',2)); self.assertIsNone(c.result)
        for i in range(21,31): c.observe(frame(i*67))
        for i in range(31,36): c.observe(hand_free(i*67))
        self.assertEqual((c.state,c.submissions),('RESULT',2))

    def test_short_hand_dropout_does_not_end_attempt(self):
        from training.holistic_migration.recognition import PresenceCapture
        from training.holistic_migration.face_features import prepare_capture
        calls=[]
        c=PresenceCapture(lambda x,training: calls.append(x.copy()) or np.full((1,50),.02))
        stream=([hand_free(i*67) for i in range(5)]+[frame(i*67) for i in range(5,11)]
                +[hand_free(i*67) for i in range(11,15)]+[frame(i*67) for i in range(15,21)]
                +[hand_free(i*67) for i in range(21,26)])
        for f in stream[:-1]: c.observe(f)
        self.assertEqual((c.state,calls),('CAPTURING',[]))  # the dropout did not count toward the end
        c.observe(stream[-1])
        self.assertEqual(len(calls),1)
        np.testing.assert_array_equal(calls[0][0],prepare_capture(stream).tensor)

    def test_quick_flick_is_not_scored_and_reason_is_kept(self):
        from training.holistic_migration.recognition import PresenceCapture
        c=PresenceCapture(lambda *a,**k: self.fail('flick inferred'))
        for i in range(5): c.observe(hand_free(i*67))
        c.observe(frame(5*67)); c.observe(frame(6*67))
        for i in range(7,12): c.observe(hand_free(i*67))
        self.assertEqual((c.state,c.attempts,c.submissions),('WAITING_FOR_HAND',1,0))
        self.assertIn('too_few_observations',c.reason)
        for i in range(12,14): c.observe(hand_free(i*67))  # still armed: hands already out of view
        c.observe(frame(14*67))
        self.assertEqual((c.state,c.attempts),('CAPTURING',2)); self.assertIsNone(c.reason)

    def test_tracking_loss_and_stream_faults_cancel_and_latch(self):
        from dataclasses import replace
        from training.holistic_migration.recognition import PresenceCapture
        cases=[('pose lost',[],frame(1005,pose=False)), ('face lost',[],frame(1005,face=False)),
               ('face lost during hand-out',[hand_free(1005),hand_free(1072)],hand_free(1139,face=False)),
               ('gap',[],frame(1300)), ('stale timestamp',[],frame(938)),
               ('nonfinite',[],replace(frame(1005),face=np.full((478,3),np.nan)))]
        for name,before,bad in cases:
            with self.subTest(name):
                c=PresenceCapture(lambda *a,**k: self.fail('fault inferred'))
                for i in range(5): c.observe(hand_free(i*67))
                for i in range(5,15): c.observe(frame(i*67))
                for f in before: c.observe(f)
                c.observe(bad)
                self.assertEqual((c.state,c.frames,c.result),('WAITING_FOR_HAND',[],None))
                self.assertIsNotNone(c.reason)
                t=c.last_timestamp
                c.observe(frame(t+67)); self.assertEqual(c.state,'WAITING_FOR_HAND')  # hands still in view
                for k in range(2,6): c.observe(hand_free(t+k*67))
                c.observe(frame(t+6*67)); self.assertEqual(c.state,'WAITING_FOR_HAND')  # four is not out of view
                for k in range(7,12): c.observe(hand_free(t+k*67))
                c.observe(frame(t+12*67)); self.assertEqual(c.state,'CAPTURING')

    def test_partial_sign_after_cancel_is_not_scored(self):
        """Reviewer probe P2: one detector dropout mid-sign is not hands out of view."""
        from training.holistic_migration.recognition import PresenceCapture
        c=PresenceCapture(lambda *a,**k: self.fail('partial sign inferred'))
        for i in range(5): c.observe(hand_free(i*67))
        for i in range(5,10): c.observe(frame(i*67))
        c.observe(frame(10*67,face=False))  # face lost mid-sign: attempt cancelled
        c.observe(hand_free(11*67))         # one-observation dropout, hands still signing
        for i in range(12,21): c.observe(frame(i*67))
        for i in range(21,26): c.observe(hand_free(i*67))
        self.assertEqual((c.state,c.attempts,c.submissions),('WAITING_FOR_HAND',1,0))

    def test_idle_tracking_fault_requires_hands_out_again(self):
        """Reviewer probe P6: hands can move unseen during a stall or tracking loss."""
        from training.holistic_migration.recognition import PresenceCapture
        for name,fault in (('stall',hand_free(2000)),('face lost',hand_free(335,face=False))):
            with self.subTest(name):
                c=PresenceCapture(None)
                for i in range(5): c.observe(hand_free(i*67))
                self.assertTrue(c.armed)
                c.observe(fault); t=fault.timestamp_ms
                for k in range(1,5): c.observe(hand_free(t+k*67))  # the hands-out count restarts
                c.observe(frame(t+5*67))
                self.assertEqual((c.state,c.attempts),('WAITING_FOR_HAND',0))
                for k in range(6,11): c.observe(hand_free(t+k*67))
                c.observe(frame(t+11*67))
                self.assertEqual((c.state,c.attempts),('CAPTURING',1))

    def test_capture_over_five_seconds_is_cancelled(self):
        from training.holistic_migration.recognition import PresenceCapture
        c=PresenceCapture(lambda *a,**k: self.fail('overlong inferred'))
        for i in range(5): c.observe(hand_free(i*67))
        for i in range(5,85): c.observe(frame(i*67))
        self.assertEqual((c.state,c.attempts,c.frames),('WAITING_FOR_HAND',1,[]))
        self.assertIn('too_long',c.reason)

    def test_five_second_limit_counts_hands_in_view_only(self):
        from training.holistic_migration.recognition import PresenceCapture
        c=PresenceCapture(scored)
        for i in range(5): c.observe(hand_free(i*67))
        for i in range(5,80): c.observe(frame(i*67))       # 4958 ms hand interval
        for i in range(80,85): c.observe(hand_free(i*67))  # hand-out tail ends past 5 s
        self.assertEqual((c.state,c.submissions),('RESULT',1))

    def test_observation_gap_boundary_is_250_ms(self):
        from training.holistic_migration.recognition import PresenceCapture
        c=PresenceCapture(None)
        for i in range(5): c.observe(hand_free(i*67))
        c.observe(frame(335)); c.observe(frame(585))
        self.assertEqual(c.state,'CAPTURING')
        c.observe(frame(836))
        self.assertEqual((c.state,c.reason),('WAITING_FOR_HAND','observation_gap'))

    def test_space_is_optional_manual_end(self):
        from training.holistic_migration.recognition import PresenceCapture
        c=PresenceCapture(scored)
        c.space(0); self.assertEqual((c.state,c.submissions),('WAITING_FOR_HAND',0))
        for i in range(5): c.observe(hand_free(i*67))
        for i in range(5,15): c.observe(frame(i*67))
        c.space(14*67)
        self.assertEqual((c.state,c.submissions),('RESULT',1))
        for i in range(15,20): c.observe(frame(i*67))  # hands still up: no new attempt
        self.assertEqual((c.state,c.attempts),('RESULT',1))
        c.observe(hand_free(20*67)); c.observe(frame(21*67))  # reviewer probe P1: one dropout
        self.assertEqual((c.state,c.attempts),('RESULT',1))
        for i in range(22,27): c.observe(hand_free(i*67))
        c.observe(frame(27*67))
        self.assertEqual((c.state,c.attempts),('CAPTURING',2))

    def test_reset_clears_result_and_waits_for_hands_out(self):
        from training.holistic_migration.recognition import PresenceCapture
        c=PresenceCapture(scored)
        for i in range(5): c.observe(hand_free(i*67))
        for i in range(5,15): c.observe(frame(i*67))
        for i in range(15,20): c.observe(hand_free(i*67))
        c.presentation=[{'display_text':'old'}]
        c.cancel()  # viewer R key
        self.assertEqual((c.state,c.result,c.presentation,c.reason),('WAITING_FOR_HAND',None,[],None))
        c.observe(hand_free(20*67)); c.observe(frame(21*67))  # reviewer probe P3: one dropout
        self.assertEqual(c.state,'WAITING_FOR_HAND')
        for i in range(22,27): c.observe(hand_free(i*67))
        c.observe(frame(27*67))
        self.assertEqual(c.state,'CAPTURING')

    def test_result_survives_idle_tracking_loss_and_stalls(self):
        from training.holistic_migration.recognition import PresenceCapture
        c=PresenceCapture(scored)
        for i in range(5): c.observe(hand_free(i*67))
        for i in range(5,15): c.observe(frame(i*67))
        for i in range(15,20): c.observe(hand_free(i*67))
        c.expire(60_000); c.observe(hand_free(20*67,face=False))
        self.assertEqual(c.state,'RESULT'); self.assertIsNotNone(c.result)

    def test_stalled_stream_cancels_active_capture(self):
        from training.holistic_migration.recognition import PresenceCapture
        c=PresenceCapture(lambda *a,**k: self.fail('stall inferred'))
        for i in range(5): c.observe(hand_free(i*67))
        c.observe(frame(335))
        c.expire(335+250); self.assertEqual(c.state,'CAPTURING')
        c.expire(335+251)
        self.assertEqual((c.state,c.reason),('WAITING_FOR_HAND','observation_gap'))
