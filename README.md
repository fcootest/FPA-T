# FPA-T

FPA-T codebase. Mirror of BigQuery project `fpa-t-494007`.

## Setup

1. Clone:
   ```bash
   git clone https://github.com/fcootest/FPA-T.git
   cd FPA-T
   ```

2. BigQuery auth (service account key lives outside repo):
   ```bash
   export GOOGLE_APPLICATION_CREDENTIALS="/g/My Drive/FPA-T/Documents/GIT-DB & Vault/FPA-T DB key.json"
   gcloud config set project fpa-t-494007
   ```

## Project layout

- `.gitignore` excludes `*key*.json`, `vault.md`, `.env*` — never commit secrets.
