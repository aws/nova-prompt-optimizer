"""
API endpoints for performance monitoring and metrics.
"""
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Query, HTTPException
from pydantic import BaseModel

from ..core.monitoring import performance_monitor, alert_manager

router = APIRouter(prefix="/monitoring", tags=["monitoring"])


class MetricsQuery(BaseModel):
    """Query parameters for metrics retrieval."""
    operation: Optional[str] = None
    since_hours: Optional[int] = Query(default=24, ge=1, le=168)  # 1 hour to 1 week
    limit: Optional[int] = Query(default=100, ge=1, le=1000)


class SystemMetricsQuery(BaseModel):
    """Query parameters for system metrics retrieval."""
    since_hours: Optional[int] = Query(default=24, ge=1, le=168)
    limit: Optional[int] = Query(default=100, ge=1, le=1000)


class AlertThresholds(BaseModel):
    """Alert threshold configuration."""
    cpu_percent: Optional[float] = None
    memory_percent: Optional[float] = None
    disk_usage_percent: Optional[float] = None
    operation_duration_ms: Optional[float] = None
    memory_usage_mb: Optional[float] = None


@router.get("/metrics", response_model=List[Dict[str, Any]])
async def get_performance_metrics(
    operation: Optional[str] = Query(None, description="Filter by operation name"),
    since_hours: int = Query(24, ge=1, le=168, description="Hours to look back"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of metrics")
):
    """Get performance metrics with optional filtering."""
    since = datetime.utcnow() - timedelta(hours=since_hours)
    
    metrics = performance_monitor.get_metrics(
        operation=operation,
        since=since,
        limit=limit
    )
    
    return metrics


@router.get("/system-metrics", response_model=List[Dict[str, Any]])
async def get_system_metrics(
    since_hours: int = Query(24, ge=1, le=168, description="Hours to look back"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of metrics")
):
    """Get system performance metrics."""
    since = datetime.utcnow() - timedelta(hours=since_hours)
    
    metrics = performance_monitor.get_system_metrics(
        since=since,
        limit=limit
    )
    
    return metrics


@router.get("/summary", response_model=Dict[str, Any])
async def get_performance_summary(
    operation: Optional[str] = Query(None, description="Filter by operation name")
):
    """Get performance summary statistics."""
    summary = performance_monitor.get_performance_summary(operation=operation)
    return summary


@router.get("/operations", response_model=List[str])
async def get_monitored_operations():
    """Get list of all monitored operations."""
    operations = set()
    for metric in performance_monitor.metrics:
        operations.add(metric.operation)
    
    return sorted(list(operations))


@router.get("/health", response_model=Dict[str, Any])
async def get_system_health():
    """Get current system health status."""
    import psutil
    
    # Get latest system metrics
    if performance_monitor.system_metrics:
        latest_metrics = performance_monitor.system_metrics[-1]
        
        # Determine health status
        health_status = "healthy"
        issues = []
        
        if latest_metrics.cpu_percent > 80:
            health_status = "warning"
            issues.append(f"High CPU usage: {latest_metrics.cpu_percent:.1f}%")
        
        if latest_metrics.memory_percent > 85:
            health_status = "critical" if health_status != "critical" else health_status
            issues.append(f"High memory usage: {latest_metrics.memory_percent:.1f}%")
        
        if latest_metrics.disk_usage_percent > 90:
            health_status = "critical"
            issues.append(f"High disk usage: {latest_metrics.disk_usage_percent:.1f}%")
        
        return {
            "status": health_status,
            "timestamp": latest_metrics.timestamp.isoformat(),
            "metrics": latest_metrics.to_dict(),
            "issues": issues
        }
    else:
        # Fallback to current system stats
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        health_status = "healthy"
        issues = []
        
        if cpu_percent > 80:
            health_status = "warning"
            issues.append(f"High CPU usage: {cpu_percent:.1f}%")
        
        if memory.percent > 85:
            health_status = "critical" if health_status != "critical" else health_status
            issues.append(f"High memory usage: {memory.percent:.1f}%")
        
        if disk.percent > 90:
            health_status = "critical"
            issues.append(f"High disk usage: {disk.percent:.1f}%")
        
        return {
            "status": health_status,
            "timestamp": datetime.utcnow().isoformat(),
            "metrics": {
                "cpu_percent": cpu_percent,
                "memory_percent": memory.percent,
                "memory_available_mb": memory.available / (1024 * 1024),
                "disk_usage_percent": disk.percent
            },
            "issues": issues
        }


@router.get("/alerts/thresholds", response_model=Dict[str, float])
async def get_alert_thresholds():
    """Get current alert thresholds."""
    return alert_manager.alert_thresholds


@router.put("/alerts/thresholds")
async def update_alert_thresholds(thresholds: AlertThresholds):
    """Update alert thresholds."""
    updated_thresholds = {}
    
    if thresholds.cpu_percent is not None:
        if not 0 <= thresholds.cpu_percent <= 100:
            raise HTTPException(status_code=400, detail="CPU threshold must be between 0 and 100")
        alert_manager.alert_thresholds['cpu_percent'] = thresholds.cpu_percent
        updated_thresholds['cpu_percent'] = thresholds.cpu_percent
    
    if thresholds.memory_percent is not None:
        if not 0 <= thresholds.memory_percent <= 100:
            raise HTTPException(status_code=400, detail="Memory threshold must be between 0 and 100")
        alert_manager.alert_thresholds['memory_percent'] = thresholds.memory_percent
        updated_thresholds['memory_percent'] = thresholds.memory_percent
    
    if thresholds.disk_usage_percent is not None:
        if not 0 <= thresholds.disk_usage_percent <= 100:
            raise HTTPException(status_code=400, detail="Disk usage threshold must be between 0 and 100")
        alert_manager.alert_thresholds['disk_usage_percent'] = thresholds.disk_usage_percent
        updated_thresholds['disk_usage_percent'] = thresholds.disk_usage_percent
    
    if thresholds.operation_duration_ms is not None:
        if thresholds.operation_duration_ms < 0:
            raise HTTPException(status_code=400, detail="Operation duration threshold must be positive")
        alert_manager.alert_thresholds['operation_duration_ms'] = thresholds.operation_duration_ms
        updated_thresholds['operation_duration_ms'] = thresholds.operation_duration_ms
    
    if thresholds.memory_usage_mb is not None:
        if thresholds.memory_usage_mb < 0:
            raise HTTPException(status_code=400, detail="Memory usage threshold must be positive")
        alert_manager.alert_thresholds['memory_usage_mb'] = thresholds.memory_usage_mb
        updated_thresholds['memory_usage_mb'] = thresholds.memory_usage_mb
    
    return {
        "message": "Alert thresholds updated successfully",
        "updated_thresholds": updated_thresholds
    }


@router.get("/slow-operations", response_model=List[Dict[str, Any]])
async def get_slow_operations(
    threshold_ms: float = Query(5000, ge=100, description="Minimum duration in milliseconds"),
    since_hours: int = Query(24, ge=1, le=168, description="Hours to look back"),
    limit: int = Query(50, ge=1, le=500, description="Maximum number of operations")
):
    """Get slow operations above the specified threshold."""
    since = datetime.utcnow() - timedelta(hours=since_hours)
    
    slow_operations = []
    for metric in performance_monitor.metrics:
        if (metric.timestamp >= since and 
            metric.duration_ms >= threshold_ms):
            slow_operations.append(metric.to_dict())
    
    # Sort by duration (slowest first) and limit
    slow_operations = sorted(slow_operations, key=lambda x: x['duration_ms'], reverse=True)
    return slow_operations[:limit]


@router.get("/memory-intensive-operations", response_model=List[Dict[str, Any]])
async def get_memory_intensive_operations(
    threshold_mb: float = Query(100, ge=1, description="Minimum memory usage in MB"),
    since_hours: int = Query(24, ge=1, le=168, description="Hours to look back"),
    limit: int = Query(50, ge=1, le=500, description="Maximum number of operations")
):
    """Get memory-intensive operations above the specified threshold."""
    since = datetime.utcnow() - timedelta(hours=since_hours)
    
    memory_intensive = []
    for metric in performance_monitor.metrics:
        if (metric.timestamp >= since and 
            metric.memory_usage_mb >= threshold_mb):
            memory_intensive.append(metric.to_dict())
    
    # Sort by memory usage (highest first) and limit
    memory_intensive = sorted(memory_intensive, key=lambda x: x['memory_usage_mb'], reverse=True)
    return memory_intensive[:limit]


@router.post("/monitoring/start")
async def start_monitoring(interval_seconds: int = Query(30, ge=5, le=300)):
    """Start system metrics monitoring."""
    performance_monitor.start_monitoring(interval_seconds)
    return {"message": f"Monitoring started with {interval_seconds}s interval"}


@router.post("/monitoring/stop")
async def stop_monitoring():
    """Stop system metrics monitoring."""
    performance_monitor.stop_monitoring()
    return {"message": "Monitoring stopped"}


@router.get("/monitoring/status")
async def get_monitoring_status():
    """Get monitoring status."""
    return {
        "active": performance_monitor._monitoring_active,
        "total_metrics": len(performance_monitor.metrics),
        "total_system_metrics": len(performance_monitor.system_metrics),
        "oldest_metric": (
            performance_monitor.metrics[0].timestamp.isoformat() 
            if performance_monitor.metrics else None
        ),
        "newest_metric": (
            performance_monitor.metrics[-1].timestamp.isoformat() 
            if performance_monitor.metrics else None
        )
    }