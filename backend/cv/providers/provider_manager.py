"""
Provider Manager
Orchestrates all job providers with parallel fetching and deduplication.
"""
import asyncio
from typing import List, Dict, Any, Optional
from datetime import datetime
from .base_provider import BaseJobProvider, JobSchema
from .remoteok_provider import RemoteOKProvider
from .arbeitnow_provider import ArbeitnowProvider
from .freelancer_provider import FreelancerProvider
from .adzuna_provider import AdzunaProvider
from .ycombinator_provider import YCombinatorProvider
from .internships_provider import InternshipsProvider
from app.utils.logger import logger


class ProviderManager:
    """Manages all job providers with parallel fetching."""
    
    def __init__(self):
        self.providers: List[BaseJobProvider] = []
        self._initialize_providers()
    
    def _initialize_providers(self):
        """Initialize all available providers."""
        self.providers = [
            RemoteOKProvider(),
            ArbeitnowProvider(),
            FreelancerProvider(),
            AdzunaProvider(),
            YCombinatorProvider(),
            InternshipsProvider(),
        ]
        
        # Log enabled providers
        enabled = [p.name for p in self.providers if p.is_enabled()]
        disabled = [p.name for p in self.providers if not p.is_enabled()]
        
        logger.info(f"Job Providers - Enabled: {enabled}")
        if disabled:
            logger.info(f"Job Providers - Disabled: {disabled}")
    
    async def fetch_all_jobs(
        self,
        keywords: List[str],
        location: Optional[str] = None,
        limit_per_provider: int = 25,
        total_limit: int = 100
    ) -> List[JobSchema]:
        """
        Fetch jobs from all enabled providers in parallel.
        
        Args:
            keywords: Search keywords
            location: Location filter (optional)
            limit_per_provider: Max jobs per provider
            total_limit: Total jobs to return after deduplication
            
        Returns:
            List of normalized, deduplicated jobs
        """
        start_time = datetime.now()
        
        # Filter enabled providers
        enabled_providers = [p for p in self.providers if p.is_enabled()]
        
        if not enabled_providers:
            logger.warning("No enabled job providers available")
            return []
        
        logger.info(f"Fetching jobs from {len(enabled_providers)} providers with keywords: {keywords[:3]}...")
        
        # Fetch from all providers in parallel
        tasks = [
            provider.fetch_jobs(keywords, location, limit_per_provider)
            for provider in enabled_providers
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Collect all jobs
        all_jobs = []
        provider_counts = {}
        
        for i, result in enumerate(results):
            provider_name = enabled_providers[i].name
            if isinstance(result, Exception):
                logger.error(f"Provider {provider_name} failed: {result}")
                provider_counts[provider_name] = 0
            else:
                all_jobs.extend(result)
                provider_counts[provider_name] = len(result)
                logger.info(f"[{provider_name}] Returned {len(result)} jobs")
        
        # Deduplicate jobs
        deduplicated = self._deduplicate_jobs(all_jobs)
        
        # Sort by date (newest first)
        deduplicated.sort(key=lambda x: x.date, reverse=True)
        
        # Limit results
        final_jobs = deduplicated[:total_limit]
        
        duration = (datetime.now() - start_time).total_seconds()
        
        logger.info(
            f"Job Fetch Complete - "
            f"Providers: {provider_counts}, "
            f"Total: {len(all_jobs)}, "
            f"Deduplicated: {len(deduplicated)}, "
            f"Final: {len(final_jobs)}, "
            f"Duration: {duration:.2f}s"
        )
        
        return final_jobs
    
    def _deduplicate_jobs(self, jobs: List[JobSchema]) -> List[JobSchema]:
        """
        Remove duplicate jobs based on title + company + location similarity.
        
        Args:
            jobs: List of jobs to deduplicate
            
        Returns:
            Deduplicated list
        """
        seen = set()
        unique_jobs = []
        
        for job in jobs:
            # Create a key from title, company, and location (normalized)
            key = self._create_job_key(job)
            
            if key not in seen:
                seen.add(key)
                unique_jobs.append(job)
            else:
                # If duplicate found, keep the one with more skills/info
                for i, existing in enumerate(unique_jobs):
                    if self._create_job_key(existing) == key:
                        if len(job.skills) > len(existing.skills):
                            unique_jobs[i] = job
                        break
        
        return unique_jobs
    
    def _create_job_key(self, job: JobSchema) -> str:
        """Create a unique key for deduplication."""
        # Normalize: lowercase, remove special chars, strip
        title = ''.join(c.lower() for c in job.title if c.isalnum() or c.isspace()).strip()
        company = ''.join(c.lower() for c in job.company if c.isalnum() or c.isspace()).strip()
        location = ''.join(c.lower() for c in job.location if c.isalnum() or c.isspace()).strip()
        
        return f"{title}|{company}|{location}"
    
    def get_provider_metrics(self) -> Dict[str, Any]:
        """Get metrics from all providers."""
        return {
            "providers": [p.get_metrics() for p in self.providers],
            "enabled_count": sum(1 for p in self.providers if p.is_enabled()),
            "total_count": len(self.providers)
        }
