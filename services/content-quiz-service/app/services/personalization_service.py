"""
Personalization Service
Business logic for personalization quiz and student preferences management
"""

from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, desc
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import logging
import json

from ..models.content_models import PersonalizationQuiz, StudentPreferences
from ..schemas.personalization import (
    PersonalizationQuizCreate, PersonalizationQuizUpdate,
    StudentPreferencesCreate, StudentPreferencesUpdate,
    LearningRecommendation, RecommendationRequest,
    LearningStyleAnalysis, WeakAreasAnalysis, PersonalizationSummary
)
from ..auth import CurrentUser

logger = logging.getLogger(__name__)

class PersonalizationService:
    """Service for managing personalization quiz and student preferences"""
    
    async def create_quiz(
        self,
        quiz_data: PersonalizationQuizCreate,
        current_user: CurrentUser,
        db: Session
    ) -> PersonalizationQuiz:
        """Create a new personalization quiz for a student"""
        try:
            # Check if user already has a quiz
            existing_quiz = db.query(PersonalizationQuiz).filter(
                PersonalizationQuiz.user_id == current_user.user_id
            ).first()
            
            if existing_quiz:
                # Update existing quiz
                for field, value in quiz_data.dict().items():
                    setattr(existing_quiz, field, value)
                existing_quiz.updated_at = datetime.utcnow()
                
                # Generate analysis and recommendations
                analysis = await self._analyze_learning_style(quiz_data)
                recommendations = await self._generate_recommendations(quiz_data, analysis)
                
                existing_quiz.learning_style_analysis = analysis
                existing_quiz.recommendations = recommendations
                
                db.commit()
                db.refresh(existing_quiz)
                return existing_quiz
            
            # Create new quiz
            quiz = PersonalizationQuiz(
                user_id=current_user.user_id,
                school_id=current_user.school_id,
                learning_style=quiz_data.learning_style.value,
                preferred_subjects=quiz_data.preferred_subjects,
                difficulty_preference=quiz_data.difficulty_preference.value,
                study_time_preference=quiz_data.study_time_preference.value,
                resource_preferences=quiz_data.resource_preferences,
                study_goals=quiz_data.study_goals,
                target_score=quiz_data.target_score,
                study_hours_per_day=quiz_data.study_hours_per_day,
                preferred_session_duration=quiz_data.preferred_session_duration
            )
            
            # Generate analysis and recommendations
            analysis = await self._analyze_learning_style(quiz_data)
            recommendations = await self._generate_recommendations(quiz_data, analysis)
            
            quiz.learning_style_analysis = analysis
            quiz.recommendations = recommendations
            
            db.add(quiz)
            db.commit()
            db.refresh(quiz)
            
            return quiz
            
        except Exception as e:
            db.rollback()
            logger.error(f"Error creating personalization quiz: {str(e)}")
            raise
    
    async def get_quiz(
        self,
        quiz_id: int,
        current_user: CurrentUser,
        db: Session
    ) -> Optional[PersonalizationQuiz]:
        """Get a specific personalization quiz"""
        try:
            quiz = db.query(PersonalizationQuiz).filter(
                and_(
                    PersonalizationQuiz.id == quiz_id,
                    PersonalizationQuiz.user_id == current_user.user_id
                )
            ).first()
            
            return quiz
            
        except Exception as e:
            logger.error(f"Error getting personalization quiz: {str(e)}")
            raise
    
    async def get_user_quiz(
        self,
        current_user: CurrentUser,
        db: Session
    ) -> Optional[PersonalizationQuiz]:
        """Get user's personalization quiz"""
        try:
            quiz = db.query(PersonalizationQuiz).filter(
                PersonalizationQuiz.user_id == current_user.user_id
            ).first()
            
            return quiz
            
        except Exception as e:
            logger.error(f"Error getting user quiz: {str(e)}")
            raise
    
    async def update_quiz(
        self,
        quiz_id: int,
        quiz_data: PersonalizationQuizUpdate,
        current_user: CurrentUser,
        db: Session
    ) -> Optional[PersonalizationQuiz]:
        """Update a personalization quiz"""
        try:
            quiz = await self.get_quiz(quiz_id, current_user, db)
            if not quiz:
                return None
            
            # Update fields
            update_data = quiz_data.dict(exclude_unset=True)
            for field, value in update_data.items():
                setattr(quiz, field, value)
            
            quiz.updated_at = datetime.utcnow()
            
            # Regenerate analysis if learning style changed
            if 'learning_style' in update_data:
                analysis = await self._analyze_learning_style(quiz_data)
                recommendations = await self._generate_recommendations(quiz_data, analysis)
                quiz.learning_style_analysis = analysis
                quiz.recommendations = recommendations
            
            db.commit()
            db.refresh(quiz)
            
            return quiz
            
        except Exception as e:
            db.rollback()
            logger.error(f"Error updating personalization quiz: {str(e)}")
            raise
    
    async def save_preferences(
        self,
        preferences: StudentPreferencesCreate,
        current_user: CurrentUser,
        db: Session
    ) -> StudentPreferences:
        """Save student learning preferences"""
        try:
            # Check if user already has preferences
            existing_prefs = db.query(StudentPreferences).filter(
                StudentPreferences.user_id == current_user.user_id
            ).first()
            
            if existing_prefs:
                # Update existing preferences
                for field, value in preferences.dict().items():
                    setattr(existing_prefs, field, value)
                existing_prefs.updated_at = datetime.utcnow()
                
                db.commit()
                db.refresh(existing_prefs)
                return existing_prefs
            
            # Create new preferences
            prefs = StudentPreferences(
                user_id=current_user.user_id,
                school_id=current_user.school_id,
                preferred_learning_methods=preferences.preferred_learning_methods,
                difficulty_level=preferences.difficulty_level.value,
                study_pace=preferences.study_pace,
                preferred_content_types=[ct.value for ct in preferences.preferred_content_types],
                auto_play_videos=preferences.auto_play_videos,
                show_transcripts=preferences.show_transcripts,
                enable_audio_summaries=preferences.enable_audio_summaries,
                preferred_study_times=preferences.preferred_study_times,
                session_duration=preferences.session_duration,
                break_duration=preferences.break_duration,
                daily_study_goal=preferences.daily_study_goal,
                text_to_speech_enabled=preferences.text_to_speech_enabled,
                large_text_mode=preferences.large_text_mode,
                high_contrast_mode=preferences.high_contrast_mode,
                dyslexia_friendly_font=preferences.dyslexia_friendly_font,
                study_reminders=preferences.study_reminders,
                achievement_notifications=preferences.achievement_notifications,
                progress_updates=preferences.progress_updates,
                quiet_hours_start=preferences.quiet_hours_start,
                quiet_hours_end=preferences.quiet_hours_end,
                preferred_language=preferences.preferred_language,
                timezone=preferences.timezone
            )
            
            db.add(prefs)
            db.commit()
            db.refresh(prefs)
            
            return prefs
            
        except Exception as e:
            db.rollback()
            logger.error(f"Error saving student preferences: {str(e)}")
            raise
    
    async def get_preferences(
        self,
        current_user: CurrentUser,
        db: Session
    ) -> Optional[StudentPreferences]:
        """Get current student preferences"""
        try:
            prefs = db.query(StudentPreferences).filter(
                StudentPreferences.user_id == current_user.user_id
            ).first()
            
            return prefs
            
        except Exception as e:
            logger.error(f"Error getting student preferences: {str(e)}")
            raise
    
    async def update_preferences(
        self,
        preferences: StudentPreferencesUpdate,
        current_user: CurrentUser,
        db: Session
    ) -> Optional[StudentPreferences]:
        """Update student preferences"""
        try:
            prefs = await self.get_preferences(current_user, db)
            if not prefs:
                return None
            
            # Update fields
            update_data = preferences.dict(exclude_unset=True)
            for field, value in update_data.items():
                if field == 'preferred_content_types' and value:
                    value = [ct.value for ct in value]
                setattr(prefs, field, value)
            
            prefs.updated_at = datetime.utcnow()
            
            db.commit()
            db.refresh(prefs)
            
            return prefs
            
        except Exception as e:
            db.rollback()
            logger.error(f"Error updating student preferences: {str(e)}")
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
            quiz = await self.get_user_quiz(current_user, db)
            prefs = await self.get_preferences(current_user, db)
            
            if not quiz:
                return []
            
            recommendations = []
            
            # Generate recommendations based on preferences
            if quiz.resource_preferences.get("video", False):
                recommendations.extend(await self._get_video_recommendations(quiz, request))
            
            if quiz.resource_preferences.get("text", False):
                recommendations.extend(await self._get_text_recommendations(quiz, request))
            
            if quiz.resource_preferences.get("audio", False):
                recommendations.extend(await self._get_audio_recommendations(quiz, request))
            
            if quiz.resource_preferences.get("interactive", False):
                recommendations.extend(await self._get_interactive_recommendations(quiz, request))
            
            if quiz.resource_preferences.get("practice", False):
                recommendations.extend(await self._get_practice_recommendations(quiz, request))
            
            # Sort by confidence score and limit results
            recommendations.sort(key=lambda x: x.confidence_score, reverse=True)
            return recommendations[:request.limit]
            
        except Exception as e:
            logger.error(f"Error getting recommendations: {str(e)}")
            raise
    
    async def analyze_learning_style(
        self,
        current_user: CurrentUser,
        db: Session
    ) -> Optional[LearningStyleAnalysis]:
        """Analyze student's learning style"""
        try:
            quiz = await self.get_user_quiz(current_user, db)
            if not quiz:
                return None
            
            # Calculate style percentages based on preferences
            style_percentages = {
                "visual": 0.0,
                "auditory": 0.0,
                "kinesthetic": 0.0,
                "reading_writing": 0.0
            }
            
            # Analyze based on resource preferences
            if quiz.resource_preferences.get("video", False):
                style_percentages["visual"] += 30
            if quiz.resource_preferences.get("audio", False):
                style_percentages["auditory"] += 30
            if quiz.resource_preferences.get("interactive", False):
                style_percentages["kinesthetic"] += 25
            if quiz.resource_preferences.get("text", False):
                style_percentages["reading_writing"] += 25
            
            # Determine primary and secondary styles
            sorted_styles = sorted(style_percentages.items(), key=lambda x: x[1], reverse=True)
            primary_style = sorted_styles[0][0]
            secondary_style = sorted_styles[1][0] if sorted_styles[1][1] > 0 else None
            
            # Generate recommendations
            recommendations = await self._get_style_recommendations(primary_style)
            strengths = await self._get_style_strengths(primary_style)
            areas_for_improvement = await self._get_style_improvements(primary_style)
            
            return LearningStyleAnalysis(
                primary_style=primary_style,
                secondary_style=secondary_style,
                style_percentages=style_percentages,
                recommendations=recommendations,
                strengths=strengths,
                areas_for_improvement=areas_for_improvement
            )
            
        except Exception as e:
            logger.error(f"Error analyzing learning style: {str(e)}")
            raise
    
    async def identify_weak_areas(
        self,
        current_user: CurrentUser,
        db: Session
    ) -> List[WeakAreasAnalysis]:
        """Identify student's weak areas based on performance"""
        try:
            # This would typically integrate with quiz performance data
            # For now, return mock data based on preferences
            quiz = await self.get_user_quiz(current_user, db)
            if not quiz:
                return []
            
            weak_areas = []
            
            # Mock weak areas based on preferred subjects
            for subject in quiz.preferred_subjects[:3]:  # Top 3 subjects
                weak_areas.append(WeakAreasAnalysis(
                    subject=subject,
                    topic=f"Advanced {subject}",
                    performance_score=65.0,  # Mock score
                    difficulty_level="medium",
                    recommended_resources=[],
                    study_suggestions=[
                        f"Focus on {subject} fundamentals",
                        f"Practice {subject} problems daily",
                        f"Review {subject} concepts weekly"
                    ]
                ))
            
            return weak_areas
            
        except Exception as e:
            logger.error(f"Error identifying weak areas: {str(e)}")
            raise
    
    async def get_personalization_summary(
        self,
        current_user: CurrentUser,
        db: Session
    ) -> PersonalizationSummary:
        """Get personalization summary for user"""
        try:
            quiz = await self.get_user_quiz(current_user, db)
            
            return PersonalizationSummary(
                quiz_completed=quiz is not None,
                learning_style=quiz.learning_style if quiz else None,
                preferred_subjects=quiz.preferred_subjects if quiz else [],
                difficulty_preference=quiz.difficulty_preference if quiz else None,
                study_time_preference=quiz.study_time_preference if quiz else None,
                resource_preferences=quiz.resource_preferences if quiz else {},
                recommendations_count=len(quiz.recommendations) if quiz and quiz.recommendations else 0,
                last_updated=quiz.updated_at if quiz else None
            )
            
        except Exception as e:
            logger.error(f"Error getting personalization summary: {str(e)}")
            raise
    
    # Private helper methods
    
    async def _analyze_learning_style(self, quiz_data: PersonalizationQuizCreate) -> Dict[str, Any]:
        """Analyze learning style from quiz data"""
        # Mock analysis - in production, this would use ML models
        return {
            "primary_style": quiz_data.learning_style.value,
            "confidence": 0.85,
            "characteristics": [
                "Prefers visual learning materials",
                "Learns best through observation",
                "Enjoys diagrams and charts"
            ] if quiz_data.learning_style.value == "visual" else [
                "Prefers audio learning materials",
                "Learns best through listening",
                "Enjoys discussions and explanations"
            ]
        }
    
    async def _generate_recommendations(
        self,
        quiz_data: PersonalizationQuizCreate,
        analysis: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Generate personalized recommendations"""
        recommendations = []
        
        # Generate recommendations based on learning style
        if quiz_data.learning_style.value == "visual":
            recommendations.append({
                "type": "video",
                "title": "Visual Learning Resources",
                "description": "Curated video content for visual learners",
                "confidence": 0.9
            })
        
        # Generate recommendations based on subjects
        for subject in quiz_data.preferred_subjects:
            recommendations.append({
                "type": "content",
                "title": f"{subject} Study Materials",
                "description": f"Personalized {subject} content",
                "subject": subject,
                "confidence": 0.8
            })
        
        return recommendations
    
    async def _get_video_recommendations(
        self,
        quiz: PersonalizationQuiz,
        request: RecommendationRequest
    ) -> List[LearningRecommendation]:
        """Get video recommendations"""
        recommendations = []
        
        for subject in quiz.preferred_subjects:
            if not request.subject or request.subject.lower() == subject.lower():
                recommendations.append(LearningRecommendation(
                    type="video",
                    title=f"Introduction to {subject}",
                    description=f"Learn {subject} fundamentals through video",
                    url=f"https://youtube.com/watch?v={subject.lower()}_intro",
                    subject=subject,
                    topic="Introduction",
                    difficulty=quiz.difficulty_preference,
                    estimated_time=15,
                    confidence_score=0.85
                ))
        
        return recommendations
    
    async def _get_text_recommendations(
        self,
        quiz: PersonalizationQuiz,
        request: RecommendationRequest
    ) -> List[LearningRecommendation]:
        """Get text-based recommendations"""
        recommendations = []
        
        for subject in quiz.preferred_subjects:
            if not request.subject or request.subject.lower() == subject.lower():
                recommendations.append(LearningRecommendation(
                    type="text",
                    title=f"{subject} Study Guide",
                    description=f"Comprehensive {subject} study materials",
                    subject=subject,
                    topic="Study Guide",
                    difficulty=quiz.difficulty_preference,
                    estimated_time=30,
                    confidence_score=0.8
                ))
        
        return recommendations
    
    async def _get_audio_recommendations(
        self,
        quiz: PersonalizationQuiz,
        request: RecommendationRequest
    ) -> List[LearningRecommendation]:
        """Get audio recommendations"""
        recommendations = []
        
        for subject in quiz.preferred_subjects:
            if not request.subject or request.subject.lower() == subject.lower():
                recommendations.append(LearningRecommendation(
                    type="audio",
                    title=f"{subject} Audio Summary",
                    description=f"Audio summary of {subject} concepts",
                    subject=subject,
                    topic="Audio Summary",
                    difficulty=quiz.difficulty_preference,
                    estimated_time=10,
                    confidence_score=0.75
                ))
        
        return recommendations
    
    async def _get_interactive_recommendations(
        self,
        quiz: PersonalizationQuiz,
        request: RecommendationRequest
    ) -> List[LearningRecommendation]:
        """Get interactive recommendations"""
        recommendations = []
        
        for subject in quiz.preferred_subjects:
            if not request.subject or request.subject.lower() == subject.lower():
                recommendations.append(LearningRecommendation(
                    type="interactive",
                    title=f"{subject} Interactive Quiz",
                    description=f"Test your {subject} knowledge",
                    subject=subject,
                    topic="Practice Quiz",
                    difficulty=quiz.difficulty_preference,
                    estimated_time=20,
                    confidence_score=0.9
                ))
        
        return recommendations
    
    async def _get_practice_recommendations(
        self,
        quiz: PersonalizationQuiz,
        request: RecommendationRequest
    ) -> List[LearningRecommendation]:
        """Get practice recommendations"""
        recommendations = []
        
        for subject in quiz.preferred_subjects:
            if not request.subject or request.subject.lower() == subject.lower():
                recommendations.append(LearningRecommendation(
                    type="practice",
                    title=f"{subject} Practice Problems",
                    description=f"Practice {subject} problems with solutions",
                    subject=subject,
                    topic="Practice Problems",
                    difficulty=quiz.difficulty_preference,
                    estimated_time=25,
                    confidence_score=0.85
                ))
        
        return recommendations
    
    async def _get_style_recommendations(self, style: str) -> List[str]:
        """Get recommendations for learning style"""
        recommendations = {
            "visual": [
                "Use diagrams and charts",
                "Watch educational videos",
                "Create mind maps",
                "Use color coding"
            ],
            "auditory": [
                "Listen to audio summaries",
                "Participate in discussions",
                "Read aloud",
                "Use verbal mnemonics"
            ],
            "kinesthetic": [
                "Use hands-on activities",
                "Take frequent breaks",
                "Use physical objects",
                "Practice with real examples"
            ],
            "reading_writing": [
                "Take detailed notes",
                "Read extensively",
                "Write summaries",
                "Use lists and bullet points"
            ]
        }
        
        return recommendations.get(style, [])
    
    async def _get_style_strengths(self, style: str) -> List[str]:
        """Get strengths for learning style"""
        strengths = {
            "visual": [
                "Excellent spatial awareness",
                "Good at recognizing patterns",
                "Strong visual memory"
            ],
            "auditory": [
                "Excellent listening skills",
                "Good at verbal communication",
                "Strong auditory memory"
            ],
            "kinesthetic": [
                "Excellent hands-on skills",
                "Good at physical activities",
                "Strong muscle memory"
            ],
            "reading_writing": [
                "Excellent reading comprehension",
                "Good at written communication",
                "Strong analytical skills"
            ]
        }
        
        return strengths.get(style, [])
    
    async def _get_style_improvements(self, style: str) -> List[str]:
        """Get improvement areas for learning style"""
        improvements = {
            "visual": [
                "Practice verbal explanations",
                "Try audio learning materials",
                "Engage in discussions"
            ],
            "auditory": [
                "Practice visual note-taking",
                "Use diagrams and charts",
                "Create visual summaries"
            ],
            "kinesthetic": [
                "Practice focused reading",
                "Use visual learning materials",
                "Develop concentration skills"
            ],
            "reading_writing": [
                "Practice verbal communication",
                "Use hands-on activities",
                "Engage in group discussions"
            ]
        }
        
        return improvements.get(style, [])
