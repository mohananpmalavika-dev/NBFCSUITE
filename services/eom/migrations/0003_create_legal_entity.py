"""
Dev migration: create legal_entity table
"""
from ..app import db
from ..app import models_legal


def upgrade():
    engine = db._build_engine(db_url=None)
    models_legal.Base.metadata.create_all(bind=engine)


if __name__ == '__main__':
    upgrade()
