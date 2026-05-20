# MoneyBuffer UK Scoring Rationale

## 1. Purpose of the Score

The MoneyBuffer UK financial resilience score is an educational early-warning indicator. It is designed to help users explore household budget pressure, emergency savings, debt commitments, and exposure to financial shocks.

The score is not a credit score, not a lending model, not an affordability assessment, not a benefits assessment, and not regulated financial advice. It should not be used to make lending, eligibility, collections, insurance, investment, debt-solution, or product-recommendation decisions.

The score is intended to support reflection and signposting. It should be interpreted alongside the plain-English explanations, stress-test results, and support resources shown in the app.

## 2. Score Components

The current score uses five explainable components.

### Emergency Runway

Emergency runway estimates how many months of essential spending could be covered by available savings.

```text
emergency_runway_months = savings_balance / essential_spending
```

This component captures short-term shock absorption. A household with a larger liquid savings buffer may be better able to cope with an unexpected bill, income disruption, or temporary increase in costs.

### Essential Spending Burden

Essential spending burden measures the share of monthly income consumed by core costs:

- rent or mortgage
- council tax
- energy
- water
- broadband and phone
- groceries
- transport
- insurance

```text
essential_spending_ratio = essential_spending / monthly_income
```

A higher ratio suggests less flexibility after core costs are paid.

### Debt-Service Burden

Debt-service burden measures debt repayments as a share of monthly income.

```text
debt_service_ratio = debt_repayments / monthly_income
```

This component captures recurring repayment pressure. A high debt-service ratio can reduce flexibility and may increase vulnerability to income or bill shocks.

### Monthly Surplus

Monthly surplus estimates the amount left after essential spending, subscriptions, discretionary spending, and debt repayments.

```text
monthly_surplus =
    monthly_income
    - essential_spending
    - subscriptions
    - discretionary_spending
    - debt_repayments
```

A negative surplus indicates that spending and commitments exceed income in the scenario being assessed.

### Credit Dependency

Credit dependency compares overdraft and credit card balances with monthly income.

```text
credit_dependency_ratio =
    max(0, overdraft_balance + credit_card_balance) / monthly_income
```

This is a supporting risk indicator. It does not identify the full financial position, but it can highlight reliance on short-term or revolving borrowing.

## 3. Scoring Curves

Each component is converted from a raw metric to a 0–100 sub-score using a **piecewise-linear function**. The function is defined by a small set of control points — `(x, y)` pairs sorted by `x` ascending. Between any two adjacent control points the score changes linearly. Values below the first control point clamp to the first `y`; values above the last control point clamp to the last `y`. All outputs are clipped to `[0, 100]`.

### Why piecewise-linear rather than a single linear function

A single linear function (the previous approach) produces an abrupt cliff: every household above the "best" threshold gets exactly 100, and every household below the "worst" threshold gets exactly 0, but the transition between them is a single straight ramp with no graduated signal at either end. A piecewise-linear function uses multiple slopes so that the score can respond more meaningfully in different parts of the distribution — for example, raising emergency savings from zero to one month of runway makes a larger proportional difference than raising it from five to six months, and the curve can reflect that.

Piecewise-linear functions are also easy to explain to a non-technical audience: each household can be shown exactly where it falls on a named segment of the curve (e.g., "between the 3-month and 6-month segment").

### Control points

The breakpoints below are **MVP assumptions, not empirically validated thresholds**. They are based on public guidance from MoneyHelper and StepChange (e.g., a 3–6 month emergency savings target) and common financial rules of thumb. They should be revisited as part of the calibration plan in Section 7.

**Emergency runway score** (higher runway → higher score)

| Runway months | Score |
|---:|---:|
| 0 | 0 |
| 1 | 30 |
| 3 | 70 |
| 6 | 100 |
| > 6 | 100 (clamped) |

**Essential spending ratio score** (lower ratio → higher score)

| Essential spending ratio | Score |
|---:|---:|
| ≤ 0.45 | 100 (clamped) |
| 0.60 | 75 |
| 0.75 | 40 |
| ≥ 0.90 | 0 (clamped) |

**Debt-service ratio score** (lower ratio → higher score)

| Debt-service ratio | Score |
|---:|---:|
| ≤ 0.10 | 100 (clamped) |
| 0.20 | 75 |
| 0.30 | 40 |
| ≥ 0.50 | 0 (clamped) |

**Monthly surplus score** (higher surplus ratio → higher score)

| Surplus as share of income | Score |
|---:|---:|
| ≤ −10% | 0 (clamped) |
| 0% | 40 |
| 10% | 75 |
| ≥ 20% | 100 (clamped) |

**Credit dependency score** (lower ratio → higher score)

| Credit balance as share of income | Score |
|---:|---:|
| 0% | 100 |
| 25% | 70 |
| 50% | 40 |
| ≥ 100% | 0 (clamped) |

## 4. Current Weighting

The current MVP weighting is:

| Component | Weight |
|---|---:|
| Emergency runway score | 30% |
| Essential spending score | 20% |
| Debt-service score | 20% |
| Monthly surplus score | 20% |
| Credit dependency score | 10% |

The weighted score is clipped between 0 and 100 and mapped to a plain-English risk band.

## 5. Rationale for Each Weight

The weights are judgement-based for MVP purposes. They are not yet empirically validated or statistically calibrated against real household outcome data.

Emergency runway receives the highest weight because liquid savings directly affect a household's short-term ability to absorb shocks. If a household has little or no savings buffer, even a relatively small unexpected expense can become difficult to manage.

Debt-service burden, essential spending burden, and monthly surplus receive similar weights because they describe recurring monthly pressure from different angles:

- essential costs show how much income is absorbed before discretionary choices
- debt repayments show recurring repayment pressure
- monthly surplus shows whether the household has cashflow headroom after regular costs

Credit dependency receives a lower weight because it is a supporting risk indicator rather than the full risk state. Credit card and overdraft balances may indicate pressure, but interpretation depends on interest rates, repayment behaviour, available credit limits, household assets, and individual circumstances not captured in the MVP.

## 6. Public Context Sources

The MVP score is not calibrated directly from these sources, but the project is informed by public UK context on household finances, expenditure, financial resilience, and fraud.

- [FCA Financial Lives Survey 2024](https://www.fca.org.uk/financial-lives/financial-lives-2024)

  The FCA Financial Lives Survey provides context on UK adults' financial lives, including vulnerability, financial resilience, credit use, and confidence. Future versions of MoneyBuffer UK could compare synthetic household distributions with relevant FCA summary statistics.

- [MoneyHelper](https://www.moneyhelper.org.uk/)

  MoneyHelper provides public guidance on budgeting, debt, pensions, benefits, money problems, and emergency savings. MoneyBuffer UK uses cautious educational signposting and should align with public-support framing rather than giving personalised advice.

- [ONS household expenditure and family spending data](https://www.ons.gov.uk/)

  ONS household expenditure and inflation data can help benchmark synthetic spending distributions, such as housing, food, transport, utilities, and other regular household costs.

- [Bank of England statistics](https://www.bankofengland.co.uk/statistics)

  Bank of England statistics provide macroeconomic and financial context, including interest rates, lending, deposits, and household credit conditions. These sources can inform scenario assumptions such as mortgage-payment stress or credit-pressure context.

- [UK Finance Annual Fraud Report 2025](https://www.ukfinance.org.uk/policy-and-guidance/reports-and-publications/annual-fraud-report-2025)

  UK Finance fraud reporting provides context on fraud typologies, payment scams, and consumer harm. This is especially relevant to the scam-risk checker and future fraud-awareness features.

## 7. Known Limitations

The current model has important limitations:

- The model is not trained on real household outcome data.
- Synthetic data is used for demonstration.
- Weights are not yet statistically calibrated.
- Household circumstances differ widely.
- The model does not include regional cost differences, household assets beyond savings, benefit entitlement, arrears, interest rates, credit limits, childcare costs, disability-related costs, informal support, or other important personal circumstances.
- The score can be sensitive to self-entered values.
- The score should not be used for lending, eligibility, collections, insurance, financial-advice, debt-advice, or product-recommendation decisions.
- A high score does not guarantee financial security.
- A low score does not mean a household has no options or support routes.

The score should be treated as a simplified educational signal, not a definitive assessment.

## 8. Future Calibration Plan

Future versions should improve the methodology before any wider use:

1. Compare synthetic distributions against FCA and ONS summary statistics.
2. Add percentile rank by household archetype so users can compare scenarios within similar synthetic groups.
3. ~~Replace hard thresholds with smoother scoring curves where appropriate.~~ **Done** — piecewise-linear scoring curves are now used for all five sub-scores (see Section 3). Breakpoints remain MVP assumptions and should be calibrated against public data.
4. Validate against labelled financial-distress, arrears, or hardship datasets if suitable data becomes available and can be used lawfully and ethically.
5. Conduct sensitivity analysis on weights to identify which assumptions most affect outcomes.
6. Review whether additional features should be included, such as regional housing costs, arrears, variable-rate exposure, benefit income, childcare costs, and priority debts.
7. Publish a versioned methodology note whenever the scoring approach changes.

Any future calibration should include privacy, fairness, explainability, and regulatory review before being used with real user data or in higher-stakes contexts.

