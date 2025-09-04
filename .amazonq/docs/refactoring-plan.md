# Nova Prompt Optimizer Frontend Refactoring Plan

## Current State Analysis (Updated August 22, 2025)

**Current Issues:**
- `app.py` is now 4,506 lines (increased from 4,496) with 53+ routes and 9+ functions
- Monolithic structure with mixed concerns (UI, business logic, routes)
- Difficult to maintain and test
- Poor separation of concerns
- **NEW**: Added dataset generation complexity with multiple approaches

**Existing Structure (Updated):**
```
frontend/
├── app.py (4,506 lines) - MONOLITHIC
├── components/ (partially organized)
│   ├── layout.py
│   ├── navbar.py
│   ├── ui.py
│   └── metrics_page.py
├── database.py
├── sample_generator.py (NEW - 685 lines)
├── dataset_conversation.py (NEW - 522 lines)
├── simple_dataset_generator.py (NEW - 85 lines)
├── simple_routes.py (NEW - 140 lines)
├── sdk_worker.py
└── other utilities...
```

**Recent Changes Added:**
- **Dataset Generation System**: Two approaches (complex conversational + simple direct)
- **AI-Powered Sample Creation**: LLM-based dataset generation with prompt analysis
- **Multiple Generator Interfaces**: Both complex wizard and simple form approaches
- **Prompt Analysis Service**: Natural language processing for requirement extraction

## Proposed Refactored Structure (Updated)

```
frontend/
├── app.py (main FastHTML app setup - ~100 lines)
├── config.py (existing - configuration)
├── database.py (existing - database layer)
│
├── routes/ (NEW - route handlers)
│   ├── __init__.py
│   ├── dashboard.py
│   ├── datasets.py
│   ├── prompts.py
│   ├── metrics.py
│   ├── optimization.py
│   ├── generator.py (complex dataset generation routes)
│   └── simple_generator.py (simple dataset generation routes)
│
├── services/ (NEW - business logic)
│   ├── __init__.py
│   ├── dataset_service.py
│   ├── prompt_service.py
│   ├── optimization_service.py
│   ├── sample_generator.py (move existing - complex generator)
│   ├── simple_dataset_generator.py (move existing - simple generator)
│   ├── dataset_conversation.py (move existing - conversational AI)
│   └── prompt_analysis_service.py (NEW - extract from conversation service)
│   └── metric_service.py (move existing)
│
├── components/ (existing - UI components)
│   ├── __init__.py
│   ├── layout.py (existing)
│   ├── navbar.py (existing)
│   ├── ui.py (existing)
│   ├── metrics_page.py (existing)
│   ├── dataset_components.py (NEW)
│   ├── prompt_components.py (NEW)
│   └── optimization_components.py (NEW)
│
├── utils/ (NEW - utilities)
│   ├── __init__.py
│   ├── simple_rate_limiter.py (move existing)
│   ├── file_utils.py (NEW)
│   └── validation.py (NEW)
│
├── static/ (NEW - static assets)
│   ├── css/
│   ├── js/
│   └── images/
│
└── templates/ (NEW - if needed for complex pages)
    └── (optional Jinja2 templates)
```

## Detailed Refactoring Steps

### Phase 1: Core Infrastructure (Priority: HIGH)

#### 1.1 Create New App Structure
- **File:** `app.py` (refactored to ~100 lines)
- **Purpose:** Main FastHTML app setup, middleware, and route registration
- **Content:**
  - App initialization
  - Middleware setup
  - Route imports and registration
  - Static file serving
  - Error handlers

#### 1.2 Create Route Modules
- **Files:** `routes/*.py`
- **Purpose:** Separate route handlers by feature area
- **Breakdown:**
  - `dashboard.py` - Home dashboard routes
  - `datasets.py` - Dataset CRUD operations
  - `prompts.py` - Prompt management routes
  - `metrics.py` - Metric generation and management
  - `optimization.py` - Optimization workflow routes
  - `generator.py` - AI dataset generation routes

### Phase 2: Service Layer (Priority: HIGH)

#### 2.1 Extract Business Logic
- **Files:** `services/*.py`
- **Purpose:** Move business logic out of routes
- **Actions:**
  - Move existing `sample_generator.py` to `services/` (685 lines)
  - Move existing `simple_dataset_generator.py` to `services/` (85 lines)
  - Move existing `dataset_conversation.py` to `services/` (522 lines)
  - Move existing `metric_service.py` to `services/`
  - Create new service classes for datasets, prompts, optimization
  - **NEW**: Extract prompt analysis logic into separate service

#### 2.2 Create Service Interfaces
```python
# services/dataset_service.py
class DatasetService:
    def create_dataset(self, name, file_data) -> Dict
    def get_dataset(self, dataset_id) -> Dict
    def list_datasets(self) -> List[Dict]
    def delete_dataset(self, dataset_id) -> bool

# services/prompt_service.py
class PromptService:
    def create_prompt(self, name, content) -> Dict
    def get_prompt(self, prompt_id) -> Dict
    def list_prompts(self) -> List[Dict]
    def update_prompt(self, prompt_id, content) -> Dict

# services/optimization_service.py
class OptimizationService:
    def start_optimization(self, config) -> str
    def get_optimization_status(self, opt_id) -> Dict
    def get_optimization_results(self, opt_id) -> Dict

# services/generator_service.py (NEW)
class GeneratorService:
    def __init__(self):
        self.complex_generator = SampleGeneratorService()
        self.simple_generator = SimpleDatasetGenerator()
        self.conversation_service = DatasetConversationService()
    
    def generate_complex(self, requirements) -> Dict
    def generate_simple(self, prompt_content, num_samples) -> Dict
    def analyze_prompt(self, prompt_text) -> Dict
```

### Phase 3: Component Organization (Priority: MEDIUM)

#### 3.1 Expand UI Components
- **Files:** `components/*.py`
- **Purpose:** Create reusable UI components
- **New Components:**
  - `dataset_components.py` - Dataset upload, display, management
  - `prompt_components.py` - Prompt editor, selector, preview
  - `optimization_components.py` - Optimization forms, progress, results

#### 3.2 Standardize Component Interface
```python
# Standard component signature
def create_component_name(data: Dict, **kwargs) -> Div:
    """Component description"""
    return Div(...)
```

### Phase 4: Utilities and Static Assets (Priority: LOW)

#### 4.1 Create Utility Modules
- **Files:** `utils/*.py`
- **Purpose:** Shared utility functions
- **Content:**
  - File handling utilities
  - Validation functions
  - Common helpers

#### 4.2 Organize Static Assets
- **Directory:** `static/`
- **Purpose:** Centralize CSS, JS, images
- **Structure:**
  - `css/` - Custom stylesheets
  - `js/` - Client-side JavaScript
  - `images/` - Static images

## Migration Strategy (Updated) - ZERO DOWNTIME APPROACH WITH AUTOMATED TESTING

### Step 0: Test Infrastructure Setup (Pre-Phase 1)
1. Create comprehensive test suite for current functionality
2. Set up automated testing pipeline
3. Establish baseline test coverage
4. **✅ AUTOMATED VALIDATION** - All tests pass before refactoring begins

### Step 1: Preparation + Initial Testing
1. Create backup of current `app.py` (4,506 lines)
2. Create new directory structure
3. Set up empty module files with `__init__.py`
4. **NEW**: Plan for dual generator system (complex + simple)
5. **NEW**: Create phase-specific test suites
6. **✅ APP REMAINS OPERATIONAL** - No changes to existing code yet
7. **🧪 RUN TESTS**: Baseline functionality validation

### Step 2: Extract Routes (Week 1) - INCREMENTAL EXTRACTION + TESTING
1. Start with simplest routes (dashboard, static pages)
2. **NEW**: Extract simple generator routes first (`simple_routes.py` → `routes/simple_generator.py`)
3. **NEW**: Extract complex generator routes (`/datasets/generator/*` → `routes/generator.py`)
4. **CRITICAL**: Move one route at a time, test immediately
5. Keep old routes as fallback until new routes are verified
6. **✅ APP FULLY FUNCTIONAL** after each route migration
7. **🧪 RUN TESTS**: Route extraction validation after each route moved

### Step 3: Extract Services (Week 2) - PARALLEL DEVELOPMENT + TESTING
1. **NEW**: Move `simple_dataset_generator.py` to `services/` first (smallest, 85 lines)
2. **NEW**: Move `dataset_conversation.py` to `services/` (522 lines)
3. **NEW**: Move `sample_generator.py` to `services/` (685 lines)
4. Update imports gradually, maintain backward compatibility
5. **CRITICAL**: Services work alongside existing code
6. **✅ APP FULLY FUNCTIONAL** - old and new code coexist
7. **🧪 RUN TESTS**: Service layer validation after each service moved

### Step 4: Organize Components (Week 3) - COMPONENT MIGRATION + TESTING
1. Group related UI components
2. **NEW**: Create generator-specific components (`generator_components.py`)
3. Update routes to use new components one by one
4. **CRITICAL**: Maintain existing component imports during transition
5. **✅ APP FULLY FUNCTIONAL** - gradual component replacement
6. **🧪 RUN TESTS**: Component integration validation after each component migrated

### Step 5: Final Cleanup (Week 4) - SAFE REMOVAL + COMPREHENSIVE TESTING
1. Move utilities to `utils/`
2. **NEW**: Consolidate generator configurations
3. Remove old monolithic code **ONLY AFTER** new code is verified
4. Update documentation
5. **✅ APP FULLY FUNCTIONAL** - cleaner, refactored architecture
6. **🧪 RUN TESTS**: Full regression testing suite

## Automated Testing Strategy

### Test Infrastructure (Created in Step 0)

#### Unit Tests (`tests/unit/`)
```python
# tests/unit/test_simple_generator.py
def test_simple_generator_creation()
def test_sample_generation()
def test_error_handling()

# tests/unit/test_dataset_conversation.py  
def test_prompt_analysis()
def test_requirements_extraction()
def test_conversation_flow()

# tests/unit/test_routes.py
def test_dashboard_route()
def test_dataset_routes()
def test_generator_routes()
```

#### Integration Tests (`tests/integration/`)
```python
# tests/integration/test_generator_workflow.py
def test_end_to_end_simple_generation()
def test_end_to_end_complex_generation()
def test_prompt_to_dataset_workflow()

# tests/integration/test_database_operations.py
def test_dataset_crud_operations()
def test_prompt_crud_operations()
def test_optimization_workflow()
```

#### API Tests (`tests/api/`)
```python
# tests/api/test_endpoints.py
def test_all_routes_respond()
def test_generator_endpoints()
def test_dataset_upload_endpoints()
def test_optimization_endpoints()
```

### Testing Commands (Run After Each Phase)

#### Phase 1 Testing:
```bash
# Baseline validation
python -m pytest tests/unit/ -v
python -m pytest tests/integration/ -v
python -m pytest tests/api/ -v
```

#### Phase 2 Testing (Route Extraction):
```bash
# Route-specific validation
python -m pytest tests/unit/test_routes.py -v
python -m pytest tests/api/test_endpoints.py -v
python -m pytest tests/integration/test_generator_workflow.py -v
```

#### Phase 3 Testing (Service Extraction):
```bash
# Service layer validation
python -m pytest tests/unit/test_simple_generator.py -v
python -m pytest tests/unit/test_dataset_conversation.py -v
python -m pytest tests/integration/test_database_operations.py -v
```

#### Phase 4 Testing (Component Organization):
```bash
# Component integration validation
python -m pytest tests/integration/ -v
python -m pytest tests/api/ -v
```

#### Phase 5 Testing (Final Cleanup):
```bash
# Full regression testing
python -m pytest tests/ -v --cov=. --cov-report=html
python -m pytest tests/performance/ -v  # Performance regression tests
```

## Zero-Downtime Guarantees with Automated Validation

### After Phase 1: ✅ **100% Operational + TESTED**
- All existing functionality intact
- New directory structure ready
- **🧪 All baseline tests pass**

### After Phase 2: ✅ **100% Operational + TESTED** 
- Routes extracted and working
- Old routes removed only after new routes tested
- **🧪 All route tests pass**

### After Phase 3: ✅ **100% Operational + TESTED**
- Services extracted and integrated
- Business logic properly separated
- **🧪 All service tests pass**

### After Phase 4: ✅ **100% Operational + TESTED**
- Components organized and reusable
- UI improvements implemented
- **🧪 All integration tests pass**

### After Phase 5: ✅ **100% OPERATIONAL + IMPROVED + FULLY TESTED**
- Clean, maintainable architecture
- Better performance and organization
- **🧪 100% test coverage achieved**

## Test Automation Pipeline

### Continuous Integration Setup:
```yaml
# .github/workflows/refactoring-tests.yml
name: Refactoring Validation
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Setup Python
        uses: actions/setup-python@v2
      - name: Install dependencies
        run: pip install -r requirements.txt pytest pytest-cov
      - name: Run unit tests
        run: pytest tests/unit/ -v
      - name: Run integration tests  
        run: pytest tests/integration/ -v
      - name: Run API tests
        run: pytest tests/api/ -v
      - name: Generate coverage report
        run: pytest --cov=. --cov-report=xml
```

### Pre-Commit Hooks:
```bash
# Run tests before each commit during refactoring
pre-commit install
# Automatically runs: pytest tests/unit/ tests/integration/
```

## Benefits of Refactoring

### Maintainability
- **Single Responsibility:** Each module has one clear purpose
- **Easier Testing:** Isolated components can be unit tested
- **Code Navigation:** Developers can quickly find relevant code

### Scalability
- **Feature Addition:** New features can be added without touching core files
- **Team Development:** Multiple developers can work on different modules
- **Performance:** Smaller modules load faster

### Code Quality
- **Separation of Concerns:** UI, business logic, and data access are separated
- **Reusability:** Components and services can be reused across features
- **Type Safety:** Better type hints and validation

## Risk Mitigation

### Testing Strategy
1. **Incremental Migration:** Move one module at a time
2. **Regression Testing:** Test each feature after migration
3. **Rollback Plan:** Keep backup of working version

### Compatibility
1. **Import Compatibility:** Maintain backward compatibility during transition
2. **Database Schema:** No database changes required
3. **API Compatibility:** Maintain existing route URLs

## Success Metrics (Updated)

### Code Quality Metrics
- **Lines per File:** Target <500 lines per file (currently: app.py = 4,506 lines)
- **Cyclomatic Complexity:** Reduce complexity per function
- **Test Coverage:** Achieve >80% test coverage
- **NEW**: Generator Separation: Complex vs Simple generators properly isolated

### Development Metrics
- **Feature Development Time:** Reduce time to add new features
- **Bug Fix Time:** Reduce time to locate and fix bugs
- **Onboarding Time:** Reduce time for new developers to understand codebase
- **NEW**: Generator Maintenance: Easier to maintain dual generator approaches

### Architecture Metrics
- **Route Distribution:** No single file >500 lines
- **Service Isolation:** Clear separation between dataset generation approaches
- **Component Reusability:** UI components shared across generator types
- **NEW**: Generator Flexibility: Easy to add new generation approaches

## Timeline (Updated)

| Phase | Duration | Deliverables | New Considerations |
|-------|----------|-------------|-------------------|
| Phase 1 | Week 1 | Core infrastructure, route extraction | Extract both generator route systems |
| Phase 2 | Week 2 | Service layer, business logic extraction | Unify dual generator services |
| Phase 3 | Week 3 | Component organization, UI improvements | Create generator-specific components |
| Phase 4 | Week 4 | Utilities, static assets, final cleanup | Consolidate generator configurations |

## Recent Changes Impact Assessment

### Positive Impacts:
✅ **Clean Simple Generator**: `simple_dataset_generator.py` (85 lines) is already well-structured
✅ **Modular Routes**: `simple_routes.py` (140 lines) demonstrates good separation
✅ **Service Pattern**: New generators follow service-oriented architecture

### Challenges Added:
⚠️ **Dual Complexity**: Now have both complex and simple generation approaches
⚠️ **Route Duplication**: Similar functionality in different route handlers
⚠️ **Service Overlap**: Both generators handle similar core functionality

### Refactoring Priorities (Updated):
1. **HIGH**: Extract generator routes first (they're newest and cleanest)
2. **HIGH**: Create unified generator service interface
3. **MEDIUM**: Consolidate shared generator functionality
4. **LOW**: Maintain backward compatibility during transition

## Approval Required

Please review this plan and approve:

- [ ] Overall architecture and structure
- [ ] Migration strategy and timeline
- [ ] Risk mitigation approach
- [ ] Success metrics and goals

**Next Steps After Approval:**
1. Create backup and new directory structure
2. Begin Phase 1 implementation
3. Set up testing framework
4. Start incremental migration

---

**Document Version:** 1.0  
**Created:** August 22, 2025  
**Author:** Amazon Q  
**Status:** Pending Approval
