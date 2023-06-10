import ipaddress
import json
import os
import sys

import PIL
import cv2
from PIL import Image
from PyQt6 import QtCore, QtGui
from PyQt6.QtCore import pyqtSlot, QDir
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import QMainWindow, QFileDialog, QTableWidgetItem
from numpy import ndarray
from ultralytics import YOLO
import torch.cuda as cuda

from src.view.abormalActionDetection import Ui_MainWindow
from lib.yolo_sup_thread import YoloSupThread as YoloSup


class InferenceWindow(QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):
        super(InferenceWindow, self).__init__(parent)
        self.setupUi(self)
        self.set_buttons()

        self.thread = None
        self.video_path = None
        self.ml_type = self.comboBox.currentIndex()

    def set_buttons(self):
        self.importButtonn.clicked.connect(self.import_video)
        self.startButton.clicked.connect(self.start_inference)
        self.comboBox.currentIndexChanged.connect(self.change_ml_type)

    def import_video(self):
        self.video_path = self.open_file_selector()
        self.pathLine.setText(self.video_path)

    def start_inference(self):
        if not self.video_path:
            return
        if self.ml_type == 1:
            pass
        else:
            self.yolo_inference()

    def change_ml_type(self):
        self.ml_type = self.comboBox.currentIndex()

    def yolo_inference(self):
        self.thread = YoloSup(self)
        self.startButton.setEnabled(False)
        self.thread.change_pixmap_signal.connect(self.update_image)
        self.thread.output_img.connect(self.showOutput)
        self.thread.finished.connect(self.thread_finished)
        self.thread.start()

    @pyqtSlot(ndarray)
    def update_image(self, img_arr):
        self.video.setPixmap(self.convert_cv_qt(img_arr).scaled(self.video.width(), self.video.height()))

    @pyqtSlot(ndarray)
    def showOutput(self, img_arr):
        self.thread = None
        self.startButton.setEnabled(True)
        self.video.setPixmap(self.convert_cv_qt(img_arr).scaled(self.video.width(), self.video.height()))

    def thread_finished(self):
        self.thread = None
        self.startButton.setEnabled(True)

    @staticmethod
    def convert_cv_qt(cv_img):
        """Convert from an opencv image to QPixmap"""
        rgb_image = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_image.shape
        bytes_per_line = ch * w
        convert_to_Qt_format = QtGui.QImage(rgb_image.data, w, h, bytes_per_line, QtGui.QImage.Format.Format_RGB888)
        # p = convert_to_Qt_format.scaled(self.disply_width, self.display_height, Qt.KeepAspectRatio)
        return QPixmap.fromImage(convert_to_Qt_format)

    def open_file_selector(self):
        from pathlib import Path
        caption = "Select Video"
        file_filter = "Video Files (*.mp4 *.avi *.mkv *.asf *.gif *.m4v *.mov *.mpeg *.mpg *.ts *.wmv *.webm)"
        dialog = QFileDialog(self, caption, str(Path.home()), file_filter)
        dialog.setFileMode(QFileDialog.FileMode.ExistingFile)
        dialog.setViewMode(QFileDialog.ViewMode.List)
        filenames = None
        if dialog.exec():
            filenames = dialog.selectedFiles()
        if filenames is None:
            return None
        else:
            return QDir.toNativeSeparators(filenames[0])