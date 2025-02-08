import json
import os
from typing import Dict, Optional

class Project:
    def __init__(self):
        self.name: str = "Untitled Project"
        self.documents: Dict[str, str] = {}  # path -> content
        self.current_file: Optional[str] = None
        self.project_path: Optional[str] = None
        self.untitled_counter = 0  # Track number of untitled documents

    def add_document(self, path: str, content: str = "") -> None:
        self.documents[path] = content
        if not self.current_file:
            self.current_file = path

    def remove_document(self, path: str) -> None:
        if path in self.documents:
            del self.documents[path]
            if self.current_file == path:
                self.current_file = next(iter(self.documents)) if self.documents else None

    def create_untitled_document(self) -> str:
        """Creates a new untitled document and returns its ID"""
        # Find the next available number
        counter = 1
        while f"Untitled {counter}" in self.documents:
            counter += 1
            
        doc_id = f"Untitled {counter}"
        self.documents[doc_id] = ""  # Add empty document
        self.current_file = doc_id  # Set as current
        return doc_id

    def save_project(self, filepath: str) -> None:
        self.project_path = filepath
        print(f"\033[94mSaving project to {filepath}\033[0m")
        project_dir = os.path.splitext(filepath)[0]  # Remove .dwproj extension
        os.makedirs(project_dir, exist_ok=True)

        # Clean up old files that are no longer in the project
        if os.path.exists(project_dir):
            existing_files = set(f for f in os.listdir(project_dir) 
                               if f.endswith('.html'))
            
            # Calculate new filenames
            new_files = set()
            for doc_id in self.documents.keys():
                if doc_id.startswith("Untitled "):
                    new_files.add(f"document_{doc_id.split()[-1]}.html")
                else:
                    base_name = os.path.splitext(doc_id)[0]
                    new_files.add(f"{base_name}.html")
            
            # Remove files that are no longer needed
            for old_file in existing_files - new_files:
                try:
                    old_path = os.path.join(project_dir, old_file)
                    os.remove(old_path)
                    print(f"Removed orphaned file: {old_path}")
                except OSError as e:
                    print(f"Error removing old file {old_file}: {e}")

        # Save all documents as files
        saved_documents = {}
        for doc_id, content in self.documents.items():
            if doc_id.startswith("Untitled "):
                file_name = f"document_{doc_id.split()[-1]}.html"
            else:
                # Ensure file has .html extension
                base_name = os.path.splitext(doc_id)[0]  # Remove any existing extension
                file_name = f"{base_name}.html"
            
            file_path = os.path.join(project_dir, file_name)
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            saved_documents[doc_id] = file_path

        # Save project metadata
        project_data = {
            'name': self.name,
            'documents': saved_documents,
            'current_file': self.current_file
        }
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(project_data, f, indent=2)

    def load_project(self, filepath: str) -> None:
        """Load project and read contents of all document files"""
        self.project_path = filepath
        with open(filepath, 'r', encoding='utf-8') as f:
            project_data = json.load(f)
            self.name = project_data['name']
            
            # Clear existing documents
            self.documents = {}
            
            # Load each document's content from its file
            for doc_id, file_path in project_data['documents'].items():
                try:
                    with open(file_path, 'r', encoding='utf-8') as doc_file:
                        self.documents[doc_id] = doc_file.read()
                except FileNotFoundError:
                    print(f"Warning: Document file not found: {file_path}")
                    self.documents[doc_id] = ""  # Create empty document if file missing
            
            self.current_file = project_data['current_file']

    def get_document(self, path: str) -> Optional[str]:
        return self.documents.get(path)

    def update_document(self, path: str, content: str) -> None:
        if path in self.documents:
            self.documents[path] = content

    def rename_document(self, old_name: str, new_name: str) -> bool:
        """Rename a document and clean up old files if needed"""
        if old_name in self.documents and new_name not in self.documents:
            # If we have a project path, clean up the old file
            if self.project_path:
                project_dir = os.path.splitext(self.project_path)[0]
                old_file = os.path.join(project_dir, 
                    f"document_{old_name.split()[-1]}.html" if old_name.startswith("Untitled ") 
                    else os.path.basename(old_name))
                try:
                    if os.path.exists(old_file):
                        os.remove(old_file)
                        print(f"Deleted old file: {old_file}")
                except OSError as e:
                    print(f"Error deleting old file: {e}")

            # Perform the rename in memory
            self.documents[new_name] = self.documents.pop(old_name)
            if self.current_file == old_name:
                self.current_file = new_name
            return True
        return False
