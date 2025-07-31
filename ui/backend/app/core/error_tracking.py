"""
Error tracking and monitoring system for the Nova Prompt Optimizer backend.
"""
import traceback
import logging
import json
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass, asdict
from enum import Enum
from functools import wraps
import asyncio

logger = logging.getLogger(__name__)


class ErrorSeverity(Enum):
    """Error severity levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class ErrorEvent:
    """Error event data structure."""
    id: str
    message: str
    exception_type: str
    severity: ErrorSeverity
    timestamp: datetime
    stack_trace: str
    context: Dict[str, Any]
    user_id: Optional[str] = None
    request_id: Optional[str] = None
    endpoint: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        data = asdict(self)
        data['timestamp'] = self.timestamp.isoformat()
        data['severity'] = self.severity.value
        return data


class ErrorTracker:
    """Error tracking and monitoring system."""
    
    def __init__(self, max_errors: int = 10000):
        self.max_errors = max_errors
        self.errors: List[ErrorEvent] = []
        self.error_callbacks: List[Callable[[ErrorEvent], None]] = []
        self.error_counts: Dict[str, int] = {}
        self.suppressed_errors: set = set()
        
    def add_error_callback(self, callback: Callable[[ErrorEvent], None]):
        """Add callback function for error notifications."""
        self.error_callbacks.append(callback)
    
    def suppress_error_type(self, exception_type: str):
        """Suppress tracking for specific error types."""
        self.suppressed_errors.add(exception_type)
    
    def unsuppress_error_type(self, exception_type: str):
        """Remove error type from suppression list."""
        self.suppressed_errors.discard(exception_type)
    
    def track_error(
        self,
        exception: Exception,
        severity: ErrorSeverity = ErrorSeverity.MEDIUM,
        context: Optional[Dict[str, Any]] = None,
        user_id: Optional[str] = None,
        request_id: Optional[str] = None,
        endpoint: Optional[str] = None
    ) -> str:
        """Track an error event."""
        exception_type = type(exception).__name__
        
        # Check if error type is suppressed
        if exception_type in self.suppressed_errors:
            return ""
        
        # Generate unique error ID
        error_id = f"error_{datetime.utcnow().timestamp()}_{id(exception)}"
        
        # Create error event
        error_event = ErrorEvent(
            id=error_id,
            message=str(exception),
            exception_type=exception_type,
            severity=severity,
            timestamp=datetime.utcnow(),
            stack_trace=traceback.format_exc(),
            context=context or {},
            user_id=user_id,
            request_id=request_id,
            endpoint=endpoint
        )
        
        # Store error
        self.errors.append(error_event)
        
        # Update error counts
        self.error_counts[exception_type] = self.error_counts.get(exception_type, 0) + 1
        
        # Keep only recent errors
        if len(self.errors) > self.max_errors:
            self.errors = self.errors[-self.max_errors:]
        
        # Log error
        log_level = {
            ErrorSeverity.LOW: logging.INFO,
            ErrorSeverity.MEDIUM: logging.WARNING,
            ErrorSeverity.HIGH: logging.ERROR,
            ErrorSeverity.CRITICAL: logging.CRITICAL
        }[severity]
        
        logger.log(
            log_level,
            f"Error tracked: {exception_type} - {str(exception)} (ID: {error_id})"
        )
        
        # Notify callbacks
        for callback in self.error_callbacks:
            try:
                callback(error_event)
            except Exception as callback_error:
                logger.error(f"Error in error callback: {callback_error}")
        
        return error_id
    
    def get_errors(
        self,
        severity: Optional[ErrorSeverity] = None,
        exception_type: Optional[str] = None,
        since: Optional[datetime] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Get error events with optional filtering."""
        filtered_errors = self.errors
        
        if severity:
            filtered_errors = [e for e in filtered_errors if e.severity == severity]
        
        if exception_type:
            filtered_errors = [e for e in filtered_errors if e.exception_type == exception_type]
        
        if since:
            filtered_errors = [e for e in filtered_errors if e.timestamp >= since]
        
        # Sort by timestamp (most recent first) and limit
        filtered_errors = sorted(filtered_errors, key=lambda x: x.timestamp, reverse=True)
        filtered_errors = filtered_errors[:limit]
        
        return [e.to_dict() for e in filtered_errors]
    
    def get_error_summary(self) -> Dict[str, Any]:
        """Get error summary statistics."""
        if not self.errors:
            return {"total_errors": 0}
        
        # Count by severity
        severity_counts = {}
        for severity in ErrorSeverity:
            severity_counts[severity.value] = len([
                e for e in self.errors if e.severity == severity
            ])
        
        # Count by exception type
        type_counts = dict(self.error_counts)
        
        # Recent errors (last 24 hours)
        recent_cutoff = datetime.utcnow() - timedelta(hours=24)
        recent_errors = [e for e in self.errors if e.timestamp >= recent_cutoff]
        
        # Most common errors
        most_common = sorted(
            type_counts.items(),
            key=lambda x: x[1],
            reverse=True
        )[:10]
        
        return {
            "total_errors": len(self.errors),
            "recent_errors_24h": len(recent_errors),
            "severity_breakdown": severity_counts,
            "most_common_errors": most_common,
            "error_rate_per_hour": len(recent_errors) / 24,
            "time_range": {
                "oldest": self.errors[0].timestamp.isoformat() if self.errors else None,
                "newest": self.errors[-1].timestamp.isoformat() if self.errors else None
            }
        }
    
    def get_error_trends(self, hours: int = 24) -> Dict[str, List[int]]:
        """Get error trends over time."""
        cutoff = datetime.utcnow() - timedelta(hours=hours)
        recent_errors = [e for e in self.errors if e.timestamp >= cutoff]
        
        # Group errors by hour
        hourly_counts = {}
        for error in recent_errors:
            hour_key = error.timestamp.replace(minute=0, second=0, microsecond=0)
            hourly_counts[hour_key] = hourly_counts.get(hour_key, 0) + 1
        
        # Fill in missing hours with 0
        trends = []
        current_hour = datetime.utcnow().replace(minute=0, second=0, microsecond=0)
        
        for i in range(hours):
            hour = current_hour - timedelta(hours=i)
            trends.append(hourly_counts.get(hour, 0))
        
        trends.reverse()  # Oldest to newest
        
        return {
            "hourly_counts": trends,
            "hours": hours,
            "total_in_period": sum(trends)
        }
    
    def clear_errors(self):
        """Clear all stored errors."""
        self.errors.clear()
        self.error_counts.clear()
        logger.info("Error tracking data cleared")


# Global error tracker instance
error_tracker = ErrorTracker()


def track_errors(
    severity: ErrorSeverity = ErrorSeverity.MEDIUM,
    context: Optional[Dict[str, Any]] = None,
    suppress_types: Optional[List[str]] = None
):
    """Decorator to automatically track errors in functions."""
    def decorator(func):
        if asyncio.iscoroutinefunction(func):
            @wraps(func)
            async def async_wrapper(*args, **kwargs):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    if not suppress_types or type(e).__name__ not in suppress_types:
                        error_tracker.track_error(
                            exception=e,
                            severity=severity,
                            context={
                                **(context or {}),
                                "function": func.__name__,
                                "args": str(args)[:200],  # Limit length
                                "kwargs": str(kwargs)[:200]
                            }
                        )
                    raise
            
            return async_wrapper
        else:
            @wraps(func)
            def sync_wrapper(*args, **kwargs):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if not suppress_types or type(e).__name__ not in suppress_types:
                        error_tracker.track_error(
                            exception=e,
                            severity=severity,
                            context={
                                **(context or {}),
                                "function": func.__name__,
                                "args": str(args)[:200],
                                "kwargs": str(kwargs)[:200]
                            }
                        )
                    raise
            
            return sync_wrapper
    
    return decorator


class AlertingSystem:
    """Error alerting system."""
    
    def __init__(self):
        self.alert_thresholds = {
            'error_rate_per_minute': 10,
            'critical_errors_per_hour': 5,
            'high_errors_per_hour': 20,
            'same_error_count': 50
        }
        self.alert_callbacks: List[Callable[[Dict[str, Any]], None]] = []
        self.last_alert_times: Dict[str, datetime] = {}
        self.alert_cooldown = timedelta(minutes=5)  # Minimum time between same alerts
    
    def add_alert_callback(self, callback: Callable[[Dict[str, Any]], None]):
        """Add callback function for alerts."""
        self.alert_callbacks.append(callback)
    
    def check_error_rate_alert(self, errors: List[ErrorEvent]):
        """Check for high error rate alerts."""
        now = datetime.utcnow()
        recent_errors = [
            e for e in errors 
            if e.timestamp >= now - timedelta(minutes=1)
        ]
        
        if len(recent_errors) >= self.alert_thresholds['error_rate_per_minute']:
            alert_key = "high_error_rate"
            if self._should_send_alert(alert_key):
                self._send_alert({
                    'type': 'high_error_rate',
                    'message': f'High error rate: {len(recent_errors)} errors in the last minute',
                    'severity': 'critical',
                    'timestamp': now.isoformat(),
                    'error_count': len(recent_errors)
                })
    
    def check_severity_alerts(self, errors: List[ErrorEvent]):
        """Check for severity-based alerts."""
        now = datetime.utcnow()
        hour_ago = now - timedelta(hours=1)
        
        # Critical errors
        critical_errors = [
            e for e in errors 
            if e.severity == ErrorSeverity.CRITICAL and e.timestamp >= hour_ago
        ]
        
        if len(critical_errors) >= self.alert_thresholds['critical_errors_per_hour']:
            alert_key = "critical_errors"
            if self._should_send_alert(alert_key):
                self._send_alert({
                    'type': 'critical_errors',
                    'message': f'{len(critical_errors)} critical errors in the last hour',
                    'severity': 'critical',
                    'timestamp': now.isoformat(),
                    'error_count': len(critical_errors)
                })
        
        # High errors
        high_errors = [
            e for e in errors 
            if e.severity == ErrorSeverity.HIGH and e.timestamp >= hour_ago
        ]
        
        if len(high_errors) >= self.alert_thresholds['high_errors_per_hour']:
            alert_key = "high_errors"
            if self._should_send_alert(alert_key):
                self._send_alert({
                    'type': 'high_errors',
                    'message': f'{len(high_errors)} high severity errors in the last hour',
                    'severity': 'warning',
                    'timestamp': now.isoformat(),
                    'error_count': len(high_errors)
                })
    
    def check_repeated_error_alert(self, error_counts: Dict[str, int]):
        """Check for repeated error alerts."""
        for error_type, count in error_counts.items():
            if count >= self.alert_thresholds['same_error_count']:
                alert_key = f"repeated_error_{error_type}"
                if self._should_send_alert(alert_key):
                    self._send_alert({
                        'type': 'repeated_error',
                        'message': f'Repeated error: {error_type} occurred {count} times',
                        'severity': 'warning',
                        'timestamp': datetime.utcnow().isoformat(),
                        'error_type': error_type,
                        'error_count': count
                    })
    
    def _should_send_alert(self, alert_key: str) -> bool:
        """Check if enough time has passed since last alert of this type."""
        last_alert = self.last_alert_times.get(alert_key)
        if last_alert is None:
            return True
        
        return datetime.utcnow() - last_alert >= self.alert_cooldown
    
    def _send_alert(self, alert: Dict[str, Any]):
        """Send alert to all registered callbacks."""
        alert_key = alert.get('type', 'unknown')
        self.last_alert_times[alert_key] = datetime.utcnow()
        
        logger.error(f"Error Alert: {alert['message']}")
        
        for callback in self.alert_callbacks:
            try:
                callback(alert)
            except Exception as e:
                logger.error(f"Error in alert callback: {e}")


# Global alerting system
alerting_system = AlertingSystem()


# Enhanced error tracker with alerting
class EnhancedErrorTracker(ErrorTracker):
    """Error tracker with alerting capabilities."""
    
    def __init__(self, max_errors: int = 10000):
        super().__init__(max_errors)
        self.alerting_system = alerting_system
    
    def track_error(
        self,
        exception: Exception,
        severity: ErrorSeverity = ErrorSeverity.MEDIUM,
        context: Optional[Dict[str, Any]] = None,
        user_id: Optional[str] = None,
        request_id: Optional[str] = None,
        endpoint: Optional[str] = None
    ) -> str:
        """Track an error event and check for alerts."""
        error_id = super().track_error(
            exception, severity, context, user_id, request_id, endpoint
        )
        
        # Check for alerts
        self.alerting_system.check_error_rate_alert(self.errors)
        self.alerting_system.check_severity_alerts(self.errors)
        self.alerting_system.check_repeated_error_alert(self.error_counts)
        
        return error_id


# Replace global instance with enhanced version
error_tracker = EnhancedErrorTracker()


# Error reporting utilities
def report_error(
    message: str,
    severity: ErrorSeverity = ErrorSeverity.MEDIUM,
    context: Optional[Dict[str, Any]] = None
):
    """Report a custom error without an exception."""
    class CustomError(Exception):
        pass
    
    try:
        raise CustomError(message)
    except CustomError as e:
        error_tracker.track_error(
            exception=e,
            severity=severity,
            context=context
        )


def setup_global_error_handler():
    """Set up global error handlers for uncaught exceptions."""
    import sys
    
    def handle_exception(exc_type, exc_value, exc_traceback):
        """Handle uncaught exceptions."""
        if issubclass(exc_type, KeyboardInterrupt):
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return
        
        error_tracker.track_error(
            exception=exc_value,
            severity=ErrorSeverity.CRITICAL,
            context={
                "source": "global_handler",
                "exc_type": exc_type.__name__
            }
        )
        
        # Call original handler
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
    
    sys.excepthook = handle_exception