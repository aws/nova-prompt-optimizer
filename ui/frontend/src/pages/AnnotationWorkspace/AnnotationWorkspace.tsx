import React, { useState, useEffect } from 'react'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { 
  AnnotationInterface, 
  AnnotationDashboard 
} from '@/components/annotation'
import { useAnnotation } from '@/hooks/useAnnotation'
import { AnnotationTask, EvaluationRubric, Annotation } from '@/types/annotation'
import { AlertCircle, Users, Target, CheckCircle } from 'lucide-react'

export const AnnotationWorkspace: React.FC = () => {
  const [activeTab, setActiveTab] = useState('dashboard')
  const [selectedTask, setSelectedTask] = useState<AnnotationTask | null>(null)
  const [selectedRubric, setSelectedRubric] = useState<EvaluationRubric | null>(null)
  const currentUserId = 'current_user' // This would come from auth context

  const {
    tasks,
    currentRubric,
    agreementMetrics,
    stats,
    loadTasks,
    loadRubric,
    submitAnnotation,
    // resolveConflict,
    isLoading,
    hasError
  } = useAnnotation({
    annotatorId: currentUserId,
    autoLoad: true
  })

  useEffect(() => {
    if (selectedTask?.rubric_id && !selectedRubric) {
      loadRubric(selectedTask.rubric_id).then(() => {
        if (currentRubric.data) {
          setSelectedRubric(currentRubric.data)
        }
      })
    }
  }, [selectedTask, selectedRubric, loadRubric, currentRubric.data])

  // const handleTaskSelect = (task: AnnotationTask) => {
  //   setSelectedTask(task)
  //   setActiveTab('annotate')
  // }

  const handleAnnotationComplete = async (annotation: Annotation) => {
    try {
      await submitAnnotation(annotation)
      // Refresh tasks after annotation
      await loadTasks(currentUserId)
    } catch (error) {
      console.error('Failed to submit annotation:', error)
    }
  }

  const handleTaskComplete = () => {
    setSelectedTask(null)
    setSelectedRubric(null)
    setActiveTab('dashboard')
    // Refresh data
    loadTasks(currentUserId)
  }

  const handleTaskAssign = (taskId: string, annotatorIds: string[]) => {
    // Implementation would depend on backend API
    console.log('Assign task:', taskId, 'to:', annotatorIds)
  }

  const handleTaskStatusUpdate = (taskId: string, status: AnnotationTask['status']) => {
    // Implementation would depend on backend API
    console.log('Update task status:', taskId, 'to:', status)
  }

  const handleExportData = (format: 'csv' | 'json') => {
    // Implementation would depend on backend API
    console.log('Export data in format:', format)
  }

  // const handleConflictResolve = (conflictId: string, resolution: any) => {
  //   resolveConflict(conflictId, resolution)
  // }

  if (hasError) {
    return (
      <div className="space-y-6">
        <div>
          <h1 className="text-3xl font-bold">Annotation Workspace</h1>
          <p className="text-muted-foreground">
            Human annotation and quality assessment
          </p>
        </div>
        
        <Alert variant="destructive">
          <AlertCircle className="h-4 w-4" />
          <AlertDescription>
            Failed to load annotation data. Please try refreshing the page.
          </AlertDescription>
        </Alert>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold">Annotation Workspace</h1>
        <p className="text-muted-foreground">
          Human annotation and quality assessment
        </p>
      </div>

      {/* Quick Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">My Tasks</CardTitle>
            <Target className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {tasks.data?.length || 0}
            </div>
            <p className="text-xs text-muted-foreground">
              Assigned to me
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Completed</CardTitle>
            <CheckCircle className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {stats.data?.completed_annotations || 0}
            </div>
            <p className="text-xs text-muted-foreground">
              Annotations done
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Agreement</CardTitle>
            <Users className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {agreementMetrics.data ? 
                (agreementMetrics.data.overall_agreement * 100).toFixed(1) + '%' : 
                'N/A'
              }
            </div>
            <p className="text-xs text-muted-foreground">
              With other annotators
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Pending</CardTitle>
            <AlertCircle className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {stats.data?.pending_annotations || 0}
            </div>
            <p className="text-xs text-muted-foreground">
              Awaiting review
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Main Content */}
      <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
        <TabsList className="grid w-full grid-cols-2">
          <TabsTrigger value="dashboard">Dashboard</TabsTrigger>
          <TabsTrigger value="annotate" disabled={!selectedTask}>
            Annotate {selectedTask && <Badge className="ml-2">{selectedTask.name}</Badge>}
          </TabsTrigger>
        </TabsList>

        <TabsContent value="dashboard" className="space-y-4">
          {tasks.data && stats.data && agreementMetrics.data ? (
            <AnnotationDashboard
              tasks={tasks.data}
              stats={stats.data}
              agreementMetrics={agreementMetrics.data}
              currentUserId={currentUserId}
              onTaskAssign={handleTaskAssign}
              onTaskStatusUpdate={handleTaskStatusUpdate}
              onExportData={handleExportData}
            />
          ) : (
            <Card>
              <CardContent className="py-8">
                <div className="text-center">
                  <div className="text-muted-foreground">
                    {isLoading ? 'Loading annotation data...' : 'No annotation data available'}
                  </div>
                </div>
              </CardContent>
            </Card>
          )}
        </TabsContent>

        <TabsContent value="annotate" className="space-y-4">
          {selectedTask && selectedRubric ? (
            <AnnotationInterface
              task={selectedTask}
              rubric={selectedRubric}
              annotatorId={currentUserId}
              onAnnotationComplete={handleAnnotationComplete}
              onTaskComplete={handleTaskComplete}
            />
          ) : (
            <Card>
              <CardContent className="py-8">
                <div className="text-center">
                  <div className="text-muted-foreground">
                    Select a task from the dashboard to begin annotation
                  </div>
                  <Button 
                    className="mt-4" 
                    onClick={() => setActiveTab('dashboard')}
                  >
                    Go to Dashboard
                  </Button>
                </div>
              </CardContent>
            </Card>
          )}
        </TabsContent>
      </Tabs>
    </div>
  )
}