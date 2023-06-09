from PyQt6.QtWidgets import QDialog, QDialogButtonBox, QVBoxLayout, QLabel


class Dialog(QDialog):
    def __init__(self, parent=None, msg="Something went wrong..."):
        super().__init__(parent)

        self.setWindowTitle("注意")

        QBtn = QDialogButtonBox.StandardButton.Ok

        self.buttonBox = QDialogButtonBox(QBtn)
        self.buttonBox.accepted.connect(self.accept)

        self.layout = QVBoxLayout()
        message = QLabel(msg)
        self.layout.addWidget(message)
        self.layout.addWidget(self.buttonBox)
        self.setLayout(self.layout)

