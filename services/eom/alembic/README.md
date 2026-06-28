Alembic scaffolding for EOM service.

To create a revision (requires alembic installed in your venv):

```bash
cd services/eom
alembic -c alembic.ini revision --autogenerate -m "initial"
alembic -c alembic.ini upgrade head
```

The `env.py` reads `DATABASE_URL` from environment.
