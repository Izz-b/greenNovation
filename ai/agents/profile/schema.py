from pydantic import BaseModel, Field
from typing import List


class ProfileInference(BaseModel):
    preferred_explanation_style: str = Field(...)
    preferred_format: str = Field(...)
    preferred_examples_domain: str = Field(...)
    pace: str = Field(...)
    adaptation_tags: List[str] = Field(default_factory=list)
    confidence: float = Field(...)
    reasoning_summary: str = Field(...)
    evidence: List[str] = Field(default_factory=list)