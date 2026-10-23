import json
from pathlib import Path
import tempfile
import unittest
from collect_original_decision_contract_v112 import collect

class Export(unittest.TestCase):
    def test_whitelist_does_not_export_credentials_or_modify_inputs(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root/'results').mkdir()
            (root/'config.json').write_text(json.dumps({'provider': {'api_key': 'PRIVATE_SENTINEL'}, 'action_rules': {'buy_min_promising': 71, 'token': 'PRIVATE_SENTINEL', 'buy_max_risk': 'PRIVATE_SENTINEL'}, 'position_sizing': {'max_position_pct': 20, 'other': 'PRIVATE_SENTINEL'}}))
            (root/'results/model_params.json').write_text(json.dumps({'trained': True, 'calibration_usable': False, 'kpi_weights': [.3,.2,.2,.1,.2], 'arbitrary': 'PRIVATE_SENTINEL'}))
            (root/'results/latest.json').write_text(json.dumps({'scores': [{'asset': 'PRIVATE_SENTINEL', 'action': 'COMPRE', 'risk': 35, 'entry': 'PRIVATE_SENTINEL'}, {'action': []}]}))
            before = {str(p): p.read_bytes() for p in root.rglob('*') if p.is_file()}
            report = collect(root)
            self.assertNotIn('PRIVATE_SENTINEL', json.dumps(report))
            self.assertEqual(report['action_counts'], {'COMPRE': 1, 'UNRECOGNIZED': 1})
            self.assertEqual(report['original_settings']['action_rules']['buy_min_promising'], 71)
            self.assertEqual(report['calibration']['kpi_weights'], [.3,.2,.2,.1,.2])
            self.assertEqual(before, {str(p): p.read_bytes() for p in root.rglob('*') if p.is_file()})

    def test_missing_files_not_fabricated(self):
        with tempfile.TemporaryDirectory() as directory:
            report = collect(directory)
            self.assertIsNone(report['original_settings']['max_positions'])
            self.assertIsNone(report['calibration']['trained'])
            self.assertEqual(report['action_counts'], {})

    def test_symlinks_refused_and_nonfinite_or_boolean_weights_not_exported(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root/'results').mkdir()
            (root/'config.json').symlink_to('/dev/null')
            (root/'results/model_params.json').write_text('{"trained": "true", "kpi_weights": [true, 0, 0, 0, 1]}')
            report = collect(root)
            self.assertEqual(report['files']['config.json']['status'], 'UNAVAILABLE')
            self.assertIsNone(report['calibration']['trained'])
            self.assertIsNone(report['calibration']['kpi_weights'])

if __name__ == '__main__':
    unittest.main()
