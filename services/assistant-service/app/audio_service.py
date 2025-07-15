"""
Audio Service - Google Text-to-Speech integration for generating educational audio content
"""

import os
import logging
from typing import Optional, Dict, Any
from datetime import datetime
import hashlib
import aiofiles
from pathlib import Path

# Import Google TTS when available
try:
    from google.cloud import texttospeech
    GOOGLE_TTS_AVAILABLE = True
except ImportError:
    GOOGLE_TTS_AVAILABLE = False

# Import gTTS as fallback
try:
    from gtts import gTTS
    GTTS_AVAILABLE = True
except ImportError:
    GTTS_AVAILABLE = False

logger = logging.getLogger(__name__)

class AudioService:
    """Service for generating audio content from text"""
    
    def __init__(self):
        self.audio_dir = Path(os.getenv('AUDIO_STORAGE_PATH', 'audio_files'))
        self.audio_dir.mkdir(exist_ok=True)
        
        # Initialize Google Cloud TTS if available
        if GOOGLE_TTS_AVAILABLE and os.getenv('GOOGLE_APPLICATION_CREDENTIALS'):
            try:
                self.tts_client = texttospeech.TextToSpeechClient()
                self.use_google_tts = True
                logger.info("Google Cloud TTS initialized successfully")
            except Exception as e:
                logger.warning(f"Failed to initialize Google Cloud TTS: {str(e)}")
                self.use_google_tts = False
        else:
            self.use_google_tts = False
            logger.info("Google Cloud TTS not available, using fallback")
    
    async def generate_audio(
        self, 
        text: str, 
        filename: Optional[str] = None,
        voice_config: Optional[Dict[str, Any]] = None
    ) -> str:
        """Generate audio from text using TTS"""
        try:
            # Clean the text for TTS
            clean_text = self._clean_text_for_tts(text)
            
            # Generate filename if not provided
            if not filename:
                text_hash = hashlib.md5(clean_text.encode()).hexdigest()[:8]
                filename = f"audio_{text_hash}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp3"
            
            # Ensure filename has correct extension
            if not filename.endswith('.mp3'):
                filename += '.mp3'
            
            audio_path = self.audio_dir / filename
            
            # Check if audio file already exists
            if audio_path.exists():
                logger.info(f"Audio file already exists: {filename}")
                return str(audio_path)
            
            # Generate audio using appropriate service
            if self.use_google_tts:
                await self._generate_google_tts(clean_text, audio_path, voice_config)
            elif GTTS_AVAILABLE:
                await self._generate_gtts(clean_text, audio_path)
            else:
                raise Exception("No TTS service available")
            
            logger.info(f"Audio generated successfully: {filename}")
            return str(audio_path)
            
        except Exception as e:
            logger.error(f"Error generating audio: {str(e)}")
            raise
    
    async def _generate_google_tts(
        self, 
        text: str, 
        audio_path: Path, 
        voice_config: Optional[Dict[str, Any]] = None
    ):
        """Generate audio using Google Cloud TTS"""
        try:
            # Set up the text input
            synthesis_input = texttospeech.SynthesisInput(text=text)
            
            # Build the voice request
            voice_settings = voice_config or {}
            voice = texttospeech.VoiceSelectionParams(
                language_code=voice_settings.get('language_code', 'en-US'),
                name=voice_settings.get('name', 'en-US-Neural2-J'),  # Female voice
                ssml_gender=texttospeech.SsmlVoiceGender.FEMALE
            )
            
            # Select the type of audio file
            audio_config = texttospeech.AudioConfig(
                audio_encoding=texttospeech.AudioEncoding.MP3,
                speaking_rate=voice_settings.get('speaking_rate', 1.0),
                pitch=voice_settings.get('pitch', 0.0),
                volume_gain_db=voice_settings.get('volume_gain_db', 0.0)
            )
            
            # Perform the text-to-speech request
            response = self.tts_client.synthesize_speech(
                input=synthesis_input,
                voice=voice,
                audio_config=audio_config
            )
            
            # Write the response to the output file
            async with aiofiles.open(audio_path, 'wb') as f:
                await f.write(response.audio_content)
                
        except Exception as e:
            logger.error(f"Error with Google TTS: {str(e)}")
            raise
    
    async def _generate_gtts(self, text: str, audio_path: Path):
        """Generate audio using gTTS as fallback"""
        try:
            # Create gTTS object
            tts = gTTS(
                text=text,
                lang='en',
                slow=False,
                tld='com'
            )
            
            # Save to temporary file first
            temp_path = audio_path.with_suffix('.tmp')
            tts.save(str(temp_path))
            
            # Move to final location
            temp_path.rename(audio_path)
            
        except Exception as e:
            logger.error(f"Error with gTTS: {str(e)}")
            raise
    
    def _clean_text_for_tts(self, text: str) -> str:
        """Clean text for better TTS output"""
        # Remove special formatting markers
        text = text.replace('[PAUSE]', '. ')
        text = text.replace('[EMPHASIS]', '')
        text = text.replace('[SLOW]', '')
        
        # Replace common abbreviations
        replacements = {
            'e.g.': 'for example',
            'i.e.': 'that is',
            'etc.': 'and so on',
            'vs.': 'versus',
            'Mr.': 'Mister',
            'Mrs.': 'Missus',
            'Dr.': 'Doctor',
            'Prof.': 'Professor'
        }
        
        for abbrev, full in replacements.items():
            text = text.replace(abbrev, full)
        
        # Ensure proper spacing
        text = ' '.join(text.split())
        
        return text
    
    async def get_audio_info(self, filename: str) -> Dict[str, Any]:
        """Get information about an audio file"""
        try:
            audio_path = self.audio_dir / filename
            
            if not audio_path.exists():
                raise FileNotFoundError(f"Audio file not found: {filename}")
            
            # Get basic file info
            stat = audio_path.stat()
            
            return {
                'filename': filename,
                'path': str(audio_path),
                'size_bytes': stat.st_size,
                'created_at': datetime.fromtimestamp(stat.st_ctime),
                'modified_at': datetime.fromtimestamp(stat.st_mtime),
                'exists': True
            }
            
        except Exception as e:
            logger.error(f"Error getting audio info: {str(e)}")
            return {
                'filename': filename,
                'exists': False,
                'error': str(e)
            }
    
    async def delete_audio(self, filename: str) -> bool:
        """Delete an audio file"""
        try:
            audio_path = self.audio_dir / filename
            
            if audio_path.exists():
                audio_path.unlink()
                logger.info(f"Audio file deleted: {filename}")
                return True
            else:
                logger.warning(f"Audio file not found for deletion: {filename}")
                return False
                
        except Exception as e:
            logger.error(f"Error deleting audio file: {str(e)}")
            return False
    
    async def generate_pronunciation_guide(
        self, 
        words: list, 
        filename: Optional[str] = None
    ) -> str:
        """Generate audio pronunciation guide for difficult words"""
        try:
            # Create pronunciation text
            pronunciation_text = "Here are the pronunciations for key terms: "
            
            for word in words:
                pronunciation_text += f"{word}. {word}. "
            
            pronunciation_text += "Let me repeat that once more: "
            
            for word in words:
                pronunciation_text += f"{word}. "
            
            # Generate audio
            if not filename:
                filename = f"pronunciation_guide_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp3"
            
            return await self.generate_audio(pronunciation_text, filename)
            
        except Exception as e:
            logger.error(f"Error generating pronunciation guide: {str(e)}")
            raise
    
    async def generate_summary_audio(
        self, 
        summary_points: list, 
        filename: Optional[str] = None
    ) -> str:
        """Generate audio summary from key points"""
        try:
            # Create summary text
            summary_text = "Here's a summary of the key points: "
            
            for i, point in enumerate(summary_points, 1):
                summary_text += f"Point {i}: {point}. "
            
            summary_text += "That concludes our summary. Remember to review these key points."
            
            # Generate audio
            if not filename:
                filename = f"summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp3"
            
            return await self.generate_audio(summary_text, filename)
            
        except Exception as e:
            logger.error(f"Error generating summary audio: {str(e)}")
            raise
    
    def list_audio_files(self) -> list:
        """List all available audio files"""
        try:
            audio_files = []
            for file_path in self.audio_dir.glob('*.mp3'):
                stat = file_path.stat()
                audio_files.append({
                    'filename': file_path.name,
                    'size_bytes': stat.st_size,
                    'created_at': datetime.fromtimestamp(stat.st_ctime),
                    'modified_at': datetime.fromtimestamp(stat.st_mtime)
                })
            
            return sorted(audio_files, key=lambda x: x['created_at'], reverse=True)
            
        except Exception as e:
            logger.error(f"Error listing audio files: {str(e)}")
            return []
    
    def cleanup_old_files(self, days: int = 30) -> int:
        """Clean up audio files older than specified days"""
        try:
            cutoff_date = datetime.now().timestamp() - (days * 24 * 60 * 60)
            deleted_count = 0
            
            for file_path in self.audio_dir.glob('*.mp3'):
                if file_path.stat().st_ctime < cutoff_date:
                    file_path.unlink()
                    deleted_count += 1
                    logger.info(f"Deleted old audio file: {file_path.name}")
            
            return deleted_count
            
        except Exception as e:
            logger.error(f"Error cleaning up old files: {str(e)}")
            return 0
