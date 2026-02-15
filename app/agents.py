from __future__ import annotations

from dataclasses import dataclass

from app.models import (
    AuditRequest,
    GuardianResult,
    InvestigationResult,
    ReasoningResult,
)
from app.nsq_registry import NSQRegistry
from app.search import SearchClient


@dataclass
class InvestigatorAgent:
    search_client: SearchClient
    nsq_registry: NSQRegistry

    def run(self, request: AuditRequest) -> InvestigationResult:
        links = self.search_client.waterfall_search(
            product_name=request.product_name,
            batch_number=request.batch_number,
            manufacturer=request.manufacturer,
        )
        query = f"{request.product_name} + {request.batch_number} + Recall"
        nsq_match = self.nsq_registry.find_exact_match(
            batch_number=request.batch_number,
            manufacturer=request.manufacturer,
        )
        return InvestigationResult(
            search_query=query,
            results=links,
            jurisdiction_chain=["CDSCO", "FDA", "Health Canada"],
            nsq_match=nsq_match,
        )


class ReasonerAgent:
    """LLM-facing logic (deterministic heuristic baseline for local development)."""

    RISK_TERMS = {
        "recall": 40,
        "nsq": 35,
        "failed": 30,
        "counterfeit": 55,
    }

    def run(self, request: AuditRequest, investigation: InvestigationResult) -> ReasoningResult:
        corpus = " ".join([investigation.search_query] + [item.title.lower() for item in investigation.results])
        risk = 10
        for term, weight in self.RISK_TERMS.items():
            if term in corpus:
                risk += weight

        if investigation.nsq_match:
            risk = max(risk, 90)

        manufacturer_bias = 0.65 if len(request.manufacturer) > 6 else 0.8
        risk = min(100, max(0, int(risk * (1.0 - (manufacturer_bias - 0.5)))))
        probability = max(0.01, min(0.99, 1 - (risk / 100)))

        rationale = (
            "Risk score is derived from regulatory risk terms, known NSQ exact-batch matches, "
            "and manufacturer compliance prior; replace this method with Gemini/Groq prompt chain "
            "for production-grade report interpretation."
        )
        if investigation.nsq_match:
            rationale += f" Exact match found in CDSCO NSQ data: {investigation.nsq_match['issue']}."

        return ReasoningResult(
            risk_score=risk,
            rationale=rationale,
            compliance_probability=probability,
        )


class GuardianAgent:
    RISKY_EXCIPIENTS = {
        "diabetes": ["sucrose", "fructose", "sorbitol"],
        "liver": ["acetaminophen"],
    }

    def run(self, request: AuditRequest) -> GuardianResult:
        flags = []
        delta = 0

        simulated_ingredients = [request.product_name.lower(), "sucrose"]

        if request.guardian_profile.diabetes and any(
            x in simulated_ingredients for x in self.RISKY_EXCIPIENTS["diabetes"]
        ):
            flags.append("Contains sugar-based excipients that may destabilize blood glucose.")
            delta += 25

        if request.guardian_profile.liver_issues and any(
            x in simulated_ingredients for x in self.RISKY_EXCIPIENTS["liver"]
        ):
            flags.append("Contains ingredients requiring liver-function caution.")
            delta += 20

        allergy_hits = [a for a in request.guardian_profile.allergies if a.lower() in simulated_ingredients]
        for allergen in allergy_hits:
            flags.append(f"Potential allergen match: {allergen}")
            delta += 35

        return GuardianResult(personalized_flags=flags, personalized_risk_delta=delta)
