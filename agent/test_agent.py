"""
test_agent.py — Integration smoke-tests for the Concierge agent.

Run from the project root:
    python -m agent.test_agent

What this script tests
----------------------
1. fallback_score() — exercised against 7 distinct context combinations that
   deliberately span all three decision bands (notify / low_incentive /
   high_incentive) so we can confirm the scoring model is not degenerate.

2. validate() — exercised against good responses, fixable LLM mis-casings,
   and deliberately broken inputs to confirm error paths work.

3. call_llm() stub — imported if available (once reasoning.py is wired up)
   and called on a representative context; LLM and fallback decisions are
   printed side-by-side for visual comparison.

Output is plain stdout — no test framework required.
"""

from __future__ import annotations

import sys
import os
import textwrap

# ---------------------------------------------------------------------------
# Path setup — allow running as a plain script from the project root OR via
# `python -m agent.test_agent`
# ---------------------------------------------------------------------------
_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

from agent.fallback_rules import fallback_score          # noqa: E402
from agent.validator import validate                      # noqa: E402


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_DIVIDER = "-" * 72

def _header(title: str) -> None:
    print(f"\n{_DIVIDER}")
    print(f"  {title}")
    print(_DIVIDER)

def _print_result(label: str, ctx: dict, result: dict) -> None:
    """Pretty-print a single test case."""
    print(f"\n  [{label}]")
    print(f"  Context  : occ={ctx['occupancy_pct']}%  cancels={ctx['cancellations_count']}"
          f"  peak={ctx['is_peak']}  tier={ctx['customer_tier']}")
    print(f"  Decision : {result['decision']}")
    print(f"  Reasoning: {textwrap.fill(result['reasoning'], width=66, subsequent_indent='             ')}")


# ---------------------------------------------------------------------------
# Test cases — 7 contexts designed to cover all three bands
# ---------------------------------------------------------------------------

CASES: list[tuple[str, dict]] = [
    # -- CASE 1: Empty restaurant, many cancellations, Gold customer, off-peak
    # Expected: high_incentive
    # Score:  (1-0.20)*40 + 5*8 - 0 + 12 = 32 + 40 + 0 + 12 = 84
    (
        "C1 - Very urgent - empty + cancels + Gold",
        {
            "occupancy_pct": 20,
            "cancellations_count": 5,
            "is_peak": False,
            "customer_tier": "Gold",
            "time_slot": "14:00",
            "candidate_reservation_id": "R1001",
        },
    ),
    # -- CASE 2: Moderate occupancy, a couple of cancellations, Silver, off-peak
    # Expected: low_incentive or high_incentive
    # Score:  (1-0.55)*40 + 2*8 - 0 + 6 = 18 + 16 + 0 + 6 = 40
    (
        "C2 - Moderate urgency - mid-occ + Silver",
        {
            "occupancy_pct": 55,
            "cancellations_count": 2,
            "is_peak": False,
            "customer_tier": "Silver",
            "time_slot": "13:00",
            "candidate_reservation_id": "R1002",
        },
    ),
    # -- CASE 3: Full restaurant, no cancellations, peak, Regular tier
    # Expected: notify
    # Score:  (1-0.95)*40 + 0 - 20 + 0 = 2 - 20 = -18
    (
        "C3 - Low urgency - full + peak + Regular",
        {
            "occupancy_pct": 95,
            "cancellations_count": 0,
            "is_peak": True,
            "customer_tier": "Regular",
            "time_slot": "19:00",
            "candidate_reservation_id": "R1003",
        },
    ),
    # -- CASE 4: Half-empty, no cancellations, peak, Gold
    # Expected: notify / borderline low_incentive
    # Score:  (1-0.50)*40 + 0 - 20 + 12 = 20 - 20 + 12 = 12
    (
        "C4 - Peak kills urgency - 50% occ + Gold + peak",
        {
            "occupancy_pct": 50,
            "cancellations_count": 0,
            "is_peak": True,
            "customer_tier": "Gold",
            "time_slot": "20:00",
            "candidate_reservation_id": "R1004",
        },
    ),
    # -- CASE 5: Very empty, no cancellations, off-peak, Regular
    # Expected: low_incentive
    # Score:  (1-0.10)*40 + 0 - 0 + 0 = 36
    (
        "C5 - Empty + off-peak + Regular (no loyalty bonus)",
        {
            "occupancy_pct": 10,
            "cancellations_count": 0,
            "is_peak": False,
            "customer_tier": "Regular",
            "time_slot": "15:00",
            "candidate_reservation_id": "R1005",
        },
    ),
    # -- CASE 6: Moderate occupancy, many cancellations, peak, Silver
    # Expected: low_incentive
    # Score:  (1-0.60)*40 + 4*8 - 20 + 6 = 16 + 32 - 20 + 6 = 34
    (
        "C6 - Many cancels but peak dampens - Silver",
        {
            "occupancy_pct": 60,
            "cancellations_count": 4,
            "is_peak": True,
            "customer_tier": "Silver",
            "time_slot": "19:30",
            "candidate_reservation_id": "R1006",
        },
    ),
    # -- CASE 7: Empty restaurant, max cancellations, off-peak, Regular
    # Expected: high_incentive (urgency is extreme even without loyalty bonus)
    # Score:  (1-0.05)*40 + 5*8 - 0 + 0 = 38 + 40 = 78
    (
        "C7 - Extreme urgency - nearly empty + max cancels",
        {
            "occupancy_pct": 5,
            "cancellations_count": 8,   # capped at 5 internally
            "is_peak": False,
            "customer_tier": "Regular",
            "time_slot": "17:00",
            "candidate_reservation_id": "R1007",
        },
    ),
]


# ---------------------------------------------------------------------------
# Section 1: fallback_score() tests
# ---------------------------------------------------------------------------

def test_fallback_score() -> None:
    _header("SECTION 1 - fallback_score() across 7 distinct contexts")

    results = []
    for label, ctx in CASES:
        result = fallback_score(ctx)
        results.append(result["decision"])
        _print_result(label, ctx, result)

    # Confirm not all decisions are identical — scoring must discriminate
    unique_decisions = set(results)
    print(f"\n  Unique decisions produced: {sorted(unique_decisions)}")
    assert len(unique_decisions) > 1, (
        "FAIL: fallback_score() returned the same decision for every case — "
        "the scoring model is degenerate!"
    )
    all_valid = all(d in {"notify", "low_incentive", "high_incentive"} for d in results)
    assert all_valid, "FAIL: One or more decisions are not valid canonical values."
    print("  [OK] Decisions vary across cases - scoring model is discriminative.")
    print("  [OK] All decision values are valid canonical strings.")


# ---------------------------------------------------------------------------
# Section 2: validate() tests
# ---------------------------------------------------------------------------

def test_validate() -> None:
    _header("SECTION 2 - validate() normalisation and error handling")

    # 2a. Perfect input - should pass through unchanged
    good = {"decision": "high_incentive", "reasoning": "Some reason.", "offer": "Some offer."}
    out = validate(good)
    assert out["decision"] == "high_incentive", f"Expected high_incentive, got {out['decision']}"
    print("\n  [2a] Perfect input -> passes unchanged [OK]")

    # 2b. LLM mis-casing: "High Incentive" -> should be fixed
    mis_cased = {"decision": "High Incentive", "reasoning": "Reason.", "offer": "Offer."}
    out = validate(mis_cased)
    assert out["decision"] == "high_incentive", f"Expected high_incentive, got {out['decision']}"
    print("  [2b] 'High Incentive' -> normalised to 'high_incentive' [OK]")

    # 2c. Another mis-casing: "Low_Incentive" (title-cased underscore variant)
    mis_cased2 = {"decision": "Low_Incentive", "reasoning": "Reason.", "offer": "Offer."}
    out = validate(mis_cased2)
    assert out["decision"] == "low_incentive", f"Expected low_incentive, got {out['decision']}"
    print("  [2c] 'Low_Incentive' -> normalised to 'low_incentive' [OK]")

    # 2d. Wordy alias: "notification only"
    wordy = {"decision": "notification only", "reasoning": "R.", "offer": "O."}
    out = validate(wordy)
    assert out["decision"] == "notify", f"Expected notify, got {out['decision']}"
    print("  [2d] 'notification only' -> normalised to 'notify' [OK]")

    # 2e. Missing key - must raise ValueError
    try:
        validate({"decision": "notify", "reasoning": "R."})   # missing "offer"
        assert False, "Should have raised ValueError"
    except ValueError as exc:
        print(f"  [2e] Missing 'offer' key -> ValueError raised [OK]  ({exc})")

    # 2f. Empty value - must raise ValueError
    try:
        validate({"decision": "notify", "reasoning": "", "offer": "O."})
        assert False, "Should have raised ValueError"
    except ValueError as exc:
        print(f"  [2f] Empty 'reasoning' -> ValueError raised [OK]  ({exc})")

    # 2g. Unrecognisable decision - must raise ValueError
    try:
        validate({"decision": "go crazy", "reasoning": "R.", "offer": "O."})
        assert False, "Should have raised ValueError"
    except ValueError as exc:
        print(f"  [2g] Unrecognisable decision -> ValueError raised [OK]  ({exc})")

    # 2h. Non-dict input - must raise ValueError
    try:
        validate("not a dict")     # type: ignore[arg-type]
        assert False, "Should have raised ValueError"
    except ValueError as exc:
        print(f"  [2h] Non-dict input -> ValueError raised [OK]  ({exc})")

    print("\n  [OK] All validate() cases passed.")


# ---------------------------------------------------------------------------
# Section 3: call_llm() side-by-side comparison (optional — skips gracefully)
# ---------------------------------------------------------------------------

def test_llm_vs_fallback() -> None:
    _header("SECTION 3 - call_llm() vs fallback_score() side-by-side (optional)")

    try:
        from agent.reasoning import run_concierge  # noqa: PLC0415
    except ImportError:
        print("\n  [SKIP] agent.reasoning not yet importable - skipping LLM comparison.")
        return

    # Use a representative mid-range context for the live comparison
    ctx = {
        "occupancy_pct": 35,
        "cancellations_count": 3,
        "is_peak": False,
        "customer_tier": "Gold",
        "time_slot": "18:00",
        "candidate_reservation_id": "R1042",
    }

    print("\n  Running fallback_score() ...")
    fb = fallback_score(ctx)
    print(f"  Fallback decision : {fb['decision']}")

    print("  Running run_concierge() (may call LLM or its own fallback) ...")
    try:
        llm = run_concierge(ctx)
        print(f"  LLM/reasoning decision: {llm['decision']}")
        if fb["decision"] == llm["decision"]:
            print("  -> Both paths agree [OK]")
        else:
            print(
                f"  -> Paths differ ({fb['decision']} vs {llm['decision']}) - "
                "this is acceptable if context is near a threshold boundary."
            )
    except Exception as exc:  # noqa: BLE001
        print(f"  [WARN] run_concierge() raised: {exc}")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print("\n" + "=" * 72)
    print("  Restaurant Reservation Concierge - Agent Test Suite")
    print("=" * 72)

    failed = 0
    for test_fn in (test_fallback_score, test_validate, test_llm_vs_fallback):
        try:
            test_fn()
        except AssertionError as exc:
            print(f"\n  [FAIL] ASSERTION in {test_fn.__name__}: {exc}")
            failed += 1
        except Exception as exc:  # noqa: BLE001
            print(f"\n  [ERROR] UNEXPECTED in {test_fn.__name__}: {exc}")
            failed += 1

    print(f"\n{'=' * 72}")
    if failed:
        print(f"  {failed} test section(s) FAILED.")
        sys.exit(1)
    else:
        print("  All test sections PASSED.")
    print("=" * 72 + "\n")
