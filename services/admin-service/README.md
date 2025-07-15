# EduNerve Admin Service

## Overview
The Admin Service provides comprehensive school administration, user management, analytics, and system oversight capabilities for the EduNerve LMS platform.

## Features

### 🏫 School Management
- School creation and configuration
- Multi-school support for super admins
- School-specific settings and customization
- Performance tracking and analytics

### 👥 User Management
- Admin user creation and management
- Role-based access control (Super Admin, School Admin, Department Head)
- Permission management
- User activity tracking

### 📊 Analytics & Reporting
- School performance dashboards
- User engagement metrics
- Custom report generation
- Data export capabilities

### 🔒 Security & Audit
- Comprehensive audit logging
- System alerts and notifications
- Background task management
- Security monitoring

### 📂 Department Management
- Department creation and management
- Department head assignments
- Budget tracking
- Resource allocation

## Tech Stack
- **Framework**: FastAPI
- **Database**: PostgreSQL/SQLite
- **Authentication**: JWT tokens
- **File Storage**: Local filesystem
- **Background Tasks**: FastAPI BackgroundTasks

## Installation

### Prerequisites
- Python 3.8+
- PostgreSQL (optional, SQLite is default)

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
DATABASE_URL=sqlite:///./admin_service.db
# DATABASE_URL=postgresql://user:password@localhost/edunerve_admin

# JWT
JWT_SECRET_KEY=your-secret-key
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30

# Service URLs
AUTH_SERVICE_URL=http://localhost:8000
CONTENT_SERVICE_URL=http://localhost:8001
ASSISTANT_SERVICE_URL=http://localhost:8002
SYNC_SERVICE_URL=http://localhost:8004

# File Storage
MAX_FILE_SIZE=10485760  # 10MB
UPLOAD_DIR=uploads
REPORTS_DIR=reports

# Email (for notifications)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
```

## API Endpoints

### Dashboard
- `GET /api/v1/admin/dashboard` - Get dashboard statistics

### School Management
- `POST /api/v1/admin/schools` - Create school (Super Admin only)
- `GET /api/v1/admin/schools` - Get schools
- `GET /api/v1/admin/schools/{school_id}` - Get school details
- `PUT /api/v1/admin/schools/{school_id}` - Update school

### User Management
- `POST /api/v1/admin/users` - Create admin user
- `GET /api/v1/admin/users` - Get admin users
- `GET /api/v1/admin/users/{user_id}` - Get user details
- `PUT /api/v1/admin/users/{user_id}` - Update user
- `DELETE /api/v1/admin/users/{user_id}` - Delete user

### Department Management
- `POST /api/v1/admin/departments` - Create department
- `GET /api/v1/admin/departments` - Get departments
- `GET /api/v1/admin/departments/{dept_id}` - Get department details
- `PUT /api/v1/admin/departments/{dept_id}` - Update department
- `DELETE /api/v1/admin/departments/{dept_id}` - Delete department

### Analytics & Reporting
- `GET /api/v1/admin/analytics/school/{school_id}` - Get school analytics
- `GET /api/v1/admin/analytics/users` - Get user analytics
- `POST /api/v1/admin/reports` - Generate report
- `GET /api/v1/admin/reports` - Get reports
- `GET /api/v1/admin/reports/{report_id}/download` - Download report

### System Management
- `GET /api/v1/admin/audit-logs` - Get audit logs
- `GET /api/v1/admin/system-alerts` - Get system alerts
- `POST /api/v1/admin/system-alerts` - Create system alert
- `GET /api/v1/admin/system-config` - Get system configuration
- `PUT /api/v1/admin/system-config` - Update system configuration

## User Roles & Permissions

### Super Admin
- Full system access
- Can create/manage schools
- Can manage all users across schools
- System configuration access

### School Admin
- Full access to their school
- Can manage school users and departments
- Can view school analytics
- Can generate reports

### Department Head
- Access to their department
- Can manage department users
- Can view department analytics
- Limited reporting access

## Database Models

### AdminUser
- User ID, school ID, system role
- Permissions and departments
- Employee information
- Contact details

### School
- School information and settings
- Contact details and address
- Subscription and status
- Performance metrics

### Department
- Department details and budget
- Head user information
- Settings and configuration

### AuditLog
- User actions and changes
- Resource tracking
- Timestamps and IP addresses

## Testing

Run the test suite:
```bash
python test_service.py
```

## Security Features

### Authentication
- JWT-based authentication
- Role-based access control
- Permission-based authorization

### Audit Logging
- All admin actions logged
- IP address tracking
- Resource change tracking
- Searchable audit trail

### Data Protection
- Input validation
- SQL injection prevention
- XSS protection
- CSRF protection

## Multi-tenancy

The service supports multi-tenancy at the school level:
- Data isolation by school_id
- Role-based access control
- School-specific configurations
- Cross-school analytics (Super Admin only)

## Background Tasks

The service supports background tasks for:
- Report generation
- Data exports
- System maintenance
- Notification sending

## Integration

### Inter-Service Communication
- REST API communication
- JWT token forwarding
- Shared user context
- Error handling and retry logic

### External Services
- Email notifications
- File storage
- Analytics services
- Backup services

## Monitoring & Logging

### Health Checks
- `/health` endpoint
- Database connectivity
- Service dependencies

### Logging
- Structured logging
- Error tracking
- Performance monitoring
- Audit trail

## Deployment

### Docker
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8003"]
```

### Environment-specific Configuration
- Development: SQLite database
- Production: PostgreSQL database
- Staging: Reduced logging

## Contributing

1. Fork the repository
2. Create feature branch
3. Add tests for new features
4. Ensure all tests pass
5. Submit pull request

## License

This project is licensed under the MIT License.
