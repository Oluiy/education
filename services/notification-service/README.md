# EduNerve Notification Service

A comprehensive, AI-powered notification service for educational institutions supporting multiple communication channels including SMS, WhatsApp, Email, Push notifications, and Voice calls.

## 🚀 Features

### Core Notification Features
- **Multi-channel Support**: SMS, WhatsApp, Email, Push notifications, Voice calls
- **Multiple Providers**: Twilio, Africa's Talking, Infobip, Firebase, SMTP
- **Priority-based Delivery**: Emergency, Urgent, High, Normal, Low priority queues
- **Template System**: Create and manage notification templates with variables
- **Bulk Notifications**: Send to target audiences with advanced filtering
- **Scheduled Notifications**: Schedule notifications for future delivery
- **Real-time Status Tracking**: Monitor delivery status and analytics

### Advanced Features
- **Multi-tenant Architecture**: School-based isolation
- **Role-based Access Control**: Admin, Teacher, Student, Parent permissions
- **Notification Settings**: User preferences and quiet hours
- **Analytics Dashboard**: Delivery rates, costs, and performance metrics
- **Retry Logic**: Automatic retry for failed notifications
- **Queue Management**: Priority-based processing with background workers
- **Contact Management**: Verify and manage user contact information
- **Webhook Support**: Real-time delivery status updates

### AI-Powered Features
- **Smart Routing**: Choose optimal delivery channels
- **Content Optimization**: Improve message delivery rates
- **Predictive Analytics**: Forecast notification patterns
- **Auto-translation**: Multi-language support
- **Spam Detection**: Filter and prevent spam notifications

## 🏗️ Architecture

```
notification-service/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI application
│   ├── models.py               # Database models
│   ├── schemas.py              # Pydantic schemas
│   ├── database.py             # Database configuration
│   ├── auth.py                 # Authentication
│   ├── notification_service.py # Core business logic
│   ├── providers.py            # Notification providers
│   └── background_tasks.py     # Background processing
├── requirements.txt
├── .env
├── start.bat / start.sh
├── test_service.py
└── README.md
```

## 🛠️ Installation

### Prerequisites
- Python 3.8+
- SQLite or PostgreSQL
- Provider API keys (Twilio, Africa's Talking, etc.)

### Quick Start

1. **Clone and setup**:
```bash
git clone <repository>
cd notification-service
```

2. **Install dependencies**:
```bash
pip install -r requirements.txt
```

3. **Configure environment**:
```bash
cp .env.example .env
# Edit .env with your configuration
```

4. **Start the service**:
```bash
# Windows
start.bat

# Linux/Mac
chmod +x start.sh
./start.sh
```

The service will be available at:
- **API**: http://localhost:8006
- **Documentation**: http://localhost:8006/docs
- **Health Check**: http://localhost:8006/health

## 📋 Configuration

### Environment Variables

```env
# Database
DATABASE_URL=sqlite:///./notification.db
# DATABASE_URL=postgresql://user:pass@localhost/edunerve_notifications

# JWT Authentication
JWT_SECRET_KEY=your-secret-key-here
JWT_ALGORITHM=HS256

# SMS Providers
SMS_PROVIDER=twilio  # twilio, africastalking, infobip
TWILIO_ACCOUNT_SID=your-twilio-sid
TWILIO_AUTH_TOKEN=your-twilio-token
TWILIO_PHONE_NUMBER=+1234567890

# Africa's Talking
AFRICASTALKING_USERNAME=your-username
AFRICASTALKING_API_KEY=your-api-key
AFRICASTALKING_SENDER_ID=EduNerve

# Infobip
INFOBIP_BASE_URL=https://api.infobip.com
INFOBIP_API_KEY=your-infobip-key
INFOBIP_SENDER=EduNerve

# WhatsApp Providers
WHATSAPP_PROVIDER=twilio  # twilio, meta, infobip
WHATSAPP_PHONE_NUMBER=+1234567890

# Meta WhatsApp
META_WHATSAPP_ACCESS_TOKEN=your-meta-token
META_WHATSAPP_PHONE_NUMBER_ID=your-phone-id

# Email
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-password
SMTP_FROM_EMAIL=notifications@edunerve.com
SMTP_FROM_NAME=EduNerve

# Push Notifications
FIREBASE_CREDENTIALS_PATH=path/to/firebase-credentials.json
FIREBASE_PROJECT_ID=your-firebase-project

# Voice Calls
VOICE_PROVIDER=twilio
```

## 🔧 API Usage

### Authentication
All endpoints require JWT authentication:
```bash
curl -H "Authorization: Bearer YOUR_JWT_TOKEN" \
     -H "Content-Type: application/json" \
     http://localhost:8006/notifications
```

### Create Notification
```bash
curl -X POST http://localhost:8006/notifications \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "notification_type": "email",
    "subject": "Welcome to EduNerve",
    "message": "Welcome to our educational platform!",
    "priority": "normal",
    "recipients": [
      {
        "name": "John Doe",
        "email": "john@example.com",
        "recipient_type": "student"
      }
    ]
  }'
```

### Quick Notification
```bash
curl -X POST http://localhost:8006/notifications/quick \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "type": "sms",
    "recipients": ["+1234567890"],
    "message": "Class starts in 10 minutes!",
    "priority": "urgent"
  }'
```

### Bulk Notification
```bash
curl -X POST http://localhost:8006/notifications/bulk \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "type": "push",
    "subject": "School Announcement",
    "message": "Important school announcement for all students",
    "target_audience": {
      "all_students": true,
      "grade_levels": ["10", "11", "12"]
    },
    "priority": "high"
  }'
```

### Get Notification Status
```bash
curl -X GET http://localhost:8006/notifications/{notification_id} \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Create Template
```bash
curl -X POST http://localhost:8006/templates \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Assignment Reminder",
    "template_type": "email",
    "subject_template": "Assignment Due: {{assignment_name}}",
    "message_template": "Hello {{student_name}}, your assignment {{assignment_name}} is due on {{due_date}}.",
    "variables": ["student_name", "assignment_name", "due_date"]
  }'
```

## 📊 Analytics

### Get Analytics Summary
```bash
curl -X GET "http://localhost:8006/analytics/summary?days=30" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

Response:
```json
{
  "period": {
    "start_date": "2024-01-01",
    "end_date": "2024-01-30",
    "days": 30
  },
  "summary": {
    "total_sent": 1500,
    "total_delivered": 1425,
    "total_failed": 75,
    "delivery_rate": 95.0
  },
  "by_type": {
    "email": 800,
    "sms": 400,
    "whatsapp": 200,
    "push": 100
  },
  "daily_data": [...]
}
```

## 🔄 Background Processing

The service includes background workers for:

- **Queue Processing**: Process notifications by priority
- **Retry Logic**: Retry failed notifications
- **Scheduled Notifications**: Process scheduled notifications
- **Analytics Updates**: Update daily analytics
- **Cleanup**: Clean up old records

### Queue Management
```bash
# Check queue status (admin only)
curl -X GET http://localhost:8006/admin/queue-status \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN"

# Manually process queue
curl -X POST http://localhost:8006/admin/process-queue \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN"
```

## 🧪 Testing

### Run Test Suite
```bash
# Make sure service is running first
python test_service.py
```

### Test Individual Components
```bash
# Test notification creation
curl -X POST http://localhost:8006/notifications \
  -H "Authorization: Bearer test_token" \
  -d @test_notification.json

# Test health check
curl http://localhost:8006/health
```

## 🔐 Security

### Authentication
- JWT-based authentication
- Role-based access control
- School-based multi-tenancy

### Data Protection
- Input validation and sanitization
- Rate limiting
- SQL injection prevention
- XSS protection

### Privacy
- GDPR compliance features
- Data retention policies
- User consent management

## 📈 Performance

### Optimization Features
- Connection pooling
- Async processing
- Queue-based delivery
- Caching strategies
- Database indexing

### Scaling
- Horizontal scaling support
- Load balancing ready
- Database sharding support
- Microservices architecture

## 🛡️ Error Handling

### Provider Failover
- Automatic provider switching
- Retry with exponential backoff
- Dead letter queue for failed messages
- Error monitoring and alerting

### Monitoring
- Health checks
- Metrics collection
- Error tracking
- Performance monitoring

## 📚 API Documentation

### Interactive Documentation
Visit http://localhost:8006/docs for interactive API documentation with Swagger UI.

### Key Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Health check |
| `/notifications` | POST | Create notification |
| `/notifications/quick` | POST | Send quick notification |
| `/notifications/bulk` | POST | Send bulk notification |
| `/notifications/{id}` | GET | Get notification status |
| `/notifications` | GET | List notifications |
| `/templates` | POST | Create template |
| `/templates` | GET | List templates |
| `/analytics/summary` | GET | Get analytics |
| `/settings` | GET/PUT | Notification settings |

## 🔧 Troubleshooting

### Common Issues

1. **Service not starting**:
   - Check Python version (3.8+)
   - Verify dependencies installed
   - Check port availability

2. **Authentication failures**:
   - Verify JWT secret key
   - Check token format
   - Validate user permissions

3. **Provider errors**:
   - Check API credentials
   - Verify provider configuration
   - Check network connectivity

4. **Database issues**:
   - Check database connection
   - Verify table creation
   - Check permissions

### Debug Mode
```bash
# Enable debug logging
export LOG_LEVEL=DEBUG

# Run with debug
python -m uvicorn app.main:app --reload --log-level debug
```

## 🚀 Deployment

### Production Deployment
```bash
# Install production dependencies
pip install gunicorn

# Run with Gunicorn
gunicorn -w 4 -k uvicorn.workers.UvicornWorker app.main:app

# With Docker
docker build -t edunerve-notification-service .
docker run -p 8006:8006 edunerve-notification-service
```

### Environment Setup
- Set up production database
- Configure provider credentials
- Set up monitoring
- Configure backups

## 📞 Support

For technical support and questions:
- 📧 Email: support@edunerve.com
- 📖 Documentation: [docs.edunerve.com](https://docs.edunerve.com)
- 🐛 Issues: [GitHub Issues](https://github.com/edunerve/notification-service/issues)

## 📄 License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## 🤝 Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

---

**EduNerve Notification Service** - Empowering educational institutions with intelligent, reliable communication solutions. 🎓✨
