"""
YouTube Service - Integration with YouTube Data API for educational video content
"""

import os
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import aiohttp
import json
from urllib.parse import urlencode
import re

logger = logging.getLogger(__name__)

class YouTubeService:
    """Service for finding and managing educational YouTube content"""
    
    def __init__(self):
        self.api_key = os.getenv('YOUTUBE_API_KEY')
        self.base_url = 'https://www.googleapis.com/youtube/v3'
        self.session = None
        
        # Educational channel whitelist (known educational channels)
        self.educational_channels = {
            'Khan Academy': 'UC4a-Gbdw7vOaccHmFo40b9g',
            'Crash Course': 'UCX6b17PVsYBQ0ip5gyeme-Q',
            'TED-Ed': 'UCsooa4yRKGN_zEE8iknghZA',
            'National Geographic': 'UCpVm7bg6pXKo1Pr6k5kxG9A',
            'BBC Learning': 'UCcmWAV5f5w0U3GNaN_jX1g',
            'Veritasium': 'UCHnyfMqiRRG1u-2MsSQLbXA',
            'Kurzgesagt': 'UCsXVk37bltHxD1rDPwtNM8Q',
            'SciShow': 'UCZYTClx2T1of7BRZ86-8fow',
            'MinutePhysics': 'UCUHW94eEFW7hkUMVaZz4eDg',
            'AsapScience': 'UCC552Sd-3nyi_tk2BudLUzA'
        }
    
    async def _get_session(self):
        """Get or create aiohttp session"""
        if not self.session:
            self.session = aiohttp.ClientSession()
        return self.session
    
    async def close_session(self):
        """Close aiohttp session"""
        if self.session:
            await self.session.close()
    
    async def search_educational_videos(
        self, 
        query: str, 
        keywords: List[str] = None,
        max_results: int = 10,
        duration_preference: str = 'medium'  # short, medium, long
    ) -> List[Dict[str, Any]]:
        """Search for educational videos on YouTube"""
        try:
            if not self.api_key:
                logger.warning("YouTube API key not configured")
                return []
            
            # Build search query
            search_query = self._build_search_query(query, keywords)
            
            # Search parameters
            params = {
                'part': 'id,snippet',
                'q': search_query,
                'type': 'video',
                'maxResults': min(max_results, 50),
                'order': 'relevance',
                'safeSearch': 'strict',
                'relevanceLanguage': 'en',
                'key': self.api_key
            }
            
            # Add duration filter
            if duration_preference == 'short':
                params['videoDuration'] = 'short'  # < 4 minutes
            elif duration_preference == 'medium':
                params['videoDuration'] = 'medium'  # 4-20 minutes
            elif duration_preference == 'long':
                params['videoDuration'] = 'long'  # > 20 minutes
            
            # Add category filter for education
            params['videoCategoryId'] = '27'  # Education category
            
            session = await self._get_session()
            url = f"{self.base_url}/search"
            
            async with session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    videos = await self._process_search_results(data.get('items', []))
                    
                    # Filter and rank videos
                    filtered_videos = self._filter_educational_content(videos)
                    return filtered_videos[:max_results]
                else:
                    logger.error(f"YouTube API error: {response.status}")
                    return []
                    
        except Exception as e:
            logger.error(f"Error searching YouTube videos: {str(e)}")
            return []
    
    async def get_video_details(self, video_id: str) -> Dict[str, Any]:
        """Get detailed information about a specific video"""
        try:
            if not self.api_key:
                return {}
            
            params = {
                'part': 'snippet,contentDetails,statistics',
                'id': video_id,
                'key': self.api_key
            }
            
            session = await self._get_session()
            url = f"{self.base_url}/videos"
            
            async with session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    items = data.get('items', [])
                    
                    if items:
                        video = items[0]
                        return self._format_video_details(video)
                    
                return {}
                
        except Exception as e:
            logger.error(f"Error getting video details: {str(e)}")
            return {}
    
    async def get_channel_videos(
        self, 
        channel_id: str, 
        max_results: int = 10
    ) -> List[Dict[str, Any]]:
        """Get recent videos from a specific educational channel"""
        try:
            if not self.api_key:
                return []
            
            params = {
                'part': 'id,snippet',
                'channelId': channel_id,
                'type': 'video',
                'maxResults': max_results,
                'order': 'date',
                'key': self.api_key
            }
            
            session = await self._get_session()
            url = f"{self.base_url}/search"
            
            async with session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    videos = await self._process_search_results(data.get('items', []))
                    return videos
                else:
                    return []
                    
        except Exception as e:
            logger.error(f"Error getting channel videos: {str(e)}")
            return []
    
    async def search_by_topic(
        self, 
        topic: str, 
        subject: str = None,
        grade_level: str = None,
        max_results: int = 5
    ) -> List[Dict[str, Any]]:
        """Search for videos by educational topic"""
        try:
            # Build enhanced search query
            search_terms = [topic]
            
            if subject:
                search_terms.append(subject)
            
            if grade_level:
                # Add grade level specific terms
                if 'secondary' in grade_level.lower():
                    search_terms.extend(['high school', 'secondary school'])
                elif 'primary' in grade_level.lower():
                    search_terms.extend(['elementary', 'primary school'])
            
            # Add educational keywords
            search_terms.extend(['explained', 'tutorial', 'lesson', 'education'])
            
            query = ' '.join(search_terms)
            
            return await self.search_educational_videos(
                query=query,
                max_results=max_results,
                duration_preference='medium'
            )
            
        except Exception as e:
            logger.error(f"Error searching by topic: {str(e)}")
            return []
    
    def _build_search_query(self, query: str, keywords: List[str] = None) -> str:
        """Build optimized search query"""
        search_terms = [query]
        
        # Add keywords if provided
        if keywords:
            search_terms.extend(keywords[:3])  # Limit to 3 keywords
        
        # Add educational qualifiers
        educational_terms = ['explained', 'tutorial', 'lesson', 'education', 'learning']
        search_terms.extend(educational_terms[:2])
        
        return ' '.join(search_terms)
    
    async def _process_search_results(self, items: List[Dict]) -> List[Dict[str, Any]]:
        """Process and format search results"""
        videos = []
        
        for item in items:
            try:
                video_id = item['id']['videoId']
                snippet = item['snippet']
                
                # Get additional details
                video_details = await self.get_video_details(video_id)
                
                video = {
                    'id': video_id,
                    'title': snippet.get('title', ''),
                    'description': snippet.get('description', ''),
                    'thumbnail': snippet.get('thumbnails', {}).get('medium', {}).get('url', ''),
                    'channel': snippet.get('channelTitle', ''),
                    'channel_id': snippet.get('channelId', ''),
                    'published_at': snippet.get('publishedAt', ''),
                    'url': f"https://www.youtube.com/watch?v={video_id}",
                    'embed_url': f"https://www.youtube.com/embed/{video_id}",
                    'duration': video_details.get('duration', ''),
                    'view_count': video_details.get('view_count', 0),
                    'like_count': video_details.get('like_count', 0),
                    'educational_score': self._calculate_educational_score(snippet, video_details)
                }
                
                videos.append(video)
                
            except Exception as e:
                logger.error(f"Error processing video item: {str(e)}")
                continue
        
        return videos
    
    def _format_video_details(self, video: Dict) -> Dict[str, Any]:
        """Format video details from API response"""
        snippet = video.get('snippet', {})
        content_details = video.get('contentDetails', {})
        statistics = video.get('statistics', {})
        
        return {
            'duration': content_details.get('duration', ''),
            'view_count': int(statistics.get('viewCount', 0)),
            'like_count': int(statistics.get('likeCount', 0)),
            'comment_count': int(statistics.get('commentCount', 0)),
            'category_id': snippet.get('categoryId', ''),
            'tags': snippet.get('tags', [])
        }
    
    def _calculate_educational_score(
        self, 
        snippet: Dict, 
        video_details: Dict
    ) -> float:
        """Calculate educational relevance score"""
        score = 0.0
        
        # Check if from known educational channel
        channel_title = snippet.get('channelTitle', '').lower()
        for edu_channel in self.educational_channels:
            if edu_channel.lower() in channel_title:
                score += 2.0
                break
        
        # Check title for educational keywords
        title = snippet.get('title', '').lower()
        educational_keywords = [
            'explained', 'tutorial', 'lesson', 'how to', 'introduction',
            'basics', 'fundamentals', 'guide', 'course', 'lecture',
            'explained simply', 'for beginners', 'step by step'
        ]
        
        for keyword in educational_keywords:
            if keyword in title:
                score += 0.5
        
        # Check description for educational content
        description = snippet.get('description', '').lower()
        if any(word in description for word in ['learn', 'study', 'education', 'course']):
            score += 0.3
        
        # Consider video metrics
        view_count = video_details.get('view_count', 0)
        like_count = video_details.get('like_count', 0)
        
        if view_count > 10000:
            score += 0.5
        if like_count > 100:
            score += 0.3
        
        # Duration preference (medium length videos)
        duration = video_details.get('duration', '')
        if duration:
            duration_minutes = self._parse_duration(duration)
            if 3 <= duration_minutes <= 20:  # Ideal length for educational content
                score += 0.5
        
        return min(score, 5.0)  # Cap at 5.0
    
    def _parse_duration(self, duration: str) -> int:
        """Parse YouTube duration format (PT1M30S) to minutes"""
        try:
            # Remove PT prefix
            duration = duration.replace('PT', '')
            
            # Extract minutes and seconds
            minutes = 0
            seconds = 0
            
            if 'H' in duration:
                parts = duration.split('H')
                hours = int(parts[0])
                minutes += hours * 60
                duration = parts[1]
            
            if 'M' in duration:
                parts = duration.split('M')
                minutes += int(parts[0])
                duration = parts[1]
            
            if 'S' in duration:
                seconds = int(duration.replace('S', ''))
            
            return minutes + (seconds / 60)
            
        except Exception:
            return 0
    
    def _filter_educational_content(self, videos: List[Dict]) -> List[Dict]:
        """Filter and rank videos by educational relevance"""
        # Sort by educational score
        sorted_videos = sorted(
            videos, 
            key=lambda x: x.get('educational_score', 0), 
            reverse=True
        )
        
        # Filter out low-quality content
        filtered_videos = [
            video for video in sorted_videos 
            if video.get('educational_score', 0) >= 1.0
        ]
        
        return filtered_videos
    
    async def get_video_transcript(self, video_id: str) -> str:
        """Get video transcript if available (placeholder for future implementation)"""
        # Note: This would require additional API or service
        # For now, return empty string
        logger.info(f"Transcript extraction not implemented for video: {video_id}")
        return ""
    
    def get_educational_channels(self) -> Dict[str, str]:
        """Get list of known educational channels"""
        return self.educational_channels.copy()
    
    async def validate_video_url(self, url: str) -> bool:
        """Validate if a YouTube URL is accessible"""
        try:
            # Extract video ID from URL
            video_id = self._extract_video_id(url)
            if not video_id:
                return False
            
            # Check if video exists
            video_details = await self.get_video_details(video_id)
            return bool(video_details)
            
        except Exception as e:
            logger.error(f"Error validating video URL: {str(e)}")
            return False
    
    def _extract_video_id(self, url: str) -> str:
        """Extract video ID from YouTube URL"""
        patterns = [
            r'(?:youtube\.com\/watch\?v=|youtu\.be\/|youtube\.com\/embed\/)([^&\n?#]+)',
            r'youtube\.com\/v\/([^&\n?#]+)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        
        return ""
