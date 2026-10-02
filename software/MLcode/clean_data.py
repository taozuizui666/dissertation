import re

# ==============================
# 可配置参数
# ==============================

import shutil

out = open('D:\data_large.txt', 'wb')
begin=8
end=18

for i in range(begin, end + 1):
    with open(f'DATA-{i}.TXT', 'rb') as f:
        shutil.copyfileobj(f, out)

out.close()

N = 150                          # 例如原数据应当有 N+1 列
input_path = r"D:\data_large.txt"      # 原始文件
output_path = r"D:\data_cleaned.txt"
encoding = "latin1"              # 保证能读任何字符，不报错
# ==============================


def is_number(s):
    """
    判断字符串 s 是否为合法数字：
    - 整数
    - 浮点数
    - 负数
    """
    s = s.strip()
    if s == "":
        return False
    # 合法数字格式：-12, 12.5, -3.14
    return bool(re.fullmatch(r"-?\d+(\.\d+)?", s))


cleaned_lines = []

with open(input_path, "r", encoding=encoding, errors="replace") as f:
    for line in f:
        line = line.strip()

        # 按逗号分割
        parts = line.split(",")

        # 检查字段数量是否正确（必须 N+1 个）
        if len(parts) != N + 1:
            continue  # 丢弃该行

        # 检查每个字段是否为数字
        if not all(is_number(p) for p in parts):
            continue  # 任何非数字 → 丢弃该行

        # 行合格 → 保存
        cleaned_lines.append(line + "\n")

# 写入新文件
with open(output_path, "w", encoding="utf-8") as f:
    f.writelines(cleaned_lines)

print(f"完成！共保留 {len(cleaned_lines)} 行有效数据。")
print(f"清洗后的文件已保存为：{output_path}")
