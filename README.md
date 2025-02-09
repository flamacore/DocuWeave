# DocuWeave

DocuWeave is a lightweight WYSIWYG Markdown Editor built with PyQt5. It offers a modern interface, dynamic theming, and streamlined project management to simplify your document editing experience.



<img width="920" alt="python_PowlkiOfZx" src="https://github.com/user-attachments/assets/627d0215-ee8c-4c3b-87ec-92b31c4becf7" />

https://www.docuweave.website also exists

## Tech Alpha Release

Welcome to the **Tech Alpha Release** of DocuWeave. This release incorporates several significant updates aimed at improving UI scaling, editor performance, and project management workflows. Although it is still in its alpha stage, we encourage you to try out the new features and provide feedback.

### What's New?

- **High DPI and Scaling**  
  Improved support for high-resolution displays ensures that all UI elements render crisply.

- **Enhanced Project Management**  
  Experience faster loading, saving, and renaming of projects with robust file handling and auto-cleanup of orphaned files.

- **Revamped Editing Experience**  
  - New toolbar icons and a refined layout.
  - Table insertion support for richer content.
  - Real-time preview updates with a responsive editing interface.

- **Performance & Stability**  
  Optimizations across the board result in quicker startup times, more efficient resource usage, and better overall responsiveness.

## Getting Started

1. **Clone the Repository:**
   ```
   git clone https://github.com/yourusername/DocuWeave.git
   ```
2. **Install Dependencies:**
   ```
   pip install -r requirements.txt
   ```
3. **Run the Application:**
   ```
   python app.py
   ```

## Changelog

For detailed changes, see [release_files/changelog.md](release_files/changelog.md).

## Contributing & Feedback

Your feedback is invaluable! As we continue to refine this alpha release, please report any issues or suggestions via our issue tracker on GitHub.

## Repository Structure

- **/core/**
  - `renderer.py`: Handles markdown to HTML conversion and manages theme variables.
  - `project.py`: Manages project file handling, saving, and loading of documents.
- **/ui/**
  - `editor_widget.py`: Implements the WYSIWYG editor.
  - `editor_template.html`: HTML template with dynamic placeholders.
  - `toolbar_widget.py`: Contains utilities for managing toolbar icons.
  - `main_window.py`: Sets up the main application window with custom title bar and context menus.
- **/resources/**
  - Contains SVG icons, the app icon, and theming in `dark_theme.qss`.

---

Happy editing and thank you for testing DocuWeave Tech Alpha!

*Uicons by [Flaticon](https://www.flaticon.com/uicons)*
