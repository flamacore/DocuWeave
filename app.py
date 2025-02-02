import sys, os
import argparse

# Insert the project root directory into sys.path to locate the core package
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from PyQt5.QtWidgets import QApplication
from ui.main_window import MainWindow

def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='DocuWeave - WYSIWYG Markdown Editor')
    parser.add_argument('--debug', action='store_true', help='Show console window for debugging')
    args = parser.parse_args()

    # Hide console if not in debug mode
    if not args.debug and sys.platform == 'win32':
        import win32gui, win32con
        hwnd = win32gui.GetForegroundWindow()
        win32gui.ShowWindow(hwnd, win32con.SW_HIDE)

    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()