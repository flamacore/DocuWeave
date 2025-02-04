import sys
import os
from PyQt5.QtWidgets import QFrame, QHBoxLayout, QPushButton, QFileDialog, QMessageBox, QMainWindow
from PyQt5.QtGui import QIcon, QPixmap, QPainter, QColor, QTransform
from PyQt5.QtCore import Qt, QSize, QEvent
from PyQt5.QtSvg import QSvgRenderer
from ui.image_dialog import ImageDialog

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

def getColoredIcon(file_path, color=None, size=QSize(32,32), stroke_color=None, stroke_width=2):
    if color is None:
        color = QColor("white")
    renderer = QSvgRenderer(file_path)
    pixmap = QPixmap(size)
    pixmap.fill(Qt.transparent)
    painter = QPainter(pixmap)
    renderer.render(painter)
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

def getFlippedIcon(file_path, color=None, size=QSize(32,32)):
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
        
        # Group 1: Undo/Redo at start
        undo_button = ToolbarButton()
        undo_button.setIcon(getColoredIcon(get_resource_path("resources/undo.svg")))  # Using colored icon
        undo_button.setToolTip("Undo")
        undo_button.clicked.connect(lambda: self.editor_widget.web_view.page().runJavaScript("document.execCommand('undo');"))
        layout.addWidget(undo_button)
        
        redo_button = ToolbarButton()
        redo_button.setIcon(getFlippedIcon(get_resource_path("resources/undo.svg")))  # Use flipped undo icon for redo
        redo_button.setToolTip("Redo")
        redo_button.clicked.connect(lambda: self.editor_widget.web_view.page().runJavaScript("document.execCommand('redo');"))
        layout.addWidget(redo_button)
        
        # Vertical separator after Undo/Redo
        separator1 = QFrame()
        separator1.setFrameShape(QFrame.VLine)
        separator1.setFrameShadow(QFrame.Sunken)
        layout.addWidget(separator1)
        
        # Group 2: Text formatting buttons (headings, bold, italic, underline, strike, quote, lists, alignments)
        h1_button = ToolbarButton()
        h1_button.setIcon(getColoredIcon(get_resource_path("resources/h1.svg")))
        h1_button.setToolTip("Heading 1")
        h1_button.clicked.connect(lambda: self.editor_widget.format_text('formatBlock', '<H1>'))
        layout.addWidget(h1_button)
        
        h2_button = ToolbarButton()
        h2_button.setIcon(getColoredIcon(get_resource_path("resources/h2.svg")))
        h2_button.setToolTip("Heading 2")
        h2_button.clicked.connect(lambda: self.editor_widget.format_text('formatBlock', '<H2>'))
        layout.addWidget(h2_button)
        
        h3_button = ToolbarButton()
        h3_button.setIcon(getColoredIcon(get_resource_path("resources/h3.svg")))
        h3_button.setToolTip("Heading 3")
        h3_button.clicked.connect(lambda: self.editor_widget.format_text('formatBlock', '<H3>'))
        layout.addWidget(h3_button)
        
        normal_button = ToolbarButton()
        normal_button.setIcon(getColoredIcon(get_resource_path("resources/normal.svg")))
        normal_button.setToolTip("Normal Text")
        normal_button.clicked.connect(lambda: self.editor_widget.format_text('formatBlock', '<P>'))
        layout.addWidget(normal_button)
        
        bold_button = ToolbarButton()
        bold_button.setIcon(getColoredIcon(get_resource_path("resources/bold.svg")))
        bold_button.setToolTip("Bold")
        bold_button.clicked.connect(lambda: self.editor_widget.format_text('bold'))
        layout.addWidget(bold_button)
        
        italic_button = ToolbarButton()
        italic_button.setIcon(getColoredIcon(get_resource_path("resources/italic.svg")))
        italic_button.setToolTip("Italic")
        italic_button.clicked.connect(lambda: self.editor_widget.format_text('italic'))
        layout.addWidget(italic_button)
        
        underline_button = ToolbarButton()
        underline_button.setIcon(getColoredIcon(get_resource_path("resources/underline.svg")))
        underline_button.setToolTip("Underline")
        underline_button.clicked.connect(lambda: self.editor_widget.format_text('underline'))
        layout.addWidget(underline_button)
        
        strike_button = ToolbarButton()
        strike_button.setIcon(getColoredIcon(get_resource_path("resources/strikethrough.svg")))
        strike_button.setToolTip("Strike Through")
        strike_button.clicked.connect(lambda: self.editor_widget.format_text('strikeThrough'))
        layout.addWidget(strike_button)
        
        quote_button = ToolbarButton()
        quote_button.setIcon(getColoredIcon(get_resource_path("resources/quote.svg")))
        quote_button.setToolTip("Blockquote")
        quote_button.clicked.connect(lambda: self.editor_widget.format_text('formatBlock', '<BLOCKQUOTE>'))
        layout.addWidget(quote_button)
        
        bullet_list_button = ToolbarButton()
        bullet_list_button.setIcon(getColoredIcon(get_resource_path("resources/bullet.svg")))
        bullet_list_button.setToolTip("Bullet List")
        bullet_list_button.clicked.connect(lambda: self.editor_widget.format_text('insertUnorderedList'))
        layout.addWidget(bullet_list_button)
        
        numbered_list_button = ToolbarButton()
        numbered_list_button.setIcon(getColoredIcon(get_resource_path("resources/numbered.svg")))
        numbered_list_button.setToolTip("Numbered List")
        numbered_list_button.clicked.connect(lambda: self.editor_widget.format_text('insertOrderedList'))
        layout.addWidget(numbered_list_button)
        
        align_left = ToolbarButton()
        align_left.setIcon(getColoredIcon(get_resource_path("resources/align_left.svg")))
        align_left.setToolTip("Align Left")
        align_left.clicked.connect(lambda: self.editor_widget.format_text('justifyLeft'))
        layout.addWidget(align_left)
        
        align_center = ToolbarButton()
        align_center.setIcon(getColoredIcon(get_resource_path("resources/align_center.svg")))
        align_center.setToolTip("Center")
        align_center.clicked.connect(lambda: self.editor_widget.format_text('justifyCenter'))
        layout.addWidget(align_center)
        
        align_right = ToolbarButton()
        align_right.setIcon(getColoredIcon(get_resource_path("resources/align_right.svg")))
        align_right.setToolTip("Align Right")
        align_right.clicked.connect(lambda: self.editor_widget.format_text('justifyRight'))
        layout.addWidget(align_right)
        
        justify = ToolbarButton()
        justify.setIcon(getColoredIcon(get_resource_path("resources/justify.svg")))
        justify.setToolTip("Justify")
        justify.clicked.connect(lambda: self.editor_widget.format_text('justifyFull'))
        layout.addWidget(justify)
        
        # Vertical separator after text formatters
        separator2 = QFrame()
        separator2.setFrameShape(QFrame.VLine)
        separator2.setFrameShadow(QFrame.Sunken)
        layout.addWidget(separator2)
        
        # Group 3: Inserter buttons at end
        emoji_button = ToolbarButton()
        emoji_button.setIcon(getColoredIcon(get_resource_path("resources/emoji.svg")))
        emoji_button.setToolTip("Insert Emoji")
        emoji_button.clicked.connect(self.insert_emoji)
        layout.addWidget(emoji_button)
        
        link_button = ToolbarButton()
        link_button.setIcon(getColoredIcon(get_resource_path("resources/link.svg")))
        link_button.setToolTip("Insert Link")
        link_button.clicked.connect(self.insert_link)
        layout.addWidget(link_button)
        
        info_box_btn = ToolbarButton()
        info_box_btn.setIcon(getColoredIcon(get_resource_path("resources/info_box.svg")))
        info_box_btn.setToolTip("Insert Info Box")
        info_box_btn.clicked.connect(self.editor_widget.insert_info_box)
        layout.addWidget(info_box_btn)
        
        image_button = ToolbarButton()
        image_button.setIcon(getColoredIcon(get_resource_path("resources/image.svg")))
        image_button.setToolTip("Insert Image")
        image_button.clicked.connect(self.show_image_dialog)
        layout.addWidget(image_button)
        
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
        from PyQt5.QtWidgets import QInputDialog
        url, ok = QInputDialog.getText(self, "Insert Link", "Enter URL:")
        if ok and url:
            self.editor_widget.format_text('createLink', url)

    def insert_emoji(self):
        from PyQt5.QtWidgets import QInputDialog
        emoji, ok = QInputDialog.getText(self, "Insert Emoji", "Enter Emoji:")
        if ok and emoji:
            js = f"document.execCommand('insertText', false, '{emoji}');"
            self.editor_widget.web_view.page().runJavaScript(js)