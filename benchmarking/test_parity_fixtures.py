"""Public CLI coverage for a versioned external six-clip campaign (synthetic inputs)."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

import numpy as np

SCRIPT = Path(__file__).with_name('parity_fixtures.py')
TARGETS = [(22, 14), (22, 8), (22, 9), (24, 10), (24, 11), (24, 18)]


class CampaignTests(unittest.TestCase):
    def setup_inputs(self, root):
        repo = root / 'repo'
        data = root / 'kumpas-data'
        seq = data / 'sequences'
        protocol = seq / 'evaluation-v1'
        protocol.mkdir(parents=True)
        selection = repo / 'training/models/protocol_selection_evaluation_v1.json'
        selection.parent.mkdir(parents=True)
        (seq / 'label_map.json').write_text(json.dumps({'22': {'id': 22, 'label': 'THREE'},
                                                       '24': {'id': 24, 'label': 'FIVE'}}))
        rows = []
        for index, (cid, clip) in enumerate(TARGETS):
            video = data / f'clips_raw/clips/{cid}/{clip}.MOV'
            video.parent.mkdir(parents=True, exist_ok=True)
            video.write_bytes(b'synthetic-freeze-only-video')
            npz = data / f'landmarks/clips_{cid}_{clip}.npz'
            npz.parent.mkdir(parents=True, exist_ok=True)
            np.savez(npz, landmarks=np.zeros((32, 1662), np.float32), class_id=cid,
                     split='train', fps=10.0, brightness=1.0, detection_rates=np.zeros(4))
            rows.append({'index': index, 'clip': npz.name, 'class_id': cid, 'partition': 'validation'})
        manifest = protocol / 'manifest.json'
        manifest.write_text(json.dumps({'version': 'evaluation-v1', 'rows': rows}))
        selection.write_text(json.dumps({'protocol_sha256': hashlib.sha256(manifest.read_bytes()).hexdigest()}))
        return repo, data, manifest, selection

    def run_cli(self, repo, output, *extra):
        return subprocess.run([sys.executable, '-E', str(SCRIPT), '--repo', str(repo),
                               '--output', str(output), *extra], capture_output=True, text=True)

    def test_freeze_all_six_before_any_extraction_and_refuse_overwrite(self):
        with tempfile.TemporaryDirectory() as temp:
            repo, data, _, _ = self.setup_inputs(Path(temp))
            output = data / 'parity/new-campaign'
            result = self.run_cli(repo, output, '--freeze-only')
            self.assertEqual(result.returncode, 0, result.stderr)
            freeze = json.loads((output / 'selection.json').read_text())
            self.assertEqual(freeze['status'], 'frozen_before_extraction')
            self.assertEqual([row['clip_id'] for row in freeze['clips']],
                             [f'clips_{cid}_{clip}.npz' for cid, clip in TARGETS])
            self.assertFalse((output / 'manifest.json').exists())
            self.assertEqual(sorted(p.name for p in output.iterdir()), ['INCOMPLETE', 'selection.json'])
            self.assertNotEqual(self.run_cli(repo, output, '--freeze-only').returncode, 0)
            self.assertEqual(freeze, json.loads((output / 'selection.json').read_text()))

    def test_generate_six_real_synthetic_video_references_and_validate_publication(self):
        import cv2
        import importlib.util
        if importlib.util.find_spec('mediapipe') is None:
            self.skipTest('MediaPipe unavailable in this interpreter; real campaign exercised separately')
        import mediapipe
        if not hasattr(mediapipe, 'solutions'):
            self.skipTest("This interpreter's MediaPipe lacks Holistic solutions; training/.venv exercised separately")
        with tempfile.TemporaryDirectory() as temp:
            repo, data, _, _ = self.setup_inputs(Path(temp))
            for cid, clip in TARGETS:
                avi = data / f'clips_raw/clips/{cid}/{clip}.avi'
                writer = cv2.VideoWriter(str(avi), cv2.VideoWriter_fourcc(*'MJPG'), 10, (16, 16))
                self.assertTrue(writer.isOpened())
                for _ in range(32):
                    writer.write(np.zeros((16, 16, 3), np.uint8))
                writer.release()
                avi.replace(avi.with_suffix('.MOV'))
            output = data / 'parity/generated'
            result = self.run_cli(repo, output)
            self.assertEqual(result.returncode, 0, result.stderr)
            manifest = json.loads((output / 'manifest.json').read_text())
            self.assertEqual(manifest['status'], 'prepared_python_references_only')
            self.assertEqual(len(manifest['fixtures']), 6)
            self.assertFalse((output / 'INCOMPLETE').exists())
            for fixture in manifest['fixtures']:
                directory = output / fixture['directory']
                reference = json.loads((directory / 'python.json').read_text())
                self.assertEqual(len(reference['frames']), 30)
                self.assertEqual(reference['fixture_binding']['clip_id'], fixture['clip_id'])
                self.assertEqual(fixture['python_sha256'], hashlib.sha256((directory / 'python.json').read_bytes()).hexdigest())
                self.assertEqual(len(list((directory / 'frames').glob('*.png'))), 30)
                self.assertEqual(fixture['summary']['sampled_presence']['pose_seen'], 0)
                self.assertFalse('prediction_agreement' in fixture['summary'])

    def test_failed_generation_never_publishes_complete_manifest(self):
        with tempfile.TemporaryDirectory() as temp:
            repo, data, _, _ = self.setup_inputs(Path(temp))
            output = data / 'parity/failed'
            result = self.run_cli(repo, output)
            self.assertNotEqual(result.returncode, 0)
            self.assertTrue((output / 'selection.json').exists())
            self.assertTrue((output / 'INCOMPLETE').exists())
            self.assertFalse((output / 'manifest.json').exists())

    def test_wrong_partition_label_hash_and_unsafe_output_fail_before_write(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            repo, data, manifest, selection = self.setup_inputs(root)
            original = manifest.read_text()
            for mutation in ('partition', 'class_id', 'duplicate', 'hash'):
                document = json.loads(original)
                if mutation == 'partition':
                    document['rows'][0]['partition'] = 'fit'
                elif mutation == 'class_id':
                    document['rows'][0]['class_id'] = True
                elif mutation == 'duplicate':
                    document['rows'].append(document['rows'][0])
                manifest.write_text(json.dumps(document))
                if mutation != 'hash':
                    selection.write_text(json.dumps({'protocol_sha256': hashlib.sha256(manifest.read_bytes()).hexdigest()}))
                else:
                    selection.write_text(json.dumps({'protocol_sha256': '0' * 64}))
                output = data / f'parity/{mutation}'
                result = self.run_cli(repo, output, '--freeze-only')
                self.assertNotEqual(result.returncode, 0)
                self.assertFalse(output.exists())
            manifest.write_text(original)
            selection.write_text(json.dumps({'protocol_sha256': hashlib.sha256(manifest.read_bytes()).hexdigest()}))
            for output in (repo / 'forbidden', data / 'parity/../escape'):
                self.assertNotEqual(self.run_cli(repo, output, '--freeze-only').returncode, 0)
                self.assertFalse(output.exists())
            (data / 'parity').mkdir(exist_ok=True)
            (data / 'parity/link').symlink_to(root, target_is_directory=True)
            self.assertNotEqual(self.run_cli(repo, data / 'parity/link/new', '--freeze-only').returncode, 0)
            self.assertFalse((root / 'new').exists())


if __name__ == '__main__':
    unittest.main()
