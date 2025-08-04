from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import Optional
import io

from .database import get_db
from .bulk_import import BulkImportService
from .models import AdminAction

router = APIRouter()

@router.post("/bulk-import/users")
async def bulk_import_users(
    file: UploadFile = File(...),
    role: str = Form(...),
    school_id: int = Form(...),
    admin_user_id: int = Form(...),
    send_emails: bool = Form(True),
    db: Session = Depends(get_db)
):
    """Bulk import users from CSV file"""
    
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="File must be a CSV")
    
    try:
        # Read file content
        file_content = await file.read()
        
        # Initialize bulk import service
        bulk_service = BulkImportService(db)
        
        # Perform bulk import
        result = bulk_service.bulk_import_users(
            file_content=file_content,
            role=role,
            school_id=school_id,
            admin_user_id=admin_user_id,
            send_emails=send_emails
        )
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/bulk-import/template/{role}")
async def get_csv_template(role: str):
    """Get CSV template for bulk import"""
    
    bulk_service = BulkImportService(None)
    csv_content = bulk_service.get_csv_template(role)
    
    # Create streaming response
    def generate():
        yield csv_content
    
    return StreamingResponse(
        io.StringIO(csv_content),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={role}_template.csv"}
    )

@router.get("/bulk-import/history")
async def get_import_history(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Get bulk import history"""
    
    actions = db.query(AdminAction).filter(
        AdminAction.action_type == "bulk_import"
    ).offset(skip).limit(limit).all()
    
    return actions
