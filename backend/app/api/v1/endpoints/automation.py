"""API Endpoints for Automation & Proactive Intelligence

Endpoints for:
- Financial reports (GET, list, download PDF)
- Alerts (GET, acknowledge)
- Notification preferences (GET, update)
- Automation rules (GET, create, update, delete)
"""

import logging
from typing import List, Optional
from datetime import datetime, timedelta

from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.orm import Session

from app.db.base import SessionLocal, get_db
from app.models.database import (
    FinancialReport,
    FinancialAlert,
    UserNotificationPreference,
    AutomationRule,
    Notification,
    TelegramUserMapping,
)
from app.schemas.base import BaseResponse
from pydantic import BaseModel

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/automation", tags=["automation"])


# ============================================================================
# SCHEMAS
# ============================================================================

class ReportSummary(BaseModel):
    """Financial report summary."""
    report_id: str
    period_start: datetime
    period_end: datetime
    report_period: str
    confidence: float
    health_score: Optional[float]
    weekly_spending: Optional[float]
    created_at: datetime

    class Config:
        from_attributes = True


class AlertSummary(BaseModel):
    """Financial alert summary."""
    id: int
    alert_type: str
    severity: str
    title: str
    message: str
    confidence: float
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class NotificationPreferenceUpdate(BaseModel):
    """Update notification preferences."""
    notifications_enabled: Optional[bool] = None
    min_confidence: Optional[float] = None
    digest_frequency: Optional[str] = None
    quiet_hours_enabled: Optional[bool] = None
    quiet_hours_start: Optional[str] = None
    quiet_hours_end: Optional[str] = None


class AutomationRuleCreate(BaseModel):
    """Create automation rule."""
    name: str
    description: Optional[str] = None
    condition_type: str
    condition_value: dict
    action_type: str
    action_value: dict


class AutomationRuleUpdate(BaseModel):
    """Update automation rule."""
    name: Optional[str] = None
    description: Optional[str] = None
    condition_value: Optional[dict] = None
    action_value: Optional[dict] = None
    is_active: Optional[bool] = None


# ============================================================================
# REPORT ENDPOINTS
# ============================================================================

@router.get("/reports", response_model=List[ReportSummary])
async def get_reports(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    period: Optional[str] = Query(None),  # "weekly", "monthly"
    db: Session = Depends(get_db),
    current_user_id: int = 1,  # In production: from auth
) -> List[ReportSummary]:
    """
    Get user's financial reports.
    
    Parameters:
    - skip: Number of reports to skip
    - limit: Number of reports to return
    - period: Filter by report period ("weekly", "monthly")
    """
    try:
        query = db.query(FinancialReport).filter(
            FinancialReport.user_id == current_user_id
        )
        
        if period:
            query = query.filter(FinancialReport.report_period == period)
        
        reports = query.order_by(
            FinancialReport.period_end.desc()
        ).offset(skip).limit(limit).all()
        
        return reports
    except Exception as e:
        logger.error(f"Error getting reports: {e}")
        raise HTTPException(status_code=500, detail="Error retrieving reports")


@router.get("/reports/{report_id}")
async def get_report(
    report_id: str,
    db: Session = Depends(get_db),
    current_user_id: int = 1,
):
    """Get detailed financial report."""
    try:
        report = db.query(FinancialReport).filter(
            FinancialReport.report_id == report_id,
            FinancialReport.user_id == current_user_id,
        ).first()
        
        if not report:
            raise HTTPException(status_code=404, detail="Report not found")
        
        # Mark as viewed
        report.viewed_at = datetime.now()
        db.commit()
        
        # Return full report
        return {
            "report_id": report.report_id,
            "period": f"{report.period_start.date()} to {report.period_end.date()}",
            "summary": report.summary,
            "key_metrics": report.key_metrics,
            "spending_analysis": report.spending_analysis,
            "income_analysis": report.income_analysis,
            "trend_analysis": report.trend_analysis,
            "health_analysis": report.health_analysis,
            "recommendations": report.recommendations,
            "charts": report.charts,
            "confidence": report.confidence,
            "generated_at": report.generated_at,
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting report {report_id}: {e}")
        raise HTTPException(status_code=500, detail="Error retrieving report")


@router.get("/reports/{report_id}/pdf")
async def download_report_pdf(
    report_id: str,
    db: Session = Depends(get_db),
    current_user_id: int = 1,
):
    """Download report as PDF."""
    try:
        report = db.query(FinancialReport).filter(
            FinancialReport.report_id == report_id,
            FinancialReport.user_id == current_user_id,
        ).first()
        
        if not report:
            raise HTTPException(status_code=404, detail="Report not found")
        
        if not report.pdf_path:
            raise HTTPException(status_code=404, detail="PDF not generated yet")
        
        # In production: return file from storage
        return {"message": "PDF download would be implemented"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error downloading PDF: {e}")
        raise HTTPException(status_code=500, detail="Error downloading PDF")


# ============================================================================
# ALERTS ENDPOINTS
# ============================================================================

@router.get("/alerts", response_model=List[AlertSummary])
async def get_alerts(
    severity: Optional[str] = Query(None),  # "info", "warning", "critical"
    active_only: bool = Query(True),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user_id: int = 1,
) -> List[AlertSummary]:
    """
    Get user's active financial alerts.
    
    Parameters:
    - severity: Filter by severity
    - active_only: Only return active alerts
    - skip: Number of alerts to skip
    - limit: Number of alerts to return
    """
    try:
        query = db.query(FinancialAlert).filter(
            FinancialAlert.user_id == current_user_id
        )
        
        if active_only:
            query = query.filter(FinancialAlert.is_active == True)
        
        if severity:
            query = query.filter(FinancialAlert.severity == severity)
        
        alerts = query.order_by(
            FinancialAlert.created_at.desc()
        ).offset(skip).limit(limit).all()
        
        return alerts
    except Exception as e:
        logger.error(f"Error getting alerts: {e}")
        raise HTTPException(status_code=500, detail="Error retrieving alerts")


@router.post("/alerts/{alert_id}/acknowledge")
async def acknowledge_alert(
    alert_id: int,
    db: Session = Depends(get_db),
    current_user_id: int = 1,
):
    """Acknowledge an alert."""
    try:
        alert = db.query(FinancialAlert).filter(
            FinancialAlert.id == alert_id,
            FinancialAlert.user_id == current_user_id,
        ).first()
        
        if not alert:
            raise HTTPException(status_code=404, detail="Alert not found")
        
        alert.acknowledged_at = datetime.now()
        alert.acknowledged_by_user = True
        db.commit()
        
        return {"status": "acknowledged", "alert_id": alert_id}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error acknowledging alert: {e}")
        raise HTTPException(status_code=500, detail="Error acknowledging alert")


@router.get("/alerts/summary")
async def get_alerts_summary(
    db: Session = Depends(get_db),
    current_user_id: int = 1,
):
    """Get alerts summary (counts by severity)."""
    try:
        total = db.query(FinancialAlert).filter(
            FinancialAlert.user_id == current_user_id,
            FinancialAlert.is_active == True,
        ).count()
        
        critical = db.query(FinancialAlert).filter(
            FinancialAlert.user_id == current_user_id,
            FinancialAlert.is_active == True,
            FinancialAlert.severity == "critical",
        ).count()
        
        warning = db.query(FinancialAlert).filter(
            FinancialAlert.user_id == current_user_id,
            FinancialAlert.is_active == True,
            FinancialAlert.severity == "warning",
        ).count()
        
        info = db.query(FinancialAlert).filter(
            FinancialAlert.user_id == current_user_id,
            FinancialAlert.is_active == True,
            FinancialAlert.severity == "info",
        ).count()
        
        return {
            "total": total,
            "critical": critical,
            "warning": warning,
            "info": info,
            "requires_attention": critical + warning,
        }
    except Exception as e:
        logger.error(f"Error getting alerts summary: {e}")
        raise HTTPException(status_code=500, detail="Error retrieving alerts summary")


# ============================================================================
# NOTIFICATION PREFERENCES ENDPOINTS
# ============================================================================

@router.get("/preferences")
async def get_notification_preferences(
    db: Session = Depends(get_db),
    current_user_id: int = 1,
):
    """Get user's notification preferences."""
    try:
        pref = db.query(UserNotificationPreference).filter(
            UserNotificationPreference.user_id == current_user_id
        ).first()
        
        if not pref:
            # Return defaults
            return {
                "notifications_enabled": True,
                "min_confidence": 0.5,
                "digest_frequency": "daily",
                "quiet_hours_enabled": False,
                "alert_types": {
                    "spending_spike": True,
                    "burn_rate_warning": True,
                    "subscription_waste": True,
                    "savings_opportunity": True,
                    "behavioral_anomaly": True,
                    "low_runway": True,
                },
                "channels": {
                    "telegram": True,
                    "email": False,
                    "in_app": True,
                },
            }
        
        return {
            "notifications_enabled": pref.notifications_enabled,
            "min_confidence": pref.min_confidence,
            "digest_frequency": pref.digest_frequency,
            "quiet_hours_enabled": pref.quiet_hours_enabled,
            "quiet_hours_start": pref.quiet_hours_start,
            "quiet_hours_end": pref.quiet_hours_end,
            "alert_types": pref.alert_types,
            "channels": pref.channels,
        }
    except Exception as e:
        logger.error(f"Error getting preferences: {e}")
        raise HTTPException(status_code=500, detail="Error retrieving preferences")


@router.put("/preferences")
async def update_notification_preferences(
    update: NotificationPreferenceUpdate,
    db: Session = Depends(get_db),
    current_user_id: int = 1,
):
    """Update user's notification preferences."""
    try:
        pref = db.query(UserNotificationPreference).filter(
            UserNotificationPreference.user_id == current_user_id
        ).first()
        
        if not pref:
            pref = UserNotificationPreference(user_id=current_user_id)
            db.add(pref)
        
        # Update fields
        if update.notifications_enabled is not None:
            pref.notifications_enabled = update.notifications_enabled
        if update.min_confidence is not None:
            pref.min_confidence = update.min_confidence
        if update.digest_frequency is not None:
            pref.digest_frequency = update.digest_frequency
        if update.quiet_hours_enabled is not None:
            pref.quiet_hours_enabled = update.quiet_hours_enabled
        if update.quiet_hours_start is not None:
            pref.quiet_hours_start = update.quiet_hours_start
        if update.quiet_hours_end is not None:
            pref.quiet_hours_end = update.quiet_hours_end
        
        db.commit()
        
        return {"status": "updated", "message": "Preferences updated successfully"}
    except Exception as e:
        logger.error(f"Error updating preferences: {e}")
        raise HTTPException(status_code=500, detail="Error updating preferences")


# ============================================================================
# AUTOMATION RULES ENDPOINTS
# ============================================================================

@router.get("/rules")
async def get_automation_rules(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user_id: int = 1,
) -> List[dict]:
    """Get user's automation rules."""
    try:
        rules = db.query(AutomationRule).filter(
            AutomationRule.user_id == current_user_id
        ).offset(skip).limit(limit).all()
        
        return [
            {
                "id": r.id,
                "name": r.name,
                "description": r.description,
                "condition_type": r.condition_type,
                "action_type": r.action_type,
                "is_active": r.is_active,
                "last_triggered_at": r.last_triggered_at,
                "trigger_count": r.trigger_count,
            }
            for r in rules
        ]
    except Exception as e:
        logger.error(f"Error getting automation rules: {e}")
        raise HTTPException(status_code=500, detail="Error retrieving rules")


@router.post("/rules")
async def create_automation_rule(
    rule: AutomationRuleCreate,
    db: Session = Depends(get_db),
    current_user_id: int = 1,
):
    """Create a new automation rule."""
    try:
        new_rule = AutomationRule(
            user_id=current_user_id,
            name=rule.name,
            description=rule.description,
            condition_type=rule.condition_type,
            condition_value=rule.condition_value,
            action_type=rule.action_type,
            action_value=rule.action_value,
        )
        
        db.add(new_rule)
        db.commit()
        db.refresh(new_rule)
        
        return {
            "id": new_rule.id,
            "name": new_rule.name,
            "status": "created",
        }
    except Exception as e:
        logger.error(f"Error creating automation rule: {e}")
        raise HTTPException(status_code=500, detail="Error creating rule")


@router.put("/rules/{rule_id}")
async def update_automation_rule(
    rule_id: int,
    update: AutomationRuleUpdate,
    db: Session = Depends(get_db),
    current_user_id: int = 1,
):
    """Update an automation rule."""
    try:
        rule = db.query(AutomationRule).filter(
            AutomationRule.id == rule_id,
            AutomationRule.user_id == current_user_id,
        ).first()
        
        if not rule:
            raise HTTPException(status_code=404, detail="Rule not found")
        
        if update.name is not None:
            rule.name = update.name
        if update.description is not None:
            rule.description = update.description
        if update.condition_value is not None:
            rule.condition_value = update.condition_value
        if update.action_value is not None:
            rule.action_value = update.action_value
        if update.is_active is not None:
            rule.is_active = update.is_active
        
        db.commit()
        
        return {"status": "updated", "rule_id": rule_id}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating automation rule: {e}")
        raise HTTPException(status_code=500, detail="Error updating rule")


@router.delete("/rules/{rule_id}")
async def delete_automation_rule(
    rule_id: int,
    db: Session = Depends(get_db),
    current_user_id: int = 1,
):
    """Delete an automation rule."""
    try:
        rule = db.query(AutomationRule).filter(
            AutomationRule.id == rule_id,
            AutomationRule.user_id == current_user_id,
        ).first()
        
        if not rule:
            raise HTTPException(status_code=404, detail="Rule not found")
        
        db.delete(rule)
        db.commit()
        
        return {"status": "deleted", "rule_id": rule_id}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting automation rule: {e}")
        raise HTTPException(status_code=500, detail="Error deleting rule")


# ============================================================================
# DASHBOARD ENDPOINTS
# ============================================================================

@router.get("/dashboard")
async def get_automation_dashboard(
    db: Session = Depends(get_db),
    current_user_id: int = 1,
):
    """Get automation dashboard summary."""
    try:
        # Recent alerts
        recent_alerts = db.query(FinancialAlert).filter(
            FinancialAlert.user_id == current_user_id,
            FinancialAlert.is_active == True,
        ).order_by(FinancialAlert.created_at.desc()).limit(5).all()
        
        # Recent reports
        recent_reports = db.query(FinancialReport).filter(
            FinancialReport.user_id == current_user_id,
        ).order_by(FinancialReport.generated_at.desc()).limit(3).all()
        
        # Active notifications
        notifications = db.query(Notification).filter(
            Notification.user_id == current_user_id,
            Notification.status.in_(["pending", "sent"]),
        ).limit(5).all()
        
        # Alert counts
        alert_count = db.query(FinancialAlert).filter(
            FinancialAlert.user_id == current_user_id,
            FinancialAlert.is_active == True,
        ).count()
        
        return {
            "recent_alerts": [
                {
                    "alert_type": a.alert_type,
                    "severity": a.severity,
                    "title": a.title,
                    "created_at": a.created_at,
                }
                for a in recent_alerts
            ],
            "recent_reports": [
                {
                    "report_id": r.report_id,
                    "period": f"{r.period_start.date()} to {r.period_end.date()}",
                    "generated_at": r.generated_at,
                }
                for r in recent_reports
            ],
            "active_alerts_count": alert_count,
            "pending_notifications": len([n for n in notifications if n.status == "pending"]),
            "unviewed_reports": len([r for r in recent_reports if r.viewed_at is None]),
        }
    except Exception as e:
        logger.error(f"Error getting dashboard: {e}")
        raise HTTPException(status_code=500, detail="Error retrieving dashboard")
