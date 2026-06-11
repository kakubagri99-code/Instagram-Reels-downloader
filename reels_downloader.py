"""
Instagram Reels Downloader Module
Downloads Instagram reels with metadata preservation
"""

import os
import json
import re
from pathlib import Path
from typing import Optional, List, Dict, Any
from datetime import datetime
import requests
from instagrapi import Client
from instagrapi.exceptions import LoginRequired, UserNotFound, MediaNotFound


class InstagramReelsDownloader:
    """Main class for downloading Instagram reels"""
    
    def __init__(self, username: Optional[str] = None, password: Optional[str] = None):
        """
        Initialize the downloader
        
        Args:
            username: Instagram username (optional)
            password: Instagram password (optional)
        """
        self.client = Client()
        self.authenticated = False
        self.username = username
        
        if username and password:
            self.login(username, password)
    
    def login(self, username: str, password: str) -> bool:
        """
        Login to Instagram account
        
        Args:
            username: Instagram username
            password: Instagram password
            
        Returns:
            True if login successful, False otherwise
        """
        try:
            self.client.login(username, password)
            self.authenticated = True
            self.username = username
            print(f"✓ Successfully logged in as {username}")
            return True
        except Exception as e:
            print(f"✗ Login failed: {str(e)}")
            return False
    
    def extract_reel_id(self, url_or_id: str) -> Optional[str]:
        """
        Extract reel ID from URL or return if already an ID
        
        Args:
            url_or_id: Instagram reel URL or reel ID
            
        Returns:
            Reel ID or None if invalid
        """
        # If it's already a short ID
        if len(url_or_id) < 20 and not url_or_id.startswith('http'):
            return url_or_id
        
        # Extract from URL
        patterns = [
            r'instagram\.com/reel/([A-Za-z0-9_-]+)',
            r'instagram\.com/p/([A-Za-z0-9_-]+)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url_or_id)
            if match:
                return match.group(1)
        
        return None
    
    def get_media_info(self, reel_id: str) -> Optional[Dict[str, Any]]:
        """
        Get reel media information
        
        Args:
            reel_id: Instagram reel ID
            
        Returns:
            Media information dictionary or None if not found
        """
        try:
            media = self.client.media_info(self.client.media_id_from_code(reel_id))
            return {
                'id': media.id,
                'caption': media.caption_text or '',
                'likes': media.like_count,
                'comments': media.comment_count,
                'author': media.user.username,
                'author_id': media.user.id,
                'created_at': media.taken_at.isoformat() if media.taken_at else None,
            }
        except (MediaNotFound, UserNotFound) as e:
            print(f"✗ Media not found: {str(e)}")
            return None
        except Exception as e:
            print(f"✗ Error getting media info: {str(e)}")
            return None
    
    def download_reel(self, url_or_id: str, output_dir: str = './downloads',
                     save_metadata: bool = True) -> bool:
        """
        Download a single reel
        
        Args:
            url_or_id: Instagram reel URL or reel ID
            output_dir: Directory to save the reel
            save_metadata: Whether to save metadata as JSON
            
        Returns:
            True if successful, False otherwise
        """
        # Extract reel ID
        reel_id = self.extract_reel_id(url_or_id)
        if not reel_id:
            print(f"✗ Invalid Instagram reel URL or ID: {url_or_id}")
            return False
        
        # Create output directory
        output_path = Path(output_dir) / reel_id
        output_path.mkdir(parents=True, exist_ok=True)
        
        print(f"\n📥 Downloading reel: {reel_id}")
        
        try:
            # Download the media
            video_path = self.client.video_download(
                self.client.media_id_from_code(reel_id),
                str(output_path)
            )
            
            print(f"✓ Video saved: {video_path}")
            
            # Save metadata if requested
            if save_metadata:
                metadata = self.get_media_info(reel_id)
                if metadata:
                    metadata['download_time'] = datetime.now().isoformat()
                    metadata_path = output_path / 'metadata.json'
                    
                    with open(metadata_path, 'w', encoding='utf-8') as f:
                        json.dump(metadata, f, indent=2, ensure_ascii=False)
                    
                    print(f"✓ Metadata saved: {metadata_path}")
            
            print(f"✓ Reel downloaded successfully!")
            return True
            
        except Exception as e:
            print(f"✗ Download failed: {str(e)}")
            return False
    
    def download_multiple(self, urls_or_ids: List[str], output_dir: str = './downloads',
                         save_metadata: bool = True, max_retries: int = 3) -> Dict[str, bool]:
        """
        Download multiple reels
        
        Args:
            urls_or_ids: List of Instagram reel URLs or IDs
            output_dir: Directory to save the reels
            save_metadata: Whether to save metadata as JSON
            max_retries: Maximum number of retries per reel
            
        Returns:
            Dictionary with download results for each reel
        """
        results = {}
        
        for i, url_or_id in enumerate(urls_or_ids, 1):
            print(f"\n[{i}/{len(urls_or_ids)}] Processing: {url_or_id}")
            
            # Retry logic
            success = False
            for attempt in range(max_retries):
                success = self.download_reel(url_or_id, output_dir, save_metadata)
                if success:
                    break
                elif attempt < max_retries - 1:
                    print(f"⏳ Retrying... (Attempt {attempt + 2}/{max_retries})")
            
            reel_id = self.extract_reel_id(url_or_id)
            results[reel_id] = success
        
        return results
    
    def download_from_file(self, file_path: str, output_dir: str = './downloads',
                          save_metadata: bool = True) -> Dict[str, bool]:
        """
        Download reels from a text file
        
        Args:
            file_path: Path to text file with URLs/IDs (one per line)
            output_dir: Directory to save the reels
            save_metadata: Whether to save metadata as JSON
            
        Returns:
            Dictionary with download results for each reel
        """
        try:
            with open(file_path, 'r') as f:
                urls = [line.strip() for line in f if line.strip()]
            
            print(f"📄 Found {len(urls)} reels to download from {file_path}")
            return self.download_multiple(urls, output_dir, save_metadata)
            
        except FileNotFoundError:
            print(f"✗ File not found: {file_path}")
            return {}
    
    def logout(self):
        """Logout from Instagram"""
        try:
            self.client.logout()
            self.authenticated = False
            print("✓ Logged out successfully")
        except Exception as e:
            print(f"✗ Logout failed: {str(e)}")
