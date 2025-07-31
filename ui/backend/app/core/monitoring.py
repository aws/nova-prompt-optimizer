"""
Performance monitoring and metrics collection for the Nova Prompt Optimizer backend.
"""
import time
import psutil
import asyncio
from typing import Dict, Any, Optional, List
from functools import wraps
from contextlib import asynccontextmanager
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


@dataclass
class PerformanceMetrics:
    """Performance metrics data structure."""
    operation: str
    duration_ms: float
    memory_usage_mb: float
    cpu_percent: float
    timestamp: datetime
    metadata: Dict[str, Any]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        data = asdict(self)
        data['timestamp'] = self.timestamp.isoformat()
        return data


@dataclass
class SystemMetrics:
    """System-wide performance metrics."""
    cpu_percent: float
    memory_percent: float
    memory_available_mb: float
    disk_usage_percent: float
    active_connections: int
    timestamp: datetime
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        data = asdict(self)
        data['timestamp'] = self.timestamp.isoformat()
        return data


class PerformanceMonitor:
    """Performance monitoring and metrics collection."""
    
    def __init__(self, max_metrics: int = 10000):
        self.max_metrics = max_metrics
        self.metrics: List[PerformanceMetrics] = []
        self.system_metrics: List[SystemMetrics] = []
        self._monitoring_active = False
        self._monitoring_task: Optional[asyncio.Task] = None
        
    def start_monitoring(self, interval_seconds: int = 30):
        """Start system metrics monitoring."""
        if self._monitoring_active:
            return
            
        self._monitoring_active = True
        self._monitoring_task = asyncio.create_task(
            self._collect_system_metrics(interval_seconds)
        )
        logger.info(f"Started performance monitoring with {interval_seconds}s interval")
    
    def stop_monitoring(self):
        """Stop system metrics monitoring."""
        self._monitoring_active = False
        if self._monitoring_task:
            self._monitoring_task.cancel()
        logger.info("Stopped performance monitoring")
    
    async def _collect_system_metrics(self, interval_seconds: int):
        """Collect system metrics periodically."""
        while self._monitoring_active:
            try:
                metrics = SystemMetrics(
                    cpu_percent=psutil.cpu_percent(interval=1),
                    memory_percent=psutil.virtual_memory().percent,
                    memory_available_mb=psutil.virtual_memory().available / (1024 * 1024),
                    disk_usage_percent=psutil.disk_usage('/').percent,
                    active_connections=len(psutil.net_connections()),
                    timestamp=datetime.utcnow()
                )
                
                self.system_metrics.append(metrics)
                
                # Keep only recent metrics
                if len(self.system_metrics) > self.max_metrics:
                    self.system_metrics = self.system_metrics[-self.max_metrics:]
                
                await asyncio.sleep(interval_seconds)
                
            except Exception as e:
                logger.error(f"Error collecting system metrics: {e}")
                await asyncio.sleep(interval_seconds)
    
    def record_operation(self, metrics: PerformanceMetrics):
        """Record performance metrics for an operation."""
        self.metrics.append(metrics)
        
        # Keep only recent metrics
        if len(self.metrics) > self.max_metrics:
            self.metrics = self.metrics[-self.max_metrics:]
        
        # Log slow operations
        if metrics.duration_ms > 5000:  # 5 seconds
            logger.warning(
                f"Slow operation detected: {metrics.operation} took {metrics.duration_ms:.2f}ms"
            )
    
    def get_metrics(
        self, 
        operation: Optional[str] = None,
        since: Optional[datetime] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Get performance metrics with optional filtering."""
        filtered_metrics = self.metrics
        
        if operation:
            filtered_metrics = [m for m in filtered_metrics if m.operation == operation]
        
        if since:
            filtered_metrics = [m for m in filtered_metrics if m.timestamp >= since]
        
        # Sort by timestamp (most recent first) and limit
        filtered_metrics = sorted(filtered_metrics, key=lambda x: x.timestamp, reverse=True)
        filtered_metrics = filtered_metrics[:limit]
        
        return [m.to_dict() for m in filtered_metrics]
    
    def get_system_metrics(
        self, 
        since: Optional[datetime] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Get system metrics with optional filtering."""
        filtered_metrics = self.system_metrics
        
        if since:
            filtered_metrics = [m for m in filtered_metrics if m.timestamp >= since]
        
        # Sort by timestamp (most recent first) and limit
        filtered_metrics = sorted(filtered_metrics, key=lambda x: x.timestamp, reverse=True)
        filtered_metrics = filtered_metrics[:limit]
        
        return [m.to_dict() for m in filtered_metrics]
    
    def get_performance_summary(self, operation: Optional[str] = None) -> Dict[str, Any]:
        """Get performance summary statistics."""
        filtered_metrics = self.metrics
        
        if operation:
            filtered_metrics = [m for m in filtered_metrics if m.operation == operation]
        
        if not filtered_metrics:
            return {"error": "No metrics found"}
        
        durations = [m.duration_ms for m in filtered_metrics]
        memory_usage = [m.memory_usage_mb for m in filtered_metrics]
        
        return {
            "operation": operation or "all",
            "total_operations": len(filtered_metrics),
            "duration_stats": {
                "min_ms": min(durations),
                "max_ms": max(durations),
                "avg_ms": sum(durations) / len(durations),
                "p95_ms": sorted(durations)[int(len(durations) * 0.95)] if len(durations) > 20 else max(durations)
            },
            "memory_stats": {
                "min_mb": min(memory_usage),
                "max_mb": max(memory_usage),
                "avg_mb": sum(memory_usage) / len(memory_usage)
            },
            "slow_operations": len([d for d in durations if d > 5000]),
            "time_range": {
                "start": min(m.timestamp for m in filtered_metrics).isoformat(),
                "end": max(m.timestamp for m in filtered_metrics).isoformat()
            }
        }


# Global performance monitor instance
performance_monitor = PerformanceMonitor()


def monitor_performance(operation_name: str, metadata: Optional[Dict[str, Any]] = None):
    """Decorator to monitor function performance."""
    def decorator(func):
        if asyncio.iscoroutinefunction(func):
            @wraps(func)
            async def async_wrapper(*args, **kwargs):
                start_time = time.time()
                process = psutil.Process()
                start_memory = process.memory_info().rss / (1024 * 1024)  # MB
                
                try:
                    result = await func(*args, **kwargs)
                    return result
                finally:
                    end_time = time.time()
                    end_memory = process.memory_info().rss / (1024 * 1024)  # MB
                    
                    metrics = PerformanceMetrics(
                        operation=operation_name,
                        duration_ms=(end_time - start_time) * 1000,
                        memory_usage_mb=end_memory - start_memory,
                        cpu_percent=process.cpu_percent(),
                        timestamp=datetime.utcnow(),
                        metadata=metadata or {}
                    )
                    
                    performance_monitor.record_operation(metrics)
            
            return async_wrapper
        else:
            @wraps(func)
            def sync_wrapper(*args, **kwargs):
                start_time = time.time()
                process = psutil.Process()
                start_memory = process.memory_info().rss / (1024 * 1024)  # MB
                
                try:
                    result = func(*args, **kwargs)
                    return result
                finally:
                    end_time = time.time()
                    end_memory = process.memory_info().rss / (1024 * 1024)  # MB
                    
                    metrics = PerformanceMetrics(
                        operation=operation_name,
                        duration_ms=(end_time - start_time) * 1000,
                        memory_usage_mb=end_memory - start_memory,
                        cpu_percent=process.cpu_percent(),
                        timestamp=datetime.utcnow(),
                        metadata=metadata or {}
                    )
                    
                    performance_monitor.record_operation(metrics)
            
            return sync_wrapper
    
    return decorator


@asynccontextmanager
async def performance_context(operation_name: str, metadata: Optional[Dict[str, Any]] = None):
    """Context manager for monitoring performance of code blocks."""
    start_time = time.time()
    process = psutil.Process()
    start_memory = process.memory_info().rss / (1024 * 1024)  # MB
    
    try:
        yield
    finally:
        end_time = time.time()
        end_memory = process.memory_info().rss / (1024 * 1024)  # MB
        
        metrics = PerformanceMetrics(
            operation=operation_name,
            duration_ms=(end_time - start_time) * 1000,
            memory_usage_mb=end_memory - start_memory,
            cpu_percent=process.cpu_percent(),
            timestamp=datetime.utcnow(),
            metadata=metadata or {}
        )
        
        performance_monitor.record_operation(metrics)


class MemoryOptimizer:
    """Memory optimization utilities."""
    
    @staticmethod
    def optimize_large_dataset_processing(chunk_size: int = 1000):
        """Decorator for processing large datasets in chunks."""
        def decorator(func):
            @wraps(func)
            async def wrapper(data, *args, **kwargs):
                if hasattr(data, '__len__') and len(data) > chunk_size:
                    # Process in chunks
                    results = []
                    for i in range(0, len(data), chunk_size):
                        chunk = data[i:i + chunk_size]
                        chunk_result = await func(chunk, *args, **kwargs)
                        results.extend(chunk_result if isinstance(chunk_result, list) else [chunk_result])
                        
                        # Force garbage collection after each chunk
                        import gc
                        gc.collect()
                    
                    return results
                else:
                    return await func(data, *args, **kwargs)
            
            return wrapper
        return decorator
    
    @staticmethod
    def memory_limit_check(max_memory_mb: int = 1000):
        """Decorator to check memory usage and raise error if exceeded."""
        def decorator(func):
            @wraps(func)
            async def wrapper(*args, **kwargs):
                process = psutil.Process()
                current_memory = process.memory_info().rss / (1024 * 1024)  # MB
                
                if current_memory > max_memory_mb:
                    raise MemoryError(
                        f"Memory usage ({current_memory:.2f}MB) exceeds limit ({max_memory_mb}MB)"
                    )
                
                return await func(*args, **kwargs)
            
            return wrapper
        return decorator


class AlertManager:
    """Performance alerting system."""
    
    def __init__(self):
        self.alert_thresholds = {
            'cpu_percent': 80.0,
            'memory_percent': 85.0,
            'disk_usage_percent': 90.0,
            'operation_duration_ms': 10000,  # 10 seconds
            'memory_usage_mb': 500  # 500MB per operation
        }
        self.alert_callbacks = []
    
    def add_alert_callback(self, callback):
        """Add callback function for alerts."""
        self.alert_callbacks.append(callback)
    
    def check_system_alerts(self, metrics: SystemMetrics):
        """Check system metrics against thresholds."""
        alerts = []
        
        if metrics.cpu_percent > self.alert_thresholds['cpu_percent']:
            alerts.append({
                'type': 'high_cpu',
                'message': f'High CPU usage: {metrics.cpu_percent:.1f}%',
                'severity': 'warning',
                'timestamp': metrics.timestamp.isoformat()
            })
        
        if metrics.memory_percent > self.alert_thresholds['memory_percent']:
            alerts.append({
                'type': 'high_memory',
                'message': f'High memory usage: {metrics.memory_percent:.1f}%',
                'severity': 'warning',
                'timestamp': metrics.timestamp.isoformat()
            })
        
        if metrics.disk_usage_percent > self.alert_thresholds['disk_usage_percent']:
            alerts.append({
                'type': 'high_disk',
                'message': f'High disk usage: {metrics.disk_usage_percent:.1f}%',
                'severity': 'critical',
                'timestamp': metrics.timestamp.isoformat()
            })
        
        for alert in alerts:
            self._send_alert(alert)
    
    def check_operation_alerts(self, metrics: PerformanceMetrics):
        """Check operation metrics against thresholds."""
        alerts = []
        
        if metrics.duration_ms > self.alert_thresholds['operation_duration_ms']:
            alerts.append({
                'type': 'slow_operation',
                'message': f'Slow operation: {metrics.operation} took {metrics.duration_ms:.0f}ms',
                'severity': 'warning',
                'timestamp': metrics.timestamp.isoformat(),
                'operation': metrics.operation
            })
        
        if metrics.memory_usage_mb > self.alert_thresholds['memory_usage_mb']:
            alerts.append({
                'type': 'high_memory_operation',
                'message': f'High memory operation: {metrics.operation} used {metrics.memory_usage_mb:.1f}MB',
                'severity': 'warning',
                'timestamp': metrics.timestamp.isoformat(),
                'operation': metrics.operation
            })
        
        for alert in alerts:
            self._send_alert(alert)
    
    def _send_alert(self, alert: Dict[str, Any]):
        """Send alert to all registered callbacks."""
        logger.warning(f"Performance Alert: {alert['message']}")
        
        for callback in self.alert_callbacks:
            try:
                callback(alert)
            except Exception as e:
                logger.error(f"Error sending alert: {e}")


# Global alert manager instance
alert_manager = AlertManager()


# Enhanced performance monitor with alerting
class EnhancedPerformanceMonitor(PerformanceMonitor):
    """Performance monitor with alerting capabilities."""
    
    def __init__(self, max_metrics: int = 10000):
        super().__init__(max_metrics)
        self.alert_manager = alert_manager
    
    def record_operation(self, metrics: PerformanceMetrics):
        """Record performance metrics and check for alerts."""
        super().record_operation(metrics)
        self.alert_manager.check_operation_alerts(metrics)
    
    async def _collect_system_metrics(self, interval_seconds: int):
        """Collect system metrics and check for alerts."""
        while self._monitoring_active:
            try:
                metrics = SystemMetrics(
                    cpu_percent=psutil.cpu_percent(interval=1),
                    memory_percent=psutil.virtual_memory().percent,
                    memory_available_mb=psutil.virtual_memory().available / (1024 * 1024),
                    disk_usage_percent=psutil.disk_usage('/').percent,
                    active_connections=len(psutil.net_connections()),
                    timestamp=datetime.utcnow()
                )
                
                self.system_metrics.append(metrics)
                self.alert_manager.check_system_alerts(metrics)
                
                # Keep only recent metrics
                if len(self.system_metrics) > self.max_metrics:
                    self.system_metrics = self.system_metrics[-self.max_metrics:]
                
                await asyncio.sleep(interval_seconds)
                
            except Exception as e:
                logger.error(f"Error collecting system metrics: {e}")
                await asyncio.sleep(interval_seconds)


# Replace global instance with enhanced version
performance_monitor = EnhancedPerformanceMonitor()