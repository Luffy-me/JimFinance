"""
Transaction Intelligence API endpoints.
Handles OCR, text processing, classification, and enrichment.
"""

import logging
from io import BytesIO

from fastapi import APIRouter, Depends, HTTPException, status, File, UploadFile, Form
from sqlalchemy.orm import Session

from app.db.base import get_db
from app.models.database import User, Account, Transaction
from app.schemas import (
    TransactionIntelligenceRequest,
    TransactionIntelligenceResponse,
    OCRUploadRequest,
    OCRUploadResponse,
    ClassificationResult,
    RecurringPatternResult,
    AnomalyDetectionResult,
)
from app.api.v1.endpoints.users import get_current_user
from app.services.transaction_intelligence import TransactionIntelligenceService

logger = logging.getLogger(__name__)

router = APIRouter()


# Initialize service
def get_intelligence_service() -> TransactionIntelligenceService:
    """Get transaction intelligence service instance."""
    return TransactionIntelligenceService()


@router.post("/intelligence/process-text", response_model=TransactionIntelligenceResponse)
async def process_text_transaction(
    request: TransactionIntelligenceRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    service: TransactionIntelligenceService = Depends(get_intelligence_service),
):
    """
    Process raw text input through intelligence pipeline.
    
    Example: "Taxi 420 RUB" or "1500 RUB Pyaterochka"
    
    Returns:
    - Classified transaction
    - Confidence score
    - Extracted merchant, amount, currency
    """
    # Verify account belongs to user
    account = db.query(Account).filter(
        (Account.id == request.account_id) & (Account.user_id == current_user.id)
    ).first()
    
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Account not found",
        )
    
    if not request.text and not (request.merchant and request.amount):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Either 'text' or both 'merchant' and 'amount' required",
        )
    
    try:
        # Process through intelligence pipeline
        if request.text:
            transaction = service.process_text_input(
                text=request.text,
                user_id=current_user.id,
                account_id=request.account_id,
                source_type="api_text",
            )
        else:
            # Process from structured input
            parsed = {
                "merchant": request.merchant,
                "amount": request.amount,
                "currency": request.currency,
                "description": request.description,
                "raw_input": f"{request.merchant} {request.amount} {request.currency}",
            }
            transaction = service._enrich_transaction(
                parsed=parsed,
                user_id=current_user.id,
                account_id=request.account_id,
                source_type="api_structured",
            )
        
        return TransactionIntelligenceResponse(**transaction)
    
    except Exception as e:
        logger.error(f"Transaction processing error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Transaction processing failed: {str(e)}",
        )


@router.post("/intelligence/process-ocr", response_model=OCRUploadResponse)
async def process_ocr_image(
    account_id: int = Form(...),
    description: str = Form(None),
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    service: TransactionIntelligenceService = Depends(get_intelligence_service),
):
    """
    Upload and process image (receipt, bank notification).
    
    Supports: PNG, JPG, PDF screenshots
    
    Returns:
    - Extracted text from OCR
    - Processed transaction with classification
    """
    # Verify account belongs to user
    account = db.query(Account).filter(
        (Account.id == account_id) & (Account.user_id == current_user.id)
    ).first()
    
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Account not found",
        )
    
    # Check file size (max 10MB)
    file_size = len(await file.read())
    await file.seek(0)
    
    if file_size > 10 * 1024 * 1024:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="File too large (max 10MB)",
        )
    
    try:
        # Read file bytes
        image_bytes = await file.read()
        
        # Process through OCR and intelligence pipeline
        transaction = service.process_bytes_input(
            image_bytes=image_bytes,
            user_id=current_user.id,
            account_id=account_id,
            source_type="ocr_upload",
        )
        
        return OCRUploadResponse(
            extracted_text=transaction.get("metadata", {}).get("raw_extracted_text", ""),
            transaction=TransactionIntelligenceResponse(**transaction),
        )
    
    except Exception as e:
        logger.error(f"OCR processing error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"OCR processing failed: {str(e)}",
        )


@router.post("/intelligence/classify", response_model=ClassificationResult)
async def classify_transaction(
    merchant: str,
    amount: float,
    currency: str = "USD",
    description: str = None,
    current_user: User = Depends(get_current_user),
    service: TransactionIntelligenceService = Depends(get_intelligence_service),
):
    """
    Classify transaction using AI (Gemini + Rule-based fallback).
    
    Returns:
    - Category (food, transport, etc.)
    - Confidence score
    - Classification reasoning
    """
    try:
        result = service._classify_transaction(
            merchant=merchant,
            amount=amount,
            currency=currency,
            description=description,
        )
        
        return ClassificationResult(**result)
    
    except Exception as e:
        logger.error(f"Classification error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Classification failed: {str(e)}",
        )


@router.post("/intelligence/recurring", response_model=RecurringPatternResult)
async def detect_recurring_pattern(
    account_id: int,
    merchant: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    service: TransactionIntelligenceService = Depends(get_intelligence_service),
):
    """
    Detect recurring payment pattern for a merchant.
    
    Returns:
    - Is recurring (true/false)
    - Pattern (daily, weekly, monthly, etc.)
    - Confidence score
    """
    # Verify account belongs to user
    account = db.query(Account).filter(
        (Account.id == account_id) & (Account.user_id == current_user.id)
    ).first()
    
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Account not found",
        )
    
    try:
        # Get recent transactions for this merchant
        recent_transactions = db.query(Transaction).filter(
            (Transaction.user_id == current_user.id) &
            (Transaction.account_id == account_id) &
            (Transaction.merchant.ilike(f"%{merchant}%"))
        ).order_by(Transaction.transaction_date.desc()).limit(12).all()
        
        if len(recent_transactions) < 2:
            return RecurringPatternResult(
                is_recurring=False,
                pattern="insufficient_data",
                average_interval=None,
                occurrences=len(recent_transactions),
                confidence=0.0,
            )
        
        # Convert to dicts
        txn_dicts = [
            {
                "id": t.id,
                "amount": float(t.amount),
                "merchant": t.merchant,
                "date": t.transaction_date,
            }
            for t in recent_transactions
        ]
        
        is_recurring, pattern, metadata = service.check_recurring(txn_dicts, merchant)
        
        return RecurringPatternResult(
            is_recurring=is_recurring,
            pattern=pattern,
            average_interval=metadata.get("average_interval"),
            occurrences=metadata.get("occurrences", 0),
            confidence=metadata.get("confidence", 0.0),
        )
    
    except Exception as e:
        logger.error(f"Recurring detection error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Recurring detection failed: {str(e)}",
        )


@router.post("/intelligence/anomaly", response_model=AnomalyDetectionResult)
async def detect_anomaly(
    account_id: int,
    amount: float,
    merchant: str,
    category: str = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    service: TransactionIntelligenceService = Depends(get_intelligence_service),
):
    """
    Detect if transaction is anomalous based on historical data.
    
    Returns:
    - Is anomaly (true/false)
    - Anomaly score (0-1)
    - Z-score
    """
    # Verify account belongs to user
    account = db.query(Account).filter(
        (Account.id == account_id) & (Account.user_id == current_user.id)
    ).first()
    
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Account not found",
        )
    
    try:
        # Get historical transactions
        historical = db.query(Transaction).filter(
            (Transaction.user_id == current_user.id) &
            (Transaction.account_id == account_id)
        ).order_by(Transaction.transaction_date.desc()).limit(100).all()
        
        if len(historical) < 10:
            return AnomalyDetectionResult(
                is_anomaly=False,
                anomaly_score=0.0,
                z_score=None,
            )
        
        # Convert to dicts
        historical_dicts = [
            {
                "amount": float(t.amount),
                "merchant": t.merchant,
                "category": t.category_id,  # Will be enhanced in real version
            }
            for t in historical
        ]
        
        transaction = {
            "amount": amount,
            "merchant": merchant,
            "category": category,
        }
        
        is_anomaly, anomaly_score = service.check_anomaly(transaction, historical_dicts)
        
        return AnomalyDetectionResult(
            is_anomaly=is_anomaly,
            anomaly_score=anomaly_score,
        )
    
    except Exception as e:
        logger.error(f"Anomaly detection error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Anomaly detection failed: {str(e)}",
        )


@router.get("/intelligence/health")
async def health_check():
    """Check if transaction intelligence service is healthy."""
    return {
        "status": "healthy",
        "service": "transaction_intelligence",
        "features": [
            "ocr",
            "text_extraction",
            "classification",
            "recurring_detection",
            "anomaly_detection",
            "duplicate_detection",
        ]
    }
