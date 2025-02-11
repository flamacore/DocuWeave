import sys
from PyQt5.QtWidgets import QDialog, QGridLayout, QPushButton, QLabel, QFrame
from PyQt5.QtCore import pyqtSignal, Qt, QByteArray
from PyQt5.QtGui import QPixmap, QIcon, QPainter
from PyQt5.QtSvg import QSvgRenderer
import requests
from pathlib import Path
import os

class EmojiSelector(QDialog):
    emojiSelected = pyqtSignal(str)
    
    # Map of emoji codes to friendly names for better UI
    EMOJI_MAP = {
        "1f600": "😀 Grinning",
        "1f601": "😁 Beaming",
        "1f602": "😂 Joy",
        "1f603": "😃 Smiley",
        "1f604": "😄 Grinning",
        "1f605": "😅 Sweating",
        "1f606": "😆 Squinting",
        "1f923": "🤣 ROFL"
    }
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Select Emoji")
        self.setMinimumSize(300, 200)
        layout = QGridLayout(self)
        self.emoji_cache = {}
        
        # Create cache directory if it doesn't exist
        cache_dir = Path(os.path.expanduser("~"), ".docuweave", "emoji_cache")
        cache_dir.mkdir(parents=True, exist_ok=True)
        
        base_url = "https://twitter.github.io/twemoji/v/latest/svg/"
        row, col = 0, 0
        
        for code in self.EMOJI_MAP.keys():
            url = f"{base_url}{code}.svg"
            cache_path = cache_dir / f"{code}.svg"
            container = QFrame()
            container_layout = QGridLayout(container)
            container_layout.setSpacing(2)
            container_layout.setContentsMargins(2, 2, 2, 2)

            btn = QPushButton()
            btn.setFlat(True)
            btn.setFixedSize(48, 48)
            
            # Try to load from cache first
            if cache_path.exists():
                renderer = QSvgRenderer(str(cache_path))
                pixmap = QPixmap(48, 48)
                pixmap.fill(Qt.transparent)
                painter = QPainter(pixmap)
                renderer.render(painter)
                painter.end()
            else:
                try:
                    resp = requests.get(url)
                    if resp.status_code == 200:
                        # Save to cache
                        cache_path.write_bytes(resp.content)
                        renderer = QSvgRenderer(QByteArray(resp.content))
                        pixmap = QPixmap(48, 48)
                        pixmap.fill(Qt.transparent)
                        painter = QPainter(pixmap)
                        renderer.render(painter)
                        painter.end()
                except Exception:
                    pixmap = QPixmap()
            
            if not pixmap.isNull():
                self.emoji_cache[code] = str(cache_path)
                btn.setIcon(QIcon(pixmap))
                btn.setIconSize(pixmap.size())
            else:
                # Use emoji character as fallback
                fallback_text = self.EMOJI_MAP[code].split()[0]
                btn.setText(fallback_text)
                btn.setStyleSheet("font-size: 24px;")

            btn.clicked.connect(lambda checked, code=code: self.select_emoji(code))
            
            # Add a label with the emoji name
            label = QLabel(self.EMOJI_MAP[code].split(None, 1)[1])
            label.setAlignment(Qt.AlignCenter)
            label.setStyleSheet("color: #ccc; font-size: 10px;")
            
            container_layout.addWidget(btn, 0, 0, 1, 1, Qt.AlignCenter)
            container_layout.addWidget(label, 1, 0, 1, 1, Qt.AlignCenter)
            
            layout.addWidget(container, row, col)
            col += 1
            if col >= 4:
                col = 0
                row += 1

    def select_emoji(self, code):
        if code in self.emoji_cache:
            self.emojiSelected.emit(self.emoji_cache[code])
        else:
            # Fallback to URL if not cached
            url = f"https://twitter.github.io/twemoji/v/latest/svg/{code}.svg"
            self.emojiSelected.emit(url)
        self.accept()
