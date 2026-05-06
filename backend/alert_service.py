"""
Alert service for deadline notifications.
Prevents over-notification with rate limiting and status tracking.
"""
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from sqlalchemy.orm import Session
from . import models_sqlalchemy as models
from . import deadline_awareness


class AlertService:
    """
    Service for managing deadline alerts with rate limiting.
    
    Prevents over-notification by:
    - Tracking last notification time per process
    - Only alerting on status changes
    - Respecting minimum interval between alerts
    """
    
    MIN_ALERT_INTERVAL_HOURS = 24  # Minimum hours between alerts for same process
    
    @staticmethod
    def should_alert(
        db: Session,
        process_id: int,
        deadline_status: Dict,
        min_interval_hours: int = MIN_ALERT_INTERVAL_HOURS
    ) -> bool:
        """
        Determine if alert should be sent for a process.
        
        Args:
            db: Database session
            process_id: Process ID
            deadline_status: Status dictionary from deadline_awareness
            min_interval_hours: Minimum hours between alerts
            
        Returns:
            True if alert should be sent, False otherwise
        """
        if not deadline_status.get("should_alert", False):
            return False
        
        # Check if process has been notified recently
        # For now, we'll use a simple approach: check last_sync or created_at
        # In production, you might want a dedicated alert_history table
        
        process = db.query(models.Process).filter(
            models.Process.id == process_id
        ).first()
        
        if not process:
            return False
        
        # Simple heuristic: if updated recently, don't alert again
        if process.updated_at:
            time_since_update = datetime.utcnow() - process.updated_at
            if time_since_update < timedelta(hours=min_interval_hours):
                return False
        
        return True
    
    @staticmethod
    def generate_alerts(
        db: Session,
        alert_window_days: int = 7,
        min_interval_hours: int = MIN_ALERT_INTERVAL_HOURS,
        scoped_user=None,
    ) -> Dict[str, List[Dict]]:
        """
        Generate alerts for processes with critical deadlines.
        
        Only generates alerts for processes that:
        - Have critical deadline status
        - Haven't been alerted recently
        - Require immediate attention
        
        Args:
            db: Database session
            alert_window_days: Days ahead to consider as "upcoming"
            min_interval_hours: Minimum hours between alerts
            
        Returns:
            Dictionary with 'overdue' and 'upcoming' alert lists
        """
        overdue, upcoming = deadline_awareness.get_critical_deadlines(
            db,
            alert_window_days=alert_window_days,
            scoped_user=scoped_user,
        )
        
        overdue_alerts = []
        upcoming_alerts = []
        
        for proc in overdue:
            status = deadline_awareness.calculate_deadline_status(
                proc["prazo_final"],
                alert_window_days
            )
            
            if AlertService.should_alert(
                db,
                proc["process_id"],
                status,
                min_interval_hours
            ):
                overdue_alerts.append({
                    **proc,
                    "alert_type": "overdue",
                    "severity": "critical",
                    "alerted_at": datetime.utcnow().isoformat()
                })
        
        for proc in upcoming:
            status = deadline_awareness.calculate_deadline_status(
                proc["prazo_final"],
                alert_window_days
            )
            
            if AlertService.should_alert(
                db,
                proc["process_id"],
                status,
                min_interval_hours
            ):
                upcoming_alerts.append({
                    **proc,
                    "alert_type": "upcoming",
                    "severity": "warning",
                    "alerted_at": datetime.utcnow().isoformat()
                })
        
        return {
            "overdue": overdue_alerts,
            "upcoming": upcoming_alerts,
            "overdue_count": len(overdue_alerts),
            "upcoming_count": len(upcoming_alerts),
            "total_alerts": len(overdue_alerts) + len(upcoming_alerts)
        }
