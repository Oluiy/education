#!/bin/bash

# EduNerve Heroku Deployment Script
# This script deploys all backend services to Heroku

set -e

echo "🚀 Starting EduNerve Heroku Deployment..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if Heroku CLI is installed
if ! command -v heroku &> /dev/null; then
    echo -e "${RED}❌ Heroku CLI not found. Please install it first:${NC}"
    echo "https://devcenter.heroku.com/articles/heroku-cli"
    exit 1
fi

# Check if logged in to Heroku
if ! heroku auth:whoami &> /dev/null; then
    echo -e "${RED}❌ Not logged in to Heroku. Please run:${NC}"
    echo "heroku login"
    exit 1
fi

# Configuration
APP_PREFIX="edunerve"
REGION="us"  # or eu for Europe

# Create Heroku apps
APPS=(
    "api-gateway"
    "auth-service"
    "content-quiz-service"
    "assistant-service"
    "admin-service"
    "sync-messaging-service"
    "file-storage-service"
    "notification-service"
)

echo -e "${YELLOW}📋 Creating Heroku apps...${NC}"

for app in "${APPS[@]}"; do
    app_name="${APP_PREFIX}-${app}"
    
    echo -e "${YELLOW}Creating ${app_name}...${NC}"
    
    # Create app if it doesn't exist
    if ! heroku apps:info --app "$app_name" &> /dev/null; then
        heroku create "$app_name" --region "$REGION"
        echo -e "${GREEN}✅ Created ${app_name}${NC}"
    else
        echo -e "${GREEN}✅ ${app_name} already exists${NC}"
    fi
done

# Add PostgreSQL to main services
echo -e "${YELLOW}🗄️ Adding PostgreSQL addon...${NC}"
heroku addons:create heroku-postgresql:hobby-dev --app "${APP_PREFIX}-api-gateway"

# Add Redis to services that need it
echo -e "${YELLOW}🔴 Adding Redis addon...${NC}"
heroku addons:create heroku-redis:hobby-dev --app "${APP_PREFIX}-api-gateway"
heroku addons:create heroku-redis:hobby-dev --app "${APP_PREFIX}-auth-service"
heroku addons:create heroku-redis:hobby-dev --app "${APP_PREFIX}-notification-service"

# Deploy each service
echo -e "${YELLOW}🚀 Deploying services...${NC}"

# API Gateway
echo -e "${YELLOW}Deploying API Gateway...${NC}"
cd api-gateway
git init
git add .
git commit -m "Initial deployment"
heroku git:remote -a "${APP_PREFIX}-api-gateway"
git push heroku main
cd ..

# Auth Service
echo -e "${YELLOW}Deploying Auth Service...${NC}"
cd services/auth-service
git init
git add .
git commit -m "Initial deployment"
heroku git:remote -a "${APP_PREFIX}-auth-service"
git push heroku main
cd ../..

# Content Quiz Service
echo -e "${YELLOW}Deploying Content Quiz Service...${NC}"
cd services/content-quiz-service
git init
git add .
git commit -m "Initial deployment"
heroku git:remote -a "${APP_PREFIX}-content-quiz-service"
git push heroku main
cd ../..

# Assistant Service
echo -e "${YELLOW}Deploying Assistant Service...${NC}"
cd services/assistant-service
git init
git add .
git commit -m "Initial deployment"
heroku git:remote -a "${APP_PREFIX}-assistant-service"
git push heroku main
cd ../..

# Admin Service
echo -e "${YELLOW}Deploying Admin Service...${NC}"
cd services/admin-service
git init
git add .
git commit -m "Initial deployment"
heroku git:remote -a "${APP_PREFIX}-admin-service"
git push heroku main
cd ../..

# Sync Messaging Service
echo -e "${YELLOW}Deploying Sync Messaging Service...${NC}"
cd services/sync-messaging-service
git init
git add .
git commit -m "Initial deployment"
heroku git:remote -a "${APP_PREFIX}-sync-messaging-service"
git push heroku main
cd ../..

# File Storage Service
echo -e "${YELLOW}Deploying File Storage Service...${NC}"
cd services/file-storage-service
git init
git add .
git commit -m "Initial deployment"
heroku git:remote -a "${APP_PREFIX}-file-storage-service"
git push heroku main
cd ../..

# Notification Service
echo -e "${YELLOW}Deploying Notification Service...${NC}"
cd services/notification-service
git init
git add .
git commit -m "Initial deployment"
heroku git:remote -a "${APP_PREFIX}-notification-service"
git push heroku main
cd ../..

# Configure environment variables
echo -e "${YELLOW}⚙️ Configuring environment variables...${NC}"

# Get database URL from main app
DATABASE_URL=$(heroku config:get DATABASE_URL --app "${APP_PREFIX}-api-gateway")
REDIS_URL=$(heroku config:get REDIS_URL --app "${APP_PREFIX}-api-gateway")

# Configure each service with the shared database
for app in "${APPS[@]}"; do
    app_name="${APP_PREFIX}-${app}"
    
    echo -e "${YELLOW}Configuring ${app_name}...${NC}"
    
    # Set common environment variables
    heroku config:set \
        DATABASE_URL="$DATABASE_URL" \
        REDIS_URL="$REDIS_URL" \
        ENVIRONMENT=production \
        DEBUG=false \
        --app "$app_name"
    
    # Set service-specific variables
    case $app in
        "api-gateway")
            heroku config:set \
                AUTH_SERVICE_URL="https://${APP_PREFIX}-auth-service.herokuapp.com" \
                CONTENT_SERVICE_URL="https://${APP_PREFIX}-content-quiz-service.herokuapp.com" \
                ASSISTANT_SERVICE_URL="https://${APP_PREFIX}-assistant-service.herokuapp.com" \
                ADMIN_SERVICE_URL="https://${APP_PREFIX}-admin-service.herokuapp.com" \
                SYNC_SERVICE_URL="https://${APP_PREFIX}-sync-messaging-service.herokuapp.com" \
                FILE_SERVICE_URL="https://${APP_PREFIX}-file-storage-service.herokuapp.com" \
                NOTIFICATION_SERVICE_URL="https://${APP_PREFIX}-notification-service.herokuapp.com" \
                --app "$app_name"
            ;;
        "notification-service")
            heroku config:set \
                TERMII_API_KEY="$TERMII_API_KEY" \
                TERMII_SENDER_ID="EduNerve" \
                --app "$app_name"
            ;;
        "content-quiz-service")
            heroku config:set \
                OPENAI_API_KEY="$OPENAI_API_KEY" \
                --app "$app_name"
            ;;
    esac
done

# Run database migrations
echo -e "${YELLOW}🗄️ Running database migrations...${NC}"
heroku run python -c "from app.database import create_tables; create_tables()" --app "${APP_PREFIX}-api-gateway"

# Health checks
echo -e "${YELLOW}🏥 Running health checks...${NC}"
for app in "${APPS[@]}"; do
    app_name="${APP_PREFIX}-${app}"
    url="https://${app_name}.herokuapp.com/health"
    
    echo -e "${YELLOW}Checking ${app_name}...${NC}"
    if curl -f "$url" > /dev/null 2>&1; then
        echo -e "${GREEN}✅ ${app_name} is healthy${NC}"
    else
        echo -e "${RED}❌ ${app_name} health check failed${NC}"
    fi
done

echo -e "${GREEN}🎉 Deployment complete!${NC}"
echo ""
echo -e "${YELLOW}📋 Next steps:${NC}"
echo "1. Configure your domain names"
echo "2. Set up SSL certificates"
echo "3. Configure monitoring (Sentry, New Relic)"
echo "4. Set up backup strategies"
echo "5. Test all integrations"
echo ""
echo -e "${YELLOW}🔗 Service URLs:${NC}"
for app in "${APPS[@]}"; do
    app_name="${APP_PREFIX}-${app}"
    echo "https://${app_name}.herokuapp.com"
done
