"""Isolated renderer fixtures, never performance measurements."""
import os
os.environ.setdefault("MPLBACKEND", "Agg")
import tempfile
import json
from pathlib import Path
import unittest
from unittest.mock import patch
import matplotlib.pyplot as plt
import plot_history as plots

class PlotHistoryTest(unittest.TestCase):
    def test_empty_regeneration_overwrites_stale_performance_figures(self):
        for kind in ('latency', 'fps'):
            with self.subTest(kind=kind), tempfile.TemporaryDirectory() as directory:
                path = Path(directory) / (kind + '_over_iterations.png')
                path.write_bytes(b'stale-apparently-successful-figure')
                with patch.object(plt, 'close'):
                    getattr(plots, 'plot_' + kind)([], Path(directory))
                    self.assertTrue(path.read_bytes().startswith(b'\x89PNG'))
                    texts = ' '.join(t.get_text() for ax in plt.gcf().axes for t in ax.texts)
                    self.assertIn('No measured', texts)
                plt.close('all')

    def test_schema_v2_latency_uses_named_summary_not_zero_or_interpreter_diagnostic(self):
        entries = [
            {'benchmark_type': 'latency', 'measurement_type': 'latency', 'timestamp': 'fixture', 'device': 'synthetic', 'gate_pass': True,
             'results': {'schema_version': 2, 'source': 'camerax_analyzer'},
             'assessment': {'boundary': 'final_analyzer_to_event_ms', 'event_latency_ms': {'n': 2, 'p50': 80, 'p95': 100}}},
            {'benchmark_type': 'latency', 'measurement_type': 'latency', 'timestamp': 'fixture', 'gate_pass': False, 'results': {}},
            {'benchmark_type': 'latency', 'measurement_type': 'interpreter_latency_diagnostic', 'timestamp': 'fixture', 'results': {'p95_ms': 1}},
        ]
        with tempfile.TemporaryDirectory() as directory, patch.object(plt, 'close'):
            plots.plot_latency(entries, Path(directory))
            ax = plt.gcf().axes[0]
            self.assertEqual([100, 80], [bar.get_height() for bar in ax.patches])
            self.assertIn('analyzer', ax.get_title().lower())
            self.assertTrue(any('REJECTED' in t.get_text() for t in ax.texts))
        plt.close('all')

    def test_schema_v2_analyzer_rates_preserve_stalls_and_rejection_labels(self):
        entries = [{'benchmark_type': 'fps', 'measurement_type': 'fps', 'gate_pass': False, 'device': 'synthetic', 'condition': 'optimal',
                    'results': {'schema_version': 2, 'source': 'camerax_analyzer', 'fps': {'analyzer': {'mean_fps': 25, 'per_second_samples': [30, 20, 0]}}}},
                   {'benchmark_type': 'fps', 'measurement_type': 'fps', 'gate_pass': False, 'results': {}}]
        with tempfile.TemporaryDirectory() as directory, patch.object(plt, 'close'):
            plots.plot_fps(entries, Path(directory))
            ax = plt.gcf().axes[0]
            self.assertEqual([25], list(ax.lines[0].get_ydata()))
            self.assertEqual([0], list(ax.lines[1].get_ydata()))
            self.assertIn('REJECTED', ax.get_xticklabels()[0].get_text())
            self.assertIn('analyzer', ax.get_title().lower())
        plt.close('all')

    def test_malformed_history_rows_and_estimates_are_not_measured_or_crashes(self):
        valid = {'benchmark_type': 'fps', 'timestamp': 'fixture', 'device': 'synthetic', 'condition': 'optimal', 'results': {}}
        with tempfile.TemporaryDirectory() as directory:
            history = Path(directory) / 'history.json'
            history.write_text(json.dumps([None, 42, {}, {'benchmark_type': 'fps', 'device': []},
                                           dict(valid, provenance='retroactive-estimate'), valid]))
            with patch.object(plots, 'HISTORY_PATH', history):
                rows = plots.load_and_filter('fps', 'synthetic', 'optimal')
                self.assertEqual([valid], rows)
                history.write_text('{malformed')
                self.assertEqual([], plots.load_and_filter('fps', None, None))

if __name__ == '__main__':
    unittest.main()
