"""
Predictive Analytics Router
API endpoints for machine learning and predictive analytics
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import Optional
import math
from datetime import datetime

from backend.shared.database.connection import get_db
from backend.shared.common.response import success_response
from backend.services.auth.dependencies import get_current_user
from backend.shared.database.reporting_models import PredictiveModel, ModelPrediction
from backend.services.reporting import schemas


router = APIRouter(prefix="/analytics", tags=["Reporting - Predictive Analytics"])


@router.get("/models", response_model=dict)
async def list_predictive_models(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    model_type: Optional[str] = Query(None),
    use_case: Optional[str] = Query(None),
    is_deployed: Optional[bool] = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """List all predictive models"""
    try:
        query = select(PredictiveModel).where(
            PredictiveModel.tenant_id == current_user["tenant_id"],
            PredictiveModel.is_deleted == False
        )
        
        if model_type:
            query = query.where(PredictiveModel.model_type == model_type)
        
        if use_case:
            query = query.where(PredictiveModel.use_case == use_case)
        
        if is_deployed is not None:
            query = query.where(PredictiveModel.is_deployed == is_deployed)
        
        # Count
        count_query = select(func.count()).select_from(PredictiveModel).where(
            PredictiveModel.tenant_id == current_user["tenant_id"],
            PredictiveModel.is_deleted == False
        )
        
        if model_type:
            count_query = count_query.where(PredictiveModel.model_type == model_type)
        if use_case:
            count_query = count_query.where(PredictiveModel.use_case == use_case)
        if is_deployed is not None:
            count_query = count_query.where(PredictiveModel.is_deployed == is_deployed)
        
        total = await db.scalar(count_query)
        
        # Paginate
        query = query.offset((page - 1) * page_size).limit(page_size)
        query = query.order_by(PredictiveModel.created_at.desc())
        
        result = await db.execute(query)
        models = result.scalars().all()
        
        return success_response(
            data={
                "items": [schemas.PredictiveModelResponse.model_validate(m) for m in models],
                "total": total or 0,
                "page": page,
                "page_size": page_size,
                "total_pages": math.ceil((total or 0) / page_size)
            },
            message=f"Found {total or 0} predictive models"
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("/models", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_predictive_model(
    data: schemas.PredictiveModelCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Create new predictive model"""
    try:
        model = PredictiveModel(
            tenant_id=current_user["tenant_id"],
            **data.model_dump(),
            created_by=current_user["user_id"],
            updated_by=current_user["user_id"]
        )
        
        db.add(model)
        await db.commit()
        await db.refresh(model)
        
        return success_response(
            data=schemas.PredictiveModelResponse.model_validate(model),
            message="Predictive model created successfully"
        )
        
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/models/{model_id}", response_model=dict)
async def get_predictive_model(
    model_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get predictive model details"""
    try:
        result = await db.execute(
            select(PredictiveModel).where(
                PredictiveModel.id == model_id,
                PredictiveModel.tenant_id == current_user["tenant_id"],
                PredictiveModel.is_deleted == False
            )
        )
        model = result.scalar_one_or_none()
        
        if not model:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Predictive model not found"
            )
        
        return success_response(
            data=schemas.PredictiveModelResponse.model_validate(model),
            message="Predictive model retrieved successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("/predict", response_model=dict)
async def make_prediction(
    request: schemas.PredictionRequest,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Make prediction using trained model
    
    Supports various use cases:
    - Credit risk scoring
    - Churn prediction
    - Default probability
    - Fraud detection
    """
    try:
        # Get model
        result = await db.execute(
            select(PredictiveModel).where(
                PredictiveModel.id == request.model_id,
                PredictiveModel.tenant_id == current_user["tenant_id"],
                PredictiveModel.is_deleted == False,
                PredictiveModel.is_deployed == True
            )
        )
        model = result.scalar_one_or_none()
        
        if not model:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Predictive model not found or not deployed"
            )
        
        # Make prediction (mock implementation)
        # In production, this would call actual ML model
        start_time = datetime.utcnow()
        
        predicted_value = None
        predicted_class = None
        probability = 0.75
        
        if model.use_case == "credit_risk":
            predicted_class = "LOW_RISK"
            probability = 0.85
        elif model.use_case == "churn":
            predicted_class = "NO_CHURN"
            probability = 0.92
        elif model.use_case == "default":
            predicted_value = 0.15  # 15% default probability
            probability = 0.88
        
        execution_time = int((datetime.utcnow() - start_time).total_seconds() * 1000)
        
        # Save prediction
        prediction = ModelPrediction(
            tenant_id=current_user["tenant_id"],
            model_id=request.model_id,
            entity_type=request.entity_type,
            entity_id=request.entity_id,
            input_features=request.input_features,
            predicted_value=predicted_value,
            predicted_class=predicted_class,
            probability=probability,
            feature_importance={
                "credit_score": 0.35,
                "income": 0.25,
                "existing_loans": 0.20,
                "payment_history": 0.20
            },
            explanation="Based on credit score, income, and payment history analysis",
            prediction_time_ms=execution_time,
            created_by=current_user["user_id"],
            updated_by=current_user["user_id"]
        )
        
        db.add(prediction)
        
        # Update model stats
        model.prediction_count += 1
        model.last_prediction_at = datetime.utcnow()
        
        await db.commit()
        await db.refresh(prediction)
        
        return success_response(
            data=schemas.PredictionResponse.model_validate(prediction),
            message="Prediction generated successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/predictions", response_model=dict)
async def list_predictions(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    model_id: Optional[int] = Query(None),
    entity_type: Optional[str] = Query(None),
    entity_id: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """List prediction history"""
    try:
        query = select(ModelPrediction).where(
            ModelPrediction.tenant_id == current_user["tenant_id"],
            ModelPrediction.is_deleted == False
        )
        
        if model_id:
            query = query.where(ModelPrediction.model_id == model_id)
        
        if entity_type:
            query = query.where(ModelPrediction.entity_type == entity_type)
        
        if entity_id:
            query = query.where(ModelPrediction.entity_id == entity_id)
        
        # Count
        count_query = select(func.count()).select_from(ModelPrediction).where(
            ModelPrediction.tenant_id == current_user["tenant_id"],
            ModelPrediction.is_deleted == False
        )
        
        if model_id:
            count_query = count_query.where(ModelPrediction.model_id == model_id)
        if entity_type:
            count_query = count_query.where(ModelPrediction.entity_type == entity_type)
        if entity_id:
            count_query = count_query.where(ModelPrediction.entity_id == entity_id)
        
        total = await db.scalar(count_query)
        
        # Paginate
        query = query.offset((page - 1) * page_size).limit(page_size)
        query = query.order_by(ModelPrediction.prediction_date.desc())
        
        result = await db.execute(query)
        predictions = result.scalars().all()
        
        return success_response(
            data={
                "items": [schemas.PredictionResponse.model_validate(p) for p in predictions],
                "total": total or 0,
                "page": page,
                "page_size": page_size,
                "total_pages": math.ceil((total or 0) / page_size)
            },
            message=f"Found {total or 0} predictions"
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/use-cases", response_model=dict)
async def get_analytics_use_cases(
    current_user: dict = Depends(get_current_user)
):
    """Get available predictive analytics use cases"""
    use_cases = [
        {
            "value": "credit_risk",
            "label": "Credit Risk Scoring",
            "description": "Predict credit risk for loan applications",
            "output_type": "classification",
            "classes": ["LOW_RISK", "MEDIUM_RISK", "HIGH_RISK"]
        },
        {
            "value": "churn",
            "label": "Customer Churn Prediction",
            "description": "Predict customer churn probability",
            "output_type": "classification",
            "classes": ["WILL_CHURN", "NO_CHURN"]
        },
        {
            "value": "default",
            "label": "Default Probability",
            "description": "Predict loan default probability",
            "output_type": "regression",
            "range": [0, 1]
        },
        {
            "value": "fraud",
            "label": "Fraud Detection",
            "description": "Detect fraudulent transactions",
            "output_type": "classification",
            "classes": ["FRAUD", "LEGITIMATE"]
        },
        {
            "value": "ltv",
            "label": "Customer Lifetime Value",
            "description": "Predict customer lifetime value",
            "output_type": "regression"
        }
    ]
    
    return success_response(
        data=use_cases,
        message="Analytics use cases retrieved successfully"
    )
