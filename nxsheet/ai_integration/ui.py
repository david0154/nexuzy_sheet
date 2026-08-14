# -*- coding: utf-8 -*-

# Copyright (c) 2026 Nexuzy Lab

"""
AI Integration UI Components

Provides UI widgets for Nexuzy Sheet AI features:
- AI prompt panel
- AI toolbar button
- Document import dialogs
"""

import logging
from typing import Optional, Callable

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, 
                             QPushButton, QTextEdit, QLabel, QDialog,
                             QProgressBar, QComboBox, QFileDialog)
from PyQt6.QtCore import Qt, pyqtSignal, QThread
from PyQt6.QtGui import QIcon

logger = logging.getLogger(__name__)


class AIWorkerThread(QThread):
    """Worker thread for AI operations (prevents UI blocking)"""
    
    finished = pyqtSignal(object)
    error = pyqtSignal(str)
    progress = pyqtSignal(str)
    
    def __init__(self, coordinator, operation_name: str, *args, **kwargs):
        super().__init__()
        self.coordinator = coordinator
        self.operation_name = operation_name
        self.args = args
        self.kwargs = kwargs
    
    def run(self):
        """Run AI operation in background"""
        try:
            self.progress.emit(f"Running {self.operation_name}...")
            
            if self.operation_name == "initialize":
                def progress_cb(msg):
                    self.progress.emit(msg)
                result = self.coordinator.initialize_async(progress_cb)
                self.finished.emit(result)
            
            elif self.operation_name == "command":
                command = self.args[0]
                context = self.kwargs.get("context")
                result = self.coordinator.process_command(command, context)
                self.finished.emit(result)
            
            elif self.operation_name == "import_image":
                image_path = self.args[0]
                output_cell = self.kwargs.get("output_cell", "A1")
                result = self.coordinator.import_from_image(image_path, output_cell)
                self.finished.emit(result)
            
            elif self.operation_name == "import_pdf":
                pdf_path = self.args[0]
                output_cell = self.kwargs.get("output_cell", "A1")
                page = self.kwargs.get("page", 0)
                result = self.coordinator.import_from_pdf(pdf_path, output_cell, page)
                self.finished.emit(result)
            
            else:
                self.error.emit(f"Unknown operation: {self.operation_name}")
        
        except Exception as e:
            logger.error(f"Worker thread error: {e}")
            self.error.emit(str(e))


class AIPanelWidget(QWidget):
    """
    AI Prompt Panel Widget
    
    Provides text input for user commands and displays AI responses.
    """
    
    command_submitted = pyqtSignal(str)  # Emitted when user submits command
    action_received = pyqtSignal(object)  # Emitted when AI returns action
    
    def __init__(self, parent=None, coordinator=None):
        super().__init__(parent)
        self.coordinator = coordinator
        self.worker_thread = None
        self._setup_ui()
    
    def _setup_ui(self):
        """Setup UI components"""
        layout = QVBoxLayout()
        
        # Title
        title = QLabel("✨ Ask Nexuzy AI")
        title.setStyleSheet("font-weight: bold; font-size: 12px;")
        layout.addWidget(title)
        
        # Command input
        self.command_input = QLineEdit()
        self.command_input.setPlaceholderText("Ask anything about this spreadsheet...")
        self.command_input.returnPressed.connect(self._on_submit)
        layout.addWidget(self.command_input)
        
        # Submit button
        self.submit_button = QPushButton("Ask AI")
        self.submit_button.clicked.connect(self._on_submit)
        layout.addWidget(self.submit_button)
        
        # Response display
        self.response_text = QTextEdit()
        self.response_text.setReadOnly(True)
        self.response_text.setMaximumHeight(150)
        self.response_text.setPlaceholderText("AI response will appear here...")
        layout.addWidget(self.response_text)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setMaximum(0)  # Indeterminate
        layout.addWidget(self.progress_bar)
        
        # Buttons for import
        import_layout = QHBoxLayout()
        
        self.import_image_btn = QPushButton("📷 Import from Image")
        self.import_image_btn.clicked.connect(self._on_import_image)
        import_layout.addWidget(self.import_image_btn)
        
        self.import_pdf_btn = QPushButton("📄 Import from PDF")
        self.import_pdf_btn.clicked.connect(self._on_import_pdf)
        import_layout.addWidget(self.import_pdf_btn)
        
        layout.addLayout(import_layout)
        
        layout.addStretch()
        self.setLayout(layout)
    
    def _on_submit(self):
        """Handle command submission"""
        command = self.command_input.text().strip()
        if not command:
            return
        
        if not self.coordinator or not self.coordinator.is_ready():
            self.response_text.setText("❌ AI not initialized. Please wait or check dependencies.")
            return
        
        self.command_input.clear()
        self.submit_button.setEnabled(False)
        self.progress_bar.setVisible(True)
        
        self.command_submitted.emit(command)
        
        # Run in worker thread
        self.worker_thread = AIWorkerThread(
            self.coordinator, "command", command,
            context={}  # TODO: Pass actual spreadsheet context
        )
        self.worker_thread.finished.connect(self._on_action_received)
        self.worker_thread.progress.connect(self._on_progress)
        self.worker_thread.error.connect(self._on_error)
        self.worker_thread.start()
    
    def _on_action_received(self, action):
        """Handle AI action response"""
        self.progress_bar.setVisible(False)
        self.submit_button.setEnabled(True)
        
        # Display response
        if action:
            response = f"Action: {action.action.value}\n"
            if action.explanation:
                response += f"\n{action.explanation}\n"
            response += f"\nConfidence: {action.confidence:.1%}"
            self.response_text.setText(response)
        
        self.action_received.emit(action)
    
    def _on_progress(self, msg: str):
        """Update progress message"""
        self.response_text.setText(msg)
    
    def _on_error(self, error_msg: str):
        """Handle error"""
        self.progress_bar.setVisible(False)
        self.submit_button.setEnabled(True)
        self.response_text.setText(f"❌ Error: {error_msg}")
    
    def _on_import_image(self):
        """Import from image file"""
        if not self.coordinator or not self.coordinator.is_ready():
            self.response_text.setText("❌ AI not initialized.")
            return
        
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select Image",
            filter="Images (*.jpg *.jpeg *.png *.bmp *.gif *.tiff)"
        )
        
        if not file_path:
            return
        
        self.submit_button.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.response_text.setText("Importing from image...")
        
        self.worker_thread = AIWorkerThread(
            self.coordinator, "import_image", file_path,
            output_cell="A1"
        )
        self.worker_thread.finished.connect(self._on_action_received)
        self.worker_thread.progress.connect(self._on_progress)
        self.worker_thread.error.connect(self._on_error)
        self.worker_thread.start()
    
    def _on_import_pdf(self):
        """Import from PDF file"""
        if not self.coordinator or not self.coordinator.is_ready():
            self.response_text.setText("❌ AI not initialized.")
            return
        
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select PDF", filter="PDF Files (*.pdf)"
        )
        
        if not file_path:
            return
        
        self.submit_button.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.response_text.setText("Importing from PDF...")
        
        self.worker_thread = AIWorkerThread(
            self.coordinator, "import_pdf", file_path,
            output_cell="A1", page=0
        )
        self.worker_thread.finished.connect(self._on_action_received)
        self.worker_thread.progress.connect(self._on_progress)
        self.worker_thread.error.connect(self._on_error)
        self.worker_thread.start()


class AIInitializationDialog(QDialog):
    """Dialog for AI initialization and model downloads"""
    
    def __init__(self, parent=None, coordinator=None):
        super().__init__(parent)
        self.coordinator = coordinator
        self.worker_thread = None
        self.setWindowTitle("Initialize Nexuzy Sheet AI")
        self.setModal(True)
        self.setMinimumWidth(500)
        self._setup_ui()
    
    def _setup_ui(self):
        """Setup UI"""
        layout = QVBoxLayout()
        
        # Title
        title = QLabel("Setting up AI Integration")
        title.setStyleSheet("font-weight: bold; font-size: 14px;")
        layout.addWidget(title)
        
        # Status text
        self.status_text = QTextEdit()
        self.status_text.setReadOnly(True)
        self.status_text.setMaximumHeight(200)
        layout.addWidget(self.status_text)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setMaximum(0)  # Indeterminate
        layout.addWidget(self.progress_bar)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.start_button = QPushButton("Start Initialization")
        self.start_button.clicked.connect(self._on_start)
        button_layout.addWidget(self.start_button)
        
        self.close_button = QPushButton("Close")
        self.close_button.clicked.connect(self.accept)
        button_layout.addWidget(self.close_button)
        
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
        self.append_status("Ready to initialize AI components.")
    
    def append_status(self, msg: str):
        """Append message to status display"""
        current = self.status_text.toPlainText()
        self.status_text.setText(current + "\n" + msg if current else msg)
        # Scroll to bottom
        self.status_text.verticalScrollBar().setValue(
            self.status_text.verticalScrollBar().maximum()
        )
    
    def _on_start(self):
        """Start initialization"""
        if not self.coordinator:
            self.append_status("❌ No coordinator available")
            return
        
        self.start_button.setEnabled(False)
        self.progress_bar.setVisible(True)
        
        self.worker_thread = AIWorkerThread(self.coordinator, "initialize")
        self.worker_thread.progress.connect(self.append_status)
        self.worker_thread.finished.connect(self._on_finished)
        self.worker_thread.error.connect(self._on_error)
        self.worker_thread.start()
    
    def _on_finished(self, success):
        """Initialization finished"""
        self.progress_bar.setVisible(False)
        if success:
            self.append_status("✅ AI initialization complete!")
        else:
            self.append_status("❌ AI initialization failed. Check logs.")
        self.start_button.setEnabled(True)
    
    def _on_error(self, error_msg):
        """Handle error"""
        self.progress_bar.setVisible(False)
        self.append_status(f"❌ Error: {error_msg}")
        self.start_button.setEnabled(True)
