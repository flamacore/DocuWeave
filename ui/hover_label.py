from PyQt5.QtWidgets import QLabel
from PyQt5.QtCore import Qt

class HoverLabel(QLabel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setAttribute(Qt.WA_Hover, True)
        self.setMouseTracking(True)

    def leaveEvent(self, event):
        self.repaint()  # Force clear hover state
        return super().leaveEvent(event)
