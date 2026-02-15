from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, HttpUrl


class Verdict(str, Enum):
    SAFE = "safe"
    CAUTION = "caution"
    ALERT = "alert"


class GuardianProfile(BaseModel):
    diabetes: bool = False
    liver_issues: bool = False
    kidney_issues: bool = False
    allergies: List[str] = Field(default_factory=list)


class AuditRequest(BaseModel):
    product_name: str = Field(min_length=2)
    batch_number: str = Field(min_length=2)
    manufacturer: str = Field(min_length=2)
    guardian_profile: GuardianProfile = Field(default_factory=GuardianProfile)


class EvidenceLink(BaseModel):
    source: str
    title: str
    url: HttpUrl
    highlighted_fragment: Optional[str] = None
    retrieved_at: datetime = Field(default_factory=datetime.utcnow)


class InvestigationResult(BaseModel):
    search_query: str
    results: List[EvidenceLink]
    jurisdiction_chain: List[str]
    nsq_match: Optional[Dict[str, Any]] = None


class ReasoningResult(BaseModel):
    risk_score: int = Field(ge=0, le=100)
    rationale: str
    compliance_probability: float = Field(ge=0.0, le=1.0)


class GuardianResult(BaseModel):
    personalized_flags: List[str] = Field(default_factory=list)
    personalized_risk_delta: int = 0


class AuditResponse(BaseModel):
    request: AuditRequest
    verdict: Verdict
    risk_score: int = Field(ge=0, le=100)
    confidence: float = Field(ge=0.0, le=1.0)
    summary: str
    reasoning: ReasoningResult
    guardian: GuardianResult
    evidence: List[EvidenceLink]
    cached: bool = False
    generated_at: datetime = Field(default_factory=datetime.utcnow)
