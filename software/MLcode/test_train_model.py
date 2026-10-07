"""验证数据约定、真实 C++ 导出、同步和失败恢复；全部使用临时数据。"""
import csv
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import numpy as np

spec = importlib.util.spec_from_file_location("train_model", Path(__file__).with_name("train_model.py"))
model = importlib.util.module_from_spec(spec)
spec.loader.exec_module(model)


def write_samples(directory, points=200, front_only=True, labels=(3, 8, 10), files=3):
    directory.mkdir()
    rng = np.random.default_rng(11)
    active = [i for i in range(points) if not front_only or i < points // 4 or i > 3 * points // 4]
    for f in range(files):
        folder = directory / str(f)
        folder.mkdir()
        with (folder / "DATA.TXT").open("w", newline="") as handle:
            writer = csv.writer(handle)
            for i in range(90):
                label = labels[i % len(labels)]
                distances = np.zeros(points, dtype=int)
                distances[active] = rng.integers(400, 2200, len(active))
                encoded = 10 if label == 201 else label
                distances[active[4]] = encoded * 450 + rng.integers(0, 180)
                distances[active[-5]] = encoded * 300 + rng.integers(0, 180)
                writer.writerow([*distances.tolist(), label])


class PipelineTests(unittest.TestCase):
    def test_probability_export_preserves_soft_leaves_and_straight_command(self):
        from sklearn.ensemble import RandomForestClassifier
        rng = np.random.default_rng(12)
        samples = rng.uniform(1, 9000, (200, 2)).astype(np.float32)
        labels = rng.choice([3, 8, 201], 200)
        classifier = RandomForestClassifier(n_estimators=7, max_depth=1, min_samples_leaf=5,
                                             class_weight="balanced", random_state=12).fit(samples, labels)
        trees = np.asarray([t.predict(samples).astype(int) for t in classifier.estimators_])
        hard = classifier.classes_[[np.bincount(trees[:, i], minlength=3).argmax()
                                    for i in range(len(samples))]]
        self.assertTrue(np.any(hard != classifier.predict(samples)))
        with tempfile.TemporaryDirectory() as directory:
            result = model.verify_cpp(model.export_header(classifier, [22, 151]), classifier,
                                      samples, Path(directory))
        self.assertEqual(result["status"], "passed")

    def test_full_pipeline_non_contiguous_labels_and_backup(self):
        with tempfile.TemporaryDirectory() as root, patch.multiple(model, N_ESTIMATORS=9, MAX_DEPTH=3):
            root = Path(root)
            data, output, firmware = root / "dataset", root / "models", root / "firmware/randomForest.h"
            write_samples(data)
            firmware.parent.mkdir()
            firmware.write_text("previous model")
            self.assertEqual(model.main(["--k", "3", "--input-dir", str(data), "--output-dir", str(output),
                                         "--firmware-header", str(firmware)]), 0)
            report = json.loads((output / model.TRAIN_REPORT_FILENAME).read_text())
            self.assertEqual(report["class_commands"], [3, 8, 10])
            self.assertEqual(report["k"], 3)
            self.assertTrue(set(report["selected_indices"]) <= set(model.active_indices()))
            self.assertTrue(set(report["validation_split"]["train_files"]).isdisjoint(
                report["validation_split"]["test_files"]))
            self.assertEqual(report["export_checks"]["cpp"]["status"], "passed")
            self.assertEqual(firmware.read_bytes(), (output / model.HEADER_FILENAME).read_bytes())
            backups = list((output / model.BACKUP_SUBDIR).rglob("*.h"))
            self.assertEqual(len(backups), 1)
            self.assertEqual(backups[0].read_text(), "previous model")

    def test_clean_rejects_bad_rows_but_keeps_unobserved_sector_zeros(self):
        with tempfile.TemporaryDirectory() as root:
            data = Path(root) / "dataset"
            write_samples(data, files=1)
            path = data / "0/DATA.TXT"
            base = [1000 if i in model.active_indices() else 0 for i in range(200)] + [8]
            extra = [base[:150] + [8], base[:-1] + [255], base[:-1] + [201], [0] * 200 + [8]]
            for value in ("broken", "NaN", "inf", -1, 10000, 1.5):
                row = base.copy()
                row[0] = value
                extra.append(row)
            with path.open("a", newline="") as handle:
                csv.writer(handle).writerows(extra)
            rows, _, report = model.load_and_clean(data)
            self.assertEqual(len(rows), 90)
            counts = report["files"][0]["counts"]
            for reason in ("wrong_column_count", "dropped_label", "label_not_allowed", "all_zero_scan",
                           "non_numeric", "non_integer_distance"):
                self.assertEqual(counts[reason], 1)
            self.assertEqual(counts["non_finite"], 2)
            self.assertEqual(counts["distance_out_of_range"], 2)

    def test_empty_input_and_cpp_failure_preserve_existing_files(self):
        with tempfile.TemporaryDirectory() as root:
            root = Path(root)
            data, output, firmware = root / "dataset", root / "models", root / "firmware/randomForest.h"
            data.mkdir()
            output.mkdir()
            firmware.parent.mkdir()
            (output / model.HEADER_FILENAME).write_text("output old")
            firmware.write_text("firmware old")
            args = ["--k", "3", "--input-dir", str(data), "--output-dir", str(output),
                    "--firmware-header", str(firmware)]
            self.assertEqual(model.main(args), 1)
            data.rmdir()
            write_samples(data)
            with patch.multiple(model, N_ESTIMATORS=2, CXX="missing-cxx-for-test"):
                self.assertEqual(model.main(args), 1)
            self.assertEqual(firmware.read_text(), "firmware old")
            self.assertEqual((output / model.HEADER_FILENAME).read_text(), "output old")
            self.assertFalse((output / model.TRAIN_REPORT_FILENAME).exists())

    def test_changed_resolution_full_scan_and_label_remap(self):
        with tempfile.TemporaryDirectory() as root, patch.multiple(
                model, LIDAR_POINT_COUNT=80, USE_FRONT_SECTOR_ONLY=False,
                LABEL_REMAP={201: 10}, N_ESTIMATORS=3, MAX_DEPTH=2):
            root = Path(root)
            data, output = root / "dataset", root / "models"
            write_samples(data, points=80, front_only=False, labels=(3, 8, 201), files=1)
            self.assertEqual(model.main(["--k", "5", "--input-dir", str(data),
                                         "--output-dir", str(output), "--no-sync"]), 0)
            report = json.loads((output / model.TRAIN_REPORT_FILENAME).read_text())
            self.assertEqual(report["class_commands"], [3, 8, 10])
            self.assertEqual(report["validation_split"]["method"], "chronological_with_gap")
            self.assertIn("LIDAR_RESOLUTION = 80", (output / model.HEADER_FILENAME).read_text())
            self.assertEqual(report["validation_split"]["train_rows"], 62)

    def test_publish_rolls_back_partial_replacement(self):
        with tempfile.TemporaryDirectory() as root:
            root = Path(root)
            stage, output = root / "stage", root / "models"
            stage.mkdir()
            output.mkdir()
            new_report, new_model = stage / model.TRAIN_REPORT_FILENAME, stage / model.HEADER_FILENAME
            new_report.write_text("new report")
            new_model.write_text("new model")
            (output / model.HEADER_FILENAME).write_text("old model")
            firmware = root / "firmware/randomForest.h"
            firmware.parent.mkdir()
            firmware.write_text("old firmware")
            replace = model.replace_file
            calls = 0

            def fail_once(source, target):
                nonlocal calls
                calls += 1
                if calls == 3:
                    raise OSError("simulated firmware write failure")
                return replace(source, target)

            with patch.object(model, "replace_file", side_effect=fail_once):
                with self.assertRaises(OSError):
                    model.publish([new_report, new_model], output, firmware)
            self.assertEqual((output / model.HEADER_FILENAME).read_text(), "old model")
            self.assertEqual(firmware.read_text(), "old firmware")
            self.assertFalse((output / model.TRAIN_REPORT_FILENAME).exists())


if __name__ == "__main__":
    unittest.main()
