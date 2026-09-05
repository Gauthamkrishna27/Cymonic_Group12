# data/generate_data.py
import csv
import random
from datetime import date, timedelta
from faker import Faker

fake = Faker()
random.seed(42)  # reproducible — don't change this once the team starts building on it

LOYALTY_TIERS = ["Gold", "Silver", "Regular"]
TIME_SLOTS = ["12:00", "13:00", "18:00", "19:00", "20:00", "21:00"]
PEAK_SLOTS = {"19:00", "20:00"}
TOTAL_TABLES = 20


def gen_customers(n=20):
    rows = []
    for i in range(1, n + 1):
        rows.append({
            "customer_id": f"C{i:03d}",
            "name": fake.name(),
            "loyalty_tier": random.choices(LOYALTY_TIERS, weights=[0.25, 0.35, 0.4])[0],
            "visit_frequency": random.randint(1, 12),
            "last_visit_date": (date.today() - timedelta(days=random.randint(1, 60))).isoformat(),
        })
    # Guarantee at least 3 Gold customers exist — don't leave this to chance
    for i in range(3):
        rows[i]["loyalty_tier"] = "Gold"
    return rows


def gen_reservations_and_occupancy(customers, days=7):
    reservations, occupancy = [], []
    res_counter = 1
    today = date.today()

    for d in range(days):
        the_date = (today + timedelta(days=d)).isoformat()
        for slot in TIME_SLOTS:
            is_peak = slot in PEAK_SLOTS
            if is_peak:
                cancels = random.randint(0, 1)
            else:
                cancels = random.randint(0, 3)

            # Build reservations for this slot first, so we know how many
            # can plausibly be cancelled without cancelling more than exist
            slot_reservations = []
            num_bookings = random.randint(max(cancels, 1), cancels + 3)
            for _ in range(num_bookings):
                cust = random.choice(customers)
                slot_reservations.append({
                    "reservation_id": f"R{res_counter:04d}",
                    "customer_id": cust["customer_id"],
                    "date": the_date, "time_slot": slot,
                    "party_size": random.randint(1, 6),
                    "status": "confirmed",
                    "table_id": f"T{random.randint(1, TOTAL_TABLES):02d}",
                })
                res_counter += 1

            # Mark exactly `cancels` of them as cancelled, matching occupancy_log
            for r in random.sample(slot_reservations, cancels):
                r["status"] = "cancelled"

            # occupied count = confirmed reservations only (cancelled ones freed up their table)
            occupied = sum(1 for r in slot_reservations if r["status"] == "confirmed")
            if is_peak:
                occupied = max(occupied, random.randint(17, 20))  # still keep peak slots realistically full
            else:
                occupied = min(max(occupied, 3), 14)

            occupancy.append({
                "date": the_date, "time_slot": slot,
                "total_tables": TOTAL_TABLES, "tables_occupied": occupied,
                "cancellations_count": cancels, "is_peak": is_peak,
            })
            reservations.extend(slot_reservations)

    return reservations, occupancy

def force_demo_scenarios(reservations, occupancy, customers):
    """Hand-lock the 3 required demo rows so they exist no matter what random did."""
    gold_ids = [c["customer_id"] for c in customers if c["loyalty_tier"] == "Gold"]

    # Scenario A: near-full peak -> no_action
    occupancy[0].update({"is_peak": True, "tables_occupied": 19, "total_tables": 20, "cancellations_count": 0})
    date_a, slot_a = occupancy[0]["date"], occupancy[0]["time_slot"]
    for r in reservations:
        if r["date"] == date_a and r["time_slot"] == slot_a:
            r["status"] = "confirmed"  # make sure none of these are accidentally cancelled

        # Scenario B: quiet off-peak, Gold customer available -> notify
    occupancy[1].update({"is_peak": False, "tables_occupied": 6, "total_tables": 20, "cancellations_count": 0})
    date_b, slot_b = occupancy[1]["date"], occupancy[1]["time_slot"]
    for r in reservations:
        if r["date"] == date_b and r["time_slot"] == slot_b:
            r["status"] = "confirmed"  # <-- ADD THIS: reset any leftover cancellations to match cancellations_count=0

    found_candidate = False
    for r in reservations:
        if r["date"] == date_b and r["time_slot"] == slot_b:
            r["customer_id"] = gold_ids[0]
            found_candidate = True
            break

    # Scenario C: moderate off-peak, cancellation spike -> low/high incentive
    occupancy[2].update({"is_peak": False, "tables_occupied": 10, "total_tables": 20, "cancellations_count": 3})
    date_c, slot_c = occupancy[2]["date"], occupancy[2]["time_slot"]
    slot_c_reservations = [r for r in reservations if r["date"] == date_c and r["time_slot"] == slot_c]

    # Need at least 1 confirmed candidate (for get_context) + 3 cancelled (to match cancellations_count)
    while len(slot_c_reservations) < 4:
        new_res = {
            "reservation_id": f"R9{len(slot_c_reservations):03d}",  # 9xxx prefix avoids colliding with generated ids
            "customer_id": random.choice(customers)["customer_id"],
            "date": date_c, "time_slot": slot_c,
            "party_size": random.randint(1, 6),
            "status": "confirmed",
            "table_id": f"T{random.randint(1, 20):02d}",
        }
        reservations.append(new_res)
        slot_c_reservations.append(new_res)

    # Mark exactly 3 of them cancelled
    for r in slot_c_reservations[:3]:
        r["status"] = "cancelled"
    # Make sure at least one remains confirmed, and assign it the Gold customer
    slot_c_reservations[3]["status"] = "confirmed"
    slot_c_reservations[3]["customer_id"] = gold_ids[1]

    return reservations, occupancy

def write_csv(path, rows, fieldnames):
    with open(path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


if __name__ == "__main__":
    customers = gen_customers(20)
    reservations, occupancy = gen_reservations_and_occupancy(customers)
    reservations, occupancy = force_demo_scenarios(reservations, occupancy, customers)

    write_csv("data/customers.csv", customers,
               ["customer_id", "name", "loyalty_tier", "visit_frequency", "last_visit_date"])
    write_csv("data/reservations.csv", reservations,
               ["reservation_id", "customer_id", "date", "time_slot", "party_size", "status", "table_id"])
    write_csv("data/occupancy_log.csv", occupancy,
               ["date", "time_slot", "total_tables", "tables_occupied", "cancellations_count", "is_peak"])

    print(f"Generated {len(customers)} customers, {len(reservations)} reservations, {len(occupancy)} occupancy rows.")
    print(f"Locked demo scenarios at: {occupancy[0]['date']}_{occupancy[0]['time_slot']} (peak/full), "
          f"{occupancy[1]['date']}_{occupancy[1]['time_slot']} (quiet), "
          f"{occupancy[2]['date']}_{occupancy[2]['time_slot']} (cancel spike)")