import sys
import ctypes
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QRadioButton, QButtonGroup
from PyQt5.QtCore import Qt

# Enable high DPI awareness on Windows
if sys.platform == "win32":
    try:
        ctypes.windll.shcore.SetProcessDpiAwareness(1)
    except Exception:
        pass

class LinkTypeDialog(QDialog):
    """Dialog for selecting between external and internal links"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Insert Link")
        # Set fixed size similar to table dialog
        self.setFixedSize(600, 300)
        self.setWindowFlags(Qt.Dialog | Qt.WindowTitleHint)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Title
        title = QLabel("Insert Link")
        title.setStyleSheet("font-size: 24px; margin-bottom: 20px;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # Instructions
        instructions = QLabel("Select link type:")
        instructions.setStyleSheet("font-size: 16px;")
        layout.addWidget(instructions)
        
        # Radio button group
        self.radio_group = QButtonGroup(self)
        
        # External URL option
        external_radio = QRadioButton("External URL")
        external_radio.setChecked(True)  # Default selection
        external_radio.setStyleSheet("font-size: 14px;")
        self.radio_group.addButton(external_radio, 0)
        layout.addWidget(external_radio)
        
        # Description for external URL
        external_desc = QLabel("   Link to a website or external resource")
        external_desc.setStyleSheet("font-size: 14px; color: #888;")
        layout.addWidget(external_desc)
        
        # Add some spacing
        spacer = QLabel("")
        spacer.setFixedHeight(10)
        layout.addWidget(spacer)
        
        # Internal document option
        internal_radio = QRadioButton("Internal Document")
        internal_radio.setStyleSheet("font-size: 14px;")
        self.radio_group.addButton(internal_radio, 1)
        layout.addWidget(internal_radio)
        
        # Description for internal document
        internal_desc = QLabel("   Link to another document within this project")
        internal_desc.setStyleSheet("font-size: 14px; color: #888;")
        layout.addWidget(internal_desc)
        
        layout.addStretch(1)  # Push buttons to bottom
        
        # Action buttons
        button_layout = QHBoxLayout()
        self.ok_button = QPushButton("OK")
        self.cancel_button = QPushButton("Cancel")
        
        # Set button styles similar to other dialogs
        for btn in (self.ok_button, self.cancel_button):
            btn.setStyleSheet("font-size: 14px;")
            btn.setFixedHeight(35)
            
        button_layout.addStretch()
        button_layout.addWidget(self.ok_button)
        button_layout.addWidget(self.cancel_button)
        layout.addLayout(button_layout)
        
        self.ok_button.clicked.connect(self.accept)
        self.cancel_button.clicked.connect(self.reject)
    
    def get_selected_type(self):
        """Return the selected link type"""
        return "external" if self.radio_group.checkedId() == 0 else "internal"