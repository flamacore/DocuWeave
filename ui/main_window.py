import os  # Added import for os
from PyQt5.QtWidgets import QMainWindow, QVBoxLayout, QWidget, QPushButton, QFileDialog, QFrame, QHBoxLayout, QMenu, QSplitter, QLabel, QApplication, QMenuBar
from PyQt5.QtCore import Qt, QPoint
from PyQt5.QtGui import QFont, QCursor
from PyQt5.QtWebEngineWidgets import QWebEngineView
from core.editor import Editor
from core.renderer import Renderer
from core.project import Project
from .editor_widget import EditorWidget
from .toolbar_widget import ToolbarWidget
from .project_sidebar import ProjectSidebar
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
        # Set window flags for frameless window
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        # For moving & resizing
        self._drag_pos = None
        self._resizing = False
        self._resize_start_pos = None
        self._resize_start_rect = None
        self._margin = 5  # pixels for resize area
        
        self.setWindowTitle("DocuWeave")
        
        # Calculate 80% of screen size for default window size
        screen = QApplication.primaryScreen().availableGeometry()
        width = int(screen.width() * 0.8)
        height = int(screen.height() * 0.8)
        x = int(screen.width() * 0.1)  # 10% from left
        y = int(screen.height() * 0.1)  # 10% from top
        self.setGeometry(x, y, width, height)
        
        # Load and apply the stylesheet
        style_path = os.path.join(os.path.dirname(__file__), 'dark_theme.qss')
        with open(style_path, 'r') as f:
            self.setStyleSheet(f.read())
            
        self.editor = Editor()
        self.renderer = Renderer()
        self.project = Project()
        self.init_ui()
        self.create_new_document()  # Create initial document
        self.menu = None  # Add this line to store the menu

    def create_title_bar(self):
        """Create custom title bar"""
        title_bar = QWidget()
        title_bar.setObjectName("titleBar")
        layout = QHBoxLayout(title_bar)
        layout.setContentsMargins(10, 5, 10, 5)
        
        # App title acting as File button
        title = QLabel("DocuWeave")
        title.setObjectName("titleLabel")
        title.setFont(QFont("Segoe UI", 12))
        title.setAlignment(Qt.AlignCenter)
        title.setFixedWidth(200)  # Set fixed width for title
        title.setStyleSheet("""
            QLabel#titleLabel {
                background-color: transparent;
                color: white;
                padding: 5px;
                border-radius: 5px;
            }
            QLabel#titleLabel:hover {
                background-color: #3e3e3e;
            }
        """)
        title.mousePressEvent = self.show_menu  # Connect click event to show_menu
        layout.addWidget(title)
        
        layout.addStretch()
        
        # Window controls
        min_btn = QPushButton("−")
        max_btn = QPushButton("□")
        close_btn = QPushButton("×")
        
        for btn in (min_btn, max_btn, close_btn):
            btn.setObjectName("windowButton")
            btn.setFixedSize(40, 40)  # Increase button size
            btn.setFont(QFont("Segoe UI", 16))  # Increase font size
            layout.addWidget(btn)
        
        min_btn.clicked.connect(self.showMinimized)
        max_btn.clicked.connect(self._toggle_maximized)
        close_btn.clicked.connect(self.close)
        
        title_bar.setFixedHeight(50)  # Adjust height to fit larger buttons
        return title_bar

    def show_menu(self, event):
        if not self.menu:
            self.menu = QMenu(self)
            self._setup_menu_bar(self.menu)
        self.menu.exec_(self.mapToGlobal(event.pos()))

    def init_ui(self):
        central_widget = QWidget()
        central_widget.setMouseTracking(True)  # Enable mouse tracking
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Add title bar at the top
        title_bar = self.create_title_bar()
        main_layout.addWidget(title_bar)
        
        # Content area
        content = QWidget()
        content.setMouseTracking(True)
        content_layout = QHBoxLayout(content)
        main_layout.addWidget(content)

        # Add project sidebar
        self.sidebar = ProjectSidebar()
        self.sidebar.file_selected.connect(self.change_document)

        # Create splitter for sidebar and editor
        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(self.sidebar)
        
        # Editor container
        editor_container = QWidget()
        editor_layout = QVBoxLayout(editor_container)
        
        # Create a frame to hold the WYSIWYG editor and toolbar
        container = QFrame()
        container.setStyleSheet("background-color: #1e1e1e;")
        editor_layout.addWidget(container, stretch=1)  # Add stretch factor
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
        editor_layout.addWidget(button_frame)

        splitter.addWidget(editor_container)
        splitter.setStretchFactor(1, 4)  # Make editor area wider
        content_layout.addWidget(splitter)

        # Add menu bar with project actions
        
        # Connect signals for real-time updates and document management
        self.sidebar.new_file_requested.connect(self.create_new_document)
        self.sidebar.file_deleted.connect(self.delete_document)
        self.sidebar.file_renamed.connect(self.rename_document)
        self.editor_widget.text_changed.connect(self.update_current_document)  # Use renamed signal
        
        # Remove save button as we're doing real-time saves
        button_frame.setVisible(False)

    def create_new_document(self):
        """Create a new document and switch to it"""
        current_content = None
        if self.project.current_file:
            # Save current content before switching
            self.editor_widget.web_view.page().runJavaScript(
                "document.getElementById('editor').innerHTML;",
                lambda content: self._handle_document_save(content)
            )
        
        # Create new document
        doc_id = self.project.create_untitled_document()
        self.sidebar.update_tree(self.project.documents)
        self.change_document(doc_id)

    def _setup_menu_bar(self, menu):
        """Setup menu bar items"""
        file_menu = menu.addMenu('File')
        
        new_doc = file_menu.addAction('New Document')
        new_doc.setShortcut('Ctrl+N')
        new_doc.triggered.connect(self.create_new_document)
        
        new_project = file_menu.addAction('New Project')
        open_project = file_menu.addAction('Open Project')
        save_project = file_menu.addAction('Save Project')
        
        new_project.triggered.connect(self.new_project)
        open_project.triggered.connect(self.open_project)
        save_project.triggered.connect(self.save_project)

    def change_document(self, path):
        """Load document content into editor"""
        if path in self.project.documents:
            content = self.project.get_document(path)
            self.editor_widget.set_content(content)
            self.project.current_file = path

    def save_markdown(self):
        """Update current document in project"""
        if self.project.current_file:
            self.editor_widget.web_view.page().runJavaScript(
                "document.getElementById('editor').innerHTML;",
                lambda content: self._handle_document_save(content)
            )
            self.sidebar.update_tree(self.project.documents)

    def _handle_save(self, html_content, file_name):
        with open(file_name, 'w', encoding='utf-8') as file:
            file.write(html_content)
        print("\033[92mSave completed: {}\033[0m".format(file_name))

    def new_project(self):
        self.project = Project()
        self.project.name = "Untitled Project"
        self.sidebar.update_tree(self.project.documents)
        self.editor_widget.set_content("")

    def open_project(self):
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getOpenFileName(
            self,
            "Open Project",
            "",
            "DocuWeave Project (*.dwproj);;All Files (*)",
            options=options
        )
        if file_name:
            self.project.load_project(file_name)
            self.sidebar.update_tree(self.project.documents)
            if self.project.current_file:
                self.change_document(self.project.current_file)

    def save_project(self):
        if not self.project.project_path:
            options = QFileDialog.Options()
            file_name, _ = QFileDialog.getSaveFileName(
                self,
                "Save Project",
                "",
                "DocuWeave Project (*.dwproj);;All Files (*)",
                options=options
            )
            if not file_name:
                return
            self.project.project_path = file_name

        # Update current document content before saving
        if self.project.current_file:
            self.editor_widget.web_view.page().runJavaScript(
                "document.getElementById('editor').innerHTML;",
                lambda content: self._handle_document_save(content)
            )
        self.project.save_project(self.project.project_path)

    def _handle_document_save(self, content):
        if self.project.current_file:
            self.project.update_document(self.project.current_file, content)

    def update_current_document(self, content):
        """Real-time update of document content"""
        if self.project.current_file:
            self.project.update_document(self.project.current_file, content)
            # Remove auto-save from here to avoid blocking UI:
            if self.project.project_path:
                 self.project.save_project(self.project.project_path)

    def delete_document(self, doc_id):
        if doc_id in self.project.documents:
            self.project.remove_document(doc_id)
            self.sidebar.update_tree(self.project.documents)
            # Create new document if we deleted the last one
            if not self.project.documents:
                self.create_new_document()
            elif self.project.current_file:
                self.change_document(self.project.current_file)

    def rename_document(self, old_name: str, new_name: str):
        """Handle document rename requests"""
        print(f"MainWindow received rename request: {old_name} -> {new_name}")  # Debug log
        
        if self.project.rename_document(old_name, new_name):
            print("Rename successful in project")  # Debug log
            # Don't update tree here - it will reset the editing state
            if self.project.project_path:
                self.project.save_project(self.project.project_path)
        else:
            print("Rename failed in project")  # Debug log
            # Only update tree if rename failed
            self.sidebar.update_tree(self.project.documents)

    def mousePressEvent(self, event):
        pos = event.pos()
        if event.button() == Qt.LeftButton:
            # Check if near right or bottom border for resizing
            if pos.x() >= self.width() - self._margin or pos.y() >= self.height() - self._margin:
                self._resizing = True
                self._resize_start_pos = event.globalPos()
                self._resize_start_rect = self.geometry()
            else:
                self._drag_pos = event.globalPos()
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        pos = event.pos()
        # Change cursor if near resize border
        if pos.x() >= self.width() - self._margin and pos.y() >= self.height() - self._margin:
            self.setCursor(QCursor(Qt.SizeFDiagCursor))
        else:
            self.setCursor(QCursor(Qt.ArrowCursor))
            
        if self._resizing:
            diff = event.globalPos() - self._resize_start_pos
            new_width = self._resize_start_rect.width() + diff.x()
            new_height = self._resize_start_rect.height() + diff.y()
            self.setGeometry(self._resize_start_rect.x(),
                             self._resize_start_rect.y(),
                             max(new_width, 400), max(new_height, 300))
        elif event.buttons() == Qt.LeftButton and self._drag_pos is not None:
            diff = event.globalPos() - self._drag_pos
            self.move(self.pos() + diff)
            self._drag_pos = event.globalPos()
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        self._resizing = False
        self._drag_pos = None
        super().mouseReleaseEvent(event)

    def _toggle_maximized(self):
        if self.isMaximized():
            self.showNormal()
        else:
            self.showMaximized()