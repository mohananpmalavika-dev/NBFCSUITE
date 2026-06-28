from fastapi import FastAPI
from .routers import enterprise
from .routers import brand

app = FastAPI(title='EOM Service')

app.include_router(enterprise.router)
app.include_router(brand.router)

@app.get('/')
def root():
    return {'service': 'eom', 'status': 'ok'}
