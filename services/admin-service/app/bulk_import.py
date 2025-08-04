import csv
import io
from typing import List, Dict, Any, Optional, Tuple
from sqlalchemy.orm import Session
from datetime import datetime
import re
import secrets
import string
import requests
import json
from enum import Enum

from .models import User, AdminUser

# Define UserRole enum locally since it's from another service
class UserRole(str, Enum):
    SUPER_ADMIN = "super_admin"
    SCHOOL_ADMIN = "school_admin"
    TEACHER = "teacher"
    STUDENT = "student"
    PARENT = "parent"

class BulkImportService:
    
    def __init__(self, db: Session, auth_service_url: str = "http://localhost:8001"):
        self.db = db
        self.auth_service_url = auth_service_url
    
    def validate_csv_headers(self, headers: List[str], required_headers: List[str]) -> Dict[str, Any]:
        """Validate CSV headers"""
        missing_headers = [h for h in required_headers if h not in headers]
        extra_headers = [h for h in headers if h not in required_headers + self._get_optional_headers()]
        
        return {
            "is_valid": len(missing_headers) == 0,
            "missing_headers": missing_headers,
            "extra_headers": extra_headers,
            "warnings": [f"Extra column '{h}' will be ignored" for h in extra_headers]
        }
    
    def _get_optional_headers(self) -> List[str]:
        """Get list of optional CSV headers"""
        return [
            "phone_number", "student_id", "parent_name", "parent_email", 
            "parent_phone", "class_name", "section", "date_of_birth",
            "address", "emergency_contact", "medical_info"
        ]
    
    def _get_required_headers_by_role(self, role: str) -> List[str]:
        """Get required headers based on user role"""
        base_headers = ["full_name", "email", "username"]
        
        if role == UserRole.STUDENT.value:
            return base_headers + ["student_id"]
        elif role == UserRole.TEACHER.value:
            return base_headers + ["employee_id"]
        elif role == UserRole.PARENT.value:
            return base_headers + ["child_student_id"]
        else:
            return base_headers
    
    def generate_username(self, full_name: str, email: str, school_id: int, existing_usernames: set) -> str:
        """Generate unique username"""
        # Try email prefix first
        base_username = email.split('@')[0].lower()
        
        # Clean username (only alphanumeric and underscores)
        base_username = re.sub(r'[^a-zA-Z0-9_]', '', base_username)
        
        if base_username and base_username not in existing_usernames:
            return base_username
        
        # Try first name + last initial
        name_parts = full_name.lower().split()
        if len(name_parts) >= 2:
            username = name_parts[0] + name_parts[-1][0]
            username = re.sub(r'[^a-zA-Z0-9_]', '', username)
            
            if username not in existing_usernames:
                return username
        
        # Add numbers until unique
        counter = 1
        while f"{base_username}{counter}" in existing_usernames:
            counter += 1
        
        return f"{base_username}{counter}"
    
    def generate_password(self, length: int = 12) -> str:
        """Generate secure random password"""
        lowercase = string.ascii_lowercase
        uppercase = string.ascii_uppercase
        digits = string.digits
        symbols = "!@#$%^&*"
        
        # Ensure at least one character from each category
        password = [
            secrets.choice(lowercase),
            secrets.choice(uppercase),
            secrets.choice(digits),
            secrets.choice(symbols)
        ]
        
        # Fill remaining length with random choices from all categories
        all_chars = lowercase + uppercase + digits + symbols
        for _ in range(length - 4):
            password.append(secrets.choice(all_chars))
        
        # Shuffle the password list
        secrets.SystemRandom().shuffle(password)
        return ''.join(password)
    
    def parse_csv_content(self, file_content: bytes, role: str) -> Tuple[List[Dict], List[str]]:
        """Parse CSV content and return data with errors"""
        
        try:
            # Detect encoding
            content_str = file_content.decode('utf-8-sig')  # Handle BOM
        except UnicodeDecodeError:
            try:
                content_str = file_content.decode('latin-1')
            except UnicodeDecodeError:
                raise ValueError("Unable to decode file. Please ensure it's a valid CSV file.")
        
        # Parse CSV
        csv_reader = csv.DictReader(io.StringIO(content_str))
        headers = csv_reader.fieldnames
        
        if not headers:
            raise ValueError("CSV file appears to be empty or invalid")
        
        # Validate headers
        required_headers = self._get_required_headers_by_role(role)
        validation = self.validate_csv_headers(headers, required_headers)
        
        if not validation["is_valid"]:
            raise ValueError(f"Missing required columns: {', '.join(validation['missing_headers'])}")
        
        # Parse rows
        rows = []
        errors = []
        
        for row_num, row in enumerate(csv_reader, start=2):  # Start at 2 for header
            try:
                # Clean and validate row data
                cleaned_row = self._clean_row_data(row, role)
                validation_errors = self._validate_row_data(cleaned_row, role, row_num)
                
                if validation_errors:
                    errors.extend(validation_errors)
                else:
                    rows.append(cleaned_row)
                    
            except Exception as e:
                errors.append(f"Row {row_num}: {str(e)}")
        
        return rows, errors
    
    def _clean_row_data(self, row: Dict, role: str) -> Dict:
        """Clean and normalize row data"""
        cleaned = {}
        
        for key, value in row.items():
            if value:
                # Remove extra whitespace
                cleaned[key] = str(value).strip()
            else:
                cleaned[key] = ""
        
        # Normalize email
        if cleaned.get("email"):
            cleaned["email"] = cleaned["email"].lower()
        
        # Clean phone numbers
        for phone_field in ["phone_number", "parent_phone", "emergency_contact"]:
            if cleaned.get(phone_field):
                cleaned[phone_field] = re.sub(r'[^\d+\-\s()]', '', cleaned[phone_field])
        
        return cleaned
    
    def _validate_row_data(self, row: Dict, role: str, row_num: int) -> List[str]:
        """Validate individual row data"""
        errors = []
        
        # Required field validation
        required_fields = self._get_required_headers_by_role(role)
        for field in required_fields:
            if not row.get(field):
                errors.append(f"Row {row_num}: Missing required field '{field}'")
        
        # Email validation
        if row.get("email"):
            email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            if not re.match(email_pattern, row["email"]):
                errors.append(f"Row {row_num}: Invalid email format")
        
        # Username validation (if provided)
        if row.get("username"):
            if len(row["username"]) < 3:
                errors.append(f"Row {row_num}: Username must be at least 3 characters")
            if not re.match(r'^[a-zA-Z0-9_]+$', row["username"]):
                errors.append(f"Row {row_num}: Username can only contain letters, numbers, and underscores")
        
        return errors
    
    def bulk_import_users(
        self, 
        file_content: bytes, 
        role: str, 
        school_id: int,
        admin_user_id: int,
        send_emails: bool = True
    ) -> Dict[str, Any]:
        """Bulk import users from CSV"""
        
        try:
            # Parse CSV
            rows, parsing_errors = self.parse_csv_content(file_content, role)
            
            if parsing_errors:
                return {
                    "success": False,
                    "errors": parsing_errors,
                    "imported_count": 0,
                    "failed_count": len(parsing_errors)
                }
            
            # Get existing usernames and emails in school
            existing_users = self.db.query(User).filter(User.school_id == school_id).all()
            existing_usernames = {user.username for user in existing_users}
            existing_emails = {user.email for user in existing_users}
            
            # Process rows
            imported_users = []
            failed_imports = []
            generated_passwords = {}
            
            for row in rows:
                try:
                    # Check for existing email
                    if row["email"] in existing_emails:
                        failed_imports.append({
                            "row_data": row,
                            "error": f"Email {row['email']} already exists"
                        })
                        continue
                    
                    # Generate username if not provided
                    if not row.get("username"):
                        row["username"] = self.generate_username(
                            row["full_name"], 
                            row["email"], 
                            school_id, 
                            existing_usernames
                        )
                    elif row["username"] in existing_usernames:
                        failed_imports.append({
                            "row_data": row,
                            "error": f"Username {row['username']} already exists"
                        })
                        continue
                    
                    # Generate password
                    password = self.generate_password()
                    generated_passwords[row["email"]] = password
                    
                    # Prepare profile data
                    profile_data = {}
                    for field in self._get_optional_headers():
                        if row.get(field):
                            profile_data[field] = row[field]
                    
                    # Create user data
                    user_data = {
                        "username": row["username"],
                        "email": row["email"],
                        "password": password,
                        "full_name": row["full_name"],
                        "phone_number": row.get("phone_number", ""),
                        "role": role,
                        "profile_data": profile_data
                    }
                    
                    # Register user via auth service HTTP call
                    auth_response = requests.post(
                        f"{self.auth_service_url}/register",
                        json=user_data,
                        headers={"Content-Type": "application/json"},
                        timeout=10
                    )
                    
                    if auth_response.status_code != 201:
                        raise Exception(f"Auth service error: {auth_response.text}")
                    
                    user_result = auth_response.json()
                    imported_users.append({
                        "user": user_result,
                        "password": password,
                        "row_data": row
                    })
                    
                    # Update tracking sets
                    existing_usernames.add(row["username"])
                    existing_emails.add(row["email"])
                    
                except Exception as e:
                    failed_imports.append({
                        "row_data": row,
                        "error": str(e)
                    })
            
            # Log admin action
            self._log_bulk_import_action(
                admin_user_id, 
                school_id, 
                role, 
                len(imported_users), 
                len(failed_imports)
            )
            
            return {
                "success": True,
                "imported_count": len(imported_users),
                "failed_count": len(failed_imports),
                "imported_users": [
                    {
                        "id": item["user"]["id"],
                        "username": item["user"]["username"],
                        "email": item["user"]["email"],
                        "full_name": item["user"]["full_name"],
                        "password": item["password"]
                    } for item in imported_users
                ],
                "failed_imports": failed_imports,
                "generated_passwords": generated_passwords
            }
            
        except Exception as e:
            return {
                "success": False,
                "errors": [str(e)],
                "imported_count": 0,
                "failed_count": 0
            }
    
    def _log_bulk_import_action(self, admin_user_id: int, school_id: int, role: str, success_count: int, failed_count: int):
        """Log bulk import action"""
        from .models import AdminAction
        
        action = AdminAction(
            admin_user_id=admin_user_id,
            action_type="bulk_import",
            target_type="users",
            target_id=school_id,
            description=f"Bulk import of {role} users",
            details={
                "role": role,
                "success_count": success_count,
                "failed_count": failed_count,
                "timestamp": datetime.utcnow().isoformat()
            }
        )
        self.db.add(action)
        self.db.commit()
    
    def get_csv_template(self, role: str) -> str:
        """Generate CSV template for role"""
        
        required_headers = self._get_required_headers_by_role(role)
        optional_headers = self._get_optional_headers()
        
        if role == UserRole.STUDENT.value:
            sample_data = {
                "full_name": "John Doe",
                "email": "john.doe@example.com",
                "username": "johndoe",
                "student_id": "STU001",
                "phone_number": "+1234567890",
                "parent_name": "Jane Doe",
                "parent_email": "jane.doe@example.com",
                "parent_phone": "+1234567891",
                "class_name": "Grade 10",
                "section": "A"
            }
        elif role == UserRole.TEACHER.value:
            sample_data = {
                "full_name": "Jane Smith",
                "email": "jane.smith@example.com",
                "username": "janesmith",
                "employee_id": "EMP001",
                "phone_number": "+1234567890",
                "class_name": "Mathematics",
                "section": "Department"
            }
        else:
            sample_data = {
                "full_name": "Parent Name",
                "email": "parent@example.com",
                "username": "parentuser",
                "phone_number": "+1234567890"
            }
        
        # Create CSV content
        all_headers = required_headers + [h for h in optional_headers if h in sample_data]
        
        csv_content = ",".join(all_headers) + "\n"
        csv_content += ",".join([sample_data.get(h, "") for h in all_headers])
        
        return csv_content
