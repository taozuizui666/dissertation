# 模型输出

运行 `../MLcode/train_model.py` 后，清理数据、特征评分、评估报告、Python 模型及
`randomForest.h` 生成到这里，头文件自动同步到 `../C_code/selfdrive/main/`。
配置和操作说明见 [MLcode/README.md](../MLcode/README.md)。

本目录中的模型、清理数据和评估报告均为生成产物，由脚本管理，不手动修改或提交到 Git。
此目录只提交 README。固件目录中的 `randomForest.h` 同样由训练脚本生成和同步。
