# Metric Builder Feature - Implementation Plan

## Overview

The Metric Builder is a comprehensive feature that allows users to create custom evaluation metrics for their prompt optimization tasks through both visual and natural language interfaces. This addresses the core issue where MetricAdapter is an Abstract Base Class requiring concrete implementations for proper evaluation scoring.

## Problem Statement

Currently, optimization evaluations return 0 scores because:
- MetricAdapter is an ABC (Abstract Base Class) requiring concrete implementation
- Users cannot define custom metrics for their specific use cases
- No way to specify evaluation criteria for different output formats (JSON, text, categories, etc.)
- Optimization runs fail or produce meaningless scores without proper metrics

## Solution Architecture

### Core Components
1. **Metric Builder UI** - Visual interface for defining metrics
2. **Natural Language Processor** - Converts text descriptions to metric logic
3. **Code Generator** - Creates concrete MetricAdapter subclasses
4. **Database Storage** - Persists metric configurations
5. **Integration Layer** - Connects metrics to optimization runs

## Database Schema

### New Table: `metrics`
```sql
CREATE TABLE metrics (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT,
    dataset_format TEXT NOT NULL,  -- 'json', 'text', 'classification'
    scoring_criteria TEXT NOT NULL, -- JSON string of criteria
    generated_code TEXT NOT NULL,   -- Python code for MetricAdapter
    natural_language_input TEXT,    -- Original NL description
    created TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_used TIMESTAMP,
    usage_count INTEGER DEFAULT 0
);
```

### Updated Table: `optimizations`
```sql
-- Add metric_id column to existing optimizations table
ALTER TABLE optimizations ADD COLUMN metric_id TEXT REFERENCES metrics(id);
```

## User Interface Design

### Navigation Structure
```
Home → Prompts → Datasets → **Metrics** → Optimizations → Results
```

### Metric Builder Page (`/metrics`)

#### Header Section
- **Page Title**: "Metric Builder"
- **Subtitle**: "Define custom evaluation metrics for your optimization tasks"
- **Action Buttons**: 
  - "Create New Metric" (primary button)
  - "Import from Template" (secondary button)

#### Metrics List Section
- **Card-based layout** showing existing metrics
- **Each card displays**:
  - Metric name and description
  - Dataset format compatibility
  - Usage count and last used date
  - Actions: Edit, Duplicate, Delete, Test
- **Search and filter** by name, format, creation date

#### Create/Edit Metric Modal
- **Two-tab interface**:
  - Tab 1: "Natural Language" 
  - Tab 2: "Visual Builder"
- **Preview section** showing generated code
- **Test section** with sample data input/output

## Feature Implementation Details

### 1. Natural Language Interface

#### Input Components
- **Large text area** for natural language description
- **Example prompts** to guide users:
  - "Score based on correct sentiment and urgency classification"
  - "Evaluate JSON output for category accuracy and completeness"
  - "Check if response contains required fields and proper format"

#### Processing Logic
- **Parse natural language** to identify:
  - Output format (JSON, text, classification)
  - Scoring criteria (accuracy, completeness, format validation)
  - Weighting preferences
- **Generate scoring logic** based on parsed intent
- **Show preview** of generated MetricAdapter code

#### Example NL Inputs and Outputs
```
Input: "Score based on correct sentiment (positive/negative/neutral) and urgency (high/medium/low)"
Output: Generates metric checking sentiment and urgency fields with equal weighting

Input: "Evaluate JSON with categories field containing boolean values, weight category accuracy 70% and format validation 30%"
Output: Generates metric with weighted scoring for categories and JSON validation
```

### 2. Visual Builder Interface

#### Dataset Format Selection
- **Radio buttons** for format types:
  - JSON with specific fields
  - Text classification
  - Multi-label classification
  - Custom format

#### Scoring Criteria Builder
- **Dynamic form** based on selected format
- **For JSON format**:
  - Field name inputs
  - Field type selection (boolean, string, number, array)
  - Scoring method (exact match, similarity, contains)
  - Weight slider (0-100%)
- **For text classification**:
  - Expected classes/categories
  - Matching method (exact, fuzzy, semantic)
  - Case sensitivity toggle

#### Visual Preview
- **Live code preview** showing generated MetricAdapter
- **Sample data testing** with input/output examples
- **Score calculation preview** showing how metrics are computed

### 3. Code Generation Engine

#### Template System
```python
# Base template for JSON metrics
class Generated{MetricName}Metric(MetricAdapter):
    def parse_json(self, input_string: str):
        # JSON parsing logic with fallbacks
        
    def _calculate_metrics(self, y_pred: Any, y_true: Any) -> Dict:
        # Generated scoring logic based on criteria
        
    def apply(self, y_pred: Any, y_true: Any):
        return self._calculate_metrics(y_pred, y_true)
        
    def batch_apply(self, y_preds: List[Any], y_trues: List[Any]):
        # Batch processing logic
```

#### Generation Rules
- **Field validation** for JSON formats
- **Weighted scoring** based on user preferences
- **Error handling** for malformed inputs
- **Consistent return format** for optimization compatibility

### 4. Integration with Optimization Flow

#### Updated Optimization Page
- **New dropdown**: "Evaluation Metric"
- **Options**:
  - "Select a metric..." (default)
  - List of user-created metrics
  - "Create new metric" (opens metric builder)

#### Optimization Execution
- **Load selected metric** from database
- **Instantiate generated MetricAdapter** class
- **Use in NovaPromptOptimizer** for proper scoring
- **Store metric_id** in optimization record

## Implementation Phases

### Phase 1: Database and Backend (Week 1)
- [ ] Create metrics table schema
- [ ] Add metric_id to optimizations table
- [ ] Implement CRUD operations for metrics
- [ ] Create metric code generation engine
- [ ] Add metric loading to SDK worker

### Phase 2: Basic UI (Week 2)
- [ ] Create metrics page with navigation
- [ ] Implement metrics list view
- [ ] Add create/edit metric modal
- [ ] Build natural language input interface
- [ ] Add code preview functionality

### Phase 3: Visual Builder (Week 3)
- [ ] Implement visual builder interface
- [ ] Add dataset format detection
- [ ] Create dynamic form generation
- [ ] Build scoring criteria configurator
- [ ] Add live preview and testing

### Phase 4: Integration (Week 4)
- [ ] Update optimization page with metric dropdown
- [ ] Integrate metric selection with optimization flow
- [ ] Add metric usage tracking
- [ ] Implement metric templates and examples
- [ ] Add comprehensive testing and validation

## Technical Specifications

### Frontend Components

#### MetricBuilder.py
```python
def create_metrics_page():
    return Div(
        create_navbar("metrics"),
        Main(
            create_metrics_header(),
            create_metrics_list(),
            create_metric_modal(),
            cls="main-content"
        )
    )
```

#### MetricModal.py
```python
def create_metric_modal():
    return Div(
        # Two-tab interface
        create_tab_system([
            {"label": "Natural Language", "content": create_nl_interface()},
            {"label": "Visual Builder", "content": create_visual_builder()}
        ]),
        # Preview and test sections
        create_code_preview(),
        create_test_interface(),
        cls="metric-modal hidden"
    )
```

### Backend Services

#### MetricService.py
```python
class MetricService:
    def generate_metric_code(self, criteria: Dict) -> str:
        # Generate MetricAdapter subclass code
        
    def parse_natural_language(self, description: str) -> Dict:
        # Parse NL input to scoring criteria
        
    def validate_metric(self, code: str) -> bool:
        # Validate generated metric code
        
    def test_metric(self, code: str, sample_data: List) -> Dict:
        # Test metric with sample data
```

### Database Operations

#### metrics.py
```python
def create_metric(name: str, criteria: Dict, code: str) -> str:
    # Create new metric record
    
def get_metrics() -> List[Dict]:
    # Get all user metrics
    
def get_metric(metric_id: str) -> Dict:
    # Get specific metric
    
def update_metric_usage(metric_id: str):
    # Update usage statistics
```

## User Experience Flow

### Creating a New Metric
1. **Navigate to Metrics page**
2. **Click "Create New Metric"**
3. **Choose input method** (Natural Language or Visual Builder)
4. **Define scoring criteria**:
   - NL: "Score based on sentiment accuracy and JSON format validation"
   - Visual: Select fields, weights, and validation rules
5. **Preview generated code**
6. **Test with sample data**
7. **Save metric** with name and description

### Using Metric in Optimization
1. **Navigate to Optimization page**
2. **Select prompt and dataset**
3. **Choose evaluation metric** from dropdown
4. **Configure optimization settings**
5. **Start optimization** with proper metric scoring

## Error Handling and Validation

### Metric Creation
- **Validate natural language** input for clarity
- **Check generated code** for syntax errors
- **Test metric** with sample data before saving
- **Prevent duplicate** metric names

### Optimization Integration
- **Verify metric compatibility** with dataset format
- **Handle missing metrics** gracefully
- **Provide fallback** to default scoring if metric fails
- **Log metric errors** for debugging

## Success Metrics

### User Adoption
- **Number of custom metrics** created per user
- **Metric reuse rate** across optimizations
- **User preference** (NL vs Visual Builder)

### Technical Performance
- **Metric generation success rate**
- **Optimization completion rate** with custom metrics
- **Score accuracy** compared to manual evaluation

### User Experience
- **Time to create** a functional metric
- **User satisfaction** with generated metrics
- **Support ticket reduction** for evaluation issues

## Future Enhancements

### Advanced Features
- **Metric templates** for common use cases
- **Collaborative metrics** sharing between users
- **A/B testing** of different metric configurations
- **Automated metric suggestions** based on dataset analysis

### Integration Improvements
- **Real-time metric validation** during creation
- **Metric performance analytics** and optimization
- **Export/import** metric configurations
- **API access** for programmatic metric creation

## Risk Mitigation

### Technical Risks
- **Code generation failures**: Implement robust templates and validation
- **Performance issues**: Cache generated metrics and optimize execution
- **Security concerns**: Validate and sandbox generated code

### User Experience Risks
- **Complex interface**: Provide clear examples and guided tutorials
- **Learning curve**: Offer templates and common patterns
- **Integration confusion**: Clear documentation and error messages

## Conclusion

The Metric Builder feature addresses a critical gap in the Nova Prompt Optimizer by enabling users to create custom evaluation metrics tailored to their specific use cases. By providing both natural language and visual interfaces, we ensure accessibility for users with different technical backgrounds while maintaining the flexibility needed for complex evaluation scenarios.

The phased implementation approach allows for iterative development and user feedback incorporation, ensuring the final product meets real-world needs and integrates seamlessly with the existing optimization workflow.
