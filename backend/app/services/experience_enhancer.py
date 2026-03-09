"""
Experience Enhancement Service
Converts basic experience descriptions into achievement-oriented bullet points.
"""
from typing import Dict, Any, List, Optional
from app.utils.logger import logger
from app.services.ai_service import AIService
from app.services.industry_detector import IndustryDetector
from cv.timeout_utils import safe_execute_with_timeout


class ExperienceEnhancer:
    """Enhance experience descriptions with AI."""
    
    def __init__(self):
        self.ai_service = AIService()
        self.industry_detector = IndustryDetector()
    
    def enhance_experience_description(
        self,
        job_title: str,
        company: str,
        description: str,
        industry: Optional[str] = None
    ) -> List[str]:
        """
        Convert basic description into achievement-oriented bullet points.
        
        Args:
            job_title: Job title
            company: Company name
            description: Basic description text
            industry: Industry (optional, for context)
            
        Returns:
            List of enhanced bullet points
        """
        if not description or not description.strip():
            # Generate suggestions based on job title if no description
            return self.suggest_achievements(job_title, industry)
        
        # Use AI to enhance if available
        if self.ai_service.mistral_key:
            try:
                return self._enhance_with_ai(job_title, company, description, industry)
            except Exception as e:
                logger.error(f"Error enhancing experience with AI: {e}")
                return self._enhance_fallback(description)
        
        # Fallback to rule-based enhancement
        return self._enhance_fallback(description)
    
    def _enhance_with_ai(
        self,
        job_title: str,
        company: str,
        description: str,
        industry: Optional[str]
    ) -> List[str]:
        """Enhance using AI."""
        from mistralai import Mistral
        
        client = Mistral(api_key=self.ai_service.mistral_key)
        
        industry_context = f"Industry: {industry}" if industry else ""
        
        prompt = f"""Convert this basic job description into 3-4 professional, achievement-oriented bullet points.

Job Title: {job_title}
Company: {company}
{industry_context}

Original Description:
{description}

Requirements:
1. Each bullet point must start with a strong action verb (Led, Developed, Implemented, Achieved, etc.)
2. Include quantifiable metrics where possible (percentages, numbers, timeframes, team sizes)
3. Focus on achievements and impact, not just tasks
4. Be specific and concrete
5. Each bullet should be 1-2 sentences
6. Use professional language suitable for a CV
7. DO NOT invent metrics or achievements that weren't mentioned
8. If no metrics are available, focus on scope, complexity, or impact

Return ONLY a JSON array of strings, no markdown, no code blocks:
["Bullet point 1", "Bullet point 2", "Bullet point 3"]"""
        
        def _make_ai_call():
            return client.chat.complete(
                model="mistral-small-latest",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a professional CV writer. Convert job descriptions into achievement-oriented bullet points. Return ONLY a JSON array of strings, no markdown, no explanations."
                    },
                    {"role": "user", "content": prompt}
                ],
                temperature=0.5,
                max_tokens=800
            )
        
        response = safe_execute_with_timeout(
            _make_ai_call,
            timeout_seconds=10,
            fallback=None
        )
        
        if response is None:
            logger.warning("AI call timed out, using fallback")
            return self._enhance_fallback(description)
        
        content = response.choices[0].message.content.strip()
        
        # Extract JSON array
        import json
        import re
        
        # Remove markdown code blocks
        content = re.sub(r'```json\s*', '', content)
        content = re.sub(r'```\s*', '', content)
        content = content.strip()
        
        # Find JSON array
        json_match = re.search(r'\[.*\]', content, re.DOTALL)
        if json_match:
            try:
                bullets = json.loads(json_match.group())
                if isinstance(bullets, list) and len(bullets) > 0:
                    return bullets[:4]  # Return max 4 bullets
            except json.JSONDecodeError:
                logger.warning("Failed to parse AI response as JSON")
        
        # Fallback if parsing fails
        return self._enhance_fallback(description)
    
    def _enhance_fallback(self, description: str) -> List[str]:
        """Fallback rule-based enhancement."""
        # Simple sentence splitting and formatting
        sentences = description.split('.')
        bullets = []
        
        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence) > 20:  # Only include substantial sentences
                # Capitalize first letter
                if sentence:
                    sentence = sentence[0].upper() + sentence[1:] if len(sentence) > 1 else sentence.upper()
                    bullets.append(sentence)
        
        return bullets[:4] if bullets else [description]
    
    def suggest_achievements(
        self,
        job_title: str,
        industry: Optional[str] = None
    ) -> List[str]:
        """
        Suggest achievement-oriented bullet points based on job title.
        
        Args:
            job_title: Job title
            industry: Industry (optional)
            
        Returns:
            List of suggested bullet points
        """
        # Use AI if available
        if self.ai_service.mistral_key:
            try:
                return self._suggest_with_ai(job_title, industry)
            except Exception as e:
                logger.error(f"Error suggesting achievements with AI: {e}")
        
        # Fallback suggestions
        return self._suggest_fallback(job_title)
    
    def _suggest_with_ai(
        self,
        job_title: str,
        industry: Optional[str]
    ) -> List[str]:
        """Suggest achievements using AI."""
        from mistralai import Mistral
        
        client = Mistral(api_key=self.ai_service.mistral_key)
        
        industry_context = f"Industry: {industry}" if industry else ""
        
        prompt = f"""Generate 3-4 professional, achievement-oriented bullet points for this job title.

Job Title: {job_title}
{industry_context}

Requirements:
1. Each bullet should start with a strong action verb
2. Include placeholders for metrics (e.g., "increased X by Y%", "managed team of X", "delivered X projects")
3. Focus on typical achievements for this role
4. Be realistic and professional
5. Each bullet should be 1-2 sentences

Return ONLY a JSON array of strings:
["Bullet point 1", "Bullet point 2", "Bullet point 3"]"""
        
        def _make_ai_call():
            return client.chat.complete(
                model="mistral-small-latest",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a professional CV writer. Generate achievement-oriented bullet points. Return ONLY a JSON array of strings."
                    },
                    {"role": "user", "content": prompt}
                ],
                temperature=0.6,
                max_tokens=600
            )
        
        response = safe_execute_with_timeout(
            _make_ai_call,
            timeout_seconds=10,
            fallback=None
        )
        
        if response is None:
            return self._suggest_fallback(job_title)
        
        content = response.choices[0].message.content.strip()
        
        import json
        import re
        
        content = re.sub(r'```json\s*', '', content)
        content = re.sub(r'```\s*', '', content)
        content = content.strip()
        
        json_match = re.search(r'\[.*\]', content, re.DOTALL)
        if json_match:
            try:
                bullets = json.loads(json_match.group())
                if isinstance(bullets, list) and len(bullets) > 0:
                    return bullets[:4]
            except json.JSONDecodeError:
                pass
        
        return self._suggest_fallback(job_title)
    
    def _suggest_fallback(self, job_title: str) -> List[str]:
        """Fallback suggestions based on job title."""
        title_lower = job_title.lower()
        
        if any(word in title_lower for word in ["developer", "engineer", "programmer"]):
            return [
                "Developed and maintained software applications using modern technologies",
                "Collaborated with cross-functional teams to deliver high-quality solutions",
                "Implemented best practices and coding standards to improve code quality"
            ]
        elif any(word in title_lower for word in ["manager", "lead", "director"]):
            return [
                "Led and managed team members to achieve project objectives",
                "Developed and implemented strategies to improve team performance",
                "Collaborated with stakeholders to deliver successful outcomes"
            ]
        elif any(word in title_lower for word in ["analyst", "data"]):
            return [
                "Analyzed data to identify trends and provide actionable insights",
                "Created reports and dashboards to support decision-making",
                "Collaborated with teams to implement data-driven solutions"
            ]
        else:
            return [
                "Contributed to key projects and initiatives",
                "Collaborated with team members to achieve objectives",
                "Demonstrated strong problem-solving and communication skills"
            ]
    
    def validate_experience_dates(
        self,
        start_date: str,
        end_date: Optional[str]
    ) -> Dict[str, Any]:
        """
        Validate and suggest corrections for experience dates.
        
        Args:
            start_date: Start date
            end_date: End date (None if current)
            
        Returns:
            Dictionary with validation results and suggestions
        """
        errors = []
        suggestions = []
        
        # Basic validation
        if not start_date:
            errors.append("Start date is required")
        
        if end_date and end_date < start_date:
            errors.append("End date cannot be before start date")
            suggestions.append("Please check your dates")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "suggestions": suggestions
        }
