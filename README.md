# DocuWeave

DocuWeave is a lightweight WYSIWYG markdown editor with project management and dynamic theming.

https://docuweave.website also exists but there's not much there :)
<img width="1045" alt="DocuWeave-0 1 0-12-tech-alpha_zLhFM2TUQk" src="https://github.com/user-attachments/assets/193f9977-c3be-472e-a79d-b8d594b78f16" />

## Features

- **Markdown Rendering**: Converts markdown to HTML via a custom `Renderer`.
- **WYSIWYG Editor**: Editable content is managed by `EditorWidget`, which supports images, info boxes, and live content updates.
- **Dynamic Theming**: 
  - Theme variables are defined in `dark_theme.qss` and injected into the HTML template.
  - CSS variables for colors, fonts, spacing, etc. enable easy customization.
- **Project Management**: Supports project creation, saving, and loading with file management via a sidebar.
- **Custom Window Frame**: Modern frameless, translucent UI with a custom title bar and context menus.

## Repository Structure

- **/core/**
  - `renderer.py`: Renders markdown to HTML and extracts CSS theme variables.
  - `project.py`: Manages project files and document storage.
- **/ui/**
  - `editor_widget.py`: Contains the WYSIWYG editor implementation.
  - `editor_template.html`: HTML template with placeholders for content and theme variables.
  - `toolbar_widget.py`: Contains SVG icon utilities (including optional stroke).
  - `main_window.py`: Manages the overall window layout and custom title bar.
  - Other UI components (custom_webview, project_sidebar, startup_dialog, etc.).
- **/resources/**
  - Includes SVG files for toolbar icons and the app icon.

## Setup & Running

1. Install dependencies (e.g., PyQt5 and markdown).
   ```
   pip install -r requirements.txt
   ```
2. Run the main application:
   ```
   python app.py
   ```
3. Enjoy the live preview in the editor.

## Recent Updates

- **SVG Icon Stroke**: Added support for an optional stroke in SVG icons for improved visual appearance.
- **Enhanced Theming**: Dynamic injection of CSS variables from QSS and proper escaping for Python string formatting.
- **Toolbar Improvements**: Added more icons and improved the toolbar layout.

_For more details, refer to the inline comments in the source files._

Happy editing!

Uicons by <a href="https://www.flaticon.com/uicons">Flaticon</a>
