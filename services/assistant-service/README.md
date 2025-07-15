# EduNerve Assistant Service

The Assistant Service is a core component of the EduNerve LMS that provides personalized AI-powered learning assistance to students. It integrates multiple AI services to generate comprehensive study resources, create personalized study plans, and track learning progress.

## Features

### 🎯 Personalized Study Plans
- AI-generated study plans based on student needs and performance
- Customizable duration and learning objectives
- Progress tracking and milestone management
- Adaptive content recommendations

### 📚 Comprehensive Study Resources
- **Text Resources**: AI-generated study notes and explanations
- **Video Resources**: Curated educational videos from YouTube
- **Audio Resources**: Text-to-speech generated audio guides
- **Practice Questions**: AI-generated quizzes and assessments

### 🤖 AI-Powered Features
- OpenAI integration for content generation
- Keyword extraction and concept mapping
- Learning analytics and performance insights
- Personalized recommendations based on student data

### 🔊 Audio Learning
- Google Text-to-Speech integration
- Custom audio guides for topics
- Pronunciation guides for difficult terms
- Audio summaries of key concepts

### 📺 Video Integration
- YouTube Data API integration
- Educational video search and curation
- Channel-based content filtering
- Video quality and educational scoring

### 📊 Learning Analytics
- Activity tracking and progress monitoring
- Performance analysis and insights
- Learning pattern identification
- Personalized improvement recommendations

## Architecture

```
assistant-service/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI application
│   ├── models.py               # SQLAlchemy models
│   ├── schemas.py              # Pydantic schemas
│   ├── database.py             # Database configuration
│   ├── auth.py                 # Authentication utilities
│   ├── assistant_service.py    # Main orchestration service
│   ├── ai_service.py           # OpenAI integration
│   ├── audio_service.py        # Google TTS integration
│   └── youtube_service.py      # YouTube API integration
├── requirements.txt            # Dependencies
├── .env                       # Environment variables
├── test_service.py            # Test suite
├── start.bat                  # Windows startup script
├── start.sh                   # Linux/Mac startup script
└── README.md                  # This file
```

## Database Models

### StudyPlan
- Stores personalized study plans for students
- Includes learning objectives, duration, and AI-generated content
- Tracks plan status and progress

### StudyResource
- Stores generated study resources (text, video, audio, quiz)
- Includes metadata, keywords, and educational content
- Supports multiple content types and difficulty levels

### StudentActivity
- Tracks all student learning activities
- Stores activity type, data, and timestamps
- Used for analytics and progress tracking

### LearningAnalytics
- Aggregated learning analytics for each student
- Includes performance metrics, preferences, and insights
- Updated based on student activities

## API Endpoints

### Study Plans
- `POST /api/v1/assistant/study-plan` - Create personalized study plan
- `GET /api/v1/assistant/study-plans` - Get all study plans
- `GET /api/v1/assistant/study-plan/{id}` - Get specific study plan

### Study Resources
- `POST /api/v1/assistant/resources` - Generate study resources
- `GET /api/v1/assistant/resources` - Get study resources (with filters)
- `GET /api/v1/assistant/resources/{id}` - Get specific resource

### Activity Tracking
- `POST /api/v1/assistant/activity` - Track student activity
- `GET /api/v1/assistant/activities` - Get student activities

### Analytics
- `GET /api/v1/assistant/analytics` - Get learning analytics

### Audio & Video
- `GET /api/v1/assistant/audio/{filename}` - Serve audio files
- `GET /api/v1/assistant/videos/search` - Search educational videos

## Configuration

### Environment Variables

```bash
# Database Configuration
DATABASE_URL=sqlite:///./assistant.db  # or PostgreSQL URL
DATABASE_TYPE=sqlite  # or postgresql

# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-3.5-turbo

# Google TTS Configuration (optional)
GOOGLE_APPLICATION_CREDENTIALS=path/to/service-account.json

# YouTube API Configuration (optional)
YOUTUBE_API_KEY=your_youtube_api_key_here

# Audio Storage
AUDIO_STORAGE_PATH=audio_files

# Service Configuration
PORT=8003
LOG_LEVEL=INFO
```

## Installation & Setup

### Prerequisites
- Python 3.8+
- PostgreSQL (optional, SQLite is default)
- OpenAI API key
- Google Cloud Service Account (for TTS)
- YouTube Data API key (for video search)

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure Environment
```bash
# Copy environment template
cp .env.example .env

# Edit .env file with your configuration
```

### 3. Database Setup
```bash
# Database tables are created automatically on startup
# For PostgreSQL, create database first:
createdb edunerve_assistant
```

### 4. Run the Service
```bash
# Development
python -m uvicorn app.main:app --host 0.0.0.0 --port 8003 --reload

# Production
python -m uvicorn app.main:app --host 0.0.0.0 --port 8003

# Using startup scripts
./start.sh    # Linux/Mac
start.bat     # Windows
```

## AI Services Integration

### OpenAI Integration
- Content generation for study materials
- Study plan creation and customization
- Practice question generation
- Learning analytics and insights

### Google TTS Integration
- Audio generation from text content
- Multiple voice options and languages
- Audio file management and serving
- Pronunciation guides

### YouTube Integration
- Educational video search and curation
- Channel-based content filtering
- Video quality assessment
- Educational content scoring

## Testing

### Run Test Suite
```bash
python test_service.py
```

### Manual Testing
```bash
# Test health endpoint
curl http://localhost:8003/health

# Test with authentication
curl -X POST http://localhost:8003/api/v1/assistant/study-plan \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "subject": "Mathematics",
    "grade_level": "Grade 10",
    "learning_objectives": ["Understand quadratic equations"],
    "duration_weeks": 4
  }'
```

## Authentication

The service uses JWT tokens for authentication. Integrate with the auth-service:

```python
# Example authentication usage
headers = {"Authorization": f"Bearer {jwt_token}"}
response = requests.post(
    "http://localhost:8003/api/v1/assistant/resources",
    headers=headers,
    json=resource_request
)
```

## Error Handling

The service includes comprehensive error handling:

- **400 Bad Request**: Invalid request data
- **401 Unauthorized**: Missing or invalid authentication
- **403 Forbidden**: Insufficient permissions
- **404 Not Found**: Resource not found
- **500 Internal Server Error**: Server errors

## Performance Considerations

### Resource Generation
- AI content generation may take 10-30 seconds
- Consider implementing background task processing
- Cache frequently requested resources

### Audio Files
- Audio files are stored locally
- Implement cleanup for old files
- Consider cloud storage for production

### Video Search
- YouTube API has rate limits
- Implement caching for search results
- Consider pre-approved video lists

## Multi-tenancy

The service supports multi-tenancy:
- All data is isolated by `school_id`
- Students can only access their own data
- Teachers can access their school's data
- Admins have school-wide access

## Monitoring & Logging

### Health Checks
- `/health` endpoint for service monitoring
- Database connection checks
- External API availability checks

### Logging
- Structured logging with timestamps
- Error tracking and alerting
- Performance metrics logging

## Security

### Authentication
- JWT token validation
- Role-based access control
- Request rate limiting

### Data Protection
- Input validation and sanitization
- SQL injection prevention
- XSS protection

## Deployment

### Docker Deployment
```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8003

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8003"]
```

### Production Considerations
- Use PostgreSQL for production database
- Implement proper logging and monitoring
- Set up SSL/TLS encryption
- Configure load balancing for high availability
- Set up automated backups

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support and questions:
- Create an issue in the repository
- Contact the development team
- Check the documentation wiki

---

**EduNerve Assistant Service** - Empowering personalized learning through AI 🎓✨
