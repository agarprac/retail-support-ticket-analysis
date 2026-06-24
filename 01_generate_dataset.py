# building a fake but realistic support ticket dataset since I couldn't get
# real company data for this. trying to mimic patterns from my actual job

import pandas as pd
import numpy as np
import random
from datetime import datetime, timedelta

random.seed(42)
np.random.seed(42)

stores = ["Castle Hill", "Parramatta", "Bondi Junction", "Chatswood", "Liverpool"]

device_categories = ["Desktop", "Laptop", "Register / POS", "Network Equipment", "Mobile Device"]

# avg_minutes and repeat_rate are rough guesses based on what feels realistic
# for a retail support desk, not pulled from anywhere real
issue_catalog = {
    "Password reset / login issue":      {"avg_minutes": 12,  "repeat_rate": 0.35, "device": "Desktop"},
    "Printer connectivity issue":         {"avg_minutes": 25,  "repeat_rate": 0.45, "device": "Network Equipment"},
    "Register freezing / crashing":       {"avg_minutes": 30,  "repeat_rate": 0.40, "device": "Register / POS"},
    "Slow computer / performance issue":  {"avg_minutes": 35,  "repeat_rate": 0.30, "device": "Desktop"},
    "Wifi / network drop out":            {"avg_minutes": 28,  "repeat_rate": 0.42, "device": "Network Equipment"},
    "Software install / update request":  {"avg_minutes": 20,  "repeat_rate": 0.15, "device": "Laptop"},
    "Payment terminal error":             {"avg_minutes": 22,  "repeat_rate": 0.38, "device": "Register / POS"},
    "Screen / hardware fault":            {"avg_minutes": 45,  "repeat_rate": 0.20, "device": "Desktop"},
    "Mobile device setup":                {"avg_minutes": 18,  "repeat_rate": 0.10, "device": "Mobile Device"},
    "Barcode scanner not working":        {"avg_minutes": 15,  "repeat_rate": 0.25, "device": "Register / POS"},
    "Email / account access issue":       {"avg_minutes": 14,  "repeat_rate": 0.20, "device": "Desktop"},
    "New starter device setup":           {"avg_minutes": 40,  "repeat_rate": 0.08, "device": "Laptop"},
}

issue_names = list(issue_catalog.keys())

# some issues just happen way more than others, same as real life
issue_weights = [0.16, 0.14, 0.12, 0.09, 0.11, 0.05, 0.09, 0.04, 0.04, 0.07, 0.05, 0.04]

priorities = ["Low", "Medium", "High"]
priority_weights = [0.35, 0.45, 0.20]

# this dict is the whole point of the project basically - printer/register/wifi
# issues don't have an article yet, everything else does
kb_article_exists = {
    "Password reset / login issue":      True,
    "Printer connectivity issue":        False,
    "Register freezing / crashing":      False,
    "Slow computer / performance issue": True,
    "Wifi / network drop out":           False,
    "Software install / update request": True,
    "Payment terminal error":            True,
    "Screen / hardware fault":           True,
    "Mobile device setup":               True,
    "Barcode scanner not working":       True,
    "Email / account access issue":      True,
    "New starter device setup":          True,
}

n_tickets = 5200
start_date = datetime(2025, 10, 1)
end_date = datetime(2026, 3, 31)
date_range_days = (end_date - start_date).days

rows = []
for i in range(n_tickets):
    issue = np.random.choice(issue_names, p=issue_weights)
    details = issue_catalog[issue]
    has_kb = kb_article_exists[issue]

    store = random.choice(stores)
    device = details["device"]
    priority = np.random.choice(priorities, p=priority_weights)

    # no kb article = takes longer to fix, makes sense since staff are
    # troubleshooting blind instead of following a known fix
    base_minutes = details["avg_minutes"]
    if not has_kb:
        base_minutes = base_minutes * 1.25
    resolution_minutes = max(5, int(np.random.normal(base_minutes, base_minutes * 0.3)))

    # same logic for repeat visits - no article means higher chance it
    # doesn't get fixed properly the first time
    repeat_rate = details["repeat_rate"]
    if not has_kb:
        repeat_rate = min(0.85, repeat_rate * 1.6)
    repeat_visit = np.random.rand() < repeat_rate

    random_day = random.randint(0, date_range_days)
    created_date = start_date + timedelta(days=random_day)
    created_datetime = created_date + timedelta(hours=random.randint(8, 20), minutes=random.randint(0, 59))

    rows.append({
        "ticket_id": f"TCK-{10000 + i}",
        "created_date": created_datetime.strftime("%Y-%m-%d"),
        "created_datetime": created_datetime.strftime("%Y-%m-%d %H:%M"),
        "store_location": store,
        "device_category": device,
        "issue_type": issue,
        "priority": priority,
        "resolution_minutes": resolution_minutes,
        "repeat_visit_needed": repeat_visit,
        "kb_article_existed": has_kb,
    })

df = pd.DataFrame(rows)
df = df.sort_values("created_datetime").reset_index(drop=True)

output_path = "/home/claude/portfolio_project/data/support_tickets.csv"
df.to_csv(output_path, index=False)

print(f"created {len(df)} tickets")
print(f"date range: {df['created_date'].min()} to {df['created_date'].max()}")
print(df['issue_type'].value_counts())
