from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routers import enterprise
from .routers import brand
from .routers import legal_entity
from .routers import business_unit
from .routers import geography
from .routers import branch
from .routers import department
from .routers import dashboard
from .routers import grade
from .routers import sections
from .routers import teams
from .routers import positions
from .routers import designations
from .routers import designation_supporting
from .db import engine
from . import models, models_legal, models_geography, models_enterprise_master, models_branch, models_department, models_grade
from . import models_section, models_team, models_position
from . import models_financial_organization
from . import models_designation
from . import models_designation_supporting



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
models_enterprise_master.Base.metadata.create_all(bind=engine)
models_branch.Base.metadata.create_all(bind=engine)
models_department.Base.metadata.create_all(bind=engine)
models_grade.Base.metadata.create_all(bind=engine)
models_section.Base.metadata.create_all(bind=engine)
models_team.Base.metadata.create_all(bind=engine)
models_position.Base.metadata.create_all(bind=engine)
models_financial_organization.Base.metadata.create_all(bind=engine)
models_designation_supporting.Base.metadata.create_all(bind=engine)

app.include_router(enterprise)




app.include_router(brand)
app.include_router(legal_entity)
app.include_router(business_unit)
app.include_router(geography)
app.include_router(branch)
app.include_router(department)
app.include_router(dashboard)
app.include_router(grade)
app.include_router(sections)
app.include_router(teams)
app.include_router(positions)
app.include_router(designations)
app.include_router(designation_supporting.router)
from .routers_financial_organization import router as finance_router
app.include_router(finance_router)




@app.get('/')
def root():
    return {'service': 'eom', 'status': 'ok'}
