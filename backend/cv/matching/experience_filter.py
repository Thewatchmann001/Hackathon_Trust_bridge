"""
Experience Filter
Match jobs based on experience level requirements.
"""
from typing import Dict, Any, Optional
from app.utils.logger import logger


class ExperienceFilter:
    """Filter and score jobs based on experience level."""
    
    def calculate_score(
        self,
        cv_years_experience: int,
        job_metadata: Optional[Dict[str, Any]] = None
    ) -> float:
        """
        Calculate experience match score (0.0 to 1.0).
        
        Args:
            cv_years_experience: Years of experience from CV
            job_metadata: Job metadata (may contain experience requirements)
            
        Returns:
            Score between 0.0 and 1.0
        """
        # If no metadata, return neutral score
        if not job_metadata:
            return 0.5
        
        # Try to extract experience requirement from metadata
        min_experience = job_metadata.get("min_experience")
        experience_level = job_metadata.get("experience_level", "").lower()
        
        # If explicit min_experience
        if min_experience is not None:
            if cv_years_experience >= min_experience:
                return 1.0
            elif cv_years_experience >= min_experience * 0.7:  # Within 30%
                return 0.7
            else:
                return 0.3
        
        # If experience level string
        if experience_level:
            level_scores = {
                "entry": (0, 2),
                "junior": (1, 3),
                "mid": (2, 5),
                "senior": (4, 8),
                "lead": (6, 10),
                "principal": (8, 15),
            }
            
            for level, (min_years, max_years) in level_scores.items():
                if level in experience_level:
                    if min_years <= cv_years_experience <= max_years:
                        return 1.0
                    elif cv_years_experience < min_years:
                        return 0.5  # Underqualified but close
                    else:
                        return 0.8  # Overqualified but still relevant
        
        # Default: neutral score
        return 0.5
