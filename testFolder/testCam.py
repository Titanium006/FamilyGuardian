import cv2

# 打开摄像头
cap = cv2.VideoCapture(0)  # 参数 0 表示第一个摄像头，如果有多个摄像头可以更改参数来选择

# 检查摄像头是否成功打开
if not cap.isOpened():
    print("Error: 无法打开摄像头")
    exit()

# 不断读取摄像头数据
while True:
    # 读取一帧图像
    ret, frame = cap.read()

    # 检查是否成功读取帧
    if not ret:
        print("Error: 无法读取帧")
        break
    print(type(frame))
    # 在窗口中显示图像
    cv2.imshow('Camera', frame)

    # 按下 'q' 键退出循环
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# 关闭摄像头和窗口
cap.release()
cv2.destroyAllWindows()
