# **dissertation**

*a self-driving car project based on AI model*

author ： TAO RAN

## 数据训练与模型部署

将采集的操作记录放进根目录 `dataset/`，每行应为 200 个雷达距离加一个操作标签。
唯一运行入口为 `software/MLcode/train_model.py`，完成清理、K 特征选择、训练、导出和同步。
K、雷达点数、路径及清理参数集中在脚本顶部。

```bash
.venv/bin/python3 software/MLcode/train_model.py
```

成功后生成 `software/ML_model/randomForest.h` 并备份、同步到
`software/C_code/selfdrive/main/randomForest.h`，打开对应 `main.ino` 编译上传。
模型头文件和训练输出属于生成产物，不手动修改，也不提交到 Git。
首次获取工程时，需要先准备数据并运行训练脚本，生成模型后再编译固件。
本机 `.venv` 已准备好；默认需要 `g++` 校验导出模型。
其他环境的安装和配置详见 [训练说明](software/MLcode/README.md)。
