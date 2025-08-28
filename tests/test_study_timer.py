"""
Tests for Study Timer and Study Sessions
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timedelta
import json

from services.content_quiz_service.app.main import app
from services.content_quiz_service.app.database import get_db, Base
from services.content_quiz_service.app.models.content_models import StudySession, StudyTimer
from services.content_quiz_service.app.schemas.study_timer import (
    SessionType, SessionStatus, TimerStatus
)

# Test database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_study_timer.db"
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

class TestStudySessions:
    """Test study session endpoints"""
    
    def test_start_study_session_success(self, client, setup_database, mock_auth_headers):
        """Test successful start of study session"""
        session_data = {
            "subject": "Mathematics",
            "topic": "Calculus",
            "session_type": "study",
            "planned_duration": 30,
            "goals": ["Complete calculus problems", "Review derivatives"],
            "notes": "Focus on understanding the concepts",
            "device_type": "web"
        }
        
        response = client.post(
            "/api/v1/study-timer/sessions",
            json=session_data,
            headers=mock_auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["subject"] == "Mathematics"
        assert data["topic"] == "Calculus"
        assert data["session_type"] == "study"
        assert data["planned_duration"] == 30
        assert data["status"] == "active"
        assert "id" in data
        assert "start_time" in data
    
    def test_start_study_session_invalid_data(self, client, setup_database, mock_auth_headers):
        """Test starting session with invalid data"""
        session_data = {
            "subject": "Mathematics",
            "session_type": "invalid_type",
            "planned_duration": 200,  # Too long
            "goals": ["Goal 1", "Goal 2", "Goal 3", "Goal 4", "Goal 5", "Goal 6"],  # Too many goals
            "device_type": "invalid_device"
        }
        
        response = client.post(
            "/api/v1/study-timer/sessions",
            json=session_data,
            headers=mock_auth_headers
        )
        
        assert response.status_code == 422  # Validation error
    
    def test_pause_study_session(self, client, setup_database, mock_auth_headers):
        """Test pausing a study session"""
        # First start a session
        session_data = {
            "subject": "Physics",
            "topic": "Mechanics",
            "session_type": "study",
            "planned_duration": 25,
            "goals": ["Understand Newton's laws"],
            "device_type": "web"
        }
        
        start_response = client.post(
            "/api/v1/study-timer/sessions",
            json=session_data,
            headers=mock_auth_headers
        )
        
        session_id = start_response.json()["id"]
        
        # Pause the session
        response = client.post(
            f"/api/v1/study-timer/sessions/{session_id}/pause",
            headers=mock_auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "paused"
    
    def test_resume_study_session(self, client, setup_database, mock_auth_headers):
        """Test resuming a paused study session"""
        # First start and pause a session
        session_data = {
            "subject": "Chemistry",
            "topic": "Organic Chemistry",
            "session_type": "study",
            "planned_duration": 45,
            "goals": ["Learn organic compounds"],
            "device_type": "web"
        }
        
        start_response = client.post(
            "/api/v1/study-timer/sessions",
            json=session_data,
            headers=mock_auth_headers
        )
        
        session_id = start_response.json()["id"]
        
        # Pause the session
        client.post(
            f"/api/v1/study-timer/sessions/{session_id}/pause",
            headers=mock_auth_headers
        )
        
        # Resume the session
        response = client.post(
            f"/api/v1/study-timer/sessions/{session_id}/resume",
            headers=mock_auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "active"
    
    def test_complete_study_session(self, client, setup_database, mock_auth_headers):
        """Test completing a study session"""
        # First start a session
        session_data = {
            "subject": "Biology",
            "topic": "Cell Biology",
            "session_type": "study",
            "planned_duration": 60,
            "goals": ["Understand cell structure", "Learn about organelles"],
            "device_type": "web"
        }
        
        start_response = client.post(
            "/api/v1/study-timer/sessions",
            json=session_data,
            headers=mock_auth_headers
        )
        
        session_id = start_response.json()["id"]
        
        # Complete the session
        completion_data = {
            "notes": "Great session, understood most concepts",
            "completed_goals": ["Understand cell structure"],
            "focus_rating": 4,
            "productivity_rating": 5,
            "difficulty_rating": 3
        }
        
        response = client.post(
            f"/api/v1/study-timer/sessions/{session_id}/complete",
            json=completion_data,
            headers=mock_auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "completed"
        assert data["notes"] == "Great session, understood most concepts"
        assert data["focus_rating"] == 4
        assert data["productivity_rating"] == 5
        assert data["difficulty_rating"] == 3
        assert "end_time" in data
        assert "actual_duration" in data
    
    def test_get_study_session(self, client, setup_database, mock_auth_headers):
        """Test getting a specific study session"""
        # First start a session
        session_data = {
            "subject": "English",
            "topic": "Literature",
            "session_type": "reading",
            "planned_duration": 20,
            "goals": ["Read chapter 5"],
            "device_type": "mobile"
        }
        
        start_response = client.post(
            "/api/v1/study-timer/sessions",
            json=session_data,
            headers=mock_auth_headers
        )
        
        session_id = start_response.json()["id"]
        
        # Get the session
        response = client.get(
            f"/api/v1/study-timer/sessions/{session_id}",
            headers=mock_auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == session_id
        assert data["subject"] == "English"
        assert data["session_type"] == "reading"
    
    def test_get_study_sessions_list(self, client, setup_database, mock_auth_headers):
        """Test getting list of study sessions"""
        # Create multiple sessions
        sessions_data = [
            {
                "subject": "Mathematics",
                "topic": "Algebra",
                "session_type": "study",
                "planned_duration": 30,
                "goals": ["Solve equations"],
                "device_type": "web"
            },
            {
                "subject": "Physics",
                "topic": "Thermodynamics",
                "session_type": "practice",
                "planned_duration": 45,
                "goals": ["Practice problems"],
                "device_type": "web"
            }
        ]
        
        for session_data in sessions_data:
            client.post(
                "/api/v1/study-timer/sessions",
                json=session_data,
                headers=mock_auth_headers
            )
        
        # Get sessions list
        response = client.get(
            "/api/v1/study-timer/sessions",
            headers=mock_auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "sessions" in data
        assert "total_count" in data
        assert "total_duration" in data
        assert "average_session_length" in data
        assert "completion_rate" in data
        assert len(data["sessions"]) >= 2
    
    def test_get_active_session(self, client, setup_database, mock_auth_headers):
        """Test getting active study session"""
        # Start a session
        session_data = {
            "subject": "History",
            "topic": "World War II",
            "session_type": "study",
            "planned_duration": 40,
            "goals": ["Learn about key events"],
            "device_type": "tablet"
        }
        
        client.post(
            "/api/v1/study-timer/sessions",
            json=session_data,
            headers=mock_auth_headers
        )
        
        # Get active session
        response = client.get(
            "/api/v1/study-timer/sessions/active",
            headers=mock_auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["subject"] == "History"
        assert data["status"] == "active"

class TestStudyTimers:
    """Test study timer endpoints"""
    
    def test_create_study_timer_success(self, client, setup_database, mock_auth_headers):
        """Test successful creation of study timer"""
        timer_data = {
            "timer_name": "Pomodoro Timer",
            "study_duration": 25,
            "break_duration": 5,
            "long_break_duration": 15,
            "sessions_before_long_break": 4,
            "auto_start_breaks": True,
            "auto_start_sessions": False,
            "sound_enabled": True,
            "notifications_enabled": True,
            "is_default": True
        }
        
        response = client.post(
            "/api/v1/study-timer/timers",
            json=timer_data,
            headers=mock_auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["timer_name"] == "Pomodoro Timer"
        assert data["study_duration"] == 25
        assert data["break_duration"] == 5
        assert data["is_default"] == True
        assert "id" in data
        assert "created_at" in data
    
    def test_create_study_timer_invalid_data(self, client, setup_database, mock_auth_headers):
        """Test creating timer with invalid data"""
        timer_data = {
            "timer_name": "",  # Empty name
            "study_duration": 200,  # Too long
            "break_duration": 60,  # Too long
            "sessions_before_long_break": 15  # Too many
        }
        
        response = client.post(
            "/api/v1/study-timer/timers",
            json=timer_data,
            headers=mock_auth_headers
        )
        
        assert response.status_code == 422  # Validation error
    
    def test_get_study_timers(self, client, setup_database, mock_auth_headers):
        """Test getting study timers"""
        # Create multiple timers
        timers_data = [
            {
                "timer_name": "Quick Study",
                "study_duration": 15,
                "break_duration": 3,
                "long_break_duration": 10,
                "sessions_before_long_break": 3,
                "is_default": False
            },
            {
                "timer_name": "Deep Focus",
                "study_duration": 50,
                "break_duration": 10,
                "long_break_duration": 20,
                "sessions_before_long_break": 2,
                "is_default": True
            }
        ]
        
        for timer_data in timers_data:
            client.post(
                "/api/v1/study-timer/timers",
                json=timer_data,
                headers=mock_auth_headers
            )
        
        # Get timers
        response = client.get(
            "/api/v1/study-timer/timers",
            headers=mock_auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 2
        # Default timer should be first
        assert data[0]["is_default"] == True
    
    def test_update_study_timer(self, client, setup_database, mock_auth_headers):
        """Test updating study timer"""
        # First create a timer
        timer_data = {
            "timer_name": "Test Timer",
            "study_duration": 30,
            "break_duration": 5,
            "long_break_duration": 15,
            "sessions_before_long_break": 4,
            "is_default": False
        }
        
        create_response = client.post(
            "/api/v1/study-timer/timers",
            json=timer_data,
            headers=mock_auth_headers
        )
        
        timer_id = create_response.json()["id"]
        
        # Update the timer
        update_data = {
            "timer_name": "Updated Timer",
            "study_duration": 45,
            "is_default": True
        }
        
        response = client.put(
            f"/api/v1/study-timer/timers/{timer_id}",
            json=update_data,
            headers=mock_auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["timer_name"] == "Updated Timer"
        assert data["study_duration"] == 45
        assert data["is_default"] == True
    
    def test_delete_study_timer(self, client, setup_database, mock_auth_headers):
        """Test deleting study timer"""
        # First create a timer
        timer_data = {
            "timer_name": "Delete Test Timer",
            "study_duration": 20,
            "break_duration": 5,
            "long_break_duration": 15,
            "sessions_before_long_break": 4,
            "is_default": False
        }
        
        create_response = client.post(
            "/api/v1/study-timer/timers",
            json=timer_data,
            headers=mock_auth_headers
        )
        
        timer_id = create_response.json()["id"]
        
        # Delete the timer
        response = client.delete(
            f"/api/v1/study-timer/timers/{timer_id}",
            headers=mock_auth_headers
        )
        
        assert response.status_code == 200
        assert response.json() == True
        
        # Verify timer is deleted
        get_response = client.get(
            f"/api/v1/study-timer/timers/{timer_id}",
            headers=mock_auth_headers
        )
        
        assert get_response.status_code == 404

class TestStudyStatistics:
    """Test study statistics endpoints"""
    
    def test_get_study_stats(self, client, setup_database, mock_auth_headers):
        """Test getting study statistics"""
        # Create some completed sessions
        sessions_data = [
            {
                "subject": "Mathematics",
                "topic": "Algebra",
                "session_type": "study",
                "planned_duration": 30,
                "goals": ["Solve equations"],
                "device_type": "web"
            },
            {
                "subject": "Physics",
                "topic": "Mechanics",
                "session_type": "practice",
                "planned_duration": 45,
                "goals": ["Practice problems"],
                "device_type": "web"
            }
        ]
        
        for session_data in sessions_data:
            start_response = client.post(
                "/api/v1/study-timer/sessions",
                json=session_data,
                headers=mock_auth_headers
            )
            
            session_id = start_response.json()["id"]
            
            # Complete the session
            completion_data = {
                "notes": "Good session",
                "completed_goals": ["Goal completed"],
                "focus_rating": 4,
                "productivity_rating": 4,
                "difficulty_rating": 3
            }
            
            client.post(
                f"/api/v1/study-timer/sessions/{session_id}/complete",
                json=completion_data,
                headers=mock_auth_headers
            )
        
        # Get statistics
        response = client.get(
            "/api/v1/study-timer/stats",
            headers=mock_auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "total_sessions" in data
        assert "total_study_time" in data
        assert "average_session_length" in data
        assert "completion_rate" in data
        assert "focus_rating_avg" in data
        assert "productivity_rating_avg" in data
        assert "study_streak" in data
        assert "weekly_goal_progress" in data
        assert "monthly_goal_progress" in data
    
    def test_get_study_stats_by_period(self, client, setup_database, mock_auth_headers):
        """Test getting study statistics for different periods"""
        periods = ["day", "week", "month", "year"]
        
        for period in periods:
            response = client.get(
                f"/api/v1/study-timer/stats?period={period}",
                headers=mock_auth_headers
            )
            
            assert response.status_code == 200
            data = response.json()
            assert "total_sessions" in data
            assert "total_study_time" in data
    
    def test_get_productivity_score(self, client, setup_database, mock_auth_headers):
        """Test getting productivity score"""
        # Create some completed sessions first
        session_data = {
            "subject": "Chemistry",
            "topic": "Organic Chemistry",
            "session_type": "study",
            "planned_duration": 60,
            "goals": ["Learn organic compounds"],
            "device_type": "web"
        }
        
        start_response = client.post(
            "/api/v1/study-timer/sessions",
            json=session_data,
            headers=mock_auth_headers
        )
        
        session_id = start_response.json()["id"]
        
        completion_data = {
            "notes": "Excellent session",
            "completed_goals": ["Learn organic compounds"],
            "focus_rating": 5,
            "productivity_rating": 5,
            "difficulty_rating": 4
        }
        
        client.post(
            f"/api/v1/study-timer/sessions/{session_id}/complete",
            json=completion_data,
            headers=mock_auth_headers
        )
        
        # Get productivity score
        response = client.get(
            "/api/v1/study-timer/productivity-score",
            headers=mock_auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, float)
        assert 0 <= data <= 100
    
    def test_get_productivity_insights(self, client, setup_database, mock_auth_headers):
        """Test getting productivity insights"""
        # Create some sessions first
        sessions_data = [
            {
                "subject": "Mathematics",
                "topic": "Calculus",
                "session_type": "study",
                "planned_duration": 30,
                "goals": ["Learn derivatives"],
                "device_type": "web"
            },
            {
                "subject": "Physics",
                "topic": "Quantum Mechanics",
                "session_type": "practice",
                "planned_duration": 45,
                "goals": ["Practice problems"],
                "device_type": "web"
            }
        ]
        
        for session_data in sessions_data:
            start_response = client.post(
                "/api/v1/study-timer/sessions",
                json=session_data,
                headers=mock_auth_headers
            )
            
            session_id = start_response.json()["id"]
            
            completion_data = {
                "notes": "Good progress",
                "completed_goals": ["Goal completed"],
                "focus_rating": 4,
                "productivity_rating": 4,
                "difficulty_rating": 3
            }
            
            client.post(
                f"/api/v1/study-timer/sessions/{session_id}/complete",
                json=completion_data,
                headers=mock_auth_headers
            )
        
        # Get productivity insights
        response = client.get(
            "/api/v1/study-timer/productivity-insights",
            headers=mock_auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "current_streak" in data
        assert "best_streak" in data
        assert "average_daily_study_time" in data
        assert "most_productive_time" in data
        assert "most_productive_subject" in data
        assert "improvement_areas" in data
        assert "recommendations" in data
        assert "weekly_trend" in data

class TestStudyTimerIntegration:
    """Integration tests for study timer features"""
    
    def test_complete_study_workflow(self, client, setup_database, mock_auth_headers):
        """Test complete study workflow"""
        # 1. Create a study timer
        timer_data = {
            "timer_name": "Integration Test Timer",
            "study_duration": 25,
            "break_duration": 5,
            "long_break_duration": 15,
            "sessions_before_long_break": 4,
            "auto_start_breaks": True,
            "auto_start_sessions": False,
            "sound_enabled": True,
            "notifications_enabled": True,
            "is_default": True
        }
        
        timer_response = client.post(
            "/api/v1/study-timer/timers",
            json=timer_data,
            headers=mock_auth_headers
        )
        
        assert timer_response.status_code == 200
        timer_id = timer_response.json()["id"]
        
        # 2. Start a study session
        session_data = {
            "subject": "Computer Science",
            "topic": "Data Structures",
            "session_type": "study",
            "planned_duration": 25,
            "goals": ["Learn about arrays", "Understand linked lists"],
            "notes": "Focus on implementation",
            "device_type": "web"
        }
        
        session_response = client.post(
            "/api/v1/study-timer/sessions",
            json=session_data,
            headers=mock_auth_headers
        )
        
        assert session_response.status_code == 200
        session_id = session_response.json()["id"]
        
        # 3. Pause the session
        pause_response = client.post(
            f"/api/v1/study-timer/sessions/{session_id}/pause",
            headers=mock_auth_headers
        )
        
        assert pause_response.status_code == 200
        assert pause_response.json()["status"] == "paused"
        
        # 4. Resume the session
        resume_response = client.post(
            f"/api/v1/study-timer/sessions/{session_id}/resume",
            headers=mock_auth_headers
        )
        
        assert resume_response.status_code == 200
        assert resume_response.json()["status"] == "active"
        
        # 5. Complete the session
        completion_data = {
            "notes": "Great session, learned a lot",
            "completed_goals": ["Learn about arrays", "Understand linked lists"],
            "focus_rating": 5,
            "productivity_rating": 5,
            "difficulty_rating": 4
        }
        
        complete_response = client.post(
            f"/api/v1/study-timer/sessions/{session_id}/complete",
            json=completion_data,
            headers=mock_auth_headers
        )
        
        assert complete_response.status_code == 200
        assert complete_response.json()["status"] == "completed"
        
        # 6. Get session details
        session_get_response = client.get(
            f"/api/v1/study-timer/sessions/{session_id}",
            headers=mock_auth_headers
        )
        
        assert session_get_response.status_code == 200
        session_data_retrieved = session_get_response.json()
        assert session_data_retrieved["status"] == "completed"
        assert session_data_retrieved["focus_rating"] == 5
        assert session_data_retrieved["productivity_rating"] == 5
        
        # 7. Get study statistics
        stats_response = client.get(
            "/api/v1/study-timer/stats",
            headers=mock_auth_headers
        )
        
        assert stats_response.status_code == 200
        stats_data = stats_response.json()
        assert stats_data["total_sessions"] >= 1
        assert stats_data["total_study_time"] > 0
        
        # 8. Get productivity insights
        insights_response = client.get(
            "/api/v1/study-timer/productivity-insights",
            headers=mock_auth_headers
        )
        
        assert insights_response.status_code == 200
        insights_data = insights_response.json()
        assert "current_streak" in insights_data
        assert "recommendations" in insights_data
        
        # 9. Verify timer data
        timer_get_response = client.get(
            f"/api/v1/study-timer/timers/{timer_id}",
            headers=mock_auth_headers
        )
        
        assert timer_get_response.status_code == 200
        timer_data_retrieved = timer_get_response.json()
        assert timer_data_retrieved["timer_name"] == "Integration Test Timer"
        assert timer_data_retrieved["is_default"] == True

class TestStudyTimerValidation:
    """Test validation rules for study timer data"""
    
    def test_session_validation_rules(self, client, setup_database, mock_auth_headers):
        """Test validation rules for session data"""
        # Test invalid session type
        session_data = {
            "subject": "Mathematics",
            "session_type": "invalid_type",
            "planned_duration": 30,
            "goals": ["Learn math"],
            "device_type": "web"
        }
        
        response = client.post(
            "/api/v1/study-timer/sessions",
            json=session_data,
            headers=mock_auth_headers
        )
        
        assert response.status_code == 422
        
        # Test too many goals
        session_data["session_type"] = "study"
        session_data["goals"] = [f"Goal {i}" for i in range(10)]
        
        response = client.post(
            "/api/v1/study-timer/sessions",
            json=session_data,
            headers=mock_auth_headers
        )
        
        assert response.status_code == 422
        
        # Test invalid device type
        session_data["goals"] = ["Learn math"]
        session_data["device_type"] = "invalid_device"
        
        response = client.post(
            "/api/v1/study-timer/sessions",
            json=session_data,
            headers=mock_auth_headers
        )
        
        assert response.status_code == 422
    
    def test_timer_validation_rules(self, client, setup_database, mock_auth_headers):
        """Test validation rules for timer data"""
        # Test empty timer name
        timer_data = {
            "timer_name": "",
            "study_duration": 25,
            "break_duration": 5,
            "long_break_duration": 15,
            "sessions_before_long_break": 4
        }
        
        response = client.post(
            "/api/v1/study-timer/timers",
            json=timer_data,
            headers=mock_auth_headers
        )
        
        assert response.status_code == 422
        
        # Test invalid durations
        timer_data["timer_name"] = "Test Timer"
        timer_data["study_duration"] = 200  # Too long
        
        response = client.post(
            "/api/v1/study-timer/timers",
            json=timer_data,
            headers=mock_auth_headers
        )
        
        assert response.status_code == 422
        
        # Test invalid sessions before long break
        timer_data["study_duration"] = 25
        timer_data["sessions_before_long_break"] = 15  # Too many
        
        response = client.post(
            "/api/v1/study-timer/timers",
            json=timer_data,
            headers=mock_auth_headers
        )
        
        assert response.status_code == 422
