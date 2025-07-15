"""
Assistant Service - Core orchestration logic for personalized student assistance
"""

import asyncio
import json
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from .models import StudyPlan, StudyResource, StudentActivity, LearningAnalytics
from .schemas import (
    StudyPlanCreate, StudyResourceCreate, StudyResourceRequest,
    StudyPlanResponse, StudyResourceResponse
)
from .ai_service import AIService
from .audio_service import AudioService
from .youtube_service import YouTubeService
from .database import get_db

logger = logging.getLogger(__name__)

class AssistantService:
    """Main orchestration service for student assistance"""
    
    def __init__(self):
        self.ai_service = AIService()
        self.audio_service = AudioService()
        self.youtube_service = YouTubeService()
    
    async def generate_study_plan(
        self, 
        user_id: int, 
        school_id: int, 
        subject: str, 
        grade_level: str, 
        learning_objectives: List[str],
        duration_weeks: int = 4,
        db: Session = None
    ) -> StudyPlanResponse:
        """Generate a personalized study plan for a student"""
        try:
            # Get student's learning analytics
            analytics = self._get_student_analytics(user_id, school_id, db)
            
            # Generate study plan using AI
            plan_data = await self.ai_service.generate_study_plan(
                subject=subject,
                grade_level=grade_level,
                learning_objectives=learning_objectives,
                duration_weeks=duration_weeks,
                student_performance=analytics
            )
            
            # Create study plan in database
            study_plan = StudyPlan(
                user_id=user_id,
                school_id=school_id,
                title=plan_data.get('title', f"{subject} Study Plan"),
                subject=subject,
                grade_level=grade_level,
                learning_objectives=learning_objectives,
                duration_weeks=duration_weeks,
                plan_content=plan_data,
                status='active',
                created_at=datetime.utcnow()
            )
            
            db.add(study_plan)
            db.commit()
            db.refresh(study_plan)
            
            # Generate initial resources for the first week
            await self._generate_initial_resources(study_plan, db)
            
            return StudyPlanResponse(
                id=study_plan.id,
                title=study_plan.title,
                subject=study_plan.subject,
                grade_level=study_plan.grade_level,
                learning_objectives=study_plan.learning_objectives,
                duration_weeks=study_plan.duration_weeks,
                plan_content=study_plan.plan_content,
                status=study_plan.status,
                created_at=study_plan.created_at,
                updated_at=study_plan.updated_at
            )
            
        except Exception as e:
            logger.error(f"Error generating study plan: {str(e)}")
            raise
    
    async def generate_study_resources(
        self, 
        request: StudyResourceRequest, 
        user_id: int, 
        school_id: int,
        db: Session
    ) -> List[StudyResourceResponse]:
        """Generate comprehensive study resources for a topic"""
        try:
            resources = []
            
            # Extract keywords and concepts
            keywords = await self.ai_service.extract_keywords(request.topic)
            
            # Generate different types of resources concurrently
            tasks = [
                self._generate_text_resource(request, keywords, user_id, school_id, db),
                self._generate_video_resources(request, keywords, user_id, school_id, db),
                self._generate_audio_resource(request, user_id, school_id, db),
                self._generate_practice_questions(request, user_id, school_id, db)
            ]
            
            # Wait for all resources to be generated
            generated_resources = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Filter out exceptions and collect successful resources
            for resource_list in generated_resources:
                if isinstance(resource_list, list):
                    resources.extend(resource_list)
                elif not isinstance(resource_list, Exception):
                    resources.append(resource_list)
            
            return resources
            
        except Exception as e:
            logger.error(f"Error generating study resources: {str(e)}")
            raise
    
    async def _generate_text_resource(
        self, 
        request: StudyResourceRequest, 
        keywords: List[str], 
        user_id: int, 
        school_id: int,
        db: Session
    ) -> StudyResourceResponse:
        """Generate text-based study material"""
        try:
            # Generate comprehensive text content
            content = await self.ai_service.generate_study_content(
                topic=request.topic,
                keywords=keywords,
                difficulty_level=request.difficulty_level,
                content_type='text',
                grade_level=request.grade_level
            )
            
            # Create resource in database
            resource = StudyResource(
                user_id=user_id,
                school_id=school_id,
                title=f"Study Notes: {request.topic}",
                content_type='text',
                topic=request.topic,
                subject=request.subject,
                grade_level=request.grade_level,
                difficulty_level=request.difficulty_level,
                content=content,
                keywords=keywords,
                metadata={'generated_by': 'ai', 'content_length': len(content)},
                created_at=datetime.utcnow()
            )
            
            db.add(resource)
            db.commit()
            db.refresh(resource)
            
            return StudyResourceResponse(
                id=resource.id,
                title=resource.title,
                content_type=resource.content_type,
                topic=resource.topic,
                subject=resource.subject,
                grade_level=resource.grade_level,
                difficulty_level=resource.difficulty_level,
                content=resource.content,
                keywords=resource.keywords,
                metadata=resource.metadata,
                created_at=resource.created_at
            )
            
        except Exception as e:
            logger.error(f"Error generating text resource: {str(e)}")
            raise
    
    async def _generate_video_resources(
        self, 
        request: StudyResourceRequest, 
        keywords: List[str], 
        user_id: int, 
        school_id: int,
        db: Session
    ) -> List[StudyResourceResponse]:
        """Generate video-based study resources from YouTube"""
        try:
            # Search for educational videos
            videos = await self.youtube_service.search_educational_videos(
                query=request.topic,
                keywords=keywords,
                max_results=3
            )
            
            resources = []
            for video in videos:
                resource = StudyResource(
                    user_id=user_id,
                    school_id=school_id,
                    title=f"Video: {video['title']}",
                    content_type='video',
                    topic=request.topic,
                    subject=request.subject,
                    grade_level=request.grade_level,
                    difficulty_level=request.difficulty_level,
                    content=video['description'],
                    keywords=keywords,
                    metadata={
                        'video_id': video['id'],
                        'video_url': video['url'],
                        'duration': video['duration'],
                        'channel': video['channel'],
                        'generated_by': 'youtube'
                    },
                    created_at=datetime.utcnow()
                )
                
                db.add(resource)
                resources.append(resource)
            
            db.commit()
            
            return [
                StudyResourceResponse(
                    id=resource.id,
                    title=resource.title,
                    content_type=resource.content_type,
                    topic=resource.topic,
                    subject=resource.subject,
                    grade_level=resource.grade_level,
                    difficulty_level=resource.difficulty_level,
                    content=resource.content,
                    keywords=resource.keywords,
                    metadata=resource.metadata,
                    created_at=resource.created_at
                )
                for resource in resources
            ]
            
        except Exception as e:
            logger.error(f"Error generating video resources: {str(e)}")
            return []
    
    async def _generate_audio_resource(
        self, 
        request: StudyResourceRequest, 
        user_id: int, 
        school_id: int,
        db: Session
    ) -> StudyResourceResponse:
        """Generate audio-based study material"""
        try:
            # Generate audio script
            script = await self.ai_service.generate_audio_script(
                topic=request.topic,
                grade_level=request.grade_level,
                difficulty_level=request.difficulty_level
            )
            
            # Generate audio file
            audio_file = await self.audio_service.generate_audio(
                text=script,
                filename=f"audio_{request.topic.replace(' ', '_').lower()}.mp3"
            )
            
            # Create resource in database
            resource = StudyResource(
                user_id=user_id,
                school_id=school_id,
                title=f"Audio Guide: {request.topic}",
                content_type='audio',
                topic=request.topic,
                subject=request.subject,
                grade_level=request.grade_level,
                difficulty_level=request.difficulty_level,
                content=script,
                keywords=await self.ai_service.extract_keywords(request.topic),
                metadata={
                    'audio_file': audio_file,
                    'script_length': len(script),
                    'generated_by': 'tts'
                },
                created_at=datetime.utcnow()
            )
            
            db.add(resource)
            db.commit()
            db.refresh(resource)
            
            return StudyResourceResponse(
                id=resource.id,
                title=resource.title,
                content_type=resource.content_type,
                topic=resource.topic,
                subject=resource.subject,
                grade_level=resource.grade_level,
                difficulty_level=resource.difficulty_level,
                content=resource.content,
                keywords=resource.keywords,
                metadata=resource.metadata,
                created_at=resource.created_at
            )
            
        except Exception as e:
            logger.error(f"Error generating audio resource: {str(e)}")
            raise
    
    async def _generate_practice_questions(
        self, 
        request: StudyResourceRequest, 
        user_id: int, 
        school_id: int,
        db: Session
    ) -> StudyResourceResponse:
        """Generate practice questions for the topic"""
        try:
            # Generate practice questions
            questions = await self.ai_service.generate_practice_questions(
                topic=request.topic,
                grade_level=request.grade_level,
                difficulty_level=request.difficulty_level,
                question_count=5
            )
            
            # Create resource in database
            resource = StudyResource(
                user_id=user_id,
                school_id=school_id,
                title=f"Practice Questions: {request.topic}",
                content_type='quiz',
                topic=request.topic,
                subject=request.subject,
                grade_level=request.grade_level,
                difficulty_level=request.difficulty_level,
                content=json.dumps(questions),
                keywords=await self.ai_service.extract_keywords(request.topic),
                metadata={
                    'question_count': len(questions),
                    'generated_by': 'ai'
                },
                created_at=datetime.utcnow()
            )
            
            db.add(resource)
            db.commit()
            db.refresh(resource)
            
            return StudyResourceResponse(
                id=resource.id,
                title=resource.title,
                content_type=resource.content_type,
                topic=resource.topic,
                subject=resource.subject,
                grade_level=resource.grade_level,
                difficulty_level=resource.difficulty_level,
                content=resource.content,
                keywords=resource.keywords,
                metadata=resource.metadata,
                created_at=resource.created_at
            )
            
        except Exception as e:
            logger.error(f"Error generating practice questions: {str(e)}")
            raise
    
    async def track_student_activity(
        self, 
        user_id: int, 
        school_id: int, 
        activity_type: str, 
        activity_data: Dict[str, Any],
        db: Session
    ):
        """Track student learning activities"""
        try:
            activity = StudentActivity(
                user_id=user_id,
                school_id=school_id,
                activity_type=activity_type,
                activity_data=activity_data,
                timestamp=datetime.utcnow()
            )
            
            db.add(activity)
            db.commit()
            
            # Update learning analytics
            await self._update_learning_analytics(user_id, school_id, activity_type, activity_data, db)
            
        except Exception as e:
            logger.error(f"Error tracking student activity: {str(e)}")
            raise
    
    def _get_student_analytics(self, user_id: int, school_id: int, db: Session) -> Dict[str, Any]:
        """Get student's learning analytics"""
        try:
            analytics = db.query(LearningAnalytics).filter(
                and_(
                    LearningAnalytics.user_id == user_id,
                    LearningAnalytics.school_id == school_id
                )
            ).first()
            
            if analytics:
                return analytics.analytics_data
            else:
                return {
                    'total_study_time': 0,
                    'subjects_studied': [],
                    'average_quiz_score': 0,
                    'learning_preferences': {},
                    'strength_areas': [],
                    'improvement_areas': []
                }
                
        except Exception as e:
            logger.error(f"Error getting student analytics: {str(e)}")
            return {}
    
    async def _update_learning_analytics(
        self, 
        user_id: int, 
        school_id: int, 
        activity_type: str, 
        activity_data: Dict[str, Any],
        db: Session
    ):
        """Update student's learning analytics based on activity"""
        try:
            analytics = db.query(LearningAnalytics).filter(
                and_(
                    LearningAnalytics.user_id == user_id,
                    LearningAnalytics.school_id == school_id
                )
            ).first()
            
            if not analytics:
                analytics = LearningAnalytics(
                    user_id=user_id,
                    school_id=school_id,
                    analytics_data={
                        'total_study_time': 0,
                        'subjects_studied': [],
                        'average_quiz_score': 0,
                        'learning_preferences': {},
                        'strength_areas': [],
                        'improvement_areas': []
                    }
                )
                db.add(analytics)
            
            # Update analytics based on activity type
            if activity_type == 'quiz_completed':
                score = activity_data.get('score', 0)
                current_avg = analytics.analytics_data.get('average_quiz_score', 0)
                analytics.analytics_data['average_quiz_score'] = (current_avg + score) / 2
                
            elif activity_type == 'study_session':
                duration = activity_data.get('duration', 0)
                analytics.analytics_data['total_study_time'] += duration
                
                subject = activity_data.get('subject')
                if subject and subject not in analytics.analytics_data['subjects_studied']:
                    analytics.analytics_data['subjects_studied'].append(subject)
            
            analytics.updated_at = datetime.utcnow()
            db.commit()
            
        except Exception as e:
            logger.error(f"Error updating learning analytics: {str(e)}")
            raise
    
    async def _generate_initial_resources(self, study_plan: StudyPlan, db: Session):
        """Generate initial resources for a new study plan"""
        try:
            # Get first week's topics from the plan
            first_week_topics = study_plan.plan_content.get('weeks', [{}])[0].get('topics', [])
            
            for topic in first_week_topics[:2]:  # Generate for first 2 topics
                request = StudyResourceRequest(
                    topic=topic,
                    subject=study_plan.subject,
                    grade_level=study_plan.grade_level,
                    difficulty_level='medium'
                )
                
                # Generate resources for this topic
                await self.generate_study_resources(
                    request=request,
                    user_id=study_plan.user_id,
                    school_id=study_plan.school_id,
                    db=db
                )
                
        except Exception as e:
            logger.error(f"Error generating initial resources: {str(e)}")
            # Don't raise here as it's not critical for study plan creation
