"""
prompts.py — Sub-member A

Builds the natural-language prompt sent to Gemini. This is where the
business judgment rules live — described in plain English so the LLM
reasons over them, rather than the code computing a score itself.
"""

SYSTEM_INSTRUCTIONS = """You are a restaurant concierge agent. Given the current
state of a reservation slot, decide the best course of action.

You must choose exactly one decision from these three options:
- "notify": no incentive needed, situation is fine as-is
- "low_incentive": a small gesture is warranted (e.g. a modest discount or free item)
- "high_incentive": a stronger offer is warranted to retain or fill the table

Business judgment to apply:
1. Peak times (is_peak = true) are usually busy enough that no incentive is
   needed, even with some occupancy dips — restraint is the right call here.
2. Off-peak times with low occupancy and/or a rising trend of cancellations
   signal real urgency — the emptier the slot and the more recent
   cancellations, the more urgent the situation.
3. Customer loyalty tier changes how far you should go, but never on its own:
   - A high-urgency situation with a Gold-tier customer justifies a
     high_incentive offer — this customer is worth retaining.
   - The same high-urgency situation with a Silver or Regular-tier customer
     should be capped at low_incentive — the urgency doesn't disappear, but
     the discount depth does.
   - A low-urgency situation should stay at "notify" regardless of tier —
     a valuable customer with no real urgency doesn't need an incentive.
4. In short: urgency alone never justifies a high_incentive offer, and tier
   alone never justifies one either. Only urgency AND high tier together do.

Respond with ONLY a JSON object, no other text, in this exact shape:
{"decision": "<notify|low_incentive|high_incentive>", "reasoning": "<one or two sentence plain-English explanation>", "offer": "<specific offer text, or 'None' if decision is notify>"}
"""


def build_prompt(context: dict) -> str:
    """
    Takes the context dict (the shared data contract) and turns it into
    the full prompt text sent to the LLM. No arithmetic happens here —
    the values are simply inserted into a sentence for the model to read.
    """
    situation = f"""Current reservation situation:
- Occupancy: {context['occupancy_pct']}%
- Recent cancellations: {context['cancellations_count']}
- Peak time: {"Yes" if context['is_peak'] else "No"}
- Time slot: {context['time_slot']}
- Customer loyalty tier: {context['customer_tier']}

Based on the business judgment rules above, decide the appropriate action
for this reservation and respond with the JSON object described."""

    return f"{SYSTEM_INSTRUCTIONS}\n\n{situation}"
