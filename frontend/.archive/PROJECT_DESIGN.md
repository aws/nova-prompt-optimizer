# Nova Prompt Optimizer - FastHTML Frontend Design

## 🎯 Project Overview

This design replaces the `web-simple` folder with a modern FastHTML-based frontend that provides:

- **Advanced Prompt Management**: Rich text editing, version control, templates
- **Human Annotation System**: Real-time collaborative annotation with feedback loops
- **Interactive Data Visualizations**: Custom charts and dashboards
- **Real-time Collaboration**: Multi-user support with live updates
- **Simplified Architecture**: Pure Python with HTMX for interactivity

## 📁 Project Structure

```
frontend/
├── app.py                      # Main FastHTML application
├── requirements.txt            # Python dependencies
├── config.py                   # Configuration settings
├── models/                     # Data models and database
│   ├── __init__.py
│   ├── database.py            # Database setup and connection
│   ├── prompt.py              # Prompt management models
│   ├── annotation.py          # Annotation models
│   └── user.py                # User and session models
├── routes/                     # Route handlers organized by feature
│   ├── __init__.py
│   ├── dashboard.py           # Main dashboard and navigation
│   ├── datasets.py            # Dataset management routes
│   ├── prompts.py             # Prompt management routes
│   ├── optimization.py        # Optimization workflow routes
│   ├── annotation.py          # Human annotation routes
│   ├── results.py             # Results and visualization routes
│   └── api.py                 # API endpoints for external access
├── components/                 # Reusable UI components
│   ├── __init__.py
│   ├── layout.py              # Page layouts and navigation
│   ├── forms.py               # Form components
│   ├── charts.py              # Chart and visualization components
│   ├── editors.py             # Rich text and code editors
│   └── widgets.py             # Custom UI widgets
├── static/                     # Static assets
│   ├── css/
│   │   ├── main.css           # Main stylesheet
│   │   ├── components.css     # Component-specific styles
│   │   └── themes.css         # Theme and color schemes
│   ├── js/
│   │   ├── editors.js         # Rich text editor integration
│   │   ├── charts.js          # Custom chart implementations
│   │   ├── collaboration.js   # Real-time collaboration features
│   │   └── utils.js           # Utility functions
│   └── assets/
│       ├── icons/             # SVG icons
│       └── images/            # Images and logos
├── templates/                  # Jinja2 templates (if needed for complex layouts)
│   └── email/                 # Email templates for notifications
├── services/                   # Business logic services
│   ├── __init__.py
│   ├── prompt_service.py      # Prompt management business logic
│   ├── annotation_service.py  # Annotation workflow logic
│   ├── optimization_service.py # Optimization orchestration
│   └── notification_service.py # Real-time notifications
├── utils/                      # Utility functions
│   ├── __init__.py
│   ├── auth.py                # Authentication helpers
│   ├── validation.py          # Input validation
│   └── helpers.py             # General utility functions
├── tests/                      # Test files
│   ├── __init__.py
│   ├── test_routes.py
│   ├── test_components.py
│   └── test_services.py
└── README.md                   # Frontend-specific documentation
```

## 🚀 Key Features

### 1. Advanced Prompt Management
- Rich text editor with syntax highlighting (Monaco Editor integration)
- Version control with diff views
- Template library with search and categorization
- Real-time collaborative editing
- Import/export functionality

### 2. Human Annotation System
- Interactive annotation interfaces (highlighting, tagging, rating)
- Real-time multi-user collaboration
- Progress tracking and quality metrics
- Feedback loops that update training data
- Annotation conflict resolution

### 3. Interactive Data Visualizations
- Real-time optimization progress charts
- Custom prompt performance comparisons
- Annotation quality dashboards
- A/B testing result visualizations
- Interactive data exploration tools

### 4. Real-time Collaboration
- Live cursor tracking in editors
- Real-time annotation updates
- Notification system for team activities
- Conflict resolution for concurrent edits

## 🛠 Technology Stack

- **FastHTML**: Web framework with HTMX integration
- **SQLite/PostgreSQL**: Database for data persistence
- **Monaco Editor**: Rich text editing capabilities
- **Chart.js/D3.js**: Interactive data visualizations
- **Server-Sent Events**: Real-time updates
- **WebSockets**: Real-time collaboration features

## 🔧 Development Workflow

1. **Setup**: `pip install -r requirements.txt`
2. **Development**: `python app.py --reload`
3. **Testing**: `pytest tests/`
4. **Production**: `python app.py --host 0.0.0.0 --port 8000`

## 📊 Architecture Benefits

- **Single Language**: Pure Python development
- **Real-time Features**: Built-in with HTMX and SSE
- **Modular Design**: Organized by feature domains
- **Scalable**: Easy to add new features and routes
- **Maintainable**: Clear separation of concerns
- **Testable**: Comprehensive test coverage

## 🔄 Migration from web-simple

1. **Data Migration**: Existing SQLite database can be reused
2. **Feature Parity**: All existing features will be preserved
3. **Enhanced UX**: Improved user experience with real-time features
4. **Simplified Deployment**: Single Python application
5. **Better Performance**: Server-side rendering with selective updates

## 🎨 UI/UX Design Principles

- **Clean Interface**: Minimal, focused design
- **Responsive Layout**: Works on desktop and mobile
- **Real-time Feedback**: Immediate visual feedback for all actions
- **Collaborative Features**: Clear indicators of multi-user activity
- **Accessibility**: WCAG 2.1 compliant interface
