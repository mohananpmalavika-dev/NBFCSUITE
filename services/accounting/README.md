# Accounting Service

FastAPI microservice for accounting workflows: GL accounts, journal entries, and bank reconciliation.

Run locally:

```powershell
cd services\accounting
python -m venv .venv
. .venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

When running with `docker-compose.yml`, the service is available on `http://localhost:8008`.
