#!/usr/bin/env python3
"""
Download manager for handling multiple concurrent video downloads
"""

import os
import asyncio
import aiohttp
import aiofiles
from typing import List, Dict, Optional, Callable
from dataclasses import dataclass, field
from enum import Enum
import yt_dlp
import logging
from pathlib import Path
import time
from concurrent.futures import ThreadPoolExecutor
import threading


class DownloadStatus(Enum):
    """Download status enumeration"""
    PENDING = "pending"
    DOWNLOADING = "downloading"
    COMPLETED = "completed"
    FAILED = "failed"
    PAUSED = "paused"
    CANCELLED = "cancelled"


@dataclass
class DownloadTask:
    """Represents a single download task"""
    video_info: 'VideoInfo'  # Reference to VideoInfo from video_crawler
    status: DownloadStatus = DownloadStatus.PENDING
    progress: float = 0.0  # 0.0 to 100.0
    downloaded_bytes: int = 0
    total_bytes: int = 0
    speed: float = 0.0  # bytes per second
    eta: Optional[int] = None  # estimated time in seconds
    error_message: Optional[str] = None
    start_time: Optional[float] = None
    end_time: Optional[float] = None
    output_path: Optional[str] = None
    
    def __post_init__(self):
        self.task_id = id(self)


class DownloadProgressCallback:
    """Callback interface for download progress updates"""
    
    def on_progress(self, task: DownloadTask):
        """Called when download progress updates"""
        pass
    
    def on_complete(self, task: DownloadTask):
        """Called when download completes successfully"""
        pass
    
    def on_error(self, task: DownloadTask, error: str):
        """Called when download encounters an error"""
        pass
    
    def on_status_change(self, task: DownloadTask, old_status: DownloadStatus, new_status: DownloadStatus):
        """Called when download status changes"""
        pass


class DownloadManager:
    """Manages multiple concurrent video downloads"""
    
    def __init__(self, max_concurrent: int = 3, download_folder: str = "~/Downloads/BulkVideos"):
        self.max_concurrent = max_concurrent
        self.download_folder = os.path.expanduser(download_folder)
        self.download_tasks: Dict[int, DownloadTask] = {}
        self.active_downloads: Dict[int, DownloadTask] = {}
        self.callback: Optional[DownloadProgressCallback] = None
        self.executor = ThreadPoolExecutor(max_workers=max_concurrent)
        self.running = False
        self.paused = False
        
        # Create download folder if it doesn't exist
        os.makedirs(self.download_folder, exist_ok=True)
        
        self.logger = logging.getLogger(__name__)
        
    def set_callback(self, callback: DownloadProgressCallback):
        """Set the progress callback"""
        self.callback = callback
        
    def add_download(self, video_info: 'VideoInfo') -> int:
        """Add a video to the download queue"""
        task = DownloadTask(video_info=video_info)
        self.download_tasks[task.task_id] = task
        
        self.logger.info(f"Added download task: {video_info.title}")
        
        # Start download if we have capacity
        if len(self.active_downloads) < self.max_concurrent and self.running and not self.paused:
            self._start_download(task)
            
        return task.task_id
        
    def add_multiple_downloads(self, video_infos: List['VideoInfo']) -> List[int]:
        """Add multiple videos to the download queue"""
        task_ids = []
        for video_info in video_infos:
            task_id = self.add_download(video_info)
            task_ids.append(task_id)
        return task_ids
        
    def start_downloads(self):
        """Start the download manager"""
        if self.running:
            return
            
        self.running = True
        self.paused = False
        
        # Start pending downloads up to the concurrent limit
        pending_tasks = [task for task in self.download_tasks.values() 
                        if task.status == DownloadStatus.PENDING]
        
        for task in pending_tasks[:self.max_concurrent]:
            self._start_download(task)
            
        self.logger.info("Download manager started")
        
    def pause_downloads(self):
        """Pause all downloads"""
        self.paused = True
        for task in self.active_downloads.values():
            if task.status == DownloadStatus.DOWNLOADING:
                task.status = DownloadStatus.PAUSED
                if self.callback:
                    self.callback.on_status_change(task, DownloadStatus.DOWNLOADING, DownloadStatus.PAUSED)
                    
        self.logger.info("Downloads paused")
        
    def resume_downloads(self):
        """Resume paused downloads"""
        self.paused = False
        paused_tasks = [task for task in self.download_tasks.values() 
                       if task.status == DownloadStatus.PAUSED]
        
        for task in paused_tasks:
            if len(self.active_downloads) < self.max_concurrent:
                self._start_download(task)
            else:
                break
                
        self.logger.info("Downloads resumed")
        
    def stop_downloads(self):
        """Stop all downloads"""
        self.running = False
        
        # Cancel active downloads
        for task in self.active_downloads.values():
            task.status = DownloadStatus.CANCELLED
            if self.callback:
                self.callback.on_status_change(task, task.status, DownloadStatus.CANCELLED)
                
        self.active_downloads.clear()
        self.executor.shutdown(wait=False)
        
        self.logger.info("Download manager stopped")
        
    def remove_download(self, task_id: int):
        """Remove a download task"""
        if task_id in self.download_tasks:
            task = self.download_tasks[task_id]
            
            # Cancel if active
            if task_id in self.active_downloads:
                task.status = DownloadStatus.CANCELLED
                del self.active_downloads[task_id]
                
            del self.download_tasks[task_id]
            
            self.logger.info(f"Removed download task: {task_id}")
            
    def get_task(self, task_id: int) -> Optional[DownloadTask]:
        """Get a download task by ID"""
        return self.download_tasks.get(task_id)
        
    def get_all_tasks(self) -> List[DownloadTask]:
        """Get all download tasks"""
        return list(self.download_tasks.values())
        
    def get_active_tasks(self) -> List[DownloadTask]:
        """Get currently active download tasks"""
        return list(self.active_downloads.values())
        
    def get_pending_tasks(self) -> List[DownloadTask]:
        """Get pending download tasks"""
        return [task for task in self.download_tasks.values() 
                if task.status == DownloadStatus.PENDING]
        
    def get_completed_tasks(self) -> List[DownloadTask]:
        """Get completed download tasks"""
        return [task for task in self.download_tasks.values() 
                if task.status == DownloadStatus.COMPLETED]
        
    def get_failed_tasks(self) -> List[DownloadTask]:
        """Get failed download tasks"""
        return [task for task in self.download_tasks.values() 
                if task.status == DownloadStatus.FAILED]
        
    def _start_download(self, task: DownloadTask):
        """Start a download task"""
        if task.task_id in self.active_downloads:
            return
            
        task.status = DownloadStatus.DOWNLOADING
        task.start_time = time.time()
        self.active_downloads[task.task_id] = task
        
        if self.callback:
            self.callback.on_status_change(task, DownloadStatus.PENDING, DownloadStatus.DOWNLOADING)
            
        # Submit to thread pool
        future = self.executor.submit(self._download_video, task)
        future.add_done_callback(lambda f: self._on_download_complete(task, f))
        
    def _download_video(self, task: DownloadTask):
        """Download a single video"""
        try:
            video_info = task.video_info
            
            # Determine output filename
            filename = self._sanitize_filename(video_info.title)
            if video_info.file_type != "unknown":
                filename += video_info.file_type
            else:
                filename += ".mp4"  # Default extension
                
            output_path = os.path.join(self.download_folder, filename)
            task.output_path = output_path
            
            # Use yt-dlp for downloading
            ydl_opts = {
                'outtmpl': output_path,
                'progress_hooks': [lambda d: self._progress_hook(task, d)],
                'format': 'best',  # Download best quality
                'quiet': True,
                'no_warnings': True,
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([video_info.url])
                
            # Mark as completed
            task.status = DownloadStatus.COMPLETED
            task.progress = 100.0
            task.end_time = time.time()
            
            if self.callback:
                self.callback.on_complete(task)
                
        except Exception as e:
            # Mark as failed
            task.status = DownloadStatus.FAILED
            task.error_message = str(e)
            task.end_time = time.time()
            
            if self.callback:
                self.callback.on_error(task, str(e))
                
            self.logger.error(f"Download failed for {video_info.title}: {e}")
            
        finally:
            # Remove from active downloads
            if task.task_id in self.active_downloads:
                del self.active_downloads[task.task_id]
                
            # Start next pending download if we have capacity
            if self.running and not self.paused:
                self._start_next_pending_download()
                
    def _progress_hook(self, task: DownloadTask, d: Dict):
        """Progress hook for yt-dlp"""
        if d['status'] == 'downloading':
            # Update progress
            if 'total_bytes' in d and d['total_bytes']:
                task.total_bytes = d['total_bytes']
                task.downloaded_bytes = d.get('downloaded_bytes', 0)
                task.progress = (task.downloaded_bytes / task.total_bytes) * 100
                
            if 'speed' in d:
                task.speed = d['speed']
                
            if 'eta' in d:
                task.eta = d['eta']
                
            if self.callback:
                self.callback.on_progress(task)
                
    def _on_download_complete(self, task: DownloadTask, future):
        """Called when a download task completes"""
        try:
            # Check if there was an exception
            future.result()
        except Exception as e:
            # This shouldn't happen since we handle exceptions in _download_video
            self.logger.error(f"Unexpected error in download task: {e}")
            
    def _start_next_pending_download(self):
        """Start the next pending download if we have capacity"""
        if len(self.active_downloads) >= self.max_concurrent:
            return
            
        pending_tasks = [task for task in self.download_tasks.values() 
                        if task.status == DownloadStatus.PENDING]
        
        if pending_tasks:
            next_task = pending_tasks[0]
            self._start_download(next_task)
            
    def _sanitize_filename(self, filename: str) -> str:
        """Sanitize filename for filesystem compatibility"""
        # Remove or replace invalid characters
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            filename = filename.replace(char, '_')
            
        # Limit length
        if len(filename) > 200:
            filename = filename[:200]
            
        return filename.strip()
        
    def get_overall_progress(self) -> float:
        """Get overall progress across all tasks"""
        if not self.download_tasks:
            return 0.0
            
        total_progress = sum(task.progress for task in self.download_tasks.values())
        return total_progress / len(self.download_tasks)
        
    def get_download_stats(self) -> Dict:
        """Get download statistics"""
        total_tasks = len(self.download_tasks)
        completed = len(self.get_completed_tasks())
        failed = len(self.get_failed_tasks())
        active = len(self.active_downloads)
        pending = len(self.get_pending_tasks())
        
        return {
            'total': total_tasks,
            'completed': completed,
            'failed': failed,
            'active': active,
            'pending': pending,
            'overall_progress': self.get_overall_progress()
        }
        
    def cleanup(self):
        """Clean up resources"""
        self.stop_downloads()
        self.executor.shutdown(wait=True)

