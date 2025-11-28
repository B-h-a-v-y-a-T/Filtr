from typing import Any, Dict, List, Optional

from pydantic import BaseModel


class EvidenceItem(BaseModel):
    source: str
    confidence: float


class AnalysisResult(BaseModel):
    summary: str
    verdict: str
    evidence: List[EvidenceItem]
    sentiment: Optional[Dict[str, Any]] = None


