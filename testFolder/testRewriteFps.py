import cv2

# 读取视频文件
video_path = 'input_video.mp4'
cap = cv2.VideoCapture(video_path)

# 获取视频信息
fps = cap.get(cv2.CAP_PROP_FPS)
frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

# # 创建视频写入对象
output_video_path = 'output_video.avi'
# fourcc = cv2.VideoWriter_fourcc(*'XVID')
# out = cv2.VideoWriter(output_video_path, fourcc, fps, (frame_width, frame_height))
#
# # 逐帧读取视频并保存
# while cap.isOpened():
#     ret, frame = cap.read()
#     if ret:
#         # 在这里可以对每一帧进行处理，例如修改图像大小、颜色转换等
#         # 这里仅仅是简单地写入原始帧
#         out.write(frame)
#     else:
#         break
#
# # 释放资源
# cap.release()
# out.release()

# 重新读取视频并修改帧率
new_fps = 30  # 新的帧率
cap = cv2.VideoCapture(output_video_path)

# 创建新的视频写入对象
new_output_video_path = 'new_output_video.avi'
new_out = cv2.VideoWriter(new_output_video_path, fourcc, new_fps, (frame_width, frame_height))

# 逐帧读取视频并保存（同时修改帧率）
while cap.isOpened():
    ret, frame = cap.read()
    if ret:
        # 在这里可以对每一帧进行处理
        new_out.write(frame)
    else:
        break

# 释放资源
cap.release()
new_out.release()
