from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional
from ..db import SessionLocal
from .. import models_geography, models_legal
from ..schemas import GeographyNodeCreate, GeographyNodeResponse, GeographyNodeUpdate, GeographyNodeListResponse, GeographyTreeResponse
from ..auth import require_role
from ..audit import record_audit
from ..events import publish_event

router = APIRouter(prefix="/eom", tags=["eom"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_geography_node(db: Session, id: str):
    node = db.query(models_geography.GeographyNode).filter(models_geography.GeographyNode.id == id).first()
    if not node:
        raise HTTPException(status_code=404, detail='Geography node not found')
    return node


@router.post('/geography', response_model=GeographyNodeResponse, status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_role('enterprise.admin'))])
def create_geography_node(payload: GeographyNodeCreate, db: Session = Depends(get_db)):
    if payload.parent_id:
        parent = db.query(models_geography.GeographyNode).filter(models_geography.GeographyNode.id == payload.parent_id).first()
        if not parent:
            raise HTTPException(status_code=404, detail='Parent geography node not found')
    if payload.business_unit_id:
        bu = db.query(models_legal.BusinessUnit).filter(models_legal.BusinessUnit.id == payload.business_unit_id).first()
        if not bu:
            raise HTTPException(status_code=404, detail='Business unit not found')
    if payload.legal_entity_id:
        legal = db.query(models_legal.LegalEntity).filter(models_legal.LegalEntity.id == payload.legal_entity_id).first()
        if not legal:
            raise HTTPException(status_code=404, detail='Legal entity not found')

    existing = db.query(models_geography.GeographyNode).filter(models_geography.GeographyNode.code == payload.code).first()
    if existing:
        raise HTTPException(status_code=400, detail='Geography code already exists')

    node = models_geography.GeographyNode(
        code=payload.code,
        name=payload.name,
        node_type=payload.node_type,
        parent_id=payload.parent_id,
        status=payload.status or 'active',
        manager=payload.manager,
        latitude=payload.latitude,
        longitude=payload.longitude,
        population=payload.population,
        area_size=payload.area_size,
        description=payload.description,
        business_unit_id=payload.business_unit_id,
        legal_entity_id=payload.legal_entity_id,
    )
    db.add(node)
    db.commit()
    db.refresh(node)
    try:
        record_audit(db, 'geography_node', node.id, 'created', payload.model_dump(exclude_unset=True))
    except Exception:
        pass
    publish_event('GEOGRAPHY_CREATED', {'id': node.id, 'code': node.code, 'name': node.name})
    return node


@router.get('/geography', response_model=GeographyNodeListResponse)
def list_geography_nodes(q: Optional[str] = None, node_type: Optional[str] = None, status: Optional[str] = None, limit: int = 25, offset: int = 0, db: Session = Depends(get_db)):
    query = db.query(models_geography.GeographyNode)
    if q:
        like = f"%{q}%"
        query = query.filter((models_geography.GeographyNode.name.ilike(like)) | (models_geography.GeographyNode.code.ilike(like)))
    if node_type:
        query = query.filter(models_geography.GeographyNode.node_type == node_type)
    if status:
        query = query.filter(models_geography.GeographyNode.status == status)
    total = query.count()
    items = query.order_by(models_geography.GeographyNode.created_at.desc()).limit(limit).offset(offset).all()
    return {'total': total, 'items': items}


@router.get('/geography/tree', response_model=GeographyTreeResponse)
def geography_tree(db: Session = Depends(get_db)):
    nodes = db.query(models_geography.GeographyNode).all()
    node_map = {node.id: node for node in nodes}
    root_nodes = []
    for node in nodes:
        if node.parent_id and node.parent_id in node_map:
            parent = node_map[node.parent_id]
            if not hasattr(parent, 'children_nodes'):
                parent.children_nodes = []
            parent.children_nodes.append(node)
        else:
            root_nodes.append(node)
    def serialize(node):
        return {
            'id': node.id,
            'code': node.code,
            'name': node.name,
            'node_type': node.node_type,
            'status': node.status,
            'manager': node.manager,
            'parent_id': node.parent_id,
            'children': [serialize(child) for child in getattr(node, 'children_nodes', [])],
        }
    return {'items': [serialize(node) for node in root_nodes]}


@router.get('/geography/{id}/analytics')
def geography_analytics(id: str, db: Session = Depends(get_db)):
    node = get_geography_node(db, id)
    return {
        'id': node.id,
        'code': node.code,
        'name': node.name,
        'node_type': node.node_type,
        'status': node.status,
        'manager': node.manager,
        'parent_id': node.parent_id,
        'coverage': 0.0,
        'customer_density': 0.0,
        'branch_count': 0,
        'population': node.population or 0.0,
    }


@router.get('/geography/{id}/coverage')
def geography_coverage(id: str, db: Session = Depends(get_db)):
    _ = get_geography_node(db, id)
    return {
        'id': id,
        'coverage_percent': 0.0,
        'branches': 0,
        'population_served': 0.0,
        'territories': 0,
    }


@router.get('/geography/search-radius')
def geography_search_radius(lat: float, lon: float, radius_km: float = 25.0, db: Session = Depends(get_db)):
    nodes = db.query(models_geography.GeographyNode).all()
    return {'items': [{'id': node.id, 'code': node.code, 'name': node.name, 'node_type': node.node_type, 'distance_km': 0.0} for node in nodes]}


@router.get('/geography/{id}', response_model=GeographyNodeResponse)
def get_geography_node_endpoint(id: str, db: Session = Depends(get_db)):
    return get_geography_node(db, id)


@router.put('/geography/{id}', response_model=GeographyNodeResponse, dependencies=[Depends(require_role('enterprise.admin'))])
def update_geography_node(id: str, payload: GeographyNodeUpdate, db: Session = Depends(get_db)):
    node = get_geography_node(db, id)
    if payload.parent_id and payload.parent_id == id:
        raise HTTPException(status_code=400, detail='Node cannot be its own parent')
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(node, field, value)
    db.add(node)
    db.commit()
    db.refresh(node)
    try:
        record_audit(db, 'geography_node', node.id, 'updated', payload.model_dump(exclude_unset=True))
    except Exception:
        pass
    publish_event('GEOGRAPHY_UPDATED', {'id': node.id})
    return node
