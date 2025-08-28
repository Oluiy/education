#!/bin/bash

# EduNerve Vercel Frontend Deployment Script

set -e

echo "🚀 Starting EduNerve Vercel Frontend Deployment..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if Vercel CLI is installed
if ! command -v vercel &> /dev/null; then
    echo -e "${RED}❌ Vercel CLI not found. Please install it first:${NC}"
    echo "npm i -g vercel"
    exit 1
fi

# Check if logged in to Vercel
if ! vercel whoami &> /dev/null; then
    echo -e "${RED}❌ Not logged in to Vercel. Please run:${NC}"
    echo "vercel login"
    exit 1
fi

# Navigate to frontend directory
cd frontend

echo -e "${YELLOW}📦 Installing dependencies...${NC}"
npm install

echo -e "${YELLOW}🏗️ Building the application...${NC}"
npm run build

echo -e "${YELLOW}🚀 Deploying to Vercel...${NC}"

# Deploy to Vercel
vercel --prod

echo -e "${GREEN}🎉 Frontend deployment complete!${NC}"
echo ""
echo -e "${YELLOW}📋 Next steps:${NC}"
echo "1. Configure custom domain in Vercel dashboard"
echo "2. Set up environment variables in Vercel"
echo "3. Configure API gateway URL"
echo "4. Test all integrations"
echo "5. Set up monitoring and analytics"
