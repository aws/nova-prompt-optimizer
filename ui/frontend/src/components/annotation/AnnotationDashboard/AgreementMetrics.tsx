import React from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Progress } from '@/components/ui/progress'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { 
  TrendingUp, 
  TrendingDown, 
  AlertTriangle, 
  Users, 
  Target,
  BarChart3,
  Eye
} from 'lucide-react'
import { AgreementMetrics as AgreementMetricsType } from '@/types/annotation'

interface AgreementMetricsProps {
  metrics: AgreementMetricsType
  onDrillDown: (dimension: string) => void
}

export const AgreementMetrics: React.FC<AgreementMetricsProps> = ({
  metrics,
  onDrillDown
}) => {
  // const [selectedDimension, setSelectedDimension] = useState<string | null>(null)

  const getAgreementColor = (agreement: number) => {
    if (agreement >= 0.8) return 'text-green-600'
    if (agreement >= 0.6) return 'text-yellow-600'
    return 'text-red-600'
  }

  const getAgreementBadge = (agreement: number) => {
    if (agreement >= 0.8) return { variant: 'default' as const, label: 'High' }
    if (agreement >= 0.6) return { variant: 'secondary' as const, label: 'Medium' }
    return { variant: 'destructive' as const, label: 'Low' }
  }

  const sortedDimensions = Object.entries(metrics.dimension_agreement)
    .sort(([, a], [, b]) => a - b)

  const sortedAnnotators = Object.entries(metrics.annotator_consistency)
    .sort(([, a], [, b]) => b - a)

  return (
    <div className="space-y-6">
      {/* Overall Agreement Summary */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Overall Agreement</CardTitle>
            <Users className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {(metrics.overall_agreement * 100).toFixed(1)}%
            </div>
            <div className="flex items-center gap-2 mt-2">
              <Badge {...getAgreementBadge(metrics.overall_agreement)}>
                {getAgreementBadge(metrics.overall_agreement).label}
              </Badge>
              {metrics.overall_agreement >= 0.8 ? (
                <TrendingUp className="h-4 w-4 text-green-500" />
              ) : (
                <TrendingDown className="h-4 w-4 text-red-500" />
              )}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Active Conflicts</CardTitle>
            <AlertTriangle className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {metrics.conflicts.filter(c => c.resolution_status === 'pending').length}
            </div>
            <p className="text-xs text-muted-foreground">
              {metrics.conflicts.length} total conflicts
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Dimensions Tracked</CardTitle>
            <Target className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {Object.keys(metrics.dimension_agreement).length}
            </div>
            <p className="text-xs text-muted-foreground">
              Evaluation dimensions
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Agreement Analysis Tabs */}
      <Tabs defaultValue="dimensions" className="w-full">
        <TabsList className="grid w-full grid-cols-3">
          <TabsTrigger value="dimensions">By Dimension</TabsTrigger>
          <TabsTrigger value="annotators">By Annotator</TabsTrigger>
          <TabsTrigger value="trends">Trends</TabsTrigger>
        </TabsList>

        {/* Dimensions Tab */}
        <TabsContent value="dimensions" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Agreement by Dimension</CardTitle>
              <CardDescription>
                Inter-annotator agreement for each evaluation dimension
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {sortedDimensions.map(([dimension, agreement]) => (
                  <div key={dimension} className="space-y-2">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        <span className="font-medium">{dimension}</span>
                        <Badge {...getAgreementBadge(agreement)}>
                          {getAgreementBadge(agreement).label}
                        </Badge>
                      </div>
                      <div className="flex items-center gap-2">
                        <span className={`text-sm font-medium ${getAgreementColor(agreement)}`}>
                          {(agreement * 100).toFixed(1)}%
                        </span>
                        <Button
                          size="sm"
                          variant="ghost"
                          onClick={() => onDrillDown(dimension)}
                        >
                          <Eye className="h-4 w-4" />
                        </Button>
                      </div>
                    </div>
                    <Progress value={agreement * 100} className="w-full" />
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          {/* Low Agreement Alert */}
          {sortedDimensions.some(([, agreement]) => agreement < 0.6) && (
            <Alert variant="destructive">
              <AlertTriangle className="h-4 w-4" />
              <AlertDescription>
                Some dimensions have low agreement scores. Consider providing additional 
                training or clarifying evaluation criteria for these dimensions.
              </AlertDescription>
            </Alert>
          )}
        </TabsContent>

        {/* Annotators Tab */}
        <TabsContent value="annotators" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Annotator Consistency</CardTitle>
              <CardDescription>
                Individual annotator consistency and reliability metrics
              </CardDescription>
            </CardHeader>
            <CardContent>
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Annotator</TableHead>
                    <TableHead>Consistency Score</TableHead>
                    <TableHead>Agreement with Others</TableHead>
                    <TableHead>Annotations Count</TableHead>
                    <TableHead>Status</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {sortedAnnotators.map(([annotatorId, consistency]) => {
                    const annotationCount = Math.floor(Math.random() * 100) + 20 // Placeholder
                    const agreementWithOthers = Math.random() * 0.4 + 0.6 // Placeholder
                    
                    return (
                      <TableRow key={annotatorId}>
                        <TableCell className="font-medium">{annotatorId}</TableCell>
                        <TableCell>
                          <div className="flex items-center gap-2">
                            <Progress value={consistency * 100} className="w-20" />
                            <span className="text-sm">{(consistency * 100).toFixed(1)}%</span>
                          </div>
                        </TableCell>
                        <TableCell>
                          <span className={getAgreementColor(agreementWithOthers)}>
                            {(agreementWithOthers * 100).toFixed(1)}%
                          </span>
                        </TableCell>
                        <TableCell>{annotationCount}</TableCell>
                        <TableCell>
                          <Badge variant={consistency > 0.8 ? 'default' : 'secondary'}>
                            {consistency > 0.8 ? 'Reliable' : 'Needs Review'}
                          </Badge>
                        </TableCell>
                      </TableRow>
                    )
                  })}
                </TableBody>
              </Table>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Trends Tab */}
        <TabsContent value="trends" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Agreement Trends</CardTitle>
              <CardDescription>
                Historical agreement patterns and improvement over time
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {/* Placeholder for trend visualization */}
                <div className="h-64 bg-muted rounded-lg flex items-center justify-center">
                  <div className="text-center">
                    <BarChart3 className="h-12 w-12 text-muted-foreground mx-auto mb-2" />
                    <p className="text-muted-foreground">
                      Agreement trend chart would be displayed here
                    </p>
                  </div>
                </div>

                {/* Trend Summary */}
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <Card>
                    <CardHeader className="pb-2">
                      <CardTitle className="text-sm">This Week</CardTitle>
                    </CardHeader>
                    <CardContent>
                      <div className="text-lg font-bold">
                        {(metrics.overall_agreement * 100).toFixed(1)}%
                      </div>
                      <div className="flex items-center gap-1 text-sm text-green-600">
                        <TrendingUp className="h-3 w-3" />
                        +2.3% from last week
                      </div>
                    </CardContent>
                  </Card>

                  <Card>
                    <CardHeader className="pb-2">
                      <CardTitle className="text-sm">Best Dimension</CardTitle>
                    </CardHeader>
                    <CardContent>
                      <div className="text-lg font-bold">
                        {sortedDimensions[sortedDimensions.length - 1]?.[0] || 'N/A'}
                      </div>
                      <div className="text-sm text-muted-foreground">
                        {((sortedDimensions[sortedDimensions.length - 1]?.[1] || 0) * 100).toFixed(1)}% agreement
                      </div>
                    </CardContent>
                  </Card>

                  <Card>
                    <CardHeader className="pb-2">
                      <CardTitle className="text-sm">Needs Attention</CardTitle>
                    </CardHeader>
                    <CardContent>
                      <div className="text-lg font-bold">
                        {sortedDimensions[0]?.[0] || 'N/A'}
                      </div>
                      <div className="text-sm text-red-600">
                        {((sortedDimensions[0]?.[1] || 0) * 100).toFixed(1)}% agreement
                      </div>
                    </CardContent>
                  </Card>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  )
}