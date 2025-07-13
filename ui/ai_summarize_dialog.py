import json
import requests
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QPushButton, 
                           QTextEdit, QLabel, QComboBox, QLineEdit, QProgressBar,
                           QMessageBox, QGroupBox, QSpinBox, QWidget)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QFont

class OllamaWorker(QThread):
    """Worker thread for Ollama API calls to avoid blocking the UI"""
    finished = pyqtSignal(str)
    error = pyqtSignal(str)
    progress = pyqtSignal(str)
    
    def __init__(self, content, model, ollama_url, summary_type, max_length):
        super().__init__()
        self.content = content
        self.model = model
        self.ollama_url = ollama_url
        self.summary_type = summary_type
        self.max_length = max_length
        
    def run(self):
        try:
            # Create appropriate prompt based on summary type
            prompts = {
                "brief": f"Please provide a brief summary of the following text in {self.max_length} words or less:\n\n{self.content}",
                "detailed": f"Please provide a detailed summary of the following text, capturing key points and important details in approximately {self.max_length} words:\n\n{self.content}",
                "bullet_points": f"Please summarize the following text as bullet points, highlighting the main ideas in {self.max_length} words or less:\n\n{self.content}",
                "key_insights": f"Please extract the key insights and takeaways from the following text in {self.max_length} words or less:\n\n{self.content}"
            }
            
            prompt = prompts.get(self.summary_type, prompts["brief"])
            
            self.progress.emit("Connecting to Ollama...")
            
            # Make request to Ollama API
            response = requests.post(
                f"{self.ollama_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False
                },
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                summary = result.get('response', 'No summary generated.')
                self.finished.emit(summary)
            else:
                self.error.emit(f"HTTP Error {response.status_code}: {response.text}")
                
        except requests.exceptions.ConnectionError:
            self.error.emit("Could not connect to Ollama. Please make sure Ollama is running and accessible.")
        except requests.exceptions.Timeout:
            self.error.emit("Request timed out. The model might be taking too long to respond.")
        except Exception as e:
            self.error.emit(f"An error occurred: {str(e)}")

class AISummarizeDialog(QDialog):
    def __init__(self, content, parent=None):
        super().__init__(parent)
        self.content = content
        self.worker = None
        self.summary_result = ""
        
        # Use the same pattern as other dialogs
        self.setObjectName("aiSummarizeDialog")
        self.setWindowTitle("AI Summarization")
        self.setFixedSize(700, 600)
        self.setWindowFlags(Qt.Dialog | Qt.WindowTitleHint)
        
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Title
        title = QLabel("AI Summarization")
        title.setStyleSheet("font-size: 24px; margin-bottom: 20px;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # Configuration section
        config_layout = QVBoxLayout()
        
        # Ollama URL
        url_layout = QHBoxLayout()
        url_label = QLabel("Ollama URL:")
        url_label.setStyleSheet("font-size: 16px;")
        url_label.setFixedWidth(120)
        url_layout.addWidget(url_label)
        
        self.url_input = QLineEdit("http://localhost:11434")
        self.url_input.setPlaceholderText("Enter Ollama server URL...")
        self.url_input.setStyleSheet("font-size: 14px;")
        self.url_input.setFixedHeight(35)
        url_layout.addWidget(self.url_input)
        
        config_layout.addLayout(url_layout)
        
        # Model selection
        model_layout = QHBoxLayout()
        model_label = QLabel("Model:")
        model_label.setStyleSheet("font-size: 16px;")
        model_label.setFixedWidth(120)
        model_layout.addWidget(model_label)
        
        self.model_combo = QComboBox()
        self.model_combo.setEditable(True)
        self.model_combo.setStyleSheet("font-size: 14px;")
        self.model_combo.setFixedHeight(35)
        # Default models
        self.model_combo.addItems([
            "llama3.2:latest",
            "llama3.2:3b",
            "llama3.1:latest", 
            "llama3.1:8b",
            "mistral:latest",
            "codellama:latest",
            "gemma2:latest"
        ])
        model_layout.addWidget(self.model_combo)
        
        # Refresh button
        refresh_btn = QPushButton("Refresh Models")
        refresh_btn.setStyleSheet("font-size: 14px;")
        refresh_btn.setFixedHeight(35)
        refresh_btn.clicked.connect(self.refresh_models)
        model_layout.addWidget(refresh_btn)
        
        config_layout.addLayout(model_layout)
        
        # Summary type and length
        options_layout = QHBoxLayout()
        
        # Summary type
        type_label = QLabel("Summary Type:")
        type_label.setStyleSheet("font-size: 16px;")
        type_label.setFixedWidth(120)
        options_layout.addWidget(type_label)
        
        self.type_combo = QComboBox()
        self.type_combo.setStyleSheet("font-size: 14px;")
        self.type_combo.setFixedHeight(35)
        self.type_combo.addItems([
            "Brief Summary",
            "Detailed Summary", 
            "Bullet Points",
            "Key Insights"
        ])
        options_layout.addWidget(self.type_combo)
        
        # Max length
        length_label = QLabel("Max Length:")
        length_label.setStyleSheet("font-size: 16px;")
        length_label.setFixedWidth(100)
        options_layout.addWidget(length_label)
        
        self.length_spin = QSpinBox()
        self.length_spin.setStyleSheet("font-size: 14px;")
        self.length_spin.setFixedHeight(35)
        self.length_spin.setMinimum(50)
        self.length_spin.setMaximum(1000)
        self.length_spin.setValue(200)
        self.length_spin.setSuffix(" words")
        options_layout.addWidget(self.length_spin)
        
        config_layout.addLayout(options_layout)
        layout.addLayout(config_layout)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setFixedHeight(25)
        layout.addWidget(self.progress_bar)
        
        # Progress label
        self.progress_label = QLabel("")
        self.progress_label.setStyleSheet("font-size: 14px;")
        self.progress_label.setAlignment(Qt.AlignCenter)
        self.progress_label.setVisible(False)
        layout.addWidget(self.progress_label)
        
        # Result area
        result_label = QLabel("Generated Summary:")
        result_label.setStyleSheet("font-size: 16px; margin-top: 10px;")
        layout.addWidget(result_label)
        
        self.result_text = QTextEdit()
        self.result_text.setReadOnly(True)
        self.result_text.setPlaceholderText("Generated summary will appear here...")
        self.result_text.setStyleSheet("font-size: 14px;")
        self.result_text.setMinimumHeight(200)
        layout.addWidget(self.result_text)
        
        # Add stretch to push buttons to bottom
        layout.addStretch()
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.generate_btn = QPushButton("Generate Summary")
        self.generate_btn.setStyleSheet("font-size: 14px;")
        self.generate_btn.setFixedHeight(35)
        self.generate_btn.clicked.connect(self.generate_summary)
        button_layout.addWidget(self.generate_btn)
        
        self.insert_btn = QPushButton("Insert into Document")
        self.insert_btn.setStyleSheet("font-size: 14px;")
        self.insert_btn.setFixedHeight(35)
        self.insert_btn.clicked.connect(self.accept)
        self.insert_btn.setEnabled(False)
        button_layout.addWidget(self.insert_btn)
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setStyleSheet("font-size: 14px;")
        cancel_btn.setFixedHeight(35)
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        # Set margins for button layout
        button_layout.setContentsMargins(0, 20, 0, 0)
        layout.addLayout(button_layout)
        
    def refresh_models(self):
        """Refresh available models from Ollama"""
        try:
            url = self.url_input.text().strip()
            if not url:
                return
                
            response = requests.get(f"{url}/api/tags", timeout=10)
            if response.status_code == 200:
                data = response.json()
                models = [model['name'] for model in data.get('models', [])]
                
                current_text = self.model_combo.currentText()
                self.model_combo.clear()
                self.model_combo.addItems(models)
                
                # Try to restore previous selection
                index = self.model_combo.findText(current_text)
                if index >= 0:
                    self.model_combo.setCurrentIndex(index)
                elif models:
                    self.model_combo.setCurrentIndex(0)
                    
                QMessageBox.information(self, "Success", f"Found {len(models)} models")
            else:
                QMessageBox.warning(self, "Error", f"Failed to fetch models: {response.status_code}")
                
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Could not connect to Ollama: {str(e)}")
    
    def generate_summary(self):
        """Generate AI summary"""
        if not self.content.strip():
            QMessageBox.warning(self, "Warning", "No content to summarize.")
            return
            
        url = self.url_input.text().strip()
        model = self.model_combo.currentText().strip()
        
        if not url or not model:
            QMessageBox.warning(self, "Warning", "Please enter Ollama URL and model.")
            return
        
        # Map UI selection to internal types
        type_mapping = {
            "Brief Summary": "brief",
            "Detailed Summary": "detailed",
            "Bullet Points": "bullet_points", 
            "Key Insights": "key_insights"
        }
        summary_type = type_mapping[self.type_combo.currentText()]
        max_length = self.length_spin.value()
        
        # Disable generate button and show progress
        self.generate_btn.setEnabled(False)
        self.generate_btn.setText("Generating...")
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)  # Indeterminate progress
        self.progress_label.setVisible(True)
        self.progress_label.setText("Generating summary...")
        
        # Start worker thread
        self.worker = OllamaWorker(self.content, model, url, summary_type, max_length)
        self.worker.finished.connect(self.on_summary_finished)
        self.worker.error.connect(self.on_summary_error)
        self.worker.progress.connect(self.on_progress_update)
        self.worker.start()
        
    def on_progress_update(self, message):
        """Update progress label"""
        self.progress_label.setText(message)
        
    def on_summary_finished(self, summary):
        """Handle successful summary generation"""
        self.summary_result = summary
        self.result_text.setPlainText(summary)
        
        # Re-enable controls
        self.generate_btn.setEnabled(True)
        self.generate_btn.setText("Generate Summary")
        self.insert_btn.setEnabled(True)
        self.progress_bar.setVisible(False)
        self.progress_label.setVisible(False)
        
        # Clean up worker
        if self.worker:
            self.worker.deleteLater()
            self.worker = None
    
    def on_summary_error(self, error_message):
        """Handle summary generation error"""
        QMessageBox.critical(self, "Error", 
                           f"Failed to generate summary:\n\n{error_message}")
        
        # Re-enable controls
        self.generate_btn.setEnabled(True)
        self.generate_btn.setText("Generate Summary")
        self.progress_bar.setVisible(False)
        self.progress_label.setVisible(False)
        
        # Clean up worker
        if self.worker:
            self.worker.deleteLater()
            self.worker = None
    
    def get_summary(self):
        """Get the generated summary"""
        return self.summary_result
        
    def closeEvent(self, event):
        """Handle dialog close"""
        if self.worker and self.worker.isRunning():
            self.worker.quit()
            self.worker.wait()
        event.accept()
