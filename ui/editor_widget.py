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

        # Store an HTML template for initial rendering with escaped curly braces
        self.html_template = '''<!DOCTYPE html>
<html>
<head>
    <script type="text/javascript" src="qrc:///qtwebchannel/qwebchannel.js"></script>
    <style>
body{{background-color:#1e1e1e;color:white;margin:0;padding:10px;font-family:sans-serif;font-size:20px}}
h1{{font-size:2.4em}}
h2{{font-size:2em}}
h3{{font-size:1.7em}}
#editor{{min-height:400px;outline:none;border-radius:10px}}
.resizable-image{{position:relative;display:inline-block;margin:5px}}
.resizable-image img{{max-width:100%;height:auto;cursor:move}}
.resizable-image .resize-handle{{position:absolute;width:10px;height:10px;background:white;border:1px solid #666;border-radius:50%}}
.resize-handle.nw{{top:-5px;left:-5px;cursor:nw-resize}}
.resize-handle.ne{{top:-5px;right:-5px;cursor:ne-resize}}
.resize-handle.sw{{bottom:-5px;left:-5px;cursor:sw-resize}}
.resize-handle.se{{bottom:-5px;right:-5px;cursor:se-resize}}
    </style>
    <script>
        document.addEventListener("DOMContentLoaded", function() {{
            var editor = document.getElementById("editor");
            
            new QWebChannel(qt.webChannelTransport, function(channel) {{
                window.qt = channel.objects.content_bridge;
                
                var lastContent = editor.innerHTML;
                setInterval(function() {{
                    if (editor.innerHTML !== lastContent) {{
                        lastContent = editor.innerHTML;
                        window.qt.content_changed(lastContent);
                    }}
                }}, 500);
            }});

            editor.addEventListener("blur", function() {{
                window.qt.content_changed(editor.innerHTML);
            }});
            
            editor.addEventListener("keydown", function(e) {{
                if (e.key === "Enter" && !e.shiftKey) {{
                    e.preventDefault();
                    document.execCommand('insertParagraph', false);
                }}
                if (e.key === "Tab") {{
                    e.preventDefault();
                    if (e.shiftKey) {{
                        document.execCommand("outdent");
                    }} else {{
                        document.execCommand("indent");
                    }}
                }}
            }});

            function makeImageResizable(img) {{
                const wrapper = document.createElement('div');
                wrapper.className = 'resizable-image';
                img.parentNode.insertBefore(wrapper, img);
                wrapper.appendChild(img);
                
                ['nw','ne','sw','se'].forEach(function(pos) {{
                    const handle = document.createElement('div');
                    handle.className = 'resize-handle ' + pos;
                    wrapper.appendChild(handle);
                }});
                
                let isResizing = false;
                let currentHandle = null;
                let originalWidth = img.width;
                let originalHeight = img.height;
                let originalX = 0;
                let originalY = 0;
                
                wrapper.addEventListener('mousedown', function(e) {{
                    if (e.target.classList.contains('resize-handle')) {{
                        isResizing = true;
                        currentHandle = e.target;
                        originalWidth = img.width;
                        originalHeight = img.height;
                        originalX = e.clientX;
                        originalY = e.clientY;
                        e.preventDefault();
                    }}
                }});
                
                document.addEventListener('mousemove', function(e) {{
                    if (!isResizing) return;
                    
                    const deltaX = e.clientX - originalX;
                    const deltaY = e.clientY - originalY;
                    
                    if (currentHandle.classList.contains('se')) {{
                        img.style.width = (originalWidth + deltaX) + 'px';
                        img.style.height = (originalHeight + deltaY) + 'px';
                    }}
                }});
                
                document.addEventListener('mouseup', function() {{
                    isResizing = false;
                    currentHandle = null;
                }});
            }}

            // Make all existing images resizable
            document.querySelectorAll('#editor img').forEach(makeImageResizable);
            
            // Make new images resizable when inserted
            const observer = new MutationObserver(function(mutations) {{
                mutations.forEach(function(mutation) {{
                    mutation.addedNodes.forEach(function(node) {{
                        if (node.nodeName === 'IMG' && !node.parentNode.classList.contains('resizable-image')) {{
                            makeImageResizable(node);
                        }}
                    }});
                }});
            }});
            
            observer.observe(editor, {{ childList: true, subtree: true }});
        }});
    </script>
</head>
<body>
    <div id="editor" contenteditable="true">{content}</div>
</body>
</html>'''
        
        # Initialize JavaScript bridge
        self.js_bridge = JavaScriptBridge()
        self.js_bridge.contentChanged.connect(self._on_content_changed)
        
        # Initialize QWebChannel with the dedicated bridge object
        self.channel = QWebChannel()
        self.web_view.page().setWebChannel(self.channel)
        self.channel.registerObject("content_bridge", self.js_bridge)

        # Render empty content on creation
        initial_content = self.renderer.render("")
        self.web_view.setHtml(self.html_template.format(content=initial_content))

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
        rendered = self.renderer.render(markdown_text)
        self.web_view.setHtml(self.html_template.format(content=rendered))

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