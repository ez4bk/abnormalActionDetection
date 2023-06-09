import cv2


class VideoHandle(object):

    def __init__(self, video_type, video_source):
        if video_type == 'file':
            self.video_source = str(video_source)
        elif video_type == 'webcam':
            self.video_source = int(video_source)
        elif video_type == 'url':
            self.video_source = str(video_source)
        else:
            self.video_source = None
        self.video = cv2.VideoCapture(self.video_source)
        self.fps = int(self.video.get(cv2.CAP_PROP_FPS))

    def get_availability(self):
        return self.video.isOpened()

    def get_frame(self):
        if self.video_source:
            success, image = self.video.read()
            if success:
                return success, cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            else:
                return success, None
        else:
            return False, None

    def play(self):
        while self.video.isOpened():
            # Capture each frame
            ret, frame = self.video.read()

            if ret:
                cv2.imshow('Frame', frame)

                # Press Q on keyboard to  exit
                if cv2.waitKey(25) & 0xFF == ord('q'):
                    break
            else:
                break

    def get_fps(self):
        return self.fps

    def get_video_source(self):
        return self.video_source

    def get_video(self):
        return self.video

    def __del__(self):
        if self.video_source:
            self.video.release()
            cv2.destroyAllWindows()

# i = 0
# while True:
#     try:
#         a = cv2.VideoCapture(i)
#     except:
#         print(i)
#         break
#     i += 1
# a = cv2.VideoCapture(1)
# print(a.isOpened())

# vid = cv2.VideoCapture('../../src/resources/三杀翻盘.mp4')
# print(vid.get(cv2.CAP_PROP_FPS))
# while vid.isOpened():
#     # Capture each frame
#     ret, frame = vid.read()
#
#     if ret:
#         cv2.imshow('Frame', frame)
#
#         # Press Q on keyboard to  exit
#         if cv2.waitKey(25) & 0xFF == ord('q'):
#             break
#     else:
#         break
