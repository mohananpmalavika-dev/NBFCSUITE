from fastapi import APIRouter, Depends
from sqlalchemy import func, or_
from sqlalchemy.orm import Session

from .. import models, models_geography, models_legal, models_department, models_position
from ..db import SessionLocal

router = APIRouter(prefix="/eom", tags=["eom"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def _count_by_status(db: Session, model):
    rows = db.query(model.status).all()
    summary: dict[str, int] = {}
    for (status,) in rows:
        key = status or "unknown"
        summary[key] = summary.get(key, 0) + 1
    return summary


def _count_rows(db: Session, model):
    return db.query(func.count(model.id)).scalar() or 0


def _workspace_sections():
    return [
        {"label": "Dashboard", "description": "Executive operational view of enterprise structure"},
        {"label": "Enterprise list", "description": "Root enterprise and brand administration"},
        {"label": "Hierarchy explorer", "description": "Tree-based drill-down across organization levels"},
        {"label": "Organization chart", "description": "Reporting, department, position, and employee views"},
        {"label": "Branch network", "description": "Geographic operating footprint and branch coverage"},
        {"label": "Reports", "description": "Standard organization, branch, and finance mappings"},
    ]


@router.get("/dashboard")
def get_eom_dashboard(db: Session = Depends(get_db)):
    enterprises = (
        db.query(models.Enterprise.id, models.Enterprise.code, models.Enterprise.name, models.Enterprise.status)
        .order_by(models.Enterprise.created_at.desc())
        .limit(5)
        .all()
    )
    brands = _count_rows(db, models.Brand)
    legal_entities = _count_rows(db, models_legal.LegalEntity)
    business_units = _count_rows(db, models_legal.BusinessUnit)
    geography_nodes = _count_rows(db, models_geography.GeographyNode)
    positions = _count_rows(db, models_position.Position)

    return {
        "title": "Enterprise Organization Management",
        "summary": {
            "enterprises": _count_rows(db, models.Enterprise),
            "brands": brands,
            "legal_entities": legal_entities,
            "business_units": business_units,
            "geography_nodes": geography_nodes,
            "branches": db.query(func.count(models_geography.GeographyNode.id)).filter(models_geography.GeographyNode.node_type == "branch").scalar() or 0,
            "departments": db.query(func.count(models_department.Department.id)).scalar() or 0,
            "employees": 0,
            "positions": positions,
            "open_approvals": 0,
        },
        "status": {
            "enterprises": _count_by_status(db, models.Enterprise),
            "brands": _count_by_status(db, models.Brand),
            "legal_entities": _count_by_status(db, models_legal.LegalEntity),
            "business_units": _count_by_status(db, models_legal.BusinessUnit),
            "geography": _count_by_status(db, models_geography.GeographyNode),
        },
        "workspace": _workspace_sections(),
        "recent_enterprises": [
            {
                "id": enterprise.id,
                "enterprise_name": enterprise.name,
                "enterprise_code": enterprise.code,
                "status": enterprise.status,
            }
            for enterprise in enterprises
        ],
        "operating_views": [
            "Operational view",
            "Financial view",
            "People view",
            "Risk view",
            "Performance view",
            "Document view",
            "AI insights",
        ],
        "reports": [
            "Branch list",
            "Branch hierarchy",
            "Department list",
            "Cost center report",
            "Profit center report",
            "Position vacancy",
            "Reporting structure",
            "Employee distribution",
            "Branch performance",
            "Organization tree",
        ],
    }


@router.get("/hierarchy")
def get_eom_hierarchy(db: Session = Depends(get_db)):
    enterprises = (
        db.query(models.Enterprise.id, models.Enterprise.code, models.Enterprise.name, models.Enterprise.status)
        .order_by(models.Enterprise.name.asc())
        .all()
    )
    legal_entities = (
        db.query(models_legal.LegalEntity.id, models_legal.LegalEntity.code, models_legal.LegalEntity.name, models_legal.LegalEntity.status)
        .order_by(models_legal.LegalEntity.name.asc())
        .all()
    )
    business_units = (
        db.query(
            models_legal.BusinessUnit.id,
            models_legal.BusinessUnit.legal_entity_id,
            models_legal.BusinessUnit.business_unit_code,
            models_legal.BusinessUnit.business_unit_name,
            models_legal.BusinessUnit.status,
        )
        .order_by(models_legal.BusinessUnit.business_unit_name.asc())
        .all()
    )
    geography = (
        db.query(
            models_geography.GeographyNode.id,
            models_geography.GeographyNode.code,
            models_geography.GeographyNode.name,
            models_geography.GeographyNode.node_type,
            models_geography.GeographyNode.status,
            models_geography.GeographyNode.business_unit_id,
        )
        .order_by(models_geography.GeographyNode.name.asc())
        .all()
    )

    return {
        "items": [
            {
                "id": enterprise.id,
                "code": enterprise.code,
                "name": enterprise.name,
                "type": "enterprise",
                "status": enterprise.status,
                "children": [
                    {
                        "id": legal.id,
                        "code": legal.code,
                        "name": legal.name,
                        "type": "legal_entity",
                        "status": legal.status,
                        "children": [
                            {
                                "id": unit.id,
                                "code": unit.business_unit_code,
                                "name": unit.business_unit_name,
                                "type": "business_unit",
                                "status": unit.status,
                                "children": [
                                    {
                                        "id": node.id,
                                        "code": node.code,
                                        "name": node.name,
                                        "type": node.node_type,
                                        "status": node.status,
                                        "children": [],
                                    }
                                    for node in geography
                                    if node.business_unit_id == unit.id
                                ],
                            }
                            for unit in business_units
                            if unit.legal_entity_id == legal.id
                        ],
                    }
                    for legal in legal_entities
                ],
            }
            for enterprise in enterprises
        ]
    }


@router.get("/search")
def search_eom(q: str, db: Session = Depends(get_db)):
    like = f"%{q}%"
    return {
        "items": [
            *[
                {"id": item.id, "type": "enterprise", "code": item.code, "name": item.name, "status": item.status}
                for item in db.query(models.Enterprise.id, models.Enterprise.code, models.Enterprise.name, models.Enterprise.status)
                .filter(or_(models.Enterprise.name.ilike(like), models.Enterprise.code.ilike(like)))
                .limit(10)
                .all()
            ],
            *[
                {"id": item.id, "type": "brand", "code": item.code, "name": item.name, "status": item.status}
                for item in db.query(models.Brand.id, models.Brand.code, models.Brand.name, models.Brand.status)
                .filter(or_(models.Brand.name.ilike(like), models.Brand.code.ilike(like)))
                .limit(10)
                .all()
            ],
            *[
                {"id": item.id, "type": "legal_entity", "code": item.code, "name": item.name, "status": item.status}
                for item in db.query(models_legal.LegalEntity.id, models_legal.LegalEntity.code, models_legal.LegalEntity.name, models_legal.LegalEntity.status)
                .filter(or_(models_legal.LegalEntity.name.ilike(like), models_legal.LegalEntity.code.ilike(like)))
                .limit(10)
                .all()
            ],
            *[
                {
                    "id": item.id,
                    "type": "business_unit",
                    "code": item.business_unit_code,
                    "name": item.business_unit_name,
                    "status": item.status,
                }
                for item in db.query(
                    models_legal.BusinessUnit.id,
                    models_legal.BusinessUnit.business_unit_code,
                    models_legal.BusinessUnit.business_unit_name,
                    models_legal.BusinessUnit.status,
                )
                .filter(
                    or_(
                        models_legal.BusinessUnit.business_unit_name.ilike(like),
                        models_legal.BusinessUnit.business_unit_code.ilike(like),
                    )
                )
                .limit(10)
                .all()
            ],
            *[
                {"id": item.id, "type": item.node_type, "code": item.code, "name": item.name, "status": item.status}
                for item in db.query(
                    models_geography.GeographyNode.id,
                    models_geography.GeographyNode.node_type,
                    models_geography.GeographyNode.code,
                    models_geography.GeographyNode.name,
                    models_geography.GeographyNode.status,
                )
                .filter(or_(models_geography.GeographyNode.name.ilike(like), models_geography.GeographyNode.code.ilike(like)))
                .limit(10)
                .all()
            ],
        ]
    }


@router.get("/reports")
def get_eom_reports():
    return {
        "items": [
            "Branch list",
            "Branch hierarchy",
            "Department list",
            "Cost center report",
            "Profit center report",
            "Position vacancy",
            "Reporting structure",
            "Employee distribution",
            "Branch performance",
            "Organization tree",
        ]
    }
