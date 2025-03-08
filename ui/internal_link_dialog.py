import sys
import ctypes
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                            QPushButton, QTreeView, QAbstractItemView)
from PyQt5.QtGui import QStandardItemModel, QStandardItem, QIcon
from PyQt5.QtCore import Qt, pyqtSignal

# Enable high DPI awareness on Windows
if sys.platform == "win32":
    try:
        ctypes.windll.shcore.SetProcessDpiAwareness(1)
    except Exception:
        pass

class InternalLinkDialog(QDialog):
    """Dialog for selecting an internal document to link to"""
    
    def __init__(self, project, parent=None):
        super().__init__(parent)
        self.project = project
        self.selected_path = None
        
        self.setWindowTitle("Link to Document")
        # Set fixed size similar to other dialogs
        self.setFixedSize(600, 400)
        self.setWindowFlags(Qt.Dialog | Qt.WindowTitleHint)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Title
        title = QLabel("Select Document to Link")
        title.setStyleSheet("font-size: 24px; margin-bottom: 20px;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # Instructions
        instructions = QLabel("Select a document from your project to create an internal link:")
        instructions.setStyleSheet("font-size: 14px;")
        layout.addWidget(instructions)
        
        # Document tree
        self.tree_view = QTreeView()
        self.tree_view.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.tree_view.setSelectionMode(QAbstractItemView.SingleSelection)
        self.tree_view.setHeaderHidden(True)
        self.tree_view.setStyleSheet("font-size: 14px;")
        layout.addWidget(self.tree_view)
        
        # Populate tree with documents
        self.populate_tree()
        
        # Action buttons
        button_layout = QHBoxLayout()
        self.link_button = QPushButton("Link")
        self.cancel_button = QPushButton("Cancel")
        
        # Style buttons consistently with other dialogs
        for btn in (self.link_button, self.cancel_button):
            btn.setStyleSheet("font-size: 14px;")
            btn.setFixedHeight(35)
            
        button_layout.addStretch()
        button_layout.addWidget(self.link_button)
        button_layout.addWidget(self.cancel_button)
        layout.addLayout(button_layout)
        
        self.link_button.clicked.connect(self.accept)
        self.cancel_button.clicked.connect(self.reject)
        
        # Connect tree selection
        self.tree_view.clicked.connect(self.on_tree_item_clicked)
        
        # Initially disable link button until selection is made
        self.link_button.setEnabled(False)
        
    def populate_tree(self):
        """Populate tree with documents from project"""
        self.model = QStandardItemModel()
        root_item = self.model.invisibleRootItem()
        
        # Add all documents to the tree
        self._add_documents_to_tree(root_item)
        
        self.tree_view.setModel(self.model)
        self.tree_view.expandAll()
        
    def _add_documents_to_tree(self, root_item):
        """Add all documents to tree recursively"""
        all_docs = self.project.get_all_documents()
        
        # Create a dictionary representation of the tree
        tree_dict = {}
        
        for doc_path in all_docs:
            if not doc_path:  # Skip empty paths
                continue
                
            path_parts = doc_path.split('/')
            current_dict = tree_dict
            
            # Build path in tree dictionary
            for i, part in enumerate(path_parts):
                if part not in current_dict:
                    current_dict[part] = {}
                
                if i < len(path_parts) - 1:
                    current_dict = current_dict[part]
        
        # Recursively build tree from dictionary
        self._build_tree_from_dict(tree_dict, root_item, "")
        
    def _build_tree_from_dict(self, tree_dict, parent_item, current_path):
        """Build tree items from dictionary recursively"""
        for key, children in sorted(tree_dict.items()):
            # Create path for this item
            if current_path:
                item_path = f"{current_path}/{key}"
            else:
                item_path = key
                
            # Create item for this document
            item = QStandardItem(key)
            item.setData(item_path, Qt.UserRole)
            
            # Set icon based on whether it has children
            if children:
                item.setIcon(QIcon.fromTheme("folder"))
            else:
                item.setIcon(QIcon.fromTheme("text-x-generic"))
                
            parent_item.appendRow(item)
            
            # Add children
            if children:
                self._build_tree_from_dict(children, item, item_path)
    
    def on_tree_item_clicked(self, index):
        """Handle tree item selection"""
        if index.isValid():
            self.selected_path = index.data(Qt.UserRole)
            self.link_button.setEnabled(True)
            
    def get_selected_path(self):
        """Return the selected document path"""
        return self.selected_path
