# DocuWeave

DocuWeave is a lightweight WYSIWYG Markdown Editor built with PyQt5. It offers a modern interface, dynamic theming, and streamlined project management to simplify your document editing experience.

![image](https://github.com/user-attachments/assets/e544e293-eaf5-49bb-82a0-eeeff4b4ed70)

https://www.docuweave.website also exists

## Tech Alpha Release

Welcome to the **Tech Alpha Release** of DocuWeave. This release incorporates several significant updates aimed at improving UI scaling, editor performance, and project management workflows. Although it is still in its alpha stage, we encourage you to try out the new features and provide feedback.

### What's New?


- **Document Hierarchy & Linking**  
  - Create nested document structures with parent-child relationships
  - Internal document linking with automatic path updates when documents are renamed
  - Improved navigation between related documents
  - Automatic sidebar selection when following document links

- **Performance & Stability**  
  Optimizations across the board result in quicker startup times, more efficient resource usage, and better overall responsiveness.

## Features

- **WYSIWYG Editor:** Edit rich text with formatting, tables, images, and more
- **Document Hierarchy:** Organize your content with nested document structure
- **Internal Links:** Create links between documents that update automatically when documents are renamed
- **Modern UI:** Dark theme interface with intuitive controls
- **Real-time Formatting:** Format text as you type with the formatting toolbar
- **Project Management:** Save and organize your documents in project files
- **Emoji Support:** Insert emoji from a built-in picker
- **Table Support:** Create and edit tables within your documents
- **Info Boxes:** Add highlighted information boxes for important notes
- **Responsive Layout:** Works well on different screen sizes and resolutions

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
  - `controller.py`: Manages interactions between editor and renderer components.
  - `editor.py`: Core document editing functionality.
  - `project.py`: Manages project files, documents, and workspace organization.
  - `renderer.py`: Handles HTML rendering and theme management.

- **/ui/**
  - `editor_widget.py`: WYSIWYG editor implementation with real-time preview.
  - `toolbar_widget.py`: Rich text formatting toolbar with customizable actions.
  - `main_window.py`: Modern window management with custom title bar.
  - `project_sidebar.py`: Document tree and project navigation.
  - `emoji_selector.py`: SVG-based emoji picker with local caching.
  - `table_dialog.py`: Table insertion interface.
  - `image_dialog.py`: Image upload and URL insertion dialog.
  - `link_type_dialog.py`: Dialog for selecting between external and internal links.
  - `external_link_dialog.py`: Dialog for creating external links.
  - `internal_link_dialog.py`: Dialog for creating internal document links.
  - `startup_dialog.py`: Initial project creation/loading interface.
  - **assets/**
    - Editor templates and JavaScript utilities.

- **/resources/**
  - SVG icons for toolbar and UI elements.
  - Dark theme styling in `dark_theme.qss`.
  - Application icon and branding assets.

- **/build/**
  - Build artifacts and distribution files.

- **/release_files/**
  - Release documentation and changelogs.

## Development

DocuWeave is developed with assistance from GitHub Copilot, leveraging various AI models and agents to enhance code quality and feature implementation. This collaborative approach between human developers and AI assistance has helped create a more robust and feature-rich application while maintaining clean code practices.

### Building from Source

To build a signed executable:

1. Generate a self-signed certificate (PowerShell):
   ```powershell
   New-SelfSignedCertificate -Type Custom -Subject "CN=DocuWeave" -KeyUsage DigitalSignature -FriendlyName "DocuWeave" -CertStoreLocation "Cert:\CurrentUser\My" -TextExtension @("2.5.29.37={text}1.3.6.1.5.5.7.3.3", "2.5.29.19={text}")
   ```

2. Export the certificate to PFX:
   ```powershell
   $pwd = ConvertTo-SecureString -String "YourPassword" -Force -AsPlainText
   Get-ChildItem -Path "Cert:\CurrentUser\My\YOUR_CERT_THUMBPRINT" | Export-PfxCertificate -FilePath DocuWeave.pfx -Password $pwd
   ```

3. Run the release build:
   ```
   python releaseBuild.py
   ```

The build script will automatically handle version increments, signing, and packaging.

---

Happy editing and thank you for testing DocuWeave Tech Alpha!

*Uicons by [Flaticon](https://www.flaticon.com/uicons)*
*Emojis by [Twitter Emoji (Twemoji)](https://github.com/twitter/twemoji)*
