from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from typing import List, Dict, Any, Optional
from app.db.session import get_db
from app.db.models.employer import Employer, EmployerStatus
from app.db.models.user import User
from app.core.dependencies import get_current_user
from app.utils.logger import logger

router = APIRouter(prefix="/api/employers", tags=["employers"])

class EmployerApplyRequest(BaseModel):
    company_name: str
    registration_number: str
    industry: str
    company_size: str
    website: Optional[str] = None
    country: str
    city: str
    contact_name: str
    contact_title: str
    contact_email: EmailStr
    contact_phone: str
    hiring_description: Optional[str] = None
    certificate_url: Optional[str] = None
    logo_url: Optional[str] = None

@router.post("/apply")
async def apply_as_employer(request: EmployerApplyRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    existing = db.query(Employer).filter(Employer.user_id == current_user.id).first()
    if existing:
        raise HTTPException(status_code=400, detail="You have already applied as an employer")

    employer = Employer(
        user_id=current_user.id,
        **request.model_dump(),
        status=EmployerStatus.PENDING
    )
    db.add(employer)
    db.commit()
    db.refresh(employer)
    return {"message": "Application submitted successfully", "application_id": employer.id}

@router.get("/me")
async def get_my_employer_status(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    employer = db.query(Employer).filter(Employer.user_id == current_user.id).first()
    if not employer:
        raise HTTPException(status_code=404, detail="Employer profile not found")
    return employer

@router.post("/shortlist/{cv_id}")
async def shortlist_cv(cv_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    # Verify current user is approved employer
    employer = db.query(Employer).filter(Employer.user_id == current_user.id).first()
    if not employer or employer.status != EmployerStatus.APPROVED:
        raise HTTPException(status_code=403, detail="Only approved employers can shortlist candidates")

    # In a real app, we'd have a Shortlist model
    # For now, return success
    return {"message": f"CV {cv_id} shortlisted successfully"}

@router.get("/shortlisted")
async def get_shortlisted_cvs(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    # Mock return for now
    return {"shortlisted_cvs": []}
