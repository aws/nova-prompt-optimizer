import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import { AppLayout } from '@/components/common/Layout'
import { Dashboard } from '@/pages/Dashboard'
import { DatasetManagement } from '@/pages/DatasetManagement'
import { PromptWorkbench } from '@/pages/PromptWorkbench'
import { OptimizationWorkflow } from '@/pages/OptimizationWorkflow'
import { AnnotationWorkspace } from '@/pages/AnnotationWorkspace'
import { ResultsAnalysis } from '@/pages/ResultsAnalysis'

function App() {
  return (
    <Router>
      <AppLayout>
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/datasets" element={<DatasetManagement />} />
          <Route path="/prompts" element={<PromptWorkbench />} />
          <Route path="/optimize" element={<OptimizationWorkflow />} />
          <Route path="/annotate" element={<AnnotationWorkspace />} />
          <Route path="/results" element={<ResultsAnalysis />} />
        </Routes>
      </AppLayout>
    </Router>
  )
}

export default App