# Synthetic Data Benchmark Reference — MoneyBuffer UK

This document explains why MoneyBuffer UK uses synthetic household data, what the synthetic dataset currently covers, which public sources should anchor future empirical calibration, and what steps are needed to close the gap between synthetic assumptions and real-world distributions.

## Status

The MVP uses synthetic household profiles and **does not yet claim empirical calibration**. All scoring thresholds, archetype distributions, and stress-test magnitudes are illustrative. They are based on public qualitative guidance (FCA, MoneyHelper, StepChange) and common financial rules of thumb, not on fitted parameters derived from representative survey microdata.

This document serves as the explicit record of that limitation and as a structured plan for future validation.

---

## 1. Why Synthetic Data Is Used

| Reason | Detail |
|---|---|
| **Privacy** | No real household records, bank transactions, or personal financial data are stored, processed, or transmitted. The MVP can be demonstrated publicly without any data-sharing agreements or privacy risk to individuals. |
| **Reproducibility** | All synthetic households are generated from a fixed random seed (`seed=42` by default). Every run of the pipeline produces the same households, scores, and stress-test outputs, making test suites deterministic and results auditable. |
| **Safe public demo** | Streamlit Community Cloud deployment requires no private data files. The app auto-generates its demo dataset at startup, removing deployment risk from misconfigured secrets or inadvertently committed data. |
| **Archetype control** | Synthetic generation gives precise control over the distribution of household types, income ranges, debt levels, and savings positions. This allows stress-test scenarios (income shocks, rent increases, energy bill rises) to be tested against households with known, reproducible characteristics rather than against opaque real-world samples. |

---

## 2. What the Synthetic Dataset Currently Covers

The generator produces households from six UK-style archetypes. Each archetype has its own income range, savings behaviour, debt profile, and spending pattern.

| Archetype | Key Characteristics | Intended Financial Pressure |
|---|---|---|
| **Stable Household** | Higher income, meaningful savings buffer, manageable debt, low credit dependency | Demonstrates the high-resilience end of the scoring range; expected to score Stable (75–100) |
| **Payday Pressure** | Near-minimum income, minimal or zero savings, relies on credit to bridge monthly shortfalls | Models acute month-to-month financial stress; expected Watch to Vulnerable (45–65) |
| **High Debt Burden** | Moderate income but high debt repayments consuming a large share of income, elevated DSR | Tests debt-service ratio sensitivity; expected Vulnerable to Critical (25–55) |
| **Irregular Income Worker** | Highly variable monthly income (gig, freelance, or zero-hours contract), limited savings | Tests income-volatility assumptions; resilience score fluctuates with income draw |
| **Low Savings Renter** | Moderate income but most of it consumed by high rent; emergency runway close to zero | Highlights the housing-cost dimension of financial vulnerability |
| **Mortgage Rate Shock Household** | Owner-occupier household whose mortgage payment has increased materially; moderate savings | Models rate-rise exposure; tests the stress-test simulator against a realistic scenario |

Synthetic households are generated with randomised individual parameters drawn from ranges calibrated per archetype. The generation logic is in [`src/moneybuffer/data_generation/households.py`](../src/moneybuffer/data_generation/households.py).

---

## 3. Public Sources for Future Benchmarking

The following publicly available UK data sources should be used when empirically calibrating archetype distributions, scoring thresholds, and risk weights in future versions.

### FCA Financial Lives Survey 2024
- **Publisher:** Financial Conduct Authority
- **URL:** fca.org.uk/data/financial-lives
- **Relevance:** Nationally representative survey of UK adults covering financial resilience, savings buffers, credit use, debt distress, vulnerability indicators, and scam exposure. The most directly relevant benchmark for this project. Key tables include: emergency savings coverage, credit product usage, over-indebtedness flags, and the FCA's own financial resilience indicator.

### ONS Household Expenditure / Family Spending Survey
- **Publisher:** Office for National Statistics
- **URL:** ons.gov.uk/peoplepopulationandcommunity/personalandhouseholdfinances/expenditure
- **Relevance:** Provides mean and distributional data on essential spending categories (food, energy, housing, transport) as a share of household income. Enables calibration of the essential spending ratio thresholds and identification of archetypes that match real expenditure percentiles.

### Bank of England Statistics
- **Publisher:** Bank of England
- **URL:** bankofengland.co.uk/statistics
- **Relevance:** Publishes debt-to-income ratios, mortgage arrears data, household debt servicing costs, and aggregate household balance sheet statistics. The Mortgage and Consumer Lending data directly informs debt-service ratio assumptions. The Financial Stability Report contains household vulnerability metrics.

### UK Finance Annual Fraud Report
- **Publisher:** UK Finance
- **URL:** ukfinance.org.uk/data-and-research/data/fraud
- **Relevance:** Annual breakdown of fraud and scam losses by type (APP fraud, card fraud, impersonation, investment scams, invoice fraud). Provides category-level frequency data for calibrating the scam type distribution in the synthetic message generator and the red-flag weight assignments in the scam classifier.

### MoneyHelper Guidance
- **Publisher:** Money and Pensions Service (MaPS)
- **URL:** moneyhelper.org.uk
- **Relevance:** MoneyHelper publishes practical guidance on emergency savings targets (3–6 months), recommended debt-to-income ratios, and budgeting benchmarks. These qualitative thresholds inform the MoneyBuffer scoring rules and action-plan triggers and should be explicitly cited when publishing scoring assumptions.

---

## 4. Benchmark Table Template

The table below is a structured template for recording the gap between synthetic assumptions and public benchmarks. It should be completed as part of any future calibration exercise.

Values marked `[TBC]` require extraction from the sources listed in Section 3.

| Metric | Synthetic dataset value | Public benchmark source | Public benchmark value | Gap / comment | Action needed |
|---|---|---|---|---|---|
| **Emergency savings distribution** | ~30% of synthetic households have zero or near-zero savings; runway distribution spans 0–18 months by archetype | FCA Financial Lives Survey 2024 | [TBC — % of UK adults with less than £100 / less than 1 month emergency savings] | Unknown until extracted | Extract FCA table; adjust zero-savings prevalence in archetype generator |
| **Essential spending ratio** | Ranges from ~35% (Stable) to ~75% (Payday Pressure / High Debt) | ONS Family Spending Survey | [TBC — mean essential spending as % of income by income quintile] | Thresholds chosen via rules of thumb; may not match actual quintile distributions | Fit lower/upper bounds per archetype to ONS quintile data |
| **Debt-service burden** | Ranges from ~5% (Stable) to ~35%+ (High Debt); DSR > 40% triggers Critical band | Bank of England household debt statistics | [TBC — median and 75th-percentile DSR for UK households] | 40% DSR cut-off is a common rule of thumb; not derived from BoE data | Validate against BoE aggregate DSR distribution; adjust band boundary if needed |
| **Rent/mortgage share of income** | Housing costs range from ~20% (owner-occupier, low rate) to ~45% (high-rent renter) | ONS Family Spending / CPI housing costs | [TBC — mean housing cost share by tenure type] | Rent share for Low Savings Renter may be underestimated given 2023–24 rental market | Increase rent range ceiling for renter archetypes using ONS / Rightmove rental tracker |
| **Income volatility** | Irregular Income Worker archetype uses ±30–50% monthly income variation | No direct ONS equivalent; FCA Financial Lives has a "variable income" segment | [TBC — % of UK workforce on zero-hours / gig contracts; income SD estimate] | Volatility range is assumed; no empirical SD fitted | Cross-reference HMRC PAYE / LFS data on zero-hours prevalence; calibrate income SD |
| **Financial vulnerability distribution** | ~15–20% of generated households score Critical or Vulnerable by design | FCA Financial Lives 2024 financial resilience indicator | [TBC — % of UK adults classified as financially vulnerable by FCA definition] | Synthetic proportion may not reflect true population prevalence | Compare FCA vulnerability prevalence; adjust archetype sampling weights accordingly |
| **Scam category coverage** | Synthetic messages cover: bank impersonation, investment, invoice, romance, delivery parcel, job offer, and lottery/prize | UK Finance Annual Fraud Report | [TBC — category breakdown of APP fraud and other scam types by volume] | Coverage appears broadly aligned; relative frequency of categories not calibrated | Extract UK Finance category proportions; adjust synthetic message generator weights |

---

## 5. Future Validation Plan

The following steps are needed to move from illustrative synthetic assumptions to empirically grounded benchmarks.

### Step 1 — Compare synthetic summary statistics against public sources
Extract the headline distributional statistics from the FCA Financial Lives Survey, ONS Family Spending Survey, and Bank of England household statistics. For each metric in the benchmark table, record the public value and compute the gap relative to the synthetic dataset. Flag any gaps larger than 10 percentage points as requiring archetype adjustment.

### Step 2 — Adjust archetype distributions
Using the gap analysis from Step 1, update the income ranges, savings distributions, debt levels, and essential spending ratios in [`src/moneybuffer/data_generation/households.py`](../src/moneybuffer/data_generation/households.py). Re-run the full pipeline to confirm that the resulting score and band distributions shift in the expected direction. Document the before/after distributions in this file.

### Step 3 — Perform sensitivity analysis on scoring weights
The current resilience score uses fixed weights (30/20/20/20/10 for runway, essential spending, debt service, surplus, credit dependency). These were chosen judgementally. A sensitivity analysis should vary each weight ±5 percentage points and record the effect on band assignment across archetypes. Weights that produce large band-assignment changes for plausible input ranges warrant empirical justification or explicit disclosure.

### Step 4 — Create household percentile ranks
Once archetype distributions are calibrated against public data, compute a percentile rank for each scored household relative to the synthetic population. Surface this in the app as a plain-English statement: for example, "Your resilience score is in the bottom 20% of UK households in this model." This makes the score more interpretable without implying clinical precision.

### Step 5 — Document fairness by archetype
For each of the six archetypes, document:
- mean and standard deviation of the resilience score
- proportion scoring each band (Stable / Watch / Vulnerable / Critical)
- mean scam-risk score
- whether the action plan generates meaningfully different guidance across archetypes

This creates a per-archetype fairness record consistent with the commitments in [RESPONSIBLE_AI.md](../RESPONSIBLE_AI.md) and provides a reproducible audit trail for future development.

---

## Notes

- This document should be updated whenever archetype parameters, scoring weights, or band thresholds are changed.
- No data scraping or automated data downloads are performed by this project. All public benchmark values must be extracted manually from the cited sources and recorded in the table above.
- The benchmark table is intentionally a template at this stage. Completing it is a prerequisite for any version of the app that claims empirical calibration or that is used in a regulated or advisory context.

---

*MoneyBuffer UK is an educational prototype. See [RESPONSIBLE_AI.md](../RESPONSIBLE_AI.md) for full scope, limitations, and prohibited uses.*
