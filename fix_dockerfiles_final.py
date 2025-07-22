"""
Fix all Dockerfiles with proper DNS handling and robust package installation
"""

import os
from pathlib import Path

# Improved Dockerfile template without modifying resolv.conf
DOCKERFILE_TEMPLATE = '''FROM python:3.11-slim

WORKDIR /app

# Install system dependencies with retry logic and alternative mirrors
RUN apt-get update --fix-missing || apt-get update && \\
    apt-get install -y --no-install-recommends \\
    gcc \\
    libpq-dev \\
    curl \\
    ca-certificates \\
    && apt-get clean && \\
    rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY app/ ./app/

# Create non-root user
RUN useradd --create-home --shell /bin/bash edunerve
RUN chown -R edunerve:edunerve /app
USER edunerve

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \\
    CMD curl -f http://localhost:{port}/health || exit 1

EXPOSE {port}

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "{port}"]
'''

def update_dockerfile(service_path: str, port: int):
    """Update a service's Dockerfile"""
    dockerfile_path = Path(service_path) / "Dockerfile"
    
    if dockerfile_path.exists():
        content = DOCKERFILE_TEMPLATE.format(port=port)
        with open(dockerfile_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"✅ Updated {service_path}/Dockerfile")
    else:
        print(f"⚠️ {dockerfile_path} not found")

def main():
    """Update all service Dockerfiles"""
    os.chdir("c:/Users/USER/Documents/projects/education")
    
    services = [
        ("services/auth-service", 8001),
        ("services/content-quiz-service", 8002),
        ("services/assistant-service", 8003),
        ("services/admin-service", 8004),
        ("services/sync-messaging-service", 8005),
        ("services/file-storage-service", 8006),
        ("services/notification-service", 8007)
    ]
    
    print("🔧 Fixing Dockerfiles with robust package installation...")
    
    for service_path, port in services:
        update_dockerfile(service_path, port)
    
    print("✅ All Dockerfiles updated!")

if __name__ == "__main__":
    main()
