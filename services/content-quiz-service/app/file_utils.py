"""
EduNerve Content & Quiz Service - File Upload Utilities
Handle file uploads to local storage and cloud storage
"""

import os
import hashlib
import mimetypes
import shutil
from typing import Optional, Tuple, List
from pathlib import Path
from fastapi import UploadFile, HTTPException, status
from PIL import Image
import PyPDF2
import magic
import cloudinary
import cloudinary.uploader
from dotenv import load_dotenv
import logging

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
MAX_FILE_SIZE = int(os.getenv("MAX_FILE_SIZE", "50000000"))  # 50MB default
ALLOWED_EXTENSIONS = os.getenv("ALLOWED_EXTENSIONS", "pdf,txt,doc,docx,ppt,pptx,mp4,mp3,jpg,jpeg,png").split(",")
UPLOAD_DIRECTORY = "uploads"
CLOUDINARY_ENABLED = bool(os.getenv("CLOUDINARY_CLOUD_NAME"))

# Cloudinary configuration
if CLOUDINARY_ENABLED:
    cloudinary.config(
        cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
        api_key=os.getenv("CLOUDINARY_API_KEY"),
        api_secret=os.getenv("CLOUDINARY_API_SECRET")
    )

# Create upload directory
os.makedirs(UPLOAD_DIRECTORY, exist_ok=True)


class FileUploadError(Exception):
    """Custom exception for file upload errors"""
    pass


class FileUploadService:
    """Service for handling file uploads"""
    
    def __init__(self):
        self.max_file_size = MAX_FILE_SIZE
        self.allowed_extensions = ALLOWED_EXTENSIONS
        self.upload_dir = Path(UPLOAD_DIRECTORY)
        self.cloudinary_enabled = CLOUDINARY_ENABLED
    
    def validate_file(self, file: UploadFile) -> bool:
        """Validate uploaded file"""
        # Check file size
        if file.size and file.size > self.max_file_size:
            raise FileUploadError(f"File size exceeds maximum limit of {self.max_file_size} bytes")
        
        # Check file extension
        if file.filename:
            extension = file.filename.split(".")[-1].lower()
            if extension not in self.allowed_extensions:
                raise FileUploadError(f"File type '{extension}' not allowed. Allowed types: {', '.join(self.allowed_extensions)}")
        
        return True
    
    def get_file_hash(self, file_path: str) -> str:
        """Generate MD5 hash of file for deduplication"""
        hash_md5 = hashlib.md5()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()
    
    def get_file_info(self, file_path: str) -> dict:
        """Get file information"""
        file_stat = os.stat(file_path)
        mime_type = mimetypes.guess_type(file_path)[0] or "application/octet-stream"
        
        return {
            "size": file_stat.st_size,
            "mime_type": mime_type,
            "hash": self.get_file_hash(file_path)
        }
    
    async def save_file_locally(self, file: UploadFile, school_id: int) -> Tuple[str, dict]:
        """Save file to local storage"""
        # Create school-specific directory
        school_dir = self.upload_dir / str(school_id)
        school_dir.mkdir(exist_ok=True)
        
        # Generate unique filename
        filename = self.generate_unique_filename(file.filename or "unknown")
        file_path = school_dir / filename
        
        # Save file
        try:
            with open(file_path, "wb") as buffer:
                content = await file.read()
                buffer.write(content)
            
            # Reset file pointer for further processing
            await file.seek(0)
            
            # Get file info
            file_info = self.get_file_info(str(file_path))
            
            return str(file_path), file_info
            
        except Exception as e:
            # Clean up file if saving failed
            if file_path.exists():
                file_path.unlink()
            raise FileUploadError(f"Failed to save file: {str(e)}")
    
    async def upload_to_cloudinary(self, file_path: str, school_id: int) -> str:
        """Upload file to Cloudinary"""
        if not self.cloudinary_enabled:
            raise FileUploadError("Cloudinary not configured")
        
        try:
            # Upload to Cloudinary
            result = cloudinary.uploader.upload(
                file_path,
                folder=f"edunerve/school_{school_id}",
                resource_type="auto",
                use_filename=True,
                unique_filename=True
            )
            
            return result.get("secure_url", "")
            
        except Exception as e:
            logger.error(f"Cloudinary upload failed: {str(e)}")
            raise FileUploadError(f"Failed to upload to cloud: {str(e)}")
    
    def generate_unique_filename(self, original_filename: str) -> str:
        """Generate unique filename"""
        import uuid
        from datetime import datetime
        
        # Get file extension
        extension = ""
        if "." in original_filename:
            extension = "." + original_filename.split(".")[-1]
        
        # Generate unique name
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        unique_id = str(uuid.uuid4())[:8]
        
        return f"{timestamp}_{unique_id}{extension}"
    
    async def process_upload(self, file: UploadFile, school_id: int) -> dict:
        """Process file upload with validation and storage"""
        # Validate file
        self.validate_file(file)
        
        # Save locally
        local_path, file_info = await self.save_file_locally(file, school_id)
        
        # Upload to cloud if enabled
        cloud_url = None
        if self.cloudinary_enabled:
            try:
                cloud_url = await self.upload_to_cloudinary(local_path, school_id)
            except Exception as e:
                logger.warning(f"Cloud upload failed, using local storage: {str(e)}")
        
        return {
            "filename": file.filename,
            "local_path": local_path,
            "cloud_url": cloud_url,
            "file_size": file_info["size"],
            "mime_type": file_info["mime_type"],
            "file_hash": file_info["hash"]
        }
    
    def delete_file(self, file_path: str) -> bool:
        """Delete file from local storage"""
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                return True
            return False
        except Exception as e:
            logger.error(f"Failed to delete file {file_path}: {str(e)}")
            return False


class TextExtractor:
    """Extract text from various file formats"""
    
    @staticmethod
    def extract_from_pdf(file_path: str) -> str:
        """Extract text from PDF file"""
        try:
            with open(file_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                text = ""
                for page in reader.pages:
                    text += page.extract_text() + "\n"
                return text.strip()
        except Exception as e:
            logger.error(f"Failed to extract text from PDF: {str(e)}")
            return ""
    
    @staticmethod
    def extract_from_txt(file_path: str) -> str:
        """Extract text from text file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                return file.read()
        except UnicodeDecodeError:
            # Try with different encoding
            try:
                with open(file_path, 'r', encoding='latin-1') as file:
                    return file.read()
            except Exception as e:
                logger.error(f"Failed to read text file: {str(e)}")
                return ""
        except Exception as e:
            logger.error(f"Failed to extract text from file: {str(e)}")
            return ""
    
    @staticmethod
    def extract_text(file_path: str) -> str:
        """Extract text from file based on type"""
        file_extension = file_path.split(".")[-1].lower()
        
        if file_extension == "pdf":
            return TextExtractor.extract_from_pdf(file_path)
        elif file_extension in ["txt", "text"]:
            return TextExtractor.extract_from_txt(file_path)
        else:
            logger.warning(f"Text extraction not supported for {file_extension}")
            return ""


class ImageProcessor:
    """Process and optimize images"""
    
    @staticmethod
    def optimize_image(file_path: str, max_width: int = 1920, max_height: int = 1080, quality: int = 85) -> str:
        """Optimize image for web display"""
        try:
            with Image.open(file_path) as img:
                # Convert to RGB if necessary
                if img.mode != 'RGB':
                    img = img.convert('RGB')
                
                # Resize if too large
                if img.width > max_width or img.height > max_height:
                    img.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)
                
                # Save optimized version
                optimized_path = file_path.replace(".", "_optimized.")
                img.save(optimized_path, format='JPEG', quality=quality, optimize=True)
                
                return optimized_path
                
        except Exception as e:
            logger.error(f"Failed to optimize image: {str(e)}")
            return file_path  # Return original if optimization fails
    
    @staticmethod
    def create_thumbnail(file_path: str, size: Tuple[int, int] = (200, 200)) -> str:
        """Create thumbnail of image"""
        try:
            with Image.open(file_path) as img:
                img.thumbnail(size, Image.Resampling.LANCZOS)
                
                # Save thumbnail
                thumbnail_path = file_path.replace(".", "_thumb.")
                img.save(thumbnail_path, format='JPEG', quality=85)
                
                return thumbnail_path
                
        except Exception as e:
            logger.error(f"Failed to create thumbnail: {str(e)}")
            return file_path


# Global instances
file_upload_service = FileUploadService()
text_extractor = TextExtractor()
image_processor = ImageProcessor()


# Helper functions
def get_content_type_from_file(file_path: str) -> str:
    """Determine content type from file path"""
    extension = file_path.split(".")[-1].lower()
    
    content_type_map = {
        "pdf": "pdf",
        "txt": "text",
        "doc": "text",
        "docx": "text",
        "ppt": "presentation",
        "pptx": "presentation",
        "mp4": "video",
        "mp3": "audio",
        "jpg": "image",
        "jpeg": "image",
        "png": "image"
    }
    
    return content_type_map.get(extension, "text")


def validate_file_type_for_content(file_path: str, expected_type: str) -> bool:
    """Validate if file type matches expected content type"""
    actual_type = get_content_type_from_file(file_path)
    return actual_type == expected_type


async def process_content_file(file: UploadFile, school_id: int) -> dict:
    """Process uploaded content file"""
    try:
        # Upload file
        upload_result = await file_upload_service.process_upload(file, school_id)
        
        # Extract text if applicable
        content_text = ""
        if upload_result["mime_type"].startswith("text/") or upload_result["local_path"].endswith(".pdf"):
            content_text = text_extractor.extract_text(upload_result["local_path"])
        
        # Determine content type
        content_type = get_content_type_from_file(upload_result["local_path"])
        
        # Process images
        if content_type == "image":
            # Create optimized version
            optimized_path = image_processor.optimize_image(upload_result["local_path"])
            thumbnail_path = image_processor.create_thumbnail(upload_result["local_path"])
            
            upload_result["optimized_path"] = optimized_path
            upload_result["thumbnail_path"] = thumbnail_path
        
        upload_result["content_type"] = content_type
        upload_result["content_text"] = content_text
        
        return upload_result
        
    except FileUploadError:
        raise
    except Exception as e:
        logger.error(f"Error processing content file: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process file: {str(e)}"
        )
