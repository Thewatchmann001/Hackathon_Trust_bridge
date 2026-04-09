from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from app.db.session import get_db
from app.db.models.cv import CV
from app.db.models.user import User
from app.core.dependencies import get_current_user
from app.services.ai_service import AIService
from app.utils.logger import logger
import json
import io
from fastapi.responses import StreamingResponse
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import LETTER

router = APIRouter(prefix="/api/cv", tags=["cv"])
ai_service = AIService()

class CVSaveRequest(BaseModel):
    personal_info: Dict[str, Any]
    summary: str
    work_experience: List[Dict[str, Any]]
    education: List[Dict[str, Any]]
    skills: Dict[str, Any]
    certifications: Optional[List[Dict[str, Any]]] = None
    template_name: Optional[str] = "Modern"

class AIEnhanceRequest(BaseModel):
    section: str
    content: str

@router.get("/me")
async def get_my_cv(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    cv = db.query(CV).filter(CV.user_id == current_user.id).first()
    if not cv:
        raise HTTPException(status_code=404, detail="CV not found")
    return cv

@router.post("/save")
async def save_cv(request: CVSaveRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    cv = db.query(CV).filter(CV.user_id == current_user.id).first()
    if not cv:
        cv = CV(user_id=current_user.id)
        db.add(cv)

    cv.personal_info = request.personal_info
    cv.summary = request.summary
    cv.work_experience = request.work_experience
    cv.education = request.education
    cv.skills = request.skills
    cv.certifications = request.certifications
    cv.template_name = request.template_name

    # Update json_content for backward compatibility
    cv.json_content = request.model_dump()

    db.commit()
    db.refresh(cv)
    return {"message": "CV saved successfully", "cv_id": cv.id}

@router.post("/ai-enhance")
async def ai_enhance(request: AIEnhanceRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    try:
        if request.section == "summary":
            # Generate summary from experience if content is empty or short
            cv = db.query(CV).filter(CV.user_id == current_user.id).first()
            exp_text = ""
            if cv and cv.work_experience:
                exp_text = " ".join([f"{e.get('job_title')} at {e.get('company')}: {e.get('description')}" for e in cv.work_experience])

            prompt = f"Generate a professional CV summary based on this work experience: {exp_text}. "
            if request.content:
                prompt += f"Also consider this existing draft: {request.content}"

            # Using ai_service.enhance_language as a proxy for generation for now
            enhanced_text = ai_service.enhance_language(prompt, "summary")
        else:
            enhanced_text = ai_service.enhance_language(request.content, request.section)

        return {"enhanced_content": enhanced_text}
    except Exception as e:
        logger.error(f"AI Enhancement failed: {str(e)}")
        raise HTTPException(status_code=500, detail="AI enhancement failed")

@router.post("/export-pdf")
async def export_pdf(request: Dict[str, Any], current_user: User = Depends(get_current_user)):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=LETTER)
    styles = getSampleStyleSheet()
    story = []

    personal = request.get('personal_info', {})
    story.append(Paragraph(f"<b>{personal.get('full_name', 'CV')}</b>", styles['Title']))
    story.append(Paragraph(f"{personal.get('email', '')} | {personal.get('phone', '')}", styles['Normal']))
    story.append(Paragraph(f"{personal.get('location', '')}", styles['Normal']))
    story.append(Spacer(1, 12))

    story.append(Paragraph("<b>Professional Summary</b>", styles['Heading2']))
    story.append(Paragraph(request.get('summary', ''), styles['Normal']))
    story.append(Spacer(1, 12))

    story.append(Paragraph("<b>Work Experience</b>", styles['Heading2']))
    for exp in request.get('work_experience', []):
        story.append(Paragraph(f"<b>{exp.get('job_title')}</b> at {exp.get('company')}", styles['Normal']))
        story.append(Paragraph(exp.get('description', ''), styles['Normal']))
        story.append(Spacer(1, 6))

    story.append(Paragraph("<b>Education</b>", styles['Heading2']))
    for edu in request.get('education', []):
        story.append(Paragraph(f"<b>{edu.get('degree')}</b>, {edu.get('institution')} ({edu.get('year')})", styles['Normal']))
        story.append(Spacer(1, 6))

    story.append(Paragraph("<b>Skills</b>", styles['Heading2']))
    skills = request.get('skills', {})
    for cat, items in skills.items():
        if items:
            story.append(Paragraph(f"<b>{cat.capitalize()}:</b> {', '.join(items)}", styles['Normal']))

    doc.build(story)
    buffer.seek(0)
    return StreamingResponse(buffer, media_type="application/pdf", headers={"Content-Disposition": "attachment; filename=cv.pdf"})

@router.post("/upload-parse")
async def upload_parse(file: UploadFile = File(...), current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    # Read file content
    content = await file.read()

    # Simple text extraction for PDF/Text (in real scenario would use a PDF lib)
    try:
        text = content.decode('utf-8')
    except:
        text = "File content extracted (binary)"

    # Use AIService to parse and structure the CV
    parsed_data = ai_service.parse_and_structure_cv(text, current_user.id, db)

    # Tailor it with AI enhancements
    tailored_data = ai_service.tailor_parsed_cv(parsed_data, db)

    return tailored_data

class CVSearchRequest(BaseModel):
    job_title: str
    skills: List[str]
    experience_level: str
    location: Optional[str] = None

@router.post("/search")
async def search_cvs(request: CVSearchRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    # 1. Query all CVs
    cvs = db.query(CV).all()
    results = []

    from app.services.matching_service import MatchingService
    matching_service = MatchingService()

    for cv in cvs:
        # Use MatchingService logic for realistic scoring
        user_skills_set = set([s.lower() for s in cv.skills.get("technical", [])]) if cv.skills else set()

        # Calculate skills match
        skills_match = matching_service._calculate_skills_match_fast(request.skills, user_skills_set)

        # Calculate experience match
        exp_years = len(cv.work_experience) if cv.work_experience else 0
        min_exp = 0
        if request.experience_level == "Junior": min_exp = 1
        elif request.experience_level == "Mid": min_exp = 3
        elif request.experience_level == "Senior": min_exp = 5

        experience_match = matching_service._calculate_experience_match(min_exp, exp_years)

        # Combined score (Weighted)
        match_score = int((skills_match * 0.7 + experience_match * 0.3) * 100)

        match_reason = f"Matches {int(skills_match*100)}% of required skills and {int(experience_match*100)}% of experience requirements."

        results.append({
            "cv_id": cv.id,
            "name": cv.personal_info.get("full_name") if cv.personal_info else "Hidden Name",
            "skills": cv.skills.get("technical", []) if cv.skills else [],
            "experience_years": exp_years,
            "match_score": match_score,
            "match_reason": match_reason
        })

    # Rank by match score
    results.sort(key=lambda x: x["match_score"], reverse=True)
    return results
