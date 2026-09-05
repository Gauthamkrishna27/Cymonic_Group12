"""
validator.py — Response validation and normalisation layer for the Concierge agent.

Called by reasoning.py on every response (LLM or fallback) before it is
returned to the UI.  Guarantees the caller always gets the exact shape
defined in CONTRACT.md, or a clear exception if the data is unsalvageable.
"""

from __future__ import annotations

import re

# ---------------------------------------------------------------------------
# Allowed decision values (CONTRACT.md §run_concierge)
# ---------------------------------------------------------------------------

_VALID_DECISIONS = {"notify", "low_incentive", "high_incentive"}

# Normalisation map: covers common LLM mis-capitalisation / spacing / wording.
# Keys are lower-cased, stripped versions of what the LLM might return.
_DECISION_ALIASES: dict[str, str] = {
    # exact canonical values (identity)
    "notify": "notify",
    "low_incentive": "low_incentive",
    "high_incentive": "high_incentive",
    # capitalisation variants
    "notify".title(): "notify",
    "low incentive": "low_incentive",
    "low-incentive": "low_incentive",
    "lowincentive": "low_incentive",
    "low_incentive".title(): "low_incentive",
    "high incentive": "high_incentive",
    "high-incentive": "high_incentive",
    "highincentive": "high_incentive",
    "high_incentive".title(): "high_incentive",
    # wordy alternatives an LLM might produce
    "no offer": "notify",
    "notification only": "notify",
    "notification": "notify",
    "small incentive": "low_incentive",
    "minor incentive": "low_incentive",
    "standard incentive": "low_incentive",
    "large incentive": "high_incentive",
    "major incentive": "high_incentive",
    "premium incentive": "high_incentive",
    "strong incentive": "high_incentive",
}


def _normalise_decision(raw: str) -> str | None:
    """Return a canonical decision string, or None if unrecognisable."""
    cleaned = raw.strip().lower()
    # Try direct lookup first (handles most cases after lowercasing)
    if cleaned in _DECISION_ALIASES:
        return _DECISION_ALIASES[cleaned]
    # Try removing punctuation/extra whitespace
    simplified = re.sub(r"[^a-z ]", " ", cleaned).strip()
    simplified = re.sub(r"\s+", " ", simplified)
    if simplified in _DECISION_ALIASES:
        return _DECISION_ALIASES[simplified]
    # Last resort: substring scan in priority order
    for canonical in ("high_incentive", "low_incentive", "notify"):
        if canonical.replace("_", " ") in simplified or canonical in simplified:
            return canonical
    return None


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def validate(response: dict) -> dict:
    """Validate and normalise a concierge response dict.

    Acceptable input shapes
    -----------------------
    Best case — all three keys present with good values::

        {"decision": "high_incentive", "reasoning": "...", "offer": "..."}

    Tolerated — decision is a recognisable mis-cased variant::

        {"decision": "High Incentive", "reasoning": "...", "offer": "..."}

    Unsalvageable — missing required keys or unrecognisable decision::

        {}                                     → ValueError
        {"decision": "go crazy"}               → ValueError
        {"decision": "notify"}                 → ValueError  (missing reasoning/offer)

    Parameters
    ----------
    response : dict
        Raw dict returned by the LLM client or fallback_score().

    Returns
    -------
    dict
        A validated ``{"decision": str, "reasoning": str, "offer": str}`` dict.
        The ``decision`` value is guaranteed to be in ``_VALID_DECISIONS``.
        ``reasoning`` and ``offer`` are stripped strings.

    Raises
    ------
    ValueError
        If the response cannot be recovered into a valid shape.
    """
    if not isinstance(response, dict):
        raise ValueError(
            f"validate() expected a dict, got {type(response).__name__!r}."
        )

    # ---- 1. Check all required keys are present and non-empty ---------------
    required = ("decision", "reasoning", "offer")
    missing = [k for k in required if k not in response]
    if missing:
        raise ValueError(
            f"Response is missing required key(s): {missing}. "
            f"Received keys: {list(response.keys())}."
        )

    empty = [k for k in required if not str(response[k]).strip()]
    if empty:
        raise ValueError(
            f"Response has empty value(s) for key(s): {empty}. "
            f"All three fields must be non-empty strings."
        )

    # ---- 2. Normalise decision ----------------------------------------------
    raw_decision = str(response["decision"])
    normalised = _normalise_decision(raw_decision)

    if normalised is None:
        raise ValueError(
            f"Cannot normalise decision value {raw_decision!r}. "
            f"Expected one of {sorted(_VALID_DECISIONS)} (or a recognisable variant)."
        )

    # ---- 3. Return clean, validated dict ------------------------------------
    return {
        "decision": normalised,
        "reasoning": str(response["reasoning"]).strip(),
        "offer": str(response["offer"]).strip(),
    }
