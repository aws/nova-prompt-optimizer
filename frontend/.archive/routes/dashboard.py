"""
Dashboard routes for Nova Prompt Optimizer Frontend
"""

import asyncio
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional

from fasthtml.common import *
from starlette.requests import Request

from components.layout import create_main_layout, create_card, create_table
from models.database import get_async_db
from models.user import User
from models.prompt import Prompt, OptimizationRun, PromptStatus, OptimizationStatus
from utils.auth import require_auth, get_current_user

# Create router
router = APIRouter()


async def get_dashboard_stats(user_id: str) -> Dict[str, Any]:
    """Get dashboard statistics for user"""
    
    async with get_async_db() as db:
        from sqlalchemy import select, func, and_
        
        # Get prompt statistics
        prompt_stats = await db.execute(
            select(
                func.count(Prompt.id).label('total'),
                func.sum(case((Prompt.status == PromptStatus.ACTIVE.value, 1), else_=0)).label('active'),
                func.sum(case((Prompt.status == PromptStatus.OPTIMIZED.value, 1), else_=0)).label('optimized'),
                func.sum(case((Prompt.status == PromptStatus.DRAFT.value, 1), else_=0)).label('draft')
            ).where(
                or_(Prompt.created_by == user_id, Prompt.collaborators.contains([user_id]))
            )
        )
        prompt_data = prompt_stats.first()
        
        # Get optimization statistics
        optimization_stats = await db.execute(
            select(
                func.count(OptimizationRun.id).label('total'),
                func.sum(case((OptimizationRun.status == OptimizationStatus.COMPLETED.value, 1), else_=0)).label('completed'),
                func.sum(case((OptimizationRun.status == OptimizationStatus.RUNNING.value, 1), else_=0)).label('running'),
                func.sum(case((OptimizationRun.status == OptimizationStatus.FAILED.value, 1), else_=0)).label('failed')
            ).where(OptimizationRun.started_by == user_id)
        )
        opt_data = optimization_stats.first()
        
        # Get recent activity (last 7 days)
        week_ago = datetime.utcnow() - timedelta(days=7)
        recent_prompts = await db.execute(
            select(func.count(Prompt.id)).where(
                and_(
                    Prompt.created_at >= week_ago,
                    or_(Prompt.created_by == user_id, Prompt.collaborators.contains([user_id]))
                )
            )
        )
        
        recent_optimizations = await db.execute(
            select(func.count(OptimizationRun.id)).where(
                and_(
                    OptimizationRun.created_at >= week_ago,
                    OptimizationRun.started_by == user_id
                )
            )
        )
        
        return {
            'prompts': {
                'total': prompt_data.total or 0,
                'active': prompt_data.active or 0,
                'optimized': prompt_data.optimized or 0,
                'draft': prompt_data.draft or 0
            },
            'optimizations': {
                'total': opt_data.total or 0,
                'completed': opt_data.completed or 0,
                'running': opt_data.running or 0,
                'failed': opt_data.failed or 0
            },
            'recent_activity': {
                'prompts': recent_prompts.scalar() or 0,
                'optimizations': recent_optimizations.scalar() or 0
            }
        }


async def get_recent_prompts(user_id: str, limit: int = 5) -> List[Dict]:
    """Get recent prompts for user"""
    
    async with get_async_db() as db:
        from sqlalchemy import select, or_, desc
        
        result = await db.execute(
            select(Prompt).where(
                or_(Prompt.created_by == user_id, Prompt.collaborators.contains([user_id]))
            ).order_by(desc(Prompt.updated_at)).limit(limit)
        )
        
        prompts = result.scalars().all()
        return [prompt.to_dict(include_content=False) for prompt in prompts]


async def get_recent_optimizations(user_id: str, limit: int = 5) -> List[Dict]:
    """Get recent optimization runs for user"""
    
    async with get_async_db() as db:
        from sqlalchemy import select, desc
        
        result = await db.execute(
            select(OptimizationRun).where(
                OptimizationRun.started_by == user_id
            ).order_by(desc(OptimizationRun.created_at)).limit(limit)
        )
        
        optimizations = result.scalars().all()
        return [opt.to_dict() for opt in optimizations]


def create_stats_card(title: str, stats: Dict[str, int], icon: str = "📊") -> Div:
    """Create statistics card"""
    
    # Calculate total and create stat items
    total = stats.get('total', 0)
    stat_items = []
    
    for key, value in stats.items():
        if key != 'total':
            percentage = (value / total * 100) if total > 0 else 0
            stat_items.append(
                Div(
                    Span(str(value), cls="stat-value"),
                    Span(key.replace('_', ' ').title(), cls="stat-label"),
                    Span(f"{percentage:.1f}%", cls="stat-percentage"),
                    cls=f"stat-item {key}"
                )
            )
    
    return create_card(
        title=None,
        content=Div(
            Div(
                Span(icon, cls="card-icon"),
                H3(title, cls="card-title"),
                Span(str(total), cls="total-count"),
                cls="card-header-stats"
            ),
            Div(
                *stat_items,
                cls="stats-grid"
            ),
            cls="stats-card-content"
        ),
        cls="stats-card"
    )


def create_activity_chart(data: Dict[str, Any]) -> Div:
    """Create activity chart"""
    
    return Div(
        H4("Recent Activity (Last 7 Days)", cls="chart-title"),
        Div(
            Div(
                Span("📝", cls="activity-icon"),
                Div(
                    Span(str(data['prompts']), cls="activity-count"),
                    Span("New Prompts", cls="activity-label"),
                    cls="activity-info"
                ),
                cls="activity-item prompts"
            ),
            Div(
                Span("🚀", cls="activity-icon"),
                Div(
                    Span(str(data['optimizations']), cls="activity-count"),
                    Span("Optimizations", cls="activity-label"),
                    cls="activity-info"
                ),
                cls="activity-item optimizations"
            ),
            cls="activity-summary"
        ),
        # Placeholder for future chart implementation
        Div(
            Canvas(
                id="activity-chart",
                width="400",
                height="200",
                style="border: 1px solid #ddd; border-radius: 4px;"
            ),
            Script(f"""
                // Initialize activity chart
                const ctx = document.getElementById('activity-chart').getContext('2d');
                const chart = new Chart(ctx, {{
                    type: 'line',
                    data: {{
                        labels: ['6 days ago', '5 days ago', '4 days ago', '3 days ago', '2 days ago', 'Yesterday', 'Today'],
                        datasets: [{{
                            label: 'Prompts',
                            data: [2, 1, 3, 2, 1, 4, {data['prompts']}],
                            borderColor: '#0066cc',
                            backgroundColor: 'rgba(0, 102, 204, 0.1)',
                            tension: 0.4
                        }}, {{
                            label: 'Optimizations',
                            data: [1, 0, 2, 1, 0, 2, {data['optimizations']}],
                            borderColor: '#28a745',
                            backgroundColor: 'rgba(40, 167, 69, 0.1)',
                            tension: 0.4
                        }}]
                    }},
                    options: {{
                        responsive: true,
                        scales: {{
                            y: {{
                                beginAtZero: true,
                                ticks: {{
                                    stepSize: 1
                                }}
                            }}
                        }},
                        plugins: {{
                            legend: {{
                                position: 'top'
                            }}
                        }}
                    }}
                }});
            """),
            cls="chart-container"
        ),
        cls="activity-chart"
    )


def create_recent_items_table(items: List[Dict], item_type: str) -> Div:
    """Create table for recent items"""
    
    if not items:
        return Div(
            P(f"No recent {item_type} found.", cls="empty-message"),
            A(f"Create New {item_type.title()}", 
              href=f"/{item_type}", 
              cls="btn btn-primary btn-sm"),
            cls="empty-state"
        )
    
    if item_type == "prompts":
        headers = ["Name", "Status", "Updated", "Actions"]
        rows = []
        for item in items:
            status_class = f"status-{item['status']}"
            updated = datetime.fromisoformat(item['updated_at'].replace('Z', '+00:00'))
            time_ago = get_time_ago(updated)
            
            rows.append([
                A(item['name'], href=f"/prompts/{item['id']}", cls="item-link"),
                Span(item['status'].title(), cls=f"status-badge {status_class}"),
                Span(time_ago, cls="time-ago"),
                Div(
                    A("Edit", href=f"/prompts/{item['id']}/edit", cls="btn btn-sm btn-secondary"),
                    A("View", href=f"/prompts/{item['id']}", cls="btn btn-sm btn-outline"),
                    cls="action-buttons"
                )
            ])
    
    else:  # optimizations
        headers = ["Prompt", "Status", "Progress", "Started", "Actions"]
        rows = []
        for item in items:
            status_class = f"status-{item['status']}"
            started = datetime.fromisoformat(item['started_at'].replace('Z', '+00:00')) if item['started_at'] else None
            time_ago = get_time_ago(started) if started else "Not started"
            
            progress_bar = Div(
                Div(style=f"width: {item['progress'] * 100}%", cls="progress-fill"),
                cls="progress-bar"
            )
            
            rows.append([
                A(f"Optimization {item['id'][:8]}", href=f"/optimization/{item['id']}", cls="item-link"),
                Span(item['status'].title(), cls=f"status-badge {status_class}"),
                Div(
                    progress_bar,
                    Span(f"{item['progress'] * 100:.1f}%", cls="progress-text"),
                    cls="progress-container"
                ),
                Span(time_ago, cls="time-ago"),
                Div(
                    A("View", href=f"/optimization/{item['id']}", cls="btn btn-sm btn-outline"),
                    cls="action-buttons"
                )
            ])
    
    return create_table(headers, rows, cls="recent-items-table")


def get_time_ago(dt: datetime) -> str:
    """Get human-readable time ago string"""
    now = datetime.utcnow().replace(tzinfo=dt.tzinfo)
    diff = now - dt
    
    if diff.days > 0:
        return f"{diff.days} day{'s' if diff.days != 1 else ''} ago"
    elif diff.seconds > 3600:
        hours = diff.seconds // 3600
        return f"{hours} hour{'s' if hours != 1 else ''} ago"
    elif diff.seconds > 60:
        minutes = diff.seconds // 60
        return f"{minutes} minute{'s' if minutes != 1 else ''} ago"
    else:
        return "Just now"


@router.get("/")
async def dashboard_page(request: Request, user: Optional[User] = None):
    """Main dashboard page"""
    
    if not user:
        user = await get_current_user(request)
        if not user:
            return RedirectResponse(url="/auth/login")
    
    # Get dashboard data
    stats = await get_dashboard_stats(user.id)
    recent_prompts = await get_recent_prompts(user.id)
    recent_optimizations = await get_recent_optimizations(user.id)
    
    # Create dashboard content
    content = Div(
        # Welcome section
        Div(
            H1(f"Welcome back, {user.full_name or user.username}!", cls="welcome-title"),
            P("Here's what's happening with your prompt optimization projects.", cls="welcome-subtitle"),
            cls="welcome-section"
        ),
        
        # Statistics cards
        Div(
            create_stats_card("Prompts", stats['prompts'], "📝"),
            create_stats_card("Optimizations", stats['optimizations'], "🚀"),
            create_activity_chart(stats['recent_activity']),
            cls="stats-grid"
        ),
        
        # Recent activity section
        Div(
            Div(
                create_card(
                    title="Recent Prompts",
                    content=create_recent_items_table(recent_prompts, "prompts"),
                    actions=[
                        A("View All Prompts", href="/prompts", cls="btn btn-outline"),
                        A("Create New Prompt", href="/prompts/new", cls="btn btn-primary")
                    ]
                ),
                cls="recent-section"
            ),
            Div(
                create_card(
                    title="Recent Optimizations",
                    content=create_recent_items_table(recent_optimizations, "optimizations"),
                    actions=[
                        A("View All Optimizations", href="/optimization", cls="btn btn-outline"),
                        A("Start New Optimization", href="/optimization/new", cls="btn btn-primary")
                    ]
                ),
                cls="recent-section"
            ),
            cls="recent-grid"
        ),
        
        # Quick actions section
        Div(
            H2("Quick Actions", cls="section-title"),
            Div(
                create_card(
                    title="Create New Prompt",
                    content=P("Start building a new prompt from scratch or use a template."),
                    actions=[A("Create Prompt", href="/prompts/new", cls="btn btn-primary")]
                ),
                create_card(
                    title="Upload Dataset",
                    content=P("Upload a new dataset for prompt optimization and evaluation."),
                    actions=[A("Upload Dataset", href="/datasets/upload", cls="btn btn-primary")]
                ),
                create_card(
                    title="Start Optimization",
                    content=P("Optimize an existing prompt using Nova models."),
                    actions=[A("Start Optimization", href="/optimization/new", cls="btn btn-primary")]
                ),
                create_card(
                    title="Annotation Tasks",
                    content=P("Review and annotate data for quality improvement."),
                    actions=[A("View Tasks", href="/annotation", cls="btn btn-primary")]
                ),
                cls="quick-actions-grid"
            ),
            cls="quick-actions-section"
        ),
        
        cls="dashboard-content"
    )
    
    return create_main_layout(
        title="Dashboard",
        content=content,
        current_page="dashboard",
        user=user.to_dict() if user else None,
        breadcrumb=[{"name": "Dashboard"}]
    )


@router.get("/stats")
async def dashboard_stats_api(request: Request):
    """API endpoint for dashboard statistics"""
    
    user = await get_current_user(request)
    if not user:
        return {"error": "Authentication required"}, 401
    
    stats = await get_dashboard_stats(user.id)
    return stats


@router.get("/activity")
async def dashboard_activity_api(request: Request):
    """API endpoint for recent activity"""
    
    user = await get_current_user(request)
    if not user:
        return {"error": "Authentication required"}, 401
    
    recent_prompts = await get_recent_prompts(user.id, limit=10)
    recent_optimizations = await get_recent_optimizations(user.id, limit=10)
    
    return {
        "prompts": recent_prompts,
        "optimizations": recent_optimizations
    }


# Real-time updates for dashboard
@router.get("/live-stats")
async def live_stats_sse(request: Request):
    """Server-sent events for live dashboard updates"""
    
    user = await get_current_user(request)
    if not user:
        return {"error": "Authentication required"}, 401
    
    async def event_stream():
        while True:
            try:
                stats = await get_dashboard_stats(user.id)
                yield f"data: {json.dumps(stats)}\n\n"
                await asyncio.sleep(30)  # Update every 30 seconds
            except Exception as e:
                yield f"data: {json.dumps({'error': str(e)})}\n\n"
                break
    
    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        }
    )
