#!/usr/bin/env python3
"""
Script to fix encoding issues in requirements.txt files and ensure all services have proper dependencies
"""
import os

# Base requirements that all services need
BASE_REQUIREMENTS = [
    "aiofiles==24.1.0",
    "aiosmtplib==4.0.1", 
    "alembic==1.14.0",
    "annotated-types==0.7.0",
    "anyio==3.7.1",
    "bcrypt==4.2.1",
    "bleach==6.1.0",
    "certifi==2025.6.15",
    "cffi==1.17.1",
    "charset-normalizer==3.4.2",
    "click==8.2.1",
    "colorama==0.4.6",
    "cryptography==44.0.0",
    "dnspython==2.7.0",
    "ecdsa==0.19.1",
    "email_validator==2.2.0",
    "fastapi==0.115.6",
    "greenlet==3.2.3",
    "h11==0.16.0",
    "httpcore==1.0.9",
    "httptools==0.6.4",
    "httpx==0.25.2",
    "idna==3.10",
    "Mako==1.3.10",
    "MarkupSafe==3.0.2",
    "mysql-connector-python==9.1.0",
    "passlib==1.7.4",
    "phonenumbers==8.13.48",
    "psycopg2-binary==2.9.9",
    "pyasn1==0.6.1",
    "pycparser==2.22",
    "pydantic==2.9.0",
    "pydantic-settings==2.5.2",
    "pydantic_core==2.23.2",
    "PyJWT==2.10.1",
    "PyMySQL==1.1.1",
    "python-decouple==3.8",
    "python-dotenv==1.0.1",
    "python-jose==3.3.0",
    "python-magic==0.4.27",
    "python-multipart==0.0.19",
    "PyYAML==6.0.2",
    "redis==5.0.1",
    "requests==2.31.0",
    "rsa==4.9.1",
    "six==1.17.0",
    "slowapi==0.1.9",
    "sniffio==1.3.1",
    "SQLAlchemy==2.0.25",
    "starlette==0.41.3",
    "typing_extensions==4.14.0",
    "tzdata==2025.2",
    "urllib3==2.5.0",
    "uvicorn==0.32.1",
    "watchfiles==1.1.0",
    "websockets==15.0.1"
]

# Services that need requirements.txt
SERVICES = [
    "api-gateway",
    "services/auth-service",
    "services/content-quiz-service", 
    "services/assistant-service",
    "services/admin-service",
    "services/sync-messaging-service",
    "services/file-storage-service",
    "services/notification-service"
]

def fix_requirements_file(service_path):
    """Fix requirements.txt file for a service"""
    requirements_path = os.path.join(service_path, "requirements.txt")
    
    print(f"Fixing requirements.txt for {service_path}")
    
    # Write requirements with proper UTF-8 encoding
    with open(requirements_path, 'w', encoding='utf-8', newline='\n') as f:
        for req in BASE_REQUIREMENTS:
            f.write(f"{req}\n")
    
    print(f"✅ Fixed {requirements_path}")

def main():
    """Main function to fix all requirements files"""
    print("🔧 Fixing requirements.txt encoding issues...")
    
    base_dir = "."
    
    for service in SERVICES:
        service_path = os.path.join(base_dir, service)
        if os.path.exists(service_path):
            fix_requirements_file(service_path)
        else:
            print(f"❌ Service path not found: {service_path}")
    
    print("\n✅ All requirements.txt files have been fixed!")
    print("📝 All services now have:")
    print("   - Proper UTF-8 encoding")
    print("   - psycopg2-binary for PostgreSQL")
    print("   - slowapi for rate limiting")
    print("   - bleach for HTML sanitization")
    print("   - python-magic for file type detection")
    print("   - phonenumbers for phone validation")
    print("   - All other required dependencies")

if __name__ == "__main__":
    main()
