from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routers import enterprise
from .routers import brand
from .routers import legal_entity
from .routers import business_unit
from .routers import geography
from .routers import dashboard
from .db import engine
from . import models, models_legal, models_geography

app = FastAPI(title='EOM Service')

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

models.Base.metadata.create_all(bind=engine)
models_legal.Base.metadata.create_all(bind=engine)
models_geography.Base.metadata.create_all(bind=engine)

app.include_router(enterprise)
app.include_router(brand)
app.include_router(legal_entity)
app.include_router(business_unit)
app.include_router(geography)
app.include_router(dashboard)

@app.get('/')
def root():
    return {'service': 'eom', 'status': 'ok'}
