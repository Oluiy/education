"""
EduNerve Content & Quiz Service - Test Script
Comprehensive testing for content upload and quiz generation
"""

import requests
import json
import os
from datetime import datetime
from pathlib import Path

# Configuration
BASE_URL = "http://localhost:8001/api/v1"
AUTH_SERVICE_URL = "http://localhost:8000/api/v1/auth"

# Test data
TEST_CONTENT = """
Mathematics - Quadratic Equations

A quadratic equation is a polynomial equation of degree 2. The general form is:
ax² + bx + c = 0

where a, b, and c are constants and a ≠ 0.

Methods of Solving Quadratic Equations:
1. Factorization Method
2. Completing the Square
3. Quadratic Formula: x = (-b ± √(b² - 4ac)) / 2a

Example:
Solve x² - 5x + 6 = 0
Using factorization: (x - 2)(x - 3) = 0
Therefore: x = 2 or x = 3

Practice Questions:
1. What is the discriminant of x² - 4x + 4 = 0?
2. Solve 2x² + 3x - 2 = 0 using the quadratic formula.
3. Find the roots of x² - 7x + 12 = 0.
"""

def create_test_file():
    """Create a test file for upload"""
    test_dir = Path("test_files")
    test_dir.mkdir(exist_ok=True)
    
    test_file = test_dir / "math_notes.txt"
    with open(test_file, "w") as f:
        f.write(TEST_CONTENT)
    
    return str(test_file)

def login_and_get_token():
    """Login and get JWT token"""
    print("🔐 Logging in to get authentication token...")
    
    # First, try to get existing user or create test data
    login_data = {
        "email": "teacher@test.com",
        "password": "TeacherPass123"
    }
    
    try:
        response = requests.post(f"{AUTH_SERVICE_URL}/login", json=login_data)
        if response.status_code == 200:
            token = response.json()["access_token"]
            print(f"✅ Login successful")
            return token
        else:
            print(f"❌ Login failed: {response.status_code}")
            print("   Make sure the auth service is running and test user exists")
            return None
    except Exception as e:
        print(f"❌ Login error: {e}")
        return None

def test_content_upload(token):
    """Test content upload functionality"""
    print("\n📄 Testing Content Upload...")
    
    # Create test file
    test_file_path = create_test_file()
    
    try:
        headers = {"Authorization": f"Bearer {token}"}
        
        # Upload content
        with open(test_file_path, "rb") as f:
            files = {"file": ("math_notes.txt", f, "text/plain")}
            data = {
                "title": "Mathematics - Quadratic Equations",
                "description": "Comprehensive notes on quadratic equations for SS2 students",
                "subject": "Mathematics",
                "class_level": "SS2",
                "topic": "Quadratic Equations",
                "keywords": "quadratic, equations, algebra, mathematics",
                "is_public": "false"
            }
            
            response = requests.post(
                f"{BASE_URL}/content/upload",
                headers=headers,
                files=files,
                data=data
            )
        
        if response.status_code == 201:
            content_data = response.json()
            print(f"✅ Content uploaded successfully")
            print(f"   Content ID: {content_data['id']}")
            print(f"   Title: {content_data['title']}")
            print(f"   File size: {content_data['file_size']} bytes")
            return content_data["id"]
        else:
            print(f"❌ Content upload failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Content upload error: {e}")
        return None
    finally:
        # Clean up test file
        if os.path.exists(test_file_path):
            os.remove(test_file_path)

def test_content_list(token):
    """Test content listing"""
    print("\n📋 Testing Content List...")
    
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"{BASE_URL}/content", headers=headers)
        
        if response.status_code == 200:
            content_list = response.json()
            print(f"✅ Content list retrieved successfully")
            print(f"   Total content items: {len(content_list)}")
            
            if content_list:
                print("   Recent content:")
                for content in content_list[:3]:  # Show first 3
                    print(f"     - {content['title']} ({content['subject']} - {content['class_level']})")
            
            return content_list
        else:
            print(f"❌ Content list failed: {response.status_code}")
            return []
            
    except Exception as e:
        print(f"❌ Content list error: {e}")
        return []

def test_ai_quiz_generation(token, content_id):
    """Test AI quiz generation"""
    print("\n🧠 Testing AI Quiz Generation...")
    
    if not content_id:
        print("❌ No content ID provided for quiz generation")
        return None
    
    try:
        headers = {"Authorization": f"Bearer {token}"}
        quiz_request = {
            "content_id": content_id,
            "subject": "Mathematics",
            "class_level": "SS2",
            "topic": "Quadratic Equations",
            "difficulty_level": "medium",
            "quiz_type": "mcq",
            "num_questions": 5,
            "duration_minutes": 30
        }
        
        response = requests.post(
            f"{BASE_URL}/quiz/generate_ai",
            headers=headers,
            json=quiz_request
        )
        
        if response.status_code == 200:
            quiz_data = response.json()
            print(f"✅ AI quiz generated successfully")
            print(f"   Quiz ID: {quiz_data['quiz_id']}")
            print(f"   Questions generated: {quiz_data['total_questions']}")
            print(f"   Total marks: {quiz_data['total_marks']}")
            print(f"   Generation model: {quiz_data['generation_model']}")
            
            # Show sample questions
            if quiz_data.get('generated_questions'):
                print("\n   Sample questions:")
                for i, question in enumerate(quiz_data['generated_questions'][:2]):
                    print(f"     Q{i+1}: {question['question_text']}")
                    if question.get('options'):
                        for j, option in enumerate(question['options']):
                            mark = "✓" if option['is_correct'] else " "
                            print(f"         {chr(65+j)}) {option['text']} {mark}")
            
            return quiz_data['quiz_id']
        else:
            print(f"❌ AI quiz generation failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ AI quiz generation error: {e}")
        return None

def test_manual_quiz_creation(token):
    """Test manual quiz creation"""
    print("\n✏️ Testing Manual Quiz Creation...")
    
    try:
        headers = {"Authorization": f"Bearer {token}"}
        
        # Create manual quiz
        quiz_data = {
            "title": "Mathematics Quiz - Basic Algebra",
            "description": "Test your understanding of basic algebraic concepts",
            "quiz_type": "mcq",
            "difficulty_level": "easy",
            "subject": "Mathematics",
            "class_level": "SS1",
            "topic": "Basic Algebra",
            "duration_minutes": 20,
            "pass_mark": 60.0,
            "questions": [
                {
                    "question_id": "q1",
                    "question_type": "mcq",
                    "question_text": "What is the value of x in the equation 2x + 5 = 13?",
                    "marks": 2.0,
                    "options": [
                        {"text": "x = 3", "is_correct": False},
                        {"text": "x = 4", "is_correct": True},
                        {"text": "x = 5", "is_correct": False},
                        {"text": "x = 6", "is_correct": False}
                    ],
                    "explanation": "2x + 5 = 13, so 2x = 8, therefore x = 4"
                },
                {
                    "question_id": "q2",
                    "question_type": "mcq",
                    "question_text": "Simplify: 3x + 2x",
                    "marks": 2.0,
                    "options": [
                        {"text": "5x", "is_correct": True},
                        {"text": "6x", "is_correct": False},
                        {"text": "5x²", "is_correct": False},
                        {"text": "3x²", "is_correct": False}
                    ],
                    "explanation": "3x + 2x = 5x (like terms can be added)"
                }
            ]
        }
        
        response = requests.post(
            f"{BASE_URL}/quiz/create_manual",
            headers=headers,
            json=quiz_data
        )
        
        if response.status_code == 201:
            quiz_response = response.json()
            print(f"✅ Manual quiz created successfully")
            print(f"   Quiz ID: {quiz_response['id']}")
            print(f"   Title: {quiz_response['title']}")
            print(f"   Questions: {quiz_response['total_questions']}")
            print(f"   Total marks: {quiz_response['total_marks']}")
            return quiz_response['id']
        else:
            print(f"❌ Manual quiz creation failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Manual quiz creation error: {e}")
        return None

def test_quiz_list(token):
    """Test quiz listing"""
    print("\n📝 Testing Quiz List...")
    
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"{BASE_URL}/quiz", headers=headers)
        
        if response.status_code == 200:
            quiz_list = response.json()
            print(f"✅ Quiz list retrieved successfully")
            print(f"   Total quizzes: {len(quiz_list)}")
            
            if quiz_list:
                print("   Recent quizzes:")
                for quiz in quiz_list[:3]:
                    ai_tag = " (AI)" if quiz.get('is_ai_generated') else ""
                    print(f"     - {quiz['title']}{ai_tag}")
                    print(f"       {quiz['subject']} - {quiz['class_level']} - {quiz['total_questions']} questions")
            
            return quiz_list
        else:
            print(f"❌ Quiz list failed: {response.status_code}")
            return []
            
    except Exception as e:
        print(f"❌ Quiz list error: {e}")
        return []

def test_quiz_submission(token, quiz_id):
    """Test quiz submission (would need student token)"""
    print(f"\n📤 Testing Quiz Submission...")
    print("   Note: This would require a student token for actual submission")
    print(f"   Quiz ID for submission: {quiz_id}")
    
    # For now, just show what a submission would look like
    sample_submission = {
        "quiz_id": quiz_id,
        "answers": [
            {"question_id": "q1", "answer": "x = 4"},
            {"question_id": "q2", "answer": "5x"}
        ],
        "time_taken_minutes": 15
    }
    
    print("   Sample submission format:")
    print(f"   {json.dumps(sample_submission, indent=2)}")

def test_service_health():
    """Test service health"""
    print("\n🏥 Testing Service Health...")
    
    try:
        response = requests.get(f"{BASE_URL}/health")
        
        if response.status_code == 200:
            health_data = response.json()
            print(f"✅ Service health check passed")
            print(f"   Service: {health_data.get('service')}")
            print(f"   Database: {health_data.get('database')}")
            print(f"   OpenAI: {health_data.get('openai')}")
            print(f"   Auth Service: {health_data.get('auth_service')}")
            return True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 EduNerve Content & Quiz Service - Test Suite")
    print("=" * 60)
    
    # Test service health first
    if not test_service_health():
        print("\n❌ Service health check failed. Make sure the service is running.")
        return
    
    # Get authentication token
    token = login_and_get_token()
    if not token:
        print("\n❌ Authentication failed. Cannot proceed with tests.")
        return
    
    # Test content management
    content_id = test_content_upload(token)
    content_list = test_content_list(token)
    
    # Test quiz management
    manual_quiz_id = test_manual_quiz_creation(token)
    quiz_list = test_quiz_list(token)
    
    # Test AI quiz generation (only if OpenAI is configured)
    if content_id:
        ai_quiz_id = test_ai_quiz_generation(token, content_id)
        if ai_quiz_id:
            test_quiz_submission(token, ai_quiz_id)
    
    # Summary
    print("\n" + "=" * 60)
    print("🎉 Test Suite Completed!")
    print(f"📊 Results Summary:")
    print(f"   - Content uploaded: {'✅' if content_id else '❌'}")
    print(f"   - Content listed: {'✅' if content_list else '❌'}")
    print(f"   - Manual quiz created: {'✅' if manual_quiz_id else '❌'}")
    print(f"   - Quiz list retrieved: {'✅' if quiz_list else '❌'}")
    
    print("\n📋 Next Steps:")
    print("1. Check the API documentation at: http://localhost:8001/docs")
    print("2. Test with your frontend application")
    print("3. Configure OpenAI API key for AI features")
    print("4. Set up production database (PostgreSQL)")
    print("5. Configure cloud storage (Cloudinary)")

if __name__ == "__main__":
    main()
