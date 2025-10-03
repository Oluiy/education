# 🎓 EduNerve - AI-Powered Educational Platform

> **A comprehensive Learning Management System designed for African secondary schools with offline-first capabilities and AI-powered features.**

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com)
[![Next.js](https://img.shields.io/badge/Next.js-14+-black.svg)](https://nextjs.org)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15+-blue.svg)](https://postgresql.org)
[![Redis](https://img.shields.io/badge/Redis-7+-red.svg)](https://redis.io)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)](https://docker.com)

## 🌟 Project Overview

EduNerve is a production-ready educational SaaS platform that addresses the unique challenges of African schools through:

- **🏗️ Microservices Architecture**: 9 independent services with API Gateway
- **🤖 AI Integration**: OpenAI-powered content generation and tutoring
- **📱 Multi-Channel Communication**: WhatsApp, SMS, Email, and Push notifications
- **🌐 Offline-First Design**: Works in low-connectivity environments
- **🔐 Enterprise Security**: JWT authentication, role-based access control
- **📊 Real-time Analytics**: Performance tracking and insights

## 🛠️ Technical Architecture

### **Backend Services**
- **API Gateway** (Port 8000) - Load balancing, rate limiting, authentication
- **Auth Service** (Port 8001) - User management, JWT tokens, RBAC
- **Content Quiz Service** (Port 8002) - Courses, lessons, quizzes, AI generation
- **Assistant Service** (Port 8003) - AI tutoring, content suggestions
- **Admin Service** (Port 8004) - School management, user administration
- **Sync Messaging Service** (Port 8005) - Real-time communication
- **File Storage Service** (Port 8006) - Document management, uploads
- **Notification Service** (Port 8007) - Multi-channel notifications
- **Super Admin Service** (Port 8008) - Platform-wide administration

### **Frontend**
- **Next.js 14** with App Router and TypeScript
- **Tailwind CSS** for responsive design
- **Real-time updates** via WebSocket
- **PWA capabilities** for offline access

### **Database & Infrastructure**
- **PostgreSQL** for relational data
- **Redis** for caching and session management
- **Docker** containerization for all services
- **Prometheus/Grafana** for monitoring

## 🚀 Key Features Implemented

### **Educational Core**
- ✅ Course and lesson management
- ✅ AI-powered quiz generation (WAEC format)
- ✅ Real-time progress tracking
- ✅ Personalized learning paths
- ✅ Bulk content import (CSV/Excel)

### **Communication System**
- ✅ WhatsApp integration for parent updates
- ✅ SMS notifications for important alerts
- ✅ Email system with templates
- ✅ Push notifications (Firebase)
- ✅ Real-time messaging

### **Administration**
- ✅ Multi-tenant school management
- ✅ Role-based user access (5 roles)
- ✅ Fee management and accounting
- ✅ Parent-teacher communication
- ✅ Analytics dashboard

### **AI & Automation**
- ✅ OpenAI integration for content generation
- ✅ Automated quiz creation
- ✅ Intelligent tutoring responses
- ✅ Performance analysis

## 🏃‍♂️ Quick Start

### **Prerequisites**
- Python 3.9+
- Node.js 18+
- PostgreSQL 15+
- Redis 7+
- Docker & Docker Compose

### **1. Clone & Setup**
```bash
git clone https://github.com/davidx345/education.git
cd education
cp .env.example .env
# Edit .env with your configuration
```

### **2. Start with Docker (Recommended)**
```bash
# Start all services
docker-compose up -d

# Check service health
curl http://localhost:8000/health
```

### **3. Manual Setup (Development)**
```bash
# Backend services
cd api-gateway
pip install -r requirements.txt
uvicorn app.main:app --port 8000 --reload

# Frontend
cd frontend
npm install
npm run dev
```

### **4. Database Setup**
```bash
# Run migrations
docker-compose exec auth-service alembic upgrade head
docker-compose exec content-quiz-service alembic upgrade head
```

## 📚 API Documentation

### **Authentication**
```bash
# Register a new school
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@school.com",
    "password": "secure123",
    "school_name": "Test School",
    "role": "admin"
  }'

# Login
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@school.com",
    "password": "secure123"
  }'
```

### **Course Management**
```bash
# Create a course
curl -X POST http://localhost:8000/courses \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Mathematics Grade 10",
    "description": "Comprehensive math curriculum",
    "grade_level": "SS1"
  }'
```

### **AI Quiz Generation**
```bash
# Generate WAEC-style quiz
curl -X POST http://localhost:8000/quizzes/generate \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "subject": "Mathematics",
    "topic": "Quadratic Equations",
    "difficulty": "intermediate",
    "question_count": 10
  }'
```

## 🧪 Testing

```bash
# Run backend tests
cd services/auth-service
pytest tests/ -v

# Run frontend tests
cd frontend
npm test

# Integration tests
cd tests
python -m pytest test_integration.py -v
```

## 🐳 Docker Deployment

### **Production Build**
```bash
# Build all services
docker-compose -f docker-compose.prod.yml build

# Deploy to production
docker-compose -f docker-compose.prod.yml up -d
```

### **Environment Variables**
Key environment variables (see `.env.example` for complete list):

| Variable | Description | Example |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection | `postgresql://user:pass@localhost:5432/edunerve` |
| `REDIS_URL` | Redis connection | `redis://localhost:6379/0` |
| `JWT_SECRET` | JWT signing key | `your-super-secret-key` |
| `OPENAI_API_KEY` | OpenAI API key | `sk-...` |
| `TERMII_API_KEY` | WhatsApp/SMS API | `TL...` |

## 📊 System Monitoring

- **Health Checks**: `GET /health` on each service
- **Metrics**: Prometheus metrics at `/metrics`
- **Logs**: Centralized logging with structured JSON
- **Performance**: Built-in APM and database query monitoring

## 🔒 Security Features

- ✅ JWT authentication with refresh tokens
- ✅ Role-based access control (5 user types)
- ✅ API rate limiting and circuit breakers
- ✅ Input validation and sanitization
- ✅ CORS protection
- ✅ Request/response logging
- ✅ Environment-based configuration

## 🌍 Multi-Language Support

- **English** (primary)
- **French** (West Africa)
- **Swahili** (East Africa)
- **Hausa, Yoruba, Igbo** (Nigeria)

## 📈 Performance & Scalability

- **Horizontal scaling** ready with stateless services
- **Database connection pooling** for high concurrency
- **Redis caching** for frequently accessed data
- **Async/await** patterns for non-blocking operations
- **Background job processing** with Celery

## 🚧 Current Status & Roadmap

### **✅ Completed**
- Complete microservices architecture
- User authentication and authorization
- Course and content management
- AI-powered quiz generation
- Multi-channel notifications
- Real-time messaging
- Analytics dashboard
- Docker deployment

### **🔄 In Progress**
- Mobile app development
- Advanced AI tutoring features
- Payment gateway integration
- Offline synchronization

### **📋 Planned**
- Video streaming capabilities
- Advanced analytics and ML
- Integration with government systems
- Multi-school district management

## 🤝 Contributing

This is a portfolio project showcasing enterprise-level backend development. Key architectural decisions:

- **Microservices** for scalability and maintainability
- **Domain-driven design** with clear service boundaries
- **Event-driven architecture** for loose coupling
- **API-first approach** with comprehensive documentation
- **Test-driven development** with high code coverage

## 📄 License

This project is for portfolio demonstration purposes. Educational use permitted.

## 📧 Contact

**David Ayodele** - Backend Engineer  
📧 Email: [your-email@domain.com]  
🔗 LinkedIn: [Your LinkedIn Profile]  
🐙 GitHub: [@davidx345](https://github.com/davidx345)

---

**Built with ❤️ for African Education**

*This project demonstrates production-ready backend architecture, microservices design, AI integration, and full-stack development capabilities.*