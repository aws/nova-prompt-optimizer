import React, { useState } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Progress } from '@/components/ui/progress'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Input } from '@/components/ui/input'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { 
  Users, 
  Clock, 
  CheckCircle, 
  AlertTriangle, 
  TrendingUp,
  Search,

  Download,
  UserCheck,
  Target
} from 'lucide-react'
import { AnnotationTask, AnnotationStats, AgreementMetrics } from '@/types/annotation'
import { AgreementMetrics as AgreementMetricsComponent } from './AgreementMetrics'
import { ConflictResolution } from './ConflictResolution'

interface AnnotationDashboardProps {
  tasks: AnnotationTask[]
  stats: AnnotationStats
  agreementMetrics: AgreementMetrics
  currentUserId: string
  onTaskAssign: (taskId: string, annotatorIds: string[]) => void
  onTaskStatusUpdate: (taskId: string, status: AnnotationTask['status']) => void
  onExportData: (format: 'csv' | 'json') => void
}

export const AnnotationDashboard: React.FC<AnnotationDashboardProps> = ({
  tasks,
  stats,
  agreementMetrics,
  currentUserId: _currentUserId,
  onTaskAssign: _onTaskAssign,
  onTaskStatusUpdate,
  onExportData
}) => {
  const [searchTerm, setSearchTerm] = useState('')
  const [statusFilter, setStatusFilter] = useState<string>('all')
  const [selectedTasks, setSelectedTasks] = useState<Set<string>>(new Set())

  const filteredTasks = tasks.filter(task => {
    const matchesSearch = task.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         task.description.toLowerCase().includes(searchTerm.toLowerCase())
    const matchesStatus = statusFilter === 'all' || task.status === statusFilter
    return matchesSearch && matchesStatus
  })

  const getTaskProgress = (task: AnnotationTask) => {
    // Calculate progress based on completed annotations vs total required
    const totalRequired = task.results.length * task.assigned_annotators.length
    // This would come from actual annotation data in a real implementation
    const completed = Math.floor(Math.random() * totalRequired) // Placeholder
    return totalRequired > 0 ? (completed / totalRequired) * 100 : 0
  }

  const getStatusColor = (status: AnnotationTask['status']) => {
    switch (status) {
      case 'completed': return 'default'
      case 'in_progress': return 'secondary'
      case 'pending': return 'outline'
      default: return 'outline'
    }
  }

  const handleTaskSelect = (taskId: string, selected: boolean) => {
    const newSelected = new Set(selectedTasks)
    if (selected) {
      newSelected.add(taskId)
    } else {
      newSelected.delete(taskId)
    }
    setSelectedTasks(newSelected)
  }

  const handleBulkStatusUpdate = (status: AnnotationTask['status']) => {
    selectedTasks.forEach(taskId => {
      onTaskStatusUpdate(taskId, status)
    })
    setSelectedTasks(new Set())
  }

  return (
    <div className="space-y-6">
      {/* Dashboard Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Annotation Dashboard</h1>
          <p className="text-muted-foreground">
            Manage annotation tasks and track quality metrics
          </p>
        </div>
        <div className="flex items-center gap-2">
          <Button variant="outline" onClick={() => onExportData('csv')}>
            <Download className="mr-2 h-4 w-4" />
            Export CSV
          </Button>
          <Button variant="outline" onClick={() => onExportData('json')}>
            <Download className="mr-2 h-4 w-4" />
            Export JSON
          </Button>
        </div>
      </div>

      {/* Stats Overview */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Annotations</CardTitle>
            <Target className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.total_annotations}</div>
            <p className="text-xs text-muted-foreground">
              {stats.completed_annotations} completed
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Completion Rate</CardTitle>
            <CheckCircle className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {((stats.completed_annotations / stats.total_annotations) * 100).toFixed(1)}%
            </div>
            <Progress 
              value={(stats.completed_annotations / stats.total_annotations) * 100} 
              className="mt-2"
            />
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Average Agreement</CardTitle>
            <Users className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {(stats.average_agreement * 100).toFixed(1)}%
            </div>
            <p className="text-xs text-muted-foreground">
              Inter-annotator agreement
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Pending Tasks</CardTitle>
            <Clock className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.pending_annotations}</div>
            <p className="text-xs text-muted-foreground">
              Awaiting annotation
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Main Content Tabs */}
      <Tabs defaultValue="tasks" className="w-full">
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="tasks">Tasks</TabsTrigger>
          <TabsTrigger value="agreement">Agreement</TabsTrigger>
          <TabsTrigger value="conflicts">Conflicts</TabsTrigger>
          <TabsTrigger value="performance">Performance</TabsTrigger>
        </TabsList>

        {/* Tasks Tab */}
        <TabsContent value="tasks" className="space-y-4">
          {/* Filters and Search */}
          <div className="flex items-center gap-4">
            <div className="flex-1">
              <div className="relative">
                <Search className="absolute left-2 top-2.5 h-4 w-4 text-muted-foreground" />
                <Input
                  placeholder="Search tasks..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="pl-8"
                />
              </div>
            </div>
            <Select value={statusFilter} onValueChange={setStatusFilter}>
              <SelectTrigger className="w-48">
                <SelectValue placeholder="Filter by status" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Status</SelectItem>
                <SelectItem value="pending">Pending</SelectItem>
                <SelectItem value="in_progress">In Progress</SelectItem>
                <SelectItem value="completed">Completed</SelectItem>
              </SelectContent>
            </Select>
          </div>

          {/* Bulk Actions */}
          {selectedTasks.size > 0 && (
            <Alert>
              <AlertTriangle className="h-4 w-4" />
              <AlertDescription className="flex items-center justify-between">
                <span>{selectedTasks.size} tasks selected</span>
                <div className="flex items-center gap-2">
                  <Button 
                    size="sm" 
                    variant="outline"
                    onClick={() => handleBulkStatusUpdate('in_progress')}
                  >
                    Start Selected
                  </Button>
                  <Button 
                    size="sm" 
                    variant="outline"
                    onClick={() => handleBulkStatusUpdate('completed')}
                  >
                    Complete Selected
                  </Button>
                </div>
              </AlertDescription>
            </Alert>
          )}

          {/* Tasks Table */}
          <Card>
            <CardHeader>
              <CardTitle>Annotation Tasks</CardTitle>
              <CardDescription>
                Manage and track annotation task progress
              </CardDescription>
            </CardHeader>
            <CardContent>
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead className="w-12">
                      <input
                        type="checkbox"
                        onChange={(e) => {
                          if (e.target.checked) {
                            setSelectedTasks(new Set(filteredTasks.map(t => t.id)))
                          } else {
                            setSelectedTasks(new Set())
                          }
                        }}
                      />
                    </TableHead>
                    <TableHead>Task</TableHead>
                    <TableHead>Status</TableHead>
                    <TableHead>Progress</TableHead>
                    <TableHead>Annotators</TableHead>
                    <TableHead>Deadline</TableHead>
                    <TableHead>Actions</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {filteredTasks.map((task) => (
                    <TableRow key={task.id}>
                      <TableCell>
                        <input
                          type="checkbox"
                          checked={selectedTasks.has(task.id)}
                          onChange={(e) => handleTaskSelect(task.id, e.target.checked)}
                        />
                      </TableCell>
                      <TableCell>
                        <div>
                          <div className="font-medium">{task.name}</div>
                          <div className="text-sm text-muted-foreground">
                            {task.description}
                          </div>
                        </div>
                      </TableCell>
                      <TableCell>
                        <Badge variant={getStatusColor(task.status)}>
                          {task.status.replace('_', ' ')}
                        </Badge>
                      </TableCell>
                      <TableCell>
                        <div className="space-y-1">
                          <Progress value={getTaskProgress(task)} className="w-20" />
                          <div className="text-xs text-muted-foreground">
                            {getTaskProgress(task).toFixed(0)}%
                          </div>
                        </div>
                      </TableCell>
                      <TableCell>
                        <div className="flex items-center gap-1">
                          <UserCheck className="h-4 w-4" />
                          <span className="text-sm">{task.assigned_annotators.length}</span>
                        </div>
                      </TableCell>
                      <TableCell>
                        {task.deadline ? (
                          <div className="text-sm">
                            {new Date(task.deadline).toLocaleDateString()}
                          </div>
                        ) : (
                          <span className="text-muted-foreground">No deadline</span>
                        )}
                      </TableCell>
                      <TableCell>
                        <div className="flex items-center gap-2">
                          <Button size="sm" variant="outline">
                            View
                          </Button>
                          <Button size="sm" variant="outline">
                            Edit
                          </Button>
                        </div>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Agreement Tab */}
        <TabsContent value="agreement">
          <AgreementMetricsComponent 
            metrics={agreementMetrics}
            onDrillDown={(dimension) => console.log('Drill down:', dimension)}
          />
        </TabsContent>

        {/* Conflicts Tab */}
        <TabsContent value="conflicts">
          <ConflictResolution 
            conflicts={agreementMetrics.conflicts}
            onResolveConflict={(conflictId, resolution) => 
              console.log('Resolve conflict:', conflictId, resolution)
            }
          />
        </TabsContent>

        {/* Performance Tab */}
        <TabsContent value="performance" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Annotator Performance</CardTitle>
              <CardDescription>
                Individual annotator statistics and quality metrics
              </CardDescription>
            </CardHeader>
            <CardContent>
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Annotator</TableHead>
                    <TableHead>Annotations</TableHead>
                    <TableHead>Avg. Agreement</TableHead>
                    <TableHead>Consistency</TableHead>
                    <TableHead>Avg. Time</TableHead>
                    <TableHead>Status</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {Object.entries(stats.annotator_performance).map(([annotatorId, performance]) => (
                    <TableRow key={annotatorId}>
                      <TableCell className="font-medium">{annotatorId}</TableCell>
                      <TableCell>
                        {Math.floor(Math.random() * 100) + 20} {/* Placeholder */}
                      </TableCell>
                      <TableCell>
                        <div className="flex items-center gap-2">
                          <span>{(performance * 100).toFixed(1)}%</span>
                          {performance > 0.8 && (
                            <TrendingUp className="h-4 w-4 text-green-500" />
                          )}
                        </div>
                      </TableCell>
                      <TableCell>
                        <Progress value={performance * 100} className="w-20" />
                      </TableCell>
                      <TableCell>
                        {Math.floor(Math.random() * 300) + 60}s {/* Placeholder */}
                      </TableCell>
                      <TableCell>
                        <Badge variant={performance > 0.8 ? 'default' : 'secondary'}>
                          {performance > 0.8 ? 'Good' : 'Needs Review'}
                        </Badge>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  )
}