import sys, os
import argparse

# Insert the project root directory into sys.path to locate the core package
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Option 1: Use a constant custom scale factor
custom_multiplier = 0.65  # Reduce default scaling factor by 20%
os.environ["QT_SCALE_FACTOR"] = str(custom_multiplier)

# Option 2 (advanced): If you want to derive from screen DPI, you'd need to create a temporary QGuiApplication first.
# However, this approach is more complex since QApplication must be created only once.
#
# from PyQt5.QtGui import QGuiApplication
# temp_app = QGuiApplication(sys.argv)
# screen = temp_app.primaryScreen()
# scale = screen.logicalDotsPerInch() / 96.0
# custom_scale = scale * 0.8  # Adjust the factor as desired
# os.environ["QT_SCALE_FACTOR"] = str(custom_scale)
# temp_app.quit()

from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QDir
from ui.main_window import MainWindow

def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='DocuWeave - WYSIWYG Markdown Editor')
    parser.add_argument('--debug', action='store_true', help='Show console window for debugging')
    args = parser.parse_args()

    # Hide console if not in debug mode
    if not args.debug and sys.platform == 'win32':
        import win32gui, win32con
        import ctypes
        # Get the console window specifically, not the foreground window
        hwnd = ctypes.windll.kernel32.GetConsoleWindow()
        if hwnd != 0:  # Only hide if console window exists
            win32gui.ShowWindow(hwnd, win32con.SW_HIDE)

    app = QApplication(sys.argv)
    
    # Register resources directory
    QDir.addSearchPath('resources', os.path.join(os.path.dirname(__file__), 'resources'))
    
    # Set application icon
    icon_path = os.path.join(os.path.dirname(__file__), "resources", "icon.ico")
    app.setWindowIcon(QIcon(icon_path))
    
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    from PyQt5.QtCore import Qt
    from PyQt5.QtWidgets import QApplication
    # Enable High DPI scaling
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
    main()