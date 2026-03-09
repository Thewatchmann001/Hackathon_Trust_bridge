"""
CV Embedder
Generate embeddings for CV using sentence transformers.
"""
from typing import List, Optional, Dict, Any
import numpy as np
from app.utils.logger import logger


class CVEmbedder:
    """Generate embeddings for CV text."""
    
    def __init__(self):
        self.model = None
        self._load_model()
    
    def _load_model(self):
        """Lazy load the embedding model."""
        try:
            from sentence_transformers import SentenceTransformer
            # Use a lightweight, fast model
            self.model = SentenceTransformer('all-MiniLM-L6-v2')
            logger.info("CV Embedder model loaded successfully")
        except ImportError:
            logger.warning("sentence-transformers not installed - embeddings disabled")
            logger.warning("Install with: pip install sentence-transformers")
            self.model = None
        except Exception as e:
            logger.error(f"Failed to load embedding model: {e}")
            self.model = None
    
    def embed_cv(self, structured_cv: Dict[str, Any]) -> Optional[List[float]]:
        """
        Generate embedding for structured CV.
        
        Args:
            structured_cv: Parsed CV data
            
        Returns:
            Embedding vector or None if model not available
        """
        if not self.model:
            return None
        
        try:
            # Combine CV text for embedding
            text_parts = []
            
            # Summary
            if structured_cv.get("summary"):
                text_parts.append(structured_cv["summary"])
            
            # Skills
            skills = structured_cv.get("skills", [])
            if skills:
                text_parts.append("Skills: " + ", ".join(skills[:20]))
            
            # Job titles
            titles = structured_cv.get("job_titles", [])
            if titles:
                text_parts.append("Experience: " + ", ".join(titles[:5]))
            
            # Education
            education = structured_cv.get("education", [])
            if education:
                edu_text = ", ".join([
                    f"{e.get('degree', '')} in {e.get('field_of_study', '')}"
                    for e in education[:2]
                ])
                if edu_text:
                    text_parts.append("Education: " + edu_text)
            
            # Combine all text
            cv_text = " ".join(text_parts)
            
            if not cv_text.strip():
                return None
            
            # Generate embedding
            embedding = self.model.encode(cv_text, convert_to_numpy=True)
            
            # Convert to list for JSON serialization
            return embedding.tolist()
            
        except Exception as e:
            logger.error(f"Error generating CV embedding: {e}", exc_info=True)
            return None
    
    def embed_job_description(self, description: str, skills: List[str]) -> Optional[List[float]]:
        """
        Generate embedding for job description.
        
        Args:
            description: Job description text
            skills: Job skills list
            
        Returns:
            Embedding vector or None
        """
        if not self.model:
            return None
        
        try:
            # Combine job text
            job_text = description
            if skills:
                job_text += " Skills: " + ", ".join(skills[:20])
            
            embedding = self.model.encode(job_text, convert_to_numpy=True)
            return embedding.tolist()
            
        except Exception as e:
            logger.error(f"Error generating job embedding: {e}", exc_info=True)
            return None
    
    def cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Calculate cosine similarity between two vectors."""
        try:
            v1 = np.array(vec1)
            v2 = np.array(vec2)
            
            dot_product = np.dot(v1, v2)
            norm1 = np.linalg.norm(v1)
            norm2 = np.linalg.norm(v2)
            
            if norm1 == 0 or norm2 == 0:
                return 0.0
            
            similarity = dot_product / (norm1 * norm2)
            return float(similarity)
            
        except Exception as e:
            logger.error(f"Error calculating cosine similarity: {e}")
            return 0.0
