from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QPushButton, 
                           QLineEdit, QLabel, QFileDialog, QRadioButton, 
                           QButtonGroup, QWidget)
from PyQt5.QtCore import Qt

class ImageDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("imageDialog")  # Set object name for QSS styling
        self.setWindowTitle("Insert Image")
        self.setFixedSize(600, 300)  # Increased size
        # Change window flags to standard dialog flags instead of frameless
        self.setWindowFlags(Qt.Dialog | Qt.WindowTitleHint)
        self.mode = "file"  # Default mode
        self.file_path = ""
        self.url = ""
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Welcome text
        title = QLabel("Insert Image")
        title.setStyleSheet("font-size: 24px; margin-bottom: 20px;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # Radio buttons for mode selection
        radio_group = QHBoxLayout()
        self.file_radio = QRadioButton("Upload File")
        self.url_radio = QRadioButton("Image URL")
        self.file_radio.setChecked(True)
        radio_group.addWidget(self.file_radio)
        radio_group.addWidget(self.url_radio)
        layout.addLayout(radio_group)
        
        # Set font size for radio buttons
        for radio in (self.file_radio, self.url_radio):
            radio.setStyleSheet("font-size: 16px;")
        
        # File selection
        self.file_widget = QWidget()
        file_layout = QHBoxLayout(self.file_widget)
        self.file_path_edit = QLineEdit()
        self.file_path_edit.setPlaceholderText("Select an image file...")  # Fixed method name
        self.browse_button = QPushButton("Browse")
        self.browse_button.clicked.connect(self.browse_file)
        file_layout.addWidget(self.file_path_edit)
        file_layout.addWidget(self.browse_button)
        layout.addWidget(self.file_widget)
        
        # URL input
        self.url_widget = QWidget()
        url_layout = QHBoxLayout(self.url_widget)
        self.url_edit = QLineEdit()
        self.url_edit.setPlaceholderText("Enter image URL...")  # Fixed method name
        url_layout.addWidget(self.url_edit)
        layout.addWidget(self.url_widget)
        self.url_widget.hide()
        
        # Set font size and height for line edits
        for edit in (self.file_path_edit, self.url_edit):
            edit.setStyleSheet("font-size: 14px;")
            edit.setFixedHeight(35)
        
        # Connect radio buttons
        self.file_radio.toggled.connect(self.toggle_mode)
        
        # Buttons
        buttons = QHBoxLayout()
        self.ok_button = QPushButton("Insert")
        self.cancel_button = QPushButton("Cancel")
        self.ok_button.clicked.connect(self.accept)
        self.cancel_button.clicked.connect(self.reject)
        buttons.addWidget(self.ok_button)
        buttons.addWidget(self.cancel_button)
        layout.addLayout(buttons)
        
        # Set size for buttons
        for btn in (self.browse_button, self.ok_button, self.cancel_button):
            btn.setFixedHeight(35)
            btn.setStyleSheet("font-size: 14px;")
        
        # Add stretch before buttons to push them to bottom
        layout.addStretch()
        
        # Set margins for button layout
        buttons.setContentsMargins(0, 20, 0, 0)

    def toggle_mode(self, checked):
        if checked:
            self.mode = "file"
            self.file_widget.show()
            self.url_widget.hide()
        else:
            self.mode = "url"
            self.file_widget.hide()
            self.url_widget.show()

    def browse_file(self):
        file_name, _ = QFileDialog.getOpenFileName(
            self, "Select Image", "", 
            "Images (*.png *.jpg *.jpeg *.gif *.webp);;All Files (*)"
        )
        if file_name:
            self.file_path = file_name
            self.file_path_edit.setText(file_name)

    def accept(self):
        if self.mode == "file":
            self.file_path = self.file_path_edit.text()
            if not self.file_path:
                return
        else:
            self.url = self.url_edit.text()
            if not self.url:
                return
        super().accept()
