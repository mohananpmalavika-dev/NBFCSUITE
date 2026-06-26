# CRM Service

FastAPI microservice for CRM workflows: leads, campaigns, and opportunity management.

Run locally:

```powershell
cd services\crm
python -m venv .venv
. .venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

When running with `docker-compose.yml`, the service is available on `http://localhost:8009`.
