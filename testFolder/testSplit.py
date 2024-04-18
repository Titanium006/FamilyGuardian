# import re
#
#
# def extract_timestamps_cameraNumber(filename):
#     # 定义日期时间格式的正则表达式模式
#     pattern = r'\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2}'
#     # 在文件名中搜索匹配的日期时间字符串
#     timestamps = re.findall(pattern, filename)
#     parts = filename.split('_')
#     camereNumber = parts[-1].split('.')[0]
#     return timestamps, camereNumber
#
#
# # 示例文件名
# filename = "2024-04-17_23-34-42_2024-04-17_23-35-09_0.mp4"
#
# # 提取时间戳
# timestamps, cameraNumber = extract_timestamps_cameraNumber(filename)
#
# # 打印结果
# for timestamp in timestamps:
#     print("时间戳:", timestamp)
# print(cameraNumber)

# 这里进来的是单个时间戳
def transform_timestamp(timestamp):
    stamplist = timestamp.split('_')
    # 将时间戳中的 '_' 替换为 ' '，将 '-' 替换为 ':'，得到新的格式
    transformed_timestamp = stamplist[-1].replace('-', ':')
    timestamp_new = stamplist[0] + ' ' + transformed_timestamp
    return timestamp_new

# 示例时间戳
timestamp = "2024-04-17_23-34-42"

# 转换时间戳格式
transformed_timestamp = transform_timestamp(timestamp)

# 打印结果
print("转换后的时间戳:", transformed_timestamp)
