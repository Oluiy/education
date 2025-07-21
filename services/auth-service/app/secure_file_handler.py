"""
EduNerve Authentication Service - Secure File Upload Handler
Secure file upload validation and processing to prevent malicious uploads
"""

import os
import mimetypes
import magic
import hashlib
import tempfile
from typing import List, Optional, Set, Dict, Any
from fastapi import HTTPException, UploadFile, status
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

class FileSecurityConfig:
    """Configuration for secure file uploads"""
    
    # Maximum file size (10MB default)
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
    
    # Allowed file extensions
    ALLOWED_EXTENSIONS = {
        'images': {'.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp'},
        'documents': {'.pdf', '.doc', '.docx', '.txt', '.rtf'},
        'spreadsheets': {'.xls', '.xlsx', '.csv'},
        'presentations': {'.ppt', '.pptx'},
        'archives': {'.zip', '.tar', '.gz'}
    }
    
    # Allowed MIME types
    ALLOWED_MIME_TYPES = {
        'image/jpeg', 'image/png', 'image/gif', 'image/webp', 'image/bmp',
        'application/pdf', 'application/msword',
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        'text/plain', 'text/rtf',
        'application/vnd.ms-excel',
        'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        'text/csv',
        'application/vnd.ms-powerpoint',
        'application/vnd.openxmlformats-officedocument.presentationml.presentation',
        'application/zip', 'application/x-tar', 'application/gzip'
    }
    
    # Dangerous file extensions to always block
    DANGEROUS_EXTENSIONS = {
        '.exe', '.bat', '.cmd', '.com', '.pif', '.scr', '.vbs', '.vbe',
        '.js', '.jse', '.jar', '.wsf', '.wsh', '.ps1', '.ps2', '.psc1',
        '.psc2', '.msh', '.msh1', '.msh2', '.mshxml', '.msh1xml', '.msh2xml',
        '.scf', '.lnk', '.inf', '.reg', '.dll', '.sys', '.drv', '.ocx',
        '.cpl', '.msi', '.msp', '.mst', '.app', '.deb', '.rpm', '.dmg',
        '.pkg', '.ipa', '.apk', '.iso', '.img', '.bin', '.run', '.command'
    }
    
    # Maximum filename length
    MAX_FILENAME_LENGTH = 255
    
    # Upload directory
    UPLOAD_DIR = "uploads"
    
    # Quarantine directory for suspicious files
    QUARANTINE_DIR = "quarantine"

class SecureFileValidator:
    """Comprehensive file validation and security checks"""
    
    @staticmethod
    def validate_filename(filename: str) -> str:
        """Validate and sanitize filename"""
        if not filename:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Filename is required"
            )
        
        # Check filename length
        if len(filename) > FileSecurityConfig.MAX_FILENAME_LENGTH:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Filename too long (max {FileSecurityConfig.MAX_FILENAME_LENGTH} characters)"
            )
        
        # Check for dangerous characters
        dangerous_chars = {'/', '\\', ':', '*', '?', '"', '<', '>', '|', '\0'}
        if any(char in filename for char in dangerous_chars):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Filename contains invalid characters"
            )
        
        # Check for path traversal
        if '..' in filename or filename.startswith('.'):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid filename"
            )
        
        # Normalize filename
        filename = filename.strip()
        
        # Check for dangerous extensions
        file_ext = Path(filename).suffix.lower()
        if file_ext in FileSecurityConfig.DANGEROUS_EXTENSIONS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File type not allowed"
            )
        
        return filename
    
    @staticmethod
    def validate_file_extension(filename: str, allowed_categories: Optional[List[str]] = None) -> str:
        """Validate file extension against allowed types"""
        file_ext = Path(filename).suffix.lower()
        
        if not file_ext:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File must have an extension"
            )
        
        # Check against allowed extensions
        allowed_extensions = set()
        
        if allowed_categories:
            for category in allowed_categories:
                if category in FileSecurityConfig.ALLOWED_EXTENSIONS:
                    allowed_extensions.update(FileSecurityConfig.ALLOWED_EXTENSIONS[category])
        else:
            # If no specific categories, allow all configured extensions
            for exts in FileSecurityConfig.ALLOWED_EXTENSIONS.values():
                allowed_extensions.update(exts)
        
        if file_ext not in allowed_extensions:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File type '{file_ext}' not allowed"
            )
        
        return file_ext
    
    @staticmethod
    async def validate_file_content(file: UploadFile) -> bytes:
        """Validate file content and check for malicious content"""
        if not file:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No file provided"
            )
        
        # Read file content
        content = await file.read()
        await file.seek(0)  # Reset file pointer
        
        # Check file size
        if len(content) > FileSecurityConfig.MAX_FILE_SIZE:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"File too large (max {FileSecurityConfig.MAX_FILE_SIZE // (1024*1024)}MB)"
            )
        
        # Check for empty file
        if len(content) == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Empty file not allowed"
            )
        
        return content
    
    @staticmethod
    def validate_mime_type(content: bytes, filename: str) -> str:
        """Validate MIME type using file content"""
        try:
            # Use python-magic to detect actual MIME type
            mime_type = magic.from_buffer(content, mime=True)
            
            # Check against allowed MIME types
            if mime_type not in FileSecurityConfig.ALLOWED_MIME_TYPES:
                logger.warning(f"Blocked file with MIME type: {mime_type}, filename: {filename}")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="File type not supported"
                )
            
            # Cross-validate with file extension
            expected_mime = mimetypes.guess_type(filename)[0]
            if expected_mime and expected_mime != mime_type:
                logger.warning(
                    f"MIME type mismatch - detected: {mime_type}, "
                    f"expected: {expected_mime}, filename: {filename}"
                )
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="File content doesn't match extension"
                )
            
            return mime_type
            
        except Exception as e:
            logger.error(f"MIME type validation failed: {e}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Could not validate file type"
            )
    
    @staticmethod
    def scan_for_malware_signatures(content: bytes, filename: str) -> bool:
        """Basic malware signature detection"""
        # Common malware signatures (simplified)
        malware_signatures = [
            b'MZ',  # PE executable header
            b'PK\x03\x04',  # ZIP header (can contain executables)
            b'\x7fELF',  # ELF executable header
            b'\xfe\xed\xfa\xce',  # Mach-O executable header
            b'<script',  # Embedded scripts
            b'javascript:',  # JavaScript URLs
            b'vbscript:',  # VBScript URLs
            b'<?php',  # PHP code
            b'<%',  # ASP/JSP code
        ]
        
        content_lower = content.lower()
        
        for signature in malware_signatures:
            if signature in content_lower:
                logger.warning(f"Malware signature detected in file: {filename}")
                return True
        
        return False
    
    @staticmethod
    def calculate_file_hash(content: bytes) -> str:
        """Calculate SHA-256 hash of file content"""
        return hashlib.sha256(content).hexdigest()

class SecureFileHandler:
    """Secure file upload handler"""
    
    def __init__(self, upload_dir: str = None):
        self.upload_dir = Path(upload_dir or FileSecurityConfig.UPLOAD_DIR)
        self.quarantine_dir = Path(FileSecurityConfig.QUARANTINE_DIR)
        
        # Create directories if they don't exist
        self.upload_dir.mkdir(parents=True, exist_ok=True)
        self.quarantine_dir.mkdir(parents=True, exist_ok=True)
    
    async def process_upload(
        self,
        file: UploadFile,
        allowed_categories: Optional[List[str]] = None,
        max_size: Optional[int] = None,
        user_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Process file upload with comprehensive security validation
        
        Args:
            file: The uploaded file
            allowed_categories: List of allowed file categories
            max_size: Maximum file size override
            user_id: ID of uploading user for logging
            
        Returns:
            Dict containing file information and upload result
        """
        try:
            # Validate filename
            filename = SecureFileValidator.validate_filename(file.filename)
            
            # Validate extension
            file_ext = SecureFileValidator.validate_file_extension(filename, allowed_categories)
            
            # Validate file content
            content = await SecureFileValidator.validate_file_content(file)
            
            # Apply custom size limit if provided
            if max_size and len(content) > max_size:
                raise HTTPException(
                    status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                    detail=f"File too large (max {max_size // (1024*1024)}MB)"
                )
            
            # Validate MIME type
            mime_type = SecureFileValidator.validate_mime_type(content, filename)
            
            # Calculate file hash
            file_hash = SecureFileValidator.calculate_file_hash(content)
            
            # Scan for malware signatures
            if SecureFileValidator.scan_for_malware_signatures(content, filename):
                # Quarantine suspicious file
                quarantine_path = self.quarantine_dir / f"{file_hash}_{filename}"
                quarantine_path.write_bytes(content)
                
                logger.warning(
                    f"Suspicious file quarantined: {filename}, "
                    f"user_id: {user_id}, hash: {file_hash}"
                )
                
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="File failed security scan"
                )
            
            # Generate secure filename
            secure_filename = self._generate_secure_filename(filename, file_hash, user_id)
            
            # Save file
            file_path = self.upload_dir / secure_filename
            file_path.write_bytes(content)
            
            # Log successful upload
            logger.info(
                f"File uploaded successfully: {filename}, "
                f"secure_name: {secure_filename}, "
                f"user_id: {user_id}, "
                f"size: {len(content)}, "
                f"hash: {file_hash}"
            )
            
            return {
                "success": True,
                "original_filename": filename,
                "secure_filename": secure_filename,
                "file_path": str(file_path),
                "file_size": len(content),
                "mime_type": mime_type,
                "file_hash": file_hash,
                "upload_timestamp": Path(file_path).stat().st_mtime
            }
            
        except HTTPException:
            # Re-raise HTTP exceptions
            raise
        except Exception as e:
            logger.error(f"File upload error: {e}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="File upload failed"
            )
    
    def _generate_secure_filename(self, original_filename: str, file_hash: str, user_id: Optional[int] = None) -> str:
        """Generate secure filename to prevent conflicts and attacks"""
        import time
        
        # Get file extension
        file_ext = Path(original_filename).suffix.lower()
        
        # Create secure filename with timestamp, hash prefix, and user ID
        timestamp = int(time.time())
        hash_prefix = file_hash[:8]
        user_prefix = f"u{user_id}_" if user_id else ""
        
        secure_name = f"{user_prefix}{timestamp}_{hash_prefix}{file_ext}"
        
        return secure_name
    
    def delete_file(self, secure_filename: str) -> bool:
        """Securely delete uploaded file"""
        try:
            file_path = self.upload_dir / secure_filename
            
            # Validate filename to prevent path traversal
            if not str(file_path).startswith(str(self.upload_dir)):
                logger.warning(f"Attempted path traversal in file deletion: {secure_filename}")
                return False
            
            if file_path.exists():
                file_path.unlink()
                logger.info(f"File deleted: {secure_filename}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"File deletion error: {e}")
            return False
    
    def get_file_info(self, secure_filename: str) -> Optional[Dict[str, Any]]:
        """Get information about uploaded file"""
        try:
            file_path = self.upload_dir / secure_filename
            
            # Validate filename to prevent path traversal
            if not str(file_path).startswith(str(self.upload_dir)):
                logger.warning(f"Attempted path traversal in file info: {secure_filename}")
                return None
            
            if not file_path.exists():
                return None
            
            stat = file_path.stat()
            
            return {
                "filename": secure_filename,
                "size": stat.st_size,
                "created": stat.st_ctime,
                "modified": stat.st_mtime,
                "path": str(file_path)
            }
            
        except Exception as e:
            logger.error(f"Error getting file info: {e}")
            return None
