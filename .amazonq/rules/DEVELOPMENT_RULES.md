# Development Rules - Nova Prompt Optimizer Frontend

## 🚨 **CRITICAL RULE: Keep New Files Lightweight**

**ALL NEW files MUST remain under 700 lines**

### **Legacy Files (Grandfathered):**

These existing files are exempt from the 700-line rule:
- `components/layout.py` (938 lines) ✅ EXEMPT
- `database.py` (1270 lines) ✅ EXEMPT  
- `sample_generator.py` (777 lines) ✅ EXEMPT
- `sdk_worker.py` (966 lines) ✅ EXEMPT

**Rule**: Do not make these files significantly larger, but they can remain as-is.

### **Mandatory Structure for New Features:**

1. **Route Handlers** → `routes/feature_name.py`
2. **UI Components** → `components/feature_name.py` 
3. **Business Logic** → `services/feature_name_service.py`
4. **Database Operations** → Use existing `database.py` or extend with new methods

### **New File Requirements:**

- **Max 700 lines per NEW file** 
- **Single responsibility** - one feature per file
- **Naming convention**: `folder/feature_name.py`
- **Setup function for routes**: `setup_feature_routes(app)`
- **Import in app.py**: Add to route setup section

## **Before Adding ANY New Feature:**

1. ✅ **Check file sizes**: `python3 check_structure.py`
2. ✅ **If any NEW file > 650 lines**: Extract code to additional files
3. ✅ **Plan file structure**: Which route/component/service files needed?
4. ✅ **Create files following naming conventions**
5. ✅ **Add route setup to app.py import section**

## **Code Review Checklist:**

- [ ] All NEW files under 700 lines
- [ ] Legacy files not significantly enlarged
- [ ] New routes in separate `routes/` files
- [ ] UI components in `components/` files  
- [ ] Business logic in `services/` files
- [ ] Route setup function added to app.py imports
- [ ] No duplicate code across files
- [ ] Each file has single responsibility

## **File Size Rules:**

| File Status | Max Lines | Rule |
|-------------|-----------|------|
| **NEW FILES** | **700** | Strict limit for all new development |
| **LEGACY FILES** | **No Limit** | Grandfathered, avoid major growth |

## **Current Architecture:**

```
✅ COMPLIANT FILES:
app.py (255 lines)
routes/ (all under 700 lines)
components/ (most under 700 lines)
services/ (all under 700 lines)

✅ LEGACY EXEMPT FILES:
components/layout.py (938 lines) - EXEMPT
database.py (1270 lines) - EXEMPT
sample_generator.py (777 lines) - EXEMPT
sdk_worker.py (966 lines) - EXEMPT
```

## **Violation Consequences:**

❌ **If any NEW file exceeds 700 lines**: STOP development, extract code immediately  
⚠️ **If legacy file grows significantly**: Consider refactoring (but not required)
❌ **If mixing concerns**: Refactor to separate route/component/service responsibilities

## **Quick Commands:**

```bash
# Run full compliance check (shows legacy exemptions)
python3 check_structure.py

# Check specific file
wc -l filename.py

# Monitor total lines
find . -name "*.py" -not -path "./.venv/*" | xargs wc -l
```

## **Current Status:**

✅ **All new development**: Must follow 700-line rule  
✅ **Legacy files**: Grandfathered and exempt  
✅ **Route architecture**: Fully compliant and lightweight

**Focus**: Apply 700-line rule to NEW features only

---

**⚡ Remember: 700-line rule for NEW files = Better architecture for future development**
