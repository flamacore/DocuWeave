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
        self.enable_table_editing()

    def enable_table_editing(self):
        js = """
        (function() {
            console.log("Enabling table editing...");
            var ed = document.getElementById('editor');
            if (!ed) {
                console.error("Editor element not found!");
                return;
            }
            
            var removalTimer = null;
            function removeHandles() {
                document.querySelectorAll('.table-handle-btn-container').forEach(container => container.remove());
            }
            function scheduleRemoval() {
                removalTimer = setTimeout(removeHandles, 300);
            }
            function cancelRemoval() {
                if (removalTimer) {
                    clearTimeout(removalTimer);
                    removalTimer = null;
                }
            }
            
            function createButtonWithBuffer(btn) {
                // Determine color based on button text
                var bgColor = '#666';
                if (btn.text === '+') {
                    bgColor = '#28a745';
                } else if (btn.text === '-') {
                    bgColor = '#dc3545';
                }
                // Create container with padding for better hover
                let container = document.createElement('div');
                container.className = 'table-handle-btn-container';
                container.style.cssText = `
                    position: fixed;
                    top: ${btn.top - 10}px;
                    left: ${btn.left - 10}px;
                    padding: 10px;
                    z-index: 1000;
                `;
                let buttonEl = document.createElement('div');
                buttonEl.className = 'table-handle-btn';
                buttonEl.textContent = btn.text;
                buttonEl.style.cssText = `
                    background: ${bgColor};
                    color: white;
                    width: 16px;
                    height: 16px;
                    text-align: center;
                    line-height: 16px;
                    cursor: pointer;
                    border-radius: 50%;
                `;
                buttonEl.onclick = btn.action;
                container.appendChild(buttonEl);
                container.addEventListener('mouseenter', cancelRemoval);
                container.addEventListener('mouseleave', scheduleRemoval);
                document.body.appendChild(container);
                return container;
            }
            
            function handleCellMouseEnter(e) {
                cancelRemoval();
            }
            
            function handleCellMouseLeave(e) {
                scheduleRemoval();
            }
            
            function handleMouseOver(e) {
                if (e.target.matches('td, th')) {
                    let cell = e.target;
                    cancelRemoval();
                    cell.removeEventListener('mouseenter', handleCellMouseEnter);
                    cell.addEventListener('mouseenter', handleCellMouseEnter);
                    cell.removeEventListener('mouseleave', handleCellMouseLeave);
                    cell.addEventListener('mouseleave', handleCellMouseLeave);
                    
                    let rect = cell.getBoundingClientRect();
                    removeHandles();
                    // Determine if this is a first row or first column cell
                    let isFirstRow = cell.parentElement.rowIndex === 0;
                    let isFirstColumn = cell.cellIndex === 0;
                    
                    let btns = [];
                    if (isFirstColumn) {
                        btns.push({
                            text: '-',
                            top: rect.top,
                            left: rect.left - 20,
                            action: () => cell.parentElement.remove()
                        });
                    }
                    if (isFirstRow) {
                        btns.push({
                            text: '-',
                            top: rect.top - 20,
                            left: rect.left,
                            action: () => {
                                let idx = Array.from(cell.parentElement.children).indexOf(cell);
                                cell.closest('table').querySelectorAll('tr').forEach(row => {
                                    if (row.cells[idx]) row.deleteCell(idx);
                                });
                            }
                        });
                    }
                    btns.push(
                        {
                            text: '+',
                            top: rect.bottom,
                            left: rect.left - 20,
                            action: () => {
                                let newRow = cell.closest('table').insertRow(cell.parentElement.rowIndex + 1);
                                for (let i = 0; i < cell.parentElement.cells.length; i++) {
                                    let newCell = newRow.insertCell();
                                    newCell.style.border = '1px solid #ccc';
                                    newCell.style.padding = '8px';
                                }
                            }
                        },
                        {
                            text: '+',
                            top: rect.top - 20,
                            left: rect.right,
                            action: () => {
                                let idx = Array.from(cell.parentElement.children).indexOf(cell) + 1;
                                cell.closest('table').querySelectorAll('tr').forEach(row => {
                                    let newCell = row.insertCell(idx);
                                    newCell.style.border = '1px solid #ccc';
                                    newCell.style.padding = '8px';
                                });
                            }
                        }
                    );
                    btns.forEach(btn => createButtonWithBuffer(btn));
                }
            }
            
            ed.addEventListener('mouseover', handleMouseOver);
            console.log("Table editing enabled!");
        })();
        """
        self.web_view.page().runJavaScript(js)

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