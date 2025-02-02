import json
import os
import sys
import shutil
from datetime import datetime
import PyInstaller.__main__

class DocuWeaveBuild:
    def __init__(self):
        self.version_file = 'semanticVersion.json'
        self.load_version()
        self.dist_dir = 'dist'
        self.build_dir = 'build'
        self.version_string = self.get_version_string()
        
    def load_version(self):
        with open(self.version_file, 'r') as f:
            self.version_info = json.load(f)
    
    def get_version_string(self):
        v = self.version_info
        version = f"{v['major']}.{v['minor']}.{v['patch']}"
        if v['prerelease']:
            version += f"-{v['prerelease']}.{v['build']}"
        return version
    
    def create_version_file(self):
        """Create version info for Windows executable"""
        version_array = [
            self.version_info['major'],
            self.version_info['minor'],
            self.version_info['patch'],
            self.version_info['build']
        ]
        version_string = ','.join(map(str, version_array))
        
        content = f"""
VSVersionInfo(
  ffi=FixedFileInfo(
    filevers=({version_string}, 0),
    prodvers=({version_string}, 0),
    mask=0x3f,
    flags=0x0,
    OS=0x40004,
    fileType=0x1,
    subtype=0x0,
    date=(0, 0)
  ),
  kids=[
    StringFileInfo(
      [
      StringTable(
        '040904B0',
        [StringStruct('CompanyName', '{self.version_info["author"]}'),
        StringStruct('FileDescription', '{self.version_info["description"]}'),
        StringStruct('FileVersion', '{self.version_string}'),
        StringStruct('InternalName', '{self.version_info["name"]}'),
        StringStruct('LegalCopyright', '{self.version_info["copyright"]}'),
        StringStruct('OriginalFilename', '{self.version_info["name"]}.exe'),
        StringStruct('ProductName', '{self.version_info["name"]}'),
        StringStruct('ProductVersion', '{self.version_string}')])
      ]), 
    VarFileInfo([VarStruct('Translation', [1033, 1200])])
  ]
)
"""
        with open('version_info.txt', 'w') as f:
            f.write(content)
    
    def build_exe(self):
        self.create_version_file()
        PyInstaller.__main__.run([
            'docuweave.pyw',
            '--name=DocuWeave',
            '--windowed',  # No console window
            '--onefile',   # Single executable
            '--icon=resources/icon.ico',  # Add your icon here
            '--add-data=ui/dark_theme.qss;ui',  # Include QSS file
            '--add-data=resources/*;resources',  # Include resources
            '--hidden-import=PyQt5.QtWebEngineWidgets',
            '--hidden-import=PyQt5.QtWebEngine',
            '--hidden-import=markdown',
            '--version-file=version_info.txt',
            '--clean',
            '--noconfirm'
        ])
        os.remove('version_info.txt')  # Clean up temporary version file

if __name__ == "__main__":
    builder = DocuWeaveBuild()
    builder.build_exe()
