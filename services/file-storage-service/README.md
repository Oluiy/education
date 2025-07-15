# EduNerve File Storage Service

## Overview
The File Storage Service provides secure, database-based file storage with advanced features for the EduNerve LMS platform. All files are stored directly in the database as binary data, eliminating filesystem dependencies and improving backup/restore capabilities.

## Features

### 📁 Database File Storage
- **No filesystem dependencies** - All files stored in database
- **BLOB storage** with metadata tracking
- **Deduplication** based on file hash
- **Encryption** support for sensitive files
- **Versioning** with complete history

### 🔒 Security & Access Control
- **Role-based access control** with permission system
- **School-level isolation** for multi-tenancy
- **File-level access control** (public, school, department, private)
- **Secure sharing** with expiration and download limits
- **Audit logging** for all file operations

### 🎯 File Processing
- **Automatic metadata extraction** (EXIF, dimensions, etc.)
- **Image processing** with thumbnail generation
- **Document text extraction** (OCR support)
- **Content type detection** and validation
- **Background processing** queue

### 📊 Analytics & Management
- **Usage analytics** and reporting
- **Storage quotas** per user and school
- **Download tracking** and statistics
- **File collections** and organization
- **Bulk operations** support

### 🔄 Integration Features
- **Multi-file upload** support
- **Search and filtering** capabilities
- **Public link sharing** with controls
- **API for service integration**
- **Backup and restore** functionality

## Tech Stack
- **Framework**: FastAPI
- **Database**: PostgreSQL/SQLite with BLOB storage
- **Authentication**: JWT tokens
- **File Processing**: Pillow, OpenCV, OCR
- **Security**: Encryption, virus scanning
- **Caching**: Redis for performance

## Installation

### Prerequisites
- Python 3.8+
- PostgreSQL (optional, SQLite is default)
- Redis (optional, for caching)

### Setup
1. Clone the repository
2. Create virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Configure environment variables:
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. Run the service:
   ```bash
   # Windows
   start.bat
   
   # Linux/Mac
   ./start.sh
   ```

## Configuration

### Environment Variables
```env
# Database
DATABASE_URL=sqlite:///./file_storage.db
# DATABASE_URL=postgresql://user:password@localhost/edunerve_files

# JWT
JWT_SECRET_KEY=your-secret-key
JWT_ALGORITHM=HS256

# Service URLs
AUTH_SERVICE_URL=http://localhost:8000

# File Storage
MAX_FILE_SIZE=50485760  # 50MB
MAX_BULK_FILES=10
ALLOWED_FILE_TYPES=["image/jpeg", "image/png", "application/pdf"]

# Processing
ENABLE_IMAGE_PROCESSING=True
ENABLE_OCR=True
ENABLE_VIDEO_PROCESSING=True

# Security
ENCRYPTION_ENABLED=True
ENCRYPTION_KEY=your-32-character-encryption-key
VIRUS_SCAN_ENABLED=False

# Cache
REDIS_URL=redis://localhost:6379/0
CACHE_TTL=3600
```

## API Endpoints

### File Upload
- `POST /api/v1/files/upload` - Upload single file
- `POST /api/v1/files/upload-multiple` - Upload multiple files

### File Management
- `GET /api/v1/files/{file_id}` - Get file metadata
- `GET /api/v1/files/{file_id}/download` - Download file
- `PUT /api/v1/files/{file_id}` - Update file metadata
- `DELETE /api/v1/files/{file_id}` - Delete file

### File Search
- `POST /api/v1/files/search` - Advanced file search
- `GET /api/v1/files` - List files with filters

### File Sharing
- `POST /api/v1/files/{file_id}/share` - Share file
- `GET /api/v1/files/{file_id}/shares` - Get file shares

### Collections
- `POST /api/v1/collections` - Create file collection
- `GET /api/v1/collections` - List collections

### Analytics
- `GET /api/v1/files/analytics` - Get file analytics
- `GET /api/v1/files/quota` - Get user quota

### Bulk Operations
- `POST /api/v1/files/bulk` - Bulk file operations

## Database Schema

### Files Table
- File metadata and binary data
- Access control and permissions
- Processing status and logs
- Usage statistics

### File Versions
- Complete version history
- Change tracking
- Rollback capabilities

### File Shares
- Sharing permissions
- Public link management
- Access tracking

### File Collections
- Organized file groups
- Bulk operations
- Shared collections

## File Processing

### Image Processing
- Thumbnail generation
- Format conversion
- EXIF data extraction
- Optimization

### Document Processing
- Text extraction (OCR)
- Preview generation
- Metadata extraction
- Format validation

### Video Processing
- Thumbnail extraction
- Format conversion
- Duration and metadata
- Compression

## Security Features

### Access Control
- Role-based permissions
- School-level isolation
- File-level access control
- Sharing restrictions

### Data Protection
- File encryption at rest
- Secure file transfer
- Virus scanning
- Input validation

### Audit Logging
- All file operations logged
- Access tracking
- Change history
- Security monitoring

## Storage Management

### Quotas
- Per-user quotas
- School-wide quotas
- File count limits
- Automatic cleanup

### Optimization
- File deduplication
- Compression
- Archiving
- Cleanup policies

## Integration

### Service Communication
- JWT authentication
- REST API endpoints
- Event notifications
- Error handling

### Client Libraries
- JavaScript SDK
- Python client
- Mobile SDK
- Web components

## Monitoring & Analytics

### File Analytics
- Usage statistics
- Popular files
- Storage trends
- User behavior

### Performance Metrics
- Upload/download speeds
- Processing times
- Error rates
- System health

## Backup & Recovery

### Backup Strategy
- Database backups include files
- Incremental backups
- Point-in-time recovery
- Cross-region replication

### Recovery Procedures
- File restoration
- Metadata recovery
- Consistency checks
- Disaster recovery

## Best Practices

### File Organization
- Use collections for grouping
- Implement naming conventions
- Tag files appropriately
- Set proper access levels

### Performance
- Optimize file sizes
- Use appropriate formats
- Implement caching
- Monitor quotas

### Security
- Regular security audits
- Access reviews
- Encryption for sensitive data
- Virus scanning

## Troubleshooting

### Common Issues
- File upload failures
- Permission errors
- Quota exceeded
- Processing failures

### Debug Tools
- Health check endpoint
- Error logging
- Performance metrics
- Database queries

## API Examples

### Upload File
```bash
curl -X POST "http://localhost:8005/api/v1/files/upload" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "file=@document.pdf" \
  -F "entity_type=content" \
  -F "access_level=school"
```

### Download File
```bash
curl -X GET "http://localhost:8005/api/v1/files/{file_id}/download" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -o downloaded_file.pdf
```

### Search Files
```bash
curl -X POST "http://localhost:8005/api/v1/files/search" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"query": "mathematics", "file_type": "document"}'
```

## Contributing

1. Fork the repository
2. Create feature branch
3. Add comprehensive tests
4. Ensure security compliance
5. Submit pull request

## License

This project is licensed under the MIT License.
