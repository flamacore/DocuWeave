from PyQt5.QtWidgets import (QTreeView, QFileDialog, QMenu, QInputDialog,
                           QMessageBox)
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from PyQt5.QtCore import Qt, pyqtSignal

class ProjectSidebar(QTreeView):
    file_selected = pyqtSignal(str)
    file_deleted = pyqtSignal(str)
    new_file_requested = pyqtSignal()
    file_renamed = pyqtSignal(str, str)  # old_name, new_name
    
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
        # Removed inline stylesheet; now handled in QSS

    def update_tree(self, documents):
        """Update tree while preserving selection and expansion states"""
        current = self.currentIndex()
        current_doc = current.data(Qt.UserRole) if current.isValid() else None

        self.model.clear()
        root = self.model.invisibleRootItem()
        
        # Sort documents with Untitled at the end
        sorted_docs = sorted(documents.keys(), 
                           key=lambda x: (x.startswith("Untitled "), 
                                        int(x.split()[-1]) if x.startswith("Untitled ") else 0,
                                        x))
        
        for doc_id in sorted_docs:
            item = QStandardItem(doc_id)
            item.setData(doc_id, Qt.UserRole)
            root.appendRow(item)
            
            # Restore selection if this was the previously selected document
            if doc_id == current_doc:
                self.setCurrentIndex(item.index())

    def _on_item_clicked(self, index):
        path = index.data(Qt.UserRole)
        if path:
            self.file_selected.emit(path)

    def _on_item_renamed(self, item):
        """Handle document rename events safely"""
        if item is None:
            return
            
        old_name = item.data(Qt.UserRole)
        new_name = item.text()
        
        print(f"Rename attempt: {old_name} -> {new_name}")  # Debug log
        
        if old_name != new_name:
            # Block signals to prevent recursive calls
            self.model.blockSignals(True)
            
            # Emit signal first, before updating the model
            self.file_renamed.emit(old_name, new_name)
            
            # Now update the item's data
            item.setData(new_name, Qt.UserRole)
            
            self.model.blockSignals(False)

    def show_context_menu(self, position):
        menu = QMenu()
        menu.setStyleSheet("""
            QMenu {
                background-color: #2d2d2d;
                color: white;
                border: 1px solid #3d3d3d;
            }
            QMenu::item:selected {
                background-color: #094771;
            }
        """)
        
        new_file = menu.addAction("New Document")
        delete_doc = menu.addAction("Delete Document")
        
        action = menu.exec_(self.mapToGlobal(position))
        
        if action == new_file:
            self.new_file_requested.emit()
            return  # Add return to prevent any other processing
        elif action == delete_doc:
            index = self.indexAt(position)
            if index.isValid():
                doc_id = index.data(Qt.UserRole)
                self.file_deleted.emit(doc_id)
