# 操作数据训练与部署

唯一运行入口是 `train_model.py`，数据清理、K 特征选择、训练、导出及固件同步均由它完成。
全部常用配置集中在文件顶部，用大写常量和中文注释分组。

本机的 `.venv` 和训练依赖已准备好。在 dissertation 根目录直接执行：

```bash
.venv/bin/python3 software/MLcode/train_model.py
```

在其他环境首次安装依赖时：

```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -r software/MLcode/requirements.txt
python3 software/MLcode/train_model.py
```

需要 Python 3.9 或更新版本、训练依赖和 `g++`。Windows 可使用 `python`、
`.venv\Scripts\activate`，并在 `CXX` 配置可用的 GNU C++ 编译器路径。
无编译器时可以显式关闭 `VERIFY_CPP_EXPORT`，报告会标记未执行该检查。
脚本不自动安装依赖，也不自动烧录开发板。

## 顶部配置

| 配置 | 默认值 / 作用 |
| --- | --- |
| `K` | 8 个特征 |
| `LIDAR_POINT_COUNT` | 200，必须与采集程序分箱数一致 |
| `INPUT_DIR` | dissertation/dataset，递归读取 `.txt`、`.csv`，不区分扩展名大小写 |
| `OUTPUT_DIR` | software/ML_model |
| `FIRMWARE_HEADER` | software/C_code/selfdrive/main/randomForest.h |
| `USE_FRONT_SECTOR_ONLY` | True，与当前采集程序的扇区限制一致 |
| `MAX_DISTANCE_MM` | 10000，不包含上界 |
| `CLEAN_*` | 整数检查、全零帧过滤、零值比例、文件内去重、录制标签过滤 |
| `TRAIN_LABELS` | 0–15；如需训练直行类别，加入 201 |
| `LABEL_REMAP` | 默认空；`{201: 10}` 将直行并入等效的转向指令 10 |
| `N_ESTIMATORS` / `MAX_DEPTH` | 88 / 3 |
| `TEST_SIZE` / `SPLIT_GAP_ROWS` | 0.2 / 10 |
| `VERIFY_CPP_EXPORT` / `CXX` | 默认用 g++ 编译并核对导出模型 |
| `VERIFY_TEENSY_BUILD` | 默认 False；设 True 并配置 Arduino CLI 后，在覆盖模型前检查整套固件编译 |
| `SYNC_TO_FIRMWARE` | 默认 True，验证成功后备份并同步 |

输入必须无表头，每行是 `d0,d1,...,d199,command`，共 201 列。
末列使用真实蓝牙操作指令，不能通过文件名生成类别。`255` 是开始录制标志，
不作为训练标签；`200` 在当前采集程序中会关闭录制，正常不会写入。
采集只更新索引 0–49 和 151–199，其余列为零，不因这些零删除正常行。
距离数组保留未更新的旧值，记录不是保证全部角度新鲜的完整扫描。
改变分辨率或采集扇区时，需要重新采集对应格式的数据，不能仅修改 Python 配置。

清理报告记录每个文件的列数分布、保留行数和各删除原因。选中特征中的零值默认进一步
排除，以符合固件需要有效距离输入的约定；这一阶段的删除数写入训练报告。

## 运行和输出

```bash
python3 software/MLcode/train_model.py --k 12
python3 software/MLcode/train_model.py --clean-only
python3 software/MLcode/train_model.py --no-sync
```

还可临时指定 `--input-dir`、`--output-dir`、`--firmware-header`。相对路径以
dissertation 为基准，不依赖当前工作目录。输出目录不能放在输入目录内部。

输出包括：

- `randomForest.h`：森林代码、分辨率、扇区、K、原始特征索引、类别到指令映射。
- `data_cleaned.csv`：清理后完整输入，仍是距离列加标签，无表头。
- `clean_report.json`：清理统计。
- `feature_scores.csv`：非常量候选特征的 ANOVA F 分数和选中标志，索引对应原始列。
- `training_report.json`：配置、特征、类别、划分、准确率、混淆矩阵、分类报告、转向容差准确率、导出检查及头文件 SHA-256。
- `randomForest.joblib`：最终 Python 模型及特征、类别配置。
- `backups/<UTC时间>/`：被替换的旧模型，分别保存输出目录和固件目录中的版本。

多文件按文件分组验证，单文件按时间切分并隔开若干相邻帧。特征选择仅使用训练部分；
验证后冻结特征，在全部有效数据上重训最终森林。报告指标来自验证阶段，不是最终森林
在其训练数据上的成绩。如果某类只出现在验证部分，流程报错，需补充采集或调整划分。
将不同独立采集记录保存成不同文件，避免把同一记录的复制件当作独立验证数据。

新头文件直接保存 sklearn 的叶节点类别概率，按森林平均概率预测，保留 `Eloquent::ML::Port::RandomForest`
接口。默认 C++ 检查覆盖数据样本、随机输入和树阈值边界，并核对真实指令与完整概率。
所有检查在临时目录完成，成功后才替换输出及固件模型，写入失败会恢复已替换文件。

根目录 dataset 为空时，不训练或替换模型。`randomForest.h` 和训练输出均为生成产物，
由脚本生成、备份和同步，不手动修改或提交到 Git。`ML_model/` 仅提交目录说明。
首次获取工程时，先准备数据并运行训练脚本，生成完整模型头文件后再编译固件。

验证代码：

```bash
python3 -m unittest discover -s software/MLcode -p 'test_*.py' -v
```
