import os  # Added import for os
import sys  # Added import for sys.exit
from PyQt5.QtWidgets import QMainWindow, QVBoxLayout, QWidget, QPushButton, QFileDialog, QFrame, QHBoxLayout, QMenu, QSplitter, QLabel, QApplication, QMenuBar, QShortcut, QInputDialog
from PyQt5.QtCore import Qt, QPoint
from PyQt5.QtGui import QFont, QCursor, QKeySequence, QIcon  # Remove QShortcut from here
from PyQt5.QtWebEngineWidgets import QWebEngineView
from core.editor import Editor
from core.renderer import Renderer
from core.project import Project
from .editor_widget import EditorWidget
from .toolbar_widget import ToolbarWidget
from .project_sidebar import ProjectSidebar
from .startup_dialog import StartupDialog  # Add this import
from ui.hover_label import HoverLabel  # new import
import colorama
colorama.init(autoreset=True)

# New: Custom QWebEngineView with modern styled context menu
class CustomWebEngineView(QWebEngineView):
    def contextMenuEvent(self, event):
        menu = self.page().createStandardContextMenu()
        # Removed inline style; rely on QSS styling via widget objectNames
        menu.exec_(event.globalPos())

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # Set window icon
        icon_path = os.path.join(os.path.dirname(__file__), "..", "resources", "icon.ico")
        self.setWindowIcon(QIcon(icon_path))
        
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
        if not self.get_document_count():
            self.create_new_document()

    def create_title_bar(self):
        """Create custom title bar"""
        title_bar = QWidget()
        title_bar.setObjectName("titleBar")
        layout = QHBoxLayout(title_bar)
        layout.setSpacing(0)  # Remove spacing between elements
        layout.setContentsMargins(10, 0, 10, 0)  # Remove vertical margins
        
        # Create icon for the title with transparency
        icon = QIcon(os.path.join(os.path.dirname(__file__), "..", "resources", "icon.ico"))
        icon_label = QLabel()
        icon_label.setObjectName("titleIcon")
        pixmap = icon.pixmap(16, 16)  # Smaller icon size
        if not pixmap.isNull():
            icon_label.setPixmap(pixmap)
        icon_label.setFixedSize(20, 40)  # Width includes small padding
        icon_label.setAlignment(Qt.AlignCenter)
        icon_label.setAttribute(Qt.WA_TranslucentBackground)  # Enable transparency
        layout.addWidget(icon_label)
        
        # Add spacing between icon and text
        layout.addSpacing(4)
        
        # Add title label
        self.title_label = HoverLabel(f"DocuWeave - {self.project.name}")
        self.title_label.setObjectName("titleLabel")
        self.title_label.setFont(QFont("Segoe UI", 12))
        self.title_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.title_label.mousePressEvent = self.show_menu
        layout.addWidget(self.title_label)
        
        layout.addStretch()
        
        # Window controls: set objectNames for QSS-driven styling.
        min_btn = QPushButton("−")
        max_btn = QPushButton("□")
        close_btn = QPushButton("×")
        for btn in (min_btn, max_btn, close_btn):
            btn.setObjectName("windowButton")
            btn.setFixedSize(30, 30)
            layout.addWidget(btn)
        
        min_btn.clicked.connect(self.showMinimized)
        max_btn.clicked.connect(self._toggle_maximized)
        close_btn.clicked.connect(self.close)
        
        title_bar.setFixedHeight(50)
        return title_bar

    def update_title_bar(self):
        """Refresh the title bar to display the current project name"""
        self.title_label.setText(f"DocuWeave - {self.project.name}")

    def show_menu(self, event):
        if not self.menu:
            self.menu = QMenu(self)
            self.menu.setObjectName("titleMenuBar")  # Set object name for QSS targeting
            self._setup_menu_bar(self.menu)
        self.menu.exec_(self.mapToGlobal(event.pos()))

    def init_ui(self):
        # Create a base container that will hold everything
        self.base_container = QWidget()
        self.base_container.setObjectName("baseContainer")
        base_layout = QVBoxLayout(self.base_container)
        base_layout.setContentsMargins(1, 1, 1, 1)  # 1px padding all around
        base_layout.setSpacing(0)
        
        # Create the main central widget
        central_widget = QWidget()
        central_widget.setObjectName("mainContainer")
        central_widget.setMouseTracking(True)
        base_layout.addWidget(central_widget)
        self.setCentralWidget(self.base_container)
        
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Rest of the UI initialization...
        title_bar = self.create_title_bar()
        main_layout.addWidget(title_bar)
        
        # Content area
        content = QWidget()
        content.setMouseTracking(True)
        content_layout = QHBoxLayout(content)
        content_layout.setContentsMargins(0, 0, 0, 0)  # Remove all margins
        content_layout.setSpacing(0)  # Remove spacing between widgets
        main_layout.addWidget(content)

        # Add project sidebar
        self.sidebar = ProjectSidebar()
        # Use the item_selected signal to handle document selection
        self.sidebar.item_selected.connect(self.change_document)

        # Create splitter for sidebar and editor
        splitter = QSplitter(Qt.Horizontal)
        splitter.setHandleWidth(1)  # Minimum handle width
        splitter.setChildrenCollapsible(False)  # Prevent collapsing
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

        # Connect signals for real-time updates and document management
        self.sidebar.new_document_requested.connect(self.create_new_document_in_parent)
        self.sidebar.document_created.connect(self.create_document)
        self.sidebar.document_deleted.connect(self.delete_document)
        self.sidebar.document_renamed.connect(self.rename_document)
        self.editor_widget.text_changed.connect(self.update_current_content)
        
        # Remove save button as we're doing real-time saves
        button_frame.setVisible(False)

    def get_document_count(self):
        """Get the total number of documents in the project"""
        return len(self.project.get_all_documents())

    def _save_current_content(self, callback=None):
        """Save current document content; then call callback."""
        if self.project.current_document:
            self.editor_widget.web_view.page().runJavaScript(
                "document.getElementById('editor').innerHTML;",
                lambda content: (self.project.update_content(self.project.current_document, content), 
                                callback() if callback else None)
            )
        else:
            if callback:
                callback()

    def change_document(self, document_path):
        """Switch to a different document: save current, clear editor, then load new content."""
        if document_path == self.project.current_document:
            return  # No need to save/reload if same document is clicked
            
        def load_new():
            self.editor_widget.set_content("")
            content = self.project.get_content(document_path)
            
            if content is not None:
                self.editor_widget.set_content(content)
                self.project.current_document = document_path
                
                # Update window title to include the current document name
                name = document_path.split('/')[-1] if document_path else "Root"
                has_children = self.project.has_children(document_path)
                document_type = "Container" if has_children else "Document"
                self.title_label.setText(f"DocuWeave - {self.project.name} - {name} ({document_type})")
                
                # Update selection in project sidebar
                self.sidebar._restore_selection(self.sidebar.model.invisibleRootItem(), document_path)
            else:
                # If content not found, create a new document
                self.create_new_document()
                
        self._save_current_content(load_new)

    def create_new_document(self, parent_path=""):
        """Save current document, then create a new untitled document and open it."""
        def after_save():
            try:
                new_doc_path = self.project.create_untitled_document(parent_path)
                self.sidebar.update_tree(self.project)
                self.editor_widget.set_content("")
                self.project.current_document = new_doc_path
                
                # Update window title
                name = new_doc_path.split('/')[-1]
                self.title_label.setText(f"DocuWeave - {self.project.name} - {name} (Document)")
            except Exception as e:
                print(f"Error creating new document: {e}")
        self._save_current_content(after_save)

    def create_new_document_in_parent(self, parent_path):
        """Create a new document in the specified parent document"""
        # Show dialog to get document name
        doc_name, ok = QInputDialog.getText(self, "New Document", "Document name:")
        if not ok or not doc_name:
            return
            
        def after_save():
            try:
                # Create document with the user-specified name
                new_doc_path = self.project.create_document(doc_name, "", parent_path)
                self.sidebar.update_tree(self.project)
                self.editor_widget.set_content("")
                self.project.current_document = new_doc_path
                
                # Update window title
                self.title_label.setText(f"DocuWeave - {self.project.name} - {doc_name} (Document)")
            except Exception as e:
                print(f"Error creating new document: {e}")
        self._save_current_content(after_save)

    def create_document(self, parent_path, document_name):
        """Create a new document with specified name at the parent path"""
        try:
            doc_path = self.project.create_document(document_name, "", parent_path)
            self.sidebar.update_tree(self.project)
            
            # Auto-save project to persist document structure
            if self.project.project_path:
                self.project.save_project(self.project.project_path)
                
            # Switch to the new document automatically
            self.change_document(doc_path)
        except Exception as e:
            print(f"Error creating document: {e}")

    def _setup_menu_bar(self, menu):
        """Setup menu bar items"""
        file_menu = menu.addMenu('File')
        
        new_doc = file_menu.addAction('New Document')
        new_doc.setShortcut('Ctrl+N')
        new_doc.triggered.connect(lambda: self.create_new_document())
        
        # Change "New Folder" to "New Container Document"
        new_container = file_menu.addAction('New Container Document')
        new_container.triggered.connect(lambda: self.create_document("", "New Container"))
        
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
        if self.project.current_document:
            self.editor_widget.web_view.page().runJavaScript(
                "document.getElementById('editor').innerHTML;",
                lambda content: self._handle_document_save(content)
            )
            self.sidebar.update_tree(self.project)

    def _handle_save(self, html_content, file_name):
        with open(file_name, 'w', encoding='utf-8') as file:
            file.write(html_content)
        print("\033[92mSave completed: {}\033[0m".format(file_name))

    def new_project(self):
        self.project = Project()
        self.project.name = "Untitled Project"
        self.sidebar.update_tree(self.project)
        self.editor_widget.set_content("")
        self.editor_widget.project = self.project
        self.toolbar_widget.editor_widget = self.editor_widget
        self.update_title_bar()  # Update title bar

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
                self.sidebar.update_tree(self.project)
                self.editor_widget.project = self.project
                self.toolbar_widget.editor_widget = self.editor_widget
                self.update_title_bar()  # Update title bar after project load
                
                # Load the current document if specified in project
                if self.project.current_document:
                    content = self.project.get_content(self.project.current_document)
                    if content is not None:
                        self.editor_widget.set_content(content)
                    else:
                        # Create a new document if current one is not found
                        self.create_new_document()
                else:
                    # If no current file but documents exist, create a new one
                    self.create_new_document()
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
                if self.project.current_document:
                    self.project.update_content(self.project.current_document, content)
                print(f"\033[94mBefore save_project, project_path: {self.project.project_path}\033[0m")
                self.project.save_project(self.project.project_path)
                print(f"\033[94mAfter save_project, project_path: {self.project.project_path}\033[0m")
                # Make sure editor widget has current project reference
                self.editor_widget.project = self.project
                if callback:
                    callback()

            if self.project.current_document:
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
        if self.project.current_document:
            self.project.update_document(self.project.current_document, content)

    def update_current_content(self, content):
        """Real-time update of current document content"""
        if self.project.current_document:
            self.project.update_content(self.project.current_document, content)
            # Auto-save to persist changes
            if self.project.project_path:
                 self.project.save_project(self.project.project_path)

    def delete_document(self, doc_path):
        """Delete a document by its path"""
        if self.project.remove_document(doc_path):
            self.sidebar.update_tree(self.project)
            
            # If current document was deleted, load a new one
            if not self.project.current_document:
                # Find another document to load
                if self.get_document_count() > 0:
                    # The project implementation should have already selected another document
                    if self.project.current_document:
                        self.change_document(self.project.current_document)
                else:
                    # No documents left, create a new one
                    self.create_new_document()
                    
            # Autosave to persist changes
            if self.project.project_path:
                self.project.save_project(self.project.project_path)

    def rename_document(self, old_path: str, new_path: str):
        """Handle document rename requests"""
        print(f"MainWindow received document rename request: {old_path} -> {new_path}")  # Debug log
        
        if self.project.rename_document(old_path, new_path):
            print("Document rename successful in project")  # Debug log
            # Update tree view
            self.sidebar.update_tree(self.project)
            
            # Auto-save project if path exists
            if self.project.project_path:
                self.project.save_project(self.project.project_path)
        else:
            print("Document rename failed in project")  # Debug log
            # Update tree to restore previous state
            self.sidebar.update_tree(self.project)

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
        self.update_title_bar()  # Update title bar after project creation
        print(f"\033[94mAfter create_new_project_at_path, project_path: {self.project.project_path}\033[0m")
        
        # Double-check project path is set
        if not self.project.project_path:
            print("\033[91mWarning: project_path not set after creation!\033[0m")
            self.project.project_path = project_file
            
        return True

    def eventFilter(self, obj, event):
        from PyQt5.QtCore import QEvent
        if obj == self.title_label and event.type() == QEvent.HoverLeave:
            self.title_label.repaint()  # Force repaint so hover state clears
        return super().eventFilter(obj, event)