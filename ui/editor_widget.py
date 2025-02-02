import os
import shutil
import uuid
from PyQt5.QtCore import QUrl
from PyQt5.QtWidgets import QFrame, QVBoxLayout, QWidget
from PyQt5.QtCore import pyqtSignal, Qt
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
        self.setStyleSheet("background-color: #1e1e1e;")
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
        self.web_view.setHtml(self.html_template.format(content=initial_content))

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

    def set_content(self, markdown_text: str):
        import html
        rendered = self.renderer.render(markdown_text)
        # Unescape HTML entities to prevent double-escaping
        unescaped = html.unescape(rendered)
        self.web_view.setHtml(self.html_template.format(content=unescaped))

    def set_document_title(self, title: str):
        # Title no longer shown; no action needed.
        pass

    def get_content(self):
        code = "document.getElementById('editor').innerHTML;"
        # Return content asynchronously in a real scenario
        return code

    def add_image_to_project(self, file_path):
        """Copy image to project's image directory and return relative path"""
        # Create images directory in current directory if no project path exists
        if self.project.project_path:
            base_dir = os.path.dirname(self.project.project_path)
        else:
            base_dir = os.getcwd()
            
        img_dir = os.path.join(base_dir, 'images')
        os.makedirs(img_dir, exist_ok=True)
        
        # Generate unique filename
        ext = os.path.splitext(file_path)[1]
        new_name = f"{uuid.uuid4()}{ext}"
        new_path = os.path.join(img_dir, new_name)
        
        # Copy file
        shutil.copy2(file_path, new_path)
        
        # Return relative path
        return f"images/{new_name}"

    def insert_image(self, src):
        """Insert image at current cursor position"""
        js = f"""
        document.execCommand('insertHTML', false, 
            '<img src="{src}" alt="Inserted image" style="max-width: 100%; height: auto;">'
        );
        """
        self.web_view.page().runJavaScript(js)

    def insert_info_box(self):
        """Insert an editable info box into the document."""
        self.web_view.page().runJavaScript("insertInfoBox();")