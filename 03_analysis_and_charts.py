# digging deeper than the SQL queries here - charts + the hours/cost estimate
# for the writeup

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker

df = pd.read_csv("/home/claude/portfolio_project/data/support_tickets.csv")
df["created_date"] = pd.to_datetime(df["created_date"])

OUTPUT_DIR = "/home/claude/portfolio_project/output"

# kb article vs no kb article, the main comparison
kb_summary = df.groupby("kb_article_existed").agg(
    ticket_count=("ticket_id", "count"),
    avg_resolution_minutes=("resolution_minutes", "mean"),
    repeat_visit_rate=("repeat_visit_needed", "mean"),
).reset_index()
kb_summary["kb_status"] = kb_summary["kb_article_existed"].map(
    {True: "Has knowledge base article", False: "No knowledge base article"}
)
print(kb_summary[["kb_status", "ticket_count", "avg_resolution_minutes", "repeat_visit_rate"]])

# the 3 problem issues
target_issues = ["Printer connectivity issue", "Register freezing / crashing", "Wifi / network drop out"]
target_df = df[df["issue_type"].isin(target_issues)].copy()

# rough estimate - assuming a repeat visit costs about the same time as the
# original visit. not measured, just a reasonable planning assumption
target_df["total_minutes"] = target_df["resolution_minutes"] * (1 + target_df["repeat_visit_needed"].astype(int))
hours_lost_per_issue = target_df.groupby("issue_type")["total_minutes"].sum() / 60
total_hours_lost = hours_lost_per_issue.sum()

print(hours_lost_per_issue.round(1))
print(f"total hours over 6 months: {total_hours_lost:.0f}")
print(f"per week across 5 stores: {total_hours_lost/26:.1f}")

# what if these 3 issues had a kb article and dropped to the same repeat rate
# as issues that already have one (27.8%)?
target_avg_repeat_rate = target_df["repeat_visit_needed"].mean()
improved_repeat_rate = 0.278

current_repeat_visits = target_df["repeat_visit_needed"].sum()
potential_repeat_visits = len(target_df) * improved_repeat_rate
visits_saved = current_repeat_visits - potential_repeat_visits
avg_minutes_per_target_ticket = target_df["resolution_minutes"].mean()
hours_saved_estimate = (visits_saved * avg_minutes_per_target_ticket) / 60

print(f"current rate: {target_avg_repeat_rate*100:.1f}%, target rate: {improved_repeat_rate*100:.1f}%")
print(f"visits avoided: {visits_saved:.0f}, hours saved: {hours_saved_estimate:.0f} ({hours_saved_estimate/26:.1f}/week)")

# chart 1 - repeat rate by issue, sorted, red = no article
issue_summary = df.groupby(["issue_type", "kb_article_existed"]).agg(
    ticket_count=("ticket_id", "count"),
    repeat_visit_rate=("repeat_visit_needed", "mean"),
).reset_index().sort_values("repeat_visit_rate", ascending=True)

colors = issue_summary["kb_article_existed"].map({True: "#4C72B0", False: "#C44E52"})

fig, ax = plt.subplots(figsize=(9, 6))
bars = ax.barh(issue_summary["issue_type"], issue_summary["repeat_visit_rate"] * 100, color=colors)
ax.set_xlabel("Repeat visit rate (%)")
ax.set_title("Repeat visit rate by issue type\nRed = no knowledge base article available", fontsize=12)
ax.xaxis.set_major_formatter(mticker.PercentFormatter())
for bar, value in zip(bars, issue_summary["repeat_visit_rate"] * 100):
    ax.text(value + 1, bar.get_y() + bar.get_height()/2, f"{value:.0f}%", va="center", fontsize=9)
plt.tight_layout()
plt.savefig(f"{OUTPUT_DIR}/chart_repeat_rate_by_issue.png", dpi=150)
plt.close()

# chart 2 - monthly trend for the 3 problem issues
monthly = target_df.copy()
monthly["month"] = monthly["created_date"].dt.to_period("M").astype(str)
monthly_trend = monthly.groupby(["month", "issue_type"])["repeat_visit_needed"].mean().reset_index()
monthly_trend["repeat_visit_needed"] = monthly_trend["repeat_visit_needed"] * 100

fig, ax = plt.subplots(figsize=(9, 5.5))
for issue in target_issues:
    subset = monthly_trend[monthly_trend["issue_type"] == issue]
    ax.plot(subset["month"], subset["repeat_visit_needed"], marker="o", label=issue)
ax.set_ylabel("Repeat visit rate (%)")
ax.set_title("Repeat visit rate over time, for the three issues\nwithout a knowledge base article", fontsize=12)
ax.legend(fontsize=9, loc="lower right")
ax.yaxis.set_major_formatter(mticker.PercentFormatter())
plt.xticks(rotation=30)
plt.tight_layout()
plt.savefig(f"{OUTPUT_DIR}/chart_monthly_trend.png", dpi=150)
plt.close()

issue_summary.to_csv(f"{OUTPUT_DIR}/summary_by_issue.csv", index=False)
kb_summary.to_csv(f"{OUTPUT_DIR}/summary_by_kb_status.csv", index=False)
monthly_trend.to_csv(f"{OUTPUT_DIR}/summary_monthly_trend.csv", index=False)

print("charts and summary csvs saved")
