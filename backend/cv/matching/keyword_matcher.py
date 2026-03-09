"""
Keyword Matcher
Calculate keyword overlap score between CV and job.
"""
from typing import List, Dict, Any
from app.utils.logger import logger


class KeywordMatcher:
    """Match jobs based on keyword overlap."""
    
    def calculate_score(
        self,
        cv_keywords: List[str],
        job_title: str,
        job_description: str,
        job_skills: List[str]
    ) -> float:
        """
        Calculate keyword overlap score (0.0 to 1.0).
        
        Args:
            cv_keywords: Keywords from CV
            job_title: Job title
            job_description: Job description
            job_skills: Job skills
            
        Returns:
            Score between 0.0 and 1.0
        """
        if not cv_keywords:
            return 0.0
        
        # Combine job text
        job_text = f"{job_title} {job_description} {' '.join(job_skills)}".lower()
        
        # Count matches
        matches = 0
        for keyword in cv_keywords:
            keyword_lower = keyword.lower()
            if keyword_lower in job_text:
                matches += 1
        
        # Score based on match percentage
        score = matches / len(cv_keywords) if cv_keywords else 0.0
        
        # Boost score if title matches (title is more important)
        if cv_keywords:
            title_lower = job_title.lower()
            title_matches = sum(1 for kw in cv_keywords if kw.lower() in title_lower)
            if title_matches > 0:
                score = min(1.0, score + 0.2)  # Boost by 0.2 for title match
        
        return min(1.0, score)
