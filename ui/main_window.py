from PyQt5.QtWidgets import QMainWindow, QVBoxLayout, QWidget, QPushButton, QFileDialog, QFrame, QHBoxLayout, QMenu
from PyQt5.QtCore import Qt
from PyQt5.QtWebEngineWidgets import QWebEngineView
from core.editor import Editor
from core.renderer import Renderer
from .editor_widget import EditorWidget
from .toolbar_widget import ToolbarWidget
import colorama
colorama.init(autoreset=True)

# New: Custom QWebEngineView with modern styled context menu
class CustomWebEngineView(QWebEngineView):
    def contextMenuEvent(self, event):
        menu = self.page().createStandardContextMenu()
        menu.setStyleSheet("""
            QMenu { background-color: #2e2e2e; border: 1px solid #555; color: white; border-radius: 10px; }
            QMenu::item { padding: 5px 25px 5px 20px; border-radius: 5px; }
            QMenu::item:selected { background-color: #3e3e3e; border-radius: 5px; }
        """)
        menu.exec_(event.globalPos())

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("WYSIWYG Markdown Editor")
        self.setGeometry(100, 100, 1000, 600)
        self.setStyleSheet("""
            QMainWindow { background-color: #2e2e2e; color: white; border-radius: 10px; }
            QPushButton { background-color: #3e3e3e; color: white; border: none; padding: 5px; border-radius: 5px; font-size: 22px; }
            QPushButton:hover { background-color: #5e5e5e; border-radius: 5px; }
            QFrame { border-radius: 10px; }
        """)
        self.editor = Editor()
        self.renderer = Renderer()
        self.init_ui()

    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        # Create a frame to hold the WYSIWYG editor and toolbar
        container = QFrame()
        container.setStyleSheet("background-color: #1e1e1e;")
        main_layout.addWidget(container, stretch=1)  # Add stretch factor
        container_layout = QVBoxLayout(container)
        container_layout.setContentsMargins(0,0,0,0)
        
        # Create editor widget
        self.editor_widget = EditorWidget(self.renderer, parent=container)
        # Create toolbar widget
        toolbar = ToolbarWidget(self.editor_widget, parent=container)

        container_layout.addWidget(toolbar)
        container_layout.addWidget(self.editor_widget)
        
        # Control buttons below the container
        button_frame = QFrame()
        button_frame.setFixedHeight(50)  # Fix the height of button area
        button_layout = QHBoxLayout(button_frame)
        button_layout.setContentsMargins(5, 5, 5, 5)  # Tighter margins
        save_button = QPushButton("Save Markdown")
        save_button.clicked.connect(self.save_markdown)
        button_layout.addWidget(save_button)
        main_layout.addWidget(button_frame)

    def save_markdown(self):
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getSaveFileName(self, "Save Markdown File", "", "Markdown Files (*.md);;All Files (*)", options=options)
        # ...existing code...
        if file_name:
            print("\033[93mStarting save to: {}\033[0m".format(file_name))
            self.editor_widget.web_view.page().runJavaScript(
                "document.getElementById('editor').innerHTML;",
                lambda html_content: self._handle_save(html_content, file_name)
            )
    # ...existing code...

    def _handle_save(self, html_content, file_name):
        with open(file_name, 'w', encoding='utf-8') as file:
            file.write(html_content)
        print("\033[92mSave completed: {}\033[0m".format(file_name))