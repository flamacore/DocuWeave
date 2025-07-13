import sys
from PyQt5.QtWidgets import QDialog, QGridLayout, QPushButton
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtGui import QPixmap, QIcon  # Added QIcon import
import requests

class EmojiSelector(QDialog):
    emojiSelected = pyqtSignal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Select Emoji")
        self.setMinimumSize(300, 200)
        layout = QGridLayout(self)
        
        # List of emoji codes (using Twemoji codes)
        emojis = [
            "1f600",  # grinning face
            "1f601",  # beaming face
            "1f602",  # tearing up laughing
            "1f603",  # smiling face
            "1f604",  # smiling face with open mouth
            "1f605",  # anxious face with sweat
            "1f606",  # smiling face with closed eyes
            "1f923"   # rolling on the floor laughing
        ]
        base_url = "https://twemoji.maxcdn.com/v/latest/72x72/"
        row, col = 0, 0
        for code in emojis:
            url = f"{base_url}{code}.png"
            btn = QPushButton()
            btn.setFlat(True)
            btn.setFixedSize(60, 60)  # Ensure button is visible even if icon fails to load
            pixmap = QPixmap()
            try:
                resp = requests.get(url)
                pixmap.loadFromData(resp.content)
            except Exception:
                pass  # In production handle errors accordingly
            if pixmap.isNull():
                btn.setText(code)  # Fallback if image fails
            else:
                btn.setIcon(QIcon(pixmap))
                btn.setIconSize(pixmap.size())
            btn.clicked.connect(lambda checked, url=url: self.select_emoji(url))
            layout.addWidget(btn, row, col)
            col += 1
            if col >= 4:
                col = 0
                row += 1

    def select_emoji(self, url):
        self.emojiSelected.emit(url)
        self.accept()
