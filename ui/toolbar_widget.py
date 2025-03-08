import sys
import os
from PyQt5.QtWidgets import QFrame, QHBoxLayout, QPushButton, QFileDialog, QMessageBox, QMainWindow, QInputDialog  # Added QInputDialog
from PyQt5.QtGui import QIcon, QPixmap, QPainter, QColor, QTransform
from PyQt5.QtCore import Qt, QSize, QEvent, QRectF, QUrl  # Added QUrl
from PyQt5.QtSvg import QSvgRenderer
from ui.image_dialog import ImageDialog
from ui.emoji_selector import EmojiSelector  # New import

# Add helper to get resource path in bundle or during development
def get_resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# Add custom ToolbarButton for interactive hover and click effects
class ToolbarButton(QPushButton):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.default_style = "background-color: transparent;"
        self.hover_style = "background-color: rgba(255, 255, 255, 0.1);"
        self.pressed_style = "background-color: rgba(255, 255, 255, 0.2);"
        self.setStyleSheet(self.default_style)
        self.setMouseTracking(True)
        self.setAttribute(Qt.WA_Hover, True)

    def enterEvent(self, event):
        self.setStyleSheet(self.hover_style)
        super().enterEvent(event)

    def leaveEvent(self, event):
        self.setStyleSheet(self.default_style)
        super().leaveEvent(event)

    def mousePressEvent(self, event):
        self.setStyleSheet(self.pressed_style)
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        self.setStyleSheet(self.hover_style)
        super().mouseReleaseEvent(event)

def getColoredIcon(file_path, color=None, size=QSize(60,60), stroke_color=None, stroke_width=2):
    if color is None:
        color = QColor("white")
    renderer = QSvgRenderer(file_path)
    pixmap = QPixmap(size)
    pixmap.fill(Qt.transparent)
    painter = QPainter(pixmap)
    # Render SVG into the full area of pixmap
    renderer.render(painter, QRectF(0, 0, size.width(), size.height()))
    painter.setCompositionMode(QPainter.CompositionMode_SourceIn)
    painter.fillRect(pixmap.rect(), color)
    painter.end()
    
    # Add stroke if requested
    if stroke_color and stroke_width > 0:
        new_size = QSize(size.width() + stroke_width * 2, size.height() + stroke_width * 2)
        stroked_pixmap = QPixmap(new_size)
        stroked_pixmap.fill(Qt.transparent)
        painter = QPainter(stroked_pixmap)
        # Offsets to simulate stroke around the icon
        offsets = [(-stroke_width, 0), (stroke_width, 0), (0, -stroke_width), (0, stroke_width),
                   (-stroke_width, -stroke_width), (stroke_width, -stroke_width),
                   (-stroke_width, stroke_width), (stroke_width, stroke_width)]
        for dx, dy in offsets:
            painter.drawPixmap(dx + stroke_width, dy + stroke_width, pixmap)
        painter.setCompositionMode(QPainter.CompositionMode_SourceIn)
        painter.fillRect(stroked_pixmap.rect(), stroke_color)
        painter.setCompositionMode(QPainter.CompositionMode_SourceOver)
        # Draw original icon in the center
        painter.drawPixmap(stroke_width, stroke_width, pixmap)
        painter.end()
        pixmap = stroked_pixmap

    return QIcon(pixmap)

def getFlippedIcon(file_path, color=None, size=QSize(60,60)):  # Changed size to 48x48
    icon = getColoredIcon(file_path, color, size)
    pixmap = icon.pixmap(size)
    transform = QTransform().scale(-1, 1)
    flipped_pixmap = pixmap.transformed(transform)
    return QIcon(flipped_pixmap)

class ToolbarWidget(QFrame):
    def __init__(self, editor_widget, parent=None):
        super().__init__(parent)
        self.editor_widget = editor_widget
        layout = QHBoxLayout(self)
        # Set a larger fixed height for the toolbar
        self.setFixedHeight(70)
        
        # Group 1: Undo/Redo at start
        undo_button = ToolbarButton()
        undo_button.setIcon(getColoredIcon(get_resource_path("resources/undo.svg")))  # Using colored icon
        undo_button.setIconSize(QSize(28,28))
        undo_button.setToolTip("Undo")
        undo_button.clicked.connect(lambda: self.editor_widget.web_view.page().runJavaScript("document.execCommand('undo');"))
        layout.addWidget(undo_button)
        
        redo_button = ToolbarButton()
        redo_button.setIcon(getFlippedIcon(get_resource_path("resources/undo.svg")))  # Use flipped undo icon for redo
        redo_button.setIconSize(QSize(28,28))
        redo_button.setToolTip("Redo")
        redo_button.clicked.connect(lambda: self.editor_widget.web_view.page().runJavaScript("document.execCommand('redo');"))
        layout.addWidget(redo_button)
        
        # Vertical separator after Undo/Redo
        separator1 = QFrame()
        separator1.setObjectName("toolbarSeparator")
        separator1.setFrameShape(QFrame.VLine)
        separator1.setFrameShadow(QFrame.Sunken)
        layout.addWidget(separator1)
        
        # Group 2: Text formatting buttons (headings, bold, italic, underline, strike, quote, lists, alignments)
        h1_button = ToolbarButton()
        h1_button.setIcon(getColoredIcon(get_resource_path("resources/h1.svg")))
        h1_button.setIconSize(QSize(28,28))
        h1_button.setToolTip("Heading 1")
        h1_button.clicked.connect(lambda: self.editor_widget.format_text('formatBlock', '<H1>'))
        layout.addWidget(h1_button)
        
        h2_button = ToolbarButton()
        h2_button.setIcon(getColoredIcon(get_resource_path("resources/h2.svg")))
        h2_button.setIconSize(QSize(28,28))
        h2_button.setToolTip("Heading 2")
        h2_button.clicked.connect(lambda: self.editor_widget.format_text('formatBlock', '<H2>'))
        layout.addWidget(h2_button)
        
        h3_button = ToolbarButton()
        h3_button.setIcon(getColoredIcon(get_resource_path("resources/h3.svg")))
        h3_button.setIconSize(QSize(28,28))
        h3_button.setToolTip("Heading 3")
        h3_button.clicked.connect(lambda: self.editor_widget.format_text('formatBlock', '<H3>'))
        layout.addWidget(h3_button)
        
        normal_button = ToolbarButton()
        normal_button.setIcon(getColoredIcon(get_resource_path("resources/normal.svg")))
        normal_button.setIconSize(QSize(28,28))
        normal_button.setToolTip("Normal Text")
        normal_button.clicked.connect(lambda: self.editor_widget.format_text('formatBlock', '<P>'))
        layout.addWidget(normal_button)
        
        bold_button = ToolbarButton()
        bold_button.setIcon(getColoredIcon(get_resource_path("resources/bold.svg")))
        bold_button.setIconSize(QSize(28,28))
        bold_button.setToolTip("Bold")
        bold_button.clicked.connect(lambda: self.editor_widget.format_text('bold'))
        layout.addWidget(bold_button)
        
        italic_button = ToolbarButton()
        italic_button.setIcon(getColoredIcon(get_resource_path("resources/italic.svg")))
        italic_button.setIconSize(QSize(28,28))
        italic_button.setToolTip("Italic")
        italic_button.clicked.connect(lambda: self.editor_widget.format_text('italic'))
        layout.addWidget(italic_button)
        
        underline_button = ToolbarButton()
        underline_button.setIcon(getColoredIcon(get_resource_path("resources/underline.svg")))
        underline_button.setIconSize(QSize(28,28))
        underline_button.setToolTip("Underline")
        underline_button.clicked.connect(lambda: self.editor_widget.format_text('underline'))
        layout.addWidget(underline_button)
        
        strike_button = ToolbarButton()
        strike_button.setIcon(getColoredIcon(get_resource_path("resources/strikethrough.svg")))
        strike_button.setIconSize(QSize(28,28))
        strike_button.setToolTip("Strike Through")
        strike_button.clicked.connect(lambda: self.editor_widget.format_text('strikeThrough'))
        layout.addWidget(strike_button)
        
        quote_button = ToolbarButton()
        quote_button.setIcon(getColoredIcon(get_resource_path("resources/quote.svg")))
        quote_button.setIconSize(QSize(28,28))
        quote_button.setToolTip("Blockquote")
        quote_button.clicked.connect(lambda: self.editor_widget.format_text('formatBlock', '<BLOCKQUOTE>'))
        layout.addWidget(quote_button)
        
        bullet_list_button = ToolbarButton()
        bullet_list_button.setIcon(getColoredIcon(get_resource_path("resources/bullet.svg")))
        bullet_list_button.setIconSize(QSize(28,28))
        bullet_list_button.setToolTip("Bullet List")
        bullet_list_button.clicked.connect(lambda: self.editor_widget.format_text('insertUnorderedList'))
        layout.addWidget(bullet_list_button)
        
        numbered_list_button = ToolbarButton()
        numbered_list_button.setIcon(getColoredIcon(get_resource_path("resources/numbered.svg")))
        numbered_list_button.setIconSize(QSize(28,28))
        numbered_list_button.setToolTip("Numbered List")
        numbered_list_button.clicked.connect(lambda: self.editor_widget.format_text('insertOrderedList'))
        layout.addWidget(numbered_list_button)
        
        align_left = ToolbarButton()
        align_left.setIcon(getColoredIcon(get_resource_path("resources/align_left.svg")))
        align_left.setIconSize(QSize(28,28))
        align_left.setToolTip("Align Left")
        align_left.clicked.connect(lambda: self.editor_widget.format_text('justifyLeft'))
        layout.addWidget(align_left)
        
        align_center = ToolbarButton()
        align_center.setIcon(getColoredIcon(get_resource_path("resources/align_center.svg")))
        align_center.setIconSize(QSize(28,28))
        align_center.setToolTip("Center")
        align_center.clicked.connect(lambda: self.editor_widget.format_text('justifyCenter'))
        layout.addWidget(align_center)
        
        align_right = ToolbarButton()
        align_right.setIcon(getColoredIcon(get_resource_path("resources/align_right.svg")))
        align_right.setIconSize(QSize(28,28))
        align_right.setToolTip("Align Right")
        align_right.clicked.connect(lambda: self.editor_widget.format_text('justifyRight'))
        layout.addWidget(align_right)
        
        justify = ToolbarButton()
        justify.setIcon(getColoredIcon(get_resource_path("resources/justify.svg")))
        justify.setIconSize(QSize(28,28))
        justify.setToolTip("Justify")
        justify.clicked.connect(lambda: self.editor_widget.format_text('justifyFull'))
        layout.addWidget(justify)
        
        # Vertical separator after text formatters
        separator2 = QFrame()
        separator2.setObjectName("toolbarSeparator")
        separator2.setFrameShape(QFrame.VLine)
        separator2.setFrameShadow(QFrame.Sunken)
        layout.addWidget(separator2)
        
        # Group 3: Inserter buttons at end
        emoji_button = ToolbarButton()
        emoji_button.setIcon(getColoredIcon(get_resource_path("resources/emoji.svg")))
        emoji_button.setIconSize(QSize(28,28))
        emoji_button.setToolTip("Insert Emoji")
        emoji_button.clicked.connect(self.show_emoji_selector)
        layout.addWidget(emoji_button)
        
        link_button = ToolbarButton()
        link_button.setIcon(getColoredIcon(get_resource_path("resources/link.svg")))
        link_button.setIconSize(QSize(28,28))
        link_button.setToolTip("Insert Link")
        link_button.clicked.connect(self.insert_link)
        layout.addWidget(link_button)
        
        info_box_btn = ToolbarButton()
        info_box_btn.setIcon(getColoredIcon(get_resource_path("resources/info_box.svg")))
        info_box_btn.setIconSize(QSize(28,28))
        info_box_btn.setToolTip("Insert Info Box")
        info_box_btn.clicked.connect(self.editor_widget.insert_info_box)
        layout.addWidget(info_box_btn)
        
        image_button = ToolbarButton()
        image_button.setIcon(getColoredIcon(get_resource_path("resources/image.svg")))
        image_button.setIconSize(QSize(28,28))
        image_button.setToolTip("Insert Image")
        image_button.clicked.connect(self.show_image_dialog)
        layout.addWidget(image_button)
        
        # Example: Insert Table button
        table_button = ToolbarButton()
        table_button.setIcon(getColoredIcon(get_resource_path("resources/table.svg")))
        table_button.setIconSize(QSize(28,28))
        table_button.setToolTip("Insert Table")
        table_button.clicked.connect(self.insert_table_dialog)
        layout.addWidget(table_button)

        layout.addStretch()
        self.setStyleSheet("background-color: #1e1e1e;")

    def set_editor_widget(self, editor_widget):
        self.editor_widget = editor_widget

    def show_image_dialog(self):
        print(f"\033[94mChecking project path: {self.editor_widget.project.project_path}\033[0m")
        
        # Find MainWindow instance
        main_window = None
        widget = self
        while widget and not isinstance(widget, QMainWindow):
            widget = widget.parent()
        main_window = widget
        
        if not self.editor_widget.project.project_path and main_window:
            # Try saving the project first and wait for completion
            def after_save():
                print(f"\033[94mProject path after save: {self.editor_widget.project.project_path}\033[0m")
                if not self.editor_widget.project.project_path:
                    QMessageBox.warning(
                        self,
                        "No Project",
                        "You must save the project before adding images.",
                        QMessageBox.Ok
                    )
                    return
                self._show_image_dialog_impl()

            saved = main_window.save_project(after_save)
            return
        
        self._show_image_dialog_impl()

    def _show_image_dialog_impl(self):
        """Internal method to show the image dialog after project path is confirmed"""
        print("\033[92mOpening image dialog...\033[0m")
        dialog = ImageDialog(self)
        dialog.setWindowModality(Qt.ApplicationModal)
        if dialog.exec_():
            if dialog.mode == "file":
                file_path = dialog.file_path
                if file_path:
                    img_path = self.editor_widget.add_image_to_project(file_path)
                    if img_path:
                        self.editor_widget.insert_image(img_path)
            else:
                url = dialog.url
                if url:
                    self.editor_widget.insert_image(url)

    def insert_link(self):
        """Show dialog for inserting a link"""
        from ui.link_type_dialog import LinkTypeDialog
        from ui.external_link_dialog import ExternalLinkDialog
        from PyQt5.QtCore import Qt
        
        # Show link type dialog first
        link_type_dialog = LinkTypeDialog(self)
        link_type_dialog.setWindowModality(Qt.ApplicationModal)
        
        if not link_type_dialog.exec_():
            return  # User cancelled
            
        link_type = link_type_dialog.get_selected_type()
        
        if link_type == "external":
            # Show external URL dialog
            external_dialog = ExternalLinkDialog(self)
            external_dialog.setWindowModality(Qt.ApplicationModal)
            
            if external_dialog.exec_():
                url = external_dialog.get_url()
                if url:
                    self.editor_widget.format_text('createLink', url)
        else:
            # Internal document link
            # First check if project is saved
            if not self.editor_widget.project.project_path:
                main_window = None
                widget = self
                while widget and not isinstance(widget, QMainWindow):
                    widget = widget.parent()
                main_window = widget
                
                if main_window:
                    def after_save():
                        if self.editor_widget.project.project_path:
                            self._show_internal_link_dialog()
                    main_window.save_project(after_save)
                return
                
            self._show_internal_link_dialog()
                
    def _show_internal_link_dialog(self):
        """Show dialog for selecting internal document to link to"""
        from ui.internal_link_dialog import InternalLinkDialog
        from PyQt5.QtCore import Qt
        
        dialog = InternalLinkDialog(self.editor_widget.project, self)
        dialog.setWindowModality(Qt.ApplicationModal)
        
        if dialog.exec_():
            doc_path = dialog.get_selected_path()
            if doc_path:
                # Create a special URL scheme for internal document links
                internal_url = f"docuweave://document/{doc_path}"
                
                # Get display text (either selected text or document name)
                display_name = doc_path.split('/')[-1]  # Use document name by default
                self.editor_widget.web_view.page().runJavaScript(
                    "window.getSelection().toString();",
                    lambda selected_text: self._create_link(internal_url, selected_text or display_name)
                )
                
    def _create_link(self, url, display_text=None):
        """Create a link with optional display text"""
        # Make sure the URL is properly encoded for special characters
        from urllib.parse import quote
        
        # Only encode the path part if it's an internal document link
        if url.startswith('docuweave://document/'):
            prefix = 'docuweave://document/'
            path = url[len(prefix):]
            encoded_path = quote(path)
            url = prefix + encoded_path
            
        if display_text:
            # Create link with specific text
            js = f"""
            (function() {{
                var selection = window.getSelection();
                if (selection.toString().trim() === '') {{
                    // No selection, insert new link with display text
                    document.execCommand('insertHTML', false, '<a href="{url}">{display_text}</a>');
                }} else {{
                    // Use selection
                    document.execCommand('createLink', false, '{url}');
                }}
            }})();
            """
        else:
            # Simply create link from selection
            js = f"document.execCommand('createLink', false, '{url}');"
        
        self.editor_widget.web_view.page().runJavaScript(js)

    def show_emoji_selector(self):
        selector = EmojiSelector(self)
        selector.emojiSelected.connect(self.insert_emoji)
        selector.exec_()
    
    def insert_emoji(self, url):
        """Insert emoji at cursor position, handling both local SVG files and remote URLs."""
        if os.path.exists(url):
            # Make sure path separator is forward slash for URLs
            url = url.replace('\\', '/')
            if not url.startswith('/'):
                url = '/' + url
            url = 'file://' + url
            
        js = (
            "document.execCommand('insertHTML', false, "
            "'<object type=\"image/svg+xml\" data=\"{url}\" " 
            "style=\"width:24px; height:24px; vertical-align: middle;\">" 
            "<img src=\"{url}\" alt=\"emoji\" "
            "style=\"width:24px; height:24px; vertical-align: middle;\"/>"
            "</object>')"
        ).format(url=url)
        self.editor_widget.web_view.page().runJavaScript(js)

    def insert_table_dialog(self):
        from PyQt5.QtWidgets import QMainWindow, QMessageBox
        # Find MainWindow instance similar to the image dialog process
        main_window = None
        widget = self
        while widget and not isinstance(widget, QMainWindow):
            widget = widget.parent()
        main_window = widget

        if not self.editor_widget.project.project_path and main_window:
            def after_save():
                if not self.editor_widget.project.project_path:
                    QMessageBox.warning(
                        self,
                        "No Project",
                        "You must save the project before inserting a table.",
                        QMessageBox.Ok
                    )
                    return
                self._show_table_dialog_impl()
            main_window.save_project(after_save)
            return

        self._show_table_dialog_impl()

    def _show_table_dialog_impl(self):
        from ui.table_dialog import TableDialog
        from PyQt5.QtCore import Qt
        dialog = TableDialog(self)
        dialog.setWindowModality(Qt.ApplicationModal)
        if dialog.exec_():
            rows, cols = dialog.get_table_dimensions()
            self.editor_widget.insert_table(rows, cols)