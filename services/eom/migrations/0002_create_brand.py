"""
Dev migration: create brand table by running models.Base.metadata.create_all
"""
from services.eom.app.db import engine
from services.eom.app import models


def upgrade():
    models.Base.metadata.create_all(bind=engine)
    print('created/ensured tables including brand')


if __name__ == '__main__':
    upgrade()
