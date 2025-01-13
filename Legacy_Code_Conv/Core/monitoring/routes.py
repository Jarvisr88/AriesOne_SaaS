"""
Monitoring routes module.
"""
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import JSONResponse
from typing import Optional, List, Dict
from datetime import datetime, timedelta
import json
from pathlib import Path
from .logger import Logger, LogEntry, PerformanceMetrics
from ..Config.config_manager import ConfigManager
from ..auth.login_form import LoginManager

router = APIRouter(prefix="/monitoring", tags=["monitoring"])
config_manager = ConfigManager("config")
logger = Logger(config_manager)

@router.get("/logs")
async def get_logs(
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    level: Optional[str] = None,
    user: Optional[str] = None,
    module: Optional[str] = None,
    limit: int = 100,
    current_user = Depends(LoginManager.check_admin_user)
) -> List[LogEntry]:
    """Get application logs with filtering."""
    logs = []
    log_dir = Path("logs")
    
    # Default to last 24 hours if no dates provided
    if not start_date:
        start_date = datetime.now() - timedelta(days=1)
    if not end_date:
        end_date = datetime.now()
    
    # Get log files in date range
    current_date = start_date
    while current_date <= end_date:
        log_file = log_dir / f'structured_{current_date.strftime("%Y%m%d")}.json'
        if log_file.exists():
            with open(log_file, 'r') as f:
                for line in f:
                    log_entry = LogEntry(**json.loads(line))
                    
                    # Apply filters
                    if level and log_entry.level != level.upper():
                        continue
                    if user and log_entry.user != user:
                        continue
                    if module and log_entry.module != module:
                        continue
                    
                    logs.append(log_entry)
                    
                    if len(logs) >= limit:
                        break
                        
            if len(logs) >= limit:
                break
                
        current_date += timedelta(days=1)
    
    return logs

@router.get("/metrics")
async def get_metrics(
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    endpoint: Optional[str] = None,
    method: Optional[str] = None,
    status_code: Optional[int] = None,
    user: Optional[str] = None,
    limit: int = 100,
    current_user = Depends(LoginManager.check_admin_user)
) -> List[PerformanceMetrics]:
    """Get performance metrics with filtering."""
    metrics = []
    metrics_dir = Path("metrics")
    
    # Default to last 24 hours if no dates provided
    if not start_date:
        start_date = datetime.now() - timedelta(days=1)
    if not end_date:
        end_date = datetime.now()
    
    # Get metrics files in date range
    current_date = start_date
    while current_date <= end_date:
        metrics_file = metrics_dir / f'metrics_{current_date.strftime("%Y%m%d")}.json'
        if metrics_file.exists():
            with open(metrics_file, 'r') as f:
                for line in f:
                    metric = PerformanceMetrics(**json.loads(line))
                    
                    # Apply filters
                    if endpoint and metric.endpoint != endpoint:
                        continue
                    if method and metric.method != method:
                        continue
                    if status_code and metric.status_code != status_code:
                        continue
                    if user and metric.user != user:
                        continue
                    
                    metrics.append(metric)
                    
                    if len(metrics) >= limit:
                        break
                        
            if len(metrics) >= limit:
                break
                
        current_date += timedelta(days=1)
    
    return metrics

@router.get("/summary")
async def get_monitoring_summary(
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    current_user = Depends(LoginManager.check_admin_user)
) -> Dict:
    """Get monitoring summary statistics."""
    # Default to last 24 hours if no dates provided
    if not start_date:
        start_date = datetime.now() - timedelta(days=1)
    if not end_date:
        end_date = datetime.now()
    
    # Get metrics
    metrics = await get_metrics(
        start_date=start_date,
        end_date=end_date,
        limit=10000
    )
    
    # Get logs
    logs = await get_logs(
        start_date=start_date,
        end_date=end_date,
        limit=10000
    )
    
    # Calculate metrics summary
    total_requests = len(metrics)
    avg_duration = sum(m.duration for m in metrics) / total_requests if total_requests > 0 else 0
    error_count = sum(1 for m in metrics if m.status_code >= 400)
    
    # Calculate logs summary
    error_logs = sum(1 for log in logs if log.level in ['ERROR', 'CRITICAL'])
    warning_logs = sum(1 for log in logs if log.level == 'WARNING')
    
    # Get top endpoints
    endpoint_stats = {}
    for metric in metrics:
        if metric.endpoint not in endpoint_stats:
            endpoint_stats[metric.endpoint] = {
                'count': 0,
                'total_duration': 0,
                'error_count': 0
            }
        stats = endpoint_stats[metric.endpoint]
        stats['count'] += 1
        stats['total_duration'] += metric.duration
        if metric.status_code >= 400:
            stats['error_count'] += 1
    
    top_endpoints = sorted(
        [
            {
                'endpoint': endpoint,
                'count': stats['count'],
                'avg_duration': stats['total_duration'] / stats['count'],
                'error_rate': stats['error_count'] / stats['count'] * 100
            }
            for endpoint, stats in endpoint_stats.items()
        ],
        key=lambda x: x['count'],
        reverse=True
    )[:5]
    
    return {
        'period': {
            'start': start_date.isoformat(),
            'end': end_date.isoformat()
        },
        'requests': {
            'total': total_requests,
            'avg_duration': avg_duration,
            'error_count': error_count,
            'error_rate': error_count / total_requests * 100 if total_requests > 0 else 0
        },
        'logs': {
            'total': len(logs),
            'error_count': error_logs,
            'warning_count': warning_logs
        },
        'top_endpoints': top_endpoints
    }
