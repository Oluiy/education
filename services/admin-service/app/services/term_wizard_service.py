"""
Term Setup Wizard Service
Business logic for guided term configuration
"""

from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, date, time
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
import logging

from models.term_models import (
    Term, ClassSchedule, AssessmentConfig, GradingConfig,
    Holiday, WizardSession, TermTemplate, CalendarEvent
)
from schemas.term_schemas import (
    TermCreate, TermUpdate, ClassScheduleCreate, AssessmentConfigCreate,
    GradingConfigCreate, HolidayCreate, WizardSessionCreate, WizardSessionUpdate,
    TermTemplateCreate, CalendarEventCreate, WizardStep, TermStatus,
    WizardStepResponse, TermSummary, WizardProgressResponse
)

logger = logging.getLogger(__name__)


class TermSetupWizardService:
    """Service for term setup wizard functionality"""
    
    def __init__(self, db: Session):
        self.db = db
    
    # === WIZARD SESSION MANAGEMENT ===
    
    def start_wizard_session(
        self,
        term_id: int,
        user_id: int
    ) -> WizardSession:
        """
        Start a new wizard session
        """
        try:
            # Check if term exists
            term = self.db.query(Term).filter(Term.term_id == term_id).first()
            if not term:
                raise ValueError("Term not found")
            
            # Check for existing active session
            existing_session = self.db.query(WizardSession).filter(
                and_(
                    WizardSession.term_id == term_id,
                    WizardSession.user_id == user_id
                )
            ).first()
            
            if existing_session:
                return existing_session
            
            # Create new session
            session = WizardSession(
                term_id=term_id,
                user_id=user_id,
                current_step=WizardStep.BASIC_INFO,
                completed_steps=[],
                step_data={}
            )
            
            self.db.add(session)
            self.db.commit()
            self.db.refresh(session)
            
            logger.info(f"Started wizard session for term {term_id}, user {user_id}")
            return session
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error starting wizard session: {e}")
            raise
    
    def get_wizard_session(
        self,
        term_id: int,
        user_id: int
    ) -> Optional[WizardSession]:
        """
        Get existing wizard session
        """
        return self.db.query(WizardSession).filter(
            and_(
                WizardSession.term_id == term_id,
                WizardSession.user_id == user_id
            )
        ).first()
    
    def update_wizard_step(
        self,
        session_id: int,
        step: WizardStep,
        step_data: Dict[str, Any]
    ) -> WizardStepResponse:
        """
        Update wizard step with validation
        """
        try:
            session = self.db.query(WizardSession).filter(
                WizardSession.session_id == session_id
            ).first()
            
            if not session:
                raise ValueError("Wizard session not found")
            
            # Validate step data
            validation_result = self._validate_step_data(step, step_data)
            
            if validation_result["valid"]:
                # Update session
                session.current_step = step
                if step not in session.completed_steps:
                    session.completed_steps.append(step)
                
                # Merge step data
                session.step_data.update({step.value: step_data})
                session.updated_at = datetime.utcnow()
                
                self.db.commit()
                
                # Determine next step
                next_step = self._get_next_step(step, session.completed_steps)
                
                return WizardStepResponse(
                    step=step,
                    completed=True,
                    next_step=next_step,
                    validation_errors=[],
                    data=step_data
                )
            else:
                return WizardStepResponse(
                    step=step,
                    completed=False,
                    validation_errors=validation_result["errors"],
                    data=step_data
                )
        
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error updating wizard step: {e}")
            raise
    
    def get_wizard_progress(
        self,
        session_id: int
    ) -> WizardProgressResponse:
        """
        Get wizard progress and status
        """
        try:
            session = self.db.query(WizardSession).filter(
                WizardSession.session_id == session_id
            ).first()
            
            if not session:
                raise ValueError("Wizard session not found")
            
            # Calculate progress
            total_steps = len(WizardStep)
            completed_steps = len(session.completed_steps)
            progress_percentage = (completed_steps / total_steps) * 100
            
            # Get next step
            next_step = self._get_next_step(session.current_step, session.completed_steps)
            
            # Get available steps
            available_steps = self._get_available_steps(session.completed_steps)
            
            # Get term summary
            term_summary = self._get_term_summary(session.term_id)
            
            return WizardProgressResponse(
                session=session,
                progress_percentage=progress_percentage,
                next_step=next_step,
                available_steps=available_steps,
                term_summary=term_summary
            )
        
        except Exception as e:
            logger.error(f"Error getting wizard progress: {e}")
            raise
    
    # === TERM MANAGEMENT ===
    
    def create_term_from_wizard(
        self,
        session_id: int
    ) -> Term:
        """
        Create or update term from wizard session data
        """
        try:
            session = self.db.query(WizardSession).filter(
                WizardSession.session_id == session_id
            ).first()
            
            if not session:
                raise ValueError("Wizard session not found")
            
            # Extract basic info from session data
            basic_info = session.step_data.get("basic_info", {})
            
            # Get existing term or create new one
            term = self.db.query(Term).filter(Term.term_id == session.term_id).first()
            
            if term:
                # Update existing term
                for key, value in basic_info.items():
                    if hasattr(term, key):
                        setattr(term, key, value)
                term.updated_at = datetime.utcnow()
            else:
                # This shouldn't happen in normal flow, but handle it
                term_data = TermCreate(
                    school_id=basic_info.get("school_id"),
                    created_by=session.user_id,
                    **basic_info
                )
                term = Term(**term_data.dict())
                self.db.add(term)
            
            # Create schedules
            schedules_data = session.step_data.get("schedule", {}).get("schedules", [])
            self._create_schedules_from_data(term.term_id, schedules_data)
            
            # Create assessments
            assessments_data = session.step_data.get("assessment", {}).get("assessments", [])
            self._create_assessments_from_data(term.term_id, assessments_data)
            
            # Create grading config
            grading_data = session.step_data.get("grading", {})
            if grading_data:
                self._create_grading_config_from_data(term.term_id, grading_data)
            
            # Create holidays
            holidays_data = session.step_data.get("holidays", {}).get("holidays", [])
            self._create_holidays_from_data(term.term_id, holidays_data)
            
            # Set term as active if wizard is complete
            if WizardStep.COMPLETE in session.completed_steps:
                term.status = TermStatus.ACTIVE
            
            self.db.commit()
            self.db.refresh(term)
            
            logger.info(f"Created/updated term {term.term_id} from wizard session")
            return term
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error creating term from wizard: {e}")
            raise
    
    # === TEMPLATE MANAGEMENT ===
    
    def create_template_from_term(
        self,
        term_id: int,
        template_name: str,
        description: Optional[str] = None,
        is_public: bool = False
    ) -> TermTemplate:
        """
        Create template from existing term
        """
        try:
            term = self.db.query(Term).filter(Term.term_id == term_id).first()
            if not term:
                raise ValueError("Term not found")
            
            # Extract term data
            template_data = {
                "basic_info": {
                    "name": term.name,
                    "academic_year": term.academic_year,
                    "description": term.description
                },
                "schedules": [
                    {
                        "class_name": s.class_name,
                        "subject_name": s.subject_name,
                        "day_of_week": s.day_of_week,
                        "start_time": s.start_time.isoformat(),
                        "end_time": s.end_time.isoformat(),
                        "room": s.room
                    }
                    for s in term.schedules
                ],
                "assessments": [
                    {
                        "assessment_type": a.assessment_type,
                        "name": a.name,
                        "weight_percentage": a.weight_percentage,
                        "description": a.description,
                        "is_required": a.is_required
                    }
                    for a in term.assessments
                ],
                "grading": {
                    "grade_scale": term.grading_config.grade_scale if term.grading_config else None,
                    "min_score": term.grading_config.min_score if term.grading_config else None,
                    "max_score": term.grading_config.max_score if term.grading_config else None,
                    "passing_score": term.grading_config.passing_score if term.grading_config else None,
                    "grade_boundaries": term.grading_config.grade_boundaries if term.grading_config else {}
                },
                "holidays": [
                    {
                        "name": h.name,
                        "description": h.description
                    }
                    for h in term.holidays
                ]
            }
            
            template = TermTemplate(
                name=template_name,
                description=description,
                template_data=template_data,
                is_public=is_public,
                school_id=term.school_id,
                created_by=term.created_by
            )
            
            self.db.add(template)
            self.db.commit()
            self.db.refresh(template)
            
            logger.info(f"Created template {template.template_id} from term {term_id}")
            return template
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error creating template from term: {e}")
            raise
    
    def apply_template_to_wizard(
        self,
        session_id: int,
        template_id: int
    ) -> WizardSession:
        """
        Apply template to wizard session
        """
        try:
            session = self.db.query(WizardSession).filter(
                WizardSession.session_id == session_id
            ).first()
            
            if not session:
                raise ValueError("Wizard session not found")
            
            template = self.db.query(TermTemplate).filter(
                TermTemplate.template_id == template_id
            ).first()
            
            if not template:
                raise ValueError("Template not found")
            
            # Apply template data to session
            session.step_data = template.template_data.copy()
            session.updated_at = datetime.utcnow()
            
            # Mark relevant steps as completed
            completed_steps = []
            if template.template_data.get("basic_info"):
                completed_steps.append(WizardStep.BASIC_INFO)
            if template.template_data.get("schedules"):
                completed_steps.append(WizardStep.SCHEDULE)
            if template.template_data.get("assessments"):
                completed_steps.append(WizardStep.ASSESSMENT)
            if template.template_data.get("grading"):
                completed_steps.append(WizardStep.GRADING)
            if template.template_data.get("holidays"):
                completed_steps.append(WizardStep.HOLIDAYS)
            
            session.completed_steps = completed_steps
            
            self.db.commit()
            self.db.refresh(session)
            
            logger.info(f"Applied template {template_id} to wizard session {session_id}")
            return session
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error applying template to wizard: {e}")
            raise
    
    # === HELPER METHODS ===
    
    def _validate_step_data(
        self,
        step: WizardStep,
        data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Validate wizard step data
        """
        errors = []
        
        try:
            if step == WizardStep.BASIC_INFO:
                required_fields = ["name", "academic_year", "start_date", "end_date"]
                for field in required_fields:
                    if not data.get(field):
                        errors.append(f"{field} is required")
                
                # Validate dates
                if data.get("start_date") and data.get("end_date"):
                    try:
                        start_date = datetime.strptime(data["start_date"], "%Y-%m-%d").date()
                        end_date = datetime.strptime(data["end_date"], "%Y-%m-%d").date()
                        if end_date <= start_date:
                            errors.append("End date must be after start date")
                    except ValueError:
                        errors.append("Invalid date format")
            
            elif step == WizardStep.SCHEDULE:
                schedules = data.get("schedules", [])
                if not schedules:
                    errors.append("At least one class schedule is required")
                
                for i, schedule in enumerate(schedules):
                    required_fields = ["class_name", "subject_name", "day_of_week", "start_time", "end_time"]
                    for field in required_fields:
                        if not schedule.get(field):
                            errors.append(f"Schedule {i+1}: {field} is required")
            
            elif step == WizardStep.ASSESSMENT:
                assessments = data.get("assessments", [])
                if not assessments:
                    errors.append("At least one assessment configuration is required")
                
                total_weight = sum(a.get("weight_percentage", 0) for a in assessments)
                if total_weight != 100:
                    errors.append(f"Total assessment weight must equal 100% (current: {total_weight}%)")
            
            elif step == WizardStep.GRADING:
                required_fields = ["grade_scale", "min_score", "max_score", "passing_score"]
                for field in required_fields:
                    if data.get(field) is None:
                        errors.append(f"{field} is required")
                
                if data.get("min_score") is not None and data.get("max_score") is not None:
                    if data["max_score"] <= data["min_score"]:
                        errors.append("Max score must be greater than min score")
            
            return {
                "valid": len(errors) == 0,
                "errors": errors
            }
        
        except Exception as e:
            logger.error(f"Error validating step data: {e}")
            return {
                "valid": False,
                "errors": [f"Validation error: {str(e)}"]
            }
    
    def _get_next_step(
        self,
        current_step: WizardStep,
        completed_steps: List[WizardStep]
    ) -> Optional[WizardStep]:
        """
        Determine next wizard step
        """
        step_order = [
            WizardStep.BASIC_INFO,
            WizardStep.SCHEDULE,
            WizardStep.SUBJECTS,
            WizardStep.ASSESSMENT,
            WizardStep.GRADING,
            WizardStep.HOLIDAYS,
            WizardStep.REVIEW,
            WizardStep.COMPLETE
        ]
        
        try:
            current_index = step_order.index(current_step)
            if current_index < len(step_order) - 1:
                return step_order[current_index + 1]
            return None
        except ValueError:
            return WizardStep.BASIC_INFO
    
    def _get_available_steps(
        self,
        completed_steps: List[WizardStep]
    ) -> List[WizardStep]:
        """
        Get available wizard steps based on completion
        """
        step_order = [
            WizardStep.BASIC_INFO,
            WizardStep.SCHEDULE,
            WizardStep.SUBJECTS,
            WizardStep.ASSESSMENT,
            WizardStep.GRADING,
            WizardStep.HOLIDAYS,
            WizardStep.REVIEW,
            WizardStep.COMPLETE
        ]
        
        available = []
        for step in step_order:
            if step in completed_steps:
                available.append(step)
            elif not available or len(available) == len(completed_steps):
                # Can access next step after completing previous
                available.append(step)
                break
        
        return available
    
    def _get_term_summary(self, term_id: int) -> Optional[TermSummary]:
        """
        Get term summary for wizard progress
        """
        try:
            term = self.db.query(Term).filter(Term.term_id == term_id).first()
            if not term:
                return None
            
            schedules_count = self.db.query(ClassSchedule).filter(
                ClassSchedule.term_id == term_id
            ).count()
            
            assessments_count = self.db.query(AssessmentConfig).filter(
                AssessmentConfig.term_id == term_id
            ).count()
            
            holidays_count = self.db.query(Holiday).filter(
                Holiday.term_id == term_id
            ).count()
            
            events_count = self.db.query(CalendarEvent).filter(
                CalendarEvent.term_id == term_id
            ).count()
            
            # Calculate completion percentage
            completion_factors = [
                schedules_count > 0,
                assessments_count > 0,
                term.grading_config is not None,
                holidays_count >= 0  # Holidays are optional
            ]
            
            completion_percentage = (sum(completion_factors) / len(completion_factors)) * 100
            
            return TermSummary(
                term=term,
                schedules_count=schedules_count,
                assessments_count=assessments_count,
                holidays_count=holidays_count,
                events_count=events_count,
                completion_percentage=completion_percentage
            )
        
        except Exception as e:
            logger.error(f"Error getting term summary: {e}")
            return None
    
    def _create_schedules_from_data(self, term_id: int, schedules_data: List[Dict]):
        """Create class schedules from wizard data"""
        for schedule_data in schedules_data:
            schedule = ClassSchedule(
                term_id=term_id,
                **schedule_data
            )
            self.db.add(schedule)
    
    def _create_assessments_from_data(self, term_id: int, assessments_data: List[Dict]):
        """Create assessment configs from wizard data"""
        for assessment_data in assessments_data:
            assessment = AssessmentConfig(
                term_id=term_id,
                **assessment_data
            )
            self.db.add(assessment)
    
    def _create_grading_config_from_data(self, term_id: int, grading_data: Dict):
        """Create grading config from wizard data"""
        grading_config = GradingConfig(
            term_id=term_id,
            **grading_data
        )
        self.db.add(grading_config)
    
    def _create_holidays_from_data(self, term_id: int, holidays_data: List[Dict]):
        """Create holidays from wizard data"""
        for holiday_data in holidays_data:
            holiday = Holiday(
                term_id=term_id,
                **holiday_data
            )
            self.db.add(holiday)
