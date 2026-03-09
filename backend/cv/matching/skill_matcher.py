"""
Skill Matcher
Calculate skill overlap percentage between CV and job.
"""
from typing import List
from app.utils.logger import logger


class SkillMatcher:
    """Match jobs based on skill overlap."""
    
    def calculate_score(
        self,
        cv_skills: List[str],
        job_skills: List[str]
    ) -> float:
        """
        Calculate skill overlap score (0.0 to 1.0).
        
        Args:
            cv_skills: Skills from CV
            job_skills: Skills required for job
            
        Returns:
            Score between 0.0 and 1.0
        """
        if not job_skills:
            return 0.5  # Neutral score if job has no skills listed
        
        if not cv_skills:
            return 0.0
        
        # Normalize skills (lowercase, strip)
        cv_skills_normalized = [s.lower().strip() for s in cv_skills]
        job_skills_normalized = [s.lower().strip() for s in job_skills]
        
        # Count matches
        matches = 0
        for job_skill in job_skills_normalized:
            # Exact match
            if job_skill in cv_skills_normalized:
                matches += 1
            else:
                # Partial match (e.g., "python" matches "python programming")
                for cv_skill in cv_skills_normalized:
                    if job_skill in cv_skill or cv_skill in job_skill:
                        matches += 1
                        break
        
        # Score is percentage of job skills matched
        score = matches / len(job_skills_normalized) if job_skills_normalized else 0.0
        
        return min(1.0, score)
