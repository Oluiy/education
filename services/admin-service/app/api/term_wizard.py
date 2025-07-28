"""
Term Setup Wizard API endpoints
Guided term configuration with step-by-step wizard
"""

from fastapi import APIRouter, HTTPException, Depends, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
import logging

from database import get_db
from services.term_wizard_service import TermSetupWizardService
from schemas.term_schemas import (
    TermCreate, TermResponse, TermUpdate, WizardStepRequest, WizardStepResponse,
    WizardProgressResponse, WizardSessionResponse, TermTemplateResponse,
    TermTemplateCreate, WizardStep, TermStatus, TermSummary
)
from auth.dependencies import get_current_user, require_roles

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/term-wizard",
    tags=["Term Setup Wizard"]
)


# === WIZARD SESSION ENDPOINTS ===

@router.post("/start/{term_id}", response_model=WizardSessionResponse)
async def start_wizard_session(
    term_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_roles(["admin", "teacher"]))
):
    """
    Start a new term setup wizard session
    """
    try:
        service = TermSetupWizardService(db)
        
        session = service.start_wizard_session(
            term_id=term_id,
            user_id=current_user["user_id"]
        )
        
        return WizardSessionResponse.from_orm(session)
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error starting wizard session: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to start wizard session"
        )


@router.get("/session/{term_id}", response_model=WizardSessionResponse)
async def get_wizard_session(
    term_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_roles(["admin", "teacher"]))
):
    """
    Get existing wizard session
    """
    try:
        service = TermSetupWizardService(db)
        
        session = service.get_wizard_session(
            term_id=term_id,
            user_id=current_user["user_id"]
        )
        
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Wizard session not found"
            )
        
        return WizardSessionResponse.from_orm(session)
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting wizard session: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get wizard session"
        )


@router.get("/progress/{session_id}", response_model=WizardProgressResponse)
async def get_wizard_progress(
    session_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_roles(["admin", "teacher"]))
):
    """
    Get wizard progress and status
    """
    try:
        service = TermSetupWizardService(db)
        
        progress = service.get_wizard_progress(session_id)
        
        return progress
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error getting wizard progress: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get wizard progress"
        )


@router.post("/step/{session_id}", response_model=WizardStepResponse)
async def update_wizard_step(
    session_id: int,
    request: WizardStepRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_roles(["admin", "teacher"]))
):
    """
    Update wizard step with validation
    """
    try:
        service = TermSetupWizardService(db)
        
        response = service.update_wizard_step(
            session_id=session_id,
            step=request.step,
            step_data=request.data
        )
        
        return response
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error updating wizard step: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update wizard step"
        )


@router.post("/complete/{session_id}", response_model=TermResponse)
async def complete_wizard(
    session_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_roles(["admin", "teacher"]))
):
    """
    Complete wizard and create/update term
    """
    try:
        service = TermSetupWizardService(db)
        
        term = service.create_term_from_wizard(session_id)
        
        return TermResponse.from_orm(term)
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error completing wizard: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to complete wizard"
        )


# === TEMPLATE ENDPOINTS ===

@router.post("/template/create/{term_id}", response_model=TermTemplateResponse)
async def create_template_from_term(
    term_id: int,
    template_name: str,
    description: Optional[str] = None,
    is_public: bool = False,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_roles(["admin"]))
):
    """
    Create template from existing term
    """
    try:
        service = TermSetupWizardService(db)
        
        template = service.create_template_from_term(
            term_id=term_id,
            template_name=template_name,
            description=description,
            is_public=is_public
        )
        
        return TermTemplateResponse.from_orm(template)
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error creating template: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create template"
        )


@router.post("/template/apply/{session_id}", response_model=WizardSessionResponse)
async def apply_template_to_wizard(
    session_id: int,
    template_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_roles(["admin", "teacher"]))
):
    """
    Apply template to wizard session
    """
    try:
        service = TermSetupWizardService(db)
        
        session = service.apply_template_to_wizard(
            session_id=session_id,
            template_id=template_id
        )
        
        return WizardSessionResponse.from_orm(session)
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error applying template: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to apply template"
        )


@router.get("/templates", response_model=List[TermTemplateResponse])
async def get_available_templates(
    school_id: Optional[int] = None,
    include_public: bool = True,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_roles(["admin", "teacher"]))
):
    """
    Get available term templates
    """
    try:
        from models.term_models import TermTemplate
        from sqlalchemy import and_, or_
        
        query = db.query(TermTemplate)
        
        # Filter by school or public templates
        conditions = []
        
        if school_id:
            conditions.append(TermTemplate.school_id == school_id)
        else:
            conditions.append(TermTemplate.school_id == current_user["school_id"])
        
        if include_public:
            conditions.append(TermTemplate.is_public == True)
        
        if conditions:
            query = query.filter(or_(*conditions))
        
        templates = query.order_by(TermTemplate.created_at.desc()).all()
        
        return [TermTemplateResponse.from_orm(template) for template in templates]
    
    except Exception as e:
        logger.error(f"Error getting templates: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get templates"
        )


# === STEP DATA VALIDATION ENDPOINTS ===

@router.post("/validate/basic-info")
async def validate_basic_info(
    data: Dict[str, Any],
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_roles(["admin", "teacher"]))
):
    """
    Validate basic info step data
    """
    try:
        service = TermSetupWizardService(db)
        
        validation_result = service._validate_step_data(WizardStep.BASIC_INFO, data)
        
        return {
            "valid": validation_result["valid"],
            "errors": validation_result["errors"]
        }
    
    except Exception as e:
        logger.error(f"Error validating basic info: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to validate basic info"
        )


@router.post("/validate/schedule")
async def validate_schedule_data(
    data: Dict[str, Any],
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_roles(["admin", "teacher"]))
):
    """
    Validate schedule step data
    """
    try:
        service = TermSetupWizardService(db)
        
        validation_result = service._validate_step_data(WizardStep.SCHEDULE, data)
        
        return {
            "valid": validation_result["valid"],
            "errors": validation_result["errors"]
        }
    
    except Exception as e:
        logger.error(f"Error validating schedule: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to validate schedule"
        )


@router.post("/validate/assessment")
async def validate_assessment_data(
    data: Dict[str, Any],
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_roles(["admin", "teacher"]))
):
    """
    Validate assessment step data
    """
    try:
        service = TermSetupWizardService(db)
        
        validation_result = service._validate_step_data(WizardStep.ASSESSMENT, data)
        
        return {
            "valid": validation_result["valid"],
            "errors": validation_result["errors"]
        }
    
    except Exception as e:
        logger.error(f"Error validating assessment: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to validate assessment"
        )


@router.post("/validate/grading")
async def validate_grading_data(
    data: Dict[str, Any],
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_roles(["admin", "teacher"]))
):
    """
    Validate grading step data
    """
    try:
        service = TermSetupWizardService(db)
        
        validation_result = service._validate_step_data(WizardStep.GRADING, data)
        
        return {
            "valid": validation_result["valid"],
            "errors": validation_result["errors"]
        }
    
    except Exception as e:
        logger.error(f"Error validating grading: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to validate grading"
        )


# === PREVIEW ENDPOINTS ===

@router.get("/preview/{session_id}")
async def preview_term_configuration(
    session_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_roles(["admin", "teacher"]))
):
    """
    Preview term configuration before completion
    """
    try:
        from models.term_models import WizardSession
        
        session = db.query(WizardSession).filter(
            WizardSession.session_id == session_id
        ).first()
        
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Wizard session not found"
            )
        
        # Extract and format data for preview
        preview_data = {
            "basic_info": session.step_data.get("basic_info", {}),
            "schedules": session.step_data.get("schedule", {}).get("schedules", []),
            "assessments": session.step_data.get("assessment", {}).get("assessments", []),
            "grading": session.step_data.get("grading", {}),
            "holidays": session.step_data.get("holidays", {}).get("holidays", []),
            "completion_status": {
                "completed_steps": session.completed_steps,
                "current_step": session.current_step,
                "total_steps": len(WizardStep),
                "progress_percentage": (len(session.completed_steps) / len(WizardStep)) * 100
            }
        }
        
        return preview_data
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error previewing term configuration: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to preview configuration"
        )


# === UTILITY ENDPOINTS ===

@router.get("/steps")
async def get_wizard_steps():
    """
    Get available wizard steps and their descriptions
    """
    steps_info = {
        WizardStep.BASIC_INFO: {
            "name": "Basic Information",
            "description": "Set term name, dates, and basic details",
            "required_fields": ["name", "academic_year", "start_date", "end_date"]
        },
        WizardStep.SCHEDULE: {
            "name": "Class Schedule",
            "description": "Configure class timetables and schedules",
            "required_fields": ["schedules"]
        },
        WizardStep.SUBJECTS: {
            "name": "Subjects",
            "description": "Set up subjects and curriculum",
            "required_fields": ["subjects"]
        },
        WizardStep.ASSESSMENT: {
            "name": "Assessment Configuration",
            "description": "Configure assessment types and weights",
            "required_fields": ["assessments"]
        },
        WizardStep.GRADING: {
            "name": "Grading System",
            "description": "Set up grading scales and boundaries",
            "required_fields": ["grade_scale", "score_ranges"]
        },
        WizardStep.HOLIDAYS: {
            "name": "Holidays & Breaks",
            "description": "Define holidays and term breaks",
            "required_fields": []  # Optional
        },
        WizardStep.REVIEW: {
            "name": "Review",
            "description": "Review all configurations before completion",
            "required_fields": []
        },
        WizardStep.COMPLETE: {
            "name": "Complete",
            "description": "Finalize and activate term configuration",
            "required_fields": []
        }
    }
    
    return {
        "steps": steps_info,
        "total_steps": len(WizardStep),
        "order": list(WizardStep)
    }


@router.get("/health")
async def health_check():
    """
    Health check endpoint
    """
    return {
        "status": "healthy",
        "service": "Term Setup Wizard",
        "timestamp": logger.info
    }
