"""
fallback_rules.py — Pure-Python fallback for the Restaurant Reservation Concierge agent.

Used by reasoning.py whenever the LLM API is unavailable.
Do NOT call any external API here.

SCORING MODEL
=============
The score is a float in roughly [0, 100].  Higher score → more urgency → richer incentive.

  occupancy_score   = (1 - occupancy_pct / 100) * 40   # low occupancy = restaurant needs fills badly
  cancel_score      = min(cancellations_count, 5) * 8   # each cancellation adds urgency (capped at 5)
  peak_penalty      = 20 if is_peak else 0               # peak hours sell themselves; reduce urgency
  tier_bonus        = {"Gold": 12, "Silver": 6}.get(customer_tier, 0)   # loyalty customers earn more

  score = occupancy_score + cancel_score - peak_penalty + tier_bonus

THRESHOLDS (agreed with LLM-prompt team via CONTRACT.md)
=========================================================
  score >= 55  →  high_incentive
  score >= 30  →  low_incentive
  score <  30  →  notify

These thresholds encode the same judgment as the LLM system prompt so both paths
produce consistent decisions under normal conditions.
"""

from __future__ import annotations

# ---------------------------------------------------------------------------
# Internal constants — change here AND update the LLM prompt together.
# ---------------------------------------------------------------------------

_WEIGHT_OCCUPANCY = 40      # max contribution when restaurant is empty
_WEIGHT_CANCEL_EACH = 8     # per cancellation
_MAX_CANCEL_CAP = 5         # cap to avoid a single outlier dominating the score
_PEAK_PENALTY = 20          # peak hours reduce urgency — tables fill anyway
_TIER_BONUS: dict[str, int] = {
    "Gold": 12,
    "Silver": 6,
    "Regular": 0,
}

_THRESHOLD_HIGH = 55        # score >= this → high_incentive
_THRESHOLD_LOW = 30         # score >= this → low_incentive  (else → notify)

# ---------------------------------------------------------------------------
# Offer text templates (must mirror the language used in the LLM prompt)
# ---------------------------------------------------------------------------

_OFFERS: dict[str, str] = {
    "notify": (
        "Hi there! A table has just become available for your requested time slot. "
        "We'd love to welcome you — please confirm your reservation at your earliest convenience."
    ),
    "low_incentive": (
        "Hi there! We have a great table available for you. "
        "As a thank-you for your loyalty, enjoy a complimentary welcome drink on us tonight."
    ),
    "high_incentive": (
        "Hi there! A prime table has opened up and we'd love to have you join us. "
        "As our valued guest, please enjoy a complimentary dessert AND 15 % off your bill "
        "as a special thank-you for your continued loyalty."
    ),
}


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def fallback_score(context: dict) -> dict:
    """Compute a rule-based reservation incentive decision without any API call.

    Parameters
    ----------
    context : dict
        Must contain the keys produced by ``data.store.get_context()``:
        ``occupancy_pct`` (int/float, 0–100),
        ``cancellations_count`` (int, >= 0),
        ``is_peak`` (bool),
        ``customer_tier`` (str, one of "Gold" / "Silver" / "Regular"),
        ``time_slot`` (str, HH:MM) — used for reasoning text only,
        ``candidate_reservation_id`` (str) — passed through, not scored.

    Returns
    -------
    dict
        ``{"decision": str, "reasoning": str, "offer": str}``
        where ``decision`` is exactly one of
        ``"notify"`` / ``"low_incentive"`` / ``"high_incentive"``.
    """
    occupancy_pct: float = float(context.get("occupancy_pct", 50))
    cancellations_count: int = int(context.get("cancellations_count", 0))
    is_peak: bool = bool(context.get("is_peak", False))
    customer_tier: str = str(context.get("customer_tier", "Regular"))
    time_slot: str = str(context.get("time_slot", ""))

    # ---- individual score components ----------------------------------------
    occupancy_score = (1.0 - occupancy_pct / 100.0) * _WEIGHT_OCCUPANCY
    cancel_score = min(cancellations_count, _MAX_CANCEL_CAP) * _WEIGHT_CANCEL_EACH
    peak_penalty = _PEAK_PENALTY if is_peak else 0
    tier_bonus = _TIER_BONUS.get(customer_tier, 0)

    score = occupancy_score + cancel_score - peak_penalty + tier_bonus

    # ---- decision mapping ---------------------------------------------------
    if score >= _THRESHOLD_HIGH:
        decision = "high_incentive"
    elif score >= _THRESHOLD_LOW:
        decision = "low_incentive"
    else:
        decision = "notify"

    # ---- plain-English reasoning --------------------------------------------
    peak_note = "a peak-hour slot (tables fill easily)" if is_peak else "an off-peak slot"
    reasoning = (
        f"Fallback scoring: occupancy={occupancy_pct:.0f}% (score +{occupancy_score:.1f}), "
        f"cancellations={cancellations_count} (score +{cancel_score:.1f}), "
        f"is_peak={is_peak} (penalty -{peak_penalty}), "
        f"customer_tier={customer_tier!r} (bonus +{tier_bonus}). "
        f"Total score={score:.1f}. "
        f"The restaurant is {'relatively empty' if occupancy_pct < 50 else 'fairly busy'} "
        f"for {peak_note}"
        + (f", with {cancellations_count} recent cancellation(s) increasing urgency" if cancellations_count else "")
        + (f", and the {customer_tier} tier warrants a generous offer" if tier_bonus > 0 else "")
        + f". Decision threshold: {'>=55->high_incentive' if score >= _THRESHOLD_HIGH else '>=30->low_incentive' if score >= _THRESHOLD_LOW else '<30->notify'}."
    )

    return {
        "decision": decision,
        "reasoning": reasoning,
        "offer": _OFFERS[decision],
    }
