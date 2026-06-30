"""
Robinhood (HOOD) Revenue-Mix & Margin Analysis
================================================
A short empirical analysis of Robinhood's quarterly financials, testing whether
reported revenue growth masks a deterioration in revenue *quality*.

Data: Robinhood 10-Q / 8-K filings (SEC EDGAR, CIK 1783879), Q1 2025 - Q1 2026.
Every figure below is taken directly from a filing; see notes for the event-contract revenue.
All figures in $ millions unless noted.

Author: Giovanni Adelchi Colalillo
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import statsmodels.api as sm

# ---------------------------------------------------------------------------
# 1. DATA  (five verified quarters, sourced from 8-K Ex 99.1 statements of ops)
# ---------------------------------------------------------------------------
# NOote on event contracts: 
# Robinhood did not disclose event-contract revenue
# independently until Q1 2026. In Q2-Q3 2025 it was volume-only; in Q4 2025
# it was bundled into "other transaction revenue." Clean revenue only
# at the two endpoints ($3mm in Q1'25, $104mm in Q1'26) and I have used NaN for the
# quarters where it isn't separately disclosed. 

data = {
    "quarter":      ["Q1-25", "Q2-25", "Q3-25", "Q4-25", "Q1-26"],
    "quarter_num":  [1, 2, 3, 4, 5],
    "total_rev":    [927, 989, 1274, 1283, 1067],
    "crypto_rev":   [252, 160, 268, 221, 134],
    "event_rev":    [3, np.nan, np.nan, np.nan, 104],
    "net_interest": [290, 357, 456, 411, 359],
    "net_income":   [336, 386, 556, 605, 346],
    "total_opex":   [557, 550, 639, 633, 656],
}
df = pd.DataFrame(data)

# ---------------------------------------------------------------------------
# 2. DERIVED METRICS
# ---------------------------------------------------------------------------
df["crypto_pct"] = df["crypto_rev"] / df["total_rev"]
df["nii_pct"]     = df["net_interest"] / df["total_rev"]
df["net_margin"]  = df["net_income"] / df["total_rev"]
df["opex_ratio"]  = df["total_opex"] / df["total_rev"]

# Year-over-year (Q1-26 vs Q1-25): both endpoints are clean for every line.
yoy = lambda col: df[col].iloc[-1] / df[col].iloc[0] - 1

print("=" * 60)
print("YEAR-OVER-YEAR (Q1-26 vs Q1-25)")
print("=" * 60)
print(f"Total revenue:   {yoy('total_rev'):+.1%}")
print(f"Crypto revenue:  {yoy('crypto_rev'):+.1%}   <- structural decline")
print(f"Event contracts: {yoy('event_rev'):+.0%}    <- off a ~zero base")
print(f"Net interest:    {yoy('net_interest'):+.1%}   <- durable, grew")
print(f"Net margin:      {df['net_margin'].iloc[0]:.1%} -> {df['net_margin'].iloc[-1]:.1%}")
print()

# ---------------------------------------------------------------------------
# 3. THE MIX-ILLUSION TEST
# ---------------------------------------------------------------------------
# Mix illusion is when total revenue grows mainly because
# a new, fast-growing line is large enough to offset a decline in an older
# one, not broad-based strength. The test recomputes growth with
# the new line removed and compare it to total growth. If core
# growth is much weaker, the headline number is doing more work than the
# underlying business supports.
#
core_q1_25 = df["total_rev"].iloc[0] - df["event_rev"].iloc[0]
core_q1_26 = df["total_rev"].iloc[-1] - df["event_rev"].iloc[-1]
core_growth = core_q1_26 / core_q1_25 - 1

print("=" * 60)
print("MIX-ILLUSION TEST (Q1-25 -> Q1-26)")
print("=" * 60)
print(f"Total revenue growth:    {yoy('total_rev'):+.1%}")
print(f"Core ex-event-contracts: {core_growth:+.1%}")
print("Headline growth is carried by a line that barely existed a year ago;")
print("the core business grew far more slowly as crypto fell ~47%.")
print()

# ---------------------------------------------------------------------------
# 4. MARGIN TREND REGRESSION
# ---------------------------------------------------------------------------
# OLS regresses net margin on a simple time index; the
# slope tells us the average change each quarter.

X = sm.add_constant(df["quarter_num"])
y = df["net_margin"]
model = sm.OLS(y, X).fit()

print("=" * 60)
print("MARGIN TREND REGRESSION (net_margin ~ time)")
print("=" * 60)
print(f"Slope: {model.params['quarter_num']*100:+.2f} pp/quarter   "
      f"R^2: {model.rsquared:.3f}   n={len(df)}")
print("Margin path:", [f"{m:.0%}" for m in df["net_margin"]])
print("Non-monotonic (Q4 seasonal peak), so the flat slope is expected;")
print("the real signal is the YoY drop, not a linear trend.")
print()

# ---------------------------------------------------------------------------
# 5. VISUALIZATION
# ---------------------------------------------------------------------------
fig, axes = plt.subplots(1, 2, figsize=(12, 4.5))

axes[0].plot(df["quarter"], df["crypto_pct"], marker="o", label="Crypto")
axes[0].plot(df["quarter"], df["nii_pct"], marker="^", label="Net interest")
axes[0].set_title("Revenue mix: crypto declining, net interest stable")
axes[0].set_ylabel("Share of total revenue")
axes[0].legend(); axes[0].grid(alpha=0.3)

axes[1].plot(df["quarter"], df["net_margin"], marker="o", color="crimson", label="Net margin")
axes[1].plot(df["quarter"], model.predict(X), linestyle="--", color="grey", label="OLS trend (flat)")
axes[1].set_title("Net margin is volatile, not a clean downtrend")
axes[1].set_ylabel("Net income / revenue")
axes[1].legend(); axes[1].grid(alpha=0.3)

plt.tight_layout()
plt.savefig("hood_analysis.png", dpi=130, bbox_inches="tight")
print("Saved chart -> hood_analysis.png")

df.to_csv("hood_metrics.csv", index=False)
print("Saved table -> hood_metrics.csv")
