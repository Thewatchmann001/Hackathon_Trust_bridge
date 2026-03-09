"""
CV Cache
Cache parsed CV data and embeddings in database.
"""
from typing import Dict, Any, Optional, List
from sqlalchemy.orm import Session
from app.db.models import CV
from app.utils.logger import logger
from .cv_parser import CVParser
from .cv_embedder import CVEmbedder


class CVCache:
    """Cache for parsed CVs and embeddings."""
    
    def __init__(self):
        self.parser = CVParser()
        self.embedder = CVEmbedder()
        self._memory_cache = {}  # In-memory cache for session
    
    def get_parsed_cv(self, cv_id: int, db: Session) -> Optional[Dict[str, Any]]:
        """
        Get parsed CV from cache or parse and cache it.
        
        Args:
            cv_id: CV ID
            db: Database session
            
        Returns:
            Parsed CV data or None
        """
        # Check memory cache first
        cache_key = f"cv_{cv_id}"
        if cache_key in self._memory_cache:
            return self._memory_cache[cache_key]
        
        # Check database
        cv = db.query(CV).filter(CV.id == cv_id).first()
        if not cv:
            return None
        
        # Check if already parsed and cached in json_content
        if cv.json_content and cv.json_content.get("_parsed"):
            parsed = cv.json_content["_parsed"].copy()  # Make a copy to avoid modifying cached version
            
            # FIX: Check if embedding is missing and try to restore it
            if not parsed.get("embedding"):
                # Check if embedding is stored separately
                if cv.json_content.get("_embedding"):
                    parsed["embedding"] = cv.json_content["_embedding"]
                    # Update cached version with embedding
                    if "_parsed" in cv.json_content:
                        cv.json_content["_parsed"]["embedding"] = cv.json_content["_embedding"]
                    try:
                        from sqlalchemy.orm.attributes import flag_modified
                        flag_modified(cv, "json_content")
                        db.commit()
                        logger.info(f"CV {cv_id}: Restored embedding from _embedding cache")
                    except Exception as e:
                        logger.warning(f"Could not update cached CV with embedding: {e}")
                else:
                    # Embedding doesn't exist - regenerate it
                    logger.info(f"CV {cv_id} missing embedding, regenerating...")
                    embedding = self.embedder.embed_cv(parsed)
                    if embedding:
                        parsed["embedding"] = embedding
                        # Update cache
                        if "_parsed" in cv.json_content:
                            cv.json_content["_parsed"]["embedding"] = embedding
                        cv.json_content["_embedding"] = embedding
                        try:
                            from sqlalchemy.orm.attributes import flag_modified
                            flag_modified(cv, "json_content")
                            db.commit()
                            logger.info(f"CV {cv_id}: Generated and cached new embedding")
                        except Exception as e:
                            logger.warning(f"Could not cache regenerated embedding: {e}")
                    else:
                        logger.warning(f"CV {cv_id}: Failed to generate embedding")
            
            self._memory_cache[cache_key] = parsed
            return parsed
        
        # Parse CV
        cv_data = {
            "json_content": cv.json_content or {},
            "summary": cv.summary or "",
        }
        
        parsed = self.parser.parse(cv_data)
        
        # Generate embedding
        embedding = self.embedder.embed_cv(parsed)
        if embedding:
            parsed["embedding"] = embedding
        
        # Cache in database
        if not cv.json_content:
            cv.json_content = {}
        
        cv.json_content["_parsed"] = parsed
        cv.json_content["_embedding"] = embedding
        
        try:
            from sqlalchemy.orm.attributes import flag_modified
            flag_modified(cv, "json_content")
            db.commit()
        except Exception as e:
            logger.error(f"Error caching CV: {e}")
            db.rollback()
        
        # Cache in memory
        self._memory_cache[cache_key] = parsed
        
        logger.info(f"CV {cv_id} parsed and cached")
        
        return parsed
    
    def get_cv_embedding(self, cv_id: int, db: Session) -> Optional[List[float]]:
        """Get CV embedding from cache."""
        parsed = self.get_parsed_cv(cv_id, db)
        if parsed:
            return parsed.get("embedding")
        return None
    
    def clear_cache(self, cv_id: Optional[int] = None):
        """Clear cache for a specific CV or all CVs."""
        if cv_id:
            cache_key = f"cv_{cv_id}"
            if cache_key in self._memory_cache:
                del self._memory_cache[cache_key]
        else:
            self._memory_cache.clear()
