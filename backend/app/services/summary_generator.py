"""
Professional Summary Generator
Generates tailored professional summaries based on CV data.
"""
from typing import Dict, Any, List, Optional
from app.utils.logger import logger
from app.services.ai_service import AIService
from app.services.industry_detector import IndustryDetector
from cv.timeout_utils import safe_execute_with_timeout


class SummaryGenerator:
    """Generate professional summaries with AI."""
    
    def __init__(self):
        self.ai_service = AIService()
        self.industry_detector = IndustryDetector()
    
    def generate_summary(
        self,
        basic_info: Dict[str, Any],
        education: List[Dict[str, Any]],
        experience: List[Dict[str, Any]],
        skills: Dict[str, Any],
        industry: Optional[str] = None
    ) -> str:
        """
        Generate a professional summary.
        
        Args:
            basic_info: Basic personal information
            education: Education entries
            experience: Work experience entries
            skills: Skills dictionary
            industry: Industry (optional)
            
        Returns:
            Generated professional summary
        """
        # Detect industry if not provided
        if not industry and education:
            field = education[0].get("field_of_study", "") if education else ""
            industry = self.industry_detector.detect_industry(field)
        
        # Use AI if available
        if self.ai_service.mistral_key:
            try:
                return self._generate_with_ai(basic_info, education, experience, skills, industry)
            except Exception as e:
                logger.error(f"Error generating summary with AI: {e}")
                return self._generate_fallback(basic_info, experience, industry)
        
        # Fallback
        return self._generate_fallback(basic_info, experience, industry)
    
    def _generate_with_ai(
        self,
        basic_info: Dict[str, Any],
        education: List[Dict[str, Any]],
        experience: List[Dict[str, Any]],
        skills: Dict[str, Any],
        industry: Optional[str]
    ) -> str:
        """Generate summary using AI."""
        from mistralai import Mistral
        
        client = Mistral(api_key=self.ai_service.mistral_key)
        
        # Extract key information
        name = basic_info.get("full_name", "Professional")
        years_exp = self._calculate_years_experience(experience)
        
        # Get top skills
        technical_skills = skills.get("technical", [])[:5]
        soft_skills = skills.get("soft", [])[:3]
        
        # Get latest education
        latest_edu = education[0] if education else {}
        degree = latest_edu.get("degree", "")
        field = latest_edu.get("field_of_study", "")
        
        # Get latest experience
        latest_exp = experience[0] if experience else {}
        current_role = latest_exp.get("job_title", "")
        current_company = latest_exp.get("company", "")
        
        industry_context = f"Industry: {industry}" if industry else ""
        
        prompt = f"""Generate a professional, achievement-oriented CV summary (3-4 sentences) for this candidate.

Name: {name}
Education: {degree} in {field}
Current Role: {current_role} at {current_company}
Years of Experience: {years_exp}
{industry_context}
Technical Skills: {', '.join(technical_skills) if technical_skills else 'Various'}
Soft Skills: {', '.join(soft_skills) if soft_skills else 'Various'}

Requirements:
1. Start with years of experience and current role/field
2. Highlight key skills and expertise
3. Mention 1-2 key achievements or strengths
4. Be concise (3-4 sentences, 100-150 words)
5. Use professional, confident tone
6. ATS-optimized with industry keywords
7. Achievement-oriented (mention impact if possible)
8. NO markdown formatting - plain text only

Return ONLY the summary text, no markdown, no code blocks, no quotes."""
        
        def _make_ai_call():
            return client.chat.complete(
                model="mistral-small-latest",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a professional CV writer. Generate concise, achievement-oriented professional summaries. Return ONLY plain text, no markdown, no code blocks, no quotes."
                    },
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=200
            )
        
        response = safe_execute_with_timeout(
            _make_ai_call,
            timeout_seconds=10,
            fallback=None
        )
        
        if response is None:
            logger.warning("AI call timed out, using fallback")
            return self._generate_fallback(basic_info, experience, industry)
        
        summary = response.choices[0].message.content.strip()
        
        # Remove markdown if present
        import re
        summary = re.sub(r'\*\*(.*?)\*\*', r'\1', summary)
        summary = re.sub(r'\*(.*?)\*', r'\1', summary)
        summary = re.sub(r'`(.*?)`', r'\1', summary)
        summary = re.sub(r'#{1,6}\s+', '', summary)
        summary = summary.strip()
        
        return summary
    
    def _generate_fallback(
        self,
        basic_info: Dict[str, Any],
        experience: List[Dict[str, Any]],
        industry: Optional[str]
    ) -> str:
        """Fallback summary generation."""
        name = basic_info.get("full_name", "Professional")
        years_exp = self._calculate_years_experience(experience)
        
        latest_exp = experience[0] if experience else {}
        current_role = latest_exp.get("job_title", "Professional")
        
        industry_text = f" in the {industry} industry" if industry else ""
        
        return f"Experienced {current_role} with {years_exp} years of professional experience{industry_text}. Skilled in delivering high-quality results and collaborating with cross-functional teams. Proven track record of success and commitment to excellence."
    
    def generate_summary_variations(
        self,
        basic_info: Dict[str, Any],
        education: List[Dict[str, Any]],
        experience: List[Dict[str, Any]],
        skills: Dict[str, Any],
        industry: Optional[str] = None,
        count: int = 3
    ) -> List[str]:
        """
        Generate multiple summary variations.
        
        Args:
            basic_info: Basic personal information
            education: Education entries
            experience: Work experience entries
            skills: Skills dictionary
            industry: Industry (optional)
            count: Number of variations (default 3)
            
        Returns:
            List of summary variations
        """
        variations = []
        
        # Generate first summary
        summary1 = self.generate_summary(basic_info, education, experience, skills, industry)
        variations.append(summary1)
        
        # Generate additional variations with different tones
        if self.ai_service.mistral_key and count > 1:
            try:
                for i in range(1, count):
                    tone = ["professional", "achievement-focused", "skills-focused"][i % 3]
                    variation = self._generate_with_tone(
                        basic_info, education, experience, skills, industry, tone
                    )
                    if variation and variation not in variations:
                        variations.append(variation)
            except Exception as e:
                logger.error(f"Error generating variations: {e}")
        
        # Fill with fallback if needed
        while len(variations) < count:
            variations.append(self._generate_fallback(basic_info, experience, industry))
        
        return variations[:count]
    
    def _generate_with_tone(
        self,
        basic_info: Dict[str, Any],
        education: List[Dict[str, Any]],
        experience: List[Dict[str, Any]],
        skills: Dict[str, Any],
        industry: Optional[str],
        tone: str
    ) -> str:
        """Generate summary with specific tone."""
        from mistralai import Mistral
        
        client = Mistral(api_key=self.ai_service.mistral_key)
        
        # Extract key information (same as _generate_with_ai)
        name = basic_info.get("full_name", "Professional")
        years_exp = self._calculate_years_experience(experience)
        
        technical_skills = skills.get("technical", [])[:5]
        soft_skills = skills.get("soft", [])[:3]
        
        latest_edu = education[0] if education else {}
        degree = latest_edu.get("degree", "")
        field = latest_edu.get("field_of_study", "")
        
        latest_exp = experience[0] if experience else {}
        current_role = latest_exp.get("job_title", "")
        current_company = latest_exp.get("company", "")
        
        industry_context = f"Industry: {industry}" if industry else ""
        
        tone_instructions = {
            "professional": "Use a formal, professional tone emphasizing experience and qualifications",
            "achievement-focused": "Emphasize quantifiable achievements and impact",
            "skills-focused": "Highlight technical and soft skills prominently"
        }
        
        prompt = f"""Generate a professional CV summary (3-4 sentences) with a {tone} tone.

Name: {name}
Education: {degree} in {field}
Current Role: {current_role} at {current_company}
Years of Experience: {years_exp}
{industry_context}
Technical Skills: {', '.join(technical_skills) if technical_skills else 'Various'}
Soft Skills: {', '.join(soft_skills) if soft_skills else 'Various'}

Tone: {tone_instructions.get(tone, 'Professional')}

Return ONLY plain text, no markdown."""
        
        def _make_ai_call():
            return client.chat.complete(
                model="mistral-small-latest",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a professional CV writer. Generate summaries with different tones. Return ONLY plain text."
                    },
                    {"role": "user", "content": prompt}
                ],
                temperature=0.8,  # Higher temperature for variation
                max_tokens=200
            )
        
        response = safe_execute_with_timeout(
            _make_ai_call,
            timeout_seconds=10,
            fallback=None
        )
        
        if response is None:
            return self._generate_fallback(basic_info, experience, industry)
        
        summary = response.choices[0].message.content.strip()
        
        import re
        summary = re.sub(r'\*\*(.*?)\*\*', r'\1', summary)
        summary = re.sub(r'\*(.*?)\*', r'\1', summary)
        summary = summary.strip()
        
        return summary
    
    def _calculate_years_experience(self, experience: List[Dict[str, Any]]) -> int:
        """Calculate total years of experience."""
        if not experience:
            return 0
        
        total_months = 0
        
        for exp in experience:
            start_date = exp.get("start_date", "")
            end_date = exp.get("end_date", "")
            
            if start_date:
                try:
                    from datetime import datetime
                    start = datetime.strptime(start_date[:7], "%Y-%m")  # YYYY-MM
                    end = datetime.now() if not end_date or end_date.lower() == "present" else datetime.strptime(end_date[:7], "%Y-%m")
                    months = (end.year - start.year) * 12 + (end.month - start.month)
                    total_months += max(0, months)
                except:
                    pass
        
        return total_months // 12
