# AI Dataset Generation Feature

## Feature Overview
**Feature Name:** AI-Powered Dataset Generation
**Priority:** High
**Estimated Effort:** Medium

## Problem Statement
- Users need evaluation datasets to optimize prompts but creating them manually is time-consuming
- Current workflow requires users to bring their own datasets
- Users may not have sufficient or diverse evaluation data
- Creating realistic test cases requires domain expertise

## Solution Design
### User Experience - Detailed Workflow

**Step 1: Entry Point**
- Navigate to Datasets page
- Two options: "Add Dataset" (existing) or "Generate Dataset" (new AI feature)
- Click "Generate Dataset" → Launch wizard

**Step 2: Prompt Selection (Optional)**
- Option to select existing prompt as reference
- If selected: AI analyzes prompt to understand requirements
- If no prompt: Start from scratch

**Step 3: Conversational Requirements Gathering**
- AI-powered conversational interface
- AI walks user through decision points using comprehensive checklist:

**Core Requirements Checklist:**
- [ ] **Role and Persona Definition**
  - What role should the LLM adopt? (e.g., "customer support agent", "medical expert")
  - What persona characteristics are important?
  - What domain expertise is required?

- [ ] **Task Description**
  - What is the specific goal of the dataset?
  - What type of interactions/scenarios to generate?
  - What is the intended use case for this data?

- [ ] **Data Characteristics**
  - [ ] **Diversity Requirements**
    - Variations in phrasing and language style
    - Different complexity levels (simple to complex)
    - Tone variations (formal, casual, frustrated, etc.)
    - Intent variations within the domain
  - [ ] **Realism Requirements**
    - Real-world scenario authenticity
    - Natural user behavior patterns
    - Contextually appropriate responses
  - [ ] **Edge Cases**
    - Challenging or unusual inputs
    - Boundary conditions
    - Error scenarios and exceptions
    - Adversarial cases
  - [ ] **Specific Constraints**
    - Length limitations (character/word counts)
    - Sentiment distribution requirements
    - Language or terminology restrictions
    - Compliance or safety requirements

- [ ] **Input Data Format**
  - What type of input data? (text, structured data, etc.)
  - Input complexity and structure
  - Required input fields/attributes

- [ ] **Output Data Format** 
  - What should the model output? (classification, extraction, generation)
  - Output structure and fields
  - Expected response format

- [ ] **Dataset Output Format**
  - File format: JSONL or CSV (user selectable)
  - **REQUIRED Column Structure:**
    - `input` - The input data/prompt for the model
    - `answer` - The expected output/response from the model
  - No custom column names - standardized format for optimization pipeline

- AI asks clarifying questions until all checklist items complete
- Validates understanding before proceeding to sample generation

**Step 4: Initial Sample Generation**
- Generate 5 sample records based on gathered requirements
- Display each record separately for review

**Step 5: Open Coding Annotation**
- User can annotate each record individually
- Annotations inform AI about:
  - Quality issues
  - Missing elements
  - Desired improvements
  - Format corrections
- AI iterates on records and generation prompt based on annotations

**Step 6: Final Configuration**
- Specify number of records to generate (10-1000)
- Select dataset output format: JSONL or CSV
- **Standardized columns:** `input` and `answer` (hardcoded)
- Generate full dataset with consistent structure
- Save to database and uploads/ directory

### Technical Design
- **AI Service Integration:** Use Nova models for dataset generation should be selectable
- **Preview System:** Show generated samples before saving
- **Edit Capability:** Allow users to modify individual samples
- **Format Validation:** Ensure generated data matches expected schema
- **Storage Integration:** Save to existing dataset management system

## Feature Requirements
### Functional Requirements
- [ ] Natural language dataset description input
- [ ] AI-powered sample generation using Nova models
- [ ] Preview interface showing generated samples
- [ ] Individual sample editing capability
- [ ] Batch regeneration of samples
- [ ] Dataset size specification (10-1000 samples)
- [ ] Output format specification (JSON structure)
- [ ] Save generated dataset to database
- [ ] Integration with existing optimization pipeline

### Non-Functional Requirements
- [ ] Generate 50 samples in under 30 seconds
- [ ] Support datasets up to 1000 samples
- [ ] Validate JSON structure of generated samples
- [ ] Handle AI generation failures gracefully

## Implementation Checklist
### Backend Tasks
- [ ] Create conversational AI service for comprehensive requirements gathering
- [ ] Implement role/persona definition system
- [ ] Build task description clarification logic
- [ ] Add data characteristics specification (diversity, realism, edge cases, constraints)
- [ ] Create format specification system (input/output/dataset formats)
- [ ] Implement prompt analysis service (if prompt provided)
- [ ] Build comprehensive checklist validation system
- [ ] Create sample generation service (5 initial records)
- [ ] Implement annotation processing system
- [ ] Add iterative refinement logic based on annotations
- [ ] Create batch dataset generation service
- [ ] Add generator state management with checklist tracking
- [ ] Error handling for each step
- [ ] Standardized dataset format with `input` and `answer` columns
- [ ] JSONL and CSV output format support
- [ ] Integration with existing dataset storage (database + uploads/)

### Frontend Tasks
- [ ] Add "Generate Dataset" button to Datasets page
- [ ] Create multi-step generator component
- [ ] Build prompt selection interface (optional)
- [ ] Implement conversational AI interface
- [ ] Create requirements checklist tracking
- [ ] Build sample record display (5 individual cards)
- [ ] Implement open coding annotation system
- [ ] Add iteration controls for sample refinement
- [ ] Create final configuration form
- [ ] Add progress tracking for full generation
- [ ] Integration with existing dataset management

### Integration Tasks
- [ ] Connect to Nova AI models
- [ ] Integrate with existing dataset system
- [ ] End-to-end generation workflow
- [ ] Error handling and user feedback
- [ ] Performance optimization

## Success Criteria
- [ ] Users can generate 50+ realistic samples in under 1 minute
- [ ] Generated samples are contextually relevant to user description
- [ ] 90%+ of generated samples are valid JSON format
- [ ] Users can successfully use generated datasets in optimization
- [ ] Positive user feedback on sample quality

## Technical Architecture
### Generator State Management
```
Step 1: Entry Point → Step 2: Prompt Selection → Step 3: Conversational Gathering → 
Step 4: Sample Generation → Step 5: Annotation & Iteration → Step 6: Final Generation
```

### Components to Create
1. **Dataset Generation Interface** (`components/dataset_generator.py`)
   - Multi-step generator interface
   - State management between steps
   - Progress tracking

2. **Conversational AI Service** (`dataset_conversation.py`)
   - Requirements gathering chatbot with comprehensive checklist
   - Role/persona definition guidance
   - Task description clarification
   - Data characteristics specification (diversity, realism, edge cases, constraints)
   - Format specification (input, output, dataset formats)
   - Prompt analysis (if provided)
   - Checklist completion validation

3. **Sample Generation & Iteration** (`sample_generator.py`)
   - Initial 5-sample generation
   - Annotation processing
   - Iterative refinement

4. **Open Coding Annotation System**
   - Individual record annotation interface
   - Annotation-to-improvement mapping
   - Feedback loop to generation prompts

### API Endpoints
- `/datasets/generator/start` - Initialize generator session
- `/datasets/generator/analyze-prompt` - Analyze selected prompt
- `/datasets/generator/conversation` - Conversational requirements gathering
- `/datasets/generator/generate-samples` - Generate initial 5 samples
- `/datasets/generator/annotate` - Process annotations and iterate
- `/datasets/generator/finalize` - Generate full dataset

### Data Flow
```
Optional Prompt → AI Analysis → Conversational Gathering → Requirements Checklist → 
Initial Samples → User Annotations → Iterative Refinement → Final Generation → 
Standardized Format (input/answer columns) → Database + File Storage
```

## Risks & Considerations
- **AI Quality Risk:** Generated samples may not match user expectations
  - *Mitigation:* Preview system with regeneration capability
- **Performance Risk:** Large dataset generation may be slow
  - *Mitigation:* Progress tracking and batch processing
- **Cost Risk:** AI model calls for large datasets
  - *Mitigation:* Reasonable size limits and user awareness

## Dependencies
- Nova AI model access for generation
- Existing dataset storage system
- Current UI framework and styling

## User Stories
1. **As a user**, I want to generate a dataset from an existing prompt so that I can create evaluation data for optimization
2. **As a user**, I want an AI to guide me through dataset requirements so that I don't miss important considerations
3. **As a user**, I want to see 5 sample records first so that I can verify the AI understands my needs
4. **As a user**, I want to annotate individual records so that I can provide specific feedback for improvement
5. **As a user**, I want the AI to iterate on samples based on my annotations so that the final dataset meets my standards
6. **As a user**, I want to specify the final dataset size and format so that it integrates with my workflow
7. **As a user**, I want the generated dataset saved automatically so that I can use it immediately for optimization

---
**Created:** 2025-08-20
**Last Updated:** 2025-08-20
**Status:** Planning
