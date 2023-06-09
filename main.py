import sys

from PyQt6.QtWidgets import QApplication

from src.controller.inference_control import InferenceWindow

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = InferenceWindow()
    window.show()
    sys.exit(app.exec())
