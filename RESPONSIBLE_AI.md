# Responsible AI Statement — MoneyBuffer UK

**Version:** 0.1.0 | **Status:** MVP prototype | **Last reviewed:** May 2026

---

## 1. Project Purpose

MoneyBuffer UK is a public-interest educational fintech prototype. It uses synthetic data and transparent scoring rules to help users explore household financial resilience, simulate bill and income shocks, identify possible scam-risk indicators, and learn about free UK support resources.

The project is designed to demonstrate explainable, responsible data science in a consumer finance context. It is not a commercial product and does not provide regulated financial advice.

---

## 2. Intended Uses

MoneyBuffer UK is designed for the following uses only:

- Exploring how synthetic UK household profiles respond to financial pressure.
- Understanding the estimated effect of income drops, rent increases, energy bill rises, and unexpected expenses on a household's financial position.
- Identifying possible scam-risk red flags in a message, using transparent rule-based indicators.
- Learning about free UK support services relevant to financial difficulty or suspected fraud.
- Demonstrating transparent, explainable fintech data science to technical reviewers, researchers, and students.

---

## 3. Prohibited Uses

MoneyBuffer UK must not be used for any of the following purposes:

| Prohibited use | Why it is out of scope |
|---|---|
| Lending decisions | The app is not a credit-risk model and produces no regulated credit assessments |
| Credit eligibility decisions | Outputs are educational illustrations, not credit scores |
| Insurance pricing or underwriting | The scoring model is not calibrated for actuarial use |
| Employment screening | Financial resilience scores must not be used to assess job applicants |
| Automated financial advice | The app does not produce personalised regulated advice |
| Real fraud investigation | The scam checker is illustrative and not a forensic tool |
| Replacing professional debt advice | Users in financial difficulty should contact a qualified adviser |
| Replacing bank or police fraud reporting | Actual suspected fraud must be reported through official channels |

---

## 4. Data Policy

**MVP default:** The app uses synthetic, fictional household profiles by default. No real customer data, bank records, or personal financial information is included in the codebase.

**User input:** The app accepts manual input of income and spending figures for illustrative simulation. Users should treat these as illustrative budget estimates only.

**Sensitive data:** Users should not enter real bank account details, National Insurance numbers, passwords, bank credentials, or any other sensitive personal or financial identifiers into this app.

**Storage:** The app does not store, transmit, log, or share any user-entered data. No authentication, database connection, or external API call is made. All computation runs locally in the user's browser session via Streamlit.

**Synthetic data reproducibility:** The synthetic household dataset is generated deterministically using a fixed random seed and is intended for educational and demonstration purposes only.

---

## 5. Fairness Risks

The current MVP scoring model may systematically underestimate resilience or misrepresent the financial position of certain groups. These are known limitations of the MVP design, not intentional design choices.

### Renters

The essential spending ratio penalises households where housing costs are a high share of income. Renters in high-cost areas may score lower than mortgaged households with similar overall financial pressure, even though their position may be more flexible in some dimensions (no long-term debt, no negative equity risk).

### Low-income households

The emergency runway sub-score benchmarks against six months of essential spending. Lower-income households may face structural barriers to building this buffer. The model does not adjust the benchmark for income level, which may cause low-income households to appear more vulnerable than their actual management strategies suggest.

### Irregular-income workers

The scoring model uses a single monthly income figure. Gig economy workers, self-employed people, and zero-hours contract workers may have highly variable income. A single snapshot figure may overstate or understate their resilience depending on the month captured.

### Disabled people with high essential costs

Households with disability-related essential costs (specialist equipment, care, accessible transport, medical supplies) may have a higher essential spending ratio that the model records as a negative signal, even though these costs are unavoidable and necessary.

### Households with dependants

Caring for children or other dependants typically increases essential spending without a proportional increase in discretionary flexibility. The model does not currently adjust scoring benchmarks for household size or composition.

### Households using credit for rational reasons

Some households use credit cards or overdrafts as a planned cash-flow management tool rather than as a sign of distress. The credit dependency sub-score treats any overdraft or credit card balance as a risk indicator, which may misrepresent households where credit use is deliberate and managed.

---

## 6. Mitigations Currently in Place

The following design choices reduce potential harm from the limitations above:

- **Explainable score drivers:** The app surfaces the top three sub-score drivers in plain English so users can judge whether the explanation reflects their actual circumstances.
- **Synthetic household archetypes:** The six household profiles include an Irregular Income Worker and a Low Savings Renter to illustrate that the model handles a range of situations, not only stable full-time employment.
- **Clear disclaimers:** Every tab in the app includes an explicit disclaimer that outputs are educational and not regulated advice.
- **No lending or credit decision use:** The app explicitly prohibits use in regulated decisions (see Section 3).
- **Educational action plan:** All recommended actions use cautious language ("consider", "you may want to") and signpost free public resources rather than financial products.
- **Support links:** The action plan includes links to MoneyHelper, StepChange, Citizens Advice, National Debtline, Action Fraud, and the FCA ScamSmart checker.
- **No data retention:** The app stores nothing outside the browser session, reducing privacy risk from sensitive input.

---

## 7. Scam Checker Limitations

The scam checker uses a transparent, rule-based approach. Users should be aware of the following limitations:

**False positives:** Keyword rules may flag legitimate messages. For example, a genuine bank notification about a suspended account, a real HMRC refund letter, or a legitimate request to transfer funds between personal accounts may trigger one or more red flags. The risk band output should be treated as a prompt to verify, not as a definitive determination.

**False negatives:** Sophisticated or novel scam messages may not match the current rule set. The checker does not detect context, tone, or social engineering that does not use the specific phrases in the rule library. New scam patterns not present in the rule library will not be detected.

**ML classifier (if present):** An optional TF-IDF logistic regression classifier is included as a proof-of-concept only. It is trained on a small number of synthetic examples and has not been validated against a representative real-world scam corpus. Its probability outputs and category predictions should not be treated as reliable indicators. The classifier is explicitly labelled experimental in the app interface.

**Official channels:** Suspected fraud should always be reported through official channels — Action Fraud (actionfraud.police.uk), the user's bank fraud team, or the FCA ScamSmart checker (fca.org.uk/scamsmart). The MoneyBuffer UK scam checker is not a substitute for these services.

---

## 8. Model Limitations

**Scoring weights are judgement-based:** The resilience score weights (30% emergency runway, 20% essential spending, 20% debt service, 20% surplus, 10% credit dependency) reflect a reasonable MVP design assumption. They have not been validated against real outcome data such as default rates, hardship events, or debt advice referrals. A future calibration exercise using FCA Financial Lives Survey or ONS Wealth and Assets Survey distributions could produce more evidentially grounded weights.

**No real outcome validation:** The model has not been tested against ground-truth financial outcomes. It is not known whether a lower resilience score reliably predicts financial distress, or whether a higher score predicts stability. The model is illustrative only.

**Synthetic data is not a real distribution:** The synthetic household profiles are generated from manually designed archetypes with plausible but not empirically calibrated ranges. The distribution of scores across households reflects the design of the archetypes, not the actual distribution of financial resilience in the UK population.

**Stress scenarios are simplified:** The bill shock simulator applies single-variable shocks to a static monthly snapshot. Real financial stress involves dynamic interactions: savings drawdown over time, changing behaviour, access to credit, family support networks, and benefit entitlements. The model does not capture these dynamics, though a time-based runway depletion chart is available for income drop scenarios.

**Scoring thresholds are not universal:** The 6-month emergency runway benchmark and the essential spending band (45%–90%) are commonly cited heuristics. Their appropriateness varies by household type, income level, employment security, and access to social safety nets.

---

## 9. Future Work

The following improvements are planned to address the limitations described above:

| Area | Planned action |
|---|---|
| Score calibration | Compare synthetic household score distributions to FCA Financial Lives Survey and ONS Wealth and Assets Survey medians by income decile |
| Fairness diagnostics | Add per-archetype score distribution analysis to identify systematic under- or over-scoring by household type |
| Scam checker validation | Build a validation set using publicly available Action Fraud and FCA published example scam messages |
| Score sensitivity analysis | Publish a sensitivity table showing how score changes when each sub-score weight is varied ±10 percentage points |
| User testing | Conduct structured user testing with target groups including renters, irregular-income workers, and people with caring responsibilities |
| Accessibility review | Review the Streamlit interface against WCAG 2.1 AA guidelines |
| Responsible AI review update | Update this document after any significant change to the scoring model, scam rules, or ML classifier |

---

## 10. Contact and Reporting

If you believe the app has produced a harmful, misleading, or discriminatory output, or if you have identified a fairness concern not addressed in this document, please raise it as a GitHub issue in the project repository.

This document will be updated alongside material changes to the scoring model, scam rules, or data pipeline.

---

*MoneyBuffer UK is an educational prototype. It is not a regulated financial service, credit reference agency, fraud detection service, or debt advice provider. Nothing in this app constitutes financial advice, debt advice, investment advice, or a regulated recommendation of any kind.*
