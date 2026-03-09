"""
Hybrid Matcher
Main matching orchestrator combining all matching strategies.
"""
from typing import List, Dict, Any, Optional
from datetime import datetime
from cv.providers.base_provider import JobSchema
from cv.analysis.cv_cache import CVCache
from cv.analysis.cv_embedder import CVEmbedder
from .keyword_matcher import KeywordMatcher
from .skill_matcher import SkillMatcher
from .embedding_matcher import EmbeddingMatcher
from .experience_filter import ExperienceFilter
from .fallback_matcher import FallbackMatcher
from .learning_resources import LearningResourcesService
from app.utils.logger import logger


class HybridMatcher:
    """Hybrid matching engine combining multiple strategies."""
    
    def __init__(self):
        self.cv_cache = CVCache()
        self.embedder = CVEmbedder()
        self.keyword_matcher = KeywordMatcher()
        self.skill_matcher = SkillMatcher()
        self.embedding_matcher = EmbeddingMatcher()
        self.experience_filter = ExperienceFilter()
        self.fallback_matcher = FallbackMatcher()
        self.learning_resources = LearningResourcesService()
    
    def match_jobs(
        self,
        cv_id: int,
        jobs: List[JobSchema],
        db,
        min_score: float = 0.1,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """
        Match jobs to CV using hybrid scoring.
        
        Args:
            cv_id: CV ID
            jobs: List of jobs to match
            db: Database session
            min_score: Minimum score threshold
            limit: Maximum number of results
            
        Returns:
            List of matched jobs with scores and explanations
        """
        start_time = datetime.now()
        
        # Get parsed CV from cache
        parsed_cv = self.cv_cache.get_parsed_cv(cv_id, db)
        if not parsed_cv:
            logger.warning(f"CV {cv_id} not found or could not be parsed")
            return []
        
        # Extract CV data
        cv_skills = parsed_cv.get("skills", [])
        cv_keywords = parsed_cv.get("keywords", [])
        cv_embedding = parsed_cv.get("embedding")
        cv_years_exp = parsed_cv.get("years_experience", 0)
        cv_industry = parsed_cv.get("industry")
        cv_job_titles = parsed_cv.get("job_titles", [])
        
        logger.info(
            f"Matching CV {cv_id} to {len(jobs)} jobs - "
            f"Skills: {len(cv_skills)}, Keywords: {len(cv_keywords)}"
        )
        
        # Score all jobs
        scored_jobs = []
        
        for job in jobs:
            # Generate job embedding if not present
            if not job.embedding:
                job.embedding = self.embedder.embed_job_description(
                    job.description, job.skills
                )
            
            # Calculate component scores
            embedding_score = self.embedding_matcher.calculate_score(
                cv_embedding, job.embedding
            )
            
            skill_score = self.skill_matcher.calculate_score(
                cv_skills, job.skills
            )
            
            # Title similarity (using keyword matcher on title)
            title_score = self.keyword_matcher.calculate_score(
                cv_job_titles + cv_keywords[:5],
                job.title,
                "",
                []
            )
            
            experience_score = self.experience_filter.calculate_score(
                cv_years_exp,
                job.metadata
            )
            
            # Calculate final hybrid score
            final_score = (
                0.4 * embedding_score +
                0.3 * skill_score +
                0.2 * title_score +
                0.1 * experience_score
            )
            
            # Calculate missing skills
            missing_skills = self._calculate_missing_skills(cv_skills, job.skills)
            
            # Generate detailed feedback about what's missing
            detailed_feedback = self._generate_detailed_feedback(
                embedding_score,
                skill_score,
                title_score,
                experience_score,
                cv_skills,
                job.skills,
                cv_years_exp,
                job.metadata,
                missing_skills
            )
            
            # Get learning resources for missing skills
            learning_resources = []
            for skill in missing_skills[:3]:  # Top 3 missing skills
                resources = self.learning_resources.get_resources_for_skill(skill, limit=2)
                learning_resources.extend(resources)
            
            # Only include jobs above threshold
            if final_score >= min_score:
                scored_jobs.append({
                    "job": job,
                    "score": final_score,
                    "components": {
                        "embedding": embedding_score,
                        "skill": skill_score,
                        "title": title_score,
                        "experience": experience_score,
                    },
                    "match_reasons": self._generate_match_reasons(
                        skill_score, embedding_score, title_score, cv_skills, job.skills
                    ),
                    "missing_skills": missing_skills,
                    "detailed_feedback": detailed_feedback,
                    "learning_resources": learning_resources[:6],  # Limit to 6 resources total
                    "is_fallback": False
                })
        
        # Sort by score descending
        scored_jobs.sort(key=lambda x: x["score"], reverse=True)
        
        # Apply limit
        top_jobs = scored_jobs[:limit]
        
        # If no matches found, use fallback
        if not top_jobs:
            logger.warning(f"No matches found for CV {cv_id}, using fallback")
            fallback_jobs = self.fallback_matcher.get_fallback_jobs(
                jobs, cv_industry, cv_keywords, limit
            )
            
            # Convert fallback jobs to match format with lower scores
            top_jobs = []
            for job in fallback_jobs:
                missing_skills = self._calculate_missing_skills(cv_skills, job.skills)
                
                # Generate feedback for fallback jobs
                detailed_feedback = self._generate_detailed_feedback(
                    0.0, 0.0, 0.0, 0.5, cv_skills, job.skills, cv_years_exp, job.metadata, missing_skills
                )
                
                # Get learning resources
                learning_resources = []
                for skill in missing_skills[:3]:
                    resources = self.learning_resources.get_resources_for_skill(skill, limit=2)
                    learning_resources.extend(resources)
                
                top_jobs.append({
                    "job": job,
                    "score": 0.3,  # Lower score for fallback
                    "components": {
                        "embedding": 0.0,
                        "skill": 0.0,
                        "title": 0.0,
                        "experience": 0.5,
                    },
                    "match_reasons": ["Fallback match - showing relevant jobs in your industry"],
                    "missing_skills": missing_skills,
                    "detailed_feedback": detailed_feedback,
                    "learning_resources": learning_resources[:6],
                    "is_fallback": True
                })
        
        duration = (datetime.now() - start_time).total_seconds()
        
        logger.info(
            f"Matched CV {cv_id} - "
            f"Scored: {len(scored_jobs)}, "
            f"Returned: {len(top_jobs)}, "
            f"Top score: {top_jobs[0]['score']:.2f} if top_jobs else 0, "
            f"Duration: {duration:.2f}s"
        )
        
        # Format results
        return self._format_results(top_jobs)
    
    def _calculate_missing_skills(self, cv_skills: List[str], job_skills: List[str]) -> List[str]:
        """Calculate skills required by job but not in CV."""
        if not job_skills:
            return []
        
        if not cv_skills:
            return job_skills[:5]  # Return all job skills if CV has none
        
        # Normalize skills for comparison
        cv_skills_lower = {s.lower().strip() for s in cv_skills}
        missing = []
        
        for job_skill in job_skills:
            job_skill_lower = job_skill.lower().strip()
            # Check if skill is missing (exact or partial match)
            found = False
            for cv_skill_lower in cv_skills_lower:
                # Exact match
                if job_skill_lower == cv_skill_lower:
                    found = True
                    break
                # Partial match (e.g., "python" matches "python programming")
                if job_skill_lower in cv_skill_lower or cv_skill_lower in job_skill_lower:
                    found = True
                    break
            if not found:
                missing.append(job_skill)
        
        return missing[:5]  # Return top 5 missing skills
    
    def _generate_match_reasons(
        self,
        skill_score: float,
        embedding_score: float,
        title_score: float,
        cv_skills: List[str],
        job_skills: List[str]
    ) -> List[str]:
        """Generate human-readable match reasons."""
        reasons = []
        
        # Skill match
        if skill_score > 0.5:
            matched_skills = [s for s in job_skills if s.lower() in [cs.lower() for cs in cv_skills]]
            if matched_skills:
                reasons.append(f"Matched {len(matched_skills)} of {len(job_skills)} required skills")
        
        # Embedding match
        if embedding_score > 0.7:
            reasons.append("Strong semantic similarity")
        elif embedding_score > 0.5:
            reasons.append("Good semantic match")
        
        # Title match
        if title_score > 0.5:
            reasons.append("Job title matches your experience")
        
        if not reasons:
            reasons.append("Relevant opportunity based on your profile")
        
        return reasons
    
    def _generate_detailed_feedback(
        self,
        embedding_score: float,
        skill_score: float,
        title_score: float,
        experience_score: float,
        cv_skills: List[str],
        job_skills: List[str],
        cv_years_exp: int,
        job_metadata: Dict[str, Any],
        missing_skills: List[str]
    ) -> Dict[str, Any]:
        """
        Generate detailed feedback explaining why the score is what it is.
        
        Returns:
            Dictionary with feedback about what's missing or needs improvement
        """
        feedback = {
            "score_breakdown": {},
            "improvement_areas": [],
            "strengths": []
        }
        
        # Analyze embedding score (semantic similarity)
        if embedding_score < 0.3:
            feedback["improvement_areas"].append({
                "area": "Semantic Match",
                "issue": "Your CV content doesn't align well with the job description",
                "impact": "High (40% weight)",
                "suggestion": "Update your CV summary and experience descriptions to better match the job requirements"
            })
        elif embedding_score > 0.7:
            feedback["strengths"].append("Strong alignment with job description")
        
        # Analyze skill score
        if skill_score < 0.3:
            if missing_skills:
                feedback["improvement_areas"].append({
                    "area": "Skills",
                    "issue": f"Missing {len(missing_skills)} required skill(s): {', '.join(missing_skills[:3])}",
                    "impact": "High (30% weight)",
                    "suggestion": f"Learn these skills to significantly improve your match score"
                })
            else:
                feedback["improvement_areas"].append({
                    "area": "Skills",
                    "issue": "Low skill overlap with job requirements",
                    "impact": "High (30% weight)",
                    "suggestion": "Review the job's required skills and add relevant ones to your CV"
                })
        elif skill_score > 0.7:
            matched_count = len([s for s in job_skills if s.lower() in [cs.lower() for cs in cv_skills]])
            feedback["strengths"].append(f"Strong skill match ({matched_count}/{len(job_skills)} skills)")
        
        # Analyze title score
        if title_score < 0.3:
            feedback["improvement_areas"].append({
                "area": "Job Title Match",
                "issue": "Your previous job titles don't match this role",
                "impact": "Medium (20% weight)",
                "suggestion": "Consider roles with titles closer to your experience, or highlight transferable skills"
            })
        elif title_score > 0.5:
            feedback["strengths"].append("Job title aligns with your experience")
        
        # Analyze experience score
        job_min_exp = job_metadata.get("min_experience", 0)
        job_max_exp = job_metadata.get("max_experience", 999)
        
        if experience_score < 0.3:
            if cv_years_exp < job_min_exp:
                feedback["improvement_areas"].append({
                    "area": "Experience Level",
                    "issue": f"Job requires {job_min_exp}+ years, you have {cv_years_exp} years",
                    "impact": "Low (10% weight)",
                    "suggestion": "Consider entry-level or junior positions, or highlight relevant projects/education"
                })
            elif cv_years_exp > job_max_exp:
                feedback["improvement_areas"].append({
                    "area": "Experience Level",
                    "issue": f"You may be overqualified (job targets {job_max_exp} years, you have {cv_years_exp})",
                    "impact": "Low (10% weight)",
                    "suggestion": "Consider if this role aligns with your career goals"
                })
        elif experience_score > 0.7:
            feedback["strengths"].append("Experience level matches job requirements")
        
        # Overall score explanation
        if len(feedback["improvement_areas"]) == 0:
            feedback["summary"] = "Great match! Your profile aligns well with this position."
        elif len(feedback["improvement_areas"]) == 1:
            feedback["summary"] = f"Good potential match. Focus on: {feedback['improvement_areas'][0]['area']}"
        else:
            feedback["summary"] = f"Moderate match. Key areas to improve: {', '.join([a['area'] for a in feedback['improvement_areas'][:2]])}"
        
        return feedback
    
    def _format_results(self, scored_jobs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Format results for API response."""
        results = []
        
        for item in scored_jobs:
            job = item["job"]
            results.append({
                "id": job.id,
                "title": job.title,
                "company": job.company,
                "location": job.location,
                "description": job.description,
                "skills": job.skills,
                "source": job.source,
                "url": job.url,
                "date": job.date.isoformat() if isinstance(job.date, datetime) else str(job.date),
                "match_score": round(item["score"] * 100, 1),  # Convert to percentage
                "match_components": {
                    "embedding": round(item["components"]["embedding"] * 100, 1),
                    "skill": round(item["components"]["skill"] * 100, 1),
                    "title": round(item["components"]["title"] * 100, 1),
                    "experience": round(item["components"]["experience"] * 100, 1),
                },
                "match_reasons": item.get("match_reasons", []),
                "missing_skills": item.get("missing_skills", []),
                "detailed_feedback": item.get("detailed_feedback", {}),
                "learning_resources": item.get("learning_resources", []),
                "is_fallback": item.get("is_fallback", False),
                "metadata": job.metadata or {}
            })
        
        return results
