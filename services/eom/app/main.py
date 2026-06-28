from fastapi import FastAPI
from .routers import enterprise
from .routers import brand
from .routers import legal_entity

app = FastAPI(title='EOM Service')

app.include_router(enterprise.router)
app.include_router(brand.router)
app.include_router(legal_entity.router)

@app.get('/')
def root():
    return {'service': 'eom', 'status': 'ok'}
