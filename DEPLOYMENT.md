# Deploying MoneyBuffer UK on Streamlit Community Cloud

MoneyBuffer UK is ready to run on Streamlit Community Cloud without API keys, secrets, or external data services. The app uses synthetic data by default and creates lightweight demo CSV files if they are missing.

## 1. Push to GitHub

Create a GitHub repository and push the project:

```bash
git init
git add .
git commit -m "Prepare MoneyBuffer UK Streamlit MVP"
git branch -M main
git remote add origin https://github.com/YOUR-USERNAME/moneybuffer-uk.git
git push -u origin main
```

If the repository already exists, commit the latest changes and push to the default branch used by Streamlit Community Cloud.

## 2. Create the Streamlit App

1. Go to [Streamlit Community Cloud](https://share.streamlit.io/).
2. Select **New app**.
3. Choose the GitHub repository and branch.
4. Set the main file path to:

```text
app/streamlit_app.py
```

5. Deploy the app.

## 3. Verify the App Loads

After deployment, open the Streamlit app URL and check:

- the sidebar displays the MoneyBuffer UK disclaimer
- the demo household selector works
- the four tabs load: Financial Health Check, Bill Shock Simulator, Scam Checker, and Action Plan
- the Scam Checker runs without needing any API key
- the Action Plan report download works

## 4. Data and Secrets

No secrets are required. The MVP uses synthetic data only.

If `data/synthetic/households.csv` or `data/synthetic/scam_messages.csv` is missing, the app generates deterministic synthetic demo data at startup. These files are fictional and do not contain real personal data.

