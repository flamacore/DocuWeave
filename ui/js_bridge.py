from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot

class JavaScriptBridge(QObject):
    contentChanged = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)

    @pyqtSlot(str)
    def content_changed(self, content):
        self.contentChanged.emit(content)
