

def clickedSlider(position):
    if 3600 > 0:
        # 计算视频当前播放的时间位置（以秒为单位）
        video_position = int((position / 100) * 3600)

        # 将视频当前播放的时间位置转换为时间格式（小时:分钟:秒）
        hours, remainder = divmod(video_position, 3600)
        minutes, seconds = divmod(remainder, 60)
        time_format = "%02d:%02d:%02d" % (hours, minutes, seconds)

        # 设置 lab_video 的文本为时间格式
        print(time_format)
    else:
        print(0)


clickedSlider(position=50)
