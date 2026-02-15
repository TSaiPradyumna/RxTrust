# RxTrust: Agentic Drug Safety Verification (FastAPI Reference Implementation)

This repository now includes two runnable paths:

1. **FastAPI reference API** (full agentic architecture).
2. **Zero-dependency sample runner** for personal PC validation with the CDSCO NSQ sample rows you shared.

## Architecture (API path)

- **Investigator (Perceive):** waterfall search across CDSCO → FDA → Health Canada and exact-match check against local NSQ dataset.
- **Reasoner (Reason):** structured risk score + compliance probability, with high-risk escalation on exact NSQ batch hit.
- **Guardian (Act):** personalized profile risk layer (diabetes/liver/allergy).
- **CacheStore (SQL):** repeated checks return instantly.

## Personal PC usage

### A) Run the sample cases immediately (no pip install needed)

```bash
python scripts/run_user_cases.py
```

This prints verdicts for your provided case list (rows 57–76).

### B) Run the API locally

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
uvicorn app.main:app --reload
```

Then open `http://127.0.0.1:8000/docs`.

## Data included

- `data/cdsco_nsq_dec25_subset.json` → subset containing your provided records (IDs 57–76).

## Next production upgrades

- Replace search abstraction with Tavily or official regulatory APIs.
- Replace heuristic reasoner with Gemini 2.0 Flash or Groq Llama-3 prompt chain.
- Add PDF parser + line-level citations from official lab reports.
- Move cache to PostgreSQL + vector index for large-scale hybrid retrieval.
