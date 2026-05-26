# MoneyBuffer UK Technical README

**Author:** Muhammad Shoaib Safridi  
**Contact:** [safridi@gmail.com](mailto:safridi@gmail.com)  
**GitHub:** [drmshoaib](https://github.com/drmshoaib)<br>
**Live app:** [moneybuffer-uk.streamlit.app](https://moneybuffer-uk.streamlit.app/)

## 1. Technical Summary

MoneyBuffer UK is a Python and Streamlit public-interest fintech prototype. It helps users explore household financial resilience, stress-test budget shocks, check transparent scam-risk indicators, and generate cautious educational action prompts.

The project is designed as an explainable MVP rather than a black-box model. The core logic uses deterministic scoring functions, synthetic data generation, transparent scam rules, and unit-tested scenario simulation. The app does not use real customer data, open-banking integrations, paid APIs, or secrets.

## 2. Technology Stack

| Area | Tools Used | Purpose |
|---|---|---|
| Language | Python 3.11+ | Core data science, scoring, rules, tests, and app logic |
| Web app | Streamlit | Interactive MVP frontend |
| Data processing | pandas, numpy | Household data generation, feature engineering, scenario outputs |
| Visualisation | Plotly | Interactive charts for spending, stress tests, and runway projection |
| Machine learning | scikit-learn | Optional TF-IDF + Logistic Regression scam classifier proof of concept |
| Reporting | fpdf2 | Lightweight educational PDF report generation |
| Testing | pytest | Unit and integration tests |
| Linting/formatting | Ruff | Fast Python linting and formatting |
| Type checking | mypy | Static checks for core source and tests |
| Packaging | pyproject.toml, src layout | Clean import structure and editable installs |
| CI | GitHub Actions | Automated lint, type-check, and test workflow |
| Deployment | Streamlit Community Cloud | Simple app deployment without secrets |

## 3. Project Structure

```text
MoneyBuffer/
|-- app/
|   `-- streamlit_app.py
|-- src/
|   `-- moneybuffer/
|       |-- data_generation/
|       |-- resilience/
|       |-- stress_testing/
|       |-- scams/
|       |-- recommendations/
|       |-- reporting/
|       |-- ui/
|       `-- validation/
|-- tests/
|-- docs/
|-- screenshots/
|-- scripts/
|-- .github/workflows/
|-- pyproject.toml
|-- requirements.txt
|-- README.md
`-- DEPLOYMENT.md
```

The code uses a `src/` layout, which avoids accidental imports from the project root and more closely matches production packaging practices.

## 4. Application Architecture

The Streamlit app is a thin interface over reusable Python modules:

1. Synthetic household profiles are loaded or generated.
2. Household inputs are validated.
3. Resilience features are calculated.
4. A 0-100 resilience score and risk band are assigned.
5. Stress scenarios can be applied to produce baseline-vs-stressed comparisons.
6. Scam messages are checked using transparent rule-based logic.
7. Optional ML scam probability can be shown as a caveated proof of concept.
8. The action-plan engine produces cautious educational prompts and UK support links.
9. A simple report can be exported.

This separation keeps business logic testable outside Streamlit.

## 5. Core Modules

### `data_generation`

Generates fictional UK-style household profiles and synthetic scam examples.

Key files:

- `households.py`
- `transactions.py`
- `scam_messages.py`

Household archetypes include:

- Stable Household
- Payday Pressure
- High Debt Burden
- Irregular Income Worker
- Low Savings Renter
- Mortgage Rate Shock Household

The synthetic data is for demonstration only and contains no real personal data.

### `resilience`

Implements the financial resilience scoring engine.

Key files:

- `features.py`
- `score.py`
- `bands.py`
- `explanations.py`

Derived metrics include:

- essential spending
- essential spending ratio
- debt service ratio
- monthly surplus
- emergency runway months
- credit dependency ratio
- fixed cost burden

The score is a weighted 0-100 blend:

```text
30% emergency runway
20% essential spending burden
20% debt-service burden
20% monthly surplus
10% credit dependency
```

Scores are clipped to `[0, 100]`, and risk bands are:

- Stable: 75-100
- Watch: 55-74
- Vulnerable: 35-54
- Critical: 0-34

The scoring rationale is documented in `docs/scoring_rationale.md`.

### `stress_testing`

Applies educational stress scenarios to household profiles.

Key files:

- `income_shocks.py`
- `bill_shocks.py`
- `scenario_engine.py`

Supported scenarios include:

- income drops of 20%, 40%, or 100%
- income shock durations of 1, 3, 6, or 12 months
- rent or mortgage increases
- energy bill increases
- unexpected expenses up to GBP 3,000
- debt or mortgage payment increases
- compound scenarios combining multiple shocks

The simulator also models a simple savings drawdown trajectory and estimates when savings may be depleted within a selected horizon.

### `scams`

Implements scam-risk detection.

Key files:

- `rules.py`
- `classifier.py`
- `explanations.py`
- `ml_model.py`

The primary scam checker is rule-based and transparent. It detects red flags such as:

- urgency language
- secrecy requests
- risky payment methods
- suspicious links
- impersonation cues
- invoice redirection
- romance scam indicators
- pig-butchering crypto scam indicators
- fake job or task scam indicators

The optional ML classifier uses:

- TF-IDF features
- Logistic Regression
- synthetic labels only

The ML classifier is deliberately de-emphasised in the app because it is not trained on a large or representative real-world scam corpus.

### `recommendations`

Generates cautious, educational action prompts and support-resource signposting.

Key files:

- `action_engine.py`
- `support_links.py`

The module avoids regulated financial advice wording. It uses phrases such as:

- "consider"
- "you may want to"
- "it may be sensible to"
- "official support resources include"

Support links include MoneyHelper, StepChange, Citizens Advice, National Debtline, Action Fraud, FCA ScamSmart, and the FCA Financial Services Register.

### `reporting`

Creates a lightweight educational PDF report using `fpdf2`.

Key file:

- `pdf_report.py`

The report includes the score, risk band, key metrics, action prompts, support links, and scam-risk snapshot where available.

### `validation`

Provides input validation warnings for unrealistic or edge-case household values.

Key file:

- `input_validation.py`

Validation is non-blocking: it highlights potential data quality issues without preventing the user from exploring scenarios.

## 6. Frontend Design

The frontend is built in Streamlit with a custom theme layer.

Key frontend features:

- sidebar disclaimer and household selector
- manual input controls
- four-tab app layout
- Plotly charts
- custom HTML/CSS cards
- risk gauge
- support-link cards
- scam red-flag display
- text and PDF report download

The theme helpers live in:

```text
src/moneybuffer/ui/theme.py
```

The design goal is serious, public-interest, and recruiter-demo friendly rather than playful or sales-heavy.

## 7. Testing Strategy

The project includes unit and integration tests under `tests/`.

Coverage areas include:

- synthetic household generation
- transaction generation
- resilience feature calculation
- score and risk band assignment
- division-by-zero handling
- stress scenario engine
- compound shock behaviour
- scam rule detection
- optional ML training and prediction
- action-plan generation
- support-link selection
- PDF report generation
- end-to-end pipeline behaviour

Core commands:

```bash
ruff check .
ruff format --check .
mypy src
pytest
```

For stricter local checking:

```bash
python -m mypy src tests
python -m pytest -q
```

## 8. Deployment

The app is prepared for Streamlit Community Cloud.

Deployment settings:

```text
Main file path: app/streamlit_app.py
```

The app:

- uses synthetic data by default
- creates demo CSV files at startup if missing
- requires no API keys
- requires no external database
- requires no secrets

Runtime dependencies are kept in `requirements.txt` for simple Streamlit deployment. Development dependencies are kept in `pyproject.toml` under the optional `dev` dependency group.

## 9. CI/CD

GitHub Actions workflow:

```text
.github/workflows/test.yml
```

The workflow runs:

1. Python 3.11 setup
2. editable install with dev dependencies
3. Ruff linting
4. Ruff format check
5. mypy type checking
6. pytest test suite

This provides a lightweight quality gate for pull requests and future changes.

## 10. Responsible AI and Safety

MoneyBuffer UK is intentionally conservative.

It is:

- not financial advice
- not debt advice
- not investment advice
- not a credit decisioning system
- not a lending tool
- not a guaranteed scam detector

The project favours explainable rules, visible assumptions, cautious language, and synthetic data. The responsible AI notes are documented in:

```text
RESPONSIBLE_AI.md
docs/scoring_rationale.md
docs/synthetic_data_benchmark.md
```

## 11. Engineering Decisions

Important engineering choices:

- `src/` layout for clean imports.
- Deterministic synthetic data generation with seeds.
- Transparent scoring rather than hidden model outputs.
- Rule-based scam checker as the primary result.
- ML classifier retained only as a clearly caveated proof of concept.
- Runtime-only `requirements.txt` for deployment simplicity.
- Optional dev dependencies in `pyproject.toml`.
- Tests written around edge cases such as zero income and negative surplus.
- No secrets or external APIs.
- Public-support links are structured data rather than hard-coded UI text.

## 12. Recruiter-Relevant Skills Demonstrated

This project demonstrates:

- Python package organisation
- data generation and feature engineering
- explainable risk scoring
- transparent rule-based classification
- lightweight ML model training
- Streamlit product prototyping
- Plotly dashboard visualisation
- PDF report generation
- defensive input validation
- type hints and typed dictionaries
- pytest testing
- mypy type checking
- Ruff linting and formatting
- GitHub Actions CI
- deployment preparation for Streamlit Community Cloud
- responsible AI and regulated-domain caution

## 13. Future Technical Roadmap

Potential next steps:

- CSV upload flow for local household budget data
- FastAPI backend exposing scoring and scenario endpoints
- React Native / Expo mobile frontend
- PostgreSQL or Firestore persistence
- more realistic synthetic data calibration
- percentile ranks by household archetype
- richer scam typology and labelled evaluation data
- improved model governance and fairness review
- downloadable scenario comparison reports
- responsible AI review before any real user-data collection
