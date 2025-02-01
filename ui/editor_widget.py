from PyQt5.QtWidgets import QFrame, QVBoxLayout, QWidget
from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtWebChannel import QWebChannel
from PyQt5.QtWebEngineWidgets import QWebEngineSettings, QWebEngineView
from .custom_webview import CustomWebEngineView
from .js_bridge import JavaScriptBridge

class EditorWidget(QWidget):
    text_changed = pyqtSignal(str)  # Rename signal to avoid collision

    def __init__(self, renderer, parent=None):
        super().__init__(parent)
        self.renderer = renderer
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

        # Store an HTML template for initial rendering
        self.html_template = """
        <!DOCTYPE html>
        <html>
        <head>
          <script type="text/javascript" src="qrc:///qtwebchannel/qwebchannel.js"></script>
          <style>
            body {{ background-color: #1e1e1e; color: white; margin: 0; padding: 10px; font-family: sans-serif; font-size: 20px; }}
            h1 {{ font-size: 2.4em; }}
            h2 {{ font-size: 2em; }}
            h3 {{ font-size: 1.7em; }}
            #editor {{ min-height: 400px; outline: none; border-radius: 10px; }}
          </style>
          <script>
          document.addEventListener("DOMContentLoaded", function() {{

              var editor = document.getElementById("editor");
              
              // Initialize QWebChannel after DOM is loaded
              new QWebChannel(qt.webChannelTransport, function(channel) {{
                  window.qt = channel.objects.content_bridge;
                  
                  // Set up content monitoring after channel is ready
                  var lastContent = editor.innerHTML;
                  setInterval(function() {{
                      if (editor.innerHTML !== lastContent) {{
                          lastContent = editor.innerHTML;
                          window.qt.content_changed(lastContent);
                      }}
                  }}, 500);
              }});

              // Finish editing on blur
              editor.addEventListener("blur", function() {{
                  window.qt.content_changed(editor.innerHTML);
              }});
              
              // On Enter (without Shift) finish editing (blur)
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
          }});
          </script>
        </head>
        <body>
          <div id="editor" contenteditable="true">{content}</div>
        </body>
        </html>
        """
        
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

        js = """
        (function(){
            var sel = window.getSelection();
            if(!sel.toString()){
                var node = sel.focusNode;
                if(node){
                    if(node.nodeType === Node.TEXT_NODE){
                        node = node.parentNode;
                    }
                    var range = document.createRange();
                    range.selectNodeContents(node);
                    sel.removeAllRanges();
                    sel.addRange(range);
                }
            }
            var ed = document.getElementById('editor'); ed.focus();

            // Helper: unwrap headings or lists from the current selection
            function unwrapTag(node){
                while(node && node !== ed){
                    var tag = (node.tagName || "").toUpperCase();
                    if(tag === "LI"){
                        // Move LI contents outside
                        var parent = node.parentNode;
                        while(node.firstChild){
                            parent.parentNode.insertBefore(node.firstChild, parent);
                        }
                        parent.removeChild(node);
                    } else if(tag === "UL" || tag === "OL" || tag === "H1" || tag === "H2" || tag === "H3"){
                        while(node.firstChild){
                            node.parentNode.insertBefore(node.firstChild, node);
                        }
                        node.parentNode.removeChild(node);
                    }
                    node = node.parentNode;
                }
            }

            if(sel.focusNode){
                unwrapTag(sel.focusNode);
            }
        """.rstrip("\n")
        if value:
            js += "document.execCommand('{}', false, '{}');".format(command, value)
        else:
            js += "document.execCommand('{}');".format(command)
        js += """
        })();
        """
        self.web_view.page().runJavaScript(js)

    def set_content(self, markdown_text: str):
        rendered = self.renderer.render(markdown_text)
        self.web_view.setHtml(self.html_template.format(content=rendered))

    def get_content(self):
        code = "document.getElementById('editor').innerHTML;"
        # Return content asynchronously in a real scenario
        return code