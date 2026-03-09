"""
Adzuna Job Provider
Fetches jobs from Adzuna API.
"""
import requests
from typing import List, Dict, Any, Optional
from datetime import datetime
from .base_provider import BaseJobProvider, JobSchema
from app.core.config import settings
from app.utils.logger import logger


class AdzunaProvider(BaseJobProvider):
    """Adzuna job provider."""
    
    def __init__(self):
        super().__init__("Adzuna")
        self.base_url = "https://api.adzuna.com/v1/api/jobs"
        self.timeout = 10
        self.app_id = getattr(settings, 'ADZUNA_APP_ID', None)
        self.api_key = getattr(settings, 'ADZUNA_API_KEY', None)
        
        if not self.app_id or not self.api_key:
            self.enabled = False
            logger.warning("Adzuna API credentials not configured - provider disabled")
    
    async def fetch_jobs(
        self,
        keywords: List[str],
        location: Optional[str] = None,
        limit: int = 50
    ) -> List[JobSchema]:
        """Fetch jobs from Adzuna."""
        if not self.is_enabled():
            return []
        
        import asyncio
        
        try:
            start_time = datetime.now()
            
            # Adzuna uses country code (us, gb, etc.)
            country = "us"  # Default, can be made configurable
            url = f"{self.base_url}/{country}/search/1"
            
            # Build query from keywords
            query = ' '.join(keywords[:5])  # Limit keywords
            
            params = {
                'app_id': self.app_id,
                'app_key': self.api_key,
                'results_per_page': min(limit, 50),
                'what': query,
                'content-type': 'application/json'
            }
            
            if location:
                params['where'] = location
            
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: requests.get(url, params=params, timeout=self.timeout)
            )
            
            if response.status_code == 429:
                self.log_rate_limit()
                return []
            
            response.raise_for_status()
            data = response.json()
            
            jobs_data = data.get('results', [])
            normalized_jobs = []
            
            for job in jobs_data:
                normalized = self.normalize_job(job)
                if normalized:
                    normalized_jobs.append(normalized)
                
                if len(normalized_jobs) >= limit:
                    break
            
            duration = (datetime.now() - start_time).total_seconds()
            self.log_fetch(len(normalized_jobs), duration)
            
            return normalized_jobs
            
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 429:
                self.log_rate_limit()
            elif e.response.status_code == 401:
                self.enabled = False
                logger.error("Adzuna authentication failed - provider disabled")
            self.log_error(e)
            return []
        except Exception as e:
            self.log_error(e)
            return []
    
    def normalize_job(self, raw_job: Dict[str, Any]) -> Optional[JobSchema]:
        """Normalize Adzuna job to JobSchema."""
        try:
            description = raw_job.get('description', '')
            skills = self.extract_skills_from_text(description)
            
            # Parse date
            date_str = raw_job.get('created', '')
            try:
                job_date = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
            except:
                job_date = datetime.now()
            
            # Generate unique ID
            job_id = f"adzuna_{raw_job.get('id', '')}"
            
            return JobSchema(
                id=job_id,
                title=raw_job.get('title', 'Untitled Position'),
                company=raw_job.get('company', {}).get('display_name', 'Unknown Company'),
                location=raw_job.get('location', {}).get('display_name', 'Unknown'),
                description=description[:1000],
                skills=skills,
                source="Adzuna",
                url=raw_job.get('redirect_url', ''),
                date=job_date,
                metadata={
                    "salary_min": raw_job.get('salary_min'),
                    "salary_max": raw_job.get('salary_max'),
                    "salary_currency": raw_job.get('salary_is_predicted'),
                    "job_type": raw_job.get('contract_type', 'Full-time')
                }
            )
        except Exception as e:
            self.logger.warning(f"Failed to normalize Adzuna job: {e}")
            return None
