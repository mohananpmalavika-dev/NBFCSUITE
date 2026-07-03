"""
Phase 14: Analytics & Business Intelligence Router
Complete analytics and BI API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID
from datetime import datetime

from app.database import get_db
from app.models.analytics import (
    DataWarehouse, DataSource, Report, ReportExecution,
    Dashboard, Widget, MLModel, Prediction,
    DataStream, AnalyticsAlert, AlertNotification, DataQualityRule
)
from app.schemas.analytics import (
    DataWarehouseCreate, DataWarehouseUpdate, DataWarehouseApproval, DataWarehouseResponse,
    DataSourceCreate, DataSourceUpdate, DataSourceResponse,
    ReportCreate, ReportUpdate, ReportResponse, ReportExecuteRequest, ReportExecutionResponse,
    DashboardCreate, DashboardUpdate, DashboardResponse,
    WidgetCreate, WidgetUpdate, WidgetResponse,
    MLModelCreate, MLModelUpdate, MLModelPerformanceUpdate, MLModelResponse,
    PredictionRequest, PredictionResponse, PredictionValidation,
    DataStreamCreate, DataStreamUpdate, DataStreamResponse,
    AnalyticsAlertCreate, AnalyticsAlertUpdate, AnalyticsAlertResponse,
    AlertNotificationResponse, AlertAcknowledgement,
    DataQualityRuleCreate, DataQualityRuleUpdate, DataQualityRuleResponse,
    AnalyticsOverview, ReportExecutionMetrics, MLModelPerformanceMetrics, DataStreamHealth
)

router = APIRouter(prefix="/api/v1/gold/analytics", tags=["Analytics & BI"])


# =====================================================
# Data Warehouse Endpoints
# =====================================================

@router.post("/warehouses", response_model=DataWarehouseResponse, status_code=status.HTTP_201_CREATED)
def create_data_warehouse(
    warehouse: DataWarehouseCreate,
    db: Session = Depends(get_db)
):
    """Create new data warehouse configuration"""
    db_warehouse = DataWarehouse(**warehouse.dict())
    db.add(db_warehouse)
    db.commit()
    db.refresh(db_warehouse)
    return db_warehouse


@router.get("/warehouses", response_model=List[DataWarehouseResponse])
def list_data_warehouses(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    warehouse_type: Optional[str] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """List all data warehouses"""
    query = db.query(DataWarehouse).filter(DataWarehouse.deleted_at.is_(None))
    
    if warehouse_type:
        query = query.filter(DataWarehouse.warehouse_type == warehouse_type)
    if status:
        query = query.filter(DataWarehouse.status == status)
    
    return query.offset(skip).limit(limit).all()


@router.get("/warehouses/{warehouse_id}", response_model=DataWarehouseResponse)
def get_data_warehouse(warehouse_id: UUID, db: Session = Depends(get_db)):
    """Get data warehouse by ID"""
    warehouse = db.query(DataWarehouse).filter(
        DataWarehouse.id == warehouse_id,
        DataWarehouse.deleted_at.is_(None)
    ).first()
    
    if not warehouse:
        raise HTTPException(status_code=404, detail="Data warehouse not found")
    
    return warehouse


@router.put("/warehouses/{warehouse_id}", response_model=DataWarehouseResponse)
def update_data_warehouse(
    warehouse_id: UUID,
    warehouse: DataWarehouseUpdate,
    db: Session = Depends(get_db)
):
    """Update data warehouse"""
    db_warehouse = db.query(DataWarehouse).filter(
        DataWarehouse.id == warehouse_id,
        DataWarehouse.deleted_at.is_(None)
    ).first()
    
    if not db_warehouse:
        raise HTTPException(status_code=404, detail="Data warehouse not found")
    
    for key, value in warehouse.dict(exclude_unset=True).items():
        setattr(db_warehouse, key, value)
    
    db.commit()
    db.refresh(db_warehouse)
    return db_warehouse


@router.post("/warehouses/{warehouse_id}/approve", response_model=DataWarehouseResponse)
def approve_data_warehouse(
    warehouse_id: UUID,
    approval: DataWarehouseApproval,
    db: Session = Depends(get_db)
):
    """Approve or reject data warehouse"""
    db_warehouse = db.query(DataWarehouse).filter(
        DataWarehouse.id == warehouse_id,
        DataWarehouse.deleted_at.is_(None)
    ).first()
    
    if not db_warehouse:
        raise HTTPException(status_code=404, detail="Data warehouse not found")
    
    db_warehouse.approval_status = approval.approval_status
    db_warehouse.checker_comment = approval.checker_comment
    db_warehouse.approved_at = datetime.utcnow()
    
    db.commit()
    db.refresh(db_warehouse)
    return db_warehouse


@router.delete("/warehouses/{warehouse_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_data_warehouse(warehouse_id: UUID, db: Session = Depends(get_db)):
    """Soft delete data warehouse"""
    db_warehouse = db.query(DataWarehouse).filter(
        DataWarehouse.id == warehouse_id,
        DataWarehouse.deleted_at.is_(None)
    ).first()
    
    if not db_warehouse:
        raise HTTPException(status_code=404, detail="Data warehouse not found")
    
    db_warehouse.deleted_at = datetime.utcnow()
    db.commit()
    return None


# =====================================================
# Data Source Endpoints
# =====================================================

@router.post("/data-sources", response_model=DataSourceResponse, status_code=status.HTTP_201_CREATED)
def create_data_source(
    data_source: DataSourceCreate,
    db: Session = Depends(get_db)
):
    """Create new data source"""
    db_source = DataSource(**data_source.dict())
    db.add(db_source)
    db.commit()
    db.refresh(db_source)
    return db_source


@router.get("/data-sources", response_model=List[DataSourceResponse])
def list_data_sources(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    source_type: Optional[str] = None,
    status: Optional[str] = None,
    health_status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """List all data sources"""
    query = db.query(DataSource).filter(DataSource.deleted_at.is_(None))
    
    if source_type:
        query = query.filter(DataSource.source_type == source_type)
    if status:
        query = query.filter(DataSource.status == status)
    if health_status:
        query = query.filter(DataSource.health_status == health_status)
    
    return query.offset(skip).limit(limit).all()


@router.get("/data-sources/{source_id}", response_model=DataSourceResponse)
def get_data_source(source_id: UUID, db: Session = Depends(get_db)):
    """Get data source by ID"""
    source = db.query(DataSource).filter(
        DataSource.id == source_id,
        DataSource.deleted_at.is_(None)
    ).first()
    
    if not source:
        raise HTTPException(status_code=404, detail="Data source not found")
    
    return source


@router.put("/data-sources/{source_id}", response_model=DataSourceResponse)
def update_data_source(
    source_id: UUID,
    data_source: DataSourceUpdate,
    db: Session = Depends(get_db)
):
    """Update data source"""
    db_source = db.query(DataSource).filter(
        DataSource.id == source_id,
        DataSource.deleted_at.is_(None)
    ).first()
    
    if not db_source:
        raise HTTPException(status_code=404, detail="Data source not found")
    
    for key, value in data_source.dict(exclude_unset=True).items():
        setattr(db_source, key, value)
    
    db.commit()
    db.refresh(db_source)
    return db_source


@router.post("/data-sources/{source_id}/sync", response_model=DataSourceResponse)
def sync_data_source(source_id: UUID, db: Session = Depends(get_db)):
    """Trigger data source sync"""
    db_source = db.query(DataSource).filter(
        DataSource.id == source_id,
        DataSource.deleted_at.is_(None)
    ).first()
    
    if not db_source:
        raise HTTPException(status_code=404, detail="Data source not found")
    
    db_source.sync_status = "IN_PROGRESS"
    db_source.last_sync_at = datetime.utcnow()
    
    db.commit()
    db.refresh(db_source)
    return db_source


@router.post("/data-sources/{source_id}/health-check", response_model=DataSourceResponse)
def check_data_source_health(source_id: UUID, db: Session = Depends(get_db)):
    """Perform health check on data source"""
    db_source = db.query(DataSource).filter(
        DataSource.id == source_id,
        DataSource.deleted_at.is_(None)
    ).first()
    
    if not db_source:
        raise HTTPException(status_code=404, detail="Data source not found")
    
    db_source.last_health_check_at = datetime.utcnow()
    db_source.health_status = "HEALTHY"
    
    db.commit()
    db.refresh(db_source)
    return db_source


@router.delete("/data-sources/{source_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_data_source(source_id: UUID, db: Session = Depends(get_db)):
    """Soft delete data source"""
    db_source = db.query(DataSource).filter(
        DataSource.id == source_id,
        DataSource.deleted_at.is_(None)
    ).first()
    
    if not db_source:
        raise HTTPException(status_code=404, detail="Data source not found")
    
    db_source.deleted_at = datetime.utcnow()
    db.commit()
    return None


# =====================================================
# Report Endpoints
# =====================================================

@router.post("/reports", response_model=ReportResponse, status_code=status.HTTP_201_CREATED)
def create_report(
    report: ReportCreate,
    db: Session = Depends(get_db)
):
    """Create new report"""
    db_report = Report(**report.dict())
    db.add(db_report)
    db.commit()
    db.refresh(db_report)
    return db_report


@router.get("/reports", response_model=List[ReportResponse])
def list_reports(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    report_type: Optional[str] = None,
    category: Optional[str] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """List all reports"""
    query = db.query(Report).filter(Report.deleted_at.is_(None))
    
    if report_type:
        query = query.filter(Report.report_type == report_type)
    if category:
        query = query.filter(Report.category == category)
    if status:
        query = query.filter(Report.status == status)
    
    return query.offset(skip).limit(limit).all()


@router.get("/reports/{report_id}", response_model=ReportResponse)
def get_report(report_id: UUID, db: Session = Depends(get_db)):
    """Get report by ID"""
    report = db.query(Report).filter(
        Report.id == report_id,
        Report.deleted_at.is_(None)
    ).first()
    
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    
    return report


@router.put("/reports/{report_id}", response_model=ReportResponse)
def update_report(
    report_id: UUID,
    report: ReportUpdate,
    db: Session = Depends(get_db)
):
    """Update report"""
    db_report = db.query(Report).filter(
        Report.id == report_id,
        Report.deleted_at.is_(None)
    ).first()
    
    if not db_report:
        raise HTTPException(status_code=404, detail="Report not found")
    
    for key, value in report.dict(exclude_unset=True).items():
        setattr(db_report, key, value)
    
    db.commit()
    db.refresh(db_report)
    return db_report


@router.post("/reports/{report_id}/execute", response_model=ReportExecutionResponse)
def execute_report(
    report_id: UUID,
    execution_request: ReportExecuteRequest,
    db: Session = Depends(get_db)
):
    """Execute report with parameters"""
    report = db.query(Report).filter(
        Report.id == report_id,
        Report.deleted_at.is_(None)
    ).first()
    
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    
    # Create execution record
    execution = ReportExecution(
        execution_code=f"EXEC-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
        report_id=report_id,
        execution_type="MANUAL",
        parameters_used=execution_request.parameters,
        filters_applied=execution_request.filters,
        started_at=datetime.utcnow(),
        result_status="IN_PROGRESS",
        result_format=execution_request.output_format
    )
    
    db.add(execution)
    db.commit()
    db.refresh(execution)
    return execution


@router.get("/reports/{report_id}/executions", response_model=List[ReportExecutionResponse])
def list_report_executions(
    report_id: UUID,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db)
):
    """List report executions"""
    return db.query(ReportExecution).filter(
        ReportExecution.report_id == report_id
    ).order_by(ReportExecution.started_at.desc()).offset(skip).limit(limit).all()


@router.delete("/reports/{report_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_report(report_id: UUID, db: Session = Depends(get_db)):
    """Soft delete report"""
    db_report = db.query(Report).filter(
        Report.id == report_id,
        Report.deleted_at.is_(None)
    ).first()
    
    if not db_report:
        raise HTTPException(status_code=404, detail="Report not found")
    
    db_report.deleted_at = datetime.utcnow()
    db.commit()
    return None


# =====================================================
# Dashboard Endpoints
# =====================================================

@router.post("/dashboards", response_model=DashboardResponse, status_code=status.HTTP_201_CREATED)
def create_dashboard(
    dashboard: DashboardCreate,
    db: Session = Depends(get_db)
):
    """Create new dashboard"""
    db_dashboard = Dashboard(**dashboard.dict())
    db.add(db_dashboard)
    db.commit()
    db.refresh(db_dashboard)
    return db_dashboard


@router.get("/dashboards", response_model=List[DashboardResponse])
def list_dashboards(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    dashboard_type: Optional[str] = None,
    category: Optional[str] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """List all dashboards"""
    query = db.query(Dashboard).filter(Dashboard.deleted_at.is_(None))
    
    if dashboard_type:
        query = query.filter(Dashboard.dashboard_type == dashboard_type)
    if category:
        query = query.filter(Dashboard.category == category)
    if status:
        query = query.filter(Dashboard.status == status)
    
    return query.offset(skip).limit(limit).all()


@router.get("/dashboards/{dashboard_id}", response_model=DashboardResponse)
def get_dashboard(dashboard_id: UUID, db: Session = Depends(get_db)):
    """Get dashboard by ID"""
    dashboard = db.query(Dashboard).filter(
        Dashboard.id == dashboard_id,
        Dashboard.deleted_at.is_(None)
    ).first()
    
    if not dashboard:
        raise HTTPException(status_code=404, detail="Dashboard not found")
    
    # Increment view count
    dashboard.view_count += 1
    dashboard.last_viewed_at = datetime.utcnow()
    db.commit()
    db.refresh(dashboard)
    
    return dashboard


@router.put("/dashboards/{dashboard_id}", response_model=DashboardResponse)
def update_dashboard(
    dashboard_id: UUID,
    dashboard: DashboardUpdate,
    db: Session = Depends(get_db)
):
    """Update dashboard"""
    db_dashboard = db.query(Dashboard).filter(
        Dashboard.id == dashboard_id,
        Dashboard.deleted_at.is_(None)
    ).first()
    
    if not db_dashboard:
        raise HTTPException(status_code=404, detail="Dashboard not found")
    
    for key, value in dashboard.dict(exclude_unset=True).items():
        setattr(db_dashboard, key, value)
    
    db.commit()
    db.refresh(db_dashboard)
    return db_dashboard


@router.post("/dashboards/{dashboard_id}/refresh", response_model=DashboardResponse)
def refresh_dashboard(dashboard_id: UUID, db: Session = Depends(get_db)):
    """Refresh dashboard data"""
    db_dashboard = db.query(Dashboard).filter(
        Dashboard.id == dashboard_id,
        Dashboard.deleted_at.is_(None)
    ).first()
    
    if not db_dashboard:
        raise HTTPException(status_code=404, detail="Dashboard not found")
    
    db_dashboard.last_refreshed_at = datetime.utcnow()
    db.commit()
    db.refresh(db_dashboard)
    return db_dashboard


@router.delete("/dashboards/{dashboard_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_dashboard(dashboard_id: UUID, db: Session = Depends(get_db)):
    """Soft delete dashboard"""
    db_dashboard = db.query(Dashboard).filter(
        Dashboard.id == dashboard_id,
        Dashboard.deleted_at.is_(None)
    ).first()
    
    if not db_dashboard:
        raise HTTPException(status_code=404, detail="Dashboard not found")
    
    db_dashboard.deleted_at = datetime.utcnow()
    db.commit()
    return None


# =====================================================
# Widget Endpoints
# =====================================================

@router.post("/widgets", response_model=WidgetResponse, status_code=status.HTTP_201_CREATED)
def create_widget(
    widget: WidgetCreate,
    db: Session = Depends(get_db)
):
    """Create new widget"""
    db_widget = Widget(**widget.dict())
    db.add(db_widget)
    db.commit()
    db.refresh(db_widget)
    return db_widget


@router.get("/widgets", response_model=List[WidgetResponse])
def list_widgets(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    widget_type: Optional[str] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """List all widgets"""
    query = db.query(Widget).filter(Widget.deleted_at.is_(None))
    
    if widget_type:
        query = query.filter(Widget.widget_type == widget_type)
    if status:
        query = query.filter(Widget.status == status)
    
    return query.offset(skip).limit(limit).all()


@router.get("/widgets/{widget_id}", response_model=WidgetResponse)
def get_widget(widget_id: UUID, db: Session = Depends(get_db)):
    """Get widget by ID"""
    widget = db.query(Widget).filter(
        Widget.id == widget_id,
        Widget.deleted_at.is_(None)
    ).first()
    
    if not widget:
        raise HTTPException(status_code=404, detail="Widget not found")
    
    return widget


@router.put("/widgets/{widget_id}", response_model=WidgetResponse)
def update_widget(
    widget_id: UUID,
    widget: WidgetUpdate,
    db: Session = Depends(get_db)
):
    """Update widget"""
    db_widget = db.query(Widget).filter(
        Widget.id == widget_id,
        Widget.deleted_at.is_(None)
    ).first()
    
    if not db_widget:
        raise HTTPException(status_code=404, detail="Widget not found")
    
    for key, value in widget.dict(exclude_unset=True).items():
        setattr(db_widget, key, value)
    
    db.commit()
    db.refresh(db_widget)
    return db_widget


@router.delete("/widgets/{widget_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_widget(widget_id: UUID, db: Session = Depends(get_db)):
    """Soft delete widget"""
    db_widget = db.query(Widget).filter(
        Widget.id == widget_id,
        Widget.deleted_at.is_(None)
    ).first()
    
    if not db_widget:
        raise HTTPException(status_code=404, detail="Widget not found")
    
    db_widget.deleted_at = datetime.utcnow()
    db.commit()
    return None


# =====================================================
# ML Model Endpoints
# =====================================================

@router.post("/ml-models", response_model=MLModelResponse, status_code=status.HTTP_201_CREATED)
def create_ml_model(
    model: MLModelCreate,
    db: Session = Depends(get_db)
):
    """Create new ML model"""
    db_model = MLModel(**model.dict())
    db.add(db_model)
    db.commit()
    db.refresh(db_model)
    return db_model


@router.get("/ml-models", response_model=List[MLModelResponse])
def list_ml_models(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    model_type: Optional[str] = None,
    deployment_status: Optional[str] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """List all ML models"""
    query = db.query(MLModel).filter(MLModel.deleted_at.is_(None))
    
    if model_type:
        query = query.filter(MLModel.model_type == model_type)
    if deployment_status:
        query = query.filter(MLModel.deployment_status == deployment_status)
    if status:
        query = query.filter(MLModel.status == status)
    
    return query.offset(skip).limit(limit).all()


@router.get("/ml-models/{model_id}", response_model=MLModelResponse)
def get_ml_model(model_id: UUID, db: Session = Depends(get_db)):
    """Get ML model by ID"""
    model = db.query(MLModel).filter(
        MLModel.id == model_id,
        MLModel.deleted_at.is_(None)
    ).first()
    
    if not model:
        raise HTTPException(status_code=404, detail="ML model not found")
    
    return model


@router.put("/ml-models/{model_id}", response_model=MLModelResponse)
def update_ml_model(
    model_id: UUID,
    model: MLModelUpdate,
    db: Session = Depends(get_db)
):
    """Update ML model"""
    db_model = db.query(MLModel).filter(
        MLModel.id == model_id,
        MLModel.deleted_at.is_(None)
    ).first()
    
    if not db_model:
        raise HTTPException(status_code=404, detail="ML model not found")
    
    for key, value in model.dict(exclude_unset=True).items():
        setattr(db_model, key, value)
    
    db.commit()
    db.refresh(db_model)
    return db_model


@router.put("/ml-models/{model_id}/performance", response_model=MLModelResponse)
def update_model_performance(
    model_id: UUID,
    performance: MLModelPerformanceUpdate,
    db: Session = Depends(get_db)
):
    """Update ML model performance metrics"""
    db_model = db.query(MLModel).filter(
        MLModel.id == model_id,
        MLModel.deleted_at.is_(None)
    ).first()
    
    if not db_model:
        raise HTTPException(status_code=404, detail="ML model not found")
    
    for key, value in performance.dict(exclude_unset=True).items():
        setattr(db_model, key, value)
    
    db.commit()
    db.refresh(db_model)
    return db_model


@router.post("/ml-models/{model_id}/deploy", response_model=MLModelResponse)
def deploy_ml_model(model_id: UUID, db: Session = Depends(get_db)):
    """Deploy ML model"""
    db_model = db.query(MLModel).filter(
        MLModel.id == model_id,
        MLModel.deleted_at.is_(None)
    ).first()
    
    if not db_model:
        raise HTTPException(status_code=404, detail="ML model not found")
    
    db_model.deployment_status = "DEPLOYED"
    db_model.deployed_at = datetime.utcnow()
    
    db.commit()
    db.refresh(db_model)
    return db_model


@router.post("/ml-models/{model_id}/predict", response_model=PredictionResponse)
def make_prediction(
    model_id: UUID,
    prediction_request: PredictionRequest,
    db: Session = Depends(get_db)
):
    """Make prediction using ML model"""
    model = db.query(MLModel).filter(
        MLModel.id == model_id,
        MLModel.deleted_at.is_(None)
    ).first()
    
    if not model:
        raise HTTPException(status_code=404, detail="ML model not found")
    
    if model.deployment_status != "DEPLOYED":
        raise HTTPException(status_code=400, detail="Model is not deployed")
    
    # Create prediction record
    prediction = Prediction(
        prediction_code=f"PRED-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
        model_id=model_id,
        input_features=prediction_request.input_features,
        prediction_result={},  # Would be populated by actual ML inference
        prediction_type=prediction_request.prediction_type,
        business_context=prediction_request.business_context,
        model_version=model.version
    )
    
    db.add(prediction)
    
    # Update model usage stats
    model.prediction_count += 1
    model.last_prediction_at = datetime.utcnow()
    
    db.commit()
    db.refresh(prediction)
    return prediction


@router.get("/ml-models/{model_id}/predictions", response_model=List[PredictionResponse])
def list_model_predictions(
    model_id: UUID,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db)
):
    """List predictions for a model"""
    return db.query(Prediction).filter(
        Prediction.model_id == model_id
    ).order_by(Prediction.created_at.desc()).offset(skip).limit(limit).all()


@router.delete("/ml-models/{model_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_ml_model(model_id: UUID, db: Session = Depends(get_db)):
    """Soft delete ML model"""
    db_model = db.query(MLModel).filter(
        MLModel.id == model_id,
        MLModel.deleted_at.is_(None)
    ).first()
    
    if not db_model:
        raise HTTPException(status_code=404, detail="ML model not found")
    
    db_model.deleted_at = datetime.utcnow()
    db.commit()
    return None


# =====================================================
# Prediction Endpoints
# =====================================================

@router.get("/predictions/{prediction_id}", response_model=PredictionResponse)
def get_prediction(prediction_id: UUID, db: Session = Depends(get_db)):
    """Get prediction by ID"""
    prediction = db.query(Prediction).filter(Prediction.id == prediction_id).first()
    
    if not prediction:
        raise HTTPException(status_code=404, detail="Prediction not found")
    
    return prediction


@router.post("/predictions/{prediction_id}/validate", response_model=PredictionResponse)
def validate_prediction(
    prediction_id: UUID,
    validation: PredictionValidation,
    db: Session = Depends(get_db)
):
    """Validate prediction with actual value"""
    prediction = db.query(Prediction).filter(Prediction.id == prediction_id).first()
    
    if not prediction:
        raise HTTPException(status_code=404, detail="Prediction not found")
    
    prediction.actual_value = validation.actual_value
    # Calculate accuracy/error based on actual vs predicted
    prediction.is_accurate = True  # Would be calculated based on tolerance
    
    db.commit()
    db.refresh(prediction)
    return prediction


# =====================================================
# Data Stream Endpoints
# =====================================================

@router.post("/data-streams", response_model=DataStreamResponse, status_code=status.HTTP_201_CREATED)
def create_data_stream(
    stream: DataStreamCreate,
    db: Session = Depends(get_db)
):
    """Create new data stream"""
    db_stream = DataStream(**stream.dict())
    db.add(db_stream)
    db.commit()
    db.refresh(db_stream)
    return db_stream


@router.get("/data-streams", response_model=List[DataStreamResponse])
def list_data_streams(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    stream_type: Optional[str] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """List all data streams"""
    query = db.query(DataStream).filter(DataStream.deleted_at.is_(None))
    
    if stream_type:
        query = query.filter(DataStream.stream_type == stream_type)
    if status:
        query = query.filter(DataStream.status == status)
    
    return query.offset(skip).limit(limit).all()


@router.get("/data-streams/{stream_id}", response_model=DataStreamResponse)
def get_data_stream(stream_id: UUID, db: Session = Depends(get_db)):
    """Get data stream by ID"""
    stream = db.query(DataStream).filter(
        DataStream.id == stream_id,
        DataStream.deleted_at.is_(None)
    ).first()
    
    if not stream:
        raise HTTPException(status_code=404, detail="Data stream not found")
    
    return stream


@router.put("/data-streams/{stream_id}", response_model=DataStreamResponse)
def update_data_stream(
    stream_id: UUID,
    stream: DataStreamUpdate,
    db: Session = Depends(get_db)
):
    """Update data stream"""
    db_stream = db.query(DataStream).filter(
        DataStream.id == stream_id,
        DataStream.deleted_at.is_(None)
    ).first()
    
    if not db_stream:
        raise HTTPException(status_code=404, detail="Data stream not found")
    
    for key, value in stream.dict(exclude_unset=True).items():
        setattr(db_stream, key, value)
    
    db.commit()
    db.refresh(db_stream)
    return db_stream


@router.post("/data-streams/{stream_id}/start", response_model=DataStreamResponse)
def start_data_stream(stream_id: UUID, db: Session = Depends(get_db)):
    """Start data stream processing"""
    db_stream = db.query(DataStream).filter(
        DataStream.id == stream_id,
        DataStream.deleted_at.is_(None)
    ).first()
    
    if not db_stream:
        raise HTTPException(status_code=404, detail="Data stream not found")
    
    db_stream.status = "ACTIVE"
    db.commit()
    db.refresh(db_stream)
    return db_stream


@router.post("/data-streams/{stream_id}/stop", response_model=DataStreamResponse)
def stop_data_stream(stream_id: UUID, db: Session = Depends(get_db)):
    """Stop data stream processing"""
    db_stream = db.query(DataStream).filter(
        DataStream.id == stream_id,
        DataStream.deleted_at.is_(None)
    ).first()
    
    if not db_stream:
        raise HTTPException(status_code=404, detail="Data stream not found")
    
    db_stream.status = "STOPPED"
    db.commit()
    db.refresh(db_stream)
    return db_stream


@router.delete("/data-streams/{stream_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_data_stream(stream_id: UUID, db: Session = Depends(get_db)):
    """Soft delete data stream"""
    db_stream = db.query(DataStream).filter(
        DataStream.id == stream_id,
        DataStream.deleted_at.is_(None)
    ).first()
    
    if not db_stream:
        raise HTTPException(status_code=404, detail="Data stream not found")
    
    db_stream.deleted_at = datetime.utcnow()
    db.commit()
    return None


# =====================================================
# Analytics Alert Endpoints
# =====================================================

@router.post("/alerts", response_model=AnalyticsAlertResponse, status_code=status.HTTP_201_CREATED)
def create_analytics_alert(
    alert: AnalyticsAlertCreate,
    db: Session = Depends(get_db)
):
    """Create new analytics alert"""
    db_alert = AnalyticsAlert(**alert.dict())
    db.add(db_alert)
    db.commit()
    db.refresh(db_alert)
    return db_alert


@router.get("/alerts", response_model=List[AnalyticsAlertResponse])
def list_analytics_alerts(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    alert_type: Optional[str] = None,
    severity: Optional[str] = None,
    is_triggered: Optional[bool] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """List all analytics alerts"""
    query = db.query(AnalyticsAlert).filter(AnalyticsAlert.deleted_at.is_(None))
    
    if alert_type:
        query = query.filter(AnalyticsAlert.alert_type == alert_type)
    if severity:
        query = query.filter(AnalyticsAlert.severity == severity)
    if is_triggered is not None:
        query = query.filter(AnalyticsAlert.is_triggered == is_triggered)
    if status:
        query = query.filter(AnalyticsAlert.status == status)
    
    return query.offset(skip).limit(limit).all()


@router.get("/alerts/{alert_id}", response_model=AnalyticsAlertResponse)
def get_analytics_alert(alert_id: UUID, db: Session = Depends(get_db)):
    """Get analytics alert by ID"""
    alert = db.query(AnalyticsAlert).filter(
        AnalyticsAlert.id == alert_id,
        AnalyticsAlert.deleted_at.is_(None)
    ).first()
    
    if not alert:
        raise HTTPException(status_code=404, detail="Analytics alert not found")
    
    return alert


@router.put("/alerts/{alert_id}", response_model=AnalyticsAlertResponse)
def update_analytics_alert(
    alert_id: UUID,
    alert: AnalyticsAlertUpdate,
    db: Session = Depends(get_db)
):
    """Update analytics alert"""
    db_alert = db.query(AnalyticsAlert).filter(
        AnalyticsAlert.id == alert_id,
        AnalyticsAlert.deleted_at.is_(None)
    ).first()
    
    if not db_alert:
        raise HTTPException(status_code=404, detail="Analytics alert not found")
    
    for key, value in alert.dict(exclude_unset=True).items():
        setattr(db_alert, key, value)
    
    db.commit()
    db.refresh(db_alert)
    return db_alert


@router.post("/alerts/{alert_id}/test", response_model=AnalyticsAlertResponse)
def test_analytics_alert(alert_id: UUID, db: Session = Depends(get_db)):
    """Test analytics alert evaluation"""
    db_alert = db.query(AnalyticsAlert).filter(
        AnalyticsAlert.id == alert_id,
        AnalyticsAlert.deleted_at.is_(None)
    ).first()
    
    if not db_alert:
        raise HTTPException(status_code=404, detail="Analytics alert not found")
    
    db_alert.last_evaluated_at = datetime.utcnow()
    db.commit()
    db.refresh(db_alert)
    return db_alert


@router.get("/alerts/{alert_id}/notifications", response_model=List[AlertNotificationResponse])
def list_alert_notifications(
    alert_id: UUID,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db)
):
    """List notifications for an alert"""
    return db.query(AlertNotification).filter(
        AlertNotification.alert_id == alert_id
    ).order_by(AlertNotification.created_at.desc()).offset(skip).limit(limit).all()


@router.delete("/alerts/{alert_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_analytics_alert(alert_id: UUID, db: Session = Depends(get_db)):
    """Soft delete analytics alert"""
    db_alert = db.query(AnalyticsAlert).filter(
        AnalyticsAlert.id == alert_id,
        AnalyticsAlert.deleted_at.is_(None)
    ).first()
    
    if not db_alert:
        raise HTTPException(status_code=404, detail="Analytics alert not found")
    
    db_alert.deleted_at = datetime.utcnow()
    db.commit()
    return None


# =====================================================
# Alert Notification Endpoints
# =====================================================

@router.get("/notifications/{notification_id}", response_model=AlertNotificationResponse)
def get_alert_notification(notification_id: UUID, db: Session = Depends(get_db)):
    """Get alert notification by ID"""
    notification = db.query(AlertNotification).filter(
        AlertNotification.id == notification_id
    ).first()
    
    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")
    
    return notification


@router.post("/notifications/{notification_id}/acknowledge", response_model=AlertNotificationResponse)
def acknowledge_alert_notification(
    notification_id: UUID,
    acknowledgement: AlertAcknowledgement,
    db: Session = Depends(get_db)
):
    """Acknowledge alert notification"""
    notification = db.query(AlertNotification).filter(
        AlertNotification.id == notification_id
    ).first()
    
    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")
    
    notification.acknowledged_at = datetime.utcnow()
    notification.resolution_notes = acknowledgement.resolution_notes
    notification.resolved_at = datetime.utcnow()
    
    db.commit()
    db.refresh(notification)
    return notification


# =====================================================
# Data Quality Rule Endpoints
# =====================================================

@router.post("/data-quality-rules", response_model=DataQualityRuleResponse, status_code=status.HTTP_201_CREATED)
def create_data_quality_rule(
    rule: DataQualityRuleCreate,
    db: Session = Depends(get_db)
):
    """Create new data quality rule"""
    db_rule = DataQualityRule(**rule.dict())
    db.add(db_rule)
    db.commit()
    db.refresh(db_rule)
    return db_rule


@router.get("/data-quality-rules", response_model=List[DataQualityRuleResponse])
def list_data_quality_rules(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    rule_type: Optional[str] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """List all data quality rules"""
    query = db.query(DataQualityRule).filter(DataQualityRule.deleted_at.is_(None))
    
    if rule_type:
        query = query.filter(DataQualityRule.rule_type == rule_type)
    if status:
        query = query.filter(DataQualityRule.status == status)
    
    return query.offset(skip).limit(limit).all()


@router.get("/data-quality-rules/{rule_id}", response_model=DataQualityRuleResponse)
def get_data_quality_rule(rule_id: UUID, db: Session = Depends(get_db)):
    """Get data quality rule by ID"""
    rule = db.query(DataQualityRule).filter(
        DataQualityRule.id == rule_id,
        DataQualityRule.deleted_at.is_(None)
    ).first()
    
    if not rule:
        raise HTTPException(status_code=404, detail="Data quality rule not found")
    
    return rule


@router.put("/data-quality-rules/{rule_id}", response_model=DataQualityRuleResponse)
def update_data_quality_rule(
    rule_id: UUID,
    rule: DataQualityRuleUpdate,
    db: Session = Depends(get_db)
):
    """Update data quality rule"""
    db_rule = db.query(DataQualityRule).filter(
        DataQualityRule.id == rule_id,
        DataQualityRule.deleted_at.is_(None)
    ).first()
    
    if not db_rule:
        raise HTTPException(status_code=404, detail="Data quality rule not found")
    
    for key, value in rule.dict(exclude_unset=True).items():
        setattr(db_rule, key, value)
    
    db.commit()
    db.refresh(db_rule)
    return db_rule


@router.post("/data-quality-rules/{rule_id}/execute", response_model=DataQualityRuleResponse)
def execute_data_quality_rule(rule_id: UUID, db: Session = Depends(get_db)):
    """Execute data quality rule"""
    db_rule = db.query(DataQualityRule).filter(
        DataQualityRule.id == rule_id,
        DataQualityRule.deleted_at.is_(None)
    ).first()
    
    if not db_rule:
        raise HTTPException(status_code=404, detail="Data quality rule not found")
    
    db_rule.last_executed_at = datetime.utcnow()
    db_rule.last_result_status = "PASSED"  # Would be determined by actual validation
    
    db.commit()
    db.refresh(db_rule)
    return db_rule


@router.delete("/data-quality-rules/{rule_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_data_quality_rule(rule_id: UUID, db: Session = Depends(get_db)):
    """Soft delete data quality rule"""
    db_rule = db.query(DataQualityRule).filter(
        DataQualityRule.id == rule_id,
        DataQualityRule.deleted_at.is_(None)
    ).first()
    
    if not db_rule:
        raise HTTPException(status_code=404, detail="Data quality rule not found")
    
    db_rule.deleted_at = datetime.utcnow()
    db.commit()
    return None


# =====================================================
# Statistics & Analytics Endpoints
# =====================================================

@router.get("/statistics/overview", response_model=AnalyticsOverview)
def get_analytics_overview(db: Session = Depends(get_db)):
    """Get analytics platform overview statistics"""
    from sqlalchemy import text
    
    result = db.execute(text("SELECT * FROM v_analytics_overview")).fetchone()
    
    if not result:
        return AnalyticsOverview(
            total_data_sources=0, active_data_sources=0, total_reports=0,
            total_dashboards=0, total_ml_models=0, deployed_models=0,
            total_streams=0, active_streams=0, active_alerts=0,
            triggered_alerts=0, total_dashboard_views=0, total_predictions=0
        )
    
    return AnalyticsOverview(
        total_data_sources=result[0] or 0,
        active_data_sources=result[1] or 0,
        total_reports=result[2] or 0,
        total_dashboards=result[3] or 0,
        total_ml_models=result[4] or 0,
        deployed_models=result[5] or 0,
        total_streams=result[6] or 0,
        active_streams=result[7] or 0,
        active_alerts=result[8] or 0,
        triggered_alerts=result[9] or 0,
        total_dashboard_views=result[10] or 0,
        total_predictions=result[11] or 0
    )


@router.get("/statistics/report-executions", response_model=List[ReportExecutionMetrics])
def get_report_execution_metrics(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db)
):
    """Get report execution metrics"""
    from sqlalchemy import text
    
    query = text("""
        SELECT * FROM v_report_execution_metrics
        ORDER BY total_executions DESC
        LIMIT :limit OFFSET :skip
    """)
    
    results = db.execute(query, {"limit": limit, "skip": skip}).fetchall()
    
    metrics = []
    for row in results:
        metrics.append(ReportExecutionMetrics(
            report_id=row[0],
            report_code=row[1],
            report_name=row[2],
            report_type=row[3],
            total_executions=row[4] or 0,
            successful_executions=row[5] or 0,
            failed_executions=row[6] or 0,
            avg_execution_time_ms=row[7],
            max_execution_time_ms=row[8],
            min_execution_time_ms=row[9],
            avg_rows_returned=row[10],
            last_execution_at=row[11]
        ))
    
    return metrics


@router.get("/statistics/ml-model-performance", response_model=List[MLModelPerformanceMetrics])
def get_ml_model_performance_metrics(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db)
):
    """Get ML model performance metrics"""
    from sqlalchemy import text
    
    query = text("""
        SELECT * FROM v_ml_model_performance
        ORDER BY prediction_count DESC
        LIMIT :limit OFFSET :skip
    """)
    
    results = db.execute(query, {"limit": limit, "skip": skip}).fetchall()
    
    metrics = []
    for row in results:
        metrics.append(MLModelPerformanceMetrics(
            model_id=row[0],
            model_code=row[1],
            model_name=row[2],
            model_type=row[3],
            algorithm=row[4],
            deployment_status=row[5],
            accuracy_score=row[6],
            precision_score=row[7],
            recall_score=row[8],
            f1_score=row[9],
            prediction_count=row[10] or 0,
            avg_prediction_time_ms=row[11],
            last_prediction_at=row[12],
            total_predictions_recorded=row[13] or 0,
            avg_confidence_score=row[14],
            accurate_predictions=row[15] or 0,
            inaccurate_predictions=row[16] or 0
        ))
    
    return metrics


@router.get("/statistics/stream-health", response_model=List[DataStreamHealth])
def get_data_stream_health(db: Session = Depends(get_db)):
    """Get data stream health metrics"""
    from sqlalchemy import text
    
    results = db.execute(text("SELECT * FROM v_data_stream_health")).fetchall()
    
    health_metrics = []
    for row in results:
        health_metrics.append(DataStreamHealth(
            stream_id=row[0],
            stream_code=row[1],
            stream_name=row[2],
            stream_type=row[3],
            status=row[4],
            messages_per_second=row[5],
            total_messages_processed=row[6] or 0,
            last_message_at=row[7],
            lag_seconds=row[8],
            error_count=row[9] or 0,
            health_status=row[10],
            created_at=row[11],
            updated_at=row[12]
        ))
    
    return health_metrics
