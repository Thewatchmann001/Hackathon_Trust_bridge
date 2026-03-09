"""
Embedding Matcher
Calculate semantic similarity using embeddings.
"""
from typing import List, Optional
from app.utils.logger import logger
from cv.analysis.cv_embedder import CVEmbedder


class EmbeddingMatcher:
    """Match jobs based on embedding similarity."""
    
    def __init__(self):
        self.embedder = CVEmbedder()
    
    def calculate_score(
        self,
        cv_embedding: Optional[List[float]],
        job_embedding: Optional[List[float]]
    ) -> float:
        """
        Calculate embedding similarity score (0.0 to 1.0).
        
        Args:
            cv_embedding: CV embedding vector
            job_embedding: Job embedding vector
            
        Returns:
            Score between 0.0 and 1.0 (cosine similarity normalized to 0-1)
        """
        if not cv_embedding or not job_embedding:
            return 0.0
        
        try:
            # Calculate cosine similarity
            similarity = self.embedder.cosine_similarity(cv_embedding, job_embedding)
            
            # Normalize from [-1, 1] to [0, 1]
            normalized = (similarity + 1) / 2
            
            return normalized
            
        except Exception as e:
            logger.error(f"Error calculating embedding similarity: {e}")
            return 0.0
