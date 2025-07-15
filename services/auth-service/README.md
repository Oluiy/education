# EduNerve Authentication Service

A multi-tenant, role-based authentication microservice for the EduNerve LMS platform, designed specifically for African secondary schools.

## 🚀 Features

- **Multi-tenant Architecture**: Each school is isolated with school-based data separation
- **Role-based Access Control**: Students, Teachers, Admins with appropriate permissions
- **JWT Authentication**: Secure token-based authentication
- **Offline-first Ready**: SQLite support for offline deployment
- **Production Ready**: PostgreSQL support for scalable deployment
- **WAEC-focused**: Designed for West African educational systems
- **Password Security**: Bcrypt hashing with strength validation
- **Email/Phone Validation**: Built-in validation for African phone numbers

## 🏗️ Architecture

```
EduNerve Auth Service
├── Multi-tenant (School-based isolation)
├── Role-based Access (Student/Teacher/Admin)
├── JWT Token Authentication
├── SQLite (Development) / PostgreSQL (Production)
└── FastAPI + SQLAlchemy + Pydantic
```

## 📦 Installation

1. **Clone and navigate to the project:**
   ```bash
   cd auth-service
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
   uvicorn app.main:app --reload
   ```

## 🔧 Configuration

### Environment Variables

```env
# Security
SECRET_KEY=your-super-secret-key-change-this-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440

# Database
DATABASE_URL=sqlite:///./edunerve_auth.db
# For PostgreSQL: postgresql://user:password@localhost/edunerve_auth

# Optional: Future integrations
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
TWILIO_ACCOUNT_SID=your-twilio-sid
TERMII_API_KEY=your-termii-key
```

## 🛣️ API Endpoints

### Authentication
- `POST /api/v1/auth/register` - Register new user
- `POST /api/v1/auth/login` - Login and get JWT token
- `GET /api/v1/auth/me` - Get current user profile
- `PUT /api/v1/auth/me` - Update current user profile

### User Management
- `GET /api/v1/auth/users` - List users (Teachers/Admins)
- `GET /api/v1/auth/users/{user_id}` - Get specific user
- `GET /api/v1/auth/students` - List students (Teachers/Admins)
- `GET /api/v1/auth/teachers` - List teachers (Admins only)
- `DELETE /api/v1/auth/users/{user_id}` - Deactivate user (Admins only)

### School Management
- `POST /api/v1/auth/schools` - Create new school
- `GET /api/v1/auth/schools` - List all schools
- `GET /api/v1/auth/schools/{school_id}` - Get specific school

### System
- `GET /api/v1/auth/health` - Health check
- `GET /api/v1/auth/stats` - School statistics (Admins only)
- `GET /` - Service information

## 📊 Database Schema

### Schools Table
- `id` - Primary key
- `name` - School name
- `code` - Unique school identifier
- `address`, `phone`, `email` - Contact information
- `principal_name` - Principal's name
- `is_active` - School status
- `max_students`, `max_teachers` - Capacity limits

### Users Table
- `id` - Primary key
- `email` - Unique email address
- `phone` - Phone number (African format supported)
- `hashed_password` - Bcrypt hashed password
- `first_name`, `last_name`, `middle_name` - Personal info
- `role` - STUDENT, TEACHER, ADMIN, PARENT
- `school_id` - Foreign key to schools table
- `class_level` - JSS1-3, SS1-3 (for students)
- `student_id`, `employee_id` - School-specific IDs
- `subjects` - JSON string of subjects (for teachers)
- `is_active`, `is_verified` - Account status
- `email_verified`, `phone_verified` - Verification status

## 🧪 Testing

### Quick Test with curl

1. **Create a school:**
   ```bash
   curl -X POST "http://localhost:8000/api/v1/auth/schools" \
     -H "Content-Type: application/json" \
     -d '{
       "name": "Lagos State Model College",
       "code": "LSMC001",
       "address": "Lagos, Nigeria",
       "phone": "+2348123456789",
       "email": "info@lsmc.edu.ng",
       "principal_name": "Dr. Adebayo Johnson"
     }'
   ```

2. **Register a user:**
   ```bash
   curl -X POST "http://localhost:8000/api/v1/auth/register" \
     -H "Content-Type: application/json" \
     -d '{
       "email": "student@example.com",
       "password": "SecurePass123",
       "first_name": "John",
       "last_name": "Doe",
       "role": "student",
       "school_id": 1,
       "class_level": "SS2"
     }'
   ```

3. **Login:**
   ```bash
   curl -X POST "http://localhost:8000/api/v1/auth/login" \
     -H "Content-Type: application/json" \
     -d '{
       "email": "student@example.com",
       "password": "SecurePass123"
     }'
   ```

## 🔐 Security Features

- **Password Requirements**: Minimum 8 characters, uppercase, lowercase, numbers
- **JWT Tokens**: Secure token-based authentication
- **Role-based Access**: Endpoint protection based on user roles
- **School Isolation**: Users can only access data from their own school
- **Bcrypt Hashing**: Strong password hashing
- **Input Validation**: Pydantic schemas for request validation

## 🌍 African-Specific Features

- **Nigerian Phone Numbers**: Automatic +234 formatting
- **WAEC Class Levels**: JSS1-3, SS1-3 validation
- **Multi-tenant Schools**: Each school is completely isolated
- **Offline-first**: SQLite support for low-connectivity areas
- **Lightweight**: Designed for shared Android devices

## 🚀 Production Deployment

### PostgreSQL Setup
```bash
# Update .env
DATABASE_URL=postgresql://user:password@localhost/edunerve_auth

# Install PostgreSQL driver
pip install psycopg2-binary
```

### Docker Deployment
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## 📈 Future Enhancements

- Email verification with SMTP
- SMS verification with Termii/Twilio
- Password reset functionality
- Rate limiting and security middleware
- Audit logging
- Multi-language support
- WhatsApp integration for parent notifications

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 📞 Support

For support, email: support@edunerve.com

---

**Built with ❤️ for African Education**
