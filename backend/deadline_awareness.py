"""
Deadline awareness and alert system.
Detects overdue and upcoming deadlines with configurable windows.
"""
from datetime import date, timedelta
from typing import Dict, List, Optional, Tuple
from sqlalchemy.orm import Session
from . import models_sqlalchemy as models


def parse_prazo_final(prazo_str: Optional[str]) -> Optional[date]:
    """
    Parse prazo_final string (DD/MM) to date object.
    
    Args:
        prazo_str: String in format "DD/MM" (e.g., "16/02")
        
    Returns:
        Date object for the current or next year, or None if invalid
    """
    if not prazo_str or not prazo_str.strip():
        return None
    
    try:
        parts = prazo_str.strip().split('/')
        if len(parts) != 2:
            return None
        
        day = int(parts[0])
        month = int(parts[1])
        
        if day < 1 or day > 31 or month < 1 or month > 12:
            return None
        
        today = date.today()
        prazo_date = date(today.year, month, day)
        
        if prazo_date < today:
            prazo_date = date(today.year + 1, month, day)
        
        return prazo_date
    except (ValueError, IndexError):
        return None


def calculate_deadline_status(
    prazo_final: Optional[str],
    alert_window_days: int = 7
) -> Dict[str, any]:
    """
    Calculate deadline status for a process.
    
    Args:
        prazo_final: String in format "DD/MM"
        alert_window_days: Days ahead to consider as "upcoming" (default: 7)
        
    Returns:
        Dictionary with:
        - status: 'overdue', 'upcoming', 'ok', 'none'
        - days_until: Days until deadline (negative if overdue)
        - should_alert: Whether to generate alert
        - severity: 'critical', 'warning', 'info', 'none'
    """
    if not prazo_final:
        return {
            "status": "none",
            "days_until": None,
            "should_alert": False,
            "severity": "none"
        }
    
    prazo_date = parse_prazo_final(prazo_final)
    if not prazo_date:
        return {
            "status": "none",
            "days_until": None,
            "should_alert": False,
            "severity": "none"
        }
    
    today = date.today()
    days_until = (prazo_date - today).days
    
    if days_until < 0:
        return {
            "status": "overdue",
            "days_until": days_until,
            "should_alert": True,
            "severity": "critical",
            "prazo_date": prazo_date
        }
    elif days_until <= alert_window_days:
        return {
            "status": "upcoming",
            "days_until": days_until,
            "should_alert": days_until <= 3,  # Alert only if 3 days or less
            "severity": "warning" if days_until <= 3 else "info",
            "prazo_date": prazo_date
        }
    else:
        return {
            "status": "ok",
            "days_until": days_until,
            "should_alert": False,
            "severity": "none",
            "prazo_date": prazo_date
        }


def get_processes_with_deadline_status(
    db: Session,
    alert_window_days: int = 7,
    include_ok: bool = False
) -> List[Dict]:
    """
    Get all processes with deadline status calculated.
    
    Args:
        db: Database session
        alert_window_days: Days ahead to consider as "upcoming"
        include_ok: Whether to include processes with OK status
        
    Returns:
        List of processes with deadline_status added
    """
    processes = db.query(models.Process).all()
    
    result = []
    for proc in processes:
        status = calculate_deadline_status(proc.prazo_final, alert_window_days)
        
        if not include_ok and status["status"] == "ok":
            continue
        
        proc_dict = {
            "id": proc.id,
            "protocol_number": proc.protocol_number,
            "processo_adm_1doc": proc.processo_adm_1doc,
            "processo_judicial": proc.processo_judicial,
            "prazo_final": proc.prazo_final,
            "deadline_status": status
        }
        result.append(proc_dict)
    
    return result


def get_critical_deadlines(
    db: Session,
    alert_window_days: int = 7
) -> Tuple[List[Dict], List[Dict]]:
    """
    Get overdue and upcoming deadlines that require attention.
    
    Args:
        db: Database session
        alert_window_days: Days ahead to consider as "upcoming"
        
    Returns:
        Tuple of (overdue_list, upcoming_list)
    """
    overdue = []
    upcoming = []
    
    processes = db.query(models.Process).filter(
        models.Process.prazo_final.isnot(None)
    ).all()
    
    for proc in processes:
        status = calculate_deadline_status(proc.prazo_final, alert_window_days)
        
        if status["status"] == "overdue":
            overdue.append({
                "process_id": proc.id,
                "protocol_number": proc.protocol_number,
                "processo_adm_1doc": proc.processo_adm_1doc,
                "processo_judicial": proc.processo_judicial,
                "prazo_final": proc.prazo_final,
                "days_overdue": abs(status["days_until"]),
                "prazo_date": status.get("prazo_date")
            })
        elif status["status"] == "upcoming" and status["should_alert"]:
            upcoming.append({
                "process_id": proc.id,
                "protocol_number": proc.protocol_number,
                "processo_adm_1doc": proc.processo_adm_1doc,
                "processo_judicial": proc.processo_judicial,
                "prazo_final": proc.prazo_final,
                "days_until": status["days_until"],
                "prazo_date": status.get("prazo_date")
            })
    
    return overdue, upcoming
