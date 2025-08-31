#!/usr/bin/env python3
"""
Main window for the Bulk Video Downloader application
"""

import os
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QLabel, QLineEdit, QPushButton, QTextEdit, 
    QProgressBar, QFileDialog, QGroupBox, QGridLayout,
    QSpinBox, QCheckBox, QComboBox, QMessageBox,
    QSplitter, QListWidget, QListWidgetItem
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer, QThreadPool, QRunnable, QObject
from PyQt6.QtGui import QFont, QIcon, QPixmap
import sys
import os

# Add the src directory to the path so we can import our modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from core.video_crawler import VideoCrawler, VideoInfo
from core.download_manager import DownloadManager, DownloadTask, DownloadStatus, DownloadProgressCallback


class CrawlSignals(QObject):
    """Signals for the crawler worker"""
    finished = pyqtSignal(list)  # Emits list of videos
    error = pyqtSignal(str)      # Emits error message


class DownloadSignals(QObject):
    """Signals for download progress updates"""
    progress_update = pyqtSignal(object)  # Emits DownloadTask
    download_complete = pyqtSignal(object)  # Emits DownloadTask
    download_error = pyqtSignal(object, str)  # Emits DownloadTask and error
    status_change = pyqtSignal(object, str, str)  # Emits DownloadTask, old_status, new_status


class CrawlWorker(QRunnable):
    """Worker for crawling videos in background"""
    
    def __init__(self, url: str):
        super().__init__()
        self.url = url
        self.signals = CrawlSignals()
        
    def run(self):
        """Run the crawling operation"""
        try:
            crawler = VideoCrawler()
            videos = crawler.crawl_for_videos(self.url)
            crawler.close()
            # Emit the finished signal with the videos
            self.signals.finished.emit(videos)
        except Exception as e:
            # Emit the error signal with the error message
            self.signals.error.emit(str(e))


class MainWindow(QMainWindow, DownloadProgressCallback):
    """Main application window"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Bulk Video Downloader")
        self.setMinimumSize(800, 600)
        self.video_crawler = None
        self.detected_videos = []
        self.download_manager = None
        
        # Thread safety - use Qt signals instead of locks
        self._download_signals = DownloadSignals()
        
        self.setup_ui()
        self.setup_connections()
        self.setup_download_manager()
        
        # Setup thread pool for background operations
        self.thread_pool = QThreadPool()
        self.thread_pool.setMaxThreadCount(5)
        
        # Timer for updating progress bars
        self.progress_timer = QTimer()
        self.progress_timer.timeout.connect(self.update_progress_bars)
        self.progress_timer.start(1000)  # Update every 1000ms to reduce race conditions
        
    def setup_download_manager(self):
        """Setup the download manager"""
        download_folder = self.folder_input.text()
        max_concurrent = self.concurrent_spinbox.value()
        
        self.download_manager = DownloadManager(
            max_concurrent=max_concurrent,
            download_folder=download_folder
        )
        self.download_manager.set_callback(self)
        
        # Connect download signals to UI updates
        self._download_signals.progress_update.connect(self._handle_progress_update)
        self._download_signals.download_complete.connect(self._handle_download_complete)
        self._download_signals.download_error.connect(self._handle_download_error)
        self._download_signals.status_change.connect(self._handle_status_change)
        

        

        
    def setup_ui(self):
        """Setup the user interface"""
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(15, 15, 15, 15)
        
        # Title
        title_label = QLabel("Bulk Video Downloader")
        title_font = QFont()
        title_font.setPointSize(18)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(title_label)
        
        # URL Input Section
        url_group = QGroupBox("")
        url_layout = QVBoxLayout(url_group)
        
        # URL input field
        url_input_layout = QHBoxLayout()
        url_label = QLabel("Website URL:")
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("https://example.com/videos")
        self.url_input.setMinimumHeight(35)
        
        self.crawl_button = QPushButton("Crawl for Videos")
        self.crawl_button.setMinimumHeight(35)
        self.crawl_button.setMinimumWidth(120)
        self.crawl_button.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:pressed {
                background-color: #3d8b40;
            }
        """)
        
        url_input_layout.addWidget(url_label)
        url_input_layout.addWidget(self.url_input)
        url_input_layout.addWidget(self.crawl_button)
        url_layout.addLayout(url_input_layout)
        
        main_layout.addWidget(url_group)
        
        # Download Settings Section
        settings_group = QGroupBox("Download Settings")
        settings_layout = QGridLayout(settings_group)
        
        # Download folder
        folder_label = QLabel("Download Folder:")
        self.folder_input = QLineEdit()
        self.folder_input.setText(os.path.expanduser("~/Downloads/BulkVideos"))
        self.folder_input.setMinimumHeight(30)
        
        self.browse_button = QPushButton("Browse")
        self.browse_button.setMinimumHeight(30)
        
        settings_layout.addWidget(folder_label, 0, 0)
        settings_layout.addWidget(self.folder_input, 0, 1)
        settings_layout.addWidget(self.browse_button, 0, 2)
        
        # Concurrent downloads
        concurrent_label = QLabel("Max Concurrent Downloads:")
        self.concurrent_spinbox = QSpinBox()
        self.concurrent_spinbox.setRange(1, 10)
        self.concurrent_spinbox.setValue(3)
        self.concurrent_spinbox.setMinimumHeight(30)
        
        settings_layout.addWidget(concurrent_label, 1, 0)
        settings_layout.addWidget(self.concurrent_spinbox, 1, 1)
        

        

        
        main_layout.addWidget(settings_group)
        

        
        # Splitter for video list and download progress
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Video List Section
        video_group = QGroupBox("Detected Videos")
        video_layout = QVBoxLayout(video_group)
        
        self.video_list = QListWidget()
        self.video_list.setSelectionMode(QListWidget.SelectionMode.MultiSelection)
        video_layout.addWidget(self.video_list)
        
        # Video list buttons
        video_buttons_layout = QHBoxLayout()
        self.select_all_button = QPushButton("Select All")
        self.clear_selection_button = QPushButton("Clear Selection")
        self.refresh_list_button = QPushButton("Refresh List")
        
        video_buttons_layout.addWidget(self.select_all_button)
        video_buttons_layout.addWidget(self.clear_selection_button)
        video_buttons_layout.addWidget(self.refresh_list_button)
        video_layout.addLayout(video_buttons_layout)
        
        splitter.addWidget(video_group)
        
        # Download Progress Section
        progress_group = QGroupBox("Download Progress")
        progress_layout = QVBoxLayout(progress_group)
        
        # Overall progress
        overall_progress_label = QLabel("Overall Progress:")
        self.overall_progress = QProgressBar()
        self.overall_progress.setMinimumHeight(25)
        
        progress_layout.addWidget(overall_progress_label)
        progress_layout.addWidget(self.overall_progress)
        

        
        # Download stats
        stats_layout = QHBoxLayout()
        self.stats_label = QLabel("Ready to start")
        stats_layout.addWidget(self.stats_label)
        
        progress_layout.addLayout(stats_layout)
        
        # Status text
        self.status_text = QTextEdit()
        self.status_text.setMaximumHeight(100)
        self.status_text.setReadOnly(True)
        self.status_text.setPlaceholderText("Status messages will appear here...")
        
        progress_layout.addWidget(self.status_text)
        
        # Download control buttons
        download_buttons_layout = QHBoxLayout()
        self.start_download_button = QPushButton("Start Download")
        self.start_download_button.setMinimumHeight(35)
        self.start_download_button.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                border: none;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
            QPushButton:pressed {
                background-color: #1565C0;
            }
        """)
        
        self.pause_download_button = QPushButton("Pause")
        self.pause_download_button.setMinimumHeight(35)
        self.pause_download_button.setEnabled(False)
        
        self.stop_download_button = QPushButton("Stop")
        self.stop_download_button.setMinimumHeight(35)
        self.stop_download_button.setEnabled(False)
        
        download_buttons_layout.addWidget(self.start_download_button)
        download_buttons_layout.addWidget(self.pause_download_button)
        download_buttons_layout.addWidget(self.stop_download_button)
        progress_layout.addLayout(download_buttons_layout)
        
        splitter.addWidget(progress_group)
        
        # Set splitter proportions
        splitter.setSizes([400, 400])
        main_layout.addWidget(splitter)
        
        # Status bar
        self.statusBar().showMessage("Ready to start")
        
    def setup_connections(self):
        """Setup signal connections"""
        # URL input
        self.crawl_button.clicked.connect(self.crawl_for_videos)
        self.url_input.returnPressed.connect(self.crawl_for_videos)
        
        # Folder selection
        self.browse_button.clicked.connect(self.browse_folder)
        
        # Video list
        self.select_all_button.clicked.connect(self.select_all_videos)
        self.clear_selection_button.clicked.connect(self.clear_video_selection)
        self.refresh_list_button.clicked.connect(self.refresh_video_list)
        
        # Download controls
        self.start_download_button.clicked.connect(self.start_download)
        self.pause_download_button.clicked.connect(self.pause_download)
        self.stop_download_button.clicked.connect(self.stop_download)
        
        # Settings changes
        self.concurrent_spinbox.valueChanged.connect(self.on_concurrent_changed)
        self.folder_input.textChanged.connect(self.on_folder_changed)
        

        
    def on_concurrent_changed(self, value):
        """Handle concurrent downloads setting change"""
        if self.download_manager:
            self.download_manager.max_concurrent = value
            
    def on_folder_changed(self, text):
        """Handle download folder setting change"""
        if self.download_manager:
            self.download_manager.download_folder = os.path.expanduser(text)
            os.makedirs(self.download_manager.download_folder, exist_ok=True)
        

            

            

            

            

            

            

        
    def crawl_for_videos(self):
        """Crawl the website for video files"""
        url = self.url_input.text().strip()
        if not url:
            QMessageBox.warning(self, "Input Error", "Please enter a valid URL")
            return
            
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
            self.url_input.setText(url)
            
        self.statusBar().showMessage("Crawling for videos...")
        self.log_status(f"Starting crawl for: {url}")
        
        # Disable crawl button during operation
        self.crawl_button.setEnabled(False)
        self.crawl_button.setText("Crawling...")
        
        # Create and run crawler worker
        worker = CrawlWorker(url)
        
        # Connect signals from the worker to the main window
        worker.signals.finished.connect(self.on_crawl_complete)
        worker.signals.error.connect(self.on_crawl_error)
        
        self.thread_pool.start(worker)
        
    def on_crawl_complete(self, videos):
        """Handle crawl completion"""
        self.detected_videos = videos
        self.update_video_list(videos)
        
        # Re-enable crawl button
        self.crawl_button.setEnabled(True)
        self.crawl_button.setText("Crawl for Videos")
        
        if videos:
            self.log_status(f"Crawl completed! Found {len(videos)} videos")
            self.statusBar().showMessage(f"Found {len(videos)} videos")
        else:
            self.log_status("No videos found on this page")
            self.statusBar().showMessage("No videos found")
            
    def on_crawl_error(self, error_msg):
        """Handle crawl errors"""
        self.log_status(f"Crawl error: {error_msg}")
        self.statusBar().showMessage("Crawl failed")
        
        # Re-enable crawl button
        self.crawl_button.setEnabled(True)
        self.crawl_button.setText("Crawl for Videos")
        
        QMessageBox.critical(self, "Crawl Error", f"Failed to crawl the website:\n{error_msg}")
        
    def update_video_list(self, videos):
        """Update the video list with detected videos"""
        self.video_list.clear()
        
        for video in videos:
            # Create a descriptive item text
            item_text = f"{video.title} ({video.file_type})"
            if video.detected_by:
                item_text += f" - {video.detected_by}"
                
            item = QListWidgetItem(item_text)
            item.setData(Qt.ItemDataRole.UserRole, video)  # Store video object
            self.video_list.addItem(item)
            
    def browse_folder(self):
        """Browse for download folder"""
        folder = QFileDialog.getExistingDirectory(
            self, "Select Download Folder", 
            self.folder_input.text()
        )
        if folder:
            self.folder_input.setText(folder)
            
    def select_all_videos(self):
        """Select all videos in the list"""
        for i in range(self.video_list.count()):
            self.video_list.item(i).setSelected(True)
            
    def clear_video_selection(self):
        """Clear video selection"""
        self.video_list.clearSelection()
        
    def refresh_video_list(self):
        """Refresh the video list"""
        self.log_status("Refreshing video list...")
        if self.detected_videos:
            self.update_video_list(self.detected_videos)
        
    def start_download(self):
        """Start downloading selected videos"""
        selected_items = self.video_list.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Selection Error", "Please select videos to download")
            return
            
        # Get selected videos
        selected_videos = []
        for item in selected_items:
            video = item.data(Qt.ItemDataRole.UserRole)
            if video:
                selected_videos.append(video)
                
        if not selected_videos:
            return
            
        # Add videos to download manager
        self.download_manager.add_multiple_downloads(selected_videos)
        
        # Start downloads
        self.download_manager.start_downloads()
        
        # Update UI state
        self.start_download_button.setEnabled(False)
        self.pause_download_button.setEnabled(True)
        self.stop_download_button.setEnabled(True)
        
        self.log_status(f"Started downloading {len(selected_videos)} videos")
        self.statusBar().showMessage(f"Downloading {len(selected_videos)} videos...")
        
    def pause_download(self):
        """Pause the download"""
        if self.download_manager:
            self.download_manager.pause_downloads()
            self.log_status("Downloads paused")
            self.pause_download_button.setText("Resume")
            
    def stop_download(self):
        """Stop the download"""
        if self.download_manager:
            self.download_manager.stop_downloads()
            self.log_status("Downloads stopped")
            
        # Reset UI state
        self.start_download_button.setEnabled(True)
        self.pause_download_button.setEnabled(False)
        self.pause_download_button.setText("Pause")
        self.stop_download_button.setEnabled(False)
        
    def update_progress_bars(self):
        """Update progress bars with current download status"""
        try:
            if not self.download_manager:
                return
                
            # Update overall progress
            overall_progress = self.download_manager.get_overall_progress()
            self.overall_progress.setValue(int(overall_progress))
            

                
            # Update stats
            stats = self.download_manager.get_download_stats()
            stats_text = f"Total: {stats['total']} | Completed: {stats['completed']} | Failed: {stats['failed']} | Active: {stats['active']} | Pending: {stats['pending']}"
            self.stats_label.setText(stats_text)
        except Exception as e:
            # Log any errors but don't crash
            print(f"Progress update error: {e}")
    
    def _handle_progress_update(self, task: DownloadTask):
        """Handle progress update from signal"""
        try:
            self.log_status(f"Progress: {task.video_info.title} - {task.progress:.1f}%")
        except Exception as e:
            print(f"Progress handler error: {e}")
    
    def _handle_download_complete(self, task: DownloadTask):
        """Handle download completion from signal"""
        try:
            self.log_status(f"Completed: {task.video_info.title}")
            
            # Check if all downloads are done
            if not self.download_manager.get_active_tasks() and not self.download_manager.get_pending_tasks():
                self.log_status("All downloads completed!")
                self.statusBar().showMessage("All downloads completed")
                
                # Reset UI state
                self.start_download_button.setEnabled(True)
                self.pause_download_button.setEnabled(False)
                self.pause_download_button.setText("Pause")
                self.stop_download_button.setEnabled(False)
        except Exception as e:
            print(f"Complete handler error: {e}")
    
    def _handle_download_error(self, task: DownloadTask, error: str):
        """Handle download error from signal"""
        try:
            self.log_status(f"Error downloading {task.video_info.title}: {error}")
        except Exception as e:
            print(f"Error handler error: {e}")
    
    def _handle_status_change(self, task: DownloadTask, old_status: str, new_status: str):
        """Handle status change from signal"""
        try:
            self.log_status(f"Status change: {task.video_info.title} - {old_status} → {new_status}")
        except Exception as e:
            print(f"Status change handler error: {e}")
        
    # DownloadProgressCallback methods
    def on_progress(self, task: DownloadTask):
        """Called when download progress updates"""
        try:
            # Emit signal for thread-safe UI update
            self._download_signals.progress_update.emit(task)
        except Exception as e:
            print(f"Progress callback error: {e}")
        
    def on_complete(self, task: DownloadTask):
        """Called when download completes successfully"""
        try:
            # Emit signal for thread-safe UI update
            self._download_signals.download_complete.emit(task)
        except Exception as e:
            print(f"Complete callback error: {e}")
            
    def on_error(self, task: DownloadTask, error: str):
        """Called when download encounters an error"""
        try:
            # Emit signal for thread-safe UI update
            self._download_signals.download_error.emit(task, error)
        except Exception as e:
            print(f"Error callback error: {e}")
        
    def on_status_change(self, task: DownloadTask, old_status: DownloadStatus, new_status: DownloadStatus):
        """Called when download status changes"""
        try:
            # Emit signal for thread-safe UI update
            self._download_signals.status_change.emit(task, old_status.value, new_status.value)
        except Exception as e:
            print(f"Status change callback error: {e}")
        

        
    def log_status(self, message):
        """Log a status message"""
        try:
            from datetime import datetime
            timestamp = datetime.now().strftime("%H:%M:%S")
            # Simple direct update - the progress timer runs on main thread
            self.status_text.append(f"[{timestamp}] {message}")
            self.status_text.ensureCursorVisible()
        except Exception as e:
            print(f"Log status error: {e}")
        
    def closeEvent(self, event):
        """Handle application close event"""
        if self.download_manager:
            self.download_manager.cleanup()
        event.accept()
