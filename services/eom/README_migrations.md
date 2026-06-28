Migrations

We provide a simple Alembic scaffold under `services/eom/alembic`.
Set `DATABASE_URL` then run:

```bash
cd services/eom
alembic -c alembic.ini revision --autogenerate -m "add changes"
alembic -c alembic.ini upgrade head
```

If Alembic isn't installed in your venv, install it:

```bash
.venv\Scripts\pip.exe install alembic
```
