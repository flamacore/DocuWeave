from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QPushButton, QFileDialog,
                           QLabel, QWidget)
from PyQt5.QtCore import Qt

class StartupDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("DocuWeave")
        self.setObjectName("startupDialog")
        self.action = None
        self.project_path = None
        
        layout = QVBoxLayout(self)
        
        welcome = QLabel("Welcome to DocuWeave")
        welcome.setStyleSheet("font-size: 24px; margin: 20px;")
        welcome.setAlignment(Qt.AlignCenter)
        layout.addWidget(welcome)
        
        new_project = QPushButton("Create New Project")
        new_project.clicked.connect(self.create_new)
        layout.addWidget(new_project)
        
        open_project = QPushButton("Open Existing Project")
        open_project.clicked.connect(self.open_existing)
        layout.addWidget(open_project)

    def create_new(self):
        self.action = "new"
        folder_path = QFileDialog.getExistingDirectory(
            self, "Select Folder for New Project", ""
        )
        if folder_path:
            self.project_path = folder_path
            self.accept()

    def open_existing(self):
        self.action = "open"
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Open Existing Project", "",
            "DocuWeave Project (*.dwproj);;All Files (*)"
        )
        if file_path:
            self.project_path = file_path
            self.accept()
