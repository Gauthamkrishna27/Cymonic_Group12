"""
Mock Backend & Contract Layer for Problem #3 Restaurant Reservation Concierge.
Conforms strictly to CONTRACT.md requirements:
- list_scenarios() -> list[dict]
- get_context(scenario_id: str) -> dict
- run_concierge(context: dict) -> dict
- update_record(reservation_id: str, new_status: str, offer_text: str = None) -> dict
"""

import copy
from datetime import datetime

# 3 Canonical Hackathon Scenarios matching the Hackathon Execution Plan
SCENARIOS = [
    {
        "id": "scenario_peak_full",
        "label": "Scenario 1: Friday 8:00 PM - Peak Window (92% Occ, 0 Cancellations)",
        "badge": "Peak Hour - 92% Occ",
        "badge_type": "success",
        "description": "Prime Friday night dinner rush. Natural walk-in velocity will fill tables. Discounting would dilute margins.",
        "context": {
            "scenario_id": "scenario_peak_full",
            "time_slot": "20:00",
            "is_peak": True,
            "occupancy_pct": 92.0,
            "cancellations_count": 0,
            "customer_id": "CUST-101",
            "customer_name": "Eleanor Vance",
            "customer_tier": "Gold",
            "reservation_id": "RES-8801",
            "table_id": "T-04",
            "party_size": 2,
            "last_visit_days_ago": 12,
            "lifetime_spend": "$1,420"
        },
        "expected_decision": "notify",
        "mock_result": {
            "decision": "notify",
            "reasoning": (
                "Dining room is operating at 92.0% capacity during prime peak hours (Friday 8:00 PM) with zero cancellations. "
                "Organic walk-in foot traffic and regular reservations will naturally absorb the remaining 2 vacant tables. "
                "Applying any discount here would dilute high-margin peak revenue and train diners to expect price cuts. "
                "Recommended Strategy: Send a personalized reservation confirmation and soft check-in reminder with zero discount."
            ),
            "offer": (
                "Good evening Eleanor! We look forward to welcoming your party of 2 to Le Bistro tonight at 8:00 PM. "
                "Your preferred booth (Table 4) is secured under your Gold Loyalty status. "
                "Please reply to this text if you require any adjustments before arrival."
            )
        }
    },
    {
        "id": "scenario_offpeak_cancellations",
        "label": "Scenario 2: Wednesday 2:30 PM - Moderate Off-Peak with Cancellations (52% Occ, 3 Cancellations)",
        "badge": "Off-Peak - 52% Occ",
        "badge_type": "warning",
        "description": "Mid-week afternoon slump compounded by 3 sudden cancellations in the last 45 minutes.",
        "context": {
            "scenario_id": "scenario_offpeak_cancellations",
            "time_slot": "14:30",
            "is_peak": False,
            "occupancy_pct": 52.0,
            "cancellations_count": 3,
            "customer_id": "CUST-205",
            "customer_name": "Marcus Brody",
            "customer_tier": "Silver",
            "reservation_id": "RES-4520",
            "table_id": "T-12",
            "party_size": 3,
            "last_visit_days_ago": 28,
            "lifetime_spend": "$680"
        },
        "expected_decision": "low_incentive",
        "mock_result": {
            "decision": "low_incentive",
            "reasoning": (
                "Mid-week lunch service is at 52.0% occupancy, amplified by 3 sudden cancellations over the past hour. "
                "With only 90 minutes until service, empty tables will erode afternoon profitability. "
                "However, heavy cash discounting degrades brand prestige. A high-perceived-value, low-cost culinary perk "
                "(Complimentary Artisan Dessert & Digestif) creates genuine booking urgency while protecting entree margins for Silver guest Marcus Brody."
            ),
            "offer": (
                "Hi Marcus! Looking for a delightful lunch break? Tables are available for our 2:30 PM seating today at Le Bistro. "
                "As a Silver member, book by 2:00 PM and enjoy a complimentary Chef's Seasonal Dessert & Artisanal Coffee on us! "
                "Tap here to claim: lebistro.menu/claim-perk-silver"
            )
        }
    },
    {
        "id": "scenario_offpeak_spike_gold",
        "label": "Scenario 3: Tuesday 5:30 PM - Severe Dip & Cancellation Spike (25% Occ, 5 Cancellations)",
        "badge": "Slump - 25% Occ",
        "badge_type": "error",
        "description": "Severe early dinner slump with 5 cancellations leaving the kitchen and waitstaff heavily underutilized.",
        "context": {
            "scenario_id": "scenario_offpeak_spike_gold",
            "time_slot": "17:30",
            "is_peak": False,
            "occupancy_pct": 25.0,
            "cancellations_count": 5,
            "customer_id": "CUST-309",
            "customer_name": "Sophia Laurent",
            "customer_tier": "Gold",
            "reservation_id": "RES-1092",
            "table_id": "T-08",
            "party_size": 4,
            "last_visit_days_ago": 15,
            "lifetime_spend": "$2,850"
        },
        "expected_decision": "high_incentive",
        "mock_result": {
            "decision": "high_incentive",
            "reasoning": (
                "Emergency capacity shortfall detected: Tuesday 5:30 PM occupancy has plummeted to 25.0% after 5 abrupt cancellations. "
                "Fixed kitchen prep and staffed floor costs heavily outweigh discounting risk. "
                "Targeting premier VIP Sophia Laurent (Gold Tier, $2,850 lifetime spend) with an exclusive 20% dining credit ensures "
                "a high party order value (party of 4) while converting an idle time window into customer goodwill."
            ),
            "offer": (
                "Exclusive VIP Invitation for Sophia Laurent: We have reserved prime Table 8 for your party of 4 this evening between 5:30 PM and 6:30 PM. "
                "Enjoy an exclusive 20% dining credit across your entire bill plus complimentary sommelier pairings. "
                "Reply YES or tap to confirm: lebistro.menu/vip-gold-claim"
            )
        }
    }
]

# In-memory mock database of recent reservations
MOCK_RESERVATIONS = [
    {"reservation_id": "RES-8801", "customer_name": "Eleanor Vance", "tier": "Gold", "time_slot": "20:00", "party_size": 2, "table_id": "T-04", "status": "confirmed", "offer_text": None, "updated_at": "18:30"},
    {"reservation_id": "RES-4520", "customer_name": "Marcus Brody", "tier": "Silver", "time_slot": "14:30", "party_size": 3, "table_id": "T-12", "status": "confirmed", "offer_text": None, "updated_at": "13:10"},
    {"reservation_id": "RES-1092", "customer_name": "Sophia Laurent", "tier": "Gold", "time_slot": "17:30", "party_size": 4, "table_id": "T-08", "status": "cancelled", "offer_text": None, "updated_at": "16:45"},
    {"reservation_id": "RES-9931", "customer_name": "David Kim", "tier": "Regular", "time_slot": "19:00", "party_size": 2, "table_id": "T-02", "status": "confirmed", "offer_text": None, "updated_at": "17:00"},
    {"reservation_id": "RES-7714", "customer_name": "Amira Patel", "tier": "Gold", "time_slot": "21:00", "party_size": 2, "table_id": "T-06", "status": "confirmed", "offer_text": None, "updated_at": "19:15"},
    {"reservation_id": "RES-3305", "customer_name": "Liam Connor", "tier": "Regular", "time_slot": "13:00", "party_size": 2, "table_id": "T-11", "status": "completed", "offer_text": None, "updated_at": "14:15"}
]

MOCK_HOURLY_TRENDS = [
    {"slot": "12:00 PM", "occupancy": 45, "cancellations": 1, "is_peak": False},
    {"slot": "01:00 PM", "occupancy": 78, "cancellations": 0, "is_peak": True},
    {"slot": "02:30 PM", "occupancy": 52, "cancellations": 3, "is_peak": False},
    {"slot": "03:30 PM", "occupancy": 28, "cancellations": 1, "is_peak": False},
    {"slot": "04:30 PM", "occupancy": 32, "cancellations": 2, "is_peak": False},
    {"slot": "05:30 PM", "occupancy": 25, "cancellations": 5, "is_peak": False},
    {"slot": "07:00 PM", "occupancy": 85, "cancellations": 1, "is_peak": True},
    {"slot": "08:00 PM", "occupancy": 92, "cancellations": 0, "is_peak": True},
    {"slot": "09:30 PM", "occupancy": 64, "cancellations": 2, "is_peak": False}
]

def list_scenarios() -> list[dict]:
    """Returns the list of scenarios for UI selection."""
    return copy.deepcopy(SCENARIOS)

def get_context(scenario_id: str) -> dict:
    """Retrieves context dictionary matching CONTRACT.md for a scenario ID."""
    for s in SCENARIOS:
        if s["id"] == scenario_id:
            return copy.deepcopy(s["context"])
    return copy.deepcopy(SCENARIOS[0]["context"])

def update_record(reservation_id: str, new_status: str, offer_text: str = None) -> dict:
    """Updates reservation record in dataset matching Member 1 signature."""
    now_str = datetime.now().strftime("%H:%M:%S")
    for r in MOCK_RESERVATIONS:
        if r["reservation_id"] == reservation_id:
            r["status"] = new_status
            r["offer_text"] = offer_text
            r["updated_at"] = now_str
            return copy.deepcopy(r)
    
    new_entry = {
        "reservation_id": reservation_id,
        "customer_name": "Valued Guest",
        "tier": "Gold",
        "time_slot": "Active Slot",
        "party_size": 2,
        "table_id": "T-01",
        "status": new_status,
        "offer_text": offer_text,
        "updated_at": now_str
    }
    MOCK_RESERVATIONS.insert(0, new_entry)
    return new_entry

def get_all_reservations() -> list[dict]:
    """Returns current reservation records."""
    return copy.deepcopy(MOCK_RESERVATIONS)

def get_occupancy_trends() -> list[dict]:
    """Returns trend metrics across dining slots."""
    return copy.deepcopy(MOCK_HOURLY_TRENDS)

def run_concierge(context: dict) -> dict:
    """
    Reasoning engine conforming to Member 2 CONTRACT.md.
    Returns:
      {
        'decision': 'notify' | 'low_incentive' | 'high_incentive',
        'reasoning': '...',
        'offer': '...'
      }
    """
    scenario_id = context.get("scenario_id")
    for s in SCENARIOS:
        if s["id"] == scenario_id:
            return copy.deepcopy(s["mock_result"])

    # Dynamic fallback evaluation for custom simulator or unseen parameters
    occupancy = float(context.get("occupancy_pct", 50.0))
    cancellations = int(context.get("cancellations_count", 0))
    is_peak = bool(context.get("is_peak", False))
    tier = str(context.get("customer_tier", "Regular"))
    slot = str(context.get("time_slot", "19:00"))
    name = str(context.get("customer_name", "Valued Guest"))

    if is_peak or occupancy >= 80.0:
        decision = "notify"
        reasoning = (
            f"Occupancy is high at {occupancy:.1f}% for slot {slot} (Peak={is_peak}) with only {cancellations} cancellation(s). "
            "Natural reservation pace will replenish capacity without requiring promotional concessions. "
            "Preserving table margins and brand status is prioritized."
        )
        offer = (
            f"Hello {name}, your reservation at Le Bistro for {slot} is scheduled. "
            "We look forward to welcoming you - please inform us if your arrival plans change."
        )
    elif occupancy < 40.0 and cancellations >= 3 and tier in ["Gold", "Silver"]:
        decision = "high_incentive"
        reasoning = (
            f"Severe occupancy crisis detected: only {occupancy:.1f}% filled with {cancellations} recent cancellations at {slot}. "
            f"Fixed labor and overhead costs make idle tables expensive. Guest {name} ({tier} Tier) has high expected spend. "
            "Offering a targeted 20% dining incentive efficiently reclaims capacity and drives immediate booking action."
        )
        offer = (
            f"Special Dining Perk for {name} ({tier} Member): Join us at Le Bistro for {slot} today "
            "and enjoy 20% off your total dining bill! Use private code: DINE20 at checkout."
        )
    elif occupancy < 65.0 or cancellations >= 2:
        decision = "low_incentive"
        reasoning = (
            f"Moderate off-peak vulnerability: {occupancy:.1f}% occupancy and {cancellations} cancellation(s) at {slot}. "
            "A direct discount is unnecessary and harms pricing anchors. Offering a complimentary welcome appetizer or dessert "
            "provides a delightful incentive while fully protecting entree margins."
        )
        offer = (
            f"Greetings {name}! Reserve your table for {slot} today at Le Bistro and savor a complimentary "
            "Chef's Seasonal Appetizer and Welcome Prosecco. Reply BOOK to reserve immediately."
        )
    else:
        decision = "notify"
        reasoning = (
            f"Balanced capacity: {occupancy:.1f}% occupancy with {cancellations} cancellation(s). "
            "Standard notification maintains diner engagement without issuing financial incentives."
        )
        offer = (
            f"Hello {name}, tables are currently available for our {slot} service at Le Bistro. "
            "We would love to host you today - book online at lebistro.menu"
        )

    return {
        "decision": decision,
        "reasoning": reasoning,
        "offer": offer
    }
