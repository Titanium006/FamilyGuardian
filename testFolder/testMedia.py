import os

# 获取当前脚本文件的目录
current_dir = os.path.dirname(os.path.abspath(__file__))

# 构建相对路径
sibling_dir = os.path.join(current_dir, '..', 'media')

# 获取目标文件的路径
file_path = os.path.join(sibling_dir, 'file.txt')

# 确保路径的正确性
file_path = os.path.abspath(file_path)

# 读取文件内容
with open(file_path, 'r') as file:
    content = file.read()

print(content)
