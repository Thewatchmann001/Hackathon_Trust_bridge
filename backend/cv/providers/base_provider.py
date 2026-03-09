"""
Base Job Provider Interface
All job providers must implement this interface.
"""
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime
from app.utils.logger import logger
import asyncio


@dataclass
class JobSchema:
    """Unified job schema for all providers."""
    id: str
    title: str
    company: str
    location: str
    description: str
    skills: List[str]
    source: str
    url: str
    date: datetime
    embedding: Optional[List[float]] = None
    metadata: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "id": self.id,
            "title": self.title,
            "company": self.company,
            "location": self.location,
            "description": self.description,
            "skills": self.skills,
            "source": self.source,
            "url": self.url,
            "date": self.date.isoformat() if isinstance(self.date, datetime) else str(self.date),
            "embedding": self.embedding,
            "metadata": self.metadata or {}
        }


class BaseJobProvider(ABC):
    """Abstract base class for all job providers."""
    
    def __init__(self, name: str):
        self.name = name
        self.logger = logger
        self.enabled = True
        self.last_fetch_time = None
        self.last_fetch_count = 0
        self.error_count = 0
        self.rate_limit_hit = False
    
    @abstractmethod
    async def fetch_jobs(
        self,
        keywords: List[str],
        location: Optional[str] = None,
        limit: int = 50
    ) -> List[JobSchema]:
        """
        Fetch jobs from this provider.
        
        Args:
            keywords: Search keywords
            location: Location filter (optional)
            limit: Maximum number of jobs to return
            
        Returns:
            List of normalized JobSchema objects
        """
        pass
    
    @abstractmethod
    def normalize_job(self, raw_job: Dict[str, Any]) -> Optional[JobSchema]:
        """
        Normalize a raw job from the provider's API to JobSchema.
        
        Args:
            raw_job: Raw job data from provider API
            
        Returns:
            Normalized JobSchema or None if invalid
        """
        pass
    
    def is_enabled(self) -> bool:
        """Check if provider is enabled and configured."""
        return self.enabled
    
    def log_fetch(self, count: int, duration: float):
        """Log fetch metrics."""
        self.last_fetch_time = datetime.now()
        self.last_fetch_count = count
        self.logger.info(
            f"[{self.name}] Fetched {count} jobs in {duration:.2f}s"
        )
    
    def log_error(self, error: Exception):
        """Log provider error."""
        self.error_count += 1
        self.logger.error(
            f"[{self.name}] Error: {str(error)}",
            exc_info=True
        )
    
    def log_rate_limit(self):
        """Log rate limit hit."""
        self.rate_limit_hit = True
        self.logger.warning(f"[{self.name}] Rate limit hit")
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get provider metrics."""
        return {
            "name": self.name,
            "enabled": self.enabled,
            "last_fetch_count": self.last_fetch_count,
            "last_fetch_time": self.last_fetch_time.isoformat() if self.last_fetch_time else None,
            "error_count": self.error_count,
            "rate_limit_hit": self.rate_limit_hit
        }
    
    def extract_skills_from_text(self, text: str) -> List[str]:
        """Extract skills from job description text."""
        if not text:
            return []
        
        # Common technical skills
        skill_keywords = {
            "python", "javascript", "java", "typescript", "go", "rust", "c++", "c#",
            "react", "angular", "vue", "node.js", "django", "flask", "fastapi",
            "spring", "express", "postgresql", "mysql", "mongodb", "redis",
            "aws", "azure", "gcp", "docker", "kubernetes", "terraform",
            "machine learning", "ai", "data science", "tensorflow", "pytorch",
            "api", "rest", "graphql", "microservices", "agile", "scrum"
        }
        
        text_lower = text.lower()
        found_skills = []
        
        for skill in skill_keywords:
            if skill.lower() in text_lower:
                found_skills.append(skill.title())
        
        return list(set(found_skills))[:10]  # Max 10 skills
