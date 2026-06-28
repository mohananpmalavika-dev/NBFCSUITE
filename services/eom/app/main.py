from fastapi import FastAPI
from .routers import enterprise

app = FastAPI(title='EOM Service')

app.include_router(enterprise.router)

@app.get('/')
def root():
    return {'service': 'eom', 'status': 'ok'}
