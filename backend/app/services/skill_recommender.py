"""
Skill Recommendation Service
Recommends skills based on field of study, experience, and industry.
"""
from typing import Dict, Any, List, Optional
from app.utils.logger import logger
from app.services.industry_detector import IndustryDetector


class SkillRecommender:
    """Recommend skills based on context."""
    
    def __init__(self):
        self.industry_detector = IndustryDetector()
    
    def recommend_skills_from_field(
        self, 
        field_of_study: str, 
        count: int = 12
    ) -> Dict[str, List[str]]:
        """
        Recommend skills based on field of study.
        
        Args:
            field_of_study: The field of study
            count: Number of skills to recommend (default 12)
            
        Returns:
            Dictionary with technical, soft, and tools skills
        """
        if not field_of_study:
            return {"technical": [], "soft": [], "tools": []}
        
        # Detect industry from field
        industry = self.industry_detector.detect_industry(field_of_study)
        
        # Get industry skills
        industry_skills = self.industry_detector.get_industry_skills(industry)
        
        # Return recommended skills (limit to count)
        return {
            "technical": industry_skills.get("technical", [])[:count],
            "soft": industry_skills.get("soft", [])[:count],
            "tools": industry_skills.get("tools", [])[:count]
        }
    
    def recommend_skills_from_experience(
        self, 
        experience_list: List[Dict[str, Any]]
    ) -> List[str]:
        """
        Recommend skills based on work experience.
        
        Args:
            experience_list: List of work experience entries
            
        Returns:
            List of recommended skills
        """
        if not experience_list:
            return []
        
        recommended = []
        
        # Extract skills from job titles and descriptions
        for exp in experience_list:
            job_title = (exp.get("job_title") or exp.get("title") or "").lower()
            description = (exp.get("description") or "").lower()
            
            # Common technical skills from job titles
            if any(word in job_title for word in ["developer", "engineer", "programmer"]):
                recommended.extend(["Programming", "Software Development", "Problem Solving"])
            if any(word in job_title for word in ["manager", "lead", "director"]):
                recommended.extend(["Leadership", "Project Management", "Team Management"])
            if any(word in job_title for word in ["analyst", "data"]):
                recommended.extend(["Data Analysis", "Analytical Thinking", "Reporting"])
            if any(word in job_title for word in ["designer", "design"]):
                recommended.extend(["Design", "Creativity", "User Experience"])
        
        # Remove duplicates and return
        return list(set(recommended))[:10]
    
    def recommend_complementary_skills(
        self, 
        selected_skills: List[str], 
        industry: str
    ) -> List[str]:
        """
        Recommend complementary skills to fill gaps.
        
        Args:
            selected_skills: Already selected skills
            industry: Industry name
            
        Returns:
            List of complementary skills
        """
        industry_skills = self.industry_detector.get_industry_skills(industry)
        
        # Get all recommended skills for industry
        all_technical = industry_skills.get("technical", [])
        all_soft = industry_skills.get("soft", [])
        all_tools = industry_skills.get("tools", [])
        
        # Find skills not yet selected
        selected_lower = [s.lower() for s in selected_skills]
        complementary = []
        
        for skill_list in [all_technical, all_soft, all_tools]:
            for skill in skill_list:
                if skill.lower() not in selected_lower:
                    complementary.append(skill)
        
        return complementary[:8]  # Return top 8 complementary skills
    
    def get_all_recommended_skills(
        self,
        field_of_study: str,
        experience_list: Optional[List[Dict[str, Any]]] = None,
        selected_skills: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Get comprehensive skill recommendations.
        
        Args:
            field_of_study: Field of study
            experience_list: Work experience
            selected_skills: Already selected skills
            
        Returns:
            Dictionary with all recommended skills
        """
        # Get skills from field
        field_skills = self.recommend_skills_from_field(field_of_study, count=12)
        
        # Get skills from experience
        experience_skills = self.recommend_skills_from_experience(experience_list or [])
        
        # Detect industry
        industry = self.industry_detector.detect_industry(field_of_study)
        
        # Get complementary skills
        all_selected = (selected_skills or []) + experience_skills
        complementary = self.recommend_complementary_skills(all_selected, industry)
        
        # Combine and deduplicate
        all_technical = list(set(field_skills.get("technical", []) + experience_skills))
        all_soft = list(set(field_skills.get("soft", [])))
        all_tools = list(set(field_skills.get("tools", [])))
        
        return {
            "recommended": {
                "technical": all_technical[:12],
                "soft": all_soft[:8],
                "tools": all_tools[:8]
            },
            "from_experience": experience_skills,
            "complementary": complementary,
            "industry": industry
        }
