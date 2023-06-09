from PyQt6.QtCore import QThread, pyqtSignal
from numpy import ndarray

from lib.video_cv.video_handle import VideoHandle


class VideoThread(QThread):
    change_pixmap_signal = pyqtSignal(ndarray)
    image_to_infer = pyqtSignal(ndarray)
    finished = pyqtSignal()

    def run(self):
        # capture from webcam
        video_handle = VideoHandle(SETTINGS_DATA['video_source'], SETTINGS_DATA['video_path'])
        video = video_handle.get_video()
        fps = video_handle.get_fps()
        frame_interval = int(fps * SETTINGS_DATA['time_interval'])
        counter = 0
        while not SETTINGS_DATA['reset']:
            ret, cv_img = video.read()
            if ret:
                self.change_pixmap_signal.emit(cv_img)
                counter += 1
                if counter % frame_interval == 0:
                    self.image_to_infer.emit(cv_img)
                    counter = 0
        self.finished.emit()
