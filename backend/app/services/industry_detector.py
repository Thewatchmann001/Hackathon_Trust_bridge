"""
Industry Detection Service
Detects industry from education field of study and provides industry-specific insights.
"""
from typing import Dict, Any, List, Optional
from app.utils.logger import logger


class IndustryDetector:
    """Detect industry from field of study and provide industry insights."""
    
    # Industry mapping based on field of study keywords
    FIELD_TO_INDUSTRY = {
        # Business & Finance
        "business": "Business",
        "finance": "Business",
        "accounting": "Business",
        "economics": "Business",
        "marketing": "Business",
        "management": "Business",
        "mba": "Business",
        "commerce": "Business",
        
        # Engineering
        "engineering": "Engineering",
        "mechanical": "Engineering",
        "electrical": "Engineering",
        "civil": "Engineering",
        "chemical": "Engineering",
        "aerospace": "Engineering",
        "industrial": "Engineering",
        
        # Computer Science & Technology
        "computer": "Technology",
        "software": "Technology",
        "information": "Technology",
        "it": "Technology",
        "data": "Technology",
        "cybersecurity": "Technology",
        "artificial intelligence": "Technology",
        "machine learning": "Technology",
        
        # Medicine & Healthcare
        "medicine": "Healthcare",
        "medical": "Healthcare",
        "nursing": "Healthcare",
        "pharmacy": "Healthcare",
        "public health": "Healthcare",
        "biomedical": "Healthcare",
        "health": "Healthcare",
        
        # Law
        "law": "Law",
        "legal": "Law",
        "jurisprudence": "Law",
        
        # Education
        "education": "Education",
        "teaching": "Education",
        "pedagogy": "Education",
        
        # Science
        "science": "Science",
        "physics": "Science",
        "chemistry": "Science",
        "biology": "Science",
        "mathematics": "Science",
        "statistics": "Science",
        
        # Arts & Humanities
        "arts": "Arts",
        "humanities": "Arts",
        "literature": "Arts",
        "history": "Arts",
        "philosophy": "Arts",
    }
    
    # Industry-specific skill categories
    INDUSTRY_SKILLS = {
        "Business": {
            "technical": ["Financial Analysis", "Data Analysis", "Project Management", "Business Strategy", "Market Research"],
            "soft": ["Leadership", "Communication", "Negotiation", "Strategic Thinking", "Problem Solving"],
            "tools": ["Excel", "PowerPoint", "Salesforce", "Tableau", "SQL"]
        },
        "Engineering": {
            "technical": ["CAD", "Systems Design", "Technical Documentation", "Quality Assurance", "Project Management"],
            "soft": ["Problem Solving", "Attention to Detail", "Team Collaboration", "Critical Thinking"],
            "tools": ["AutoCAD", "MATLAB", "SolidWorks", "Project Management Tools"]
        },
        "Technology": {
            "technical": ["Programming", "Software Development", "Database Management", "Cloud Computing", "DevOps"],
            "soft": ["Problem Solving", "Collaboration", "Continuous Learning", "Adaptability"],
            "tools": ["Git", "Docker", "AWS", "CI/CD Tools", "IDEs"]
        },
        "Healthcare": {
            "technical": ["Patient Care", "Medical Procedures", "Healthcare Compliance", "Medical Documentation"],
            "soft": ["Empathy", "Communication", "Attention to Detail", "Stress Management"],
            "tools": ["Electronic Health Records", "Medical Software", "Diagnostic Tools"]
        },
        "Law": {
            "technical": ["Legal Research", "Case Analysis", "Compliance", "Contract Review"],
            "soft": ["Analytical Thinking", "Communication", "Attention to Detail", "Ethics"],
            "tools": ["Legal Databases", "Case Management Software", "Document Management"]
        },
        "Education": {
            "technical": ["Curriculum Development", "Educational Technology", "Assessment Design"],
            "soft": ["Patience", "Communication", "Adaptability", "Empathy"],
            "tools": ["Learning Management Systems", "Educational Software"]
        },
        "Science": {
            "technical": ["Research Methodology", "Data Analysis", "Laboratory Techniques", "Statistical Analysis"],
            "soft": ["Critical Thinking", "Problem Solving", "Attention to Detail"],
            "tools": ["Statistical Software", "Laboratory Equipment", "Data Analysis Tools"]
        },
        "Arts": {
            "technical": ["Creative Design", "Content Creation", "Digital Media"],
            "soft": ["Creativity", "Communication", "Adaptability"],
            "tools": ["Design Software", "Content Management Systems"]
        }
    }
    
    # Industry-specific ATS keywords
    INDUSTRY_KEYWORDS = {
        "Business": ["leadership", "strategy", "analytics", "operations", "management", "financial", "revenue", "growth"],
        "Engineering": ["technical", "systems", "design", "implementation", "optimization", "quality", "standards"],
        "Technology": ["programming", "development", "frameworks", "algorithms", "architecture", "deployment", "scalability"],
        "Healthcare": ["patient care", "compliance", "medical", "treatment", "diagnosis", "safety", "protocols"],
        "Law": ["research", "compliance", "legal", "litigation", "contracts", "regulations", "analysis"],
        "Education": ["curriculum", "teaching", "learning", "pedagogy", "assessment", "student", "instruction"],
        "Science": ["research", "analysis", "methodology", "experimentation", "data", "hypothesis", "publication"],
        "Arts": ["creative", "design", "content", "media", "visual", "communication", "aesthetic"]
    }
    
    def detect_industry(self, field_of_study: str) -> str:
        """
        Detect industry from field of study.
        
        Args:
            field_of_study: The field of study (e.g., "Computer Science", "Business Administration")
            
        Returns:
            Detected industry name or "General" if not found
        """
        if not field_of_study:
            return "General"
        
        field_lower = field_of_study.lower().strip()
        
        # Check for exact matches first
        for keyword, industry in self.FIELD_TO_INDUSTRY.items():
            if keyword in field_lower:
                logger.info(f"Detected industry '{industry}' from field '{field_of_study}'")
                return industry
        
        # Default to General if no match
        logger.info(f"No industry match found for '{field_of_study}', defaulting to 'General'")
        return "General"
    
    def get_industry_skills(self, industry: str) -> Dict[str, List[str]]:
        """
        Get recommended skills for an industry.
        
        Args:
            industry: Industry name
            
        Returns:
            Dictionary with technical, soft, and tools skills
        """
        return self.INDUSTRY_SKILLS.get(industry, {
            "technical": [],
            "soft": [],
            "tools": []
        })
    
    def get_industry_keywords(self, industry: str) -> List[str]:
        """
        Get ATS keywords for an industry.
        
        Args:
            industry: Industry name
            
        Returns:
            List of ATS keywords
        """
        return self.INDUSTRY_KEYWORDS.get(industry, [])
    
    def get_industry_insights(self, industry: str) -> Dict[str, Any]:
        """
        Get comprehensive industry insights.
        
        Args:
            industry: Industry name
            
        Returns:
            Dictionary with skills, keywords, and recommendations
        """
        return {
            "industry": industry,
            "skills": self.get_industry_skills(industry),
            "keywords": self.get_industry_keywords(industry),
            "recommendations": self._get_industry_recommendations(industry)
        }
    
    def _get_industry_recommendations(self, industry: str) -> List[str]:
        """Get industry-specific CV recommendations."""
        recommendations = {
            "Business": [
                "Highlight leadership experience and quantifiable business results",
                "Emphasize strategic thinking and decision-making",
                "Include metrics: revenue growth, cost reduction, team size"
            ],
            "Engineering": [
                "Focus on technical projects and problem-solving",
                "Include specific technologies and tools used",
                "Highlight design, implementation, and optimization achievements"
            ],
            "Technology": [
                "Showcase programming languages and frameworks",
                "Include project portfolios and GitHub links",
                "Emphasize problem-solving and technical depth"
            ],
            "Healthcare": [
                "Highlight patient care experience and outcomes",
                "Include certifications and compliance knowledge",
                "Emphasize attention to detail and empathy"
            ],
            "Law": [
                "Showcase research and analytical skills",
                "Include case outcomes and legal achievements",
                "Highlight compliance and regulatory knowledge"
            ],
            "Education": [
                "Emphasize teaching experience and student outcomes",
                "Include curriculum development and innovation",
                "Highlight communication and adaptability"
            ],
            "Science": [
                "Focus on research methodology and findings",
                "Include publications and research contributions",
                "Emphasize analytical and critical thinking"
            ],
            "Arts": [
                "Showcase creative projects and portfolios",
                "Include design tools and software proficiency",
                "Highlight communication and visual skills"
            ]
        }
        
        return recommendations.get(industry, [
            "Tailor your CV to the specific role",
            "Highlight relevant experience and achievements",
            "Use industry-specific keywords"
        ])
