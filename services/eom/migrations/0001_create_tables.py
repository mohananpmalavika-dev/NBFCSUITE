"""
Simple dev migration: create initial tables for EOM service.
Run with:
    python -m services.eom.migrations.0001_create_tables
This is intentionally simple for dev use; for production use Alembic.
"""
from services.eom.app.db import engine
from services.eom.app import models


def upgrade():
    models.Base.metadata.create_all(bind=engine)
    print('created tables')


if __name__ == '__main__':
    upgrade()
