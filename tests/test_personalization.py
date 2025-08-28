"""
Tests for Personalization Quiz and Student Preferences
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import json

from services.content_quiz_service.app.main import app
from services.content_quiz_service.app.database import get_db, Base
from services.content_quiz_service.app.models.content_models import PersonalizationQuiz, StudentPreferences
from services.content_quiz_service.app.schemas.personalization import (
    LearningStyle, DifficultyLevel, StudyTimePreference, ResourceType
)

# Test database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_personalization.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture(scope="function")
def setup_database():
    """Setup test database"""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def client():
    """Test client"""
    return TestClient(app)

@pytest.fixture
def mock_user():
    """Mock user for testing"""
    return {
        "user_id": 1,
        "school_id": 1,
        "email": "test@example.com",
        "role": "student"
    }

@pytest.fixture
def mock_auth_headers(mock_user):
    """Mock authentication headers"""
    return {"Authorization": f"Bearer mock_token_{mock_user['user_id']}"}

class TestPersonalizationQuiz:
    """Test personalization quiz endpoints"""
    
    def test_create_personalization_quiz_success(self, client, setup_database, mock_auth_headers):
        """Test successful creation of personalization quiz"""
        quiz_data = {
            "learning_style": "visual",
            "preferred_subjects": ["Mathematics", "Physics"],
            "difficulty_preference": "medium",
            "study_time_preference": "morning",
            "resource_preferences": {
                "video": True,
                "text": False,
                "audio": True,
                "interactive": True,
                "practice": True
            },
            "study_goals": ["Improve problem solving", "Master calculus"],
            "target_score": 85.0,
            "study_hours_per_day": 3.0,
            "preferred_session_duration": 30
        }
        
        response = client.post(
            "/api/v1/personalization/quiz",
            json=quiz_data,
            headers=mock_auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["learning_style"] == "visual"
        assert data["preferred_subjects"] == ["Mathematics", "Physics"]
        assert data["difficulty_preference"] == "medium"
        assert data["study_time_preference"] == "morning"
        assert "id" in data
        assert "created_at" in data
    
    def test_create_personalization_quiz_invalid_data(self, client, setup_database, mock_auth_headers):
        """Test creation with invalid data"""
        quiz_data = {
            "learning_style": "invalid_style",
            "preferred_subjects": [],  # Empty list
            "difficulty_preference": "medium",
            "study_time_preference": "morning",
            "resource_preferences": {
                "video": True,
                "text": False
            }
        }
        
        response = client.post(
            "/api/v1/personalization/quiz",
            json=quiz_data,
            headers=mock_auth_headers
        )
        
        assert response.status_code == 422  # Validation error
    
    def test_get_personalization_quiz(self, client, setup_database, mock_auth_headers):
        """Test getting personalization quiz"""
        # First create a quiz
        quiz_data = {
            "learning_style": "auditory",
            "preferred_subjects": ["English", "History"],
            "difficulty_preference": "easy",
            "study_time_preference": "afternoon",
            "resource_preferences": {
                "video": False,
                "text": True,
                "audio": True,
                "interactive": False,
                "practice": True
            }
        }
        
        create_response = client.post(
            "/api/v1/personalization/quiz",
            json=quiz_data,
            headers=mock_auth_headers
        )
        
        quiz_id = create_response.json()["id"]
        
        # Get the quiz
        response = client.get(
            f"/api/v1/personalization/quiz/{quiz_id}",
            headers=mock_auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == quiz_id
        assert data["learning_style"] == "auditory"
    
    def test_get_personalization_quiz_not_found(self, client, setup_database, mock_auth_headers):
        """Test getting non-existent quiz"""
        response = client.get(
            "/api/v1/personalization/quiz/999",
            headers=mock_auth_headers
        )
        
        assert response.status_code == 404
    
    def test_get_learning_recommendations(self, client, setup_database, mock_auth_headers):
        """Test getting learning recommendations"""
        # First create a quiz
        quiz_data = {
            "learning_style": "kinesthetic",
            "preferred_subjects": ["Chemistry", "Biology"],
            "difficulty_preference": "hard",
            "study_time_preference": "evening",
            "resource_preferences": {
                "video": True,
                "text": True,
                "audio": False,
                "interactive": True,
                "practice": True
            }
        }
        
        client.post(
            "/api/v1/personalization/quiz",
            json=quiz_data,
            headers=mock_auth_headers
        )
        
        # Get recommendations
        request_data = {
            "subject": "Chemistry",
            "limit": 5
        }
        
        response = client.post(
            "/api/v1/personalization/recommendations",
            json=request_data,
            headers=mock_auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) <= 5
    
    def test_get_learning_style_analysis(self, client, setup_database, mock_auth_headers):
        """Test getting learning style analysis"""
        # First create a quiz
        quiz_data = {
            "learning_style": "reading_writing",
            "preferred_subjects": ["Literature", "Philosophy"],
            "difficulty_preference": "medium",
            "study_time_preference": "night",
            "resource_preferences": {
                "video": False,
                "text": True,
                "audio": False,
                "interactive": False,
                "practice": True
            }
        }
        
        client.post(
            "/api/v1/personalization/quiz",
            json=quiz_data,
            headers=mock_auth_headers
        )
        
        # Get learning style analysis
        response = client.get(
            "/api/v1/personalization/learning-style",
            headers=mock_auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "primary_style" in data
        assert "style_percentages" in data
        assert "recommendations" in data
    
    def test_get_weak_areas(self, client, setup_database, mock_auth_headers):
        """Test getting weak areas analysis"""
        # First create a quiz
        quiz_data = {
            "learning_style": "visual",
            "preferred_subjects": ["Mathematics", "Physics", "Chemistry"],
            "difficulty_preference": "medium",
            "study_time_preference": "morning",
            "resource_preferences": {
                "video": True,
                "text": True,
                "audio": True,
                "interactive": True,
                "practice": True
            }
        }
        
        client.post(
            "/api/v1/personalization/quiz",
            json=quiz_data,
            headers=mock_auth_headers
        )
        
        # Get weak areas
        response = client.get(
            "/api/v1/personalization/weak-areas",
            headers=mock_auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

class TestStudentPreferences:
    """Test student preferences endpoints"""
    
    def test_save_student_preferences_success(self, client, setup_database, mock_auth_headers):
        """Test successful saving of student preferences"""
        preferences_data = {
            "preferred_learning_methods": ["video", "practice"],
            "difficulty_level": "medium",
            "study_pace": "normal",
            "preferred_content_types": ["video", "text"],
            "auto_play_videos": True,
            "show_transcripts": True,
            "enable_audio_summaries": False,
            "preferred_study_times": ["morning", "afternoon"],
            "session_duration": 25,
            "break_duration": 5,
            "daily_study_goal": 120,
            "text_to_speech_enabled": False,
            "large_text_mode": False,
            "high_contrast_mode": False,
            "dyslexia_friendly_font": False,
            "study_reminders": True,
            "achievement_notifications": True,
            "progress_updates": True,
            "quiet_hours_start": "22:00",
            "quiet_hours_end": "08:00",
            "preferred_language": "en",
            "timezone": "UTC"
        }
        
        response = client.post(
            "/api/v1/personalization/preferences",
            json=preferences_data,
            headers=mock_auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["difficulty_level"] == "medium"
        assert data["study_pace"] == "normal"
        assert data["session_duration"] == 25
        assert "id" in data
        assert "created_at" in data
    
    def test_save_student_preferences_invalid_data(self, client, setup_database, mock_auth_headers):
        """Test saving preferences with invalid data"""
        preferences_data = {
            "difficulty_level": "invalid_level",
            "study_pace": "invalid_pace",
            "session_duration": 200,  # Too long
            "quiet_hours_start": "25:00",  # Invalid time
            "preferred_language": "invalid_lang"
        }
        
        response = client.post(
            "/api/v1/personalization/preferences",
            json=preferences_data,
            headers=mock_auth_headers
        )
        
        assert response.status_code == 422  # Validation error
    
    def test_get_student_preferences(self, client, setup_database, mock_auth_headers):
        """Test getting student preferences"""
        # First save preferences
        preferences_data = {
            "preferred_learning_methods": ["reading", "practice"],
            "difficulty_level": "easy",
            "study_pace": "slow",
            "preferred_content_types": ["text", "audio"],
            "auto_play_videos": False,
            "show_transcripts": True,
            "enable_audio_summaries": True,
            "preferred_study_times": ["evening"],
            "session_duration": 45,
            "break_duration": 10,
            "daily_study_goal": 180,
            "text_to_speech_enabled": True,
            "large_text_mode": True,
            "high_contrast_mode": False,
            "dyslexia_friendly_font": False,
            "study_reminders": True,
            "achievement_notifications": False,
            "progress_updates": True,
            "quiet_hours_start": "23:00",
            "quiet_hours_end": "07:00",
            "preferred_language": "en",
            "timezone": "UTC"
        }
        
        client.post(
            "/api/v1/personalization/preferences",
            json=preferences_data,
            headers=mock_auth_headers
        )
        
        # Get preferences
        response = client.get(
            "/api/v1/personalization/preferences",
            headers=mock_auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["difficulty_level"] == "easy"
        assert data["study_pace"] == "slow"
        assert data["session_duration"] == 45
        assert data["text_to_speech_enabled"] == True
    
    def test_get_student_preferences_not_found(self, client, setup_database, mock_auth_headers):
        """Test getting preferences when none exist"""
        response = client.get(
            "/api/v1/personalization/preferences",
            headers=mock_auth_headers
        )
        
        assert response.status_code == 404
    
    def test_update_student_preferences(self, client, setup_database, mock_auth_headers):
        """Test updating student preferences"""
        # First save preferences
        preferences_data = {
            "preferred_learning_methods": ["video"],
            "difficulty_level": "medium",
            "study_pace": "normal",
            "preferred_content_types": ["video"],
            "auto_play_videos": True,
            "show_transcripts": True,
            "enable_audio_summaries": True,
            "preferred_study_times": ["morning"],
            "session_duration": 25,
            "break_duration": 5,
            "daily_study_goal": 120,
            "text_to_speech_enabled": False,
            "large_text_mode": False,
            "high_contrast_mode": False,
            "dyslexia_friendly_font": False,
            "study_reminders": True,
            "achievement_notifications": True,
            "progress_updates": True,
            "quiet_hours_start": "22:00",
            "quiet_hours_end": "08:00",
            "preferred_language": "en",
            "timezone": "UTC"
        }
        
        client.post(
            "/api/v1/personalization/preferences",
            json=preferences_data,
            headers=mock_auth_headers
        )
        
        # Update preferences
        update_data = {
            "difficulty_level": "hard",
            "session_duration": 60,
            "text_to_speech_enabled": True,
            "large_text_mode": True
        }
        
        response = client.put(
            "/api/v1/personalization/preferences",
            json=update_data,
            headers=mock_auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["difficulty_level"] == "hard"
        assert data["session_duration"] == 60
        assert data["text_to_speech_enabled"] == True
        assert data["large_text_mode"] == True

class TestPersonalizationIntegration:
    """Integration tests for personalization features"""
    
    def test_complete_personalization_workflow(self, client, setup_database, mock_auth_headers):
        """Test complete personalization workflow"""
        # 1. Create personalization quiz
        quiz_data = {
            "learning_style": "visual",
            "preferred_subjects": ["Mathematics", "Physics", "Chemistry"],
            "difficulty_preference": "medium",
            "study_time_preference": "morning",
            "resource_preferences": {
                "video": True,
                "text": True,
                "audio": False,
                "interactive": True,
                "practice": True
            },
            "study_goals": ["Master calculus", "Understand quantum physics"],
            "target_score": 90.0,
            "study_hours_per_day": 4.0,
            "preferred_session_duration": 45
        }
        
        quiz_response = client.post(
            "/api/v1/personalization/quiz",
            json=quiz_data,
            headers=mock_auth_headers
        )
        
        assert quiz_response.status_code == 200
        quiz_id = quiz_response.json()["id"]
        
        # 2. Save student preferences
        preferences_data = {
            "preferred_learning_methods": ["video", "practice"],
            "difficulty_level": "medium",
            "study_pace": "normal",
            "preferred_content_types": ["video", "text"],
            "auto_play_videos": True,
            "show_transcripts": True,
            "enable_audio_summaries": False,
            "preferred_study_times": ["morning", "afternoon"],
            "session_duration": 45,
            "break_duration": 10,
            "daily_study_goal": 240,
            "text_to_speech_enabled": False,
            "large_text_mode": False,
            "high_contrast_mode": False,
            "dyslexia_friendly_font": False,
            "study_reminders": True,
            "achievement_notifications": True,
            "progress_updates": True,
            "quiet_hours_start": "22:00",
            "quiet_hours_end": "08:00",
            "preferred_language": "en",
            "timezone": "UTC"
        }
        
        prefs_response = client.post(
            "/api/v1/personalization/preferences",
            json=preferences_data,
            headers=mock_auth_headers
        )
        
        assert prefs_response.status_code == 200
        
        # 3. Get learning recommendations
        recommendations_response = client.post(
            "/api/v1/personalization/recommendations",
            json={"subject": "Mathematics", "limit": 10},
            headers=mock_auth_headers
        )
        
        assert recommendations_response.status_code == 200
        recommendations = recommendations_response.json()
        assert len(recommendations) > 0
        
        # 4. Get learning style analysis
        analysis_response = client.get(
            "/api/v1/personalization/learning-style",
            headers=mock_auth_headers
        )
        
        assert analysis_response.status_code == 200
        analysis = analysis_response.json()
        assert analysis["primary_style"] == "visual"
        
        # 5. Get weak areas
        weak_areas_response = client.get(
            "/api/v1/personalization/weak-areas",
            headers=mock_auth_headers
        )
        
        assert weak_areas_response.status_code == 200
        weak_areas = weak_areas_response.json()
        assert isinstance(weak_areas, list)
        
        # 6. Verify quiz data
        quiz_get_response = client.get(
            f"/api/v1/personalization/quiz/{quiz_id}",
            headers=mock_auth_headers
        )
        
        assert quiz_get_response.status_code == 200
        quiz_data_retrieved = quiz_get_response.json()
        assert quiz_data_retrieved["learning_style"] == "visual"
        assert quiz_data_retrieved["preferred_subjects"] == ["Mathematics", "Physics", "Chemistry"]
        
        # 7. Verify preferences data
        prefs_get_response = client.get(
            "/api/v1/personalization/preferences",
            headers=mock_auth_headers
        )
        
        assert prefs_get_response.status_code == 200
        prefs_data_retrieved = prefs_get_response.json()
        assert prefs_data_retrieved["difficulty_level"] == "medium"
        assert prefs_data_retrieved["session_duration"] == 45

class TestPersonalizationValidation:
    """Test validation rules for personalization data"""
    
    def test_quiz_validation_rules(self, client, setup_database, mock_auth_headers):
        """Test validation rules for quiz data"""
        # Test empty subjects
        quiz_data = {
            "learning_style": "visual",
            "preferred_subjects": [],
            "difficulty_preference": "medium",
            "study_time_preference": "morning",
            "resource_preferences": {"video": True}
        }
        
        response = client.post(
            "/api/v1/personalization/quiz",
            json=quiz_data,
            headers=mock_auth_headers
        )
        
        assert response.status_code == 422
        
        # Test too many subjects
        quiz_data["preferred_subjects"] = [f"Subject{i}" for i in range(15)]
        
        response = client.post(
            "/api/v1/personalization/quiz",
            json=quiz_data,
            headers=mock_auth_headers
        )
        
        assert response.status_code == 422
        
        # Test invalid resource preferences
        quiz_data["preferred_subjects"] = ["Mathematics"]
        quiz_data["resource_preferences"] = {"invalid_resource": True}
        
        response = client.post(
            "/api/v1/personalization/quiz",
            json=quiz_data,
            headers=mock_auth_headers
        )
        
        assert response.status_code == 422
    
    def test_preferences_validation_rules(self, client, setup_database, mock_auth_headers):
        """Test validation rules for preferences data"""
        # Test invalid study pace
        preferences_data = {
            "difficulty_level": "medium",
            "study_pace": "invalid_pace",
            "preferred_content_types": ["video"],
            "auto_play_videos": True,
            "show_transcripts": True,
            "enable_audio_summaries": True,
            "preferred_study_times": ["morning"],
            "session_duration": 25,
            "break_duration": 5,
            "daily_study_goal": 120,
            "text_to_speech_enabled": False,
            "large_text_mode": False,
            "high_contrast_mode": False,
            "dyslexia_friendly_font": False,
            "study_reminders": True,
            "achievement_notifications": True,
            "progress_updates": True,
            "quiet_hours_start": "22:00",
            "quiet_hours_end": "08:00",
            "preferred_language": "en",
            "timezone": "UTC"
        }
        
        response = client.post(
            "/api/v1/personalization/preferences",
            json=preferences_data,
            headers=mock_auth_headers
        )
        
        assert response.status_code == 422
        
        # Test invalid session duration
        preferences_data["study_pace"] = "normal"
        preferences_data["session_duration"] = 200  # Too long
        
        response = client.post(
            "/api/v1/personalization/preferences",
            json=preferences_data,
            headers=mock_auth_headers
        )
        
        assert response.status_code == 422
        
        # Test invalid time format
        preferences_data["session_duration"] = 25
        preferences_data["quiet_hours_start"] = "25:00"  # Invalid time
        
        response = client.post(
            "/api/v1/personalization/preferences",
            json=preferences_data,
            headers=mock_auth_headers
        )
        
        assert response.status_code == 422
