from PyQt5.QtWidgets import QFrame, QVBoxLayout
from .custom_webview import CustomWebEngineView

class EditorWidget(QFrame):
    def __init__(self, renderer, parent=None):
        super().__init__(parent)
        self.renderer = renderer
        self.setStyleSheet("background-color: #1e1e1e;")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)  # Remove margins
        self.web_view = CustomWebEngineView()
        layout.addWidget(self.web_view, stretch=1)  # Add stretch factor

        # Store an HTML template for initial rendering
        self.html_template = """
        <html>
        <head>
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
              editor.addEventListener("keydown", function(e) {{
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

        # Render empty content on creation
        initial_content = self.renderer.render("")
        self.web_view.setHtml(self.html_template.format(content=initial_content))

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