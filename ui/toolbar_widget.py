
from PyQt5.QtWidgets import QFrame, QHBoxLayout, QPushButton

class ToolbarWidget(QFrame):
    def __init__(self, editor_widget, parent=None):
        super().__init__(parent)
        self.editor_widget = editor_widget
        layout = QHBoxLayout(self)

        h1_button = QPushButton("H1")
        h1_button.clicked.connect(lambda: self.editor_widget.format_text('formatBlock', '<H1>'))
        layout.addWidget(h1_button)

        h2_button = QPushButton("H2")
        h2_button.clicked.connect(lambda: self.editor_widget.format_text('formatBlock', '<H2>'))
        layout.addWidget(h2_button)

        h3_button = QPushButton("H3")
        h3_button.clicked.connect(lambda: self.editor_widget.format_text('formatBlock', '<H3>'))
        layout.addWidget(h3_button)

        normal_button = QPushButton("Normal")
        normal_button.clicked.connect(lambda: self.editor_widget.format_text('formatBlock', '<P>'))
        layout.addWidget(normal_button)

        bold_button = QPushButton("B")
        bold_font = bold_button.font()
        bold_font.setBold(True)
        bold_button.setFont(bold_font)
        bold_button.clicked.connect(lambda: self.editor_widget.format_text('bold'))
        layout.addWidget(bold_button)

        italic_button = QPushButton("I")
        italic_font = italic_button.font()
        italic_font.setItalic(True)
        italic_button.setFont(italic_font)
        italic_button.clicked.connect(lambda: self.editor_widget.format_text('italic'))
        layout.addWidget(italic_button)

        underline_button = QPushButton("U")
        underline_font = underline_button.font()
        underline_font.setUnderline(True)
        underline_button.setFont(underline_font)
        underline_button.clicked.connect(lambda: self.editor_widget.format_text('underline'))
        layout.addWidget(underline_button)

        strike_button = QPushButton("S")
        strike_font = strike_button.font()
        strike_font.setStrikeOut(True)
        strike_button.setFont(strike_font)
        strike_button.clicked.connect(lambda: self.editor_widget.format_text('strikeThrough'))
        layout.addWidget(strike_button)

        quote_button = QPushButton("\"")
        quote_button.clicked.connect(lambda: self.editor_widget.format_text('formatBlock', '<BLOCKQUOTE>'))
        layout.addWidget(quote_button)

        bullet_list_button = QPushButton("Bullet List")
        bullet_list_button.clicked.connect(lambda: self.editor_widget.format_text('insertUnorderedList'))
        layout.addWidget(bullet_list_button)

        numbered_list_button = QPushButton("Numbered List")
        numbered_list_button.clicked.connect(lambda: self.editor_widget.format_text('insertOrderedList'))
        layout.addWidget(numbered_list_button)

        layout.addStretch()
        self.setStyleSheet("background-color: #1e1e1e;")