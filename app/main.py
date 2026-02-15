from __future__ import annotations

from fastapi import FastAPI

from app.agents import GuardianAgent, InvestigatorAgent, ReasonerAgent
from app.cache import CacheStore
from app.models import AuditRequest, AuditResponse, Verdict
from app.nsq_registry import NSQRegistry
from app.search import SearchClient

app = FastAPI(title="RxTrust Agentic API", version="0.2.0")

search_client = SearchClient()
cache_store = CacheStore()
nsq_registry = NSQRegistry()
investigator = InvestigatorAgent(search_client=search_client, nsq_registry=nsq_registry)
reasoner = ReasonerAgent()
guardian = GuardianAgent()


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/audit", response_model=AuditResponse)
def audit_drug(request: AuditRequest) -> AuditResponse:
    cached = cache_store.get(request)
    if cached:
        return cached

    investigation = investigator.run(request)
    reasoning = reasoner.run(request, investigation)
    guardian_result = guardian.run(request)

    total_risk = min(100, reasoning.risk_score + guardian_result.personalized_risk_delta)
    if total_risk >= 70:
        verdict = Verdict.ALERT
    elif total_risk >= 35:
        verdict = Verdict.CAUTION
    else:
        verdict = Verdict.SAFE

    match_text = " Exact NSQ batch match found." if investigation.nsq_match else " No exact NSQ batch match found."
    response = AuditResponse(
        request=request,
        verdict=verdict,
        risk_score=total_risk,
        confidence=reasoning.compliance_probability,
        summary=(
            f"Waterfall audit across {', '.join(investigation.jurisdiction_chain)} "
            f"returned {len(investigation.results)} evidence links.{match_text}"
        ),
        reasoning=reasoning,
        guardian=guardian_result,
        evidence=investigation.results,
    )
    cache_store.set(request, response)
    return response
