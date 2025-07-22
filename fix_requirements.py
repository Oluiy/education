"""
Fix all requirements.txt files with compatible package versions
"""

import os
from pathlib import Path

# Updated requirements.txt content with compatible versions
REQUIREMENTS_CONTENT = """fastapi==0.104.1
uvicorn==0.24.0
pydantic==2.5.0
sqlalchemy==2.0.23
alembic==1.13.0
psycopg2-binary==2.9.9
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-multipart==0.0.6
python-dotenv==1.0.0
httpx==0.25.2
redis==5.0.1
celery==5.3.4
cryptography>=40.0.0,<46.0.0
aiofiles==23.2.1
pydantic-settings==2.1.0
email-validator>=1.3.0
phonenumbers>=8.13.0
bleach>=6.0.0
requests>=2.31.0
Pillow>=10.0.0
"""

# Service-specific additional requirements
SERVICE_SPECIFIC = {
    "sync-messaging-service": ["websockets==12.0", "schedule==1.2.1"],
    "notification-service": ["twilio>=8.0.0", "pdfkit>=1.0.0"],
    "assistant-service": ["openai>=1.0.0", "tiktoken>=0.5.0"],
    "file-storage-service": ["python-magic>=0.4.0", "boto3>=1.28.0"],
    "admin-service": ["reportlab>=4.0.0", "openpyxl>=3.1.0"],
}

def update_requirements(service_path: str):
    """Update a service's requirements.txt"""
    service_name = service_path.split('/')[-1]
    requirements_path = Path(service_path) / "requirements.txt"
    
    if requirements_path.exists():
        # Start with base requirements
        content = REQUIREMENTS_CONTENT.strip()
        
        # Add service-specific requirements
        if service_name in SERVICE_SPECIFIC:
            content += "\n" + "\n".join(SERVICE_SPECIFIC[service_name])
        
        with open(requirements_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"✅ Updated {service_path}/requirements.txt")
    else:
        print(f"⚠️ {requirements_path} not found")

def main():
    """Update all service requirements.txt files"""
    os.chdir("c:/Users/USER/Documents/projects/education")
    
    services = [
        "services/auth-service",
        "services/content-quiz-service",
        "services/assistant-service",
        "services/admin-service",
        "services/sync-messaging-service",
        "services/file-storage-service",
        "services/notification-service"
    ]
    
    print("🔧 Fixing requirements.txt files with compatible versions...")
    
    for service_path in services:
        update_requirements(service_path)
    
    print("✅ All requirements.txt files updated!")
    print("📝 Key changes:")
    print("   - cryptography: Fixed yanked version (41.0.8 → >=40.0.0,<46.0.0)")
    print("   - email-validator: Made version flexible (>=1.3.0)")
    print("   - phonenumbers: Added for phone validation (>=8.13.0)")
    print("   - bleach: Added for HTML sanitization (>=6.0.0)")
    print("   - All packages: Updated to compatible versions")

if __name__ == "__main__":
    main()
