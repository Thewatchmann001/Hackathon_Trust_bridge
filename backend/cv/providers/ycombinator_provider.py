"""
Y-Combinator Jobs Provider
Fetches startup jobs from Y-Combinator via RapidAPI.
"""
import http.client
import json
from typing import List, Dict, Any, Optional
from datetime import datetime
from .base_provider import BaseJobProvider, JobSchema
from app.core.config import settings
from app.utils.logger import logger


class YCombinatorProvider(BaseJobProvider):
    """Y-Combinator jobs provider via RapidAPI."""
    
    def __init__(self):
        super().__init__("Y-Combinator")
        self.host = "free-y-combinator-jobs-api.p.rapidapi.com"
        self.timeout = 10
        self.rapidapi_key = getattr(settings, 'RAPIDAPI_KEY', None)
        
        if not self.rapidapi_key:
            self.enabled = False
            logger.warning("RapidAPI key not configured - Y-Combinator provider disabled")
    
    async def fetch_jobs(
        self,
        keywords: List[str],
        location: Optional[str] = None,
        limit: int = 50
    ) -> List[JobSchema]:
        """Fetch jobs from Y-Combinator."""
        if not self.is_enabled():
            return []
        
        import asyncio
        
        try:
            start_time = datetime.now()
            
            # Build query from keywords
            query = ' '.join(keywords[:3])
            
            conn = http.client.HTTPSConnection(self.host, timeout=self.timeout)
            headers = {
                'X-RapidAPI-Key': self.rapidapi_key,
                'X-RapidAPI-Host': self.host
            }
            
            # Use the active jobs endpoint
            endpoint = "/active-jb-7d"
            
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: self._make_request(conn, endpoint, headers)
            )
            
            if response.get('status') == 429:
                self.log_rate_limit()
                return []
            
            # Handle both list and dict responses
            if isinstance(response, list):
                jobs_data = response
            else:
                jobs_data = response.get('data', [])
            
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
            
        except Exception as e:
            self.log_error(e)
            return []
    
    def _make_request(self, conn, endpoint: str, headers: dict) -> dict:
        """Make HTTP request."""
        try:
            conn.request("GET", endpoint, headers=headers)
            response = conn.getresponse()
            
            if response.status == 429:
                return {'status': 429}
            
            if response.status != 200:
                logger.warning(f"Y-Combinator API returned status {response.status}")
                return {}
            
            data = json.loads(response.read().decode())
            return data
        except Exception as e:
            logger.error(f"Y-Combinator API request failed: {e}")
            return {}
    
    def normalize_job(self, raw_job: Dict[str, Any]) -> Optional[JobSchema]:
        """Normalize Y-Combinator job to JobSchema."""
        try:
            description = raw_job.get('description', '')
            skills = self.extract_skills_from_text(description)
            
            # Parse date
            date_str = raw_job.get('posted_date', '')
            try:
                job_date = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
            except:
                job_date = datetime.now()
            
            job_id = f"yc_{raw_job.get('id', '')}"
            
            return JobSchema(
                id=job_id,
                title=raw_job.get('title', 'Untitled Position'),
                company=raw_job.get('company', 'Unknown Company'),
                location=raw_job.get('location', 'Remote'),
                description=description[:1000],
                skills=skills,
                source="Y-Combinator",
                url=raw_job.get('url', ''),
                date=job_date,
                metadata={
                    "job_type": "Startup Job",
                    "yc_batch": raw_job.get('batch', '')
                }
            )
        except Exception as e:
            self.logger.warning(f"Failed to normalize Y-Combinator job: {e}")
            return None
