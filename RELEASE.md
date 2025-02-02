### Steps to Build and Release

1. **Install Requirements:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Create Resources:**
   - Ensure you have an `icon.ico` in the `resources` folder.
   - Ensure the `ui/dark_theme.qss` file exists.

3. **Run the Build Script:**
   ```bash
   python releaseBuild.py
   ```

4. **Executable Location:**
   - The executable will be created in the `dist` folder.

5. **Release on GitHub:**
   - Create a new release on GitHub.
   - Upload the executable.
   - Include the following files in a zip:
     - `DocuWeave.exe`
     - `README.md` with installation & usage instructions
     - `LICENSE` file
     - `changelog.md` (optional)

### Example Release Notes

## DocuWeave v1.0.0-alpha.1

### Installation
1. Download `DocuWeave.exe`
2. Place it in a dedicated folder
3. Run `DocuWeave.exe`

### Requirements
- Windows 10/11
- No additional installation needed - everything is bundled in the exe

### Features
- WYSIWYG Markdown Editor
- Project-based document management
- Dark theme
- Image support with resize capabilities
- Real-time saving
