"""
Learning Resources Service
Fetches free course links for skills from various platforms.
"""
from typing import List, Dict, Any
from app.utils.logger import logger


class LearningResourcesService:
    """Service to provide learning resources for skills."""
    
    def __init__(self):
        self.platforms = {
            "youtube": "YouTube",
            "coursera": "Coursera",
            "alison": "Alison",
            "udemy": "Udemy",
            "edx": "edX",
            "khan": "Khan Academy",
            "freecodecamp": "freeCodeCamp"
        }
    
    def get_resources_for_skill(self, skill: str, limit: int = 3) -> List[Dict[str, Any]]:
        """
        Get free learning resources for a skill.
        
        Args:
            skill: Skill name (e.g., "Python", "React", "AWS")
            limit: Maximum number of resources to return per platform
            
        Returns:
            List of learning resources with platform, title, and URL
        """
        skill_lower = skill.lower().strip()
        resources = []
        
        # Normalize skill name for URL generation
        skill_normalized = skill_lower.replace(" ", "-").replace("+", "plus")
        
        # YouTube resources
        youtube_urls = self._get_youtube_urls(skill, skill_normalized)
        for url in youtube_urls[:limit]:
            resources.append({
                "platform": "YouTube",
                "title": f"Learn {skill} - Free Tutorial",
                "url": url,
                "type": "video",
                "free": True
            })
        
        # Coursera free courses
        coursera_urls = self._get_coursera_urls(skill, skill_normalized)
        for url in coursera_urls[:limit]:
            resources.append({
                "platform": "Coursera",
                "title": f"{skill} Course - Free Audit",
                "url": url,
                "type": "course",
                "free": True
            })
        
        # Alison courses
        alison_urls = self._get_alison_urls(skill, skill_normalized)
        for url in alison_urls[:limit]:
            resources.append({
                "platform": "Alison",
                "title": f"Free {skill} Course",
                "url": url,
                "type": "course",
                "free": True
            })
        
        # freeCodeCamp
        freecodecamp_urls = self._get_freecodecamp_urls(skill, skill_normalized)
        for url in freecodecamp_urls[:limit]:
            resources.append({
                "platform": "freeCodeCamp",
                "title": f"Learn {skill} - Full Course",
                "url": url,
                "type": "course",
                "free": True
            })
        
        # edX free courses
        edx_urls = self._get_edx_urls(skill, skill_normalized)
        for url in edx_urls[:limit]:
            resources.append({
                "platform": "edX",
                "title": f"{skill} Course - Free Audit",
                "url": url,
                "type": "course",
                "free": True
            })
        
        return resources[:limit * 2]  # Return top resources across platforms
    
    def _get_youtube_urls(self, skill: str, skill_normalized: str) -> List[str]:
        """Generate YouTube search URLs for skill."""
        # Common YouTube channels and search patterns
        skill_encoded = skill.replace(" ", "+")
        
        urls = [
            f"https://www.youtube.com/results?search_query=learn+{skill_encoded}+tutorial+free",
            f"https://www.youtube.com/results?search_query={skill_encoded}+full+course+free",
            f"https://www.youtube.com/results?search_query={skill_encoded}+beginner+tutorial"
        ]
        
        # Add specific channel searches for popular skills
        popular_skills_channels = {
            "python": "https://www.youtube.com/results?search_query=python+programming+freecodecamp",
            "javascript": "https://www.youtube.com/results?search_query=javascript+full+course+freecodecamp",
            "react": "https://www.youtube.com/results?search_query=react+js+full+course+freecodecamp",
            "java": "https://www.youtube.com/results?search_query=java+programming+freecodecamp",
            "aws": "https://www.youtube.com/results?search_query=aws+cloud+practitioner+free",
            "docker": "https://www.youtube.com/results?search_query=docker+tutorial+freecodecamp",
            "kubernetes": "https://www.youtube.com/results?search_query=kubernetes+tutorial+free",
            "sql": "https://www.youtube.com/results?search_query=sql+database+freecodecamp",
            "node": "https://www.youtube.com/results?search_query=nodejs+full+course+freecodecamp",
            "html": "https://www.youtube.com/results?search_query=html+css+freecodecamp",
            "css": "https://www.youtube.com/results?search_query=html+css+freecodecamp",
            "git": "https://www.youtube.com/results?search_query=git+github+tutorial+free",
        }
        
        skill_lower = skill.lower()
        if skill_lower in popular_skills_channels:
            urls.insert(0, popular_skills_channels[skill_lower])
        
        return urls
    
    def _get_coursera_urls(self, skill: str, skill_normalized: str) -> List[str]:
        """Generate Coursera course URLs (free audit option)."""
        skill_encoded = skill.replace(" ", "+")
        
        urls = [
            f"https://www.coursera.org/search?query={skill_encoded}&index=prod_all_launched_products_term_optimization",
            f"https://www.coursera.org/courses?query={skill_encoded}&index=prod_all_launched_products_term_optimization"
        ]
        
        return urls
    
    def _get_alison_urls(self, skill: str, skill_normalized: str) -> List[str]:
        """Generate Alison course URLs."""
        skill_encoded = skill.replace(" ", "%20")
        
        urls = [
            f"https://alison.com/courses?query={skill_encoded}",
            f"https://alison.com/courses?search={skill_encoded}"
        ]
        
        return urls
    
    def _get_freecodecamp_urls(self, skill: str, skill_normalized: str) -> List[str]:
        """Generate freeCodeCamp course URLs."""
        skill_lower = skill.lower()
        
        # Map common skills to freeCodeCamp paths
        skill_paths = {
            "python": "https://www.freecodecamp.org/learn/scientific-computing-with-python/",
            "javascript": "https://www.freecodecamp.org/learn/javascript-algorithms-and-data-structures/",
            "react": "https://www.freecodecamp.org/learn/front-end-development-libraries/",
            "sql": "https://www.freecodecamp.org/learn/relational-database/",
            "html": "https://www.freecodecamp.org/learn/2022/responsive-web-design/",
            "css": "https://www.freecodecamp.org/learn/2022/responsive-web-design/",
            "node": "https://www.freecodecamp.org/learn/back-end-development-and-apis/",
            "aws": "https://www.freecodecamp.org/learn/",
            "docker": "https://www.freecodecamp.org/learn/",
            "git": "https://www.freecodecamp.org/learn/",
        }
        
        urls = []
        if skill_lower in skill_paths:
            urls.append(skill_paths[skill_lower])
        
        # Generic search
        urls.append(f"https://www.freecodecamp.org/news/search/?query={skill.replace(' ', '+')}")
        
        return urls
    
    def _get_edx_urls(self, skill: str, skill_normalized: str) -> List[str]:
        """Generate edX course URLs (free audit option)."""
        skill_encoded = skill.replace(" ", "+")
        
        urls = [
            f"https://www.edx.org/search?q={skill_encoded}",
            f"https://www.edx.org/course?search_query={skill_encoded}"
        ]
        
        return urls
