#!/usr/bin/env python3
"""操作数据 -> 清理 -> K 特征 -> 随机森林 -> C++ 头文件 -> 固件同步。"""

from pathlib import Path

# ======================== 配置区：优先修改这里 ========================
# Python 没有 C 的 #define；大写常量提供相同的集中配置方式。
PROJECT_ROOT = Path(__file__).resolve().parents[2]

# 输入 / 输出（绝对路径，或相对于 dissertation 的路径）
INPUT_DIR = PROJECT_ROOT / "dataset"
OUTPUT_DIR = PROJECT_ROOT / "software" / "ML_model"
FIRMWARE_HEADER = PROJECT_ROOT / "software/C_code/selfdrive/main/randomForest.h"
INPUT_EXTENSIONS = (".txt", ".csv")       # 不区分大小写，递归搜索
HEADER_FILENAME = "randomForest.h"
CLEANED_FILENAME = "data_cleaned.csv"
CLEAN_REPORT_FILENAME = "clean_report.json"
FEATURE_SCORES_FILENAME = "feature_scores.csv"
TRAIN_REPORT_FILENAME = "training_report.json"
PYTHON_MODEL_FILENAME = "randomForest.joblib"
BACKUP_SUBDIR = "backups"
SYNC_TO_FIRMWARE = True                   # 成功后备份并覆盖固件模型
SAVE_CLEANED_DATA = True
SAVE_PYTHON_MODEL = True

# 数据格式：必须与 collect_data 中的 LIDAR_RESOLUTION 一致
LIDAR_POINT_COUNT = 200                   # 一行有该数量的距离 + 1 个标签
USE_FRONT_SECTOR_ONLY = True              # index < N/4 或 index > 3*N/4
MAX_DISTANCE_MM = 10000                   # 有效距离上界，不包含该值
INPUT_ENCODING = "utf-8-sig"
INPUT_DELIMITER = ","
INPUT_HAS_HEADER = False
ALLOW_TRAILING_COMMA = False

# clean：未采集扇区正常情况下全是 0，不能因存在 0 删除整行
CLEAN_REQUIRE_INTEGER_DISTANCES = True
CLEAN_DROP_ALL_ZERO_SCANS = True
CLEAN_MAX_ZERO_FRACTION = 1.0              # 仅在采集扇区计算，1.0 不限制
CLEAN_REMOVE_DUPLICATES = False           # 开启后在每个文件内去重
CLEAN_DROP_LABELS = (255,)                # 255 是录制标志
TRAIN_LABELS = tuple(range(16))           # 需要保留直行类别时加入 201
LABEL_REMAP = {}                          # 例如 {201: 10}，两者车轮控制相同
MIN_CLEAN_ROWS = 20

# K 个有效特征：原始列索引、顺序自动写进头文件
K = 8
FEATURE_CANDIDATE_INDICES = None          # None = 实际采集列；或 (22, 23, ...)
REQUIRE_SELECTED_FEATURES_POSITIVE = True # 丢弃选中列为 0 的行，符合固件有效输入

# 训练 / 验证：多个文件按文件分组；单文件按时间顺序切分
TEST_SIZE = 0.2
SPLIT_GAP_ROWS = 10                       # 单文件训练 / 验证间丢弃的相邻帧
RANDOM_SEED = 42
N_ESTIMATORS = 88
MAX_DEPTH = 3
MIN_SAMPLES_LEAF = 1
CLASS_WEIGHT = None                      # 可改为 "balanced"
N_JOBS = 1                               # 概率累加顺序可重复
TOLERANCE_LEVELS = (1, 2)                 # 仅对 0–15 转向指令计算容差准确率

# 验证 / 发布：验证失败绝不覆盖原模型
VERIFY_CPP_EXPORT = True                  # 编译真实 C++ 推理核对 Python 预测
CXX = "g++"                              # 可填编译器绝对路径
VERIFY_SAMPLE_COUNT = 1000
VERIFY_RANDOM_PROBE_COUNT = 200
VERIFY_TEENSY_BUILD = False               # 启用后须能找到 Arduino CLI
ARDUINO_CLI = "arduino-cli"               # 可填 Arduino IDE 内 CLI 的绝对路径
ARDUINO_CONFIG_FILE = None                # 可选 CLI yaml 路径
ARDUINO_FQBN = "teensy:avr:teensy40:usb=serial"
TOOL_TIMEOUT_SECONDS = 180
# ======================== 配置区结束 ========================

import argparse
from collections import Counter
import csv
from datetime import datetime, timezone
import hashlib
import json
import math
import os
import shutil
import subprocess
import sys
import tempfile


def resolve_path(value):
    path = Path(value).expanduser()
    return (path if path.is_absolute() else PROJECT_ROOT / path).resolve()


def active_indices():
    return [i for i in range(LIDAR_POINT_COUNT)
            if not USE_FRONT_SECTOR_ONLY or
            i < LIDAR_POINT_COUNT // 4 or i > 3 * LIDAR_POINT_COUNT // 4]


def validate_config(args):
    if not isinstance(LIDAR_POINT_COUNT, int) or not 1 <= LIDAR_POINT_COUNT <= 65535:
        raise ValueError("LIDAR_POINT_COUNT 必须为 1–65535 的整数。")
    if not 1 <= args.k <= len(active_indices()):
        raise ValueError("K 必须在 1 与实际采集列数之间。")
    if not 0 < TEST_SIZE < 1 or SPLIT_GAP_ROWS < 0:
        raise ValueError("TEST_SIZE 必须在 0–1 之间，SPLIT_GAP_ROWS 不能为负。")
    if (not 0 <= CLEAN_MAX_ZERO_FRACTION <= 1 or not isinstance(MAX_DISTANCE_MM, int)
            or not 1 < MAX_DISTANCE_MM <= 65535):
        raise ValueError("检查 CLEAN_MAX_ZERO_FRACTION / MAX_DISTANCE_MM。")
    if not TRAIN_LABELS or not set(TRAIN_LABELS) <= set(range(16)) | {200, 201}:
        raise ValueError("TRAIN_LABELS 只能包含控制程序支持的 0–15、200、201。")
    if len(INPUT_DELIMITER) != 1:
        raise ValueError("INPUT_DELIMITER 必须为一个字符。")
    if FEATURE_CANDIDATE_INDICES is not None:
        if not set(FEATURE_CANDIDATE_INDICES) <= set(active_indices()):
            raise ValueError("FEATURE_CANDIDATE_INDICES 含未采集或越界的列。")
    names = (HEADER_FILENAME, CLEANED_FILENAME, CLEAN_REPORT_FILENAME,
             FEATURE_SCORES_FILENAME, TRAIN_REPORT_FILENAME, PYTHON_MODEL_FILENAME)
    if len(set(names)) != len(names) or any(Path(n).name != n for n in names):
        raise ValueError("输出文件名必须互不相同且不含目录，目录请修改 OUTPUT_DIR。")
    if args.sync and args.firmware_header.name != "randomForest.h":
        raise ValueError("固件 main.ino 引用 randomForest.h，请保持目标文件名一致。")
    if args.output_dir.is_relative_to(args.input_dir):
        raise ValueError("OUTPUT_DIR 不能位于 INPUT_DIR 内，避免再次读入上次清理的输出。")
    if VERIFY_SAMPLE_COUNT < 1 or VERIFY_RANDOM_PROBE_COUNT < 0:
        raise ValueError("VERIFY_SAMPLE_COUNT 至少为 1，VERIFY_RANDOM_PROBE_COUNT 不能为负。")


def load_and_clean(input_dir):
    extensions = {s.lower() for s in INPUT_EXTENSIONS}
    files = sorted(p for p in input_dir.rglob("*") if p.is_file() and p.suffix.lower() in extensions)
    if not files:
        raise ValueError(f"{input_dir} 没有操作数据，原模型未更换。")
    rows, groups, reports = [], [], []
    active = active_indices()
    for group, path in enumerate(files):
        counts, columns, labels_seen, seen = Counter(), Counter(), Counter(), set()
        source = str(path.relative_to(input_dir))
        with path.open(encoding=INPUT_ENCODING, errors="replace") as handle:
            for line_number, line in enumerate(handle, 1):
                counts["total"] += 1
                if INPUT_HAS_HEADER and line_number == 1:
                    counts["header"] += 1
                    continue
                line = line.strip()
                if not line:
                    counts["blank"] += 1
                    continue
                parts = line.split(INPUT_DELIMITER)
                if ALLOW_TRAILING_COMMA and not parts[-1].strip():
                    parts.pop()
                columns[len(parts)] += 1
                if len(parts) != LIDAR_POINT_COUNT + 1:
                    counts["wrong_column_count"] += 1
                    continue
                try:
                    values = [float(p) for p in parts]
                except ValueError:
                    counts["non_numeric"] += 1
                    continue
                if not all(math.isfinite(v) for v in values):
                    counts["non_finite"] += 1
                    continue
                if not values[-1].is_integer():
                    counts["non_integer_label"] += 1
                    continue
                label = int(values[-1])
                labels_seen[label] += 1
                if label in CLEAN_DROP_LABELS:
                    counts["dropped_label"] += 1
                    continue
                label = LABEL_REMAP.get(label, label)
                if label not in TRAIN_LABELS:
                    counts["label_not_allowed"] += 1
                    continue
                distances = values[:-1]
                if any(v < 0 or v >= MAX_DISTANCE_MM for v in distances):
                    counts["distance_out_of_range"] += 1
                    continue
                if CLEAN_REQUIRE_INTEGER_DISTANCES and any(not v.is_integer() for v in distances):
                    counts["non_integer_distance"] += 1
                    continue
                zeros = sum(distances[i] == 0 for i in active)
                if CLEAN_DROP_ALL_ZERO_SCANS and zeros == len(active):
                    counts["all_zero_scan"] += 1
                    continue
                if zeros / len(active) > CLEAN_MAX_ZERO_FRACTION:
                    counts["too_many_zeros"] += 1
                    continue
                row = tuple(distances) + (label,)
                if CLEAN_REMOVE_DUPLICATES:
                    if row in seen:
                        counts["duplicate"] += 1
                        continue
                    seen.add(row)
                rows.append(row)
                groups.append(group)
                counts["kept"] += 1
        reports.append({"file": source, "counts": dict(counts),
                        "observed_column_counts": dict(columns),
                        "label_counts_before_filter": dict(labels_seen)})
        print(f"清理 {source}: {counts['kept']}/{counts['total']} 行保留")
    if not rows:
        raise ValueError(f"没有有效数据；应有 {LIDAR_POINT_COUNT + 1} 列。统计：{reports}")
    report = {"expected_columns": LIDAR_POINT_COUNT + 1, "files": reports,
              "kept_rows": len(rows), "label_counts": dict(Counter(r[-1] for r in rows))}
    return rows, groups, report


def split_rows(groups, labels):
    import numpy as np
    from sklearn.model_selection import GroupShuffleSplit
    indices = np.arange(len(labels))
    if len(set(groups)) > 1:
        split = GroupShuffleSplit(n_splits=1, test_size=TEST_SIZE, random_state=RANDOM_SEED)
        train, test = next(split.split(indices, labels, groups))
        method = "by_file"
    else:
        boundary = int(len(labels) * (1 - TEST_SIZE))
        train, test = indices[:max(0, boundary - SPLIT_GAP_ROWS)], indices[boundary:]
        method = "chronological_with_gap"
    if len(train) < 2 or len(test) < 1:
        raise ValueError("训练或验证数据不足；补充数据或调整 TEST_SIZE / SPLIT_GAP_ROWS。")
    missing = set(labels) - set(labels[train])
    if missing or len(set(labels[train])) < 2:
        raise ValueError(f"训练部分缺少类别 {sorted(missing)} 或少于两类；"
                         "请补充多次采集数据或调整划分配置，不回退到随机相邻帧划分。")
    if len(train) <= len(set(labels[train])):
        raise ValueError("训练样本数必须多于类别数，才能计算 ANOVA F 分数。")
    return train, test, method


def make_classifier():
    from sklearn.ensemble import RandomForestClassifier
    return RandomForestClassifier(n_estimators=N_ESTIMATORS, max_depth=MAX_DEPTH,
                                  min_samples_leaf=MIN_SAMPLES_LEAF, class_weight=CLASS_WEIGHT,
                                  random_state=RANDOM_SEED, n_jobs=N_JOBS)


def train(rows, groups, k):
    import numpy as np
    from sklearn.feature_selection import SelectKBest, f_classif
    from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
    data = np.asarray(rows, dtype=np.float64)
    X, y = data[:, :-1], data[:, -1].astype(int)
    train_idx, test_idx, method = split_rows(groups, y)
    candidates = active_indices() if FEATURE_CANDIDATE_INDICES is None else sorted(set(FEATURE_CANDIDATE_INDICES))
    candidates = np.asarray([i for i in candidates if np.ptp(X[train_idx, i]) > 0])
    if len(candidates) < k:
        raise ValueError(f"训练部分仅有 {len(candidates)} 个非常量候选特征，无法选择 K={k}。")
    selector = SelectKBest(f_classif, k=k)
    with np.errstate(divide="ignore", invalid="ignore"):
        selector.fit(X[train_idx][:, candidates], y[train_idx])
    selected = candidates[selector.get_support(indices=True)]
    valid = np.all(X[:, selected] > 0, axis=1) if REQUIRE_SELECTED_FEATURES_POSITIVE else np.ones(len(y), bool)
    train_idx, test_idx = train_idx[valid[train_idx]], test_idx[valid[test_idx]]
    if len(test_idx) == 0 or set(y) != set(y[train_idx]) or len(set(y[train_idx])) < 2:
        raise ValueError("选中特征的有效样本不足或训练类别缺失；检查 0 值、K 和数据划分。")
    samples = X[:, selected].astype(np.float32)
    classifier = make_classifier().fit(samples[train_idx], y[train_idx])
    predictions, true = classifier.predict(samples[test_idx]), y[test_idx]
    labels = sorted(set(y.tolist()))
    metrics = {"accuracy": float(accuracy_score(true, predictions)), "confusion_labels": labels,
               "confusion_matrix": confusion_matrix(true, predictions, labels=labels).tolist(),
               "classification_report": classification_report(true, predictions, labels=labels,
                                                              output_dict=True, zero_division=0)}
    steering = (true >= 0) & (true <= 15)
    if steering.any():
        errors = np.abs(predictions[steering] - true[steering])
        predicted_steering = (predictions[steering] >= 0) & (predictions[steering] <= 15)
        metrics["steering_mae"] = float(np.mean(errors))
        metrics["steering_tolerant_accuracy"] = {
            str(t): float(np.mean(predicted_steering & (errors <= t))) for t in TOLERANCE_LEVELS}
    split = {"method": method, "train_rows": len(train_idx), "test_rows": len(test_idx),
             "train_files": sorted({groups[i] for i in train_idx}),
             "test_files": sorted({groups[i] for i in test_idx}),
             "selected_zero_rows_dropped": int((~valid).sum()),
             "train_label_counts": dict(Counter(y[train_idx].tolist())),
             "test_label_counts": dict(Counter(true.tolist()))}
    # 验证后只重训森林；冻结特征，不用验证数据重新选特征。
    classifier = make_classifier().fit(samples[valid], y[valid])
    scores = [(int(i), float(s), int(i in selected)) for i, s in zip(candidates, selector.scores_)]
    return classifier, selected.tolist(), samples[valid], scores, split, metrics


def cpp_number(value):
    value = format(float(value), ".17g")
    return value if "." in value or "e" in value else value + ".0"


def export_header(classifier, selected):
    """保留 sklearn 的叶节点概率平均，避免硬投票改变预测结果。"""
    classes = [int(v) for v in classifier.classes_]
    lines = ["#pragma once", "#include <stdint.h>",
             "// Generated by software/MLcode/train_model.py. Do not edit separately.",
             "namespace ModelConfig {",
             f"constexpr uint16_t LIDAR_RESOLUTION = {LIDAR_POINT_COUNT};",
             f"constexpr uint16_t MAX_DISTANCE_MM = {MAX_DISTANCE_MM};",
             f"constexpr bool FRONT_SECTOR_ONLY = {'true' if USE_FRONT_SECTOR_ONLY else 'false'};",
             f"constexpr uint16_t FEATURE_COUNT = {len(selected)};",
             "constexpr uint16_t FEATURE_INDICES[FEATURE_COUNT] = {" + ", ".join(map(str, selected)) + "};",
             f"constexpr uint16_t CLASS_COUNT = {len(classes)};",
             "constexpr int CLASS_COMMANDS[CLASS_COUNT] = {" + ", ".join(map(str, classes)) + "};",
             "constexpr bool isActiveIndex(uint16_t index) {",
             "    return index < LIDAR_RESOLUTION && (!FRONT_SECTOR_ONLY ||",
             "           index < LIDAR_RESOLUTION / 4 || index > 3 * LIDAR_RESOLUTION / 4);",
             "}", "inline int commandForClass(int index) {",
             "    return index >= 0 && index < CLASS_COUNT ? CLASS_COMMANDS[index] : 200;",
             "}", "}", "namespace Eloquent { namespace ML { namespace Port {",
             "class RandomForest {", "public:",
             "    void predictProba(const float *x, double *probabilities) const {",
             "        for (uint16_t i = 0; i < ModelConfig::CLASS_COUNT; ++i) probabilities[i] = 0.0;"]

    def emit_node(tree, node, indent):
        if tree.children_left[node] == tree.children_right[node]:
            values = tree.value[node][0]
            # scikit-learn >= 1.4 已保存归一化概率，直接保留完整精度。
            for i, value in enumerate(values):
                if value:
                    lines.append(f"{indent}probabilities[{i}] += {cpp_number(value)};")
        else:
            feature, threshold = tree.feature[node], cpp_number(tree.threshold[node])
            lines.append(f"{indent}if (x[{feature}] <= {threshold}) {{")
            emit_node(tree, tree.children_left[node], indent + "    ")
            lines.append(indent + "} else {")
            emit_node(tree, tree.children_right[node], indent + "    ")
            lines.append(indent + "}")

    for i, estimator in enumerate(classifier.estimators_, 1):
        lines.append(f"        // tree #{i}")
        emit_node(estimator.tree_, 0, "        ")
    lines += [f"        for (uint16_t i = 0; i < ModelConfig::CLASS_COUNT; ++i) probabilities[i] /= {len(classifier.estimators_)}.0;",
              "    }", "    int predict(const float *x) const {",
              "        double probabilities[ModelConfig::CLASS_COUNT];", "        predictProba(x, probabilities);",
              "        int best = 0;", "        for (uint16_t i = 1; i < ModelConfig::CLASS_COUNT; ++i)",
              "            if (probabilities[i] > probabilities[best]) best = i;",
              "        return best;", "    }", "};", "}}}", ""]
    return "\n".join(lines)


def run_tool(command, **kwargs):
    result = subprocess.run(command, text=True, capture_output=True, timeout=TOOL_TIMEOUT_SECONDS, **kwargs)
    if result.returncode:
        raise ValueError(f"工具失败：{command[0]}\n{result.stdout[-4000:]}\n{result.stderr[-4000:]}")
    return result.stdout


def verify_cpp(header, classifier, samples, directory):
    import numpy as np
    compiler = shutil.which(CXX)
    if not compiler:
        raise ValueError(f"找不到 C++ 编译器 {CXX}；配置 CXX 或显式关闭 VERIFY_CPP_EXPORT。")
    rng = np.random.default_rng(RANDOM_SEED)
    chosen = rng.choice(len(samples), min(len(samples), VERIFY_SAMPLE_COUNT), replace=False)
    probes = rng.uniform(1, MAX_DISTANCE_MM - 1,
                         size=(VERIFY_RANDOM_PROBE_COUNT, samples.shape[1])).astype(np.float32)
    edges = []
    for estimator in classifier.estimators_:
        for feature, threshold in zip(estimator.tree_.feature, estimator.tree_.threshold):
            if feature >= 0:
                value = np.float32(threshold)
                for edge in (np.nextafter(value, np.float32(-np.inf)), value,
                             np.nextafter(value, np.float32(np.inf))):
                    row = samples[chosen[0]].copy()
                    row[feature] = edge
                    edges.append(row)
    check = np.vstack((samples[chosen], probes, np.asarray(edges).reshape(-1, samples.shape[1])))
    (directory / "randomForest.h").write_text(header, encoding="utf-8")
    source = directory / "verify.cpp"
    source.write_text('''#include <iostream>
#include <iomanip>
#include "randomForest.h"
int main() {
    Eloquent::ML::Port::RandomForest model;
    float x[ModelConfig::FEATURE_COUNT];
    while (std::cin >> x[0]) {
        for (unsigned i = 1; i < ModelConfig::FEATURE_COUNT; ++i)
            if (!(std::cin >> x[i])) return 2;
        double p[ModelConfig::CLASS_COUNT];
        model.predictProba(x, p);
        std::cout << ModelConfig::commandForClass(model.predict(x));
        for (double v : p) std::cout << ' ' << std::setprecision(17) << v;
        std::cout << '\\n';
    }
}
''', encoding="utf-8")
    binary = directory / ("verify.exe" if os.name == "nt" else "verify")
    run_tool([compiler, "-std=c++11", "-O2", str(source), "-o", str(binary)])
    inputs = "".join(" ".join(cpp_number(v) for v in row) + "\n" for row in check)
    result = np.asarray([list(map(float, line.split())) for line in
                         run_tool([str(binary)], input=inputs).splitlines()])
    if result.shape != (len(check), len(classifier.classes_) + 1):
        raise ValueError("C++ 验证输出不完整。")
    if not np.array_equal(result[:, 0], classifier.predict(check)):
        raise ValueError("C++ 与 Python 指令预测不一致，原模型未更换。")
    np.testing.assert_allclose(result[:, 1:], classifier.predict_proba(check), rtol=1e-12, atol=1e-12)
    print(f"C++ 导出验证通过：{len(check)} 个样本（含随机输入和阈值边界）")
    return {"status": "passed", "samples": len(check)}


def verify_teensy(header, firmware_header, directory):
    cli = shutil.which(ARDUINO_CLI)
    if not cli:
        raise ValueError("找不到 Arduino CLI；配置 ARDUINO_CLI 或关闭 VERIFY_TEENSY_BUILD。")
    if not (firmware_header.parent / "main.ino").is_file():
        raise ValueError("Teensy 编译目录缺少 main.ino。")
    sketch = directory / "main"
    shutil.copytree(firmware_header.parent, sketch)
    (sketch / "randomForest.h").write_text(header, encoding="utf-8")
    command = [cli]
    if ARDUINO_CONFIG_FILE:
        command += ["--config-file", str(resolve_path(ARDUINO_CONFIG_FILE))]
    command += ["compile", "--fqbn", ARDUINO_FQBN, "--build-path", str(directory / "build"), str(sketch)]
    run_tool(command)
    print("Teensy 4.0 工程编译通过")
    return {"status": "passed", "fqbn": ARDUINO_FQBN}


def json_safe(value):
    if isinstance(value, Path):
        return str(value)
    if isinstance(value, dict):
        return {str(k): json_safe(v) for k, v in value.items()}
    if isinstance(value, (tuple, list)):
        return [json_safe(v) for v in value]
    return value


def write_json(path, value):
    path.write_text(json.dumps(json_safe(value), ensure_ascii=False, indent=2, allow_nan=False) + "\n", encoding="utf-8")


def replace_file(source, target):
    target.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(dir=target.parent, delete=False) as handle:
        temporary = Path(handle.name)
    try:
        shutil.copyfile(source, temporary)
        os.chmod(temporary, target.stat().st_mode & 0o777 if target.exists() else 0o644)
        os.replace(temporary, target)
    finally:
        temporary.unlink(missing_ok=True)


def publish(staged_files, output_dir, firmware_header=None):
    """各文件原子替换；失败恢复已替换文件，模型另存永久备份。"""
    targets = [(source, output_dir / source.name) for source in staged_files]
    if firmware_header:
        model = next(p for p in staged_files if p.name == HEADER_FILENAME)
        if firmware_header != output_dir / HEADER_FILENAME:
            targets.append((model, firmware_header))
    with tempfile.TemporaryDirectory(prefix="ml-rollback-") as temporary:
        rollback, changed = {}, []
        for i, (_, target) in enumerate(targets):
            old = Path(temporary) / str(i)
            if target.exists():
                shutil.copy2(target, old)
                rollback[target] = old
            else:
                rollback[target] = None
        model_targets = [t for _, t in targets if t.name == HEADER_FILENAME or t == firmware_header]
        if any(t.exists() for t in model_targets):
            stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
            backup = output_dir / BACKUP_SUBDIR / stamp
            backup.mkdir(parents=True)
            for i, target in enumerate(model_targets):
                if target.exists():
                    shutil.copy2(target, backup / f"{i}_{target.name}")
            print(f"旧模型备份：{backup}")
        try:
            for source, target in targets:
                replace_file(source, target)
                changed.append(target)
        except BaseException:
            for target in reversed(changed):
                if rollback[target] is None:
                    target.unlink(missing_ok=True)
                else:
                    replace_file(rollback[target], target)
            raise


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--k", type=int, default=K)
    parser.add_argument("--input-dir", default=INPUT_DIR)
    parser.add_argument("--output-dir", default=OUTPUT_DIR)
    parser.add_argument("--firmware-header", default=FIRMWARE_HEADER)
    parser.add_argument("--no-sync", action="store_true", help="只输出模型，不覆盖固件")
    parser.add_argument("--clean-only", action="store_true", help="只输出清理数据和报告")
    args = parser.parse_args(argv)
    args.input_dir, args.output_dir, args.firmware_header = map(
        resolve_path, (args.input_dir, args.output_dir, args.firmware_header))
    args.sync = SYNC_TO_FIRMWARE and not args.no_sync and not args.clean_only
    try:
        validate_config(args)
        rows, groups, clean_report = load_and_clean(args.input_dir)
        if not args.clean_only and len(rows) < MIN_CLEAN_ROWS:
            raise ValueError(f"清理后仅 {len(rows)} 行，至少需要 MIN_CLEAN_ROWS={MIN_CLEAN_ROWS}。")
        with tempfile.TemporaryDirectory(prefix="dissertation-ml-") as temporary:
            stage = Path(temporary)
            write_json(stage / CLEAN_REPORT_FILENAME, clean_report)
            artifacts = [stage / CLEAN_REPORT_FILENAME]
            if SAVE_CLEANED_DATA:
                with (stage / CLEANED_FILENAME).open("w", encoding="utf-8", newline="") as handle:
                    csv.writer(handle, delimiter=INPUT_DELIMITER).writerows(rows)
                artifacts.append(stage / CLEANED_FILENAME)
            if not args.clean_only:
                import joblib
                import numpy as np
                import sklearn
                if tuple(int(v) for v in sklearn.__version__.split(".")[:2]) < (1, 4):
                    raise ValueError("需要 scikit-learn >= 1.4，请按 requirements.txt 更新依赖。")
                classifier, selected, samples, scores, split, metrics = train(rows, groups, args.k)
                for key in ("train_files", "test_files"):
                    split[key] = [clean_report["files"][i]["file"] for i in split[key]]
                header = export_header(classifier, selected)
                checks = {"cpp": {"status": "disabled"}, "teensy": {"status": "disabled"}}
                if VERIFY_CPP_EXPORT:
                    checks["cpp"] = verify_cpp(header, classifier, samples, stage)
                if VERIFY_TEENSY_BUILD:
                    checks["teensy"] = verify_teensy(header, args.firmware_header, stage)
                model_path = stage / HEADER_FILENAME
                model_path.write_text(header, encoding="utf-8")
                artifacts.append(model_path)
                with (stage / FEATURE_SCORES_FILENAME).open("w", encoding="utf-8", newline="") as handle:
                    writer = csv.writer(handle)
                    writer.writerow(("original_index", "f_score", "selected"))
                    writer.writerows(scores)
                artifacts.append(stage / FEATURE_SCORES_FILENAME)
                report = {"created_at": datetime.now(timezone.utc).isoformat(),
                          "input_dir": str(args.input_dir), "output_dir": str(args.output_dir),
                          "firmware_header": str(args.firmware_header) if args.sync else None,
                          "configuration": {n: v for n, v in globals().items() if n.isupper()},
                          "versions": {"numpy": np.__version__, "sklearn": sklearn.__version__},
                          "cleaning": clean_report, "k": args.k, "selected_indices": selected,
                          "class_commands": classifier.classes_.astype(int).tolist(),
                          "validation_split": split, "validation_metrics": metrics,
                          "validation_note": "指标来自独立验证集；最终森林使用冻结特征在全部有效数据上重训。",
                          "refit_rows": len(samples), "export_checks": checks,
                          "header_sha256": hashlib.sha256(header.encode()).hexdigest()}
                write_json(stage / TRAIN_REPORT_FILENAME, report)
                artifacts.append(stage / TRAIN_REPORT_FILENAME)
                if SAVE_PYTHON_MODEL:
                    joblib.dump({"classifier": classifier, "selected_indices": selected,
                                 "lidar_point_count": LIDAR_POINT_COUNT,
                                 "class_commands": report["class_commands"]}, stage / PYTHON_MODEL_FILENAME)
                    artifacts.append(stage / PYTHON_MODEL_FILENAME)
                print(f"选中特征：{selected}；验证准确率：{metrics['accuracy']:.4f}")
            publish(artifacts, args.output_dir, args.firmware_header if args.sync else None)
        print(f"输出目录：{args.output_dir}")
        if args.sync:
            print(f"已同步模型：{args.firmware_header}")
        return 0
    except ImportError as error:
        print(f"缺少训练依赖：{error}。请执行 python -m pip install --user -r software/MLcode/requirements.txt", file=sys.stderr)
        return 1
    except (ValueError, OSError, AssertionError, subprocess.TimeoutExpired) as error:
        print(f"流程失败：{error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
