from PyQt5.QtWidgets import QDialog, QVBoxLayout, QPushButton, QLabel
from PyQt5.QtCore import Qt

class StartupDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Welcome to DocuWeave")
        self.setObjectName("startupDialog")
        self.setFixedSize(400, 200)
        self.action = None
        
        layout = QVBoxLayout(self)
        
        # Welcome text
        welcome = QLabel("Welcome to DocuWeave")
        welcome.setStyleSheet("font-size: 24px; margin-bottom: 20px;")
        welcome.setAlignment(Qt.AlignCenter)
        layout.addWidget(welcome)
        
        # Create new project button
        new_project = QPushButton("Create New Project")
        new_project.clicked.connect(self.create_new)
        new_project.setFixedHeight(40)
        layout.addWidget(new_project)
        
        # Open existing project button
        open_project = QPushButton("Open Existing Project")
        open_project.clicked.connect(self.open_existing)
        open_project.setFixedHeight(40)
        layout.addWidget(open_project)
        
        layout.addStretch()

    def create_new(self):
        self.action = "new"
        self.accept()

    def open_existing(self):
        self.action = "open"
        self.accept()
