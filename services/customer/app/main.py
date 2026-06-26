from fastapi import FastAPI
from .routers.customer import router as customer_router
from .routers.office import router as office_router
from .routers.branch import router as branch_router
from .db import init_db

app = FastAPI(title="customer-service", version="0.1.0")
app.include_router(customer_router)
app.include_router(office_router)
app.include_router(branch_router)


@app.on_event("startup")
async def startup():
    init_db()


@app.get("/")
async def root():
    return {"service": "customer", "version": "0.1.0"}

@app.get("/health")
async def health():
    return {"status": "ok", "service": "customer"}

@app.get("/ready")
async def ready():
    return {"ready": True}