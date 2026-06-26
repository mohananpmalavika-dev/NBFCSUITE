# Compliance Service

FastAPI microservice for AML, PEP screening, and audit trails.

Run locally:

```powershell
cd services\compliance
python -m venv .venv
. .venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

When running with `docker-compose.yml`, the service is available on `http://localhost:8011`.
