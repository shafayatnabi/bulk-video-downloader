#!/usr/bin/env python3
"""
Video crawler for detecting video files from web pages
"""

import re
import requests
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
from typing import List, Dict, Optional, Set
import logging
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor, as_completed
import time


@dataclass
class VideoInfo:
    """Information about a detected video"""
    url: str
    title: str
    file_type: str
    size: Optional[str] = None
    duration: Optional[str] = None
    quality: Optional[str] = None
    source_page: str = ""
    detected_by: str = ""


class VideoCrawler:
    """Crawler for detecting video files from web pages"""
    
    def __init__(self, max_workers: int = 5, timeout: int = 30):
        self.max_workers = max_workers
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
        # Video file extensions
        self.video_extensions = {
            '.mp4', '.avi', '.mkv', '.mov', '.wmv', '.flv', '.webm', '.m4v',
            '.3gp', '.ogv', '.ts', '.mts', '.m2ts', '.divx', '.xvid'
        }
        
        # Video MIME types
        self.video_mime_types = {
            'video/mp4', 'video/avi', 'video/x-msvideo', 'video/x-matroska',
            'video/quicktime', 'video/x-ms-wmv', 'video/x-flv', 'video/webm',
            'video/3gpp', 'video/ogg', 'video/mp2t'
        }
        
        # Video URL patterns
        self.video_patterns = [
            r'https?://[^\s<>"\']+\.(?:mp4|avi|mkv|mov|wmv|flv|webm|m4v|3gp|ogv|ts)',
            r'https?://[^\s<>"\']+/video/[^\s<>"\']+',
            r'https?://[^\s<>"\']+/media/[^\s<>"\']+',
            r'https?://[^\s<>"\']+/stream/[^\s<>"\']+',
            r'https?://[^\s<>"\']+/embed/[^\s<>"\']+',
            r'https?://[^\s<>"\']+/player/[^\s<>"\']+',
        ]
        
        # Common video hosting platforms
        self.video_platforms = {
            'youtube.com', 'youtu.be', 'vimeo.com', 'dailymotion.com',
            'twitch.tv', 'facebook.com', 'instagram.com', 'tiktok.com'
        }
        
        self.logger = logging.getLogger(__name__)
        
    def crawl_for_videos(self, url: str) -> List[VideoInfo]:
        """
        Crawl a website for video files
        
        Args:
            url: The website URL to crawl
            
        Returns:
            List of detected video information
        """
        try:
            self.logger.info(f"Starting crawl for: {url}")
            
            # Normalize URL
            if not url.startswith(('http://', 'https://')):
                url = 'https://' + url
                
            # Get the main page
            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            base_url = response.url
            
            # Collect all potential video sources
            videos = []
            
            # Method 1: Direct video file links
            direct_videos = self._find_direct_video_links(soup, base_url)
            videos.extend(direct_videos)
            
            # Method 2: Video tags
            tag_videos = self._find_video_tags(soup, base_url)
            videos.extend(tag_videos)
            
            # Method 3: Source tags
            source_videos = self._find_source_tags(soup, base_url)
            videos.extend(source_videos)
            
            # Method 4: Object/embed tags
            embed_videos = self._find_embed_videos(soup, base_url)
            videos.extend(embed_videos)
            
            # Method 5: JavaScript variables
            js_videos = self._find_javascript_videos(soup, base_url)
            videos.extend(js_videos)
            
            # Method 6: CSS background images (potential video thumbnails)
            css_videos = self._find_css_videos(soup, base_url)
            videos.extend(css_videos)
            
            # Method 7: Iframe sources
            iframe_videos = self._find_iframe_videos(soup, base_url)
            videos.extend(iframe_videos)
            
            # Remove duplicates and validate
            unique_videos = self._deduplicate_videos(videos)
            valid_videos = self._validate_videos(unique_videos)
            
            self.logger.info(f"Found {len(valid_videos)} valid videos")
            return valid_videos
            
        except Exception as e:
            self.logger.error(f"Error crawling {url}: {e}")
            return []
    
    def _find_direct_video_links(self, soup: BeautifulSoup, base_url: str) -> List[VideoInfo]:
        """Find direct links to video files"""
        videos = []
        
        # Find all links
        for link in soup.find_all('a', href=True):
            href = link['href']
            full_url = urljoin(base_url, href)
            
            # Check if it's a video file
            if self._is_video_url(full_url):
                title = link.get_text(strip=True) or self._extract_title_from_url(full_url)
                videos.append(VideoInfo(
                    url=full_url,
                    title=title,
                    file_type=self._get_file_extension(full_url),
                    source_page=base_url,
                    detected_by="direct_link"
                ))
        
        return videos
    
    def _find_video_tags(self, soup: BeautifulSoup, base_url: str) -> List[VideoInfo]:
        """Find video tags"""
        videos = []
        
        for video in soup.find_all('video'):
            # Check src attribute
            if video.get('src'):
                src = urljoin(base_url, video['src'])
                title = video.get('title') or video.get('alt') or "Video"
                videos.append(VideoInfo(
                    url=src,
                    title=title,
                    file_type=self._get_file_extension(src),
                    source_page=base_url,
                    detected_by="video_tag"
                ))
            
            # Check source tags
            for source in video.find_all('source'):
                if source.get('src'):
                    src = urljoin(base_url, source['src'])
                    title = source.get('title') or video.get('title') or "Video"
                    videos.append(VideoInfo(
                        url=src,
                        title=title,
                        file_type=self._get_file_extension(src),
                        source_page=base_url,
                        detected_by="video_source_tag"
                    ))
        
        return videos
    
    def _find_source_tags(self, soup: BeautifulSoup, base_url: str) -> List[VideoInfo]:
        """Find source tags that might contain videos"""
        videos = []
        
        for source in soup.find_all('source'):
            if source.get('src'):
                src = urljoin(base_url, source['src'])
                if self._is_video_url(src):
                    title = source.get('title') or "Video Source"
                    videos.append(VideoInfo(
                        url=src,
                        title=title,
                        file_type=self._get_file_extension(src),
                        source_page=base_url,
                        detected_by="source_tag"
                    ))
        
        return videos
    
    def _find_embed_videos(self, soup: BeautifulSoup, base_url: str) -> List[VideoInfo]:
        """Find embedded videos in object and embed tags"""
        videos = []
        
        # Object tags
        for obj in soup.find_all('object'):
            if obj.get('data'):
                data = urljoin(base_url, obj['data'])
                if self._is_video_url(data):
                    title = obj.get('title') or "Embedded Video"
                    videos.append(VideoInfo(
                        url=data,
                        title=title,
                        file_type=self._get_file_extension(data),
                        source_page=base_url,
                        detected_by="object_tag"
                    ))
        
        # Embed tags
        for embed in soup.find_all('embed'):
            if embed.get('src'):
                src = urljoin(base_url, embed['src'])
                if self._is_video_url(src):
                    title = embed.get('title') or "Embedded Video"
                    videos.append(VideoInfo(
                        url=src,
                        title=title,
                        file_type=self._get_file_extension(src),
                        source_page=base_url,
                        detected_by="embed_tag"
                    ))
        
        return videos
    
    def _find_javascript_videos(self, soup: BeautifulSoup, base_url: str) -> List[VideoInfo]:
        """Find video URLs in JavaScript code"""
        videos = []
        
        # Look for script tags
        for script in soup.find_all('script'):
            if script.string:
                # Find video URLs in JavaScript
                for pattern in self.video_patterns:
                    matches = re.findall(pattern, script.string, re.IGNORECASE)
                    for match in matches:
                        full_url = urljoin(base_url, match)
                        if self._is_video_url(full_url):
                            videos.append(VideoInfo(
                                url=full_url,
                                title=self._extract_title_from_url(full_url),
                                file_type=self._get_file_extension(full_url),
                                source_page=base_url,
                                detected_by="javascript"
                            ))
        
        return videos
    
    def _find_css_videos(self, soup: BeautifulSoup, base_url: str) -> List[VideoInfo]:
        """Find potential video URLs in CSS"""
        videos = []
        
        # Look for style tags
        for style in soup.find_all('style'):
            if style.string:
                # Find URLs in CSS
                url_pattern = r'url\(["\']?([^"\')\s]+)["\']?\)'
                matches = re.findall(url_pattern, style.string)
                for match in matches:
                    full_url = urljoin(base_url, match)
                    if self._is_video_url(full_url):
                        videos.append(VideoInfo(
                            url=full_url,
                            title=self._extract_title_from_url(full_url),
                            file_type=self._get_file_extension(full_url),
                            source_page=base_url,
                            detected_by="css"
                        ))
        
        return videos
    
    def _find_iframe_videos(self, soup: BeautifulSoup, base_url: str) -> List[VideoInfo]:
        """Find videos in iframe sources"""
        videos = []
        
        for iframe in soup.find_all('iframe'):
            if iframe.get('src'):
                src = urljoin(base_url, iframe['src'])
                
                # Check if it's a video platform
                if self._is_video_platform(src):
                    title = iframe.get('title') or "Embedded Video"
                    videos.append(VideoInfo(
                        url=src,
                        title=title,
                        file_type="embedded",
                        source_page=base_url,
                        detected_by="iframe"
                    ))
        
        return videos
    
    def _is_video_url(self, url: str) -> bool:
        """Check if a URL points to a video file"""
        parsed = urlparse(url)
        
        # Check file extension
        if any(parsed.path.lower().endswith(ext) for ext in self.video_extensions):
            return True
        
        # Check for video patterns in URL
        for pattern in self.video_patterns:
            if re.search(pattern, url, re.IGNORECASE):
                return True
        
        return False
    
    def _is_video_platform(self, url: str) -> bool:
        """Check if URL is from a known video platform"""
        parsed = urlparse(url)
        return any(platform in parsed.netloc.lower() for platform in self.video_platforms)
    
    def _get_file_extension(self, url: str) -> str:
        """Extract file extension from URL"""
        parsed = urlparse(url)
        path = parsed.path.lower()
        
        for ext in self.video_extensions:
            if path.endswith(ext):
                return ext
        
        return "unknown"
    
    def _extract_title_from_url(self, url: str) -> str:
        """Extract a title from URL"""
        parsed = urlparse(url)
        path = parsed.path
        
        # Remove file extension
        for ext in self.video_extensions:
            if path.endswith(ext):
                path = path[:-len(ext)]
        
        # Clean up the path
        title = path.split('/')[-1]
        title = title.replace('-', ' ').replace('_', ' ').replace('%20', ' ')
        title = re.sub(r'[^\w\s-]', '', title)
        
        return title.strip() or "Untitled Video"
    
    def _deduplicate_videos(self, videos: List[VideoInfo]) -> List[VideoInfo]:
        """Remove duplicate videos based on URL"""
        seen_urls = set()
        unique_videos = []
        
        for video in videos:
            if video.url not in seen_urls:
                seen_urls.add(video.url)
                unique_videos.append(video)
        
        return unique_videos
    
    def _validate_videos(self, videos: List[VideoInfo]) -> List[VideoInfo]:
        """Validate video URLs by checking if they're accessible"""
        valid_videos = []
        
        def validate_video(video: VideoInfo) -> Optional[VideoInfo]:
            try:
                # Quick HEAD request to check if URL is accessible
                response = self.session.head(video.url, timeout=10, allow_redirects=True)
                if response.status_code == 200:
                    # Check if it's actually a video
                    content_type = response.headers.get('content-type', '')
                    if any(video_type in content_type.lower() for video_type in ['video', 'stream']):
                        return video
                    elif video.file_type != "unknown":
                        return video
                return None
            except Exception:
                return None
        
        # Use ThreadPoolExecutor for concurrent validation
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_video = {executor.submit(validate_video, video): video for video in videos}
            
            for future in as_completed(future_to_video):
                result = future.result()
                if result:
                    valid_videos.append(result)
        
        return valid_videos
    
    def crawl_multiple_pages(self, urls: List[str]) -> List[VideoInfo]:
        """Crawl multiple pages for videos"""
        all_videos = []
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_url = {executor.submit(self.crawl_for_videos, url): url for url in urls}
            
            for future in as_completed(future_to_url):
                try:
                    videos = future.result()
                    all_videos.extend(videos)
                except Exception as e:
                    self.logger.error(f"Error crawling {future_to_url[future]}: {e}")
        
        return self._deduplicate_videos(all_videos)
    
    def close(self):
        """Close the session"""
        self.session.close()
