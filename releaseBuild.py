import os
import json
import subprocess
import zipfile
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
        version = f"{v['major']}.{v['minor']}.{v['patch']}-{v['build']}"
        if v.get('prerelease'):
            version += f"-{v['prerelease']}"
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
    
    def update_version(self):
        self.version_info["patch"] += 1
        self.version_info["build"] += 1
        if self.version_info["patch"] >= 10:
            self.version_info["patch"] = 0
            self.version_info["minor"] += 1
        with open(self.version_file, 'w') as f:
            json.dump(self.version_info, f, indent=4)

    def clean_dist_folder(self):
        if os.path.isdir(self.dist_dir):
            print(f"Cleaning dist folder: {self.dist_dir}")
            shutil.rmtree(self.dist_dir)

    def build_exe(self):
        self.clean_dist_folder()
        self.update_version()
        print("Version updated!")

        self.create_version_file()
        # Run PyInstaller to build the exe
        cmd = [
            "pyinstaller", "--onefile", "--windowed",
            "--add-data", "ui;ui",
            "--add-data", "resources;resources",
            "app.py"
        ]
        subprocess.run(cmd, check=True)
        
        # Locate the built exe; assume it is named 'app.exe' in dist folder
        original_exe = os.path.join(self.dist_dir, "app.exe")
        versioned_exe = os.path.join(self.dist_dir, f"DocuWeave-{self.version_string}.exe")
        os.rename(original_exe, versioned_exe)
        print(f"Renamed exe to: {versioned_exe}")
        
        # Create release zip archive including exe and files under "release_files" folder.
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        zip_name = os.path.join(self.dist_dir, f"DocuWeave-{self.version_string}.zip")
        with zipfile.ZipFile(zip_name, 'w') as zipf:
            zipf.write(versioned_exe, os.path.basename(versioned_exe))
            for fname in ['LICENSE', 'README.md', 'changelog.md']:
                file_path = os.path.join("release_files", fname)
                if os.path.exists(file_path):
                    zipf.write(file_path, fname)
                else:
                    print(f"Warning: {file_path} not found; skipping.")
        print(f"Created release archive: {zip_name}")
        os.remove(versioned_exe)
        print("Removed exe after zipping.")

if __name__ == "__main__":
    builder = DocuWeaveBuild()
    builder.build_exe()
