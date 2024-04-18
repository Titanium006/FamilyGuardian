import os

def get_mp4_files(directory):
    mp4_files = []
    # 获取目录中所有文件和子目录
    files = os.listdir(directory)
    # 遍历文件列表
    for file in files:
        # 构建文件的完整路径
        file_path = os.path.join(directory, file)
        # 判断是否为文件以及是否为MP4文件
        if os.path.isfile(file_path) and file.lower().endswith('.mp4'):
            # 提取文件名部分，并添加到列表中
            mp4_files.append(os.path.basename(file_path))
    return mp4_files

# 指定目录路径
directory = "D:/大三下/软工课设/HomeSurface/detect_results/20240417"

# 获取MP4文件列表
mp4_files = get_mp4_files(directory)

# 打印MP4文件列表
for mp4_file in mp4_files:
    print(mp4_file)
