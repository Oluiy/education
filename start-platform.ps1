# EduNerve Platform - Complete Startup Script (PowerShell)
# This script builds and starts all services with proper initialization

# Set error handling
$ErrorActionPreference = "Stop"

Write-Host "🚀 Starting EduNerve Educational Platform..." -ForegroundColor Blue
Write-Host "================================================" -ForegroundColor Blue

# Function to print colored output
function Write-Status {
    param($Message)
    Write-Host "[INFO] $Message" -ForegroundColor Cyan
}

function Write-Success {
    param($Message)
    Write-Host "[SUCCESS] $Message" -ForegroundColor Green
}

function Write-Warning {
    param($Message)
    Write-Host "[WARNING] $Message" -ForegroundColor Yellow
}

function Write-Error {
    param($Message)
    Write-Host "[ERROR] $Message" -ForegroundColor Red
}

# Check if Docker is running
try {
    docker info | Out-Null
    Write-Status "Docker is running"
} catch {
    Write-Error "Docker is not running. Please start Docker Desktop and try again."
    exit 1
}

# Check if Docker Compose is available
try {
    docker-compose version | Out-Null
    Write-Status "Docker Compose is available"
} catch {
    try {
        docker compose version | Out-Null
        Write-Status "Docker Compose (v2) is available"
        $dockerComposeCmd = "docker compose"
    } catch {
        Write-Error "Docker Compose is not available. Please install Docker Compose."
        exit 1
    }
}

if (-not $dockerComposeCmd) {
    $dockerComposeCmd = "docker-compose"
}

# Clean up any existing containers
Write-Status "Cleaning up existing containers..."
try {
    Invoke-Expression "$dockerComposeCmd down -v --remove-orphans" | Out-Null
} catch {
    # Ignore errors if no containers exist
}

# Remove any dangling images
Write-Status "Cleaning up dangling images..."
docker image prune -f | Out-Null

# Build all services
Write-Status "Building all services..."
Invoke-Expression "$dockerComposeCmd build --no-cache"

# Start infrastructure services first
Write-Status "Starting infrastructure services (PostgreSQL, Redis)..."
Invoke-Expression "$dockerComposeCmd up -d postgres redis"

# Wait for PostgreSQL to be ready
Write-Status "Waiting for PostgreSQL to be ready..."
$postgresReady = $false
$attempts = 0
while (-not $postgresReady -and $attempts -lt 30) {
    try {
        Invoke-Expression "$dockerComposeCmd exec postgres pg_isready -U edunerve -d edunerve" | Out-Null
        $postgresReady = $true
        Write-Success "PostgreSQL is ready"
    } catch {
        Write-Host "PostgreSQL is not ready yet. Waiting..." -ForegroundColor Gray
        Start-Sleep -Seconds 2
        $attempts++
    }
}

if (-not $postgresReady) {
    Write-Error "PostgreSQL failed to start within 60 seconds"
    exit 1
}

# Wait for Redis to be ready
Write-Status "Waiting for Redis to be ready..."
$redisReady = $false
$attempts = 0
while (-not $redisReady -and $attempts -lt 30) {
    try {
        $result = Invoke-Expression "$dockerComposeCmd exec redis redis-cli ping"
        if ($result -match "PONG") {
            $redisReady = $true
            Write-Success "Redis is ready"
        }
    } catch {
        Write-Host "Redis is not ready yet. Waiting..." -ForegroundColor Gray
        Start-Sleep -Seconds 2
        $attempts++
    }
}

if (-not $redisReady) {
    Write-Error "Redis failed to start within 60 seconds"
    exit 1
}

# Start backend services
Write-Status "Starting backend services..."
Invoke-Expression "$dockerComposeCmd up -d auth-service content-quiz-service file-storage-service sync-messaging-service assistant-service admin-service notification-service"

# Wait for services to be healthy
Write-Status "Waiting for backend services to be ready..."
Start-Sleep -Seconds 10

# Start API Gateway
Write-Status "Starting API Gateway..."
Invoke-Expression "$dockerComposeCmd up -d api-gateway"

# Wait for API Gateway to be ready
Write-Status "Waiting for API Gateway to be ready..."
$gatewayReady = $false
$attempts = 0
while (-not $gatewayReady -and $attempts -lt 30) {
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:8000/health" -UseBasicParsing -TimeoutSec 2
        if ($response.StatusCode -eq 200) {
            $gatewayReady = $true
            Write-Success "API Gateway is ready"
        }
    } catch {
        Write-Host "API Gateway is not ready yet. Waiting..." -ForegroundColor Gray
        Start-Sleep -Seconds 2
        $attempts++
    }
}

if (-not $gatewayReady) {
    Write-Error "API Gateway failed to start within 60 seconds"
    exit 1
}

# Setup frontend
Write-Status "Setting up frontend..."
Set-Location -Path "frontend"

# Check if Node.js is installed
try {
    node --version | Out-Null
    Write-Status "Node.js is available"
} catch {
    Write-Error "Node.js is not installed. Please install Node.js and npm from https://nodejs.org/"
    exit 1
}

# Install dependencies
Write-Status "Installing frontend dependencies..."
npm install

# Build the frontend
Write-Status "Building frontend application..."
npm run build

# Start the frontend in development mode
Write-Status "Starting frontend development server..."
$frontendJob = Start-Job -ScriptBlock { 
    Set-Location -Path $args[0]
    npm run dev 
} -ArgumentList (Get-Location).Path

# Go back to root directory
Set-Location -Path ".."

# Display service status
Write-Host ""
Write-Host "🎉 EduNerve Platform is now running!" -ForegroundColor Green
Write-Host "================================================" -ForegroundColor Green
Write-Host ""
Write-Host "📊 Service Status:" -ForegroundColor Cyan
Write-Host "✅ PostgreSQL Database: localhost:5432" -ForegroundColor Green
Write-Host "✅ Redis Cache: localhost:6379" -ForegroundColor Green
Write-Host "✅ API Gateway: http://localhost:8000" -ForegroundColor Green
Write-Host "✅ Frontend Application: http://localhost:3000" -ForegroundColor Green
Write-Host ""
Write-Host "🔧 Backend Services:" -ForegroundColor Cyan
Write-Host "  • Auth Service: Port 8001" -ForegroundColor White
Write-Host "  • Content & Quiz Service: Port 8002" -ForegroundColor White
Write-Host "  • File Storage Service: Port 8003" -ForegroundColor White
Write-Host "  • Sync & Messaging Service: Port 8004" -ForegroundColor White
Write-Host "  • AI Assistant Service: Port 8005" -ForegroundColor White
Write-Host "  • Admin Service: Port 8006" -ForegroundColor White
Write-Host "  • Notification Service: Port 8007" -ForegroundColor White
Write-Host ""
Write-Host "📱 Frontend Features Available:" -ForegroundColor Cyan
Write-Host "  • Course Management: http://localhost:3000/dashboard/courses" -ForegroundColor White
Write-Host "  • Quiz System: http://localhost:3000/dashboard/quizzes" -ForegroundColor White
Write-Host "  • Real-time Messaging: http://localhost:3000/dashboard/messages" -ForegroundColor White
Write-Host "  • File Management: http://localhost:3000/dashboard/files" -ForegroundColor White
Write-Host "  • Analytics Dashboard: http://localhost:3000/dashboard/analytics" -ForegroundColor White
Write-Host ""
Write-Host "🔗 API Documentation:" -ForegroundColor Cyan
Write-Host "  • API Gateway: http://localhost:8000/docs" -ForegroundColor White
Write-Host "  • Direct service docs available on individual service ports" -ForegroundColor White
Write-Host ""
Write-Host "💾 Database Access:" -ForegroundColor Cyan
Write-Host "  • Host: localhost" -ForegroundColor White
Write-Host "  • Port: 5432" -ForegroundColor White
Write-Host "  • Database: edunerve" -ForegroundColor White
Write-Host "  • Username: edunerve" -ForegroundColor White
Write-Host "  • Password: edunerve2024" -ForegroundColor White
Write-Host ""
Write-Host "🛑 To stop all services:" -ForegroundColor Cyan
Write-Host "  docker-compose down" -ForegroundColor White
Write-Host "  Stop-Job -Job $($frontendJob.Id)  # Stop frontend dev server" -ForegroundColor White
Write-Host ""

# Health check all services
Write-Status "Performing health checks..."
Write-Host ""

# Check API Gateway
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8000/health" -UseBasicParsing -TimeoutSec 5
    if ($response.StatusCode -eq 200) {
        Write-Success "API Gateway: Healthy"
    }
} catch {
    Write-Warning "API Gateway: Not responding"
}

# Check frontend (may take a moment to start)
Start-Sleep -Seconds 5
try {
    $response = Invoke-WebRequest -Uri "http://localhost:3000" -UseBasicParsing -TimeoutSec 5
    if ($response.StatusCode -eq 200) {
        Write-Success "Frontend: Healthy"
    }
} catch {
    Write-Warning "Frontend: Not ready yet (may still be starting)"
}

# Check individual services through API Gateway
$services = @("auth", "content", "files", "sync", "assistant", "admin", "notifications")
foreach ($service in $services) {
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:8000/api/v1/$service/health" -UseBasicParsing -TimeoutSec 5
        if ($response.StatusCode -eq 200) {
            Write-Success "$service service: Healthy"
        }
    } catch {
        Write-Warning "$service service: Not responding"
    }
}

Write-Host ""
Write-Success "Platform startup complete!"
Write-Host ""
Write-Host "📖 Next Steps:" -ForegroundColor Cyan
Write-Host "1. Open http://localhost:3000 in your browser" -ForegroundColor White
Write-Host "2. Create an admin account or use test credentials" -ForegroundColor White
Write-Host "3. Start creating courses and content" -ForegroundColor White
Write-Host "4. Invite students and teachers" -ForegroundColor White
Write-Host ""
Write-Host "📚 Documentation and API testing:" -ForegroundColor Cyan
Write-Host "• Visit http://localhost:8000/docs for API documentation" -ForegroundColor White
Write-Host "• Use the frontend interface for user-friendly interaction" -ForegroundColor White
Write-Host ""
Write-Host "🎯 Key Features to Test:" -ForegroundColor Cyan
Write-Host "• Create and manage courses" -ForegroundColor White
Write-Host "• Upload and organize course materials" -ForegroundColor White
Write-Host "• Generate AI-powered quizzes" -ForegroundColor White
Write-Host "• Real-time messaging and collaboration" -ForegroundColor White
Write-Host "• Progress tracking and analytics" -ForegroundColor White
Write-Host ""

# Keep script running to show logs
Write-Status "Monitoring service logs (Ctrl+C to stop)..."
try {
    Invoke-Expression "$dockerComposeCmd logs -f"
} catch {
    Write-Host "Log monitoring stopped." -ForegroundColor Yellow
} finally {
    # Clean up frontend job when script exits
    if ($frontendJob) {
        Stop-Job -Job $frontendJob
        Remove-Job -Job $frontendJob
    }
}
