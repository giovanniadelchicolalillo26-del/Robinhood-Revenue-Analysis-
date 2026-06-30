# Robinhood (HOOD) Revenue-Mix & Margin Analysis

A short empirical analysis of Robinhood's quarterly financials, testing whether
reported revenue growth masks a deterioration in revenue *quality*.

## Question

Robinhood reported ~15% year-over-year revenue growth in Q1 2026. This analysis
asks: **is that growth broad-based, or is it carried by one volatile line while
the core business weakens?**

## What is the "mix illusion" test?

A company's total revenue can grow even while its underlying business is
getting weaker, if a new, fast-growing revenue line is large enough to mask a
decline in an older one. We call this a **mix illusion**: the headline growth
number is real, but it reflects a *shift in revenue composition* (mix) rather
than broad-based improvement. The test for it is simple — recompute growth
with the new/volatile line removed, and compare the two growth rates. If
"core" growth (ex the new line) is much weaker than total growth, the headline
number is doing more work than the underlying business actually supports.

Here, the new line is Robinhood's event-contracts (prediction markets)
revenue, which barely existed a year ago. The question we're asking: how much
of Robinhood's reported growth is this one young, fast-growing line carrying,
versus the rest of the business?

## Approach

- Built a small, auditable five-quarter panel from Robinhood's SEC filings
  (10-Q / 8-K, EDGAR CIK 1783879), Q1 2025 – Q1 2026. Every figure traces to
  a specific filing — see the data block in `hood_analysis.py` for sourcing.
- Used `pandas` to compute revenue-mix shares, net margin, and a "core revenue
  ex-event-contracts" series — i.e., total revenue with the event-contracts
  line subtracted out, isolating growth in the rest of the business.
- Ran a simple OLS time trend on net margin with `statsmodels` to check
  whether margin compression is a steady trend or something lumpier.
- Visualized the mix shift and margin path with `matplotlib`.

## Key findings

- **Mix illusion:** total revenue grew +15.1% YoY, but stripping out the
  event-contracts line, core revenue grew only +4.2% — because crypto revenue
  fell 46.8% YoY over the same period.
- **Mix shift:** crypto's share of revenue fell from ~27% to ~13% of total
  while event contracts rose from near-zero to fill the gap; net interest
  (the durable base) stayed in the 31–36% range throughout.
- **Margin:** net margin is *non-monotonic* across the five quarters — it
  rose from 36% to a 47% seasonal peak in Q4 2025, then fell sharply to 32%
  in Q1 2026. The OLS time-trend regression comes back essentially flat
  (slope ≈ 0, R² ≈ 0) — correctly, since a straight line can't capture a
  rise-then-fall pattern. The real compression signal is the YoY comparison
  (36% → 32%), not a linear trend, and the regression is left in deliberately
  to make that limitation explicit rather than cherry-picking a fit.

## Caveats

- `n = 5` quarters — the regression is illustrative of method, not a powerful
  statistical claim.
- Event-contract revenue is only cleanly disclosed at the two endpoints
  ($3mm in Q1 2025, $104mm in Q1 2026). Robinhood did not break it out as its
  own line in Q2–Q3 2025 (volume-only disclosure) or Q4 2025 (bundled into
  "other transaction revenue"); those quarters are left as NaN rather than
  estimated, so the mix-illusion test is run on the two disclosed endpoints.

## Run it

```bash
pip install -r requirements.txt
python hood_analysis.py
```

Outputs `hood_analysis.png` (charts) and `hood_metrics.csv` (enriched table).
