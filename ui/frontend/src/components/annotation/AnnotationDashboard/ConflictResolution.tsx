import React, { useState } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Textarea } from '@/components/ui/textarea'
import { Label } from '@/components/ui/label'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table'
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog'
// import { Alert, AlertDescription } from '@/components/ui/alert'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { 
  AlertTriangle, 
  Users, 
  CheckCircle, 
  // Clock, 
  // MessageSquare,
  Gavel,
  TrendingUp,
  Eye
} from 'lucide-react'
import { AnnotationConflict, AnnotationResolution } from '@/types/annotation'

interface ConflictResolutionProps {
  conflicts: AnnotationConflict[]
  onResolveConflict: (conflictId: string, resolution: AnnotationResolution) => void
}

export const ConflictResolution: React.FC<ConflictResolutionProps> = ({
  conflicts,
  onResolveConflict
}) => {
  // const [selectedConflict, setSelectedConflict] = useState<AnnotationConflict | null>(null)
  const [resolutionMethod, setResolutionMethod] = useState<AnnotationResolution['resolution_method']>('consensus')
  const [rationale, setRationale] = useState('')
  const [finalScores, setFinalScores] = useState<Record<string, number>>({})

  const pendingConflicts = conflicts.filter(c => c.resolution_status === 'pending')
  const resolvedConflicts = conflicts.filter(c => c.resolution_status === 'resolved')

  const handleResolveConflict = (conflict: AnnotationConflict) => {
    if (!rationale.trim()) {
      alert('Please provide a rationale for the resolution')
      return
    }

    const resolution: AnnotationResolution = {
      resolved_by: 'current_user', // This would come from auth context
      resolution_method: resolutionMethod,
      final_scores: finalScores,
      rationale: rationale.trim(),
      timestamp: new Date().toISOString()
    }

    onResolveConflict(conflict.result_id, resolution)
    // setSelectedConflict(null)
    setRationale('')
    setFinalScores({})
  }

  const getConflictSeverity = (disagreementScore: number) => {
    if (disagreementScore >= 0.7) return { level: 'High', variant: 'destructive' as const }
    if (disagreementScore >= 0.4) return { level: 'Medium', variant: 'secondary' as const }
    return { level: 'Low', variant: 'outline' as const }
  }

  const calculateAverageScores = (conflict: AnnotationConflict) => {
    const averages: Record<string, number> = {}
    
    conflict.annotations.forEach(annotation => {
      Object.entries(annotation.scores).forEach(([dimension, score]) => {
        if (!averages[dimension]) averages[dimension] = 0
        averages[dimension] += score
      })
    })

    Object.keys(averages).forEach(dimension => {
      averages[dimension] = averages[dimension] / conflict.annotations.length
    })

    return averages
  }

  const ConflictDetailsDialog = ({ conflict }: { conflict: AnnotationConflict }) => (
    <Dialog>
      <DialogTrigger asChild>
        <Button size="sm" variant="outline">
          <Eye className="mr-2 h-4 w-4" />
          View Details
        </Button>
      </DialogTrigger>
      <DialogContent className="max-w-4xl max-h-[80vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>Conflict Resolution</DialogTitle>
          <DialogDescription>
            Resolve disagreements between annotators for result {conflict.result_id}
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-6">
          {/* Conflict Overview */}
          <Card>
            <CardHeader>
              <CardTitle className="text-lg">Conflict Overview</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <Label className="text-sm font-medium">Disagreement Score</Label>
                  <div className="flex items-center gap-2 mt-1">
                    <span className="text-lg font-bold">
                      {(conflict.disagreement_score * 100).toFixed(1)}%
                    </span>
                    <Badge {...getConflictSeverity(conflict.disagreement_score)}>
                      {getConflictSeverity(conflict.disagreement_score).level}
                    </Badge>
                  </div>
                </div>
                <div>
                  <Label className="text-sm font-medium">Conflicting Dimensions</Label>
                  <div className="flex flex-wrap gap-1 mt-1">
                    {conflict.conflicting_dimensions.map(dimension => (
                      <Badge key={dimension} variant="outline">
                        {dimension}
                      </Badge>
                    ))}
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Annotator Scores Comparison */}
          <Card>
            <CardHeader>
              <CardTitle className="text-lg">Annotator Scores</CardTitle>
            </CardHeader>
            <CardContent>
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Dimension</TableHead>
                    {conflict.annotations.map((annotation, index) => (
                      <TableHead key={annotation.id}>
                        Annotator {index + 1}
                      </TableHead>
                    ))}
                    <TableHead>Average</TableHead>
                    <TableHead>Variance</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {Object.keys(conflict.annotations[0].scores).map(dimension => {
                    const scores = conflict.annotations.map(a => a.scores[dimension])
                    const average = scores.reduce((a, b) => a + b, 0) / scores.length
                    const variance = scores.reduce((acc, score) => acc + Math.pow(score - average, 2), 0) / scores.length
                    
                    return (
                      <TableRow key={dimension}>
                        <TableCell className="font-medium">{dimension}</TableCell>
                        {scores.map((score, index) => (
                          <TableCell key={index}>
                            <span className={conflict.conflicting_dimensions.includes(dimension) ? 'text-red-600 font-bold' : ''}>
                              {score}
                            </span>
                          </TableCell>
                        ))}
                        <TableCell>{average.toFixed(2)}</TableCell>
                        <TableCell>
                          <Badge variant={variance > 1 ? 'destructive' : 'outline'}>
                            {variance.toFixed(2)}
                          </Badge>
                        </TableCell>
                      </TableRow>
                    )
                  })}
                </TableBody>
              </Table>
            </CardContent>
          </Card>

          {/* Resolution Form */}
          {conflict.resolution_status === 'pending' && (
            <Card>
              <CardHeader>
                <CardTitle className="text-lg">Resolve Conflict</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="space-y-2">
                  <Label>Resolution Method</Label>
                  <Select value={resolutionMethod} onValueChange={(value: any) => setResolutionMethod(value)}>
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="consensus">Consensus Building</SelectItem>
                      <SelectItem value="expert_decision">Expert Decision</SelectItem>
                      <SelectItem value="majority_vote">Majority Vote</SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                <div className="space-y-2">
                  <Label>Final Scores</Label>
                  <div className="grid grid-cols-2 gap-4">
                    {Object.keys(conflict.annotations[0].scores).map(dimension => {
                      const averageScore = calculateAverageScores(conflict)[dimension]
                      return (
                        <div key={dimension} className="space-y-1">
                          <Label className="text-sm">{dimension}</Label>
                          <input
                            type="number"
                            min="1"
                            max="5"
                            step="0.1"
                            defaultValue={averageScore.toFixed(1)}
                            onChange={(e) => setFinalScores(prev => ({
                              ...prev,
                              [dimension]: parseFloat(e.target.value)
                            }))}
                            className="w-full px-3 py-2 border rounded-md"
                          />
                        </div>
                      )
                    })}
                  </div>
                </div>

                <div className="space-y-2">
                  <Label>Rationale</Label>
                  <Textarea
                    placeholder="Explain the reasoning behind this resolution..."
                    value={rationale}
                    onChange={(e) => setRationale(e.target.value)}
                    rows={4}
                  />
                </div>

                <Button 
                  onClick={() => handleResolveConflict(conflict)}
                  className="w-full"
                  disabled={!rationale.trim()}
                >
                  <Gavel className="mr-2 h-4 w-4" />
                  Resolve Conflict
                </Button>
              </CardContent>
            </Card>
          )}

          {/* Existing Resolution */}
          {conflict.resolution && (
            <Card>
              <CardHeader>
                <CardTitle className="text-lg flex items-center gap-2">
                  <CheckCircle className="h-5 w-5 text-green-500" />
                  Resolution
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <Label className="text-sm font-medium">Resolved By</Label>
                    <p>{conflict.resolution.resolved_by}</p>
                  </div>
                  <div>
                    <Label className="text-sm font-medium">Method</Label>
                    <Badge variant="outline">
                      {conflict.resolution.resolution_method.replace('_', ' ')}
                    </Badge>
                  </div>
                </div>
                <div>
                  <Label className="text-sm font-medium">Rationale</Label>
                  <p className="text-sm text-muted-foreground mt-1">
                    {conflict.resolution.rationale}
                  </p>
                </div>
                <div>
                  <Label className="text-sm font-medium">Final Scores</Label>
                  <div className="flex flex-wrap gap-2 mt-1">
                    {Object.entries(conflict.resolution.final_scores).map(([dimension, score]) => (
                      <Badge key={dimension} variant="secondary">
                        {dimension}: {score}
                      </Badge>
                    ))}
                  </div>
                </div>
              </CardContent>
            </Card>
          )}
        </div>
      </DialogContent>
    </Dialog>
  )

  return (
    <div className="space-y-6">
      {/* Conflict Summary */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Pending Conflicts</CardTitle>
            <AlertTriangle className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-red-600">
              {pendingConflicts.length}
            </div>
            <p className="text-xs text-muted-foreground">
              Require resolution
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Resolved Conflicts</CardTitle>
            <CheckCircle className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-green-600">
              {resolvedConflicts.length}
            </div>
            <p className="text-xs text-muted-foreground">
              Successfully resolved
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Resolution Rate</CardTitle>
            <TrendingUp className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {conflicts.length > 0 ? ((resolvedConflicts.length / conflicts.length) * 100).toFixed(1) : 0}%
            </div>
            <p className="text-xs text-muted-foreground">
              Of all conflicts
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Conflicts Tabs */}
      <Tabs defaultValue="pending" className="w-full">
        <TabsList className="grid w-full grid-cols-2">
          <TabsTrigger value="pending">
            Pending ({pendingConflicts.length})
          </TabsTrigger>
          <TabsTrigger value="resolved">
            Resolved ({resolvedConflicts.length})
          </TabsTrigger>
        </TabsList>

        {/* Pending Conflicts */}
        <TabsContent value="pending" className="space-y-4">
          {pendingConflicts.length === 0 ? (
            <Card>
              <CardContent className="py-8">
                <div className="text-center">
                  <CheckCircle className="h-12 w-12 text-green-500 mx-auto mb-4" />
                  <h3 className="text-lg font-semibold">No Pending Conflicts</h3>
                  <p className="text-muted-foreground">
                    All annotation conflicts have been resolved.
                  </p>
                </div>
              </CardContent>
            </Card>
          ) : (
            <Card>
              <CardHeader>
                <CardTitle>Pending Conflicts</CardTitle>
                <CardDescription>
                  Conflicts that require manual resolution
                </CardDescription>
              </CardHeader>
              <CardContent>
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Result ID</TableHead>
                      <TableHead>Severity</TableHead>
                      <TableHead>Conflicting Dimensions</TableHead>
                      <TableHead>Annotators</TableHead>
                      <TableHead>Actions</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {pendingConflicts.map((conflict) => (
                      <TableRow key={conflict.result_id}>
                        <TableCell className="font-medium">
                          {conflict.result_id.substring(0, 8)}...
                        </TableCell>
                        <TableCell>
                          <Badge {...getConflictSeverity(conflict.disagreement_score)}>
                            {getConflictSeverity(conflict.disagreement_score).level}
                          </Badge>
                        </TableCell>
                        <TableCell>
                          <div className="flex flex-wrap gap-1">
                            {conflict.conflicting_dimensions.slice(0, 2).map(dimension => (
                              <Badge key={dimension} variant="outline" className="text-xs">
                                {dimension}
                              </Badge>
                            ))}
                            {conflict.conflicting_dimensions.length > 2 && (
                              <Badge variant="outline" className="text-xs">
                                +{conflict.conflicting_dimensions.length - 2}
                              </Badge>
                            )}
                          </div>
                        </TableCell>
                        <TableCell>
                          <div className="flex items-center gap-1">
                            <Users className="h-4 w-4" />
                            <span>{conflict.annotations.length}</span>
                          </div>
                        </TableCell>
                        <TableCell>
                          <ConflictDetailsDialog conflict={conflict} />
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </CardContent>
            </Card>
          )}
        </TabsContent>

        {/* Resolved Conflicts */}
        <TabsContent value="resolved" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Resolved Conflicts</CardTitle>
              <CardDescription>
                Previously resolved annotation conflicts
              </CardDescription>
            </CardHeader>
            <CardContent>
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Result ID</TableHead>
                    <TableHead>Resolution Method</TableHead>
                    <TableHead>Resolved By</TableHead>
                    <TableHead>Date</TableHead>
                    <TableHead>Actions</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {resolvedConflicts.map((conflict) => (
                    <TableRow key={conflict.result_id}>
                      <TableCell className="font-medium">
                        {conflict.result_id.substring(0, 8)}...
                      </TableCell>
                      <TableCell>
                        <Badge variant="outline">
                          {conflict.resolution?.resolution_method.replace('_', ' ')}
                        </Badge>
                      </TableCell>
                      <TableCell>
                        {conflict.resolution?.resolved_by}
                      </TableCell>
                      <TableCell>
                        {conflict.resolution?.timestamp && 
                          new Date(conflict.resolution.timestamp).toLocaleDateString()
                        }
                      </TableCell>
                      <TableCell>
                        <ConflictDetailsDialog conflict={conflict} />
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