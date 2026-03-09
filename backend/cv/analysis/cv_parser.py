"""
Structured CV Parser
Extracts structured data from CV once and caches it.
"""
from typing import Dict, Any, List, Optional
from app.utils.logger import logger


class CVParser:
    """Parse CV into structured JSON format."""
    
    def parse(self, cv_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Parse CV data into structured format.
        
        Args:
            cv_data: Raw CV data (from database or upload)
            
        Returns:
            Structured CV data with extracted fields
        """
        try:
            # Handle both json_content structure and direct structure
            content = cv_data.get("json_content", {}) or cv_data
            
            structured = {
                "personal_info": self._extract_personal_info(content),
                "skills": self._extract_skills(content),
                "experience": self._extract_experience(content),
                "education": self._extract_education(content),
                "summary": self._extract_summary(content),
                "job_titles": self._extract_job_titles(content),
                "industry": self._detect_industry(content),
                "years_experience": self._calculate_years_experience(content),
                "keywords": self._extract_keywords(content),
            }
            
            logger.info(f"CV parsed - Skills: {len(structured['skills'])}, Experience: {len(structured['experience'])}")
            
            return structured
            
        except Exception as e:
            logger.error(f"Error parsing CV: {e}", exc_info=True)
            return self._get_empty_structure()
    
    def _extract_personal_info(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Extract personal information."""
        personal_info = content.get("personal_info", {})
        return {
            "full_name": personal_info.get("full_name", ""),
            "email": personal_info.get("email", ""),
            "location": personal_info.get("location", ""),
        }
    
    def _extract_skills(self, content: Dict[str, Any]) -> List[str]:
        """Extract all skills from CV."""
        skills = []
        
        # Check various skill field names
        skills_data = (
            content.get("personal_skills", {}) or
            content.get("skills", {}) or
            {}
        )
        
        # Extract from different skill categories
        skill_categories = [
            "job_related_skills", "technical_skills", "technical",
            "computer_skills", "programming_skills",
            "soft", "social_skills",
            "tools"
        ]
        
        for category in skill_categories:
            if category in skills_data:
                category_skills = skills_data[category]
                if isinstance(category_skills, list):
                    skills.extend(category_skills)
                elif isinstance(category_skills, str):
                    skills.append(category_skills)
        
        # Also extract from experience descriptions
        experience = content.get("experience", []) or content.get("work_experience", [])
        for exp in experience:
            desc = exp.get("description", "")
            if desc:
                # Simple keyword extraction
                tech_keywords = ["python", "javascript", "react", "node", "sql", "aws", "docker"]
                for keyword in tech_keywords:
                    if keyword.lower() in desc.lower() and keyword.title() not in skills:
                        skills.append(keyword.title())
        
        return list(set(skills))  # Remove duplicates
    
    def _extract_experience(self, content: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract work experience."""
        experience = content.get("experience", []) or content.get("work_experience", [])
        
        structured_exp = []
        for exp in experience:
            if isinstance(exp, dict):
                structured_exp.append({
                    "job_title": exp.get("job_title", exp.get("title", exp.get("position", ""))),
                    "company": exp.get("company", exp.get("employer", "")),
                    "start_date": exp.get("start_date", ""),
                    "end_date": exp.get("end_date", ""),
                    "description": exp.get("description", ""),
                })
        
        return structured_exp
    
    def _extract_education(self, content: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract education."""
        education = content.get("education", [])
        
        structured_edu = []
        for edu in education:
            if isinstance(edu, dict):
                structured_edu.append({
                    "degree": edu.get("degree", edu.get("qualification", "")),
                    "field_of_study": edu.get("field_of_study", ""),
                    "institution": edu.get("institution", edu.get("school", "")),
                })
        
        return structured_edu
    
    def _extract_summary(self, content: Dict[str, Any]) -> str:
        """Extract professional summary."""
        return content.get("summary", "") or ""
    
    def _extract_job_titles(self, content: Dict[str, Any]) -> List[str]:
        """Extract job titles from experience."""
        titles = []
        experience = content.get("experience", []) or content.get("work_experience", [])
        
        for exp in experience:
            if isinstance(exp, dict):
                title = exp.get("job_title", exp.get("title", exp.get("position", "")))
                if title:
                    titles.append(title)
        
        return list(set(titles))
    
    def _detect_industry(self, content: Dict[str, Any]) -> Optional[str]:
        """Detect industry from education/experience."""
        from app.services.industry_detector import IndustryDetector
        
        detector = IndustryDetector()
        
        # Check education first
        education = content.get("education", [])
        if education:
            field = education[0].get("field_of_study", "")
            if field:
                return detector.detect_industry(field)
        
        # Check experience for industry keywords
        experience = content.get("experience", []) or content.get("work_experience", [])
        for exp in experience:
            if isinstance(exp, dict):
                desc = exp.get("description", "").lower()
                if any(word in desc for word in ["software", "developer", "programming"]):
                    return "Technology"
                elif any(word in desc for word in ["business", "management", "sales"]):
                    return "Business"
        
        return None
    
    def _calculate_years_experience(self, content: Dict[str, Any]) -> int:
        """Calculate total years of experience."""
        from datetime import datetime
        
        experience = content.get("experience", []) or content.get("work_experience", [])
        total_months = 0
        
        for exp in experience:
            if isinstance(exp, dict):
                start_date = exp.get("start_date", "")
                end_date = exp.get("end_date", "")
                
                if start_date:
                    try:
                        start = datetime.fromisoformat(start_date[:7] + "-01")  # YYYY-MM
                        end = datetime.now() if not end_date or end_date.lower() == "present" else datetime.fromisoformat(end_date[:7] + "-01")
                        months = (end.year - start.year) * 12 + (end.month - start.month)
                        total_months += max(0, months)
                    except:
                        pass
        
        return total_months // 12
    
    def _extract_keywords(self, content: Dict[str, Any]) -> List[str]:
        """Extract keywords from CV."""
        keywords = []
        
        # From skills
        skills = self._extract_skills(content)
        keywords.extend(skills[:10])
        
        # From job titles
        titles = self._extract_job_titles(content)
        keywords.extend(titles[:5])
        
        # From summary
        summary = self._extract_summary(content)
        if summary:
            words = summary.split()
            keywords.extend([w for w in words if len(w) > 4][:10])
        
        return list(set(keywords))[:20]
    
    def _get_empty_structure(self) -> Dict[str, Any]:
        """Return empty structured CV."""
        return {
            "personal_info": {},
            "skills": [],
            "experience": [],
            "education": [],
            "summary": "",
            "job_titles": [],
            "industry": None,
            "years_experience": 0,
            "keywords": [],
        }
