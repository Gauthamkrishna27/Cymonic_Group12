# data/store.py
import pandas as pd
import os
from datetime import datetime

BASE_DIR = os.path.dirname(__file__)
CUSTOMERS_PATH = os.path.join(BASE_DIR, "customers.csv")
RESERVATIONS_PATH = os.path.join(BASE_DIR, "reservations.csv")
OCCUPANCY_PATH = os.path.join(BASE_DIR, "occupancy_log.csv")
DECISIONS_LOG_PATH = os.path.join(BASE_DIR, "decisions_log.csv")

VALID_STATUSES = {"notified", "offer_sent"}  # "no_action" -> skip calling update_record() entirely


def _parse_bool(value) -> bool:
    """Guard against pandas reading is_peak as the literal string 'False',
    which bool('False') would wrongly evaluate as True."""
    return str(value).strip().lower() in ("true", "1", "yes")


def _scenario_key(row):
    """Build a stable scenario_id like '2026-09-05_18:00' from an occupancy row."""
    return f"{row['date']}_{row['time_slot']}"


def list_scenarios() -> list[dict]:
    occ = pd.read_csv(OCCUPANCY_PATH)
    scenarios = []
    for _, row in occ.iterrows():
        sid = _scenario_key(row)
        pct = round(100 * row["tables_occupied"] / row["total_tables"])
        peak_label = "PEAK" if _parse_bool(row["is_peak"]) else "off-peak"
        label = f"{row['date']} {row['time_slot']} — {pct}% full, {row['cancellations_count']} cancels, {peak_label}"
        scenarios.append({"scenario_id": sid, "label": label})
    return scenarios


def get_context(scenario_id: str) -> dict:
    occ = pd.read_csv(OCCUPANCY_PATH)
    occ["sid"] = occ.apply(_scenario_key, axis=1)
    match = occ[occ["sid"] == scenario_id]
    if match.empty:
        raise ValueError("scenario not found")
    row = match.iloc[0]

    date_, slot = scenario_id.split("_")
    res = pd.read_csv(RESERVATIONS_PATH)
    candidates = res[(res["date"] == date_) & (res["time_slot"] == slot) & (res["status"] == "confirmed")]

    customers = pd.read_csv(CUSTOMERS_PATH)
    if not candidates.empty:
        cust_row = candidates.iloc[0]
        cust = customers[customers["customer_id"] == cust_row["customer_id"]].iloc[0]
        tier = cust["loyalty_tier"]
        cand_res_id = cust_row["reservation_id"]
    else:
        tier = "Regular"
        cand_res_id = None

    occupancy_pct = round(100 * row["tables_occupied"] / row["total_tables"])

    return {
        "occupancy_pct": int(occupancy_pct),
        "cancellations_count": int(row["cancellations_count"]),
        "is_peak": _parse_bool(row["is_peak"]),
        "time_slot": slot,
        "customer_tier": tier,
        "candidate_reservation_id": cand_res_id,
    }


def update_record(reservation_id: str, new_status: str, offer_text: str = None) -> None:
    if new_status not in VALID_STATUSES:
        raise ValueError(
            f"new_status must be one of {VALID_STATUSES} — "
            f"'no_action' cases should skip calling update_record(), not pass it in."
        )

    res = pd.read_csv(RESERVATIONS_PATH)
    if reservation_id not in res["reservation_id"].values:
        raise KeyError(f"{reservation_id} not found")
    idx = res.index[res["reservation_id"] == reservation_id][0]
    res.at[idx, "status"] = new_status
    res.to_csv(RESERVATIONS_PATH, index=False)

    log_row = pd.DataFrame([{
        "reservation_id": reservation_id,
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "decision": new_status,
        "offer_text": offer_text or "",
    }])
    if os.path.exists(DECISIONS_LOG_PATH):
        log_row.to_csv(DECISIONS_LOG_PATH, mode="a", header=False, index=False)
    else:
        log_row.to_csv(DECISIONS_LOG_PATH, index=False)


if __name__ == "__main__":
    scenarios = list_scenarios()
    print(f"{len(scenarios)} scenarios available\n")

    print("--- Testing get_context() on first 3 scenarios ---")
    for s in scenarios[:3]:
        ctx = get_context(s["scenario_id"])
        print(f"{s['label']}\n  -> {ctx}\n")

    print("--- Testing error handling ---")
    try:
        get_context("bad_id")
    except ValueError as e:
        print(f"get_context correctly raised: {e}")

    try:
        update_record("BAD_ID", "notified")
    except KeyError as e:
        print(f"update_record correctly raised: {e}")

    try:
        update_record("R0001", "no_action")
    except ValueError as e:
        print(f"update_record correctly rejected invalid status: {e}")
    print("\n--- Testing a successful update_record() call ---")
    update_record("R0001", "notified", offer_text="Test offer for verification")
    print("update_record succeeded — check data/decisions_log.csv now, it should exist with 1 row.")