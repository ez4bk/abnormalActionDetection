import cv2
import torch
from PyQt6.QtCore import QThread, pyqtSignal
from numpy import ndarray
from ultralytics import YOLO
import torch.cuda as cuda


class YoloSupThread(QThread):
    change_pixmap_signal = pyqtSignal(ndarray)
    output_img = pyqtSignal(ndarray)
    finished = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__()
        self.parent = parent

    def run(self):
        if self.parent.ml_type == 0:
            model = YOLO('yolov8n_unsup.pt')
        elif self.parent.ml_type == 2:
            model = YOLO('yolov8n_sup.pt')
        else:
            self.finished.emit()
        names = model.names
        device = 0 if cuda.is_available() else 'mps' if torch.backends.mps.is_available() else 'cpu'
        cap = cv2.VideoCapture(self.parent.video_path)
        abnormal_behaviors = ['a', 'b']

        while cap.isOpened():
            success, frame = cap.read()
            if success:
                results = model(frame, conf=0.7, device=device)
                annotated_frame = results[0].plot()
                self.change_pixmap_signal.emit(annotated_frame)
                for res in results:
                    for cls in res.boxes.cls:
                        if names[int(cls)] in abnormal_behaviors:
                            self.output_img.emit(frame)
                            break
        self.finished.emit()
