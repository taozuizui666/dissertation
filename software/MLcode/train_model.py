#!/usr/bin/env python3
"""指定批次 -> 配对校验 -> 按地图验证 -> 随机森林 -> Python/C++ 模型。"""

from pathlib import Path

# ======================== 配置区：优先修改这里 ========================
# Python 没有 C 的 #define；大写常量提供相同的集中配置方式。
PROJECT_ROOT = Path(__file__).resolve().parents[2]

# 输入 / 输出（绝对路径，或相对于 dissertation 的路径）
DATA_SOURCE = "simulation"                # simulation / physical；标签含义不同，禁止混训
INPUT_DIR = PROJECT_ROOT / "dataset" / DATA_SOURCE
INPUT_BATCHES = ("collection_20261023_092900_850f9f",) if DATA_SOURCE == "simulation" else ()
DATA_VARIANT = "dropout"                 # 仿真："raw" / "dropout" / "both"（成对加载）
OUTPUT_DIR = PROJECT_ROOT / "software" / "ML_model" / DATA_SOURCE
FIRMWARE_HEADER = PROJECT_ROOT / "software/C_code/selfdrive/main/randomForest.h"
INPUT_EXTENSIONS = (".txt", ".csv")       # 不区分大小写，递归搜索
HEADER_FILENAME = "randomForest.h"
CLEANED_FILENAME = "data_cleaned.csv"
CLEAN_REPORT_FILENAME = "clean_report.json"
FEATURE_SCORES_FILENAME = "feature_scores.csv"
TRAIN_REPORT_FILENAME = "training_report.json"
PYTHON_MODEL_FILENAME = "randomForest.joblib"
BACKUP_SUBDIR = "backups"
SYNC_TO_FIRMWARE = False                  # simulation 禁止同步到旧实车控制器
SAVE_CLEANED_DATA = False                 # 避免默认再生成数 GB CSV；报告始终保存
SAVE_PYTHON_MODEL = True
READ_CHUNK_ROWS = 20000                   # 分块读取/验证，完整数据暂存为紧凑磁盘数组

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
CLEAN_DROP_LABELS = (255,)                # 255 是录制标志
TRAIN_LABELS = tuple(range(15 if DATA_SOURCE == "simulation" else 16))
STRAIGHT_COMMAND = 7 if DATA_SOURCE == "simulation" else 10
LABEL_REMAP = {}                          # 例如 {201: 10}，两者车轮控制相同
MIN_CLEAN_ROWS = 20

# all 模式完整保留 200 列（含固定零列）；k_best 模式才做训练集上的特征选择
FEATURE_MODE = "all"                     # all / k_best
K = 8
FEATURE_CANDIDATE_INDICES = None          # None = 实际采集列；或 (22, 23, ...)
REQUIRE_SELECTED_FEATURES_POSITIVE = False # 保留缺点零值，让 dropout 参与训练

# 仿真按地图分组：跨批次同地图及 raw/dropout 永远同侧
VALIDATION_MAPS = ("ellipse_002",) if DATA_SOURCE == "simulation" else ()
TEST_SIZE = 0.2
SPLIT_GAP_ROWS = 10                       # 单文件训练 / 验证间丢弃的相邻帧
RANDOM_SEED = 42
N_ESTIMATORS = 88
MAX_DEPTH = 3
MIN_SAMPLES_LEAF = 1
CLASS_WEIGHT = None                      # 可改为 "balanced"
N_JOBS = 1                               # 概率累加顺序可重复
TOLERANCE_LEVELS = (1, 2)                 # 转向标签允许相差的档位数

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
from dataclasses import dataclass
import csv
from datetime import datetime, timezone
import hashlib
from itertools import islice, zip_longest
import json
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
    if DATA_SOURCE not in ("simulation", "physical") or READ_CHUNK_ROWS < 1:
        raise ValueError("检查 DATA_SOURCE / READ_CHUNK_ROWS。")
    if DATA_SOURCE == "simulation" and (args.sync or VERIFY_TEENSY_BUILD):
        raise ValueError("仿真标签与旧实车不同，禁止同步或编译为旧实车模型。")
    if args.feature_mode == "k_best" and not 1 <= args.k <= len(active_indices()):
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


@dataclass
class Dataset:
    rows: object
    groups: object
    variants: object
    report: dict


def discover_sources(input_dir, batches):
    """每项为 (地图/分组名, 可选 raw 路径, 可选 dropout 路径)。"""
    if DATA_VARIANT not in ("raw", "dropout", "both"):
        raise ValueError("DATA_VARIANT 必须为 raw、dropout 或 both。")
    if DATA_SOURCE == "physical":
        files = sorted(p for p in input_dir.rglob("*")
                       if p.is_file() and p.suffix.lower() in INPUT_EXTENSIONS)
        sources = [(str(p.relative_to(input_dir)), p, None) for p in files]
    else:
        if not batches:
            raise ValueError("仿真必须通过 INPUT_BATCHES 或 --batch 明确指定采集批次。")
        if len(set(batches)) != len(batches):
            raise ValueError("采集批次重复。")
        sources = []
        for batch in batches:
            if Path(batch).name != batch:
                raise ValueError("批次只填写目录名，不填写路径。")
            directory = input_dir / batch
            variants = ("raw", "dropout") if DATA_VARIANT == "both" else (DATA_VARIANT,)
            files = {variant: {p.name.removesuffix(f"_{variant}.csv"): p
                               for p in sorted((directory / variant).glob(f"*_{variant}.csv"))}
                     for variant in variants}
            for variant in variants:
                if not files[variant]:
                    raise ValueError(f"{directory}/{variant} 没有训练数据。")
            if DATA_VARIANT == "both" and files["raw"].keys() != files["dropout"].keys():
                raise ValueError(f"{directory} 的 raw/dropout 文件未一一配对。")
            for name in files[variants[0]]:
                sources.append((name, files.get("raw", {}).get(name),
                                files.get("dropout", {}).get(name)))
    if not sources:
        raise ValueError(f"{input_dir} 没有训练数据，原模型未更换。")
    return sources


def read_chunks(path, report):
    """严格检查格式；损坏行中止，避免跳行破坏 raw/dropout 对齐。"""
    import numpy as np
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        if INPUT_HAS_HEADER:
            digest.update(next(handle, b""))
        while lines := list(islice(handle, READ_CHUNK_ROWS)):
            for line in lines:
                digest.update(line)
            if lines[0].startswith(b"version https://git-lfs.github.com/spec/"):
                raise ValueError(f"{path} 是 Git LFS 指针，请先下载实际数据。")
            text = [line.decode(INPUT_ENCODING).strip() for line in lines]
            if ALLOW_TRAILING_COMMA:
                text = [line.removesuffix(INPUT_DELIMITER) for line in text]
            try:
                data = np.loadtxt(text, delimiter=INPUT_DELIMITER, dtype=np.float64,
                                  ndmin=2, comments=None)
            except ValueError as error:
                raise ValueError(f"{path} 第 {report['total'] + 1} 行起格式异常：{error}") from error
            if data.shape != (len(lines), LIDAR_POINT_COUNT + 1):
                raise ValueError(f"{path} 存在空行或列数异常，应为 {LIDAR_POINT_COUNT + 1} 列。")
            report["total"] += len(data)
            yield data
    report["sha256"] = digest.hexdigest()


def clean_mask(data, report):
    import numpy as np
    keep = np.ones(len(data), dtype=bool)
    counts = report.setdefault("removed", Counter())

    def reject(reason, invalid):
        counts[reason] += int(np.count_nonzero(keep & invalid))
        keep[invalid] = False

    reject("non_finite", ~np.isfinite(data).all(axis=1))
    labels, distances = data[:, -1], data[:, :-1]
    reject("non_integer_label", labels != np.floor(labels))
    reject("dropped_label", np.isin(labels, CLEAN_DROP_LABELS))
    original = labels.copy()
    for old, new in LABEL_REMAP.items():
        labels[original == old] = new
    reject("label_not_allowed", ~np.isin(labels, TRAIN_LABELS))
    reject("distance_out_of_range", ((distances < 0) | (distances >= MAX_DISTANCE_MM)).any(axis=1))
    if CLEAN_REQUIRE_INTEGER_DISTANCES:
        reject("non_integer_distance", (distances != np.floor(distances)).any(axis=1))
    zeros = (distances[:, active_indices()] == 0).mean(axis=1)
    if CLEAN_DROP_ALL_ZERO_SCANS:
        reject("all_zero_scan", zeros == 1)
    reject("too_many_zeros", zeros > CLEAN_MAX_ZERO_FRACTION)
    return keep


def load_and_clean(input_dir, cache_dir, batches=None):
    import numpy as np
    sources = discover_sources(input_dir, INPUT_BATCHES if batches is None else batches)
    names = sorted({name for name, _, _ in sources})
    reports, total, labels = [], 0, Counter()
    dtype = np.uint16 if CLEAN_REQUIRE_INTEGER_DISTANCES else np.float32
    row_path, index_path = cache_dir / "rows.bin", cache_dir / "indices.bin"
    with row_path.open("wb") as row_file, index_path.open("wb") as index_file:
        for name, raw, dropout in sources:
            paths = [p for p in (raw, dropout) if p is not None]
            file_reports = [{"file": str(p.relative_to(input_dir)), "map": name,
                             "variant": "raw" if p == raw else "dropout", "total": 0,
                             "kept": 0, "label_counts": Counter()} for p in paths]
            streams = [read_chunks(p, r) for p, r in zip(paths, file_reports)]
            for chunks in zip_longest(*streams):
                if any(c is None for c in chunks) or len({len(c) for c in chunks}) != 1:
                    raise ValueError(f"{name}: raw/dropout 行数不一致。")
                if raw is not None and dropout is not None:
                    raw_data, drop_data = chunks
                    if not np.array_equal(raw_data[:, -1], drop_data[:, -1], equal_nan=True):
                        raise ValueError(f"{name}: raw/dropout 标签未对齐。")
                    equal = (drop_data[:, :-1] == raw_data[:, :-1]) | (drop_data[:, :-1] == 0)
                    equal |= np.isnan(drop_data[:, :-1]) & np.isnan(raw_data[:, :-1])
                    if not equal.all():
                        raise ValueError(f"{name}: dropout 含非置零改动，配对数据不一致。")
                masks = [clean_mask(c, r) for c, r in zip(chunks, file_reports)]
                joint = np.logical_and.reduce(masks)
                for chunk, mask, report in zip(chunks, masks, file_reports):
                    report["removed"]["paired_invalid"] += int(np.count_nonzero(mask & ~joint))
                    kept = chunk[joint].astype(dtype)
                    kept.tofile(row_file)
                    index = np.empty((len(kept), 2), dtype=np.int32)
                    index[:, 0], index[:, 1] = names.index(name), int(report["variant"] == "dropout")
                    index.tofile(index_file)
                    report["kept"] += len(kept)
                    unique, counts = np.unique(kept[:, -1], return_counts=True)
                    label_counts = {int(k): int(v) for k, v in zip(unique, counts)}
                    report["label_counts"].update(label_counts)
                    labels.update(label_counts)
                    total += len(kept)
            reports.extend(file_reports)
            print(f"读取 {paths[0].parent.parent.name}/{name}: " +
                  ", ".join(f"{r['variant']} {r['kept']}/{r['total']}" for r in file_reports), flush=True)
    if not total:
        raise ValueError("没有有效数据，原模型未更换。")
    rows = np.memmap(row_path, dtype=dtype, mode="r", shape=(total, LIDAR_POINT_COUNT + 1))
    index = np.memmap(index_path, dtype=np.int32, mode="r", shape=(total, 2))
    report = {"source": DATA_SOURCE, "data_variant": DATA_VARIANT if DATA_SOURCE == "simulation" else "raw",
              "expected_columns": LIDAR_POINT_COUNT + 1,
              "files": reports, "group_names": names, "kept_rows": total,
              "label_counts": dict(labels), "storage_dtype": str(rows.dtype)}
    return Dataset(rows, index[:, 0], index[:, 1], report)


def split_rows(dataset):
    import numpy as np
    from sklearn.model_selection import GroupShuffleSplit
    groups, labels = dataset.groups, dataset.rows[:, -1]
    indices = np.arange(len(labels))
    names = dataset.report["group_names"]
    if DATA_SOURCE == "simulation":
        if not VALIDATION_MAPS or not set(VALIDATION_MAPS) <= set(names):
            raise ValueError(f"VALIDATION_MAPS 必须是输入中的地图；当前地图：{names}")
        test_mask = np.isin(groups, [names.index(name) for name in VALIDATION_MAPS])
        train, test = indices[~test_mask], indices[test_mask]
        method = "held_out_maps"
    elif len(names) > 1:
        splitter = GroupShuffleSplit(n_splits=1, test_size=TEST_SIZE, random_state=RANDOM_SEED)
        train, test = next(splitter.split(indices, labels, groups))
        method = "by_file"
    else:
        boundary = int(len(labels) * (1 - TEST_SIZE))
        train, test = indices[:max(0, boundary - SPLIT_GAP_ROWS)], indices[boundary:]
        method = "chronological_with_gap"
    if len(train) < 2 or len(test) < 1:
        raise ValueError("训练或验证数据不足，请检查地图划分。")
    missing = set(np.unique(labels)) - set(np.unique(labels[train]))
    if missing or len(np.unique(labels[train])) < 2:
        raise ValueError(f"训练部分缺少类别 {sorted(missing)} 或少于两类。")
    return train, test, method


def make_classifier():
    from sklearn.ensemble import RandomForestClassifier
    return RandomForestClassifier(n_estimators=N_ESTIMATORS, max_depth=MAX_DEPTH,
                                  min_samples_leaf=MIN_SAMPLES_LEAF, class_weight=CLASS_WEIGHT,
                                  random_state=RANDOM_SEED, n_jobs=N_JOBS)


def feature_array(rows, indices, selected):
    import numpy as np
    result = np.empty((len(indices), len(selected)), dtype=np.float32)
    for start in range(0, len(indices), READ_CHUNK_ROWS):
        subset = indices[start:start + READ_CHUNK_ROWS]
        result[start:start + len(subset)] = rows[np.ix_(subset, selected)]
    return result


def validation_metrics(true, predictions, labels, majority):
    import numpy as np
    from sklearn.metrics import accuracy_score, classification_report, confusion_matrix, f1_score
    errors = np.abs(predictions.astype(int) - true.astype(int))
    return {"rows": len(true), "accuracy": float(accuracy_score(true, predictions)),
            "macro_f1": float(f1_score(true, predictions, labels=np.unique(true), average="macro", zero_division=0)),
            "majority_baseline_accuracy": float(np.mean(true == majority)),
            "confusion_labels": labels,
            "confusion_matrix": confusion_matrix(true, predictions, labels=labels).tolist(),
            "classification_report": classification_report(true, predictions, labels=labels,
                                                           output_dict=True, zero_division=0),
            "steering_mae": float(np.mean(errors)),
            "steering_tolerant_accuracy": {str(t): float(np.mean(errors <= t)) for t in TOLERANCE_LEVELS}}


def train(dataset, k=K, feature_mode=FEATURE_MODE):
    import numpy as np
    from sklearn.feature_selection import SelectKBest, f_classif
    rows, groups = dataset.rows, dataset.groups
    y = rows[:, -1].astype(np.int16)
    train_idx, test_idx, method = split_rows(dataset)
    scores = []
    if feature_mode == "all":
        selected = list(range(LIDAR_POINT_COUNT))
    elif feature_mode == "k_best":
        selection_idx = train_idx[dataset.variants[train_idx] == 0]
        if not len(selection_idx):
            selection_idx = train_idx  # dropout 单独模式只用训练侧 dropout 评分
        candidates = active_indices() if FEATURE_CANDIDATE_INDICES is None else sorted(set(FEATURE_CANDIDATE_INDICES))
        candidates = [i for i in candidates if np.ptp(rows[selection_idx, i]) > 0]
        if not 1 <= k <= len(candidates):
            raise ValueError(f"训练部分仅有 {len(candidates)} 个非常量候选特征，无法选择 K={k}。")
        selector = SelectKBest(f_classif, k=k)
        with np.errstate(divide="ignore", invalid="ignore"):
            selector.fit(feature_array(rows, selection_idx, candidates), y[selection_idx])
        selected = np.asarray(candidates)[selector.get_support(indices=True)].tolist()
        scores = [(i, float(v), int(i in selected)) for i, v in zip(candidates, selector.scores_)]
    else:
        raise ValueError("FEATURE_MODE 必须为 all 或 k_best。")
    if REQUIRE_SELECTED_FEATURES_POSITIVE:
        raise ValueError("当前训练保留 dropout 零值，请将 REQUIRE_SELECTED_FEATURES_POSITIVE 设为 False。")
    print(f"训练：{len(train_idx)} 行，{len(selected)} 列，{N_ESTIMATORS} 棵树；验证 {len(test_idx)} 行", flush=True)
    samples = feature_array(rows, train_idx, selected)
    classifier = make_classifier().fit(samples, y[train_idx])
    del samples
    predictions = np.empty(len(test_idx), dtype=y.dtype)
    for start in range(0, len(test_idx), READ_CHUNK_ROWS):
        subset = test_idx[start:start + READ_CHUNK_ROWS]
        predictions[start:start + len(subset)] = classifier.predict(feature_array(rows, subset, selected))
    labels = sorted(int(v) for v in np.unique(y))
    train_counts = dict(zip(*np.unique(y[train_idx], return_counts=True)))
    majority = max(train_counts, key=train_counts.get)
    metrics = {"combined": validation_metrics(y[test_idx], predictions, labels, majority)}
    for variant, name in enumerate(("raw", "dropout")):
        mask = dataset.variants[test_idx] == variant
        if mask.any():
            metrics[name] = validation_metrics(y[test_idx][mask], predictions[mask], labels, majority)
    names = dataset.report["group_names"]
    split = {"method": method, "train_rows": len(train_idx), "test_rows": len(test_idx),
             "train_groups": [names[int(i)] for i in np.unique(groups[train_idx])],
             "test_groups": [names[int(i)] for i in np.unique(groups[test_idx])],
             "train_label_counts": {int(k): int(v) for k, v in train_counts.items()},
             "test_label_counts": {int(k): int(v) for k, v in zip(*np.unique(y[test_idx], return_counts=True))},
             "absent_labels": sorted(set(TRAIN_LABELS) - set(labels))}
    rng = np.random.default_rng(RANDOM_SEED)
    chosen = rng.choice(len(rows), min(len(rows), VERIFY_SAMPLE_COUNT), replace=False)
    samples = feature_array(rows, chosen, selected)
    return classifier, selected, samples, scores, split, metrics


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
    zero_probes = samples[chosen[:min(100, len(chosen))]].copy()
    zero_probes[:, ::3] = 0
    check = np.vstack((samples[chosen], probes, zero_probes, np.zeros((1, samples.shape[1]), dtype=np.float32),
                       np.asarray(edges).reshape(-1, samples.shape[1])))
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
    print(f"C++ 导出验证通过：{len(check)} 个样本（含零值、随机输入和阈值边界）")
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
    parser.add_argument("--k", type=int, default=K, help="仅 k_best 模式生效")
    parser.add_argument("--feature-mode", choices=("all", "k_best"), default=FEATURE_MODE)
    parser.add_argument("--batch", action="append", help="批次目录名，可重复指定；覆盖 INPUT_BATCHES")
    parser.add_argument("--check", action="store_true", help="仅检查配置和文件配对，不训练")
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
        batches = args.batch if args.batch is not None else INPUT_BATCHES
        sources = discover_sources(args.input_dir, batches)
        if args.check:
            names = {name for name, _, _ in sources}
            if DATA_SOURCE == "simulation" and (not VALIDATION_MAPS or not set(VALIDATION_MAPS) < names):
                raise ValueError("VALIDATION_MAPS 必须存在且留有训练地图。")
            print(f"配置检查通过：{len(sources)} 组文件，数据 {DATA_VARIANT}，特征 {args.feature_mode}，验证地图 {VALIDATION_MAPS}")
            return 0
        with tempfile.TemporaryDirectory(prefix="dissertation-ml-") as temporary:
            stage = Path(temporary)
            dataset = load_and_clean(args.input_dir, stage, batches)
            rows, clean_report = dataset.rows, dataset.report
            if not args.clean_only and len(rows) < MIN_CLEAN_ROWS:
                raise ValueError(f"清理后仅 {len(rows)} 行，至少需要 {MIN_CLEAN_ROWS} 行。")
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
                classifier, selected, samples, scores, split, metrics = train(dataset, args.k, args.feature_mode)
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
                          "cleaning": clean_report, "feature_mode": args.feature_mode,
                          "input_batches": list(batches), "data_variant": clean_report["data_variant"],
                          "feature_count": len(selected),
                          "k": args.k if args.feature_mode == "k_best" else None, "selected_indices": selected,
                          "class_commands": classifier.classes_.astype(int).tolist(),
                          "validation_split": split, "validation_metrics": metrics,
                          "validation_note": "保存的森林即验证的森林；未使用验证地图重训。macro_f1 按验证中出现的类别计算。",
                          "refit_on_validation": False, "export_checks": checks,
                          "header_sha256": hashlib.sha256(header.encode()).hexdigest()}
                write_json(stage / TRAIN_REPORT_FILENAME, report)
                artifacts.append(stage / TRAIN_REPORT_FILENAME)
                if SAVE_PYTHON_MODEL:
                    joblib.dump({"classifier": classifier, "selected_indices": selected,
                                 "lidar_point_count": LIDAR_POINT_COUNT,
                                 "class_commands": report["class_commands"],
                                 "data_source": DATA_SOURCE, "data_variant": clean_report["data_variant"],
                                 "straight_command": STRAIGHT_COMMAND,
                                 "allow_zero_input": True, "feature_mode": args.feature_mode}, stage / PYTHON_MODEL_FILENAME)
                    artifacts.append(stage / PYTHON_MODEL_FILENAME)
                print(f"特征数：{len(selected)}；验证准确率：{metrics['combined']['accuracy']:.4f}")
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
