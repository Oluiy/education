# 🚀 EduNerve Implementation Plan - Priority 1

## 📋 **WHAT TO IMPLEMENT FIRST (2-3 weeks)**

### **Week 1: Personalization & Study Timer APIs**

#### **Day 1-2: Personalization Quiz API**
**Files to create/modify:**
1. `services/content-quiz-service/app/schemas/personalization.py`
2. `services/content-quiz-service/app/models/content_models.py` (add PersonalizationQuiz model)
3. `services/content-quiz-service/app/services/personalization_service.py`
4. `services/content-quiz-service/app/main.py` (add router)

**Key Features:**
- Student learning style assessment
- Subject preference collection
- Difficulty level preferences
- Study time preferences
- Learning resource preferences

#### **Day 3-4: Study Timer API**
**Files to create/modify:**
1. `services/content-quiz-service/app/schemas/study_timer.py`
2. `services/content-quiz-service/app/models/content_models.py` (add StudySession model)
3. `services/content-quiz-service/app/services/study_timer_service.py`
4. `services/content-quiz-service/app/main.py` (add router)

**Key Features:**
- Study session tracking
- Pomodoro timer integration
- Session analytics
- Productivity scoring
- Study streak tracking

#### **Day 5-7: Database Migrations & Testing**
- Create database migrations
- Add indexes for performance
- Write unit tests
- Integration testing

### **Week 2: Smart Assistant API**

#### **Day 1-3: Smart Assistant Core**
**Files to create/modify:**
1. `services/assistant-service/app/schemas/assistant.py`
2. `services/assistant-service/app/models/assistant_models.py`
3. `services/assistant-service/app/services/assistant_service.py`
4. `services/assistant-service/app/main.py` (add router)

**Key Features:**
- AI chat interface
- Learning recommendations
- YouTube video suggestions
- Audio summary generation
- Practice quiz generation

#### **Day 4-5: AI Integration**
- OpenAI GPT-4 integration
- YouTube API integration
- Text-to-speech integration
- Recommendation algorithms

#### **Day 6-7: Testing & Optimization**
- API testing
- Performance optimization
- Error handling
- Rate limiting

### **Week 3: Enhanced Content API & Integration**

#### **Day 1-2: Content Viewer Enhancement**
**Files to modify:**
1. `services/content-quiz-service/app/api/content.py` (enhance existing)
2. `services/content-quiz-service/app/services/content_service.py`

**Key Features:**
- Content streaming
- Progress tracking
- Annotations support
- Offline content caching

#### **Day 3-4: API Gateway Integration**
**Files to modify:**
1. `api-gateway/app/main.py` (add new routes)
2. `api-gateway/app/routes.py` (add proxy routes)

#### **Day 5-7: Frontend Integration & Testing**
- Update frontend to use new APIs
- End-to-end testing
- Performance testing
- Bug fixes

## 🛠️ **IMPLEMENTATION STEPS**

### **Step 1: Create Database Models**

```python
# services/content-quiz-service/app/models/content_models.py

class PersonalizationQuiz(Base):
    __tablename__ = "personalization_quizzes"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    school_id = Column(Integer, ForeignKey("schools.id"))
    
    # Quiz responses
    learning_style = Column(String(50))  # visual, auditory, kinesthetic
    preferred_subjects = Column(JSON)
    difficulty_preference = Column(String(20))  # easy, medium, hard
    study_time_preference = Column(String(20))  # morning, afternoon, evening
    resource_preferences = Column(JSON)  # video, text, audio, interactive
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class StudySession(Base):
    __tablename__ = "study_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    school_id = Column(Integer, ForeignKey("schools.id"))
    
    # Session details
    subject = Column(String(100))
    topic = Column(String(200))
    start_time = Column(DateTime, default=datetime.utcnow)
    end_time = Column(DateTime)
    duration_minutes = Column(Integer)
    status = Column(String(20))  # active, paused, completed
    
    # Session data
    notes = Column(Text)
    goals_achieved = Column(Boolean, default=False)
    productivity_score = Column(Float)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
```

### **Step 2: Create Schemas**

```python
# services/content-quiz-service/app/schemas/personalization.py

from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime

class PersonalizationQuizCreate(BaseModel):
    learning_style: str
    preferred_subjects: List[str]
    difficulty_preference: str
    study_time_preference: str
    resource_preferences: Dict[str, bool]

class PersonalizationQuizResponse(BaseModel):
    id: int
    user_id: int
    learning_style: str
    preferred_subjects: List[str]
    difficulty_preference: str
    study_time_preference: str
    resource_preferences: Dict[str, bool]
    created_at: datetime
    
    class Config:
        from_attributes = True

class StudentPreferencesCreate(BaseModel):
    quiz_id: int
    additional_preferences: Dict[str, Any]

class StudentPreferencesResponse(BaseModel):
    id: int
    user_id: int
    quiz_id: int
    preferences: Dict[str, Any]
    created_at: datetime
    
    class Config:
        from_attributes = True

class LearningRecommendation(BaseModel):
    type: str  # video, quiz, content, practice
    title: str
    description: str
    url: Optional[str]
    subject: str
    topic: str
    difficulty: str
    estimated_time: int  # minutes
    confidence_score: float

class RecommendationRequest(BaseModel):
    subject: Optional[str] = None
    topic: Optional[str] = None
    limit: int = 10
```

### **Step 3: Create Services**

```python
# services/content-quiz-service/app/services/personalization_service.py

from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from ..models.content_models import PersonalizationQuiz, StudentPreferences
from ..schemas.personalization import PersonalizationQuizCreate, StudentPreferencesCreate
from ..auth import CurrentUser
import logging

logger = logging.getLogger(__name__)

class PersonalizationService:
    async def create_quiz(
        self,
        quiz_data: PersonalizationQuizCreate,
        current_user: CurrentUser,
        db: Session
    ) -> PersonalizationQuiz:
        """Create a new personalization quiz"""
        try:
            quiz = PersonalizationQuiz(
                user_id=current_user.user_id,
                school_id=current_user.school_id,
                learning_style=quiz_data.learning_style,
                preferred_subjects=quiz_data.preferred_subjects,
                difficulty_preference=quiz_data.difficulty_preference,
                study_time_preference=quiz_data.study_time_preference,
                resource_preferences=quiz_data.resource_preferences
            )
            
            db.add(quiz)
            db.commit()
            db.refresh(quiz)
            
            return quiz
            
        except Exception as e:
            db.rollback()
            logger.error(f"Error creating personalization quiz: {str(e)}")
            raise
    
    async def get_recommendations(
        self,
        request: RecommendationRequest,
        current_user: CurrentUser,
        db: Session
    ) -> List[LearningRecommendation]:
        """Get personalized learning recommendations"""
        try:
            # Get user preferences
            preferences = db.query(PersonalizationQuiz).filter(
                PersonalizationQuiz.user_id == current_user.user_id
            ).first()
            
            if not preferences:
                return []
            
            # Generate recommendations based on preferences
            recommendations = []
            
            # Example recommendation logic
            if preferences.resource_preferences.get("video", False):
                recommendations.append(LearningRecommendation(
                    type="video",
                    title="Introduction to Mathematics",
                    description="Learn basic mathematical concepts",
                    url="https://youtube.com/watch?v=example",
                    subject="Mathematics",
                    topic="Basic Concepts",
                    difficulty=preferences.difficulty_preference,
                    estimated_time=15,
                    confidence_score=0.8
                ))
            
            return recommendations[:request.limit]
            
        except Exception as e:
            logger.error(f"Error getting recommendations: {str(e)}")
            raise
```

### **Step 4: Update Main Application**

```python
# services/content-quiz-service/app/main.py

# Add these imports
from .api import personalization, study_timer

# Add these routers
app.include_router(personalization.router, prefix="/api/v1")
app.include_router(study_timer.router, prefix="/api/v1")
```

## 🧪 **TESTING STRATEGY**

### **Unit Tests**
```python
# tests/test_personalization.py

import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_create_personalization_quiz():
    response = client.post(
        "/api/v1/personalization/quiz",
        json={
            "learning_style": "visual",
            "preferred_subjects": ["Mathematics", "Physics"],
            "difficulty_preference": "medium",
            "study_time_preference": "morning",
            "resource_preferences": {
                "video": True,
                "text": False,
                "audio": True,
                "interactive": True
            }
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["learning_style"] == "visual"
```

### **Integration Tests**
```python
# tests/test_integration.py

def test_complete_student_workflow():
    # 1. Create personalization quiz
    # 2. Start study session
    # 3. Get recommendations
    # 4. Complete study session
    # 5. Verify analytics
    pass
```

## 📊 **SUCCESS METRICS**

### **API Performance**
- Response time < 200ms for all endpoints
- 99.9% uptime
- < 1% error rate

### **User Engagement**
- 80% of students complete personalization quiz
- 70% use study timer regularly
- 60% engage with AI assistant

### **Learning Outcomes**
- 15% improvement in quiz scores
- 20% increase in study time
- 25% better retention rates

## 🚀 **DEPLOYMENT CHECKLIST**

### **Before Deployment**
- [ ] All unit tests passing
- [ ] Integration tests passing
- [ ] Database migrations ready
- [ ] Environment variables configured
- [ ] API documentation updated

### **After Deployment**
- [ ] Health checks passing
- [ ] Performance monitoring active
- [ ] Error tracking configured
- [ ] User feedback collected
- [ ] Analytics tracking working

## 💡 **NEXT STEPS AFTER WEEK 3**

1. **Production Environment Setup** (Week 4)
2. **Mobile App Development** (Week 5-8)
3. **African Market Features** (Week 9-12)
4. **Payment Integration** (Week 13-16)

---

**Estimated Time: 2-3 weeks**
**Priority: HIGH**
**Impact: CRITICAL for student experience**
