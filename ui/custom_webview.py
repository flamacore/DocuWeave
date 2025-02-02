from PyQt5.QtWebEngineWidgets import QWebEngineView

class CustomWebEngineView(QWebEngineView):
    def contextMenuEvent(self, event):
        menu = self.page().createStandardContextMenu()
        menu.exec_(event.globalPos())