# Auth Service

Minimal FastAPI-based authentication & IAM microservice skeleton.

Run locally:

```powershell
cd services\auth
python -m venv .venv
. .venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```
