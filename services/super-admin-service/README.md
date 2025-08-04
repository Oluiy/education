# EduNerve Super Admin Service

The Super Admin Service provides centralized management capabilities for the EduNerve educational platform.

## Features

- **School Management**: Create, update, suspend, and activate schools
- **Platform Analytics**: Monitor platform statistics and revenue metrics
- **Multi-tenant Support**: Isolated data management across schools
- **Admin Management**: Manage school administrators and permissions

## API Endpoints

### School Management
- `POST /schools` - Create new school with primary admin
- `GET /schools` - List schools with pagination and filtering
- `GET /schools/{id}` - Get school details
- `PUT /schools/{id}` - Update school information
- `PATCH /schools/{id}/suspend` - Suspend school
- `PATCH /schools/{id}/activate` - Activate school

### Analytics
- `GET /analytics/platform` - Platform statistics
- `GET /analytics/revenue` - Revenue analytics
- `GET /analytics/current` - Current platform metrics

### Administration
- `GET /schools/{id}/admins` - List school administrators
- `PATCH /schools/{id}/user-counts` - Update user counts

## Environment Variables

```env
DATABASE_URL=postgresql://user:password@localhost/edunerve_db
ENVIRONMENT=development
DEBUG=true
SERVICE_PORT=8009
SECRET_KEY=your-secret-key-here
AUTH_SERVICE_URL=http://localhost:8001
ADMIN_SERVICE_URL=http://localhost:8002
NOTIFICATION_SERVICE_URL=http://localhost:8003
```

## Installation

```bash
cd services/super-admin-service
pip install -r requirements.txt
python run.py
```

## API Documentation

Once running, visit:
- Swagger UI: http://localhost:8009/docs
- ReDoc: http://localhost:8009/redoc
