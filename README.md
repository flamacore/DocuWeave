# This is a VERY EARLY PROTOTYPE. Don't use it. Not ready for anything yet.

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
- Customizable themes using QSS:
  - Easily modify the default dark theme or create new ones
  - Real-time theme updates using standard Qt Style Sheet syntax

## Project Structure
```
DocuWeave
├── app.py              # Application entry point
├── ui/                 # User interface components
│   ├── main_window.py  # Main application window
│   ├── editor_widget.py # WYSIWYG editor component
│   ├── toolbar_widget.py # Formatting toolbar
│   ├── project_sidebar.py # Project sidebar
│   ├── custom_webview.py # Custom web view for editor
│   ├── js_bridge.py    # JavaScript bridge for editor
│   └── dark_theme.qss  # Default dark theme
├── core/               # Core functionality
│   ├── editor.py       # Editor operations
│   ├── renderer.py     # Markdown rendering
│   ├── project.py      # Project management
│   └── controller.py   # Controller for editor and renderer
├── requirements.txt    # Project dependencies
└── README.md           # Project documentation
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

## Customization
### Themes
DocuWeave uses Qt Style Sheets (QSS) for theming, making it simple to change the look and feel:
- Copy and modify the default `dark_theme.qss` to create your own theme.
- Adjust properties like colors, borders, and fonts using standard QSS syntax.
- Load your custom theme file in place of the default one for a personalized experience.

Example snippet:
```qss
/* Custom theme example */
QMainWindow {
    background-color: #2e2e2e;
    color: white;
}

#titleBar {
    background-color: #1e1e1e;
    min-height: 50px;
}
```

## Contributing
Contributions are welcome! Feel free to submit issues and pull requests.

## License
This project is licensed under the MIT License.