# 🚀 EduNerve MVP Production Deployment Guide

## 🎯 Overview

This guide provides step-by-step instructions for deploying the EduNerve MVP backend to production environments including local, cloud, and containerized deployments.

## 📋 Pre-Deployment Checklist

### ✅ **Infrastructure Requirements**
- [ ] PostgreSQL 13+ database server
- [ ] Redis 6+ server (for caching and rate limiting)
- [ ] Python 3.8+ runtime environment
- [ ] SSL certificates for HTTPS
- [ ] Termii API account for WhatsApp integration
- [ ] SMTP server for email notifications

### ✅ **Environment Configuration**
- [ ] Database credentials configured
- [ ] Secret keys generated (unique for production)
- [ ] External API keys (Termii, SMTP) configured
- [ ] Service URLs updated for production
- [ ] CORS origins configured for frontend domains

## 🛠️ Deployment Options

### Option 1: Local Development Setup

```bash
# 1. Clone and navigate to project
git clone <repository-url>
cd education

# 2. Run enhancement script
python enhance_services.py

# 3. Configure environment
cp services/auth-service/.env.example services/auth-service/.env
# Edit .env files with your configurations

# 4. Start all services
chmod +x start_services.sh
./start_services.sh start

# 5. Verify deployment
./start_services.sh status
python integration_test.py
```

### Option 2: Docker Deployment

```bash
# 1. Build and start with Docker Compose
docker-compose up -d

# 2. Verify services
docker-compose ps
docker-compose logs

# 3. Run integration tests
docker-compose exec super-admin-service python /app/integration_test.py
```

### Option 3: Cloud Deployment (Heroku)

Each service includes Heroku-ready configuration:

```bash
# 1. Create Heroku apps for each service
heroku create edunerve-auth-service
heroku create edunerve-admin-service
heroku create edunerve-notification-service
heroku create edunerve-super-admin-service

# 2. Add PostgreSQL and Redis addons
heroku addons:create heroku-postgresql:hobby-dev -a edunerve-auth-service
heroku addons:create heroku-redis:hobby-dev -a edunerve-notification-service

# 3. Configure environment variables
heroku config:set DATABASE_URL=<postgresql-url> -a edunerve-auth-service
heroku config:set TERMII_API_KEY=<your-key> -a edunerve-notification-service

# 4. Deploy each service
cd services/auth-service
git init && git add . && git commit -m "Initial commit"
heroku git:remote -a edunerve-auth-service
git push heroku main

# Repeat for other services
```

### Option 4: Kubernetes Deployment

```yaml
# kubernetes/namespace.yaml
apiVersion: v1
kind: Namespace
metadata:
  name: edunerve

---
# kubernetes/configmap.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: edunerve-config
  namespace: edunerve
data:
  DATABASE_URL: "postgresql://user:pass@postgres:5432/edunerve_db"
  REDIS_URL: "redis://redis:6379/0"

---
# kubernetes/auth-service.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: auth-service
  namespace: edunerve
spec:
  replicas: 3
  selector:
    matchLabels:
      app: auth-service
  template:
    metadata:
      labels:
        app: auth-service
    spec:
      containers:
      - name: auth-service
        image: edunerve/auth-service:latest
        ports:
        - containerPort: 8001
        envFrom:
        - configMapRef:
            name: edunerve-config
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"

---
apiVersion: v1
kind: Service
metadata:
  name: auth-service
  namespace: edunerve
spec:
  selector:
    app: auth-service
  ports:
  - port: 8001
    targetPort: 8001
  type: ClusterIP
```

Deploy with:
```bash
kubectl apply -f kubernetes/
kubectl get pods -n edunerve
```

## 🔧 Environment Configuration

### Production Environment Variables

Create production `.env` files for each service:

```env
# Production Database
DATABASE_URL=postgresql://edunerve_prod:secure_password@db.example.com:5432/edunerve_prod

# Security (Generate unique keys!)
SECRET_KEY=prod-secret-key-64-chars-minimum-change-this-immediately
JWT_SECRET_KEY=prod-jwt-secret-key-64-chars-minimum-change-this-too

# Service URLs (Update for production)
AUTH_SERVICE_URL=https://auth.edunerve.com
ADMIN_SERVICE_URL=https://admin.edunerve.com
NOTIFICATION_SERVICE_URL=https://notifications.edunerve.com
SUPER_ADMIN_SERVICE_URL=https://superadmin.edunerve.com

# External APIs
TERMII_API_KEY=your_production_termii_api_key
WHATSAPP_SENDER_ID=EduNerve

# Email Configuration
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=noreply@edunerve.com
SMTP_PASSWORD=your_app_specific_password

# Production Settings
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=INFO

# CORS (Update with your frontend domains)
ALLOWED_ORIGINS=https://app.edunerve.com,https://admin.edunerve.com
```

### Database Setup

```sql
-- Create production database
CREATE DATABASE edunerve_prod;

-- Create dedicated user
CREATE USER edunerve_prod WITH PASSWORD 'very_secure_password_here';

-- Grant permissions
GRANT ALL PRIVILEGES ON DATABASE edunerve_prod TO edunerve_prod;

-- Connect and create extensions
\c edunerve_prod;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
```

## 🔒 Security Configuration

### SSL/TLS Setup (Nginx)

```nginx
server {
    listen 80;
    server_name api.edunerve.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name api.edunerve.com;
    
    ssl_certificate /etc/ssl/certs/edunerve.com.crt;
    ssl_certificate_key /etc/ssl/private/edunerve.com.key;
    
    # Modern SSL configuration
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512;
    ssl_prefer_server_ciphers off;
    
    # Security headers
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";
    add_header Strict-Transport-Security "max-age=63072000; includeSubDomains; preload";
    
    # Route to services
    location /auth/ {
        proxy_pass http://localhost:8001/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    location /admin/ {
        proxy_pass http://localhost:8002/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
    
    location /notifications/ {
        proxy_pass http://localhost:8003/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
    
    location /super-admin/ {
        proxy_pass http://localhost:8009/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### Firewall Configuration

```bash
# Allow only necessary ports
ufw default deny incoming
ufw default allow outgoing
ufw allow ssh
ufw allow 80
ufw allow 443
ufw allow from 10.0.0.0/8 to any port 5432  # Database access only from internal network
ufw enable
```

## 📊 Monitoring & Logging

### Application Monitoring

```yaml
# docker-compose.monitoring.yml
version: '3.8'

services:
  prometheus:
    image: prom/prometheus
    ports:
      - "9090:9090"
    volumes:
      - ./monitoring/prometheus.yml:/etc/prometheus/prometheus.yml

  grafana:
    image: grafana/grafana
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
    volumes:
      - grafana_data:/var/lib/grafana

volumes:
  grafana_data:
```

### Log Management

```bash
# Set up log rotation
cat > /etc/logrotate.d/edunerve << EOF
/var/log/edunerve/*.log {
    daily
    missingok
    rotate 30
    compress
    notifempty
    create 0644 www-data www-data
    sharedscripts
    postrotate
        systemctl reload nginx
    endscript
}
EOF
```

## 🔄 Backup Strategy

### Database Backup

```bash
#!/bin/bash
# backup_db.sh

BACKUP_DIR="/backups/edunerve"
DATE=$(date +%Y%m%d_%H%M%S)
DB_NAME="edunerve_prod"

# Create backup directory
mkdir -p $BACKUP_DIR

# Create backup
pg_dump $DB_NAME > $BACKUP_DIR/edunerve_backup_$DATE.sql

# Compress backup
gzip $BACKUP_DIR/edunerve_backup_$DATE.sql

# Remove backups older than 30 days
find $BACKUP_DIR -name "*.sql.gz" -mtime +30 -delete

echo "Backup completed: edunerve_backup_$DATE.sql.gz"
```

```bash
# Add to crontab for daily backups at 2 AM
crontab -e
0 2 * * * /usr/local/bin/backup_db.sh
```

## 🚀 Deployment Automation

### CI/CD Pipeline (GitHub Actions)

```yaml
# .github/workflows/deploy.yml
name: Deploy EduNerve Backend

on:
  push:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r services/auth-service/requirements.txt
    
    - name: Run tests
      run: |
        python -m pytest services/super-admin-service/tests/

  deploy:
    needs: test
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Deploy to production
      run: |
        # Your deployment script here
        echo "Deploying to production..."
```

## 📈 Performance Optimization

### Database Optimization

```sql
-- Create indexes for performance
CREATE INDEX idx_users_school_id ON users(school_id);
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_auth_sessions_token ON auth_sessions(token);
CREATE INDEX idx_notification_logs_phone ON notification_logs(phone_number);

-- Analyze tables
ANALYZE users;
ANALYZE auth_sessions;
ANALYZE notification_logs;
```

### Redis Configuration

```conf
# redis.conf optimizations
maxmemory 256mb
maxmemory-policy allkeys-lru
save 900 1
save 300 10
save 60 10000
```

## 🆘 Troubleshooting

### Common Issues

1. **Service won't start**
   ```bash
   # Check logs
   ./start_services.sh logs
   
   # Check port availability
   netstat -tulpn | grep :8001
   ```

2. **Database connection errors**
   ```bash
   # Test database connection
   psql -h localhost -U edunerve_user -d edunerve_db
   
   # Check connection pool
   SELECT * FROM pg_stat_activity WHERE datname = 'edunerve_db';
   ```

3. **WhatsApp notifications not sending**
   ```bash
   # Verify Termii API key
   curl -X GET "https://api.ng.termii.com/api/get-balance?api_key=YOUR_API_KEY"
   
   # Check notification logs
   SELECT * FROM notification_logs WHERE status = 'failed' ORDER BY created_at DESC LIMIT 10;
   ```

### Health Checks

```bash
# Check all services
curl http://localhost:8001/health  # Auth Service
curl http://localhost:8002/health  # Admin Service
curl http://localhost:8003/health  # Notification Service
curl http://localhost:8009/health  # Super Admin Service

# Database health
SELECT 1;

# Redis health
redis-cli ping
```

## 📞 Production Support

### Monitoring Alerts

Set up alerts for:
- Service downtime (health check failures)
- High error rates (>5% in 5 minutes)
- Database connection issues
- High response times (>2 seconds)
- Failed notification deliveries

### Performance Metrics

Monitor these key metrics:
- Request latency (p95 < 500ms)
- Error rate (< 1%)
- Database connections (< 80% of pool)
- Memory usage (< 80%)
- CPU usage (< 70%)

---

## 🎉 Deployment Complete!

Your EduNerve MVP backend is now production-ready with:

✅ **Multi-tenant architecture** with complete data isolation  
✅ **Comprehensive security** with JWT auth, rate limiting, CORS  
✅ **Scalable infrastructure** ready for horizontal scaling  
✅ **Monitoring & logging** for production observability  
✅ **Backup & recovery** strategies implemented  
✅ **CI/CD pipeline** for automated deployments  

**Your educational SaaS platform is ready to serve schools and students!** 🎓
