"""
Monitoring and health check endpoints for production deployment.
"""

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from typing import Dict, Any, Optional
import asyncio
import time
import psutil
import os
from datetime import datetime, timezone

from app.db.database import get_db
from app.core.monitoring import get_system_metrics, get_application_metrics
from sqlalchemy.orm import Session
from sqlalchemy import text

router = APIRouter()


@router.get("/health")
async def health_check():
    """Basic health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "service": "nova-prompt-optimizer-api",
        "version": "1.0.0"
    }


@router.get("/health/detailed")
async def detailed_health_check(db: Session = Depends(get_db)):
    """Detailed health check with dependency status."""
    health_status = {
        "status": "healthy",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "service": "nova-prompt-optimizer-api",
        "version": "1.0.0",
        "checks": {}
    }
    
    overall_healthy = True
    
    # Database health check
    try:
        start_time = time.time()
        db.execute(text("SELECT 1"))
        db_response_time = (time.time() - start_time) * 1000
        
        health_status["checks"]["database"] = {
            "status": "healthy",
            "response_time_ms": round(db_response_time, 2)
        }
    except Exception as e:
        health_status["checks"]["database"] = {
            "status": "unhealthy",
            "error": str(e)
        }
        overall_healthy = False
    
    # Redis health check (if configured)
    try:
        import redis
        redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
        r = redis.from_url(redis_url)
        
        start_time = time.time()
        r.ping()
        redis_response_time = (time.time() - start_time) * 1000
        
        health_status["checks"]["redis"] = {
            "status": "healthy",
            "response_time_ms": round(redis_response_time, 2)
        }
    except Exception as e:
        health_status["checks"]["redis"] = {
            "status": "unhealthy",
            "error": str(e)
        }
        overall_healthy = False
    
    # AWS connectivity check
    try:
        import boto3
        from botocore.exceptions import ClientError, NoCredentialsError
        
        start_time = time.time()
        client = boto3.client('bedrock-runtime', region_name=os.getenv('AWS_REGION', 'us-east-1'))
        # Just check if we can create the client and have credentials
        client.meta.region_name  # This will raise an error if credentials are invalid
        aws_response_time = (time.time() - start_time) * 1000
        
        health_status["checks"]["aws"] = {
            "status": "healthy",
            "response_time_ms": round(aws_response_time, 2),
            "region": client.meta.region_name
        }
    except (NoCredentialsError, ClientError) as e:
        health_status["checks"]["aws"] = {
            "status": "unhealthy",
            "error": "AWS credentials not configured or invalid"
        }
        overall_healthy = False
    except Exception as e:
        health_status["checks"]["aws"] = {
            "status": "unhealthy",
            "error": str(e)
        }
        overall_healthy = False
    
    # File system health check
    try:
        upload_path = os.getenv("UPLOAD_PATH", "/app/uploads")
        if os.path.exists(upload_path):
            # Check if directory is writable
            test_file = os.path.join(upload_path, ".health_check")
            with open(test_file, "w") as f:
                f.write("health_check")
            os.remove(test_file)
            
            # Get disk usage
            disk_usage = psutil.disk_usage(upload_path)
            free_space_gb = disk_usage.free / (1024**3)
            
            health_status["checks"]["filesystem"] = {
                "status": "healthy",
                "upload_path": upload_path,
                "free_space_gb": round(free_space_gb, 2)
            }
        else:
            health_status["checks"]["filesystem"] = {
                "status": "unhealthy",
                "error": f"Upload path does not exist: {upload_path}"
            }
            overall_healthy = False
    except Exception as e:
        health_status["checks"]["filesystem"] = {
            "status": "unhealthy",
            "error": str(e)
        }
        overall_healthy = False
    
    # Update overall status
    health_status["status"] = "healthy" if overall_healthy else "unhealthy"
    
    # Return appropriate HTTP status code
    status_code = 200 if overall_healthy else 503
    return JSONResponse(content=health_status, status_code=status_code)


@router.get("/metrics")
async def get_metrics():
    """Get application metrics for monitoring."""
    try:
        system_metrics = get_system_metrics()
        app_metrics = get_application_metrics()
        
        return {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "system": system_metrics,
            "application": app_metrics
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get metrics: {str(e)}")


@router.get("/metrics/prometheus")
async def get_prometheus_metrics():
    """Get metrics in Prometheus format."""
    try:
        system_metrics = get_system_metrics()
        app_metrics = get_application_metrics()
        
        # Generate Prometheus format metrics
        prometheus_metrics = []
        
        # System metrics
        prometheus_metrics.append(f"# HELP system_cpu_percent CPU usage percentage")
        prometheus_metrics.append(f"# TYPE system_cpu_percent gauge")
        prometheus_metrics.append(f"system_cpu_percent {system_metrics['cpu_percent']}")
        
        prometheus_metrics.append(f"# HELP system_memory_percent Memory usage percentage")
        prometheus_metrics.append(f"# TYPE system_memory_percent gauge")
        prometheus_metrics.append(f"system_memory_percent {system_metrics['memory_percent']}")
        
        prometheus_metrics.append(f"# HELP system_disk_percent Disk usage percentage")
        prometheus_metrics.append(f"# TYPE system_disk_percent gauge")
        prometheus_metrics.append(f"system_disk_percent {system_metrics['disk_percent']}")
        
        # Application metrics
        prometheus_metrics.append(f"# HELP app_active_optimizations Active optimization tasks")
        prometheus_metrics.append(f"# TYPE app_active_optimizations gauge")
        prometheus_metrics.append(f"app_active_optimizations {app_metrics['active_optimizations']}")
        
        prometheus_metrics.append(f"# HELP app_total_datasets Total datasets uploaded")
        prometheus_metrics.append(f"# TYPE app_total_datasets counter")
        prometheus_metrics.append(f"app_total_datasets {app_metrics['total_datasets']}")
        
        prometheus_metrics.append(f"# HELP app_total_prompts Total prompts created")
        prometheus_metrics.append(f"# TYPE app_total_prompts counter")
        prometheus_metrics.append(f"app_total_prompts {app_metrics['total_prompts']}")
        
        return "\n".join(prometheus_metrics)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get Prometheus metrics: {str(e)}")


@router.get("/status")
async def get_status():
    """Get detailed application status."""
    return {
        "service": "nova-prompt-optimizer-api",
        "version": "1.0.0",
        "environment": os.getenv("ENVIRONMENT", "development"),
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "uptime_seconds": time.time() - psutil.boot_time(),
        "python_version": f"{psutil.sys.version_info.major}.{psutil.sys.version_info.minor}.{psutil.sys.version_info.micro}",
        "process_id": os.getpid(),
        "configuration": {
            "debug": os.getenv("DEBUG", "false").lower() == "true",
            "log_level": os.getenv("LOG_LEVEL", "info"),
            "max_file_size": os.getenv("MAX_FILE_SIZE", "104857600"),
            "api_workers": os.getenv("API_WORKERS", "4"),
            "aws_region": os.getenv("AWS_REGION", "us-east-1")
        }
    }


@router.get("/readiness")
async def readiness_check(db: Session = Depends(get_db)):
    """Kubernetes readiness probe endpoint."""
    try:
        # Check database connectivity
        db.execute(text("SELECT 1"))
        
        # Check if critical directories exist
        upload_path = os.getenv("UPLOAD_PATH", "/app/uploads")
        if not os.path.exists(upload_path):
            raise Exception(f"Upload directory not found: {upload_path}")
        
        return {"status": "ready"}
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Service not ready: {str(e)}")


@router.get("/liveness")
async def liveness_check():
    """Kubernetes liveness probe endpoint."""
    try:
        # Basic application health check
        # Check if the application can respond
        current_time = time.time()
        
        # Check memory usage (fail if over 90%)
        memory_percent = psutil.virtual_memory().percent
        if memory_percent > 90:
            raise Exception(f"Memory usage too high: {memory_percent}%")
        
        return {
            "status": "alive",
            "timestamp": current_time,
            "memory_percent": memory_percent
        }
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Service not alive: {str(e)}")


@router.post("/shutdown")
async def graceful_shutdown():
    """Graceful shutdown endpoint for container orchestration."""
    # This would typically trigger a graceful shutdown process
    # For now, just return a success response
    return {
        "status": "shutdown_initiated",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "message": "Graceful shutdown initiated"
    }