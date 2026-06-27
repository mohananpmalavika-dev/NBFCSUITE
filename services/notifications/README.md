# Notifications Service

A standalone notification engine for the NBFC Suite.

## Features

- SMS
- WhatsApp
- Email
- Push notifications
- Voice calls
- In-app notifications

## Endpoints

- `GET /` - service metadata
- `GET /health` - health check
- `POST /notifications/send` - send a notification through a channel
- `POST /events` - ingest domain events that trigger notification workflows
- `GET /notifications` - list notifications by tenant
- `GET /notifications/in_app/{user_id}` - list in-app notifications for a user

## Startup

Set `DATABASE_URL` to a PostgreSQL database, then run:

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```
