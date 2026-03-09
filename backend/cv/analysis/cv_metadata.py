"""
CV Metadata
Extract and store CV metadata for fast matching.
"""
from typing import Dict, Any
from .cv_parser import CVParser


class CVMetadata:
    """CV metadata extractor."""
    
    def __init__(self):
        self.parser = CVParser()
    
    def extract_metadata(self, structured_cv: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract metadata from structured CV.
        
        Args:
            structured_cv: Parsed CV data
            
        Returns:
            Metadata dictionary
        """
        return {
            "skills": structured_cv.get("skills", []),
            "job_titles": structured_cv.get("job_titles", []),
            "industry": structured_cv.get("industry"),
            "years_experience": structured_cv.get("years_experience", 0),
            "keywords": structured_cv.get("keywords", []),
            "has_summary": bool(structured_cv.get("summary")),
            "has_experience": len(structured_cv.get("experience", [])) > 0,
            "has_education": len(structured_cv.get("education", [])) > 0,
        }
