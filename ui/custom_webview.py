
from PyQt5.QtWebEngineWidgets import QWebEngineView

class CustomWebEngineView(QWebEngineView):
    def contextMenuEvent(self, event):
        menu = self.page().createStandardContextMenu()
        menu.setStyleSheet("""
            QMenu { background-color: #2e2e2e; border: 1px solid #555; color: white; border-radius: 10px; }
            QMenu::item { padding: 5px 25px 5px 20px; border-radius: 5px; }
            QMenu::item:selected { background-color: #3e3e3e; border-radius: 5px; }
        """)
        menu.exec_(event.globalPos())