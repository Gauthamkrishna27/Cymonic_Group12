# data/full_check.py
import pandas as pd

customers = pd.read_csv("data/customers.csv")
res = pd.read_csv("data/reservations.csv")
occ = pd.read_csv("data/occupancy_log.csv")

print("=== 1. Row counts ===")
print(f"customers: {len(customers)}, reservations: {len(res)}, occupancy_log: {len(occ)}")

print("\n=== 2. Loyalty tier variety (problem statement requires tiers) ===")
print(customers["loyalty_tier"].value_counts())
gold_count = (customers["loyalty_tier"] == "Gold").sum()
print(f"Gold customers: {gold_count} (need >= 2 for scenarios B and C)")

print("\n=== 3. Reservation status variety ===")
print(res["status"].value_counts())

print("\n=== 4. No capacity violations ===")
bad = occ[occ["tables_occupied"] > occ["total_tables"]]
print(f"Rows where occupied > total: {len(bad)} (should be 0)")

print("\n=== 5. Cancellation consistency (already passed, re-confirming) ===")
mismatches = 0
for _, row in occ.iterrows():
    slot_res = res[(res["date"] == row["date"]) & (res["time_slot"] == row["time_slot"])]
    actual = (slot_res["status"] == "cancelled").sum()
    if actual != row["cancellations_count"]:
        mismatches += 1
print(f"Mismatches: {mismatches} (should be 0)")

print("\n=== 6. The 3 required demo scenarios exist and are correctly shaped ===")
a, b, c = occ.iloc[0], occ.iloc[1], occ.iloc[2]

def pct(row):
    return round(100 * row["tables_occupied"] / row["total_tables"])

print(f"Scenario A (peak/full, expect no_action): is_peak={a['is_peak']}, occ%={pct(a)}, cancels={a['cancellations_count']}")
print(f"Scenario B (quiet, expect notify):        is_peak={b['is_peak']}, occ%={pct(b)}, cancels={b['cancellations_count']}")
print(f"Scenario C (cancel spike, expect incentive): is_peak={c['is_peak']}, occ%={pct(c)}, cancels={c['cancellations_count']}")

print("\n=== 7. Scenario B and C have a valid confirmed Gold candidate reservation ===")
for label, row in [("B", b), ("C", c)]:
    slot_res = res[(res["date"] == row["date"]) & (res["time_slot"] == row["time_slot"]) & (res["status"] == "confirmed")]
    slot_res = slot_res.merge(customers, on="customer_id")
    gold_confirmed = slot_res[slot_res["loyalty_tier"] == "Gold"]
    print(f"Scenario {label}: {len(gold_confirmed)} confirmed Gold-tier reservation(s) found "
          f"({'OK' if len(gold_confirmed) > 0 else 'MISSING — get_context() will fall back to Regular tier!'})")

print("\n=== 8. Foreign key integrity ===")
orphans = set(res["customer_id"]) - set(customers["customer_id"])
print(f"Reservations with unknown customer_id: {len(orphans)} (should be 0)")

print("\n=== 9. Duplicate ID check ===")
print(f"Duplicate customer_id: {customers['customer_id'].duplicated().sum()}")
print(f"Duplicate reservation_id: {res['reservation_id'].duplicated().sum()}")