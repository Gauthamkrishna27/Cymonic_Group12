# CONTRACT.md — Restaurant Reservation Concierge

Read this before writing any code. Field names and function signatures here are locked — do not invent your own.

## Project Overview
An agent-based tool that, given occupancy/cancellation/time/customer-tier context, decides whether to notify a loyalty customer with no offer, a low incentive, or a high incentive — with visible reasoning — and updates the reservation dataset accordingly.

## Tech Stack
- Frontend/UI: Streamlit
- Backend: Python (monolith, no separate server)
- Database: CSV files read/written via pandas (or SQLite if the team prefers — pick ONE, don't mix)
- AI/Reasoning: LLM API call (Groq or Gemini free tier) with a rule-based fallback
- Version Control: Git + GitHub

## Repository Structure
```
project/
│
├── data/
│   ├── customers.csv
│   ├── reservations.csv
│   ├── occupancy_log.csv
│   └── store.py
│
├── agent/
│   ├── reasoning.py
│   ├── prompts.py
│   ├── fallback_rules.py
│   └── test_agent.py
│
├── ui/
│   └── components.py
│
├── docs/
│   └── demo_script.md
│
├── app.py
├── requirements.txt
├── .env.example
├── README.md
└── CONTRACT.md
```

## API / FUNCTION CONTRACT

### `data/store.py`

**`get_context(scenario_id: str) -> dict`**
Request: scenario_id (string, matches a row/group in occupancy_log.csv)
Response:
```json
{
  "occupancy_pct": 32,
  "cancellations_count": 2,
  "is_peak": false,
  "time_slot": "18:00",
  "customer_tier": "Gold",
  "candidate_reservation_id": "R1042"
}
```
Error response: raises `ValueError("scenario not found")` if scenario_id is invalid — caller must catch this.

**`update_record(reservation_id: str, new_status: str, offer_text: str = None) -> None`**
Request: reservation_id (string), new_status (one of: "notified", "offer_sent", "no_action"), offer_text (string or None)
Response: None (writes to reservations.csv)
Error response: raises `KeyError` if reservation_id not found.

**`list_scenarios() -> list[dict]`**
Response: list of `{"scenario_id": str, "label": str}` for populating the UI dropdown.

### `agent/reasoning.py`

**`run_concierge(context: dict) -> dict`**
Request (must match `get_context()` output exactly):
```json
{
  "occupancy_pct": 32,
  "cancellations_count": 2,
  "is_peak": false,
  "time_slot": "18:00",
  "customer_tier": "Gold"
}
```
Response:
```json
{
  "decision": "high_incentive",
  "reasoning": "Occupancy is low for an off-peak slot with a recent cancellation spike; a Gold-tier customer justifies a stronger incentive to protect long-term value.",
  "offer": "Hi [Name], we have a table ready for you tonight at 6 PM — enjoy a complimentary dessert on us as a thank-you for your loyalty."
}
```
`decision` must be exactly one of: `"notify"`, `"low_incentive"`, `"high_incentive"`.
Error response: on API failure/timeout, must internally fall back to `agent/fallback_rules.py` and still return this same JSON shape — never raise an unhandled exception up to the UI.

## DATA CONTRACT

**customers.csv**
| field | type | required | notes |
|---|---|---|---|
| customer_id | string | yes | unique |
| name | string | yes | |
| loyalty_tier | string | yes | one of: Gold, Silver, Regular |
| visit_frequency | integer | yes | visits per month, approx |
| last_visit_date | string (YYYY-MM-DD) | yes | |

**reservations.csv**
| field | type | required | notes |
|---|---|---|---|
| reservation_id | string | yes | unique |
| customer_id | string | yes | FK to customers.csv |
| date | string (YYYY-MM-DD) | yes | |
| time_slot | string (HH:MM) | yes | |
| party_size | integer | yes | |
| status | string | yes | one of: confirmed, cancelled, completed, notified, offer_sent |
| table_id | string | yes | |

**occupancy_log.csv**
| field | type | required | notes |
|---|---|---|---|
| date | string (YYYY-MM-DD) | yes | |
| time_slot | string (HH:MM) | yes | |
| total_tables | integer | yes | |
| tables_occupied | integer | yes | |
| cancellations_count | integer | yes | cancellations in this slot |
| is_peak | boolean | yes | |

No one may add, rename, or remove fields without updating this file and telling the whole team.

## ENVIRONMENT VARIABLES

`.env.example`
```
LLM_API_KEY=
LLM_PROVIDER=groq
```
Owner: Member 2 (Agent/Reasoning Lead) owns obtaining and documenting the API key setup.

## CODING RULES
- Naming: snake_case for Python variables/functions, PascalCase for any classes.
- API/function responses: always return the exact JSON shape defined above — no extra or missing keys.
- Error handling: never let an exception from your module crash the whole app; catch and return a safe default or a clear error string.
- File naming: lowercase with underscores, matches the repo structure above exactly.
- Imports: absolute imports from project root (e.g. `from data.store import get_context`).
- Commit messages: `[module] short description`, e.g. `[agent] add fallback rule scoring`.

## GIT RULES
- `main` = always-working/demo branch. Never commit directly to it except for approved integration merges.
- Branches:
  - `feature/data-layer` (Member 1)
  - `feature/agent-reasoning` (Member 2)
  - `feature/ui` (Member 3)
  - `feature/integration` (Member 4)
- Commit small and often (every 20-30 minutes), not one giant commit at the end.
- Merge into `main` via a quick PR (even a 30-second self-review) — someone else glances at it first when possible.
- Pull from `main` frequently to avoid large, painful merge conflicts later.
- Do not edit another member's owned files directly — flag the issue to them instead.
