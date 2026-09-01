from PyQt5.QtWidgets import QDialog, QGridLayout, QPushButton
from PyQt5.QtCore import pyqtSignal
from ui.scale import px

# Drawn with the platform emoji font, so no downloads and nothing to crop.
# Space separated because several of these are more than one code point.
EMOJIS = (
    "😀 😁 😂 🤣 😊 😍 😎 😉 "
    "🙂 😌 😔 😢 😭 😡 😱 😴 "
    "🤔 🤗 🤩 🥳 😇 🙃 😜 🤯 "
    "👍 👎 👏 🙏 👋 💪 🤝 ✌️ "
    "❤️ 💔 ⭐ ✨ 🔥 💯 ⚡ 🎉 "
    "✅ ❌ ⚠️ ❓ ❗ 📌 📎 🔒 "
    "📝 📄 📁 📊 📈 💡 🔍 🔧 "
    "🚀 🐛 ⏰ ☕ 🎯 🧠 🌍 🌙"
).split()

COLUMNS = 8


class EmojiSelector(QDialog):
    emojiSelected = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Select Emoji")
        layout = QGridLayout(self)
        layout.setSpacing(px(2))

        button_size = px(38)
        for index, emoji in enumerate(EMOJIS):
            btn = QPushButton(emoji)
            btn.setFlat(True)
            btn.setFixedSize(button_size, button_size)
            btn.setStyleSheet(f"font-size: {px(20)}px; border: none;")
            btn.setToolTip(emoji)
            btn.clicked.connect(lambda _checked, emoji=emoji: self.select_emoji(emoji))
            layout.addWidget(btn, index // COLUMNS, index % COLUMNS)

    def select_emoji(self, emoji):
        self.emojiSelected.emit(emoji)
        self.accept()
