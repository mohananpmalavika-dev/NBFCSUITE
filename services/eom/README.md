EOM service - developer notes

Run migrations (dev):

```powershell
# create tables in configured DB (default sqlite ./eom.sqlite3)
python -m services.eom.migrations.0001_create_tables
```

Run the service locally:

```powershell
# ensure virtualenv activated
$env:DATABASE_URL = 'sqlite:///./eom.sqlite3'
uvicorn services.eom.app.main:app --reload --port 8002
```

Event bus:
- By default events are appended to `var/events.log`.
- To enable HTTP delivery set `EVENT_BUS_URL` to a POST endpoint.

Docker+compose (example):

```yaml
services:
  eom:
    build: .
    command: uvicorn services.eom.app.main:app --host 0.0.0.0 --port 8002
    environment:
      - DATABASE_URL=postgresql://user:pass@db:5432/eom
      - EVENT_BUS_URL=http://event-bus:8080/events
    ports:
      - 8002:8002
```
