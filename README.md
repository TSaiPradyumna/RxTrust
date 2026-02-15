# RxTrust: Agentic Drug Safety Verification (FastAPI Reference Implementation)

This repository implements a baseline of the strategy you described:

- **Investigator (Perceive):** runs a waterfall search across CDSCO → FDA → Health Canada and builds deep links with text fragments.
- **Reasoner (Reason):** computes a structured risk score and compliance probability (heuristic stand-in for Gemini/Groq).
- **Guardian (Act):** personalizes the verdict using a user health profile (diabetes, liver issues, allergies).

## Architecture

```text
Client
  -> FastAPI /audit endpoint
      -> CacheStore (SQL)
      -> InvestigatorAgent
      -> ReasonerAgent
      -> GuardianAgent
      -> Structured JSON verdict
```

## Why this matches your strategy

1. **Pull model:** every audit request performs a live-style waterfall search abstraction before scoring.
2. **Chain of evidence:** output includes direct links and text-fragment anchors for human verification.
3. **Personalized guardian layer:** clinical profile is combined with regulatory risk to produce final verdict.
4. **Hybrid caching pattern:** SQL cache makes repeated batch checks instant and lowers cost/latency.

## Run locally

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
uvicorn app.main:app --reload
```

Then open `http://127.0.0.1:8000/docs`.

## Example payload

```json
{
  "product_name": "Cough Syrup",
  "batch_number": "OLM24120",
  "manufacturer": "Example Pharma",
  "guardian_profile": {
    "diabetes": true,
    "liver_issues": false,
    "allergies": ["fructose"]
  }
}
```

## Next production upgrades

- Replace `SearchClient` internals with Tavily/official APIs.
- Replace `ReasonerAgent` heuristic with Gemini 2.0 Flash or Groq-hosted Llama-3 prompt chain.
- Add PDF parsing + citation extraction for test failure details (e.g., dissolution, assay, contamination).
- Move cache from SQLite to PostgreSQL + pgvector/SingleStore for hybrid retrieval and audit replay.
