"""
CV Wizard Service
Main orchestration service for the guided CV creation wizard.
"""
from typing import Dict, Any, List, Optional
from app.utils.logger import logger
from app.services.industry_detector import IndustryDetector
from app.services.skill_recommender import SkillRecommender
from app.services.experience_enhancer import ExperienceEnhancer
from app.services.summary_generator import SummaryGenerator
from cv.cv_generator import CVGenerator


class CVWizardService:
    """Main service for CV wizard orchestration."""
    
    def __init__(self):
        self.industry_detector = IndustryDetector()
        self.skill_recommender = SkillRecommender()
        self.experience_enhancer = ExperienceEnhancer()
        self.summary_generator = SummaryGenerator()
        self.cv_generator = CVGenerator()
    
    def process_wizard_step(
        self,
        step_number: int,
        step_data: Dict[str, Any],
        previous_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Process a single wizard step.
        
        Args:
            step_number: Step number (1-6)
            step_data: Data for current step
            previous_data: Data from previous steps
            
        Returns:
            Processed data with suggestions and next step info
        """
        previous_data = previous_data or {}
        
        if step_number == 1:
            # Step 1: Basic Info - no processing needed
            return {
                "success": True,
                "processed_data": step_data,
                "suggestions": [],
                "next_step": 2
            }
        
        elif step_number == 2:
            # Step 2: Education - detect industry
            field_of_study = step_data.get("field_of_study", "")
            industry = self.industry_detector.detect_industry(field_of_study)
            industry_insights = self.industry_detector.get_industry_insights(industry)
            
            return {
                "success": True,
                "processed_data": {
                    **step_data,
                    "detected_industry": industry
                },
                "suggestions": industry_insights.get("recommendations", []),
                "industry": industry,
                "industry_insights": industry_insights,
                "next_step": 3
            }
        
        elif step_number == 3:
            # Step 3: Experience - enhance descriptions
            industry = previous_data.get("step2", {}).get("detected_industry")
            enhanced_experience = []
            
            for exp in step_data.get("experience", []):
                job_title = exp.get("job_title", "")
                company = exp.get("company", "")
                description = exp.get("description", "")
                
                # Enhance description
                enhanced_bullets = self.experience_enhancer.enhance_experience_description(
                    job_title, company, description, industry
                )
                
                enhanced_experience.append({
                    **exp,
                    "enhanced_bullets": enhanced_bullets,
                    "description": description  # Keep original
                })
            
            return {
                "success": True,
                "processed_data": {
                    **step_data,
                    "experience": enhanced_experience
                },
                "suggestions": [],
                "next_step": 4
            }
        
        elif step_number == 4:
            # Step 4: Skills - recommend skills
            field_of_study = previous_data.get("step2", {}).get("field_of_study", "")
            experience = previous_data.get("step3", {}).get("experience", [])
            selected_skills = step_data.get("selected_skills", [])
            
            recommendations = self.skill_recommender.get_all_recommended_skills(
                field_of_study,
                experience,
                selected_skills
            )
            
            return {
                "success": True,
                "processed_data": step_data,
                "recommendations": recommendations,
                "next_step": 5
            }
        
        elif step_number == 5:
            # Step 5: Summary - generate summary
            basic_info = previous_data.get("step1", {})
            education = previous_data.get("step2", {}).get("education", [])
            experience = previous_data.get("step3", {}).get("experience", [])
            skills = previous_data.get("step4", {}).get("skills", {})
            industry = previous_data.get("step2", {}).get("detected_industry")
            
            # Generate summary
            summary = self.summary_generator.generate_summary(
                basic_info, education, experience, skills, industry
            )
            
            # Generate variations
            variations = self.summary_generator.generate_summary_variations(
                basic_info, education, experience, skills, industry, count=3
            )
            
            return {
                "success": True,
                "processed_data": {
                    **step_data,
                    "generated_summary": summary,
                    "summary_variations": variations
                },
                "suggestions": [],
                "next_step": 6
            }
        
        elif step_number == 6:
            # Step 6: Preview - generate final CV
            return {
                "success": True,
                "processed_data": step_data,
                "suggestions": [],
                "next_step": None  # Complete
            }
        
        else:
            return {
                "success": False,
                "error": f"Invalid step number: {step_number}",
                "next_step": None
            }
    
    def validate_step_data(self, step_number: int, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate step data.
        
        Args:
            step_number: Step number
            data: Step data
            
        Returns:
            Validation result
        """
        errors = []
        
        if step_number == 1:
            # Validate basic info
            if not data.get("full_name"):
                errors.append("Full name is required")
            if not data.get("email"):
                errors.append("Email is required")
            elif "@" not in data.get("email", ""):
                errors.append("Invalid email format")
        
        elif step_number == 2:
            # Validate education
            if not data.get("field_of_study"):
                errors.append("Field of study is required")
            if not data.get("degree"):
                errors.append("Degree is required")
            if not data.get("institution"):
                errors.append("Institution is required")
        
        elif step_number == 3:
            # Validate experience
            experience = data.get("experience", [])
            if not experience:
                errors.append("At least one experience entry is required")
            for exp in experience:
                if not exp.get("job_title"):
                    errors.append("Job title is required for all experience entries")
                if not exp.get("company"):
                    errors.append("Company name is required for all experience entries")
        
        elif step_number == 4:
            # Validate skills
            selected_skills = data.get("selected_skills", [])
            if not selected_skills or len(selected_skills) < 3:
                errors.append("Please select at least 3 skills")
        
        elif step_number == 5:
            # Validate summary
            summary = data.get("summary", "")
            if not summary or len(summary.strip()) < 50:
                errors.append("Summary must be at least 50 characters")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors
        }
    
    def generate_final_cv(self, all_steps_data: Dict[str, Any], user_id: int, db) -> Dict[str, Any]:
        """
        Generate final CV from all wizard steps.
        
        Args:
            all_steps_data: Data from all steps
            user_id: User ID
            db: Database session
            
        Returns:
            Generated CV data
        """
        # Extract data from steps
        step1 = all_steps_data.get("step1", {})
        step2 = all_steps_data.get("step2", {})
        step3 = all_steps_data.get("step3", {})
        step4 = all_steps_data.get("step4", {})
        step5 = all_steps_data.get("step5", {})
        
        # Build CV structure
        personal_info = {
            "full_name": step1.get("full_name", ""),
            "email": step1.get("email", ""),
            "phone": step1.get("phone", ""),
            "location": step1.get("location", ""),
            "linkedin": step1.get("linkedin", ""),
            "portfolio": step1.get("portfolio", "")
        }
        
        # Education is stored as a single object in step2, convert to list format
        education = []
        if step2 and step2.get("degree"):
            education.append({
                "degree": step2.get("degree", ""),
                "field_of_study": step2.get("field_of_study", ""),
                "institution": step2.get("institution", ""),
                "start_date": step2.get("start_date", ""),
                "end_date": step2.get("end_date", ""),
                "gpa": step2.get("gpa", ""),
                "honors": step2.get("honors", "")
            })
        experience = step3.get("experience", [])
        skills = step4.get("skills", {})
        summary = step5.get("summary", "")
        
        # Format experience bullets
        formatted_experience = []
        for exp in experience:
            bullets = exp.get("enhanced_bullets", [])
            formatted_experience.append({
                "job_title": exp.get("job_title", ""),
                "company": exp.get("company", ""),
                "start_date": exp.get("start_date", ""),
                "end_date": exp.get("end_date", ""),
                "description": "\n".join(bullets) if bullets else exp.get("description", "")
            })
        
        # Generate CV using CVGenerator
        result = self.cv_generator.generate_cv(
            user_id=user_id,
            personal_info=personal_info,
            experience=formatted_experience,
            education=education,
            skills=skills,
            db=db
        )
        
        # Add summary if not already in result
        if summary and "json_content" in result:
            if "summary" not in result["json_content"]:
                result["json_content"]["summary"] = summary
        
        return result
