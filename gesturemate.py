#!/usr/bin/env python3
"""
GestureMate - A gesture drawing app for timed figure drawing practice.
"""

import sys
import os
import random
import json
import subprocess
from datetime import date, timedelta
from pathlib import Path
from typing import List

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QFileDialog, QSpinBox, QListWidget,
    QDialog, QDialogButtonBox, QGroupBox, QFormLayout, QMessageBox,
    QProgressBar, QCheckBox, QListWidgetItem, QTreeWidget, QTreeWidgetItem,
    QComboBox, QInputDialog, QToolTip
)
from PyQt6.QtCore import QTimer, Qt, QSize, QStandardPaths, QUrl, QRect
from PyQt6.QtGui import (
    QPixmap, QPalette, QColor, QAction, QImage, QTransform, QIcon,
    QPainter, QFont, QFontMetrics
)


# Supported image formats (module-level constant)
SUPPORTED_IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.bmp', '.gif', '.webp'}

# Maximum number of files to check when scanning folders (prevents UI freezing)
MAX_FILES_TO_CHECK = 5000


class SettingsDialog(QDialog):
    """Dialog for configuring session settings."""
    
    def __init__(self, parent=None, saved_folders=None, image_duration=60, session_duration=30, halfway_sound=True, presets=None):
        super().__init__(parent)
        self.setWindowTitle("Session Settings")
        self.setModal(True)
        self.folders = []
        self.saved_folders = saved_folders or {}
        self.default_image_duration = image_duration
        self.default_session_duration = session_duration
        self.default_halfway_sound = halfway_sound
        self.presets = presets if presets is not None else {}
        self.presets_modified = False
        self.setup_ui()
        self.load_saved_folders()
        
    def setup_ui(self):
        """Setup the settings dialog UI."""
        layout = QVBoxLayout()

        # Presets group
        preset_group = QGroupBox("Presets")
        preset_layout = QHBoxLayout()

        self.preset_combo = QComboBox()
        self.preset_combo.setMinimumWidth(200)
        preset_layout.addWidget(self.preset_combo, stretch=1)

        load_preset_btn = QPushButton("Load")
        load_preset_btn.clicked.connect(self.load_preset)
        load_preset_btn.setToolTip("Apply the selected preset to the settings below")
        preset_layout.addWidget(load_preset_btn)

        save_preset_btn = QPushButton("Save Preset...")
        save_preset_btn.clicked.connect(self.save_preset)
        save_preset_btn.setToolTip("Save the current settings below as a named preset")
        preset_layout.addWidget(save_preset_btn)

        delete_preset_btn = QPushButton("Delete")
        delete_preset_btn.clicked.connect(self.delete_preset)
        delete_preset_btn.setToolTip("Delete the selected preset")
        preset_layout.addWidget(delete_preset_btn)

        preset_group.setLayout(preset_layout)
        layout.addWidget(preset_group)
        self.refresh_preset_combo()

        # Folder selection group
        folder_group = QGroupBox("Image Folders")
        folder_layout = QVBoxLayout()
        
        self.folder_tree = QTreeWidget()
        self.folder_tree.setHeaderLabels(["Folder", "Images"])
        self.folder_tree.setColumnWidth(0, 400)
        self.folder_tree.itemChanged.connect(self.on_item_changed)
        folder_layout.addWidget(self.folder_tree)
        
        folder_btn_layout = QHBoxLayout()
        add_folder_btn = QPushButton("Add Folder")
        add_folder_btn.clicked.connect(self.add_folder)
        remove_folder_btn = QPushButton("Remove Selected")
        remove_folder_btn.clicked.connect(self.remove_folder)
        refresh_btn = QPushButton("🔄 Refresh")
        refresh_btn.clicked.connect(self.refresh_folders)
        refresh_btn.setToolTip("Refresh folders to detect newly added subfolders")
        # Add a subtle highlight style to the refresh button
        refresh_btn.setStyleSheet("""
            QPushButton {
                background-color: #3a5f7d;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #4a7fa0;
            }
            QPushButton:pressed {
                background-color: #2a4f6d;
            }
        """)
        
        folder_btn_layout.addWidget(add_folder_btn)
        folder_btn_layout.addWidget(remove_folder_btn)
        folder_btn_layout.addWidget(refresh_btn)
        folder_layout.addLayout(folder_btn_layout)
        
        folder_group.setLayout(folder_layout)
        layout.addWidget(folder_group)
        
        # Timer settings group
        timer_group = QGroupBox("Timer Settings")
        timer_layout = QFormLayout()
        
        self.image_duration = QSpinBox()
        self.image_duration.setRange(10, 3600)
        self.image_duration.setValue(self.default_image_duration)
        self.image_duration.setSuffix(" seconds")
        timer_layout.addRow("Duration per image:", self.image_duration)
        
        self.session_duration = QSpinBox()
        self.session_duration.setRange(1, 480)
        self.session_duration.setValue(self.default_session_duration)
        self.session_duration.setSuffix(" minutes")
        timer_layout.addRow("Total session duration:", self.session_duration)
        
        timer_group.setLayout(timer_layout)
        layout.addWidget(timer_group)
        
        # Session options group
        options_group = QGroupBox("Session Options")
        options_layout = QVBoxLayout()
        
        self.shuffle_checkbox = QCheckBox("Shuffle images")
        self.shuffle_checkbox.setChecked(True)
        options_layout.addWidget(self.shuffle_checkbox)
        
        self.halfway_sound_checkbox = QCheckBox("Play sound halfway through each image")
        self.halfway_sound_checkbox.setChecked(self.default_halfway_sound)
        options_layout.addWidget(self.halfway_sound_checkbox)
        
        options_group.setLayout(options_layout)
        layout.addWidget(options_group)
        
        # Dialog buttons
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | 
            QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
        
        self.setLayout(layout)
        
    def on_item_changed(self, item, column):
        """Handle item checkbox state changes.
        
        When a top-level folder's checkbox is changed, propagate the state to all children.
        Only top-level items trigger propagation to allow individual subfolder control.
        """
        # Only handle checkbox changes in column 0
        if column != 0:
            return
        
        # Only propagate from top-level items (parent is None)
        # This allows users to manually adjust individual subfolders after bulk operations
        # and prevents infinite recursion when we programmatically update child items
        if item.parent() is None:
            # This is a top-level folder, propagate state to all children
            new_state = item.checkState(0)
            
            # Block signals to avoid recursive calls
            self.folder_tree.blockSignals(True)
            
            try:
                # Set all children to the same state
                for i in range(item.childCount()):
                    child = item.child(i)
                    child.setCheckState(0, new_state)
            finally:
                # Unblock signals
                self.folder_tree.blockSignals(False)
    
    def count_images_in_folder(self, folder_path):
        """Count images in a specific folder (non-recursive)."""
        count = 0
        folder = Path(folder_path)
        if folder.exists() and folder.is_dir():
            for file_path in folder.iterdir():
                if file_path.is_file() and file_path.suffix.lower() in SUPPORTED_IMAGE_EXTENSIONS:
                    count += 1
        return count
    
    def get_subfolders_with_images(self, parent_folder):
        """Get all subfolders that contain images (directly or in sub-subfolders)."""
        subfolders = []
        parent_path = Path(parent_folder)
        
        if not parent_path.exists():
            return subfolders
        
        # Get immediate subfolders
        for item in parent_path.iterdir():
            if item.is_dir():
                # Check if this subfolder or any of its descendants has images
                # Limit iteration to prevent excessive scanning
                has_images = False
                try:
                    file_count = 0
                    for file_path in item.rglob('*'):
                        file_count += 1
                        if file_count > MAX_FILES_TO_CHECK:
                            break
                        if file_path.is_file() and file_path.suffix.lower() in SUPPORTED_IMAGE_EXTENSIONS:
                            has_images = True
                            break
                except (PermissionError, OSError):
                    # Skip folders we can't access
                    continue
                
                if has_images:
                    subfolders.append(str(item))
        
        return sorted(subfolders)
    
    def count_images_recursive(self, folder_path):
        """Count all images in a folder recursively.
        
        Note: Uses a file count limit to prevent UI freezing on very large folders.
        """
        count = 0
        folder = Path(folder_path)
        if folder.exists() and folder.is_dir():
            try:
                # Use single rglob('*') and filter by extension for efficiency
                # Limit iteration to prevent UI freezing on very large folders
                file_count = 0
                for file_path in folder.rglob('*'):
                    file_count += 1
                    if file_count > MAX_FILES_TO_CHECK:
                        # If we hit the limit, return approximate count with indicator
                        # This prevents UI freezing but gives user an idea of size
                        return count
                    if file_path.is_file() and file_path.suffix.lower() in SUPPORTED_IMAGE_EXTENSIONS:
                        count += 1
            except (PermissionError, OSError):
                # Skip folders we can't access
                pass
        return count
    
    def add_folder(self):
        """Add a folder to the tree with subfolders."""
        folder = QFileDialog.getExistingDirectory(
            self, "Select Image Folder"
        )
        if not folder:
            return
        
        # Check if folder already exists in tree
        root = self.folder_tree.invisibleRootItem()
        for i in range(root.childCount()):
            item = root.child(i)
            if item.data(0, Qt.ItemDataRole.UserRole) == folder:
                QMessageBox.information(self, "Folder Exists", "This folder has already been added.")
                return
        
        # Count images in the main folder
        total_images = self.count_images_recursive(folder)
        
        if total_images == 0:
            response = QMessageBox.question(
                self, "No Images Found",
                f"No images found in {Path(folder).name}. Add it anyway?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if response == QMessageBox.StandardButton.No:
                return
        
        # Create tree item for the main folder
        folder_item = QTreeWidgetItem()
        folder_item.setText(0, Path(folder).name)
        folder_item.setText(1, str(total_images))
        folder_item.setCheckState(0, Qt.CheckState.Checked)
        folder_item.setData(0, Qt.ItemDataRole.UserRole, folder)
        folder_item.setToolTip(0, folder)
        
        # Get subfolders
        subfolders = self.get_subfolders_with_images(folder)
        
        # Add subfolder items
        for subfolder in subfolders:
            # Count images for this subfolder
            subfolder_images = self.count_images_recursive(subfolder)
            subfolder_item = QTreeWidgetItem()
            subfolder_item.setText(0, Path(subfolder).name)
            subfolder_item.setText(1, str(subfolder_images))
            subfolder_item.setCheckState(0, Qt.CheckState.Checked)
            subfolder_item.setData(0, Qt.ItemDataRole.UserRole, subfolder)
            subfolder_item.setToolTip(0, subfolder)
            folder_item.addChild(subfolder_item)
        
        self.folder_tree.addTopLevelItem(folder_item)
        folder_item.setExpanded(True)
    
    def load_saved_folders(self):
        """Load saved folders into the tree."""
        # Group folders by parent-child relationships
        parent_folders = {}
        subfolder_states = {}
        
        # First pass: identify parent folders and their children
        for folder, enabled in self.saved_folders.items():
            folder_path = Path(folder)
            if not folder_path.exists():
                continue
            
            # Check if this folder is a subfolder of any other saved folder
            is_subfolder = False
            for other_folder in self.saved_folders.keys():
                if folder != other_folder:
                    other_path = Path(other_folder)
                    try:
                        # Check if folder is a child of other_folder
                        # relative_to() raises ValueError if paths are unrelated
                        folder_path.relative_to(other_path)
                        # It's a subfolder
                        is_subfolder = True
                        if other_folder not in parent_folders:
                            parent_folders[other_folder] = []
                        parent_folders[other_folder].append(folder)
                        subfolder_states[folder] = enabled
                        break
                    except ValueError:
                        # Not a subfolder - paths are unrelated
                        pass
            
            if not is_subfolder:
                # It's a top-level folder
                if folder not in parent_folders:
                    parent_folders[folder] = []
        
        # Second pass: create tree items for parent folders
        for parent_folder in sorted(parent_folders.keys()):
            parent_path = Path(parent_folder)
            if not parent_path.exists():
                continue
            
            # Count images
            total_images = self.count_images_recursive(parent_folder)
            
            # Create tree item for parent
            folder_item = QTreeWidgetItem()
            folder_item.setText(0, parent_path.name)
            folder_item.setText(1, str(total_images))
            folder_item.setCheckState(0, Qt.CheckState.Checked if self.saved_folders.get(parent_folder, True) else Qt.CheckState.Unchecked)
            folder_item.setData(0, Qt.ItemDataRole.UserRole, parent_folder)
            folder_item.setToolTip(0, parent_folder)
            
            # Add subfolders if any
            saved_subfolders = parent_folders[parent_folder]
            if saved_subfolders:
                # These are explicitly saved subfolders
                for subfolder in sorted(saved_subfolders):
                    subfolder_path = Path(subfolder)
                    if not subfolder_path.exists():
                        continue
                    
                    subfolder_images = self.count_images_recursive(subfolder)
                    subfolder_item = QTreeWidgetItem()
                    subfolder_item.setText(0, subfolder_path.name)
                    subfolder_item.setText(1, str(subfolder_images))
                    subfolder_item.setCheckState(0, Qt.CheckState.Checked if subfolder_states.get(subfolder, True) else Qt.CheckState.Unchecked)
                    subfolder_item.setData(0, Qt.ItemDataRole.UserRole, subfolder)
                    subfolder_item.setToolTip(0, subfolder)
                    folder_item.addChild(subfolder_item)
            else:
                # Discover subfolders that weren't explicitly saved
                discovered_subfolders = self.get_subfolders_with_images(parent_folder)
                for subfolder in discovered_subfolders:
                    subfolder_path = Path(subfolder)
                    subfolder_images = self.count_images_recursive(subfolder)
                    subfolder_item = QTreeWidgetItem()
                    subfolder_item.setText(0, subfolder_path.name)
                    subfolder_item.setText(1, str(subfolder_images))
                    # Default to checked for newly discovered subfolders
                    subfolder_item.setCheckState(0, Qt.CheckState.Checked)
                    subfolder_item.setData(0, Qt.ItemDataRole.UserRole, subfolder)
                    subfolder_item.setToolTip(0, subfolder)
                    folder_item.addChild(subfolder_item)
            
            self.folder_tree.addTopLevelItem(folder_item)
            folder_item.setExpanded(True)
            
    def remove_folder(self):
        """Remove selected folder from the tree."""
        current_item = self.folder_tree.currentItem()
        if current_item:
            # If it's a child item, remove from parent
            parent = current_item.parent()
            if parent:
                parent.removeChild(current_item)
            else:
                # It's a top-level item
                index = self.folder_tree.indexOfTopLevelItem(current_item)
                self.folder_tree.takeTopLevelItem(index)
    
    def refresh_folders(self):
        """Refresh the folder tree to detect newly added subfolders."""
        # Store current checkbox states
        current_states = {}
        root = self.folder_tree.invisibleRootItem()
        for i in range(root.childCount()):
            item = root.child(i)
            folder_path = item.data(0, Qt.ItemDataRole.UserRole)
            current_states[folder_path] = item.checkState(0) == Qt.CheckState.Checked
            
            # Store child states
            for j in range(item.childCount()):
                child_item = item.child(j)
                child_folder = child_item.data(0, Qt.ItemDataRole.UserRole)
                current_states[child_folder] = child_item.checkState(0) == Qt.CheckState.Checked
        
        # Clear the tree
        self.folder_tree.clear()
        
        # Reload folders with preserved states
        parent_folders = {}
        
        # Identify parent folders from current states
        for folder in current_states.keys():
            folder_path = Path(folder)
            if not folder_path.exists():
                continue
            
            is_subfolder = False
            for other_folder in current_states.keys():
                if folder != other_folder:
                    other_path = Path(other_folder)
                    try:
                        folder_path.relative_to(other_path)
                        is_subfolder = True
                        if other_folder not in parent_folders:
                            parent_folders[other_folder] = []
                        break
                    except ValueError:
                        pass
            
            if not is_subfolder:
                if folder not in parent_folders:
                    parent_folders[folder] = []
        
        # Recreate tree items with current states
        for parent_folder in sorted(parent_folders.keys()):
            parent_path = Path(parent_folder)
            if not parent_path.exists():
                continue
            
            # Count images
            total_images = self.count_images_recursive(parent_folder)
            
            # Create tree item for parent
            folder_item = QTreeWidgetItem()
            folder_item.setText(0, parent_path.name)
            folder_item.setText(1, str(total_images))
            folder_item.setCheckState(0, Qt.CheckState.Checked if current_states.get(parent_folder, True) else Qt.CheckState.Unchecked)
            folder_item.setData(0, Qt.ItemDataRole.UserRole, parent_folder)
            folder_item.setToolTip(0, parent_folder)
            
            # Discover all subfolders (including newly added ones)
            discovered_subfolders = self.get_subfolders_with_images(parent_folder)
            for subfolder in discovered_subfolders:
                subfolder_path = Path(subfolder)
                subfolder_images = self.count_images_recursive(subfolder)
                subfolder_item = QTreeWidgetItem()
                subfolder_item.setText(0, subfolder_path.name)
                subfolder_item.setText(1, str(subfolder_images))
                # Use existing state if available, otherwise default to checked
                subfolder_item.setCheckState(0, Qt.CheckState.Checked if current_states.get(subfolder, True) else Qt.CheckState.Unchecked)
                subfolder_item.setData(0, Qt.ItemDataRole.UserRole, subfolder)
                subfolder_item.setToolTip(0, subfolder)
                folder_item.addChild(subfolder_item)
            
            self.folder_tree.addTopLevelItem(folder_item)
            folder_item.setExpanded(True)
            
    def refresh_preset_combo(self, select=None):
        """Repopulate the preset dropdown, optionally selecting a preset by name."""
        self.preset_combo.clear()
        self.preset_combo.addItems(sorted(self.presets.keys(), key=str.lower))
        if select:
            index = self.preset_combo.findText(select)
            if index >= 0:
                self.preset_combo.setCurrentIndex(index)

    def load_preset(self):
        """Apply the selected preset to the dialog controls."""
        name = self.preset_combo.currentText()
        if not name or name not in self.presets:
            QMessageBox.information(self, "No Preset Selected", "There are no saved presets to load.")
            return

        preset = self.presets[name]
        self.image_duration.setValue(preset.get('image_duration', self.default_image_duration))
        self.session_duration.setValue(preset.get('session_duration', self.default_session_duration * 60) // 60)
        self.shuffle_checkbox.setChecked(preset.get('shuffle', True))
        self.halfway_sound_checkbox.setChecked(preset.get('halfway_sound', True))

        # Rebuild the folder tree from the preset's saved folder states
        self.saved_folders = dict(preset.get('folders', {}))
        self.folder_tree.clear()
        self.load_saved_folders()

    def save_preset(self):
        """Save the current dialog settings as a named preset."""
        name, ok = QInputDialog.getText(
            self, "Save Preset", "Preset name:",
            text=self.preset_combo.currentText()
        )
        if not ok:
            return
        name = name.strip()
        if not name:
            return

        if name in self.presets:
            response = QMessageBox.question(
                self, "Overwrite Preset",
                f"A preset named '{name}' already exists. Overwrite it?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if response == QMessageBox.StandardButton.No:
                return

        settings = self.get_settings()
        self.presets[name] = {
            'folders': settings['all_folders'],
            'image_duration': settings['image_duration'],
            'session_duration': settings['session_duration'],
            'shuffle': settings['shuffle'],
            'halfway_sound': settings['halfway_sound']
        }
        self.presets_modified = True
        self.refresh_preset_combo(select=name)

    def delete_preset(self):
        """Delete the selected preset."""
        name = self.preset_combo.currentText()
        if not name or name not in self.presets:
            return

        response = QMessageBox.question(
            self, "Delete Preset",
            f"Delete the preset '{name}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if response == QMessageBox.StandardButton.No:
            return

        del self.presets[name]
        self.presets_modified = True
        self.refresh_preset_combo()

    def get_settings(self):
        """Return the current settings."""
        # Get enabled folders from tree
        enabled_folders = []
        all_folders = {}
        
        root = self.folder_tree.invisibleRootItem()
        for i in range(root.childCount()):
            item = root.child(i)
            folder_path = item.data(0, Qt.ItemDataRole.UserRole)
            is_checked = item.checkState(0) == Qt.CheckState.Checked
            
            # For parent folders, if checked and has no children, add the whole folder
            if item.childCount() == 0:
                all_folders[folder_path] = is_checked
                if is_checked:
                    enabled_folders.append(folder_path)
            else:
                # If has children, check each child
                has_checked_children = False
                for j in range(item.childCount()):
                    child_item = item.child(j)
                    child_folder = child_item.data(0, Qt.ItemDataRole.UserRole)
                    child_checked = child_item.checkState(0) == Qt.CheckState.Checked
                    all_folders[child_folder] = child_checked
                    if child_checked:
                        enabled_folders.append(child_folder)
                        has_checked_children = True
                
                # Also store the parent folder state for persistence
                all_folders[folder_path] = is_checked
        
        return {
            'folders': enabled_folders,
            'all_folders': all_folders,
            'image_duration': self.image_duration.value(),
            'session_duration': self.session_duration.value() * 60,  # Convert to seconds
            'shuffle': self.shuffle_checkbox.isChecked(),
            'halfway_sound': self.halfway_sound_checkbox.isChecked()
        }


def format_duration(seconds):
    """Format a duration in seconds as a compact human-readable string."""
    hours, remainder = divmod(seconds, 3600)
    minutes = remainder // 60
    if hours:
        return f"{hours}h {minutes}m"
    if minutes:
        return f"{minutes}m"
    return f"{seconds}s"


def compute_streak(daily_time):
    """Count consecutive days of practice ending today (or yesterday)."""
    day = date.today()
    # The streak is still alive if the last practice was yesterday
    if day.isoformat() not in daily_time:
        day -= timedelta(days=1)
    streak = 0
    while day.isoformat() in daily_time:
        streak += 1
        day -= timedelta(days=1)
    return streak


class HomeScreenWidget(QWidget):
    """Home screen showing usage statistics, a weekly trend chart and a daily activity heatmap."""

    SURFACE = QColor("#2b2b2b")
    INK = QColor("#ffffff")
    INK_SECONDARY = QColor("#c3c2b7")
    INK_MUTED = QColor("#898781")
    GRIDLINE = QColor("#3d3d3c")
    BASELINE = QColor("#4a4a48")
    ACCENT = QColor("#f0a030")
    BAR = QColor("#3987e5")
    CELL_EMPTY = QColor("#383838")
    # Sequential blue ramp, dim -> bright; dark end validated >= 2:1 on the surface
    CELL_RAMP = [QColor("#1c5cab"), QColor("#2a78d6"), QColor("#5598e7"), QColor("#86b6ef")]

    TREND_WEEKS = 12

    def __init__(self, parent=None):
        super().__init__(parent)
        self.stats = {}
        self.setMouseTracking(True)
        self._hover_zones = []  # (QRect, tooltip text)

    def set_stats(self, stats):
        self.stats = stats
        self.update()

    def mouseMoveEvent(self, event):
        pos = event.position().toPoint()
        for rect, tip in self._hover_zones:
            if rect.contains(pos):
                QToolTip.showText(event.globalPosition().toPoint(), tip, self)
                return
        QToolTip.hideText()
        super().mouseMoveEvent(event)

    def _font(self, point_size, bold=False):
        font = QFont(self.font())
        font.setPointSize(point_size)
        font.setBold(bold)
        return font

    def _draw_centered_text(self, painter, y, text, font, color):
        """Draw a horizontally centered line of text; return the y below it."""
        painter.setFont(font)
        painter.setPen(color)
        metrics = QFontMetrics(font)
        painter.drawText(QRect(0, y, self.width(), metrics.height()),
                         Qt.AlignmentFlag.AlignHCenter, text)
        return y + metrics.height()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.fillRect(self.rect(), self.SURFACE)
        self._hover_zones = []

        sessions = self.stats.get('sessions_completed', 0)
        if not sessions:
            y = max(20, self.height() // 2 - 60)
            y = self._draw_centered_text(painter, y, "Welcome to GestureMate", self._font(24, bold=True), self.INK)
            y += 12
            y = self._draw_centered_text(
                painter, y, "Set up your image folders in File > Settings, then press Space to start.",
                self._font(11), self.INK_MUTED)
            self._draw_centered_text(
                painter, y + 4, "Your practice statistics will appear here.",
                self._font(11), self.INK_MUTED)
            return

        daily = self.stats.get('daily_time', {})
        content_w = min(760, self.width() - 60)
        left = (self.width() - content_w) // 2

        content_h = 620
        y = max(10, (self.height() - content_h) // 2)

        # --- Header ---
        y = self._draw_centered_text(painter, y, "GestureMate", self._font(24, bold=True), self.INK)
        streak = compute_streak(daily)
        if streak:
            plural = "day" if streak == 1 else "days"
            y = self._draw_centered_text(
                painter, y + 4, f"\U0001F525 {streak} {plural} in a row", self._font(13), self.ACCENT)
        y += 10

        # --- Stat row ---
        stat_items = (
            (format_duration(self.stats.get('total_time', 0)), "total practice"),
            (str(sessions), "sessions"),
            (str(self.stats.get('images_viewed', 0)), "images drawn"),
        )
        col_w = content_w // 3
        value_font = self._font(17, bold=True)
        label_font = self._font(9)
        value_h = QFontMetrics(value_font).height()
        for i, (value, label) in enumerate(stat_items):
            cell = QRect(left + i * col_w, y, col_w, value_h)
            painter.setFont(value_font)
            painter.setPen(self.INK)
            painter.drawText(cell, Qt.AlignmentFlag.AlignHCenter, value)
            painter.setFont(label_font)
            painter.setPen(self.INK_MUTED)
            painter.drawText(cell.translated(0, value_h), Qt.AlignmentFlag.AlignHCenter, label)
        y += value_h + QFontMetrics(label_font).height() + 8

        today_time = daily.get(date.today().isoformat(), 0)
        today_line = f"Today: {format_duration(today_time)}" if today_time else "No practice yet today"
        y = self._draw_centered_text(painter, y, today_line, self._font(11), self.INK_SECONDARY)
        y += 16

        # --- Weekly trend chart ---
        y = self._draw_trend_chart(painter, left, y, content_w, daily)
        y += 20

        # --- Daily activity heatmap ---
        y = self._draw_heatmap(painter, left, y, content_w, daily)
        y += 14

        self._draw_centered_text(
            painter, y, "Press Space or click 'Start Session' to begin", self._font(10), self.INK_MUTED)

    def _draw_trend_chart(self, painter, left, y, content_w, daily):
        """Draw a bar chart of practice time per week; return the y below it."""
        title_font = self._font(10)
        painter.setFont(title_font)
        painter.setPen(self.INK_SECONDARY)
        painter.drawText(left, y + QFontMetrics(title_font).ascent(),
                         f"Practice time — last {self.TREND_WEEKS} weeks")
        y += QFontMetrics(title_font).height() + 6

        # Weekly totals, oldest first, ending with the current week
        this_monday = date.today() - timedelta(days=date.today().weekday())
        weeks = []
        for i in range(self.TREND_WEEKS - 1, -1, -1):
            week_start = this_monday - timedelta(weeks=i)
            total = sum(daily.get((week_start + timedelta(days=d)).isoformat(), 0) for d in range(7))
            weeks.append((week_start, total))

        plot_h = 130
        gutter = 52
        plot = QRect(left + gutter, y, content_w - gutter, plot_h)

        # Scale to a "nice" top: whole half-hours
        max_val = max(total for _, total in weeks)
        top = max(1800, -(-max_val // 1800) * 1800)

        # Gridlines and y labels at 0 / half / top
        label_font = self._font(8)
        painter.setFont(label_font)
        for fraction in (0.0, 0.5, 1.0):
            line_y = plot.bottom() - round(plot_h * fraction)
            painter.setPen(self.BASELINE if fraction == 0.0 else self.GRIDLINE)
            painter.drawLine(plot.left(), line_y, plot.right(), line_y)
            painter.setPen(self.INK_MUTED)
            painter.drawText(QRect(left, line_y - 7, gutter - 8, 14),
                             Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter,
                             format_duration(int(top * fraction)))

        slot_w = plot.width() / len(weeks)
        bar_w = max(4, round(slot_w * 0.6))
        max_index = max(range(len(weeks)), key=lambda i: weeks[i][1])
        for i, (week_start, total) in enumerate(weeks):
            bar_x = round(plot.left() + i * slot_w + (slot_w - bar_w) / 2)
            bar_h = round(plot_h * total / top)
            bar = QRect(bar_x, plot.bottom() - bar_h, bar_w, bar_h)
            if total:
                radius = min(4, bar_w // 2, bar_h)
                painter.setPen(Qt.PenStyle.NoPen)
                painter.setBrush(self.BAR)
                # Round only the top corners: extend below and clip to the bar
                painter.save()
                painter.setClipRect(bar)
                painter.drawRoundedRect(bar.adjusted(0, 0, 0, radius), radius, radius)
                painter.restore()
                # Direct label on the tallest bar only
                if i == max_index:
                    painter.setFont(label_font)
                    painter.setPen(self.INK_SECONDARY)
                    painter.drawText(QRect(bar_x - 30, bar.top() - 16, bar_w + 60, 14),
                                     Qt.AlignmentFlag.AlignHCenter, format_duration(total))
            # x label every other week
            if i % 2 == 0:
                painter.setFont(label_font)
                painter.setPen(self.INK_MUTED)
                painter.drawText(QRect(round(plot.left() + i * slot_w), plot.bottom() + 4,
                                       round(slot_w), 14),
                                 Qt.AlignmentFlag.AlignHCenter,
                                 f"{week_start.day} {week_start.strftime('%b')}")
            tip = f"Week of {week_start.day} {week_start.strftime('%b')}\n" + (
                format_duration(total) if total else "No practice")
            self._hover_zones.append(
                (QRect(round(plot.left() + i * slot_w), plot.top(), round(slot_w), plot_h), tip))

        return plot.bottom() + 20

    def _draw_heatmap(self, painter, left, y, content_w, daily):
        """Draw a calendar heatmap of daily practice time; return the y below it."""
        cell = 15
        gap = 3
        step = cell + gap
        gutter = 30
        columns = max(8, min(52, (content_w - gutter + gap) // step))
        rows = 7

        title_font = self._font(10)
        painter.setFont(title_font)
        painter.setPen(self.INK_SECONDARY)
        painter.drawText(left, y + QFontMetrics(title_font).ascent(),
                         f"Daily activity — last {columns} weeks")
        y += QFontMetrics(title_font).height() + 4

        month_row_h = 14
        grid_x = left + gutter
        grid_y = y + month_row_h

        today = date.today()
        this_monday = today - timedelta(days=today.weekday())
        first_monday = this_monday - timedelta(weeks=columns - 1)

        window_days = [
            (first_monday + timedelta(weeks=c, days=r), c, r)
            for c in range(columns) for r in range(rows)
            if first_monday + timedelta(weeks=c, days=r) <= today
        ]
        max_day = max((daily.get(d.isoformat(), 0) for d, _, _ in window_days), default=0)

        label_font = self._font(8)

        # Month labels above the column where the month changes
        painter.setFont(label_font)
        painter.setPen(self.INK_MUTED)
        previous_month = None
        last_label_x = -1000
        for c in range(columns):
            month = (first_monday + timedelta(weeks=c)).month
            if month != previous_month:
                label_x = grid_x + c * step
                if label_x - last_label_x >= 28:
                    painter.drawText(label_x, y + QFontMetrics(label_font).ascent(),
                                     (first_monday + timedelta(weeks=c)).strftime("%b"))
                    last_label_x = label_x
                previous_month = month

        # Weekday labels
        for row, name in ((0, "Mon"), (2, "Wed"), (4, "Fri")):
            painter.drawText(QRect(left, grid_y + row * step, gutter - 6, cell),
                             Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter, name)

        # Cells
        painter.setPen(Qt.PenStyle.NoPen)
        for day, c, r in window_days:
            seconds = daily.get(day.isoformat(), 0)
            if seconds <= 0:
                color = self.CELL_EMPTY
            else:
                # Quantize into 4 intensity levels relative to the busiest day
                level = min(3, int(4 * seconds / max_day) if max_day else 0)
                color = self.CELL_RAMP[level]
            painter.setBrush(color)
            rect = QRect(grid_x + c * step, grid_y + r * step, cell, cell)
            painter.drawRoundedRect(rect, 3, 3)
            tip = f"{day.strftime('%a')} {day.day} {day.strftime('%b %Y')}\n" + (
                format_duration(seconds) if seconds else "No practice")
            self._hover_zones.append((rect.adjusted(-1, -1, 1, 1), tip))

        grid_bottom = grid_y + rows * step - gap

        # Intensity legend, bottom-right
        painter.setFont(label_font)
        legend_y = grid_bottom + 8
        swatches = [self.CELL_EMPTY] + self.CELL_RAMP
        legend_w = len(swatches) * step
        more_w = QFontMetrics(label_font).horizontalAdvance("More")
        less_w = QFontMetrics(label_font).horizontalAdvance("Less")
        x = grid_x + columns * step - gap - legend_w - more_w - 6
        painter.setPen(self.INK_MUTED)
        painter.drawText(x - less_w - 6, legend_y + QFontMetrics(label_font).ascent() + 1, "Less")
        painter.setPen(Qt.PenStyle.NoPen)
        for i, color in enumerate(swatches):
            painter.setBrush(color)
            painter.drawRoundedRect(QRect(x + i * step, legend_y, cell, cell), 3, 3)
        painter.setPen(self.INK_MUTED)
        painter.drawText(x + legend_w + 2, legend_y + QFontMetrics(label_font).ascent() + 1, "More")

        return legend_y + cell


class GestureMate(QMainWindow):
    """Main application window."""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("GestureMate - Gesture Drawing Practice")
        self.images = []
        self.images_per_folder = {}  # Track image counts per folder
        self.current_image_index = 0
        self.is_session_active = False
        self.session_time_remaining = 0
        self.image_time_remaining = 0
        self.shuffle_enabled = True
        self.current_pixmap = None
        self.flip_horizontal = False
        self.flip_vertical = False
        self.greyscale = False
        self.rotation_angle = 0  # 0, 90, 180, or 270 degrees
        self.halfway_sound_played = False
        self.image_duration_half = 0  # Cache for halfway point
        
        # Default settings
        self.image_duration = 60  # 60 seconds default
        self.session_duration = 1800  # 30 minutes default
        self.halfway_sound_enabled = True
        
        # Load saved settings
        self.config_file = self.get_config_file_path()
        config = self.load_config()
        self.saved_folders = config.get('folders', {})
        self.image_duration = config.get('image_duration', 60)
        self.session_duration = config.get('session_duration', 1800)
        self.halfway_sound_enabled = config.get('halfway_sound', True)
        self.presets = config.get('presets', {})
        self.stats = config.get('stats', {})
        self.session_images_viewed = 0

        # Setup sound effect
        self.setup_sound()

        self.setup_ui()
        self.setup_timers()
        self.show_home_screen()
        
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

        # Home screen with usage statistics (shown when no session is running)
        self.home_widget = HomeScreenWidget()
        main_layout.addWidget(self.home_widget, stretch=1)
        self.image_label.hide()
        
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
        
        # Session menu
        session_menu = menubar.addMenu("S&ession")
        
        start_action = QAction("&Start Session", self)
        start_action.setShortcut("Space")
        start_action.triggered.connect(self.start_session)
        session_menu.addAction(start_action)
        
        pause_action = QAction("&Pause/Resume", self)
        pause_action.setShortcut("P")
        pause_action.triggered.connect(self.pause_session)
        session_menu.addAction(pause_action)
        
        stop_action = QAction("S&top Session", self)
        stop_action.setShortcut("Escape")
        stop_action.triggered.connect(self.stop_session)
        session_menu.addAction(stop_action)
        
        session_menu.addSeparator()
        
        next_action = QAction("&Next Image", self)
        next_action.setShortcut("Right")
        next_action.triggered.connect(self.next_image)
        session_menu.addAction(next_action)
        
        prev_action = QAction("Pre&vious Image", self)
        prev_action.setShortcut("Left")
        prev_action.triggered.connect(self.previous_image)
        session_menu.addAction(prev_action)
        
        # Transform menu
        transform_menu = menubar.addMenu("&Transform")
        
        flip_h_action = QAction("Flip &Horizontal", self)
        flip_h_action.setShortcut("H")
        flip_h_action.triggered.connect(self.toggle_flip_horizontal)
        transform_menu.addAction(flip_h_action)
        
        flip_v_action = QAction("Flip &Vertical", self)
        flip_v_action.setShortcut("V")
        flip_v_action.triggered.connect(self.toggle_flip_vertical)
        transform_menu.addAction(flip_v_action)
        
        greyscale_action = QAction("&Greyscale", self)
        greyscale_action.setShortcut("G")
        greyscale_action.triggered.connect(self.toggle_greyscale)
        transform_menu.addAction(greyscale_action)
        
        transform_menu.addSeparator()
        
        rotate_cw_action = QAction("Rotate &Clockwise", self)
        rotate_cw_action.setShortcut("R")
        rotate_cw_action.triggered.connect(self.rotate_clockwise)
        transform_menu.addAction(rotate_cw_action)
        
        rotate_ccw_action = QAction("Rotate C&ounter-Clockwise", self)
        rotate_ccw_action.setShortcut("Shift+R")
        rotate_ccw_action.triggered.connect(self.rotate_counter_clockwise)
        transform_menu.addAction(rotate_ccw_action)
        
        reset_transform_action = QAction("Reset &Transformations", self)
        reset_transform_action.setShortcut("T")
        reset_transform_action.triggered.connect(self.reset_transformations)
        transform_menu.addAction(reset_transform_action)
        
        # Help menu
        help_menu = menubar.addMenu("&Help")
        
        about_action = QAction("&About", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
        
    def create_control_panel(self):
        """Create the control panel widget."""
        panel = QWidget()
        panel.setMaximumHeight(180)
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
        
        self.prev_btn = QPushButton("Previous")
        self.prev_btn.clicked.connect(self.previous_image)
        self.prev_btn.setEnabled(False)
        self.prev_btn.setMinimumHeight(40)
        button_layout.addWidget(self.prev_btn)
        
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
        
        # Image transformation buttons
        transform_layout = QHBoxLayout()
        
        self.flip_h_btn = QPushButton("Flip Horizontal")
        self.flip_h_btn.clicked.connect(self.toggle_flip_horizontal)
        self.flip_h_btn.setEnabled(False)
        self.flip_h_btn.setCheckable(True)
        transform_layout.addWidget(self.flip_h_btn)
        
        self.flip_v_btn = QPushButton("Flip Vertical")
        self.flip_v_btn.clicked.connect(self.toggle_flip_vertical)
        self.flip_v_btn.setEnabled(False)
        self.flip_v_btn.setCheckable(True)
        transform_layout.addWidget(self.flip_v_btn)
        
        self.greyscale_btn = QPushButton("Greyscale")
        self.greyscale_btn.clicked.connect(self.toggle_greyscale)
        self.greyscale_btn.setEnabled(False)
        self.greyscale_btn.setCheckable(True)
        transform_layout.addWidget(self.greyscale_btn)
        
        self.rotate_cw_btn = QPushButton("Rotate ↻")
        self.rotate_cw_btn.clicked.connect(self.rotate_clockwise)
        self.rotate_cw_btn.setEnabled(False)
        transform_layout.addWidget(self.rotate_cw_btn)
        
        self.rotate_ccw_btn = QPushButton("Rotate ↺")
        self.rotate_ccw_btn.clicked.connect(self.rotate_counter_clockwise)
        self.rotate_ccw_btn.setEnabled(False)
        transform_layout.addWidget(self.rotate_ccw_btn)
        
        self.reset_transform_btn = QPushButton("Reset Transform")
        self.reset_transform_btn.clicked.connect(self.reset_transformations)
        self.reset_transform_btn.setEnabled(False)
        transform_layout.addWidget(self.reset_transform_btn)
        
        layout.addLayout(transform_layout)
        
        panel.setLayout(layout)
        return panel
        
    def setup_timers(self):
        """Setup the timers for session and image display."""
        self.session_timer = QTimer()
        self.session_timer.timeout.connect(self.update_session_timer)
        
        self.image_timer = QTimer()
        self.image_timer.timeout.connect(self.update_image_timer)
    
    def setup_sound(self):
        """Setup the sound effect for halfway notification."""
        # Get the directory where the script is located
        script_dir = Path(__file__).parent
        self.beep_sound_path = script_dir / 'beep.wav'
        
        # If beep.wav doesn't exist, create it
        if not self.beep_sound_path.exists():
            self.create_beep_sound()
        
        self.use_system_beep = True
    
    def create_beep_sound(self):
        """Create a beep sound file if it doesn't exist."""
        try:
            import wave
            import struct
            import math
            
            duration = 0.2
            frequency = 800
            sample_rate = 44100
            num_samples = int(duration * sample_rate)
            
            # Generate sine wave
            samples = []
            for i in range(num_samples):
                value = int(32767 * 0.3 * math.sin(2 * math.pi * frequency * i / sample_rate))
                samples.append(struct.pack('h', value))
            
            # Write to WAV file
            with wave.open(str(self.beep_sound_path), 'w') as wav_file:
                wav_file.setnchannels(1)  # Mono
                wav_file.setsampwidth(2)  # 2 bytes per sample
                wav_file.setframerate(sample_rate)
                wav_file.writeframes(b''.join(samples))
        except Exception as e:
            print(f"Could not create beep sound: {e}")
    
    def play_beep_sound(self):
        """Play the beep sound using available system tools."""
        try:
            import shutil
            # Try different methods to play the sound
            if sys.platform == 'linux':
                # Try common Linux audio players
                for player in ['aplay', 'paplay', 'ffplay', 'play']:
                    player_path = shutil.which(player)
                    if player_path:
                        subprocess.Popen(
                            [player_path, str(self.beep_sound_path)],
                            stdout=subprocess.DEVNULL,
                            stderr=subprocess.DEVNULL
                        )
                        return
            elif sys.platform == 'darwin':  # macOS
                afplay_path = shutil.which('afplay')
                if afplay_path:
                    subprocess.Popen(
                        [afplay_path, str(self.beep_sound_path)],
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL
                    )
                    return
            elif sys.platform == 'win32':  # Windows
                import winsound
                winsound.PlaySound(str(self.beep_sound_path), winsound.SND_FILENAME | winsound.SND_ASYNC)
                return
            
            # Fallback: try QApplication.beep()
            QApplication.beep()
        except Exception as e:
            print(f"Could not play beep sound: {e}")
            # Final fallback: print to console
            print('\a')  # ASCII bell character
        
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
        
        # Add subtle hover effects to buttons
        self.setStyleSheet("""
            QPushButton:hover:!pressed {
                background-color: #5a5a5a;
                border: 1px solid #2a82da;
            }
            QPushButton:pressed {
                background-color: #404040;
            }
            QPushButton:checked {
                background-color: #2a82da;
                font-weight: bold;
            }
            QProgressBar {
                border: 1px solid #444;
                border-radius: 3px;
                text-align: center;
            }
            QProgressBar::chunk {
                background-color: #2a82da;
            }
        """)
        
    def show_settings(self):
        """Show the settings dialog."""
        dialog = SettingsDialog(
            self,
            self.saved_folders,
            self.image_duration,
            self.session_duration // 60,  # Convert back to minutes
            self.halfway_sound_enabled,
            self.presets
        )
        accepted = dialog.exec() == QDialog.DialogCode.Accepted
        self.presets = dialog.presets
        if accepted:
            settings = dialog.get_settings()
            if not settings['folders']:
                QMessageBox.warning(
                    self, "No Folders Selected",
                    "Please select at least one folder containing images."
                )
                if dialog.presets_modified:
                    self.save_config()
                return
            
            # Save configuration
            self.saved_folders = settings['all_folders']
            self.image_duration = settings['image_duration']
            self.session_duration = settings['session_duration']
            self.halfway_sound_enabled = settings['halfway_sound']
            self.save_config()
            
            self.shuffle_enabled = settings['shuffle']
            self.load_images(settings['folders'])
            
            if self.images:
                # Build folder count message
                folder_info = "\n".join([
                    f"  • {Path(folder).name}: {count} images"
                    for folder, count in self.images_per_folder.items()
                ])
                QMessageBox.information(
                    self, "Settings Applied",
                    f"Loaded {len(self.images)} total images from {len(self.images_per_folder)} folder(s):\n\n"
                    f"{folder_info}\n\n"
                    f"Image duration: {self.image_duration}s\n"
                    f"Session duration: {self.session_duration // 60}m\n"
                    f"Shuffle: {'Yes' if self.shuffle_enabled else 'No'}\n"
                    f"Halfway sound: {'Yes' if self.halfway_sound_enabled else 'No'}"
                )
            else:
                QMessageBox.warning(
                    self, "No Images Found",
                    "No supported images found in the selected folders.\n"
                    "Supported formats: JPG, PNG, BMP, GIF, WEBP"
                )
        elif dialog.presets_modified:
            # Persist preset changes even if the dialog was cancelled
            self.save_config()

    def load_images(self, folders: List[str]):
        """Load images from the specified folders."""
        self.images = []
        self.images_per_folder = {}
        
        for folder in folders:
            folder_path = Path(folder)
            if folder_path.exists():
                folder_images = []
                for file_path in folder_path.rglob('*'):
                    if file_path.is_file() and file_path.suffix.lower() in SUPPORTED_IMAGE_EXTENSIONS:
                        folder_images.append(str(file_path))
                
                # Track count per folder
                if folder_images:
                    self.images_per_folder[folder] = len(folder_images)
                    self.images.extend(folder_images)
        
        # Shuffle images if enabled
        if self.shuffle_enabled:
            random.shuffle(self.images)
        else:
            self.images.sort()
        
        self.current_image_index = 0
        
    def start_session(self):
        """Start a drawing session."""
        if not self.images:
            # Try to load images from saved folders if available
            enabled_folders = [folder for folder, enabled in self.saved_folders.items() if enabled]
            if enabled_folders:
                self.load_images(enabled_folders)
            
            if not self.images:
                response = QMessageBox.question(
                    self, "No Images",
                    "No images have been loaded yet. Would you like to configure settings now?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                )
                if response == QMessageBox.StandardButton.Yes:
                    self.show_settings()
                return
        
        self.is_session_active = True
        self.session_time_remaining = self.session_duration
        self.image_time_remaining = self.image_duration
        self.image_duration_half = self.image_duration // 2  # Integer division for exact comparison
        self.current_image_index = 0
        self.halfway_sound_played = False
        self.session_images_viewed = 1

        # Reset transformations
        self.flip_horizontal = False
        self.flip_vertical = False
        self.greyscale = False
        self.rotation_angle = 0
        self.flip_h_btn.setChecked(False)
        self.flip_v_btn.setChecked(False)
        self.greyscale_btn.setChecked(False)
        
        # Update UI
        self.start_btn.setEnabled(False)
        self.pause_btn.setEnabled(True)
        self.pause_btn.setText("Pause")
        self.prev_btn.setEnabled(True)
        self.next_btn.setEnabled(True)
        self.stop_btn.setEnabled(True)
        self.flip_h_btn.setEnabled(True)
        self.flip_v_btn.setEnabled(True)
        self.greyscale_btn.setEnabled(True)
        self.rotate_cw_btn.setEnabled(True)
        self.rotate_ccw_btn.setEnabled(True)
        self.reset_transform_btn.setEnabled(True)
        
        # Start timers
        self.session_timer.start(1000)  # 1 second interval
        self.image_timer.start(1000)

        # Display first image
        self.home_widget.hide()
        self.image_label.show()
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
        was_active = self.is_session_active
        self.session_timer.stop()
        self.image_timer.stop()
        self.is_session_active = False

        if was_active:
            self.record_session_stats()
        
        # Reset UI
        self.start_btn.setEnabled(True)
        self.pause_btn.setEnabled(False)
        self.prev_btn.setEnabled(False)
        self.next_btn.setEnabled(False)
        self.stop_btn.setEnabled(False)
        self.flip_h_btn.setEnabled(False)
        self.flip_v_btn.setEnabled(False)
        self.greyscale_btn.setEnabled(False)
        self.rotate_cw_btn.setEnabled(False)
        self.rotate_ccw_btn.setEnabled(False)
        self.reset_transform_btn.setEnabled(False)
        
        self.image_timer_label.setText("Image: --:--")
        self.session_timer_label.setText("Session: --:--")
        self.progress_bar.setValue(0)
        self.current_pixmap = None
        self.show_home_screen()
        
    def next_image(self):
        """Skip to the next image."""
        if not self.is_session_active:
            return
        
        self.current_image_index = (self.current_image_index + 1) % len(self.images)
        self.image_time_remaining = self.image_duration
        self.halfway_sound_played = False
        self.session_images_viewed += 1
        self.display_current_image()
    
    def previous_image(self):
        """Go back to the previous image."""
        if not self.is_session_active:
            return
        
        self.current_image_index = (self.current_image_index - 1) % len(self.images)
        self.image_time_remaining = self.image_duration
        self.halfway_sound_played = False
        self.display_current_image()
    
    def toggle_flip_horizontal(self):
        """Toggle horizontal flip."""
        self.flip_horizontal = not self.flip_horizontal
        if self.is_session_active and self.images:
            self.display_current_image()
    
    def toggle_flip_vertical(self):
        """Toggle vertical flip."""
        self.flip_vertical = not self.flip_vertical
        if self.is_session_active and self.images:
            self.display_current_image()
    
    def toggle_greyscale(self):
        """Toggle greyscale filter."""
        self.greyscale = not self.greyscale
        if self.is_session_active and self.images:
            self.display_current_image()
    
    def rotate_clockwise(self):
        """Rotate image 90 degrees clockwise."""
        if self.is_session_active and self.images:
            self.rotation_angle = (self.rotation_angle - 90) % 360
            self.display_current_image()
    
    def rotate_counter_clockwise(self):
        """Rotate image 90 degrees counter-clockwise."""
        if self.is_session_active and self.images:
            self.rotation_angle = (self.rotation_angle + 90) % 360
            self.display_current_image()
    
    def reset_transformations(self):
        """Reset all image transformations."""
        if self.is_session_active and self.images:
            self.flip_horizontal = False
            self.flip_vertical = False
            self.greyscale = False
            self.rotation_angle = 0
            self.flip_h_btn.setChecked(False)
            self.flip_v_btn.setChecked(False)
            self.greyscale_btn.setChecked(False)
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
        
        # Play sound at halfway point
        if (self.halfway_sound_enabled and 
            not self.halfway_sound_played and 
            self.image_time_remaining <= self.image_duration_half):
            self.halfway_sound_played = True
            try:
                self.play_beep_sound()
            except Exception as e:
                print(f"Error playing sound: {e}")
        
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
        
        # Apply transformations
        if self.greyscale or self.flip_horizontal or self.flip_vertical or self.rotation_angle != 0:
            image = pixmap.toImage()
            
            # Apply greyscale
            if self.greyscale:
                image = image.convertToFormat(QImage.Format.Format_Grayscale8)
            
            # Apply rotation first
            if self.rotation_angle != 0:
                transform = QTransform()
                transform.rotate(self.rotation_angle)
                image = image.transformed(transform, Qt.TransformationMode.SmoothTransformation)
            
            # Apply flips
            if self.flip_horizontal:
                image = image.mirrored(True, False)
            if self.flip_vertical:
                image = image.mirrored(False, True)
            
            pixmap = QPixmap.fromImage(image)
        
        # Store the current pixmap for transformations
        self.current_pixmap = pixmap
        
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
            "<li>Space: Start Session</li>"
            "<li>P: Pause/Resume</li>"
            "<li>Escape: Stop Session</li>"
            "<li>Right Arrow: Next Image</li>"
            "<li>Left Arrow: Previous Image</li>"
            "<li>H: Flip Horizontal</li>"
            "<li>V: Flip Vertical</li>"
            "<li>G: Greyscale</li>"
            "<li>R: Rotate Clockwise</li>"
            "<li>Shift+R: Rotate Counter-Clockwise</li>"
            "<li>T: Reset Transformations</li>"
            "</ul>"
        )
    
    def record_session_stats(self):
        """Record the finished session into the usage statistics."""
        elapsed = max(0, self.session_duration - self.session_time_remaining)
        if elapsed <= 0:
            return

        today = date.today().isoformat()
        daily = self.stats.setdefault('daily_time', {})
        daily[today] = daily.get(today, 0) + elapsed
        # Keep the daily history bounded
        if len(daily) > 400:
            for key in sorted(daily)[:-400]:
                del daily[key]

        self.stats['total_time'] = self.stats.get('total_time', 0) + elapsed
        self.stats['sessions_completed'] = self.stats.get('sessions_completed', 0) + 1
        self.stats['images_viewed'] = self.stats.get('images_viewed', 0) + self.session_images_viewed
        self.save_config()

    def show_home_screen(self):
        """Show the welcome screen with usage statistics in the image area."""
        self.image_label.clear()
        self.image_label.hide()
        self.home_widget.set_stats(self.stats)
        self.home_widget.show()

    def get_config_file_path(self):
        """Get the path to the configuration file."""
        config_dir = QStandardPaths.writableLocation(QStandardPaths.StandardLocation.AppConfigLocation)
        config_path = Path(config_dir)
        config_path.mkdir(parents=True, exist_ok=True)
        return config_path / "gesturemate_config.json"
    
    def load_config(self):
        """Load configuration from file."""
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r') as f:
                    return json.load(f)
        except Exception as e:
            print(f"Error loading config: {e}")
        return {}
    
    def save_config(self):
        """Save configuration to file."""
        try:
            config = {
                'folders': self.saved_folders,
                'image_duration': self.image_duration,
                'session_duration': self.session_duration,
                'halfway_sound': self.halfway_sound_enabled,
                'presets': self.presets,
                'stats': self.stats
            }
            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=2)
        except Exception as e:
            print(f"Error saving config: {e}")


def main():
    """Main entry point for the application."""
    app = QApplication(sys.argv)
    app.setApplicationName("GestureMate")

    icon_path = Path(__file__).parent / 'gesturemate.png'
    if icon_path.exists():
        app.setWindowIcon(QIcon(str(icon_path)))

    window = GestureMate()
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
