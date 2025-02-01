# DocuWeave - Modern Markdown Editor

## Overview
DocuWeave is a modern, WYSIWYG Markdown editor built with Python and PyQt5. It provides a sleek dark-themed interface that lets you edit and preview markdown content in real-time, with an intuitive formatting toolbar.

## Features
- Modern dark-themed UI with rounded corners
- Real-time WYSIWYG markdown editing
- Intuitive formatting toolbar with:
  - Headings (H1, H2, H3)
  - Text styling (Bold, Italic, Underline, Strikethrough)
  - Lists (Bullet and Numbered)
  - Blockquotes
- Smart format handling (prevents nested headings/lists)
- Tab indentation support
- Save as markdown files

## Project Structure
```
DocuWeave
├── app.py              # Application entry point
├── ui/                 # User interface components
│   ├── main_window.py  # Main application window
│   ├── editor_widget.py # WYSIWYG editor component
│   ├── toolbar_widget.py # Formatting toolbar
│   └── custom_webview.py # Custom web view for editor
├── core/              # Core functionality
│   ├── editor.py      # Editor operations
│   └── renderer.py    # Markdown rendering
└── README.md
```

## Installation
1. Clone the repository:
   ```
   git clone https://github.com/yourusername/DocuWeave.git
   ```
2. Navigate to the project directory:
   ```
   cd DocuWeave
   ```
3. Install required dependencies:
   ```
   pip install -r requirements.txt
   ```

## Usage
Run the application:
```
python app.py
```

## Contributing
Contributions are welcome! Feel free to submit issues and pull requests.

## License
This project is licensed under the MIT License.