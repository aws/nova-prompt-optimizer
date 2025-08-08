# Archived Files - Nova Prompt Optimizer Frontend

**Archive Date:** August 7, 2024  
**Reason:** Cleanup after implementing SQLite persistence and SDK integration

## 📁 **What's in This Archive**

This directory contains files that were part of the development process but are no longer used by the current application. They have been archived for reference and potential future use.

### **Backup App Files**
- `app.py.backup` (146KB) - Backup from dashboard layout changes
- `app.py.broken` (146KB) - Broken version during development
- `app_backup.py` (61KB) - Earlier backup version
- `app_clean.py` (5KB) - Clean version attempt
- `app_clean_post.py` (8KB) - Post-clean version
- `app_working.py` (10KB) - Working version backup

### **Old Architecture Components**
- `models/` - Old database models (replaced by `database.py`)
  - `user.py` - User model and authentication
  - `database.py` - Old database connection system
  - `prompt.py` - Prompt and optimization models
- `routes/` - Old route handlers (now in `app.py`)
  - `dashboard.py` - Dashboard route handlers
- `templates/` - HTML templates (replaced by FastHTML components)
- `static/` - CSS and assets (using CDN now)

### **Data Files**
- `data_datasets.json` - Sample dataset data
- `data_prompts.json` - Sample prompt data
- `data_optimizations.json` - Sample optimization data
- `optimization.log` - Old optimization logs
- `data/` - Empty data directory
- `logs/` - Empty logs directory
- `uploads/` - Empty uploads directory

### **Configuration Files**
- `.env` - Environment variables (not used by current app)
- `.env.template` - Environment template
- `.sesskey` - Session key file
- `setup.py` - Old setup script
- `init_db.py` - Old database initialization
- `INSTALL.md` - Outdated installation instructions

### **Requirements Files**
- `requirements.txt` - Full requirements (bloated)
- `requirements-advanced.txt` - Advanced requirements
- `requirements-minimal.txt` - Minimal requirements

## 🔄 **Current vs Archived Architecture**

### **Old Architecture (Archived)**
```
Frontend (FastHTML)
    ↓ Routes
Route Handlers (routes/)
    ↓ Models  
Database Models (models/)
    ↓ Database
PostgreSQL/Complex Setup
```

### **New Architecture (Current)**
```
Frontend (FastHTML)
    ↓ Direct Integration
App Routes (app.py)
    ↓ Simple Database
SQLite (database.py)
    ↓ SDK Integration
Nova Prompt Optimizer SDK
```

## ⚠️ **Important Notes**

1. **Don't Delete**: These files contain development history and may be useful for reference
2. **Not Dependencies**: Current app doesn't depend on any of these files
3. **Safe Archive**: All files have been verified as unused by current codebase
4. **Space Saved**: ~500KB of disk space cleaned up in main directory

## 🔍 **If You Need Something**

If you need to reference or restore any of these files:

1. **Check this archive first** - Most development artifacts are here
2. **Git history** - Full development history is in version control
3. **Current equivalents** - Most functionality has been reimplemented in the current clean architecture

## 📊 **Archive Statistics**

- **Total Files Archived:** 30+ files
- **Directories Archived:** 7 directories
- **Space Archived:** ~500KB
- **Development Phases:** Covers 3 major refactoring phases

This archive represents the evolution from a complex multi-file architecture to a clean, simple, and maintainable codebase.
