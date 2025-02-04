import os  # Added import for os
import sys  # Added import for sys.exit
from PyQt5.QtWidgets import QMainWindow, QVBoxLayout, QWidget, QPushButton, QFileDialog, QFrame, QHBoxLayout, QMenu, QSplitter, QLabel, QApplication, QMenuBar, QShortcut
from PyQt5.QtCore import Qt, QPoint
from PyQt5.QtGui import QFont, QCursor, QKeySequence  # Remove QShortcut from here
from PyQt5.QtWebEngineWidgets import QWebEngineView
from core.editor import Editor
from core.renderer import Renderer
from core.project import Project
from .editor_widget import EditorWidget
from .toolbar_widget import ToolbarWidget
from .project_sidebar import ProjectSidebar
from .startup_dialog import StartupDialog  # Add this import
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
        
        # Comment out the frameless + translucent settings
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
        style_path = os.path.join(os.path.dirname(__file__), "..", "resources", "dark_theme.qss")
        with open(style_path, 'r') as f:
            self.setStyleSheet(f.read())
        
        # Initialize core components
        self.editor = Editor()
        self.renderer = Renderer()
        self.project = Project()
        self.menu = None
        
        # Initialize UI first
        self.init_ui()
        
        # Add shortcuts for saving (Ctrl+S) and opening projects (Ctrl+O)
        self.shortcut_save = QShortcut(QKeySequence("Ctrl+S"), self)
        self.shortcut_save.activated.connect(lambda: self.save_project())
        
        self.shortcut_open = QShortcut(QKeySequence("Ctrl+O"), self)
        self.shortcut_open.activated.connect(lambda: self.open_project())
        
        # Handle project selection; if canceled, continue with a new document.
        self.show_startup_dialog()
        
        # Only create a new document if none already exist
        if not self.project.documents:
            self.create_new_document()

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
            btn.setFixedSize(30, 30)  # Increase button size
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
        container.setObjectName("editorFrame")  # Use qss styling, remove inline style
        editor_layout.addWidget(container, stretch=1)  # Add stretch factor
        container_layout = QVBoxLayout(container)
        container_layout.setContentsMargins(0,0,0,0)
        
        # Create editor widget with project reference
        self.editor_widget = EditorWidget(self.renderer, self.project, parent=container)
        # Create toolbar widget
        toolbar = ToolbarWidget(self.editor_widget, parent=container)
        self.toolbar_widget = toolbar

        container_layout.addWidget(self.toolbar_widget)
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

    def _save_current_document(self, callback=None):
        """Save current document content; then call callback."""
        if self.project.current_file:
            self.editor_widget.web_view.page().runJavaScript(
                "document.getElementById('editor').innerHTML;",
                lambda content: (self.project.update_document(self.project.current_file, content), callback() if callback else None)
            )
        else:
            if callback:
                callback()

    def change_document(self, new_path):
        """Switch to a different document: save current, clear editor, then load new content."""
        if new_path == self.project.current_file:
            return  # No need to save/reload if same document is clicked
        def load_new():
            self.editor_widget.set_content("")
            if new_path in self.project.documents:
                new_content = self.project.get_document(new_path)
                self.editor_widget.set_content(new_content)
                self.project.current_file = new_path
            else:
                self.create_new_document()
        self._save_current_document(load_new)

    def create_new_document(self):
        """Save current document, then create a new untitled document and open it."""
        def after_save():
            new_doc_id = self.project.create_untitled_document()
            self.sidebar.update_tree(self.project.documents)
            self.editor_widget.set_content("")
            self.project.current_file = new_doc_id
        self._save_current_document(after_save)

    def _setup_menu_bar(self, menu):
        """Setup menu bar items"""
        file_menu = menu.addMenu('File')
        
        new_doc = file_menu.addAction('New Document')
        new_doc.setShortcut('Ctrl+N')
        new_doc.triggered.connect(self.create_new_document)
        
        new_project = file_menu.addAction('New Project')
        new_project.triggered.connect(self.new_project)
        
        open_project = file_menu.addAction('Open Project')
        open_project.setShortcut('Ctrl+O')
        open_project.triggered.connect(self.open_project)
        
        save_project = file_menu.addAction('Save Project')
        save_project.setShortcut('Ctrl+S')
        save_project.triggered.connect(self.save_project)
        # ...existing code...

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
        self.editor_widget.project = self.project
        self.toolbar_widget.editor_widget = self.editor_widget

    def open_project(self, file_path=None):
        """Open a project from file path or show dialog to select one"""
        if not file_path:
            options = QFileDialog.Options()
            file_path, _ = QFileDialog.getOpenFileName(
                self,
                "Open Project",
                "",
                "DocuWeave Project (*.dwproj);;All Files (*)",
                options=options
            )
        
        if file_path:
            try:
                self.project.load_project(file_path)
                self.sidebar.update_tree(self.project.documents)
                self.editor_widget.project = self.project
                self.toolbar_widget.editor_widget = self.editor_widget
                # Open the first document if it exists; otherwise, create a new one.
                if self.project.documents:
                    first_doc = next(iter(self.project.documents))
                    self._save_current_document(lambda: self.change_document(first_doc))
                else:
                    self.create_new_document()
                self.editor_widget.project = self.project
                return True
            except Exception as e:
                print(f"Error loading project: {e}")
                return False
        return False

    def save_project(self, callback=None):
        """Save project and execute callback when complete"""
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
                print("\033[91mProject save cancelled by user\033[0m")
                # Do not call callback so that downstream actions halt.
                return False
            
            if not file_name.endswith('.dwproj'):
                file_name += '.dwproj'
            print(f"\033[94mSetting project path: {file_name}\033[0m")
            self.project.project_path = file_name

        try:
            # Update current document content before saving
            def after_content_save(content):
                if self.project.current_file:
                    self.project.update_document(self.project.current_file, content)
                print(f"\033[94mBefore save_project, project_path: {self.project.project_path}\033[0m")
                self.project.save_project(self.project.project_path)
                print(f"\033[94mAfter save_project, project_path: {self.project.project_path}\033[0m")
                # Make sure editor widget has current project reference
                self.editor_widget.project = self.project
                if callback:
                    callback()

            if self.project.current_file:
                self.editor_widget.web_view.page().runJavaScript(
                    "document.getElementById('editor').innerHTML;",
                    after_content_save
                )
            else:
                self.project.save_project(self.project.project_path)
                if callback:
                    callback()
            return True
            
        except Exception as e:
            print(f"\033[91mError saving project: {e}\033[0m")
            if callback:
                callback()
            return False

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
        if (doc_id in self.project.documents):
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
        # Update cursor based on position
        if pos.x() >= self.width() - self._margin and pos.y() >= self.height() - self._margin:
            self.setCursor(Qt.SizeFDiagCursor)
        elif pos.x() >= self.width() - self._margin:
            self.setCursor(Qt.SizeHorCursor)
        elif pos.y() >= self.height() - self._margin:
            self.setCursor(Qt.SizeVerCursor)
        else:
            self.setCursor(Qt.ArrowCursor)
            
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

    def show_startup_dialog(self):
        """Show startup dialog and handle project creation/opening"""
        dialog = StartupDialog(self)
        result = dialog.exec_()
        
        if result == StartupDialog.Accepted:
            if dialog.action == "new":
                if dialog.project_path:
                    return self.create_new_project_at_path(dialog.project_path)
            elif dialog.action == "open":
                if dialog.project_path:
                    return self.open_project(dialog.project_path)
        return False

    def create_new_project_at_path(self, folder_path):
        """Create new project at specified location"""
        self.project = Project()
        self.project.name = os.path.basename(folder_path)
        
        # Create project file path
        project_file = os.path.join(folder_path, f"{self.project.name}.dwproj")
        self.project.project_path = project_file
        
        # Update editor references before saving
        self.editor_widget.project = self.project
        self.toolbar_widget.editor_widget = self.editor_widget
        
        # Save the project immediately to create necessary folders
        self.project.save_project(project_file)
        print(f"\033[94mAfter create_new_project_at_path, project_path: {self.project.project_path}\033[0m")
        
        # Double-check project path is set
        if not self.project.project_path:
            print("\033[91mWarning: project_path not set after creation!\033[0m")
            self.project.project_path = project_file
            
        return True