# 🎓 EduNerve - AI-Powered Educational Platform

> **A comprehensive Learning Management System designed for African secondary schools with offline-first capabilities and AI-powered features.**

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com)
[![Next.js](https://img.shields.io/badge/Next.js-14+-black.svg)](https://nextjs.org)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15+-blue.svg)](https://postgresql.org)
[![Redis](https://img.shields.io/badge/Redis-7+-red.svg)](https://redis.io)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)](https://docker.com)

##  Project Overview

EduNerve is a production-ready educational SaaS platform that addresses the unique challenges of African schools through:

- ** Microservices Architecture**: 9 independent services with API Gateway
- ** AI Integration**: OpenAI-powered content generation and tutoring
- ** Multi-Channel Communication**: WhatsApp, SMS, Email, and Push notifications
- ** Offline-First Design**: Works in low-connectivity environments
- ** Enterprise Security**: JWT authentication, role-based access control
- ** Real-time Analytics**: Performance tracking and insights

##  Technical Architecture

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

##  Key Features Implemented

### **Educational Core**
-  Course and lesson management
-  AI-powered quiz generation (WAEC format)
-  Real-time progress tracking
-  Personalized learning paths
-  Bulk content import (CSV/Excel)

### **Communication System**
-  WhatsApp integration for parent updates
-  SMS notifications for important alerts
-  Email system with templates
-  Push notifications (Firebase)
-  Real-time messaging

### **Administration**
-  Multi-tenant school management
-  Role-based user access (5 roles)
-  Fee management and accounting
-  Parent-teacher communication
-  Analytics dashboard

### **AI & Automation**
-  OpenAI integration for content generation
-  Automated quiz creation
-  Intelligent tutoring responses
-  Performance analysis

    System Monitoring

- **Health Checks**: `GET /health` on each service
- **Metrics**: Prometheus metrics at `/metrics`
- **Logs**: Centralized logging with structured JSON
- **Performance**: Built-in APM and database query monitoring

##  Security Features

-  JWT authentication with refresh tokens
-  Role-based access control (5 user types)
-  API rate limiting and circuit breakers
-  Input validation and sanitization
-  CORS protection
-  Request/response logging
-  Environment-based configuration

##  Performance & Scalability

- **Horizontal scaling** ready with stateless services
- **Database connection pooling** for high concurrency
- **Redis caching** for frequently accessed data
- **Async/await** patterns for non-blocking operations
- **Background job processing** with Celery

##  Current Status & Roadmap

### ** Completed**
- Complete microservices architecture
- User authentication and authorization
- Course and content management
- AI-powered quiz generation
- Multi-channel notifications
- Real-time messaging
- Analytics dashboard
- Docker deployment

### ** In Progress**
- Mobile app development
- Advanced AI tutoring features
- Payment gateway integration
- Offline synchronization

### ** Planned**
- Video streaming capabilities
- Advanced analytics and ML
- Integration with government systems
- Multi-school district management


##  Contact

**David Ayodele** - Backend Engineer  
 Email: [davidayo2603@gmail.com]  
 GitHub: [@davidx345](https://github.com/davidx345)

---