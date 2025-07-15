# EduNerve Content & Quiz Service

AI-powered content management and quiz generation system for the EduNerve LMS platform.

## 🚀 Features

- **📄 Content Management**: Upload and manage PDFs, documents, videos, and images
- **🧠 AI Quiz Generation**: Generate WAEC-standard quizzes using OpenAI GPT
- **✅ Automatic Grading**: Auto-grade MCQs and theory questions with AI
- **📊 Analytics**: Track quiz performance and content usage
- **🏫 Multi-tenant**: School-based isolation and access control
- **🔒 Secure**: JWT authentication with role-based permissions
- **🌍 African-focused**: Designed for Nigerian education system

## 📦 Installation

1. **Navigate to the service directory:**
   ```bash
   cd content-quiz-service
   ```

2. **Create virtual environment:**
   ```bash
   python -m venv venv
   # Windows
   venv\Scripts\activate
   # Linux/Mac
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables:**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. **Run the application:**
   ```bash
   uvicorn app.main:app --reload --port 8001
   ```

## 🔧 Configuration

### Environment Variables

```env
# Database
DATABASE_URL=postgresql://user:password@localhost/edunerve_content_quiz

# OpenAI (Required for AI features)
OPENAI_API_KEY=your-openai-api-key-here
OPENAI_MODEL=gpt-4o-mini

# File Storage
CLOUDINARY_CLOUD_NAME=your-cloudinary-cloud-name
CLOUDINARY_API_KEY=your-cloudinary-api-key
CLOUDINARY_API_SECRET=your-cloudinary-api-secret

# Auth Service
AUTH_SERVICE_URL=http://localhost:8000/api/v1/auth

# Upload Settings
MAX_FILE_SIZE=50000000  # 50MB
ALLOWED_EXTENSIONS=pdf,txt,doc,docx,ppt,pptx,mp4,mp3,jpg,jpeg,png
```

## 🛣️ API Endpoints

### Content Management
- `POST /api/v1/content/upload` - Upload content files
- `GET /api/v1/content` - List content with filters
- `GET /api/v1/content/{id}` - Get specific content
- `PUT /api/v1/content/{id}` - Update content metadata
- `DELETE /api/v1/content/{id}` - Delete content

### Quiz Management
- `POST /api/v1/quiz/create_manual` - Create quiz manually
- `POST /api/v1/quiz/generate_ai` - Generate quiz with AI
- `GET /api/v1/quiz` - List quizzes
- `GET /api/v1/quiz/{id}` - Get specific quiz
- `PUT /api/v1/quiz/{id}` - Update quiz
- `DELETE /api/v1/quiz/{id}` - Delete quiz

### Submissions & Grading
- `POST /api/v1/quiz/submit` - Submit quiz answers
- `POST /api/v1/quiz/grade/{submission_id}` - Grade submission

### Analytics
- `GET /api/v1/stats/quiz/{quiz_id}` - Quiz statistics
- `GET /api/v1/stats/content/{content_id}` - Content statistics

## 📊 Database Schema

### Content Table
- File metadata and storage paths
- Educational categorization (subject, class, topic)
- Multi-tenant school isolation
- Content text extraction for AI processing

### Quiz Table
- Question storage in JSON format
- AI generation metadata
- Grading configuration
- Publishing status

### Submission Table
- Student answers and timing
- Grading results and feedback
- AI-generated explanations

### Grade Table
- Individual question grades
- AI confidence scores
- Teacher review capabilities

## 🧠 AI Features

### Quiz Generation
The service uses OpenAI GPT to generate WAEC-standard questions:

```python
# Example AI prompt structure
prompt = f"""
Generate {num_questions} {quiz_type} questions for {subject} at {class_level} level.
Difficulty: {difficulty_level}
Topic: {topic}

Content to base questions on:
{content_text}

Requirements:
1. Questions must be appropriate for Nigerian secondary school students
2. Follow WAEC examination standards
3. Use clear, simple English
4. Include relevant Nigerian context where applicable
"""
```

### Automatic Grading
- **MCQ**: Instant correct/incorrect marking
- **Theory**: AI-powered grading with confidence scores
- **Feedback**: Detailed explanations for incorrect answers

## 🔐 Security & Access Control

### Role-based Access
- **Students**: Can view published quizzes and submit answers
- **Teachers**: Can upload content, create/manage quizzes
- **Admins**: Full access to school's content and analytics

### Multi-tenant Isolation
- Each school's data is completely isolated
- Content sharing only through public content flag
- JWT token validation with auth service

## 📱 File Upload Support

### Supported Formats
- **Documents**: PDF, TXT, DOC, DOCX, PPT, PPTX
- **Media**: MP4, MP3, JPG, JPEG, PNG
- **Size limit**: 50MB per file

### Storage Options
- **Local**: Files stored in school-specific folders
- **Cloud**: Cloudinary integration for public access
- **Deduplication**: MD5 hash checking to prevent duplicates

## 🧪 Testing

### Quick API Test

1. **Upload content:**
   ```bash
   curl -X POST "http://localhost:8001/api/v1/content/upload" \
     -H "Authorization: Bearer YOUR_JWT_TOKEN" \
     -F "file=@sample.pdf" \
     -F "title=Mathematics Notes" \
     -F "subject=Mathematics" \
     -F "class_level=SS2"
   ```

2. **Generate AI quiz:**
   ```bash
   curl -X POST "http://localhost:8001/api/v1/quiz/generate_ai" \
     -H "Authorization: Bearer YOUR_JWT_TOKEN" \
     -H "Content-Type: application/json" \
     -d '{
       "content_id": 1,
       "subject": "Mathematics",
       "class_level": "SS2",
       "difficulty_level": "medium",
       "quiz_type": "mcq",
       "num_questions": 10
     }'
   ```

## 🔗 Integration

### Auth Service Integration
- JWT token validation for all endpoints
- User role and school verification
- Automatic user context injection

### Frontend Integration
- RESTful API with comprehensive documentation
- File upload with progress tracking
- Real-time quiz submission and grading

## 📈 Analytics & Monitoring

### Quiz Statistics
- Attempt counts and completion rates
- Score distributions and pass rates
- Question-level performance analysis

### Content Usage
- View and download tracking
- Quiz generation frequency
- Popular content identification

## 🚀 Production Deployment

### Database Setup
```bash
# PostgreSQL configuration
DATABASE_URL=postgresql://user:password@localhost/edunerve_content_quiz
```

### Environment Configuration
```bash
# Production settings
OPENAI_API_KEY=your-production-openai-key
CLOUDINARY_CLOUD_NAME=your-production-cloudinary
```

### Docker Deployment
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8001
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8001"]
```

## 🎯 Nigerian Education Focus

### WAEC Standards
- Question formats match WAEC examination style
- Appropriate difficulty levels for each class
- Nigerian context and examples in questions

### Class Level Support
- JSS1, JSS2, JSS3 (Junior Secondary School)
- SS1, SS2, SS3 (Senior Secondary School)
- Subject-specific question generation

### Language Considerations
- Simple, clear English appropriate for Nigerian students
- Avoidance of complex vocabulary
- Cultural relevance in examples and contexts

## 📞 Support

- **API Documentation**: http://localhost:8001/docs
- **Health Check**: http://localhost:8001/health
- **Service Status**: Integrated with auth service monitoring

---

**Built with ❤️ for African Education**
