import os
import shutil
import uuid
from PyQt5.QtCore import QUrl
from PyQt5.QtWidgets import QFrame, QVBoxLayout, QWidget
from PyQt5.QtCore import pyqtSignal, Qt, QUrl  # added QUrl import
from PyQt5.QtWebChannel import QWebChannel
from PyQt5.QtWebEngineWidgets import QWebEngineSettings, QWebEngineView
from ui.custom_webview import CustomWebEngineView
from ui.js_bridge import JavaScriptBridge

class EditorWidget(QWidget):
    text_changed = pyqtSignal(str)  # Rename signal to avoid collision

    def __init__(self, renderer, project, parent=None):
        super().__init__(parent)
        self.renderer = renderer
        self.project = project  # Store project reference
        self.setStyleSheet("background-color: var(--body-bg);")  # Now uses theme variable if needed
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)  # Remove margins
        self.web_view = QWebEngineView()
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
        tmpl_path = os.path.join(os.path.dirname(__file__), "editor_template.html")
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
        
        js = f"""
        (function(){{
            var ed = document.getElementById('editor');
            var sel = window.getSelection();
            function getHeading(node){{
                while(node && node !== ed){{
                    if(node.nodeName.match(/^H[1-6]$/)) return node;
                    node = node.parentNode;
                }}
                return null;
            }}
            function inList(node){{
                while(node && node !== ed){{
                    if(node.nodeName.match(/^(LI|UL|OL)$/)) return true;
                    node = node.parentNode;
                }}
                return false;
            }}
            var currentHeading = getHeading(sel.anchorNode);
            var appliedCommand = "{command}";
            var appliedValue = {f'"{value}"' if value is not None else 'null'};
            
            // Prevent heading if selection is within a list
            if(appliedCommand === 'formatBlock' && appliedValue && appliedValue.match(/<H[1-6]>/i)){{
                if(inList(sel.anchorNode)){{
                    console.log("Cannot add heading inside a list");
                    return;
                }}
                var tag = appliedValue.replace(/[<>]/g, '').toUpperCase();
                if(currentHeading && currentHeading.nodeName === tag){{
                    document.execCommand('formatBlock', false, '<P>');
                    return;
                }}
            }}
            else if(currentHeading && appliedCommand !== 'formatBlock'){{
                document.execCommand('formatBlock', false, '<P>');
            }}
            ed.focus();
            if(appliedValue)
                document.execCommand(appliedCommand, false, appliedValue);
            else
                document.execCommand(appliedCommand, false, null);
        }})();
        """
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
        if self.project.project_path:
            project_folder = os.path.splitext(self.project.project_path)[0]
            base_url = QUrl.fromLocalFile(project_folder + os.sep)
        else:
            base_url = QUrl()
        self.web_view.setHtml(final_html, base_url)

    def set_document_title(self, title: str):
        # Title no longer shown; no action needed.
        pass

    def get_content(self):
        code = "document.getElementById('editor').innerHTML;"
        # Return content asynchronously in a real scenario
        return code

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
                
                # Generate and log the relative path - use forward slashes for web URLs
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