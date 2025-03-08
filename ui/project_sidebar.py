from PyQt5.QtWidgets import (QTreeView, QFileDialog, QMenu, QInputDialog,
                           QMessageBox)
from PyQt5.QtGui import QStandardItemModel, QStandardItem, QIcon
from PyQt5.QtCore import Qt, pyqtSignal

class ProjectSidebar(QTreeView):
    # Unified signals for document operations
    item_selected = pyqtSignal(str)  # Path to document
    document_deleted = pyqtSignal(str)  # Path to document
    new_document_requested = pyqtSignal(str)  # Parent document path
    document_created = pyqtSignal(str, str)  # Parent path, document name
    document_renamed = pyqtSignal(str, str)  # old_path, new_path
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.model = QStandardItemModel()
        self.setModel(self.model)
        self.setHeaderHidden(True)
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_context_menu)
        self.clicked.connect(self._on_item_clicked)
        self.setEditTriggers(QTreeView.DoubleClicked |
                           QTreeView.EditKeyPressed)
        self.model.itemChanged.connect(self._on_item_renamed)
        
        # Set up tree behavior
        self.setDragEnabled(True)
        self.setAcceptDrops(True)
        self.setDropIndicatorShown(True)
        self.setDragDropMode(QTreeView.InternalMove)
        
        # Store expanded states
        self.expanded_paths = set()
        self.expanded.connect(self._on_item_expanded)
        self.collapsed.connect(self._on_item_collapsed)
        
        # Flag indicating if a document has children
        self.HAS_CHILDREN_ROLE = Qt.UserRole + 1

    def update_tree(self, project):
        """Update tree with hierarchical document structure from Project"""
        # Store selection and expanded states before clearing
        current = self.currentIndex()
        current_path = current.data(Qt.UserRole) if current.isValid() else None
        
        self.model.clear()
        root = self.model.invisibleRootItem()
        
        # Recursively build tree from root document
        self._build_tree(project.root_document, root, project)
        
        # Restore expansion states
        self._restore_expansion_states(root)
        
        # Restore selection
        if current_path:
            self._restore_selection(root, current_path)

    def _build_tree(self, doc, parent_item, project):
        """Recursively build tree from document structure"""
        # Skip the root document
        if doc.name != "root":
            # Create item for this document
            doc_item = QStandardItem(doc.name)
            doc_item.setData(doc.get_full_path(), Qt.UserRole)
            
            # Set flags based on whether it has children
            has_children = len(doc.children) > 0
            doc_item.setData(has_children, self.HAS_CHILDREN_ROLE)
            
            # Set appropriate icon based on children
            if has_children:
                doc_item.setIcon(QIcon.fromTheme("folder"))
            else:
                doc_item.setIcon(QIcon.fromTheme("text-x-generic"))
            
            parent_item.appendRow(doc_item)
            parent_item = doc_item
        
        # Sort children by name for consistent display
        sorted_children = sorted(doc.children.keys())
        
        # Add children documents
        for child_name in sorted_children:
            child_doc = doc.children[child_name]
            # Recursively process child
            self._build_tree(child_doc, parent_item, project)
    
    def _on_item_expanded(self, index):
        """Track expanded state"""
        if index.isValid():
            path = index.data(Qt.UserRole)
            if path:
                self.expanded_paths.add(path)
    
    def _on_item_collapsed(self, index):
        """Track collapsed state"""
        if index.isValid():
            path = index.data(Qt.UserRole)
            if path and path in self.expanded_paths:
                self.expanded_paths.remove(path)
    
    def _restore_expansion_states(self, parent_item):
        """Recursively restore expansion states"""
        row_count = parent_item.rowCount()
        for row in range(row_count):
            item = parent_item.child(row)
            if not item:
                continue
                
            path = item.data(Qt.UserRole)
            has_children = item.data(self.HAS_CHILDREN_ROLE)
            
            # Only expand documents with children
            if has_children and path in self.expanded_paths:
                index = self.model.indexFromItem(item)
                self.setExpanded(index, True)
            
            # Check children
            self._restore_expansion_states(item)
    
    def _restore_selection(self, parent_item, path_to_select):
        """Recursively find and select an item by path"""
        if not path_to_select:
            return

        # Iterate through the children of the parent item
        for row in range(parent_item.rowCount()):
            child = parent_item.child(row)
            if not child:
                continue
                
            item_path = child.data(Qt.UserRole)
            if item_path == path_to_select:
                # Found the item, select it and make sure it's visible
                index = self.model.indexFromItem(child)
                self.setCurrentIndex(index)
                self.scrollTo(index)
                return True
            elif path_to_select.startswith(item_path + '/'):
                # Path is under this item, expand it and recursively search
                index = self.model.indexFromItem(child)
                self.setExpanded(index, True)
                if self._restore_selection(child, path_to_select):
                    return True

        return False

    def _on_item_clicked(self, index):
        """Handle item click - emit signal for document"""
        if not index.isValid():
            return
            
        path = index.data(Qt.UserRole)
        if path:
            # Emit the item_selected signal for the document
            self.item_selected.emit(path)

    def _on_item_renamed(self, item):
        """Handle item rename events"""
        if item is None:
            return
            
        try:
            old_path = item.data(Qt.UserRole)
            new_name = item.text()
            
            # Calculate new path based on parent
            parent = item.parent() or self.model.invisibleRootItem()
            parent_path = parent.data(Qt.UserRole) if parent != self.model.invisibleRootItem() else ""
            
            if parent_path:
                new_path = f"{parent_path}/{new_name}"
            else:
                new_path = new_name
            
            if old_path != new_path:
                # Block signals to prevent recursive calls
                self.model.blockSignals(True)
                
                # Emit document renamed signal
                self.document_renamed.emit(old_path, new_path)
                
                # The update_tree method should be called from MainWindow after rename
                self.model.blockSignals(False)
        except Exception as e:
            # Restore the model and show error
            print(f"Error during rename: {e}")
            self.model.blockSignals(False)
            QMessageBox.warning(self, "Rename Error", 
                               f"An error occurred during renaming: {str(e)}")

    def show_context_menu(self, position):
        """Show context menu with actions appropriate for documents"""
        index = self.indexAt(position)
        menu = QMenu()
        menu.setObjectName("projectSidebarMenu")
        
        # Default action - new document at root
        new_doc_action = menu.addAction("New Document")
        
        # Include item-specific actions if an item is selected
        delete_action = None
        rename_action = None
        
        if index.isValid():
            menu.addSeparator()
            rename_action = menu.addAction("Rename")
            delete_action = menu.addAction("Delete")
            
            path = index.data(Qt.UserRole)
            
            # Add document-specific actions
            menu.addSeparator()
            new_child_doc_action = menu.addAction("New Child Document")
        
        # Show menu and handle action
        action = menu.exec_(self.mapToGlobal(position))
        
        # Handle the selected action
        if not action:
            return
            
        # Global actions
        if action == new_doc_action:
            self.new_document_requested.emit("")  # Empty path for root
            return
        
        # Item-specific actions (only available if index is valid)
        if not index.isValid():
            return
            
        path = index.data(Qt.UserRole)
            
        if action == delete_action:
            self._delete_document(path)
        elif action == rename_action:
            self.edit(index)  # Use built-in editor
        elif action == locals().get('new_child_doc_action'):
            self.new_document_requested.emit(path)

    def _delete_document(self, path):
        """Delete a document after confirmation"""
        reply = QMessageBox.question(
            self, 
            "Delete Document", 
            f"Are you sure you want to delete '{path}' and all its contents?",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            self.document_deleted.emit(path)
