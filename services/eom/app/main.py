from fastapi import FastAPI
from .routers import enterprise
from .routers import brand
from .routers import legal_entity
from .routers import business_unit
from .db import engine
from . import models, models_legal

app = FastAPI(title='EOM Service')

models.Base.metadata.create_all(bind=engine)
models_legal.Base.metadata.create_all(bind=engine)

app.include_router(enterprise.router)
app.include_router(brand.router)
app.include_router(legal_entity.router)
app.include_router(business_unit.router)

@app.get('/')
def root():
    return {'service': 'eom', 'status': 'ok'}
