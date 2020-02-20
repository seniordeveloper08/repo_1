
# import module
import cv2
import datetime
  
# create video capture object
data = cv2.VideoCapture('../share/9/videos/output15.ts')
  
# count the number of frames
frames = data.get(cv2.CAP_PROP_FRAME_COUNT)
fps = data.get(cv2.CAP_PROP_FPS)
  
# calculate duration of the video
seconds = round(frames / fps)
video_time = datetime.timedelta(seconds=seconds)
print(f"duration in seconds: {seconds}")
print(f"video time: {video_time}")