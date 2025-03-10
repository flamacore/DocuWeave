import os
import shutil
import uuid
from PyQt5.QtCore import QUrl
from PyQt5.QtWidgets import QFrame, QVBoxLayout, QWidget
from PyQt5.QtCore import pyqtSignal, Qt, QUrl  # added QUrl import
from PyQt5.QtWebChannel import QWebChannel
from PyQt5.QtWebEngineWidgets import QWebEngineSettings, QWebEngineView, QWebEnginePage
from PyQt5.QtGui import QDesktopServices
from ui.custom_webview import CustomWebEngineView
from ui.js_bridge import JavaScriptBridge

class CustomWebEnginePage(QWebEnginePage):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add JavaScript to handle link clicks
        self.loadFinished.connect(self._add_link_handler)

    def _add_link_handler(self, ok):
        if ok:
            js = """
            document.addEventListener('click', function(e) {
                if (e.target.tagName === 'A') {
                    e.preventDefault();
                    window.location.href = e.target.href;
                }
            });
            """
            self.runJavaScript(js)

    def acceptNavigationRequest(self, url, _type, isMainFrame):
        # Handle internal document links with our custom scheme
        if url.scheme() == 'docuweave':
            if url.host() == 'document':
                # Extract document path from the URL and properly decode it
                doc_path = url.path().lstrip('/')
                # URL decode the path to handle special characters
                from urllib.parse import unquote
                doc_path = unquote(doc_path)
                print(f"Internal navigation to document: {doc_path}")
                
                # Find MainWindow to trigger document navigation
                try:
                    from PyQt5.QtWidgets import QApplication
                    for widget in QApplication.topLevelWidgets():
                        if widget.__class__.__name__ == "MainWindow":
                            # Navigate to the document
                            widget.change_document(doc_path)
                            return False
                except Exception as e:
                    print(f"Error during document navigation: {str(e)}")
                    return False
                        
                return False
                
        # Handle existing URL types
        if url.scheme() in ['data', 'qrc']:
            return True
        
        # Handle external URLs
        if url.scheme() in ['http', 'https']:
            print(f"Opening in system browser: {url.toString()}")
            QDesktopServices.openUrl(url)
            return False
            
        return True

class EditorWidget(QWidget):
    text_changed = pyqtSignal(str)  # Rename signal to avoid collision

    def __init__(self, renderer, project, parent=None):
        super().__init__(parent)
        self.renderer = renderer
        self.project = project  # Store project reference
        # Removed inline background-style; styling is applied via dark_theme.qss.
        # self.setStyleSheet("background-color: var(--body-bg);")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)  # Remove margins
        self.web_view = QWebEngineView()
        page = CustomWebEnginePage(self.web_view)
        self.web_view.setPage(page)
        self.web_view.setContextMenuPolicy(Qt.PreventContextMenu)
        self.web_view.setFocusPolicy(Qt.StrongFocus)
        layout.addWidget(self.web_view, stretch=1)  # Add stretch factor

        # Configure web settings
        settings = self.web_view.page().settings()
        settings.setAttribute(QWebEngineSettings.LocalContentCanAccessFileUrls, True)
        settings.setAttribute(QWebEngineSettings.LocalContentCanAccessRemoteUrls, True)
        settings.setAttribute(QWebEngineSettings.JavascriptCanAccessClipboard, True)
        settings.setAttribute(QWebEngineSettings.LocalStorageEnabled, True)

        # Revert HTML template to original: only editable content is present.
        tmpl_path = os.path.join(os.path.dirname(__file__), "assets", "editor_template.html")
        with open(tmpl_path, "r", encoding="utf-8") as f:
            self.html_template = f.read()
        
        # Set default title and content
        self.current_title = "Untitled Document"
        initial_content = self.renderer.render("")
        # Get theme variables from qss via renderer helper
        theme_vars = self.renderer.get_theme_variables()
        html = self.html_template.format(content=initial_content, theme_vars=theme_vars)
        self.web_view.setHtml(html, QUrl("qrc:///"))

        # Initialize JavaScript bridge
        self.js_bridge = JavaScriptBridge()
        self.js_bridge.contentChanged.connect(self._on_content_changed)
        
        # Initialize QWebChannel with the dedicated bridge object
        self.channel = QWebChannel()
        self.web_view.page().setWebChannel(self.channel)
        self.channel.registerObject("content_bridge", self.js_bridge)

    def _on_content_changed(self, content):
        """Handle content changes from JavaScript"""
        self.text_changed.emit(content)

    def format_text(self, command, value=None):
        # Log the applied formatting
        print("\033[94mApplying command: {} {}\033[0m".format(command, value if value else ""))
        js = """"""
        js_path = os.path.join(os.path.dirname(__file__), "assets", "editor_widget_formatter.js")
        with open(js_path, "r", encoding="utf-8") as f:
            js = f.read()
        self.web_view.page().runJavaScript(js)

    def set_content(self, text: str):
        import html
        if text.lstrip().startswith('<'):
            content_html = text
        else:
            rendered = self.renderer.render(text)
            content_html = html.unescape(rendered)
        # Check if the template expects both placeholders
        if "{theme_vars}" in self.html_template:
            theme_vars = self.renderer.get_theme_variables()
            final_html = self.html_template.format(content=content_html, theme_vars=theme_vars)
        else:
            final_html = self.html_template.format(content=content_html)
        
        # Inject CSS to style links and fix local file access
        styles = """
        <style>
        a { color: var(--theme-link-color) !important; text-decoration: underline; cursor: pointer; }
        a[href^="docuweave://"] { color: var(--theme-internal-link-color, #7cb342) !important; }
        @font-face { font-family: 'emoji'; src: local('Apple Color Emoji'), local('Segoe UI Emoji'); }
        img[alt="emoji"] { font-family: 'emoji'; }
        </style>
        <script>
        // Enable local file access for images
        const originalFetch = window.fetch;
        window.fetch = function(url, options) {
            if (url.startsWith('file://')) {
                return new Promise((resolve) => {
                    const img = new Image();
                    img.src = url;
                    resolve(new Response(img));
                });
            }
            return originalFetch(url, options);
        };
        </script>
        """
        final_html = styles + final_html
        
        if self.project.project_path:
            project_folder = os.path.splitext(self.project.project_path)[0]
            base_url = QUrl.fromLocalFile(project_folder + os.sep)
        else:
            base_url = QUrl()
        
        settings = self.web_view.settings()
        settings.setAttribute(QWebEngineSettings.LocalContentCanAccessFileUrls, True)
        settings.setAttribute(QWebEngineSettings.AllowRunningInsecureContent, True)
        
        self.web_view.setHtml(final_html, base_url)
        self.enable_table_editing()

    def enable_table_editing(self):
        js_path = os.path.join(os.path.dirname(__file__), "assets", "table_editing.js")
        with open(js_path, "r", encoding="utf-8") as f:
            js = f.read()
        self.web_view.page().runJavaScript(js)

    def add_image_to_project(self, file_path):
        """Copy image to project's image directory and return relative path"""
        try:
            if self.project.project_path:
                # Get the project folder (where documents are stored)
                project_folder = os.path.splitext(self.project.project_path)[0]
                print(f"\033[94mProject folder path: {project_folder}\033[0m")
                
                # Create images subfolder within the project documents folder
                img_dir = os.path.join(project_folder, 'images')
                print(f"\033[94mCreating image directory at: {img_dir}\033[0m")
                os.makedirs(img_dir, exist_ok=True)
                
                # Generate unique filename and copy
                ext = os.path.splitext(file_path)[1]
                new_name = f"{uuid.uuid4()}{ext}"
                new_path = os.path.join(img_dir, new_name)
                print(f"\033[94mCopying image from {file_path} to {new_path}\033[0m")
                shutil.copy2(file_path, new_path)
                
                # Generate and log the relative path - use forward slashes for web paths
                rel_path = f"images/{new_name}"  # Always use forward slashes for web paths
                print(f"\033[92mReturning relative image path: {rel_path}\033[0m")
                return rel_path
            else:
                print("\033[91mNo project path set - cannot add image to project\033[0m")
                return None
                
        except Exception as e:
            print(f"\033[91mError adding image to project: {str(e)}\033[0m")
            return None

    def insert_image(self, src):
        """Insert image at current cursor position as scalable proportionally"""
        if src:
            src = src.replace('\\', '/')
            js = f"""
            document.execCommand('insertHTML', false, 
                '<div class="scalable-image" contenteditable="false" style="display: inline-block; resize: horizontal; overflow: auto; border: 1px solid #ccc; margin: 5px; width:300px;"><img src="{src}" alt="Inserted image" style="display: block; width: 100%; height: auto;"/></div>'
            );
            """
            self.web_view.page().runJavaScript(js)
        else:
            print("\033[91mAttempted to insert image with empty src\033[0m")

    def insert_info_box(self):
        """Insert an editable info box into the document."""
        self.web_view.page().runJavaScript("insertInfoBox();")

    def insert_table(self, rows, cols):
        js = f"""
        (function() {{
            var ed = document.getElementById('editor');
            ed.focus();
            var table = document.createElement('table');
            table.style.width = '70%';
            table.style.borderCollapse = 'collapse';
            table.style.border = '1px solid #ccc';
            for (var r = 0; r < {rows}; r++) {{
                var row = table.insertRow(r);
                for (var c = 0; c < {cols}; c++) {{
                    var cell = row.insertCell(c);
                    cell.style.border = '1px solid #ccc';
                    cell.style.padding = '8px';
                    cell.textContent = '';
                }}
            }}
            document.execCommand('insertHTML', false, table.outerHTML);
        }})();
        """
        self.web_view.page().runJavaScript(js, lambda result: self.enable_table_editing())