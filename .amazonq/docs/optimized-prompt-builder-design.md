# Optimized Prompt Builder - Design & Implementation Plan

## 📋 **Overview**

The Optimized Prompt Builder is a declarative prompt construction feature that leverages the Nova SDK's built-in best practices and optimization capabilities. It provides a user-friendly interface for creating high-quality prompts that follow Nova's proven patterns.

## 🎯 **Objectives**

- **Democratize prompt engineering** - Enable non-technical users to create optimized prompts
- **Leverage Nova SDK best practices** - Use proven patterns from the SDK's template system
- **Integrate seamlessly** - Work with existing optimization and evaluation workflows
- **Provide real-time feedback** - Show prompt structure and validation as users build

## 🏗️ **Architecture Design**

### **Core Components**

```
┌─────────────────────────────────────────────────────────────┐
│                    Frontend UI Layer                        │
├─────────────────────────────────────────────────────────────┤
│  Builder Form  │  Preview Panel  │  Validation Panel       │
├─────────────────────────────────────────────────────────────┤
│                 Prompt Builder Service                      │
├─────────────────────────────────────────────────────────────┤
│              Nova SDK Integration Layer                     │
├─────────────────────────────────────────────────────────────┤
│    PromptAdapter  │  Nova Meta Prompter  │  Optimization   │
└─────────────────────────────────────────────────────────────┘
```

### **Data Flow**

1. **User Input** → Builder Form (Task, Context, Instructions, Format)
2. **Real-time Preview** → Generated System/User Prompts
3. **Validation** → Best Practice Compliance Check
4. **Build** → PromptAdapter Creation
5. **Optimize** → Nova Meta Prompter Enhancement
6. **Save** → Database Storage for Reuse

## 🔧 **Implementation Plan**

### **Phase 1: Core Builder Service (Week 1)**

#### **New Files**
```
frontend/services/prompt_builder.py
```

**Key Classes:**
```python
class OptimizedPromptBuilder:
    """Declarative prompt builder using Nova best practices"""
    
    def __init__(self):
        self.task: str = ""
        self.context: List[str] = []
        self.instructions: List[str] = []
        self.response_format: List[str] = []
        self.variables: Set[str] = set()
        self.metadata: Dict[str, Any] = {}
    
    def set_task(self, description: str) -> 'OptimizedPromptBuilder'
    def add_context(self, context: str) -> 'OptimizedPromptBuilder'
    def add_instruction(self, instruction: str) -> 'OptimizedPromptBuilder'
    def set_response_format(self, format_spec: str) -> 'OptimizedPromptBuilder'
    def add_variable(self, name: str) -> 'OptimizedPromptBuilder'
    def validate(self) -> Dict[str, List[str]]
    def build(self) -> PromptAdapter
    def preview(self) -> Dict[str, str]

class NovaPromptTemplate:
    """Nova SDK template integration"""
    
    @staticmethod
    def apply_best_practices(builder: OptimizedPromptBuilder) -> Dict[str, str]
    @staticmethod
    def validate_structure(prompt_dict: Dict[str, str]) -> List[str]
```

#### **Modified Files**
```
frontend/config.py  # Add prompt builder settings
```

### **Phase 2: Database Integration (Week 1)**

#### **New Files**
```
frontend/migrations/add_prompt_builder.py
```

**Database Schema:**
```sql
CREATE TABLE prompt_templates (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT,
    task TEXT NOT NULL,
    context_items TEXT,  -- JSON array
    instructions TEXT,   -- JSON array
    response_format TEXT, -- JSON array
    variables TEXT,      -- JSON array
    metadata TEXT,       -- JSON object
    created_date TEXT,
    last_modified TEXT
);

CREATE TABLE prompt_builder_sessions (
    id TEXT PRIMARY KEY,
    template_id TEXT,
    current_state TEXT,  -- JSON object
    created_date TEXT,
    FOREIGN KEY (template_id) REFERENCES prompt_templates(id)
);
```

#### **Modified Files**
```
frontend/database.py  # Add prompt builder methods
```

**New Database Methods:**
```python
def create_prompt_template(self, name: str, builder_data: Dict) -> str
def get_prompt_template(self, template_id: str) -> Dict
def list_prompt_templates(self) -> List[Dict]
def update_prompt_template(self, template_id: str, builder_data: Dict) -> bool
def delete_prompt_template(self, template_id: str) -> bool
def save_builder_session(self, session_data: Dict) -> str
def load_builder_session(self, session_id: str) -> Dict
```

### **Phase 3: UI Components (Week 2)**

#### **New Files**
```
frontend/components/prompt_builder.py
frontend/templates/prompt_builder/builder_form.py
frontend/templates/prompt_builder/preview_panel.py
frontend/templates/prompt_builder/validation_panel.py
```

**UI Component Structure:**
```python
# Builder Form Components
def task_input_section() -> Div
def context_builder_section() -> Div
def instructions_builder_section() -> Div
def response_format_section() -> Div
def variables_manager_section() -> Div

# Preview Components
def system_prompt_preview(prompt_text: str) -> Div
def user_prompt_preview(prompt_text: str) -> Div
def combined_preview(system: str, user: str) -> Div

# Validation Components
def validation_results(issues: List[str]) -> Div
def best_practices_checklist(checks: Dict[str, bool]) -> Div
def improvement_suggestions(suggestions: List[str]) -> Div
```

#### **Modified Files**
```
frontend/components/layout.py  # Add prompt builder navigation
```

### **Phase 4: Web Routes & Integration (Week 2)**

#### **New Files**
```
frontend/routes/prompt_builder.py
```

**Route Structure:**
```python
@app.get("/prompt-builder")
async def prompt_builder_page()

@app.post("/prompt-builder/preview")
async def preview_prompt(request)

@app.post("/prompt-builder/validate")
async def validate_prompt(request)

@app.post("/prompt-builder/build")
async def build_prompt(request)

@app.post("/prompt-builder/save-template")
async def save_template(request)

@app.get("/prompt-builder/templates")
async def list_templates()

@app.get("/prompt-builder/template/{template_id}")
async def load_template(template_id: str)
```

#### **Modified Files**
```
frontend/app.py           # Add prompt builder routes
frontend/simple_routes.py # Add "Build Optimized Prompt" option
```

### **Phase 5: SDK Integration & Optimization (Week 3)**

#### **Modified Files**
```
frontend/sdk_worker.py  # Integrate OptimizedPromptBuilder
```

**Integration Points:**
```python
def create_prompt_from_builder(builder_data: Dict) -> PromptAdapter
def optimize_built_prompt(prompt_adapter: PromptAdapter, mode: str = "pro") -> PromptAdapter
def evaluate_built_prompt(prompt_adapter: PromptAdapter, dataset_id: str, metric_id: str) -> Dict
```

## 📊 **User Experience Flow**

### **1. Builder Interface**
```
┌─────────────────────────────────────────────────────────────┐
│  Optimized Prompt Builder                                   │
├─────────────────────────────────────────────────────────────┤
│  Task Description: [Text Area]                             │
│  Context Items:    [+ Add Context] [List of contexts]      │
│  Instructions:     [+ Add Rule] [List of instructions]     │
│  Response Format:  [Format Builder] [Preview]              │
│  Variables:        [+ Add Variable] [Variable list]        │
├─────────────────────────────────────────────────────────────┤
│  [Preview] [Validate] [Build Prompt] [Save Template]       │
└─────────────────────────────────────────────────────────────┘
```

### **2. Real-time Preview**
```
┌─────────────────────────────────────────────────────────────┐
│  Generated Prompt Preview                                   │
├─────────────────────────────────────────────────────────────┤
│  System Prompt:                                            │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │ Task: [Generated task description]                     │ │
│  │ Context: [Context items formatted]                     │ │
│  │ Instructions: [Instructions with MUST/DO NOT]          │ │
│  │ Response Format: [Structured format requirements]      │ │
│  └─────────────────────────────────────────────────────────┘ │
│                                                             │
│  User Prompt:                                              │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │ [User-facing prompt with variables]                    │ │
│  └─────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

### **3. Validation Panel**
```
┌─────────────────────────────────────────────────────────────┐
│  Best Practices Validation                                  │
├─────────────────────────────────────────────────────────────┤
│  ✅ Task clearly defined                                    │
│  ✅ Context provides sufficient information                 │
│  ✅ Instructions use strong directive language              │
│  ✅ Response format is specific                             │
│  ⚠️  Consider adding more context for complex tasks         │
│  ❌ Missing required variables in user prompt               │
├─────────────────────────────────────────────────────────────┤
│  Suggestions:                                              │
│  • Add examples to clarify expected output                 │
│  • Use "MUST" instead of "should" for requirements         │
└─────────────────────────────────────────────────────────────┘
```

## 🔄 **Integration with Existing Features**

### **Flexible Generator Enhancement**
- Add "Build Optimized Prompt" button alongside existing options
- Allow users to start with builder or import existing prompts
- Seamless transition from builder to optimization workflow

### **Optimization Workflow**
- Built prompts automatically compatible with existing optimization
- Support for "Optimize Further" with builder-created prompts
- Evaluation integration with custom metrics

### **Dataset Integration**
- Builder prompts work with existing dataset management
- Variable mapping to dataset columns
- Automatic validation against dataset structure

## 📈 **Success Metrics**

### **User Adoption**
- Number of prompts created via builder vs manual creation
- User retention and repeat usage of builder feature
- Time reduction in prompt creation process

### **Quality Metrics**
- Optimization score improvements for builder-created prompts
- Validation compliance rates
- User satisfaction with generated prompts

### **Technical Metrics**
- Builder session completion rates
- Template reuse frequency
- Integration success with existing workflows

## 🚀 **Deployment Strategy**

### **Phase 1 Rollout (Week 1)**
- Core builder service with basic validation
- Simple database integration
- Internal testing with sample prompts

### **Phase 2 Rollout (Week 2)**
- Full UI implementation
- Real-time preview and validation
- Template management system

### **Phase 3 Rollout (Week 3)**
- Complete SDK integration
- Optimization workflow integration
- Production deployment with monitoring

## 🔧 **Technical Considerations**

### **Performance**
- Real-time preview updates with debouncing
- Efficient template storage and retrieval
- Minimal impact on existing optimization workflows

### **Scalability**
- Template sharing and collaboration features
- Bulk template operations
- Export/import capabilities

### **Maintenance**
- Automated testing for prompt generation
- Version control for template changes
- Monitoring and error tracking

## 🧪 **Testing Strategy**

### **Unit Tests**

#### **New Test Files**
```
frontend/tests/unit/test_prompt_builder.py
frontend/tests/unit/test_nova_prompt_template.py
frontend/tests/unit/test_prompt_builder_database.py
frontend/tests/unit/test_prompt_builder_routes.py
```

**Test Coverage:**
```python
# test_prompt_builder.py
class TestOptimizedPromptBuilder:
    def test_set_task_updates_task_field()
    def test_add_context_appends_to_list()
    def test_add_instruction_with_validation()
    def test_set_response_format_validates_structure()
    def test_add_variable_updates_set()
    def test_validate_returns_issues_for_incomplete_prompt()
    def test_build_creates_valid_prompt_adapter()
    def test_preview_generates_system_and_user_prompts()

# test_nova_prompt_template.py
class TestNovaPromptTemplate:
    def test_apply_best_practices_formats_correctly()
    def test_validate_structure_catches_missing_sections()
    def test_variable_injection_preserves_all_variables()
    def test_system_user_prompt_separation()

# test_prompt_builder_database.py
class TestPromptBuilderDatabase:
    def test_create_prompt_template_returns_id()
    def test_get_prompt_template_returns_correct_data()
    def test_list_prompt_templates_pagination()
    def test_update_prompt_template_modifies_existing()
    def test_delete_prompt_template_removes_record()
    def test_save_builder_session_stores_state()

# test_prompt_builder_routes.py
class TestPromptBuilderRoutes:
    def test_prompt_builder_page_renders()
    def test_preview_prompt_returns_formatted_output()
    def test_validate_prompt_returns_validation_results()
    def test_build_prompt_creates_prompt_adapter()
    def test_save_template_stores_in_database()
```

### **Integration Tests**

#### **New Test Files**
```
frontend/tests/integration/test_prompt_builder_workflow.py
frontend/tests/integration/test_sdk_integration.py
frontend/tests/integration/test_optimization_pipeline.py
```

**Integration Test Coverage:**
```python
# test_prompt_builder_workflow.py
class TestPromptBuilderWorkflow:
    def test_complete_builder_to_optimization_flow()
    def test_template_save_and_reload_workflow()
    def test_builder_with_existing_dataset_integration()
    def test_validation_feedback_loop()

# test_sdk_integration.py
class TestSDKIntegration:
    def test_prompt_adapter_creation_from_builder()
    def test_nova_meta_prompter_optimization()
    def test_miprov2_optimization_compatibility()
    def test_evaluation_with_built_prompts()

# test_optimization_pipeline.py
class TestOptimizationPipeline:
    def test_builder_prompt_through_full_optimization()
    def test_optimize_further_with_builder_prompts()
    def test_baseline_vs_optimized_evaluation()
    def test_prompt_candidate_extraction()
```

### **Test Data & Fixtures**

#### **New Test Files**
```
frontend/tests/fixtures/prompt_builder_fixtures.py
frontend/tests/data/sample_builder_templates.json
frontend/tests/data/validation_test_cases.json
```

**Test Fixtures:**
```python
# prompt_builder_fixtures.py
@pytest.fixture
def sample_builder_data():
    return {
        "task": "Analyze customer feedback sentiment",
        "context": ["Customer support context", "Product feedback analysis"],
        "instructions": ["Use positive/negative/neutral classification", "Provide confidence scores"],
        "response_format": ["JSON format with sentiment and confidence"],
        "variables": ["customer_feedback"]
    }

@pytest.fixture
def invalid_builder_data():
    return {"task": "", "context": [], "instructions": []}

@pytest.fixture
def mock_prompt_adapter():
    # Mock PromptAdapter for testing
    pass

@pytest.fixture
def test_database():
    # In-memory test database
    pass
```

## 📊 **Test Execution Strategy**

### **Local Testing**
```bash
# Run unit tests
pytest frontend/tests/unit/test_prompt_builder*.py -v

# Run integration tests  
pytest frontend/tests/integration/test_prompt_builder*.py -v

# Run all prompt builder tests
pytest frontend/tests/ -k "prompt_builder" -v

# Generate coverage report
pytest --cov=frontend/services/prompt_builder --cov-report=html
```

### **Test Coverage Goals**
- **Unit Tests**: 95% coverage for core builder logic
- **Integration Tests**: 85% coverage for workflow paths
- **Route Tests**: 90% coverage for API endpoints
- **Database Tests**: 100% coverage for CRUD operations

### **Performance Tests**
```python
# test_prompt_builder_performance.py
class TestPromptBuilderPerformance:
    def test_preview_generation_under_100ms()
    def test_validation_response_time()
    def test_template_loading_performance()
    def test_concurrent_builder_sessions()
```

## 🔧 **Modified Implementation Plan**

### **Phase 1: Core Builder Service + Tests (Week 1)**

#### **New Files**
```
frontend/services/prompt_builder.py
frontend/tests/unit/test_prompt_builder.py
frontend/tests/unit/test_nova_prompt_template.py
frontend/tests/fixtures/prompt_builder_fixtures.py
```

### **Phase 2: Database Integration + Tests (Week 1)**

#### **New Files**
```
frontend/migrations/add_prompt_builder.py
frontend/tests/unit/test_prompt_builder_database.py
frontend/tests/integration/test_prompt_builder_workflow.py
```

### **Phase 3: UI Components + Route Tests (Week 2)**

#### **New Files**
```
frontend/components/prompt_builder.py
frontend/routes/prompt_builder.py
frontend/tests/unit/test_prompt_builder_routes.py
frontend/tests/data/sample_builder_templates.json
```

### **Phase 4: SDK Integration + Integration Tests (Week 3)**

#### **New Files**
```
frontend/tests/integration/test_sdk_integration.py
frontend/tests/integration/test_optimization_pipeline.py
frontend/tests/data/validation_test_cases.json
```

## 📝 **Updated File Summary**

### **New Files (15)**
```
# Core Implementation (6)
frontend/services/prompt_builder.py
frontend/components/prompt_builder.py
frontend/routes/prompt_builder.py
frontend/templates/prompt_builder/builder_form.py
frontend/templates/prompt_builder/preview_panel.py
frontend/migrations/add_prompt_builder.py

# Unit Tests (4)
frontend/tests/unit/test_prompt_builder.py
frontend/tests/unit/test_nova_prompt_template.py
frontend/tests/unit/test_prompt_builder_database.py
frontend/tests/unit/test_prompt_builder_routes.py

# Integration Tests (3)
frontend/tests/integration/test_prompt_builder_workflow.py
frontend/tests/integration/test_sdk_integration.py
frontend/tests/integration/test_optimization_pipeline.py

# Test Data & Fixtures (2)
frontend/tests/fixtures/prompt_builder_fixtures.py
frontend/tests/data/sample_builder_templates.json
```

### **Modified Files (7)**
```
frontend/app.py
frontend/database.py
frontend/components/layout.py
frontend/sdk_worker.py
frontend/simple_routes.py
frontend/config.py
frontend/requirements-test.txt  # Add testing dependencies
```

**Total Implementation: 22 files (15 new, 7 modified), 3-week timeline with comprehensive testing**

This design provides a comprehensive yet minimal approach to implementing the Optimized Prompt Builder, leveraging existing infrastructure while adding powerful new capabilities for prompt creation and optimization.
