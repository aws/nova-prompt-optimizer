# Design Document

## Overview

The Nova Prompt Optimizer Frontend is a web-based application that provides an intuitive interface for the existing Nova Prompt Optimizer Python SDK. The system follows a clean separation between a FastAPI backend that wraps the existing adapters and a React frontend that provides the user interface.

The architecture maintains the existing backend adapters unchanged while adding a web layer that enables dataset management, prompt editing, optimization execution, and human annotation workflows. The system supports the complete optimization pipeline from data upload through result analysis and quality assurance.

## Architecture

### Project Structure

The frontend will be organized under a `/ui` directory in the project root, maintaining clean separation from the existing Python SDK:

```
nova-prompt-optimizer/
├── src/                                    # Existing Python SDK (unchanged)
├── samples/                                # Existing samples (unchanged)
├── ui/                                     # New frontend application
│   ├── backend/                            # FastAPI backend
│   │   ├── app/
│   │   │   ├── __init__.py
│   │   │   ├── main.py                     # FastAPI application entry point
│   │   │   ├── config.py                   # Configuration settings
│   │   │   ├── dependencies.py             # Dependency injection
│   │   │   ├── models/                     # Pydantic models
│   │   │   │   ├── __init__.py
│   │   │   │   ├── dataset.py
│   │   │   │   ├── prompt.py
│   │   │   │   ├── optimization.py
│   │   │   │   ├── annotation.py
│   │   │   │   └── common.py
│   │   │   ├── routers/                    # API route handlers
│   │   │   │   ├── __init__.py
│   │   │   │   ├── datasets.py
│   │   │   │   ├── prompts.py
│   │   │   │   ├── optimization.py
│   │   │   │   ├── evaluation.py
│   │   │   │   ├── annotations.py
│   │   │   │   └── websocket.py
│   │   │   ├── services/                   # Business logic layer
│   │   │   │   ├── __init__.py
│   │   │   │   ├── dataset_service.py
│   │   │   │   ├── prompt_service.py
│   │   │   │   ├── optimization_service.py
│   │   │   │   ├── evaluation_service.py
│   │   │   │   ├── annotation_service.py
│   │   │   │   └── rubric_service.py
│   │   │   ├── adapters/                   # Integration with existing SDK
│   │   │   │   ├── __init__.py
│   │   │   │   ├── dataset_adapter.py
│   │   │   │   ├── prompt_adapter.py
│   │   │   │   ├── optimization_adapter.py
│   │   │   │   └── evaluation_adapter.py
│   │   │   ├── core/                       # Core utilities
│   │   │   │   ├── __init__.py
│   │   │   │   ├── exceptions.py
│   │   │   │   ├── logging.py
│   │   │   │   ├── security.py
│   │   │   │   └── tasks.py
│   │   │   └── db/                         # Database layer
│   │   │       ├── __init__.py
│   │   │       ├── database.py
│   │   │       ├── models.py
│   │   │       └── migrations/
│   │   ├── requirements.txt                # Backend dependencies
│   │   ├── Dockerfile                      # Backend container
│   │   └── pytest.ini                      # Test configuration
│   ├── frontend/                           # React frontend
│   │   ├── public/
│   │   │   ├── index.html
│   │   │   ├── favicon.ico
│   │   │   └── manifest.json
│   │   ├── src/
│   │   │   ├── components/                 # React components
│   │   │   │   ├── common/                 # Shared components
│   │   │   │   │   ├── Layout/
│   │   │   │   │   │   ├── AppLayout.tsx
│   │   │   │   │   │   ├── Navigation.tsx
│   │   │   │   │   │   └── index.ts
│   │   │   │   │   ├── ui/                 # Shadcn/UI components
│   │   │   │   │   │   ├── button.tsx
│   │   │   │   │   │   ├── input.tsx
│   │   │   │   │   │   ├── dialog.tsx
│   │   │   │   │   │   ├── table.tsx
│   │   │   │   │   │   ├── card.tsx
│   │   │   │   │   │   ├── badge.tsx
│   │   │   │   │   │   ├── progress.tsx
│   │   │   │   │   │   ├── tabs.tsx
│   │   │   │   │   │   ├── form.tsx
│   │   │   │   │   │   ├── select.tsx
│   │   │   │   │   │   ├── textarea.tsx
│   │   │   │   │   │   ├── toast.tsx
│   │   │   │   │   │   ├── alert.tsx
│   │   │   │   │   │   ├── dropdown-menu.tsx
│   │   │   │   │   │   ├── sheet.tsx
│   │   │   │   │   │   ├── separator.tsx
│   │   │   │   │   │   └── index.ts
│   │   │   │   │   ├── Loading/
│   │   │   │   │   │   ├── LoadingSpinner.tsx
│   │   │   │   │   │   ├── ProgressBar.tsx
│   │   │   │   │   │   └── index.ts
│   │   │   │   │   └── ErrorBoundary/
│   │   │   │   │       ├── ErrorBoundary.tsx
│   │   │   │   │       ├── ErrorDisplay.tsx
│   │   │   │   │       └── index.ts
│   │   │   │   ├── dataset/                # Dataset management
│   │   │   │   │   ├── DatasetUpload/
│   │   │   │   │   │   ├── DatasetUpload.tsx
│   │   │   │   │   │   ├── FileDropzone.tsx
│   │   │   │   │   │   ├── ColumnMapper.tsx
│   │   │   │   │   │   └── index.ts
│   │   │   │   │   ├── DatasetList/
│   │   │   │   │   │   ├── DatasetList.tsx
│   │   │   │   │   │   ├── DatasetCard.tsx
│   │   │   │   │   │   └── index.ts
│   │   │   │   │   ├── DatasetPreview/
│   │   │   │   │   │   ├── DatasetPreview.tsx
│   │   │   │   │   │   ├── DataTable.tsx
│   │   │   │   │   │   └── index.ts
│   │   │   │   │   └── index.ts
│   │   │   │   ├── prompt/                 # Prompt management
│   │   │   │   │   ├── PromptEditor/
│   │   │   │   │   │   ├── PromptEditor.tsx
│   │   │   │   │   │   ├── CodeEditor.tsx
│   │   │   │   │   │   ├── VariableDetector.tsx
│   │   │   │   │   │   └── index.ts
│   │   │   │   │   ├── PromptPreview/
│   │   │   │   │   │   ├── PromptPreview.tsx
│   │   │   │   │   │   ├── TemplateRenderer.tsx
│   │   │   │   │   │   └── index.ts
│   │   │   │   │   ├── PromptLibrary/
│   │   │   │   │   │   ├── PromptLibrary.tsx
│   │   │   │   │   │   ├── PromptCard.tsx
│   │   │   │   │   │   └── index.ts
│   │   │   │   │   └── index.ts
│   │   │   │   ├── optimization/           # Optimization workflow
│   │   │   │   │   ├── OptimizationConfig/
│   │   │   │   │   │   ├── OptimizationConfig.tsx
│   │   │   │   │   │   ├── OptimizerSelector.tsx
│   │   │   │   │   │   ├── ModelSelector.tsx
│   │   │   │   │   │   └── index.ts
│   │   │   │   │   ├── OptimizationProgress/
│   │   │   │   │   │   ├── OptimizationProgress.tsx
│   │   │   │   │   │   ├── ProgressTracker.tsx
│   │   │   │   │   │   ├── LogViewer.tsx
│   │   │   │   │   │   └── index.ts
│   │   │   │   │   ├── OptimizationResults/
│   │   │   │   │   │   ├── OptimizationResults.tsx
│   │   │   │   │   │   ├── ResultsComparison.tsx
│   │   │   │   │   │   ├── MetricsVisualization.tsx
│   │   │   │   │   │   └── index.ts
│   │   │   │   │   └── index.ts
│   │   │   │   ├── annotation/             # Human annotation system
│   │   │   │   │   ├── RubricGenerator/
│   │   │   │   │   │   ├── RubricGenerator.tsx
│   │   │   │   │   │   ├── DimensionEditor.tsx
│   │   │   │   │   │   └── index.ts
│   │   │   │   │   ├── AnnotationInterface/
│   │   │   │   │   │   ├── AnnotationInterface.tsx
│   │   │   │   │   │   ├── AnnotationForm.tsx
│   │   │   │   │   │   ├── ResultViewer.tsx
│   │   │   │   │   │   └── index.ts
│   │   │   │   │   ├── AnnotationDashboard/
│   │   │   │   │   │   ├── AnnotationDashboard.tsx
│   │   │   │   │   │   ├── AgreementMetrics.tsx
│   │   │   │   │   │   ├── ConflictResolution.tsx
│   │   │   │   │   │   └── index.ts
│   │   │   │   │   └── index.ts
│   │   │   │   ├── evaluation/             # Evaluation and metrics
│   │   │   │   │   ├── MetricBuilder/
│   │   │   │   │   │   ├── MetricBuilder.tsx
│   │   │   │   │   │   ├── CodeEditor.tsx
│   │   │   │   │   │   ├── MetricTester.tsx
│   │   │   │   │   │   └── index.ts
│   │   │   │   │   ├── EvaluationResults/
│   │   │   │   │   │   ├── EvaluationResults.tsx
│   │   │   │   │   │   ├── ScoreBreakdown.tsx
│   │   │   │   │   │   └── index.ts
│   │   │   │   │   └── index.ts
│   │   │   │   └── index.ts
│   │   │   ├── pages/                      # Page components
│   │   │   │   ├── Dashboard/
│   │   │   │   │   ├── Dashboard.tsx
│   │   │   │   │   └── index.ts
│   │   │   │   ├── DatasetManagement/
│   │   │   │   │   ├── DatasetManagement.tsx
│   │   │   │   │   └── index.ts
│   │   │   │   ├── PromptWorkbench/
│   │   │   │   │   ├── PromptWorkbench.tsx
│   │   │   │   │   └── index.ts
│   │   │   │   ├── OptimizationWorkflow/
│   │   │   │   │   ├── OptimizationWorkflow.tsx
│   │   │   │   │   └── index.ts
│   │   │   │   ├── AnnotationWorkspace/
│   │   │   │   │   ├── AnnotationWorkspace.tsx
│   │   │   │   │   └── index.ts
│   │   │   │   ├── ResultsAnalysis/
│   │   │   │   │   ├── ResultsAnalysis.tsx
│   │   │   │   │   └── index.ts
│   │   │   │   └── index.ts
│   │   │   ├── hooks/                      # Custom React hooks
│   │   │   │   ├── useDataset.ts
│   │   │   │   ├── usePrompt.ts
│   │   │   │   ├── useOptimization.ts
│   │   │   │   ├── useAnnotation.ts
│   │   │   │   ├── useWebSocket.ts
│   │   │   │   ├── useLocalStorage.ts
│   │   │   │   └── index.ts
│   │   │   ├── services/                   # API client services
│   │   │   │   ├── api/
│   │   │   │   │   ├── client.ts           # Base API client
│   │   │   │   │   ├── datasets.ts
│   │   │   │   │   ├── prompts.ts
│   │   │   │   │   ├── optimization.ts
│   │   │   │   │   ├── annotations.ts
│   │   │   │   │   └── index.ts
│   │   │   │   ├── websocket/
│   │   │   │   │   ├── client.ts
│   │   │   │   │   ├── handlers.ts
│   │   │   │   │   └── index.ts
│   │   │   │   └── index.ts
│   │   │   ├── store/                      # State management
│   │   │   │   ├── context/
│   │   │   │   │   ├── AppContext.tsx
│   │   │   │   │   ├── DatasetContext.tsx
│   │   │   │   │   ├── OptimizationContext.tsx
│   │   │   │   │   └── index.ts
│   │   │   │   ├── reducers/
│   │   │   │   │   ├── datasetReducer.ts
│   │   │   │   │   ├── optimizationReducer.ts
│   │   │   │   │   └── index.ts
│   │   │   │   └── index.ts
│   │   │   ├── types/                      # TypeScript type definitions
│   │   │   │   ├── api.ts
│   │   │   │   ├── dataset.ts
│   │   │   │   ├── prompt.ts
│   │   │   │   ├── optimization.ts
│   │   │   │   ├── annotation.ts
│   │   │   │   ├── common.ts
│   │   │   │   └── index.ts
│   │   │   ├── utils/                      # Utility functions
│   │   │   │   ├── formatting.ts
│   │   │   │   ├── validation.ts
│   │   │   │   ├── file-handling.ts
│   │   │   │   ├── date-time.ts
│   │   │   │   ├── constants.ts
│   │   │   │   └── index.ts
│   │   │   ├── styles/                     # Styling
│   │   │   │   ├── globals.css             # Global styles + Shadcn/UI base
│   │   │   │   └── components.css          # Custom component styles
│   │   │   ├── lib/                        # Utility libraries
│   │   │   │   ├── utils.ts                # Shadcn/UI utility functions (cn, etc.)
│   │   │   │   └── validations.ts          # Form validation schemas
│   │   │   ├── assets/                     # Static assets
│   │   │   │   ├── images/
│   │   │   │   ├── icons/
│   │   │   │   └── fonts/
│   │   │   ├── App.tsx                     # Main App component
│   │   │   ├── App.css
│   │   │   ├── index.tsx                   # React entry point
│   │   │   └── index.css
│   │   ├── package.json                    # Frontend dependencies
│   │   ├── tsconfig.json                   # TypeScript configuration
│   │   ├── tailwind.config.js              # Tailwind CSS configuration
│   │   ├── components.json                 # Shadcn/UI configuration
│   │   ├── vite.config.ts                  # Vite build configuration
│   │   └── Dockerfile                      # Frontend container
│   ├── shared/                             # Shared utilities and types
│   │   ├── types/
│   │   │   ├── api-schema.ts               # Shared API types
│   │   │   └── index.ts
│   │   ├── utils/
│   │   │   ├── validation.py               # Shared validation logic
│   │   │   └── constants.py
│   │   └── scripts/
│   │       ├── generate-types.py           # Generate TS types from Pydantic
│   │       └── setup-dev.sh
│   ├── docker-compose.yml                  # Development environment
│   ├── docker-compose.prod.yml             # Production environment
│   ├── .env.example                        # Environment variables template
│   ├── .gitignore                          # Git ignore rules for UI
│   └── README.md                           # UI-specific documentation
├── requirements.txt                        # Existing Python requirements
├── pyproject.toml                          # Existing project config
└── README.md                               # Main project README
```

### High-Level Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────────────┐
│   React SPA     │    │   FastAPI        │    │   Nova Prompt           │
│   Frontend      │◄──►│   Backend        │◄──►│   Optimizer SDK         │
│                 │    │                  │    │   (Unchanged)           │
└─────────────────┘    └──────────────────┘    └─────────────────────────┘
         │                       │                         │
         │                       │                         │
         ▼                       ▼                         ▼
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────────────┐
│   Browser       │    │   Task Queue     │    │   AWS Bedrock           │
│   Storage       │    │   (Background    │    │   Integration           │
│                 │    │    Jobs)         │    │                         │
└─────────────────┘    └──────────────────┘    └─────────────────────────┘
```

### Component Architecture

The system is organized into distinct layers:

**Frontend Layer (React + TypeScript + Shadcn/UI)**

- Component-based UI using Shadcn/UI design system with Tailwind CSS
- Consistent design language with accessible, customizable components
- State management using React Context and custom hooks
- Real-time updates through WebSocket connections
- Responsive design supporting desktop and tablet interfaces
- Dark/light theme support built into Shadcn/UI components

**API Layer (FastAPI)**

- RESTful endpoints wrapping existing Python adapters
- Background task management for long-running operations
- WebSocket support for real-time progress updates
- Authentication and session management

**Integration Layer**

- Direct imports of existing Nova Prompt Optimizer adapters
- No modifications to existing backend code
- Proper error handling and logging
- Resource management and cleanup

**Data Layer**

- File storage for uploaded datasets and generated artifacts
- Database for metadata, user sessions, and annotation data
- Caching layer for optimization results and intermediate data

## Components and Interfaces

### Shadcn/UI Integration

The frontend will use Shadcn/UI as the primary component library, providing:

**Design System Benefits:**

- Consistent, accessible components built on Radix UI primitives
- Tailwind CSS integration with CSS variables for theming
- Copy-paste component architecture for easy customization
- Built-in dark/light mode support
- TypeScript-first with excellent type safety

**Key Shadcn/UI Components Used:**

- `Card`, `CardHeader`, `CardContent`, `CardFooter` for layout containers
- `Button`, `Input`, `Textarea`, `Select` for form controls
- `Table`, `TableHeader`, `TableBody`, `TableRow`, `TableCell` for data display
- `Dialog`, `Sheet`, `DropdownMenu` for overlays and navigation
- `Progress`, `Badge`, `Alert` for status and feedback
- `Tabs`, `Separator`, `Form` for organization and structure
- `Toast` for notifications and user feedback

**Setup Configuration:**

```json
// components.json
{
  "$schema": "https://ui.shadcn.com/schema.json",
  "style": "default",
  "rsc": false,
  "tsx": true,
  "tailwind": {
    "config": "tailwind.config.js",
    "css": "src/styles/globals.css",
    "baseColor": "slate",
    "cssVariables": true
  },
  "aliases": {
    "components": "@/components",
    "utils": "@/lib/utils"
  }
}
```

**Custom Theme Configuration:**

```css
/* globals.css */
@tailwind base;
@tailwind components;
@tailwind utilities;

@layer base {
  :root {
    --background: 0 0% 100%;
    --foreground: 222.2 84% 4.9%;
    --primary: 221.2 83.2% 53.3%;
    --primary-foreground: 210 40% 98%;
    /* Additional custom variables for Nova branding */
    --nova-blue: 214 100% 59%;
    --nova-purple: 262 83% 58%;
  }

  .dark {
    --background: 222.2 84% 4.9%;
    --foreground: 210 40% 98%;
    /* Dark mode variables */
  }
}
```

### Frontend Components

**Core Layout Components**

```typescript
interface AppLayoutProps {
  children: React.ReactNode;
  currentStep: WorkflowStep;
  onStepChange: (step: WorkflowStep) => void;
}

interface NavigationProps {
  steps: WorkflowStep[];
  currentStep: WorkflowStep;
  completedSteps: WorkflowStep[];
}
```

**Dataset Management Components (Shadcn/UI Implementation)**

```typescript
interface DatasetUploadProps {
  onUploadComplete: (dataset: Dataset) => void;
  acceptedFormats: string[];
  maxFileSize: number;
}

// Example implementation with Shadcn/UI
const DatasetUpload: React.FC<DatasetUploadProps> = ({ onUploadComplete }) => {
  return (
    <Card className="w-full">
      <CardHeader>
        <CardTitle>Upload Dataset</CardTitle>
        <CardDescription>
          Upload a CSV or JSON file to get started with prompt optimization
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="border-2 border-dashed border-muted-foreground/25 rounded-lg p-8 text-center">
          <Upload className="mx-auto h-12 w-12 text-muted-foreground" />
          <p className="mt-2 text-sm text-muted-foreground">
            Drag & drop your file here, or click to browse
          </p>
        </div>
        <div className="grid grid-cols-2 gap-4">
          <div className="space-y-2">
            <Label htmlFor="input-columns">Input Columns</Label>
            <Input id="input-columns" placeholder="e.g., input, question" />
          </div>
          <div className="space-y-2">
            <Label htmlFor="output-columns">Output Columns</Label>
            <Input id="output-columns" placeholder="e.g., answer, response" />
          </div>
        </div>
      </CardContent>
      <CardFooter>
        <Button onClick={handleUpload} className="w-full">
          <Upload className="mr-2 h-4 w-4" />
          Process Dataset
        </Button>
      </CardFooter>
    </Card>
  );
};

interface DatasetPreviewProps {
  dataset: Dataset;
  maxRows: number;
  onColumnMapping: (mapping: ColumnMapping) => void;
}

interface DatasetListProps {
  datasets: Dataset[];
  selectedDataset?: Dataset;
  onSelect: (dataset: Dataset) => void;
  onDelete: (datasetId: string) => void;
}
```

**Prompt Editor Components (Shadcn/UI Implementation)**

```typescript
interface PromptEditorProps {
  prompt?: Prompt;
  variables: string[];
  onSave: (prompt: Prompt) => void;
  onPreview: (prompt: Prompt, sampleData: any) => void;
}

// Example implementation with Shadcn/UI
const PromptEditor: React.FC<PromptEditorProps> = ({ prompt, onSave }) => {
  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle>Prompt Configuration</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="prompt-name">Prompt Name</Label>
            <Input id="prompt-name" placeholder="Enter prompt name" />
          </div>
          
          <Tabs defaultValue="system" className="w-full">
            <TabsList className="grid w-full grid-cols-2">
              <TabsTrigger value="system">System Prompt</TabsTrigger>
              <TabsTrigger value="user">User Prompt</TabsTrigger>
            </TabsList>
            
            <TabsContent value="system" className="space-y-2">
              <Label>System Prompt</Label>
              <Textarea 
                className="min-h-[200px] font-mono text-sm"
                placeholder="Enter your system prompt with {{variables}}"
              />
            </TabsContent>
            
            <TabsContent value="user" className="space-y-2">
              <Label>User Prompt</Label>
              <Textarea 
                className="min-h-[200px] font-mono text-sm"
                placeholder="Enter your user prompt with {{variables}}"
              />
            </TabsContent>
          </Tabs>
          
          <div className="space-y-2">
            <Label>Detected Variables</Label>
            <div className="flex flex-wrap gap-2">
              {variables.map((variable) => (
                <Badge key={variable} variant="secondary">
                  {variable}
                </Badge>
              ))}
            </div>
          </div>
        </CardContent>
        
        <CardFooter className="flex justify-between">
          <Button variant="outline" onClick={handlePreview}>
            <Eye className="mr-2 h-4 w-4" />
            Preview
          </Button>
          <Button onClick={handleSave}>
            <Save className="mr-2 h-4 w-4" />
            Save Prompt
          </Button>
        </CardFooter>
      </Card>
    </div>
  );
};

interface PromptPreviewProps {
  prompt: Prompt;
  sampleData: any;
  renderedOutput: string;
}

interface PromptLibraryProps {
  prompts: Prompt[];
  onSelect: (prompt: Prompt) => void;
  onDuplicate: (prompt: Prompt) => void;
  onDelete: (promptId: string) => void;
}
```

**Optimization Components (Shadcn/UI Implementation)**

```typescript
interface OptimizationConfigProps {
  dataset: Dataset;
  prompt: Prompt;
  availableOptimizers: OptimizerType[];
  availableModels: ModelInfo[];
  onStart: (config: OptimizationConfig) => void;
}

// Example implementation with Shadcn/UI
const OptimizationConfig: React.FC<OptimizationConfigProps> = ({ onStart }) => {
  return (
    <Card className="w-full">
      <CardHeader>
        <CardTitle>Optimization Configuration</CardTitle>
        <CardDescription>
          Configure your optimization parameters and start the process
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-6">
        <div className="grid grid-cols-2 gap-4">
          <div className="space-y-2">
            <Label>Optimizer Type</Label>
            <Select>
              <SelectTrigger>
                <SelectValue placeholder="Select optimizer" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="nova">Nova Prompt Optimizer</SelectItem>
                <SelectItem value="miprov2">MIPROv2</SelectItem>
                <SelectItem value="meta-prompter">Meta Prompter</SelectItem>
              </SelectContent>
            </Select>
          </div>
          
          <div className="space-y-2">
            <Label>Model</Label>
            <Select>
              <SelectTrigger>
                <SelectValue placeholder="Select model" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="nova-pro">Nova Pro</SelectItem>
                <SelectItem value="nova-lite">Nova Lite</SelectItem>
                <SelectItem value="claude-3">Claude 3</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </div>
        
        <div className="space-y-2">
          <Label>Max Iterations</Label>
          <Input type="number" defaultValue="10" min="1" max="50" />
        </div>
        
        <Separator />
        
        <div className="space-y-4">
          <h4 className="text-sm font-medium">Selected Configuration</h4>
          <div className="grid grid-cols-2 gap-4 text-sm">
            <div>
              <span className="text-muted-foreground">Dataset:</span>
              <Badge variant="outline" className="ml-2">
                {dataset.name}
              </Badge>
            </div>
            <div>
              <span className="text-muted-foreground">Prompt:</span>
              <Badge variant="outline" className="ml-2">
                {prompt.name}
              </Badge>
            </div>
          </div>
        </div>
      </CardContent>
      <CardFooter>
        <Button onClick={handleStart} className="w-full">
          <Play className="mr-2 h-4 w-4" />
          Start Optimization
        </Button>
      </CardFooter>
    </Card>
  );
};

interface OptimizationProgressProps {
  task: OptimizationTask;
  onCancel: (taskId: string) => void;
  onPause: (taskId: string) => void;
}

// Progress component example
const OptimizationProgress: React.FC<OptimizationProgressProps> = ({ task }) => {
  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center justify-between">
          Optimization in Progress
          <Badge variant={task.status === 'running' ? 'default' : 'secondary'}>
            {task.status}
          </Badge>
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="space-y-2">
          <div className="flex justify-between text-sm">
            <span>Progress</span>
            <span>{Math.round(task.progress * 100)}%</span>
          </div>
          <Progress value={task.progress * 100} className="w-full" />
        </div>
        
        <div className="text-sm text-muted-foreground">
          Current Step: {task.current_step}
        </div>
        
        <div className="flex gap-2">
          <Button variant="outline" size="sm" onClick={() => onPause(task.id)}>
            <Pause className="mr-2 h-4 w-4" />
            Pause
          </Button>
          <Button variant="destructive" size="sm" onClick={() => onCancel(task.id)}>
            <X className="mr-2 h-4 w-4" />
            Cancel
          </Button>
        </div>
      </CardContent>
    </Card>
  );
};

interface OptimizationResultsProps {
  results: OptimizationResults;
  onExport: (format: ExportFormat) => void;
  onAnnotate: (results: OptimizationResults) => void;
}
```

**Annotation Components**

```typescript
interface RubricGeneratorProps {
  dataset: Dataset;
  onRubricGenerated: (rubric: EvaluationRubric) => void;
  onRubricEdit: (rubric: EvaluationRubric) => void;
}

interface AnnotationInterfaceProps {
  results: OptimizationResults[];
  rubric: EvaluationRubric;
  annotator: User;
  onAnnotationComplete: (annotations: Annotation[]) => void;
}

interface AnnotationDashboardProps {
  annotations: Annotation[];
  interAnnotatorAgreement: AgreementMetrics;
  onResolveConflict: (conflictId: string, resolution: any) => void;
}
```

### Backend API Interfaces

**Dataset Endpoints**

```python
@router.post("/datasets/upload", response_model=DatasetResponse)
async def upload_dataset(
    file: UploadFile,
    input_columns: List[str],
    output_columns: List[str],
    split_ratio: float = 0.8
) -> DatasetResponse

@router.get("/datasets/{dataset_id}", response_model=Dataset)
async def get_dataset(dataset_id: str) -> Dataset

@router.get("/datasets/{dataset_id}/preview", response_model=DatasetPreview)
async def preview_dataset(
    dataset_id: str,
    limit: int = 10,
    offset: int = 0
) -> DatasetPreview
```

**Prompt Endpoints**

```python
@router.post("/prompts", response_model=PromptResponse)
async def create_prompt(prompt: PromptCreate) -> PromptResponse

@router.put("/prompts/{prompt_id}", response_model=PromptResponse)
async def update_prompt(prompt_id: str, prompt: PromptUpdate) -> PromptResponse

@router.post("/prompts/{prompt_id}/preview", response_model=PromptPreview)
async def preview_prompt(
    prompt_id: str,
    sample_data: Dict[str, Any]
) -> PromptPreview
```

**Optimization Endpoints**

```python
@router.post("/optimize/start", response_model=OptimizationTaskResponse)
async def start_optimization(
    config: OptimizationConfig,
    background_tasks: BackgroundTasks
) -> OptimizationTaskResponse

@router.get("/optimize/{task_id}/status", response_model=OptimizationTask)
async def get_optimization_status(task_id: str) -> OptimizationTask

@router.post("/optimize/{task_id}/cancel")
async def cancel_optimization(task_id: str) -> StatusResponse
```

**Annotation Endpoints**

```python
@router.post("/rubrics/generate", response_model=EvaluationRubric)
async def generate_rubric(
    dataset_id: str,
    rubric_config: RubricConfig
) -> EvaluationRubric

@router.post("/annotations", response_model=AnnotationResponse)
async def create_annotation(annotation: AnnotationCreate) -> AnnotationResponse

@router.get("/annotations/tasks/{annotator_id}", response_model=List[AnnotationTask])
async def get_annotation_tasks(annotator_id: str) -> List[AnnotationTask]
```

### Integration with Existing Adapters

**Dataset Adapter Integration**

```python
class DatasetService:
    def __init__(self):
        self.csv_adapter = CSVDatasetAdapter
        self.json_adapter = JSONDatasetAdapter
    
    async def process_dataset(
        self,
        file_content: bytes,
        file_type: str,
        input_columns: Set[str],
        output_columns: Set[str]
    ) -> ProcessedDataset:
        # Direct usage of existing adapters
        if file_type == "csv":
            adapter = self.csv_adapter(input_columns, output_columns)
        else:
            adapter = self.json_adapter(input_columns, output_columns)
        
        # Save file temporarily and process
        with tempfile.NamedTemporaryFile(suffix=f".{file_type}") as tmp:
            tmp.write(file_content)
            tmp.flush()
            adapter.adapt(tmp.name)
        
        return ProcessedDataset.from_adapter(adapter)
```

**Optimization Service Integration**

```python
class OptimizationService:
    def __init__(self):
        self.inference_adapter = BedrockInferenceAdapter(region_name="us-east-1")
    
    async def run_optimization(
        self,
        task_id: str,
        config: OptimizationConfig
    ) -> OptimizationResults:
        # Load existing components
        dataset_adapter = self.load_dataset_adapter(config.dataset_id)
        prompt_adapter = self.load_prompt_adapter(config.prompt_id)
        metric_adapter = self.load_metric_adapter(config.metric_id)
        
        # Use existing optimizer
        if config.optimizer_type == "nova":
            optimizer = NovaPromptOptimizer(
                prompt_adapter=prompt_adapter,
                dataset_adapter=dataset_adapter,
                metric_adapter=metric_adapter,
                inference_adapter=self.inference_adapter
            )
        
        # Run optimization with progress tracking
        optimized_prompt = await self.run_with_progress(
            optimizer.optimize, task_id
        )
        
        return OptimizationResults.from_adapter(optimized_prompt)
```

## Data Models

### Core Data Models

**Dataset Models**

```python
class Dataset(BaseModel):
    id: str
    name: str
    file_type: str
    input_columns: List[str]
    output_columns: List[str]
    row_count: int
    train_size: int
    test_size: int
    split_ratio: float
    uploaded_at: datetime
    file_path: str
    metadata: Dict[str, Any]

class DatasetPreview(BaseModel):
    columns: List[str]
    rows: List[Dict[str, Any]]
    total_rows: int
    sample_variables: Dict[str, List[str]]
```

**Prompt Models**

```python
class Prompt(BaseModel):
    id: str
    name: str
    description: Optional[str]
    system_prompt: str
    user_prompt: str
    variables: List[str]
    created_at: datetime
    updated_at: datetime
    version: int

class PromptPreview(BaseModel):
    rendered_system: str
    rendered_user: str
    variables_used: List[str]
    template_valid: bool
    validation_errors: List[str]
```

**Optimization Models**

```python
class OptimizationConfig(BaseModel):
    dataset_id: str
    prompt_id: str
    metric_id: str
    optimizer_type: OptimizerType
    model_id: str
    max_iterations: int = 10
    evaluation_split: float = 0.2
    parameters: Dict[str, Any] = {}

class OptimizationTask(BaseModel):
    id: str
    status: TaskStatus
    progress: float
    current_step: str
    config: OptimizationConfig
    started_at: datetime
    estimated_completion: Optional[datetime]
    results: Optional[OptimizationResults]
    error_message: Optional[str]

class OptimizationResults(BaseModel):
    task_id: str
    original_prompt: Prompt
    optimized_prompt: Prompt
    original_scores: Dict[str, float]
    optimized_scores: Dict[str, float]
    improvement_metrics: Dict[str, float]
    evaluation_details: List[EvaluationResult]
    optimization_log: List[OptimizationStep]
```

**Annotation Models**

```python
class EvaluationRubric(BaseModel):
    id: str
    name: str
    description: str
    dimensions: List[RubricDimension]
    generated_from_dataset: str
    created_at: datetime
    ai_generated: bool

class RubricDimension(BaseModel):
    name: str
    description: str
    scale_type: ScaleType  # numeric, categorical, boolean
    scale_range: Union[Tuple[int, int], List[str]]
    criteria: List[str]
    weight: float = 1.0

class Annotation(BaseModel):
    id: str
    annotator_id: str
    result_id: str
    rubric_id: str
    scores: Dict[str, Any]  # dimension_name -> score
    comments: Optional[str]
    confidence: float
    time_spent: int  # seconds
    created_at: datetime

class AnnotationTask(BaseModel):
    id: str
    annotator_id: str
    results_to_annotate: List[str]
    rubric_id: str
    status: AnnotationStatus
    assigned_at: datetime
    due_date: Optional[datetime]
    completed_at: Optional[datetime]
```

## Error Handling

### Frontend Error Handling

**Error Boundary Implementation**

```typescript
class OptimizationErrorBoundary extends React.Component {
  componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    // Log error to monitoring service
    logError(error, errorInfo);
    
    // Show user-friendly error message
    this.setState({ hasError: true, error });
  }
}
```

**API Error Handling**

```typescript
class APIClient {
  async request<T>(endpoint: string, options: RequestOptions): Promise<T> {
    try {
      const response = await fetch(endpoint, options);
      
      if (!response.ok) {
        const errorData = await response.json();
        throw new APIError(errorData.message, response.status, errorData.details);
      }
      
      return response.json();
    } catch (error) {
      if (error instanceof APIError) {
        throw error;
      }
      throw new NetworkError('Failed to connect to server');
    }
  }
}
```

### Backend Error Handling

**Custom Exception Classes**

```python
class OptimizationError(Exception):
    def __init__(self, message: str, error_code: str, details: Dict[str, Any] = None):
        self.message = message
        self.error_code = error_code
        self.details = details or {}
        super().__init__(message)

class DatasetProcessingError(OptimizationError):
    pass

class PromptValidationError(OptimizationError):
    pass

class MetricEvaluationError(OptimizationError):
    pass
```

**Global Exception Handler**

```python
@app.exception_handler(OptimizationError)
async def optimization_exception_handler(request: Request, exc: OptimizationError):
    return JSONResponse(
        status_code=400,
        content={
            "error": exc.error_code,
            "message": exc.message,
            "details": exc.details,
            "timestamp": datetime.utcnow().isoformat()
        }
    )
```

## Testing Strategy

### Frontend Testing

**Unit Testing with Jest and React Testing Library**

- Component rendering and interaction tests
- Custom hook testing with proper mocking
- API client testing with mock responses
- Utility function testing

**Integration Testing**

- End-to-end workflow testing with Cypress
- API integration testing with mock backend
- File upload and processing workflows
- Real-time update functionality

**Visual Testing**

- Storybook for component documentation
- Visual regression testing with Chromatic
- Responsive design testing across devices

### Backend Testing

**Unit Testing with pytest**

- Service layer testing with mocked adapters
- API endpoint testing with test client
- Data model validation testing
- Error handling and edge case testing

**Integration Testing**

- Full workflow testing with real adapters
- Database integration testing
- Background task testing
- WebSocket connection testing

**Performance Testing**

- Load testing for concurrent optimizations
- Memory usage testing with large datasets
- API response time benchmarking
- Background task queue performance

This design provides a comprehensive foundation for building the Nova Prompt Optimizer frontend while maintaining clean separation from the existing backend and ensuring scalability for future enhancements.
