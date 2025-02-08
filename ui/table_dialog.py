import sys
import ctypes
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QSpinBox, QPushButton
from PyQt5.QtCore import Qt

# Enable high DPI awareness on Windows
if sys.platform == "win32":
    try:
        ctypes.windll.shcore.SetProcessDpiAwareness(1)
    except Exception:
        pass

class TableDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Insert Table")
        # Set fixed size similar to image dialog
        self.setFixedSize(600, 300)
        self.setWindowFlags(Qt.Dialog | Qt.WindowTitleHint)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # Title
        title = QLabel("Insert Table")
        title.setStyleSheet("font-size: 24px; margin-bottom: 20px;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        # Rows input
        row_layout = QHBoxLayout()
        row_label = QLabel("Number of rows:")
        row_label.setStyleSheet("font-size: 16px;")
        self.rows_spin = QSpinBox()
        self.rows_spin.setMinimum(1)
        self.rows_spin.setMaximum(50)
        self.rows_spin.setValue(3)
        self.rows_spin.setStyleSheet("font-size: 14px; height: 35px;")
        row_layout.addWidget(row_label)
        row_layout.addWidget(self.rows_spin)
        layout.addLayout(row_layout)

        # Columns input
        col_layout = QHBoxLayout()
        col_label = QLabel("Number of columns:")
        col_label.setStyleSheet("font-size: 16px;")
        self.cols_spin = QSpinBox()
        self.cols_spin.setMinimum(1)
        self.cols_spin.setMaximum(50)
        self.cols_spin.setValue(3)
        self.cols_spin.setStyleSheet("font-size: 14px; height: 35px;")
        col_layout.addWidget(col_label)
        col_layout.addWidget(self.cols_spin)
        layout.addLayout(col_layout)

        # Action buttons
        button_layout = QHBoxLayout()
        self.insert_button = QPushButton("Insert")
        self.cancel_button = QPushButton("Cancel")
        # Set button styles similar to image dialog
        for btn in (self.insert_button, self.cancel_button):
            btn.setStyleSheet("font-size: 14px;")
            btn.setFixedHeight(35)
        button_layout.addStretch()
        button_layout.addWidget(self.insert_button)
        button_layout.addWidget(self.cancel_button)
        layout.addLayout(button_layout)

        self.insert_button.clicked.connect(self.accept)
        self.cancel_button.clicked.connect(self.reject)

    def get_table_dimensions(self):
        return self.rows_spin.value(), self.cols_spin.value()