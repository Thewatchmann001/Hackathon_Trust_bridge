"""
Fallback Matcher
Provide fallback matching when no good matches found.
"""
from typing import List, Dict, Any, Optional
from app.utils.logger import logger
from cv.providers.base_provider import JobSchema


class FallbackMatcher:
    """Fallback matching strategies."""
    
    def get_fallback_jobs(
        self,
        all_jobs: List[JobSchema],
        cv_industry: Optional[str],
        cv_keywords: List[str],
        limit: int = 10
    ) -> List[JobSchema]:
        """
        Get fallback jobs when no good matches found.
        
        Args:
            all_jobs: All available jobs
            cv_industry: CV industry
            cv_keywords: CV keywords
            limit: Number of jobs to return
            
        Returns:
            List of fallback jobs
        """
        if not all_jobs:
            return []
        
        fallback_jobs = []
        
        # Strategy 1: Industry-based matching
        if cv_industry:
            industry_jobs = [
                job for job in all_jobs
                if cv_industry.lower() in job.description.lower() or
                   cv_industry.lower() in job.title.lower()
            ]
            fallback_jobs.extend(industry_jobs[:limit])
        
        # Strategy 2: Keyword-based (broader match)
        if cv_keywords and len(fallback_jobs) < limit:
            keyword_jobs = []
            for job in all_jobs:
                job_text = f"{job.title} {job.description}".lower()
                # Match if any keyword appears
                if any(kw.lower() in job_text for kw in cv_keywords[:5]):
                    keyword_jobs.append(job)
            
            # Add jobs not already in fallback
            existing_ids = {job.id for job in fallback_jobs}
            for job in keyword_jobs:
                if job.id not in existing_ids:
                    fallback_jobs.append(job)
                    if len(fallback_jobs) >= limit:
                        break
        
        # Strategy 3: Just return recent jobs if still not enough
        if len(fallback_jobs) < limit:
            # Sort by date (newest first)
            sorted_jobs = sorted(all_jobs, key=lambda x: x.date, reverse=True)
            existing_ids = {job.id for job in fallback_jobs}
            for job in sorted_jobs:
                if job.id not in existing_ids:
                    fallback_jobs.append(job)
                    if len(fallback_jobs) >= limit:
                        break
        
        logger.info(f"Fallback matcher returned {len(fallback_jobs)} jobs")
        
        return fallback_jobs[:limit]
