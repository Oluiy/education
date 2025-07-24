#!/usr/bin/env python3
"""
Comprehensive script to fix all microservices dependencies and missing modules
"""

import os
import re
import sys
from pathlib import Path

def main():
    project_root = Path(__file__).parent
    services_dir = project_root / "services"
    api_gateway_dir = project_root / "api-gateway"
    
    print("🔧 Starting comprehensive microservices fix...")
    
    # Define missing packages for each service
    missing_packages = {
        'api-gateway': ['slowapi==0.1.9'],
        'auth-service': ['bleach==6.1.0'],
        'content-quiz-service': ['bleach==6.1.0'],
        'assistant-service': ['bleach==6.1.0'],
        'admin-service': ['bleach==6.1.0'],
        'sync-messaging-service': ['bleach==6.1.0'],
        'file-storage-service': ['python-magic==0.4.27', 'bleach==6.1.0'],
        'notification-service': ['phonenumbers==8.13.27', 'bleach==6.1.0']
    }
    
    # Fix API Gateway
    print("\n📦 Fixing API Gateway...")
    fix_api_gateway_requirements(api_gateway_dir, missing_packages['api-gateway'])
    
    # Fix each service
    for service_name, packages in missing_packages.items():
        if service_name == 'api-gateway':
            continue
            
        service_dir = services_dir / service_name
        if service_dir.exists():
            print(f"\n📦 Fixing {service_name}...")
            fix_service_requirements(service_dir, packages)
            fix_models_file(service_dir, service_name)
        else:
            print(f"⚠️  Service directory not found: {service_dir}")
    
    print("\n✅ All fixes completed!")
    print("\n🐳 Now rebuild containers with:")
    print("docker-compose down")
    print("docker-compose build --no-cache")
    print("docker-compose up -d")

def fix_api_gateway_requirements(api_gateway_dir, packages):
    """Fix API Gateway requirements"""
    requirements_file = api_gateway_dir / "requirements.txt"
    
    if not requirements_file.exists():
        print(f"⚠️  Requirements file not found: {requirements_file}")
        return
    
    # Read existing requirements
    with open(requirements_file, 'r') as f:
        content = f.read()
    
    # Add missing packages
    for package in packages:
        package_name = package.split('==')[0]
        if package_name not in content:
            print(f"   ➕ Adding {package}")
            content += f"\n{package}"
    
    # Write back
    with open(requirements_file, 'w') as f:
        f.write(content)
    
    print(f"   ✅ Updated {requirements_file}")

def fix_service_requirements(service_dir, packages):
    """Fix service requirements.txt file"""
    requirements_file = service_dir / "requirements.txt"
    
    if not requirements_file.exists():
        print(f"   ⚠️  Requirements file not found: {requirements_file}")
        return
    
    # Read existing requirements
    with open(requirements_file, 'r') as f:
        content = f.read()
    
    # Add missing packages
    for package in packages:
        package_name = package.split('==')[0]
        if package_name not in content:
            print(f"   ➕ Adding {package}")
            content += f"\n{package}"
    
    # Write back
    with open(requirements_file, 'w') as f:
        f.write(content)
    
    print(f"   ✅ Updated {requirements_file}")

def fix_models_file(service_dir, service_name):
    """Fix models.py file with required models"""
    models_file = service_dir / "app" / "models.py"
    
    if not models_file.exists():
        print(f"   ⚠️  Models file not found: {models_file}")
        return
    
    # Read existing models
    with open(models_file, 'r') as f:
        content = f.read()
    
    # Define required models for each service
    required_models = get_required_models(service_name)
    
    # Check if models exist and add if missing
    for model_name, model_code in required_models.items():
        if f"class {model_name}" not in content:
            print(f"   ➕ Adding model {model_name}")
            content += f"\n\n{model_code}"
    
    # Write back
    with open(models_file, 'w') as f:
        f.write(content)
    
    print(f"   ✅ Updated {models_file}")

def get_required_models(service_name):
    """Get required models for each service"""
    
    base_imports = """from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey, JSON, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()"""
    
    if service_name == "assistant-service":
        return {
            "StudyPlan": f'''{base_imports}

class StudyPlan(Base):
    __tablename__ = "study_plans"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    subject = Column(String(100))
    difficulty_level = Column(String(50))
    estimated_hours = Column(Integer)
    goals = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = Column(Boolean, default=True)''',
            
            "StudyResource": f'''{base_imports}

class StudyResource(Base):
    __tablename__ = "study_resources"
    
    id = Column(Integer, primary_key=True, index=True)
    study_plan_id = Column(Integer, ForeignKey("study_plans.id"))
    title = Column(String(255), nullable=False)
    description = Column(Text)
    resource_type = Column(String(50))  # video, article, book, etc.
    url = Column(String(500))
    difficulty_level = Column(String(50))
    estimated_time = Column(Integer)  # in minutes
    created_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)''',
            
            "StudentActivity": f'''{base_imports}

class StudentActivity(Base):
    __tablename__ = "student_activities"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True)
    activity_type = Column(String(100))  # study, quiz, assignment, etc.
    resource_id = Column(Integer)
    title = Column(String(255))
    description = Column(Text)
    duration_minutes = Column(Integer)
    score = Column(Float)
    completed = Column(Boolean, default=False)
    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime)
    metadata = Column(JSON)''',
            
            "LearningAnalytics": f'''{base_imports}

class LearningAnalytics(Base):
    __tablename__ = "learning_analytics"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True)
    subject = Column(String(100))
    metric_type = Column(String(100))  # progress, performance, engagement
    metric_value = Column(Float)
    period_start = Column(DateTime)
    period_end = Column(DateTime)
    calculated_at = Column(DateTime, default=datetime.utcnow)
    metadata = Column(JSON)'''
        }
    
    elif service_name == "notification-service":
        return {
            "Notification": f'''{base_imports}

class Notification(Base):
    __tablename__ = "notifications"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True)
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    notification_type = Column(String(50))  # email, sms, push, whatsapp
    status = Column(String(50), default="pending")  # pending, sent, failed
    priority = Column(String(20), default="medium")  # low, medium, high
    scheduled_at = Column(DateTime)
    sent_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    metadata = Column(JSON)'''
        }
    
    elif service_name == "sync-messaging-service":
        return {
            "Message": f'''{base_imports}

class Message(Base):
    __tablename__ = "messages"
    
    id = Column(Integer, primary_key=True, index=True)
    sender_id = Column(Integer, nullable=False)
    recipient_id = Column(Integer, nullable=False)
    conversation_id = Column(String(100))
    message_type = Column(String(50), default="text")  # text, image, file, etc.
    content = Column(Text, nullable=False)
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    metadata = Column(JSON)''',
            
            "Conversation": f'''{base_imports}

class Conversation(Base):
    __tablename__ = "conversations"
    
    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(String(100), unique=True, index=True)
    participants = Column(JSON)  # List of user IDs
    conversation_type = Column(String(50), default="direct")  # direct, group
    title = Column(String(255))
    last_message_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)'''
        }
    
    elif service_name == "file-storage-service":
        return {
            "FileRecord": f'''{base_imports}

class FileRecord(Base):
    __tablename__ = "file_records"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True)
    filename = Column(String(255), nullable=False)
    original_filename = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_size = Column(Integer)
    file_type = Column(String(100))
    mime_type = Column(String(100))
    upload_date = Column(DateTime, default=datetime.utcnow)
    is_public = Column(Boolean, default=False)
    description = Column(Text)
    metadata = Column(JSON)'''
        }
    
    # Return empty dict for services that don't need specific models
    return {}

if __name__ == "__main__":
    main()
