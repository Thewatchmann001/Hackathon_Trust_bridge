"""
New Job Matcher
Main integration point for the redesigned job matching system.
"""
from typing import List, Dict, Any, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from cv.providers.provider_manager import ProviderManager
from cv.matching.hybrid_matcher import HybridMatcher
from cv.analysis.cv_cache import CVCache
from cv.analysis.cv_parser import CVParser
from app.utils.logger import logger


class NewJobMatcher:
    """New job matching system with modular providers and hybrid matching."""
    
    def __init__(self):
        self.provider_manager = ProviderManager()
        self.hybrid_matcher = HybridMatcher()
        self.cv_cache = CVCache()
        self.cv_parser = CVParser()
    
    async def match_cv_to_jobs(
        self,
        cv_id: int,
        keywords: Optional[List[str]] = None,
        location: Optional[str] = None,
        limit: int = 50,
        db: Session = None
    ) -> Dict[str, Any]:
        """
        Match CV to jobs using the new system.
        
        Args:
            cv_id: CV ID
            keywords: Optional keywords (will be extracted from CV if not provided)
            location: Optional location filter
            limit: Maximum number of results
            db: Database session
            
        Returns:
            Dictionary with matched jobs and metadata
        """
        start_time = datetime.now()
        
        # Get parsed CV
        parsed_cv = self.cv_cache.get_parsed_cv(cv_id, db)
        if not parsed_cv:
            logger.error(f"CV {cv_id} not found")
            return {
                "success": False,
                "error": "CV not found",
                "jobs": [],
                "metadata": {}
            }
        
        # Extract keywords from CV if not provided
        if not keywords:
            keywords = parsed_cv.get("keywords", [])
            # Also add skills and job titles
            keywords.extend(parsed_cv.get("skills", [])[:10])
            keywords.extend(parsed_cv.get("job_titles", [])[:5])
            keywords = list(set(keywords))[:15]  # Deduplicate and limit
        
        logger.info(f"Matching CV {cv_id} with keywords: {keywords[:5]}...")
        
        # Fetch jobs from all providers
        jobs = await self.provider_manager.fetch_all_jobs(
            keywords=keywords,
            location=location,
            limit_per_provider=25,
            total_limit=200  # Fetch more for better matching
        )
        
        if not jobs:
            logger.warning(f"No jobs fetched for CV {cv_id}")
            return {
                "success": False,
                "error": "No jobs available",
                "jobs": [],
                "metadata": {
                    "provider_metrics": self.provider_manager.get_provider_metrics()
                }
            }
        
        logger.info(f"Fetched {len(jobs)} jobs, now matching...")
        
        # Match jobs using hybrid matcher
        matched_jobs = self.hybrid_matcher.match_jobs(
            cv_id=cv_id,
            jobs=jobs,
            db=db,
            min_score=0.1,  # Low threshold to ensure results
            limit=limit
        )
        
        duration = (datetime.now() - start_time).total_seconds()
        
        # Get provider metrics
        provider_metrics = self.provider_manager.get_provider_metrics()
        
        return {
            "success": True,
            "jobs": matched_jobs,
            "metadata": {
                "total_jobs_fetched": len(jobs),
                "matched_jobs": len(matched_jobs),
                "duration_seconds": round(duration, 2),
                "provider_metrics": provider_metrics,
                "cv_keywords": keywords[:10],
            }
        }
