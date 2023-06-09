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

from config import SETTINGS_DATA, JSON_DIR
from lib.export_excel.export_to_excel import ExportToExcel
from lib.video_cv.video_thread import VideoThread
from src.controller.dialog_control import Dialog
from src.view.inference_view_window import Ui_InferenceWindow
from src.model.res_wrapper import ResWrapper


class InferenceWindow(QMainWindow, Ui_InferenceWindow):
    def __init__(self, parent=None):
        super(InferenceWindow, self).__init__(parent)
        self.setupUi(self)
        self.start_x = None
        self.start_y = None
        self.v_thread = None
        self.setWindowFlags(QtCore.Qt.WindowType.FramelessWindowHint)
        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_TranslucentBackground)

        self.inferences = ResWrapper()
        self.current_img = None
        self.device_max_index = -1
        self.export_path = ''
        self.stop_condition = ''

        self.set_buttons()
        # self.init_devices()
        # self.init_video()
        self.init_stop_condition()
        self.init_setting_lines()

    def init_stop_condition(self):
        cats = self.inferences.get_all_cats()
        cats.sort()
        for _ in cats:
            self.stopCondComboBox.addItem(str(_))

    def init_setting_lines(self):
        self.timeIntervalLine.setText(str(SETTINGS_DATA['time_interval']))
        self.inferenceLine.setText(str(SETTINGS_DATA['confidence']))
        self.stop_condition = SETTINGS_DATA['stop_condition']
        self.export_path = SETTINGS_DATA['export_path']
        self.resultExportLine.setText(self.export_path)
        self.resultExportLine.setReadOnly(True)
        self.resultExportLine.setToolTip(self.export_path)

    def init_devices(self):
        account = SETTINGS_DATA['account']
        password = SETTINGS_DATA['password']
        ip = SETTINGS_DATA['ip']
        port = SETTINGS_DATA['port']

        if ip == '' or ip is None:
            dialog = Dialog(msg="摄像头地址为空")
            dialog.exec()
            self.stackedWidget.setCurrentIndex(1)
        else:
            self.deviceLine.setText(ip)
            video_path = f"rtsp://{account}:{password}@{ip}:{port}/ch1/main/av_stream"
            self.deviceLine.setEnabled(False)
            temp = cv2.VideoCapture(video_path)
            if not temp.isOpened():
                dialog = Dialog(msg="摄像头地址错误")
                dialog.exec()
                temp.release()
            else:
                SETTINGS_DATA['video_path'] = video_path
                self.write_to_json()
            self.deviceLine.setEnabled(True)

    def init_video(self):
        self.videoView.setScaledContents(True)
        self.videoSettingLabel.setScaledContents(True)
        self.v_thread = VideoThread()
        self.menuList.setEnabled(True)
        self.v_thread.change_pixmap_signal.connect(self.update_image)
        self.v_thread.image_to_infer.connect(self.showImage)
        self.v_thread.finished.connect(self.v_thread_finished)
        self.v_thread.start()

    def v_thread_finished(self):
        self.v_thread = None
        SETTINGS_DATA['reset'] = False
        self.write_to_json()

    @pyqtSlot(ndarray)
    def showImage(self, img_arr):
        if self.startButton.isEnabled():
            return
        img = cv2.cvtColor(img_arr, cv2.COLOR_BGR2RGB)
        self.current_img = Image.fromarray(img)
        h, w, ch = img.shape
        bytes_per_line = ch * w
        convert_to_Qt_format = QtGui.QImage(img.data, w, h, bytes_per_line, QtGui.QImage.Format.Format_RGB888)
        self.inputImg.setPixmap(QPixmap.fromImage(convert_to_Qt_format))
        if not self.startButton.isEnabled():
            while not self.start_inference():
                pass

    @pyqtSlot(ndarray)
    def update_image(self, cv_img):
        """Updates the image_label with a new opencv image"""
        qt_img = self.convert_cv_qt(cv_img)
        self.videoView.setPixmap(qt_img)
        self.videoSettingLabel.setPixmap(qt_img)

    @staticmethod
    def convert_cv_qt(cv_img):
        """Convert from an opencv image to QPixmap"""
        rgb_image = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_image.shape
        bytes_per_line = ch * w
        convert_to_Qt_format = QtGui.QImage(rgb_image.data, w, h, bytes_per_line, QtGui.QImage.Format.Format_RGB888)
        # p = convert_to_Qt_format.scaled(self.disply_width, self.display_height, Qt.KeepAspectRatio)
        return QPixmap.fromImage(convert_to_Qt_format)

    def set_buttons(self):
        self.stopButton.setEnabled(False)
        self.menuList.itemClicked.connect(lambda: self.menu_set_widgets(self.menuList.currentItem().text()))
        self.importButton.clicked.connect(lambda: self.set_inputImg())
        self.startButton.clicked.connect(lambda: self.set_start_button())
        self.stopButton.clicked.connect(lambda: self.set_stop_button())
        self.exitButton.clicked.connect(lambda: sys.exit())
        self.inferenceButton.clicked.connect(lambda: self.set_inference())
        self.inferenceLine.textChanged.connect(lambda: self.inference_line_check())
        self.timeIntervalButton.clicked.connect(lambda: self.set_time_interval())
        self.timeIntervalLine.textChanged.connect(lambda: self.time_interval_line_check())
        self.resultExportFile.clicked.connect(lambda: self.set_export_button())
        self.deviceButton.clicked.connect(lambda: self.set_device())
        self.deviceLine.textChanged.connect(lambda: self.device_line_check())
        self.stopCondComboBox.currentIndexChanged.connect(lambda: self.set_stop_condition())

    def set_stop_condition(self):
        SETTINGS_DATA['stop_condition'] = self.stopCondComboBox.currentText()
        self.stop_condition = SETTINGS_DATA['stop_condition']
        self.write_to_json()

    def set_stop_button(self):
        self.stopButton.setEnabled(False)
        self.menuList.setEnabled(True)
        self.importButton.setEnabled(True)
        self.startButton.setEnabled(True)
        SETTINGS_DATA['reset'] = True
        self.write_to_json()
        self.init_video()

    def set_device(self):
        new_ip = self.deviceLine.text()
        SETTINGS_DATA['reset'] = True
        SETTINGS_DATA['ip'] = new_ip
        self.write_to_json()
        self.init_devices()
        self.init_video()

    def set_start_button(self):
        self.startButton.setEnabled(False)
        self.menuList.setEnabled(False)
        self.importButton.setEnabled(False)
        self.stopButton.setEnabled(True)

    def set_inference(self):
        new_conf = self.inferenceLine.text()
        SETTINGS_DATA["confidence"] = float(new_conf)
        self.write_to_json()

    def inference_line_check(self):
        temp = self.inferenceLine.text()
        try:
            float(temp)
            self.inferenceButton.setEnabled(True)
            return True
        except ValueError:
            self.inferenceButton.setEnabled(False)
            return False

    def time_interval_line_check(self):
        temp = self.timeIntervalLine.text()
        try:
            int(temp)
            self.timeIntervalButton.setEnabled(True)
            return True
        except ValueError:
            self.timeIntervalButton.setEnabled(False)
            return False

    def set_time_interval(self):
        new_time = self.timeIntervalLine.text()
        SETTINGS_DATA["time_interval"] = int(new_time)
        SETTINGS_DATA['reset'] = True
        self.write_to_json()
        self.init_video()

    def set_export_button(self):
        self.export_path = os.path.join(self.open_file_selector('dir'), '')
        self.resultExportLine.setText(self.export_path)
        SETTINGS_DATA['export_path'] = self.export_path
        self.write_to_json()

    @staticmethod
    def write_to_json():
        with open(JSON_DIR, 'w') as f:
            json.dump(SETTINGS_DATA, f, indent=4)

    def menu_set_widgets(self, item_name):
        if item_name == "主页":
            self.stackedWidget.setCurrentIndex(0)
        elif item_name == "设置":
            self.stackedWidget.setCurrentIndex(1)
        elif item_name == "控制台输出":
            self.stackedWidget.setCurrentIndex(2)
        elif item_name == "结果导出":
            if self.export_path is None or self.export_path == "":
                dialog = Dialog(self, "请先设置导出路径")
                dialog.exec()
            else:
                filename = self.set_export_filename(self.export_path, 'result.xlsx')
                export = ExportToExcel(self.inferences.results_to_list(), filename)
                if export.export():
                    dialog = Dialog(self, "导出成功")
                    dialog.exec()
                else:
                    dialog = Dialog(self, "导出失败：无数据")
                    dialog.exec()

    @staticmethod
    def set_export_filename(path, name):
        filename = os.path.join(path, name)
        while os.path.exists(filename):
            name_temp = name.split('.')
            if len(name_temp[0].split('_')) > 1:
                temp = name_temp[0].split('_')
                temp[-1] = str(int(temp[-1]) + 1)
                name_temp[0] = '_'.join(temp)
            else:
                name_temp[0] = name_temp[0] + '_1'
            name = '.'.join(name_temp)
            filename = os.path.join(path, name)
        return filename

    def start_inference(self):
        if not self.current_img:
            return False
        if not self.inferences.start_inference(self.current_img, self.stop_condition):
            self.set_stop_button()
        res_img = self.inferences.get_res_img_arr()
        h, w, ch = res_img.shape
        bytes_per_line = ch * w
        convert_to_Qt_format = QtGui.QImage(res_img.data, w, h, bytes_per_line, QtGui.QImage.Format.Format_RGB888)
        self.resultImg.setPixmap(QPixmap.fromImage(convert_to_Qt_format))
        self.update_table()
        return True

    def update_table(self):
        self.tableWidget.setRowCount(0)
        for _ in self.inferences.results_to_list():
            rowPos = self.tableWidget.rowCount()
            self.tableWidget.insertRow(rowPos)
            self.tableWidget.setItem(rowPos, 0, QTableWidgetItem(str(_[0])))
            self.tableWidget.setItem(rowPos, 1, QTableWidgetItem(str(_[1])))
            self.tableWidget.setItem(rowPos, 2, QTableWidgetItem(str(_[2])))

    def set_inputImg(self):
        _ = self.open_file_selector()
        if not _:
            return
        try:
            pixmap = QPixmap(_)
        except PIL.UnidentifiedImageError:
            dialog = Dialog(self, "无法识别的图片格式")
            dialog.exec()
            return
        self.current_img = _
        self.inputImg.setPixmap(pixmap)
        self.inputImg.setScaledContents(True)
        while not self.start_inference():
            pass

    def open_file_selector(self, mode="file"):
        dialog = QFileDialog(self)
        if mode == "file":
            dialog.setFileMode(QFileDialog.FileMode.ExistingFile)
        elif mode == "dir":
            dialog.setFileMode(QFileDialog.FileMode.Directory)
        dialog.setViewMode(QFileDialog.ViewMode.List)
        filenames = None
        if dialog.exec():
            filenames = dialog.selectedFiles()
        if filenames is None:
            return None
        else:
            return QDir.toNativeSeparators(filenames[0])

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.MouseButton.LeftButton:
            super(InferenceWindow, self).mousePressEvent(event)
            self.start_x = event.pos().x()
            self.start_y = event.pos().y()

    def mouseReleaseEvent(self, event):
        self.start_x = None
        self.start_y = None

    def mouseMoveEvent(self, event):
        try:
            super(InferenceWindow, self).mouseMoveEvent(event)
            dis_x = event.pos().x() - self.start_x
            dis_y = event.pos().y() - self.start_y
            self.move(self.x() + dis_x, self.y() + dis_y)
        except:
            pass

    def device_line_check(self):
        temp = self.deviceLine.text()
        # check if temp is in the format of an ip address
        try:
            ipaddress.ip_address(temp)
            self.deviceButton.setEnabled(True)
        except ValueError:
            self.deviceButton.setEnabled(False)
