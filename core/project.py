import json
import os
from typing import Dict, Optional, List, Any

class Document:
    def __init__(self, name: str, content: str = "", parent_path: str = ""):
        self.name = name
        self.content = content
        self.parent_path = parent_path  # Path to parent document
        self.children: Dict[str, 'Document'] = {}  # name -> Document (children documents)
    
    def get_full_path(self) -> str:
        """Get full path including parent path"""
        if self.parent_path:
            return f"{self.parent_path}/{self.name}"
        return self.name
    
    def add_child(self, doc: 'Document') -> None:
        """Add child document to this document"""
        self.children[doc.name] = doc
    
    def get_child(self, name: str) -> Optional['Document']:
        """Get child document by name"""
        return self.children.get(name)
    
    def remove_child(self, name: str) -> bool:
        """Remove child document by name"""
        if name in self.children:
            del self.children[name]
            return True
        return False
    
    def rename_child(self, old_name: str, new_name: str) -> bool:
        """Rename a child document"""
        if old_name in self.children and new_name not in self.children:
            doc = self.children[old_name]
            doc.name = new_name
            self.children[new_name] = doc
            del self.children[old_name]
            return True
        return False
    
    def to_dict(self) -> dict:
        """Convert to serializable dictionary"""
        return {
            "name": self.name,
            "content": self.content,
            "parent_path": self.parent_path,
            "children": {name: doc.to_dict() for name, doc in self.children.items()}
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Document':
        """Create document from dictionary data"""
        doc = cls(
            name=data["name"],
            content=data.get("content", ""),
            parent_path=data.get("parent_path", "")
        )
        
        # Load children documents
        for name, child_data in data.get("children", {}).items():
            doc.children[name] = cls.from_dict(child_data)
        
        return doc

class Project:
    def __init__(self):
        self.name: str = "Untitled Project"
        self.root_document = Document("root")  # Root document contains all other documents
        self.current_document: Optional[str] = None  # Full path to current document
        self.project_path: Optional[str] = None  # Path to .dwproj file
        self.untitled_counter = 0  # Track number of untitled documents
    
    def get_document_by_path(self, path: str) -> Optional[Document]:
        """Get document by its full path"""
        if not path:
            return self.root_document
        
        # Split path into components
        path_parts = path.split('/')
        
        # Navigate document structure
        current_doc = self.root_document
        for i in range(len(path_parts)):
            doc_name = path_parts[i]
            current_doc = current_doc.get_child(doc_name)
            if current_doc is None:
                return None
        
        return current_doc
    
    def get_content(self, path: str) -> Optional[str]:
        """Get document content by path"""
        doc = self.get_document_by_path(path)
        return doc.content if doc else None
    
    def update_content(self, path: str, content: str) -> bool:
        """Update document content by path"""
        doc = self.get_document_by_path(path)
        if doc:
            doc.content = content
            return True
        return False
    
    def has_children(self, path: str) -> bool:
        """Check if a document has children"""
        doc = self.get_document_by_path(path)
        return doc is not None and len(doc.children) > 0
    
    def create_document(self, name: str, content: str = "", parent_path: str = "") -> str:
        """Create a new document at the specified parent path"""
        # Get or create parent document path
        parent_doc = self._ensure_document_path(parent_path)
        
        # Create document
        doc = Document(name=name, content=content, parent_path=parent_path)
        parent_doc.add_child(doc)
        
        # Set as current if no current document
        full_path = doc.get_full_path()
        if not self.current_document:
            self.current_document = full_path
        
        return full_path
    
    def _ensure_document_path(self, path: str) -> Document:
        """Ensure document path exists, creating if necessary"""
        if not path:
            return self.root_document
        
        # Split path into components
        path_parts = path.split('/')
        
        # Navigate and create document structure as needed
        current_doc = self.root_document
        current_path = ""
        
        for doc_name in path_parts:
            if current_path:
                current_path += "/" + doc_name
            else:
                current_path = doc_name
                
            next_doc = current_doc.get_child(doc_name)
            if next_doc is None:
                # Create missing document
                next_doc = Document(name=doc_name, parent_path=current_path[:-len(doc_name)-1] if len(current_path) > len(doc_name) else "")
                current_doc.add_child(next_doc)
            
            current_doc = next_doc
        
        return current_doc

    def create_untitled_document(self, parent_path: str = "") -> str:
        """Creates a new untitled document and returns its path"""
        # Find the next available number
        counter = 1
        parent_doc = self._ensure_document_path(parent_path)
        
        while f"Untitled {counter}" in parent_doc.children:
            counter += 1
            
        doc_name = f"Untitled {counter}"
        return self.create_document(doc_name, "", parent_path)

    def remove_document(self, path: str) -> bool:
        """Remove document by path"""
        if not path:  # Can't remove root document
            return False
            
        parts = path.split('/')
        parent_path = '/'.join(parts[:-1]) if len(parts) > 1 else ""
        doc_name = parts[-1]
        
        parent_doc = self.get_document_by_path(parent_path)
        if parent_doc and parent_doc.remove_child(doc_name):
            if self.current_document == path or self.current_document and self.current_document.startswith(path + '/'):
                # Find another document to set as current
                if parent_doc.children:
                    # Use first document in current parent
                    doc_name = next(iter(parent_doc.children))
                    doc = parent_doc.children[doc_name]
                    self.current_document = doc.get_full_path()
                else:
                    # No documents in this parent, use the parent itself
                    self.current_document = parent_path if parent_path else self._find_any_document_path()
            return True
        return False

    def _find_any_document_path(self) -> Optional[str]:
        """Find any document in the project to set as current"""
        # Helper function to search recursively
        def find_path(doc: Document, path_prefix: str) -> Optional[str]:
            # First, return this document if it's not the root
            if doc.name != "root":
                return path_prefix
                
            # Check children documents
            if doc.children:
                doc_name = next(iter(doc.children))
                child_doc = doc.children[doc_name]
                return child_doc.get_full_path()
            
            return None
        
        return find_path(self.root_document, "")

    def _get_all_document_paths(self) -> List[str]:
        """Get paths to all documents in the project"""
        result = []
        
        def collect_paths(doc: Document, path_prefix: str):
            # Add this document if it's not the root
            if doc.name != "root":
                result.append(path_prefix)
            
            # Process children documents
            for child_name, child_doc in doc.children.items():
                child_path = f"{path_prefix}/{child_name}" if path_prefix else child_name
                collect_paths(child_doc, child_path)
        
        collect_paths(self.root_document, "")
        return result
    
    def save_project(self, filepath: str) -> None:
        """Save project to disk"""
        self.project_path = filepath
        print(f"\033[94mSaving project to {filepath}\033[0m")
        project_dir = os.path.splitext(filepath)[0]  # Remove .dwproj extension
        os.makedirs(project_dir, exist_ok=True)

        # Save all documents to files
        saved_documents = {}
        
        def save_documents(doc: Document, doc_path: str = ""):
            # Skip root document
            if doc.name != "root":
                # Create directory for document if it has children
                if doc.children:
                    os.makedirs(os.path.join(project_dir, doc_path), exist_ok=True)
                
                # Save document content
                file_path = os.path.join(project_dir, f"{doc_path}/__content.html")
                os.makedirs(os.path.dirname(file_path), exist_ok=True)
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(doc.content)
                saved_documents[doc_path] = file_path
            
            # Process children documents
            for child_name, child_doc in doc.children.items():
                child_path = f"{doc_path}/{child_name}" if doc_path else child_name
                save_documents(child_doc, child_path)
        
        # Start saving from root document
        save_documents(self.root_document)
        
        # Clean up old files that are no longer in the project
        self._cleanup_orphaned_files(project_dir, saved_documents)

        # Save project metadata
        project_data = {
            'name': self.name,
            'documents': saved_documents,
            'current_document': self.current_document,
            'document_structure': self.root_document.to_dict()
        }
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(project_data, f, indent=2)

    def _cleanup_orphaned_files(self, project_dir: str, saved_documents: Dict[str, str]):
        """Remove files that are no longer part of the project"""
        # Get set of files that should exist
        expected_files = set(os.path.relpath(path, project_dir) for path in saved_documents.values())
        
        # Walk directory and remove orphaned files
        for root, dirs, files in os.walk(project_dir):
            for file in files:
                if file.endswith('.html'):
                    rel_path = os.path.relpath(os.path.join(root, file), project_dir)
                    if rel_path not in expected_files and file != "index.html": # Don't delete index.html
                        try:
                            os.remove(os.path.join(root, file))
                            print(f"Removed orphaned file: {rel_path}")
                        except OSError as e:
                            print(f"Error removing old file {rel_path}: {e}")

    def load_project(self, filepath: str) -> None:
        """Load project and read contents of all document files"""
        self.project_path = filepath
        with open(filepath, 'r', encoding='utf-8') as f:
            project_data = json.load(f)
            self.name = project_data['name']
            
            # Check if we have new document structure format
            if 'document_structure' in project_data:
                # New format with unified document structure
                self.root_document = Document.from_dict(project_data['document_structure'])
                
                # Load document contents
                for doc_path, file_path in project_data.get('documents', {}).items():
                    try:
                        with open(file_path, 'r', encoding='utf-8') as doc_file:
                            doc = self.get_document_by_path(doc_path)
                            if doc:
                                doc.content = doc_file.read()
                    except FileNotFoundError:
                        print(f"Warning: Document file not found: {file_path}")
            else:
                # Legacy format with separate folders/documents
                self.root_document = Document("root")
                
                # Convert legacy format to new unified document structure
                self._convert_legacy_format(project_data)
            
            self.current_document = project_data.get('current_document')
            if not self.current_document:
                # Try to find any document to use as current
                self.current_document = self._find_any_document_path()
    
    def _convert_legacy_format(self, project_data):
        """Convert legacy format with folders/documents to new unified document structure"""
        # Process folders first to establish hierarchy
        folders = {}
        for folder_path, folder_info in project_data.get('folders', {}).items():
            # Create folder documents with their content
            try:
                with open(folder_info, 'r', encoding='utf-8') as f:
                    folder_content = f.read()
            except FileNotFoundError:
                folder_content = ""
            
            if folder_path:
                parts = folder_path.split('/')
                parent_path = '/'.join(parts[:-1]) if len(parts) > 1 else ""
                folder_name = parts[-1]
                
                # Create document for this folder
                parent_doc = self._ensure_document_path(parent_path)
                folder_doc = Document(name=folder_name, content=folder_content, parent_path=parent_path)
                parent_doc.add_child(folder_doc)
                folders[folder_path] = folder_doc
        
        # Process documents and add to their parent folders
        for doc_path, file_path in project_data.get('documents', {}).items():
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    doc_content = f.read()
            except FileNotFoundError:
                doc_content = ""
                
            parts = doc_path.split('/')
            parent_path = '/'.join(parts[:-1]) if len(parts) > 1 else ""
            doc_name = parts[-1]
            
            # Create document under parent
            parent_doc = self._ensure_document_path(parent_path)
            doc = Document(name=doc_name, content=doc_content, parent_path=parent_path)
            parent_doc.add_child(doc)
    
    def update_document_links(self, old_path: str, new_path: str) -> None:
        """Update docuweave://document/ links in all documents when a document path changes"""
        import re
        
        # Create search pattern for links to the old path
        # This handles both exact matches and child documents
        # We need to handle URL-encoded paths as well
        from urllib.parse import quote
        
        # Function to update links in a single document
        def update_links_in_document(doc: Document):
            if not doc.content:
                return
                
            # Pattern for exact match
            exact_pattern = f'docuweave://document/{re.escape(old_path)}"'
            replacement = f'docuweave://document/{new_path}"'
            doc.content = re.sub(exact_pattern, replacement, doc.content)
            
            # Pattern for child documents
            if old_path:  # Only if old_path is not empty
                child_pattern = f'docuweave://document/{re.escape(old_path)}/'
                child_replacement = f'docuweave://document/{new_path}/'
                doc.content = re.sub(child_pattern, child_replacement, doc.content)
                
            # URL-encoded versions
            encoded_old_path = quote(old_path)
            encoded_new_path = quote(new_path)
            
            exact_encoded_pattern = f'docuweave://document/{encoded_old_path}"'
            encoded_replacement = f'docuweave://document/{encoded_new_path}"'
            doc.content = re.sub(exact_encoded_pattern, encoded_replacement, doc.content)
            
            if old_path:  # Only if old_path is not empty
                child_encoded_pattern = f'docuweave://document/{encoded_old_path}/'
                child_encoded_replacement = f'docuweave://document/{encoded_new_path}/'
                doc.content = re.sub(child_encoded_pattern, child_encoded_replacement, doc.content)
        
        # Process all documents recursively
        def process_documents(doc):
            # Update links in this document
            if doc.name != "root":
                update_links_in_document(doc)
                
            # Process children
            for child in doc.children.values():
                process_documents(child)
        
        # Start processing from root
        process_documents(self.root_document)

    def rename_document(self, old_path: str, new_path: str) -> bool:
        """Rename a document or move it to a different parent"""
        # Skip root
        if not old_path:
            return False
            
        # Extract old and new parent paths and document names
        old_parts = old_path.split('/')
        new_parts = new_path.split('/')
        
        old_parent_path = '/'.join(old_parts[:-1]) if len(old_parts) > 1 else ""
        old_name = old_parts[-1]
        
        new_parent_path = '/'.join(new_parts[:-1]) if len(new_parts) > 1 else ""
        new_name = new_parts[-1]
        
        # Get the document
        doc = self.get_document_by_path(old_path)
        if not doc:
            return False
        
        # If old and new parent paths are the same, simple rename within parent
        if old_parent_path == new_parent_path:
            parent_doc = self.get_document_by_path(old_parent_path)
            if parent_doc and parent_doc.rename_child(old_name, new_name):
                # Update document's name
                doc.name = new_name
                
                # Update current_document reference if needed
                if self.current_document == old_path:
                    self.current_document = new_path
                elif self.current_document and self.current_document.startswith(old_path + '/'):
                    # Update paths of documents inside this one
                    self.current_document = new_path + self.current_document[len(old_path):]
                
                # Update parent_path for all children
                self._update_child_paths(doc, new_parent_path)
                
                # Update any internal links to this document
                self.update_document_links(old_path, new_path)
                
                return True
        else:
            # Moving document between parents
            old_parent = self.get_document_by_path(old_parent_path)
            new_parent = self._ensure_document_path(new_parent_path)
            
            if old_parent and new_parent and old_name in old_parent.children:
                # Get document content and children
                content = doc.content
                children = doc.children.copy()
                
                # Remove from old parent
                old_parent.remove_child(old_name)
                
                # Create in new parent with new name
                new_doc = Document(name=new_name, content=content, parent_path=new_parent_path)
                new_parent.add_child(new_doc)
                
                # Move all children to new document
                for child_name, child_doc in children.items():
                    child_doc.parent_path = new_path
                    new_doc.children[child_name] = child_doc
                
                # Update all children's parent paths recursively
                self._update_child_paths(new_doc, new_parent_path)
                
                # Update current_document reference if needed
                if self.current_document == old_path:
                    self.current_document = new_path
                elif self.current_document and self.current_document.startswith(old_path + '/'):
                    # Current document was inside the moved document
                    relative_path = self.current_document[len(old_path) + 1:]
                    self.current_document = f"{new_path}/{relative_path}"
                
                # Update any internal links to this document
                self.update_document_links(old_path, new_path)
                
                return True
                
        return False
    
    def _update_child_paths(self, doc: Document, parent_path: str):
        """Recursively update parent_path for a document and all its children"""
        # Update this document's parent_path
        doc_path = f"{parent_path}/{doc.name}" if parent_path else doc.name
        doc.parent_path = parent_path
        
        # Update parent_path for all children documents
        for child_doc in doc.children.values():
            child_doc.parent_path = doc_path
            # Recursively update grandchildren
            self._update_child_paths(child_doc, doc_path)
            
    def get_all_documents(self) -> Dict[str, str]:
        """Get a dictionary of all documents for compatibility with old code"""
        result = {}
        
        def collect_documents(doc: Document):
            # Skip root document
            if doc.name != "root":
                result[doc.get_full_path()] = doc.content
            
            # Collect children documents
            for child_doc in doc.children.values():
                collect_documents(child_doc)
        
        collect_documents(self.root_document)
        return result
