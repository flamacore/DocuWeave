import sys
import ctypes
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton
from PyQt5.QtCore import Qt
from ui.scale import px, scaled_css

# Enable high DPI awareness on Windows
if sys.platform == "win32":
    try:
        ctypes.windll.shcore.SetProcessDpiAwareness(1)
    except Exception:
        pass

class ExternalLinkDialog(QDialog):
    """Dialog for entering an external URL"""
    
    def __init__(self, parent=None, initial_url=""):
        super().__init__(parent)
        self.setWindowTitle("External Link")
        # Set fixed size similar to table dialog
        self.setFixedSize(px(600), px(300))
        self.setWindowFlags(Qt.Dialog | Qt.WindowTitleHint)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Title
        title = QLabel("External Link")
        title.setStyleSheet(scaled_css("font-size: 24px; margin-bottom: 20px;"))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # Instructions
        instructions = QLabel("Enter URL:")
        instructions.setStyleSheet(scaled_css("font-size: 16px;"))
        layout.addWidget(instructions)
        
        # URL input field
        self.url_input = QLineEdit(initial_url)
        self.url_input.setStyleSheet(scaled_css("font-size: 14px; height: 35px; padding: 0 10px;"))
        self.url_input.setPlaceholderText("https://example.com")
        layout.addWidget(self.url_input)
        
        # Help text
        help_text = QLabel("URLs will automatically have 'http://' added if not specified.")
        help_text.setStyleSheet(scaled_css("font-size: 14px; color: #888;"))
        layout.addWidget(help_text)
        
        layout.addStretch(1)  # Push buttons to bottom
        
        # Action buttons
        button_layout = QHBoxLayout()
        self.ok_button = QPushButton("OK")
        self.cancel_button = QPushButton("Cancel")
        
        # Set button styles similar to other dialogs
        for btn in (self.ok_button, self.cancel_button):
            btn.setStyleSheet(scaled_css("font-size: 14px;"))
            btn.setFixedHeight(px(35))
            
        button_layout.addStretch()
        button_layout.addWidget(self.ok_button)
        button_layout.addWidget(self.cancel_button)
        layout.addLayout(button_layout)
        
        self.ok_button.clicked.connect(self.accept)
        self.cancel_button.clicked.connect(self.reject)
        
        # Set focus to URL input
        self.url_input.setFocus()
    
    def get_url(self):
        """Return the entered URL, ensuring it has http:// prefix if not specified"""
        url = self.url_input.text().strip()
        if url and not url.startswith(('http://', 'https://')):
            url = 'http://' + url
        return url