#!/usr/bin/env python3
"""
GestureMate - A gesture drawing app for timed figure drawing practice.
"""

import sys
import os
import random
from pathlib import Path
from typing import List

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QFileDialog, QSpinBox, QListWidget,
    QDialog, QDialogButtonBox, QGroupBox, QFormLayout, QMessageBox,
    QProgressBar
)
from PyQt6.QtCore import QTimer, Qt, QSize
from PyQt6.QtGui import QPixmap, QPalette, QColor, QAction


class SettingsDialog(QDialog):
    """Dialog for configuring session settings."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Session Settings")
        self.setModal(True)
        self.folders = []
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the settings dialog UI."""
        layout = QVBoxLayout()
        
        # Folder selection group
        folder_group = QGroupBox("Image Folders")
        folder_layout = QVBoxLayout()
        
        self.folder_list = QListWidget()
        folder_layout.addWidget(self.folder_list)
        
        folder_btn_layout = QHBoxLayout()
        add_folder_btn = QPushButton("Add Folder")
        add_folder_btn.clicked.connect(self.add_folder)
        remove_folder_btn = QPushButton("Remove Selected")
        remove_folder_btn.clicked.connect(self.remove_folder)
        
        folder_btn_layout.addWidget(add_folder_btn)
        folder_btn_layout.addWidget(remove_folder_btn)
        folder_layout.addLayout(folder_btn_layout)
        
        folder_group.setLayout(folder_layout)
        layout.addWidget(folder_group)
        
        # Timer settings group
        timer_group = QGroupBox("Timer Settings")
        timer_layout = QFormLayout()
        
        self.image_duration = QSpinBox()
        self.image_duration.setRange(10, 3600)
        self.image_duration.setValue(60)
        self.image_duration.setSuffix(" seconds")
        timer_layout.addRow("Duration per image:", self.image_duration)
        
        self.session_duration = QSpinBox()
        self.session_duration.setRange(1, 480)
        self.session_duration.setValue(30)
        self.session_duration.setSuffix(" minutes")
        timer_layout.addRow("Total session duration:", self.session_duration)
        
        timer_group.setLayout(timer_layout)
        layout.addWidget(timer_group)
        
        # Dialog buttons
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | 
            QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
        
        self.setLayout(layout)
        
    def add_folder(self):
        """Add a folder to the list."""
        folder = QFileDialog.getExistingDirectory(
            self, "Select Image Folder"
        )
        if folder:
            self.folders.append(folder)
            self.folder_list.addItem(folder)
            
    def remove_folder(self):
        """Remove selected folder from the list."""
        current_row = self.folder_list.currentRow()
        if current_row >= 0:
            self.folder_list.takeItem(current_row)
            self.folders.pop(current_row)
            
    def get_settings(self):
        """Return the current settings."""
        return {
            'folders': self.folders,
            'image_duration': self.image_duration.value(),
            'session_duration': self.session_duration.value() * 60  # Convert to seconds
        }


class GestureMate(QMainWindow):
    """Main application window."""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("GestureMate - Gesture Drawing Practice")
        self.images = []
        self.current_image_index = 0
        self.is_session_active = False
        self.session_time_remaining = 0
        self.image_time_remaining = 0
        
        # Supported image formats
        self.image_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.gif', '.webp'}
        
        self.setup_ui()
        self.setup_timers()
        
    def setup_ui(self):
        """Setup the main window UI."""
        # Set window to maximized by default
        self.showMaximized()
        
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Image display area
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_label.setStyleSheet("background-color: #2b2b2b;")
        self.image_label.setMinimumSize(800, 600)
        self.image_label.setScaledContents(False)
        main_layout.addWidget(self.image_label, stretch=1)
        
        # Control panel
        control_panel = self.create_control_panel()
        main_layout.addWidget(control_panel)
        
        central_widget.setLayout(main_layout)
        
        # Menu bar
        self.create_menu_bar()
        
        # Set dark theme
        self.set_dark_theme()
        
    def create_menu_bar(self):
        """Create the menu bar."""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu("&File")
        
        settings_action = QAction("&Settings", self)
        settings_action.setShortcut("Ctrl+S")
        settings_action.triggered.connect(self.show_settings)
        file_menu.addAction(settings_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("E&xit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Help menu
        help_menu = menubar.addMenu("&Help")
        
        about_action = QAction("&About", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
        
    def create_control_panel(self):
        """Create the control panel widget."""
        panel = QWidget()
        panel.setMaximumHeight(120)
        layout = QVBoxLayout()
        
        # Timer displays
        timer_layout = QHBoxLayout()
        
        self.image_timer_label = QLabel("Image: --:--")
        self.image_timer_label.setStyleSheet(
            "font-size: 18px; font-weight: bold; padding: 5px;"
        )
        timer_layout.addWidget(self.image_timer_label)
        
        timer_layout.addStretch()
        
        self.session_timer_label = QLabel("Session: --:--")
        self.session_timer_label.setStyleSheet(
            "font-size: 18px; font-weight: bold; padding: 5px;"
        )
        timer_layout.addWidget(self.session_timer_label)
        
        layout.addLayout(timer_layout)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setMaximum(100)
        self.progress_bar.setValue(0)
        layout.addWidget(self.progress_bar)
        
        # Control buttons
        button_layout = QHBoxLayout()
        
        self.start_btn = QPushButton("Start Session")
        self.start_btn.clicked.connect(self.start_session)
        self.start_btn.setMinimumHeight(40)
        button_layout.addWidget(self.start_btn)
        
        self.pause_btn = QPushButton("Pause")
        self.pause_btn.clicked.connect(self.pause_session)
        self.pause_btn.setEnabled(False)
        self.pause_btn.setMinimumHeight(40)
        button_layout.addWidget(self.pause_btn)
        
        self.next_btn = QPushButton("Next Image")
        self.next_btn.clicked.connect(self.next_image)
        self.next_btn.setEnabled(False)
        self.next_btn.setMinimumHeight(40)
        button_layout.addWidget(self.next_btn)
        
        self.stop_btn = QPushButton("Stop")
        self.stop_btn.clicked.connect(self.stop_session)
        self.stop_btn.setEnabled(False)
        self.stop_btn.setMinimumHeight(40)
        button_layout.addWidget(self.stop_btn)
        
        layout.addLayout(button_layout)
        
        panel.setLayout(layout)
        return panel
        
    def setup_timers(self):
        """Setup the timers for session and image display."""
        self.session_timer = QTimer()
        self.session_timer.timeout.connect(self.update_session_timer)
        
        self.image_timer = QTimer()
        self.image_timer.timeout.connect(self.update_image_timer)
        
    def set_dark_theme(self):
        """Apply a dark theme to the application."""
        palette = QPalette()
        palette.setColor(QPalette.ColorRole.Window, QColor(53, 53, 53))
        palette.setColor(QPalette.ColorRole.WindowText, Qt.GlobalColor.white)
        palette.setColor(QPalette.ColorRole.Base, QColor(35, 35, 35))
        palette.setColor(QPalette.ColorRole.AlternateBase, QColor(53, 53, 53))
        palette.setColor(QPalette.ColorRole.ToolTipBase, Qt.GlobalColor.white)
        palette.setColor(QPalette.ColorRole.ToolTipText, Qt.GlobalColor.white)
        palette.setColor(QPalette.ColorRole.Text, Qt.GlobalColor.white)
        palette.setColor(QPalette.ColorRole.Button, QColor(53, 53, 53))
        palette.setColor(QPalette.ColorRole.ButtonText, Qt.GlobalColor.white)
        palette.setColor(QPalette.ColorRole.BrightText, Qt.GlobalColor.red)
        palette.setColor(QPalette.ColorRole.Link, QColor(42, 130, 218))
        palette.setColor(QPalette.ColorRole.Highlight, QColor(42, 130, 218))
        palette.setColor(QPalette.ColorRole.HighlightedText, Qt.GlobalColor.black)
        self.setPalette(palette)
        
    def show_settings(self):
        """Show the settings dialog."""
        dialog = SettingsDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            settings = dialog.get_settings()
            if not settings['folders']:
                QMessageBox.warning(
                    self, "No Folders Selected",
                    "Please select at least one folder containing images."
                )
                return
            
            self.load_images(settings['folders'])
            self.image_duration = settings['image_duration']
            self.session_duration = settings['session_duration']
            
            if self.images:
                QMessageBox.information(
                    self, "Settings Applied",
                    f"Loaded {len(self.images)} images.\n"
                    f"Image duration: {self.image_duration}s\n"
                    f"Session duration: {self.session_duration // 60}m"
                )
            else:
                QMessageBox.warning(
                    self, "No Images Found",
                    "No supported images found in the selected folders.\n"
                    "Supported formats: JPG, PNG, BMP, GIF, WEBP"
                )
                
    def load_images(self, folders: List[str]):
        """Load images from the specified folders."""
        self.images = []
        for folder in folders:
            folder_path = Path(folder)
            if folder_path.exists():
                for file_path in folder_path.rglob('*'):
                    if file_path.is_file() and file_path.suffix.lower() in self.image_extensions:
                        self.images.append(str(file_path))
        
        # Shuffle images for variety
        random.shuffle(self.images)
        self.current_image_index = 0
        
    def start_session(self):
        """Start a drawing session."""
        if not self.images:
            QMessageBox.warning(
                self, "No Images",
                "Please configure settings and select image folders first."
            )
            self.show_settings()
            return
        
        self.is_session_active = True
        self.session_time_remaining = self.session_duration
        self.image_time_remaining = self.image_duration
        self.current_image_index = 0
        
        # Update UI
        self.start_btn.setEnabled(False)
        self.pause_btn.setEnabled(True)
        self.pause_btn.setText("Pause")
        self.next_btn.setEnabled(True)
        self.stop_btn.setEnabled(True)
        
        # Start timers
        self.session_timer.start(1000)  # 1 second interval
        self.image_timer.start(1000)
        
        # Display first image
        self.display_current_image()
        
    def pause_session(self):
        """Pause or resume the session."""
        if self.session_timer.isActive():
            self.session_timer.stop()
            self.image_timer.stop()
            self.pause_btn.setText("Resume")
        else:
            self.session_timer.start(1000)
            self.image_timer.start(1000)
            self.pause_btn.setText("Pause")
            
    def stop_session(self):
        """Stop the current session."""
        self.session_timer.stop()
        self.image_timer.stop()
        self.is_session_active = False
        
        # Reset UI
        self.start_btn.setEnabled(True)
        self.pause_btn.setEnabled(False)
        self.next_btn.setEnabled(False)
        self.stop_btn.setEnabled(False)
        
        self.image_timer_label.setText("Image: --:--")
        self.session_timer_label.setText("Session: --:--")
        self.progress_bar.setValue(0)
        self.image_label.clear()
        self.image_label.setText("Session ended. Click 'Start Session' to begin.")
        
    def next_image(self):
        """Skip to the next image."""
        if not self.is_session_active:
            return
        
        self.current_image_index = (self.current_image_index + 1) % len(self.images)
        self.image_time_remaining = self.image_duration
        self.display_current_image()
        
    def update_session_timer(self):
        """Update the session timer."""
        self.session_time_remaining -= 1
        
        minutes = self.session_time_remaining // 60
        seconds = self.session_time_remaining % 60
        self.session_timer_label.setText(f"Session: {minutes:02d}:{seconds:02d}")
        
        # Update progress bar
        elapsed = self.session_duration - self.session_time_remaining
        progress = int((elapsed / self.session_duration) * 100)
        self.progress_bar.setValue(progress)
        
        if self.session_time_remaining <= 0:
            self.stop_session()
            QMessageBox.information(
                self, "Session Complete",
                "Your drawing session has ended!"
            )
            
    def update_image_timer(self):
        """Update the image timer."""
        self.image_time_remaining -= 1
        
        minutes = self.image_time_remaining // 60
        seconds = self.image_time_remaining % 60
        self.image_timer_label.setText(f"Image: {minutes:02d}:{seconds:02d}")
        
        if self.image_time_remaining <= 0:
            self.next_image()
            
    def display_current_image(self):
        """Display the current image, scaled to fit the screen."""
        if not self.images:
            return
        
        image_path = self.images[self.current_image_index]
        pixmap = QPixmap(image_path)
        
        if pixmap.isNull():
            # If image can't be loaded, skip to next
            self.next_image()
            return
        
        # Scale image to fit the label while maintaining aspect ratio
        label_size = self.image_label.size()
        scaled_pixmap = pixmap.scaled(
            label_size,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )
        
        self.image_label.setPixmap(scaled_pixmap)
        
    def resizeEvent(self, event):
        """Handle window resize events."""
        super().resizeEvent(event)
        if self.is_session_active and self.images:
            self.display_current_image()
            
    def show_about(self):
        """Show the about dialog."""
        QMessageBox.about(
            self, "About GestureMate",
            "<h2>GestureMate</h2>"
            "<p>A gesture drawing practice application for artists.</p>"
            "<p>Select image folders, set your timers, and practice!</p>"
            "<p><b>Keyboard Shortcuts:</b></p>"
            "<ul>"
            "<li>Ctrl+S: Settings</li>"
            "<li>Ctrl+Q: Quit</li>"
            "</ul>"
        )


def main():
    """Main entry point for the application."""
    app = QApplication(sys.argv)
    app.setApplicationName("GestureMate")
    
    window = GestureMate()
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
