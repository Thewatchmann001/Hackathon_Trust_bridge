"""
Modular Job Provider System
Each provider implements a unified interface for fetching and normalizing jobs.
"""
from .base_provider import BaseJobProvider, JobSchema
from .provider_manager import ProviderManager

__all__ = ["BaseJobProvider", "JobSchema", "ProviderManager"]
