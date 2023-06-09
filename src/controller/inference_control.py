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

from src.view.abormalActionDetection import Ui_MainWindow


class InferenceWindow(QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):
        super(InferenceWindow, self).__init__(parent)
        self.setupUi(self)

        self.set_buttons()

    def set_buttons(self):
        self.importButtonn.clicked.connect(self.import_video)

    def import_video(self):
        path = self.open_file_selector()
        self.pathLine.setText(path)

    # def init_video(self):
    #     self.videoView.setScaledContents(True)
    #     self.videoSettingLabel.setScaledContents(True)
    #     self.v_thread = VideoThread()
    #     self.menuList.setEnabled(True)
    #     self.v_thread.change_pixmap_signal.connect(self.update_image)
    #     self.v_thread.image_to_infer.connect(self.showImage)
    #     self.v_thread.finished.connect(self.v_thread_finished)
    #     self.v_thread.start()
    #
    # def v_thread_finished(self):
    #     self.v_thread = None
    #
    # @pyqtSlot(ndarray)
    # def showImage(self, img_arr):
    #     if self.startButton.isEnabled():
    #         return
    #     img = cv2.cvtColor(img_arr, cv2.COLOR_BGR2RGB)
    #     self.current_img = Image.fromarray(img)
    #     h, w, ch = img.shape
    #     bytes_per_line = ch * w
    #     convert_to_Qt_format = QtGui.QImage(img.data, w, h, bytes_per_line, QtGui.QImage.Format.Format_RGB888)
    #     self.inputImg.setPixmap(QPixmap.fromImage(convert_to_Qt_format))
    #     if not self.startButton.isEnabled():
    #         while not self.start_inference():
    #             pass
    #
    # @pyqtSlot(ndarray)
    # def update_image(self, cv_img):
    #     """Updates the image_label with a new opencv image"""
    #     qt_img = self.convert_cv_qt(cv_img)
    #     self.videoView.setPixmap(qt_img)
    #     self.videoSettingLabel.setPixmap(qt_img)
    #
    # @staticmethod
    # def convert_cv_qt(cv_img):
    #     """Convert from an opencv image to QPixmap"""
    #     rgb_image = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)
    #     h, w, ch = rgb_image.shape
    #     bytes_per_line = ch * w
    #     convert_to_Qt_format = QtGui.QImage(rgb_image.data, w, h, bytes_per_line, QtGui.QImage.Format.Format_RGB888)
    #     # p = convert_to_Qt_format.scaled(self.disply_width, self.display_height, Qt.KeepAspectRatio)
    #     return QPixmap.fromImage(convert_to_Qt_format)
    #
    # def start_inference(self):
    #     if not self.current_img:
    #         return False
    #     if not self.inferences.start_inference(self.current_img, self.stop_condition):
    #         self.set_stop_button()
    #     res_img = self.inferences.get_res_img_arr()
    #     h, w, ch = res_img.shape
    #     bytes_per_line = ch * w
    #     convert_to_Qt_format = QtGui.QImage(res_img.data, w, h, bytes_per_line, QtGui.QImage.Format.Format_RGB888)
    #     self.resultImg.setPixmap(QPixmap.fromImage(convert_to_Qt_format))
    #     self.update_table()
    #     return True
    #
    # def update_table(self):
    #     self.tableWidget.setRowCount(0)
    #     for _ in self.inferences.results_to_list():
    #         rowPos = self.tableWidget.rowCount()
    #         self.tableWidget.insertRow(rowPos)
    #         self.tableWidget.setItem(rowPos, 0, QTableWidgetItem(str(_[0])))
    #         self.tableWidget.setItem(rowPos, 1, QTableWidgetItem(str(_[1])))
    #         self.tableWidget.setItem(rowPos, 2, QTableWidgetItem(str(_[2])))

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