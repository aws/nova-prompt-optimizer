import { useState, useCallback } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Textarea } from '@/components/ui/textarea'
import { Badge } from '@/components/ui/badge'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { Separator } from '@/components/ui/separator'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { 
  Play, 
  Plus, 
  Trash2, 
  CheckCircle, 
  XCircle, 
  AlertTriangle,
  Clock,
  Target,
  TrendingUp
} from 'lucide-react'
import { cn } from '@/lib/utils'
import type { MetricTestCase, MetricTestResult } from '@/types/metric'

interface MetricTesterProps {
  code: string
  testCases: MetricTestCase[]
  onTestCasesChange: (testCases: MetricTestCase[]) => void
  onTest: () => Promise<void>
  testResult?: MetricTestResult | null
  loading?: boolean
  className?: string
}

interface TestCaseFormData {
  name: string
  predictions: string
  ground_truth: string
  expected_result: string
}

const DEFAULT_TEST_CASE: TestCaseFormData = {
  name: '',
  predictions: '',
  ground_truth: '',
  expected_result: ''
}

export function MetricTester({
  code,
  testCases,
  onTestCasesChange,
  onTest,
  testResult,
  loading = false,
  className
}: MetricTesterProps) {
  const [newTestCase, setNewTestCase] = useState<TestCaseFormData>(DEFAULT_TEST_CASE)
  const [activeTab, setActiveTab] = useState<'cases' | 'results'>('cases')

  // Parse JSON safely
  const parseJSON = useCallback((jsonString: string): any => {
    try {
      return JSON.parse(jsonString)
    } catch {
      // Try to parse as array of strings
      const lines = jsonString.split('\n').filter(line => line.trim())
      if (lines.length === 1) {
        return lines[0].trim()
      }
      return lines.map(line => line.trim())
    }
  }, [])

  // Add new test case
  const handleAddTestCase = useCallback(() => {
    if (!newTestCase.name.trim() || !newTestCase.predictions.trim() || !newTestCase.ground_truth.trim()) {
      return
    }

    try {
      const predictions = parseJSON(newTestCase.predictions)
      const ground_truth = parseJSON(newTestCase.ground_truth)
      const expected_result = newTestCase.expected_result.trim() 
        ? parseJSON(newTestCase.expected_result) 
        : undefined

      const testCase: MetricTestCase = {
        id: `test_${Date.now()}`,
        name: newTestCase.name.trim(),
        predictions: Array.isArray(predictions) ? predictions : [predictions],
        ground_truth: Array.isArray(ground_truth) ? ground_truth : [ground_truth],
        expected_result
      }

      onTestCasesChange([...testCases, testCase])
      setNewTestCase(DEFAULT_TEST_CASE)
    } catch (error) {
      // Handle parsing error - could show a toast or alert
      console.error('Failed to parse test case data:', error)
    }
  }, [newTestCase, testCases, onTestCasesChange, parseJSON])

  // Remove test case
  const handleRemoveTestCase = useCallback((id: string) => {
    onTestCasesChange(testCases.filter(tc => tc.id !== id))
  }, [testCases, onTestCasesChange])

  // Update test case form
  const handleTestCaseChange = useCallback((field: keyof TestCaseFormData, value: string) => {
    setNewTestCase(prev => ({ ...prev, [field]: value }))
  }, [])

  // Run tests
  const handleRunTests = useCallback(async () => {
    if (testCases.length === 0) {
      return
    }
    
    setActiveTab('results')
    await onTest()
  }, [testCases.length, onTest])

  // Format result for display
  const formatResult = useCallback((result: any): string => {
    if (typeof result === 'number') {
      return result.toFixed(4)
    }
    if (typeof result === 'object') {
      return JSON.stringify(result, null, 2)
    }
    return String(result)
  }, [])

  const canAddTestCase = newTestCase.name.trim() && newTestCase.predictions.trim() && newTestCase.ground_truth.trim()
  const canRunTests = testCases.length > 0 && code.trim()

  return (
    <div className={cn('space-y-4', className)}>
      <Tabs value={activeTab} onValueChange={(value) => setActiveTab(value as 'cases' | 'results')}>
        <TabsList className="grid w-full grid-cols-2">
          <TabsTrigger value="cases" className="flex items-center gap-2">
            <Target className="h-4 w-4" />
            Test Cases ({testCases.length})
          </TabsTrigger>
          <TabsTrigger value="results" className="flex items-center gap-2">
            <TrendingUp className="h-4 w-4" />
            Results
          </TabsTrigger>
        </TabsList>

        <TabsContent value="cases" className="space-y-4">
          {/* Add New Test Case */}
          <Card>
            <CardHeader>
              <CardTitle className="text-lg">Add Test Case</CardTitle>
              <CardDescription>
                Create test cases to validate your metric implementation
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="test-name">Test Name</Label>
                  <Input
                    id="test-name"
                    value={newTestCase.name}
                    onChange={(e) => handleTestCaseChange('name', e.target.value)}
                    placeholder="e.g., Basic accuracy test"
                    disabled={loading}
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="expected-result">Expected Result (Optional)</Label>
                  <Input
                    id="expected-result"
                    value={newTestCase.expected_result}
                    onChange={(e) => handleTestCaseChange('expected_result', e.target.value)}
                    placeholder='e.g., 0.75 or {"accuracy": 0.8}'
                    disabled={loading}
                  />
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="predictions">Predictions</Label>
                  <Textarea
                    id="predictions"
                    value={newTestCase.predictions}
                    onChange={(e) => handleTestCaseChange('predictions', e.target.value)}
                    placeholder={`["cat", "dog", "bird"]\nor one per line:\ncat\ndog\nbird`}
                    rows={4}
                    disabled={loading}
                  />
                  <div className="text-xs text-muted-foreground">
                    JSON array or one value per line
                  </div>
                </div>
                <div className="space-y-2">
                  <Label htmlFor="ground-truth">Ground Truth</Label>
                  <Textarea
                    id="ground-truth"
                    value={newTestCase.ground_truth}
                    onChange={(e) => handleTestCaseChange('ground_truth', e.target.value)}
                    placeholder={`["cat", "cat", "bird"]\nor one per line:\ncat\ncat\nbird`}
                    rows={4}
                    disabled={loading}
                  />
                  <div className="text-xs text-muted-foreground">
                    JSON array or one value per line
                  </div>
                </div>
              </div>

              <Button 
                onClick={handleAddTestCase}
                disabled={!canAddTestCase || loading}
                className="w-full"
              >
                <Plus className="mr-2 h-4 w-4" />
                Add Test Case
              </Button>
            </CardContent>
          </Card>

          {/* Existing Test Cases */}
          {testCases.length > 0 && (
            <Card>
              <CardHeader>
                <CardTitle className="text-lg">Test Cases</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                {testCases.map((testCase, index) => (
                  <div key={testCase.id} className="border rounded-lg p-4 space-y-3">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        <Badge variant="outline">#{index + 1}</Badge>
                        <span className="font-medium">{testCase.name}</span>
                      </div>
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => handleRemoveTestCase(testCase.id)}
                        disabled={loading}
                      >
                        <Trash2 className="h-4 w-4" />
                      </Button>
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
                      <div>
                        <Label className="text-xs font-medium text-muted-foreground">Predictions</Label>
                        <div className="mt-1 p-2 bg-muted/50 rounded text-xs font-mono">
                          {JSON.stringify(testCase.predictions, null, 2)}
                        </div>
                      </div>
                      <div>
                        <Label className="text-xs font-medium text-muted-foreground">Ground Truth</Label>
                        <div className="mt-1 p-2 bg-muted/50 rounded text-xs font-mono">
                          {JSON.stringify(testCase.ground_truth, null, 2)}
                        </div>
                      </div>
                    </div>

                    {testCase.expected_result !== undefined && (
                      <div>
                        <Label className="text-xs font-medium text-muted-foreground">Expected Result</Label>
                        <div className="mt-1 p-2 bg-muted/50 rounded text-xs font-mono">
                          {formatResult(testCase.expected_result)}
                        </div>
                      </div>
                    )}
                  </div>
                ))}

                <Separator />

                <Button 
                  onClick={handleRunTests}
                  disabled={!canRunTests || loading}
                  className="w-full"
                >
                  <Play className="mr-2 h-4 w-4" />
                  {loading ? 'Running Tests...' : 'Run All Tests'}
                </Button>
              </CardContent>
            </Card>
          )}

          {testCases.length === 0 && (
            <Card>
              <CardContent className="pt-6">
                <div className="text-center text-muted-foreground">
                  <Target className="mx-auto h-12 w-12 mb-4 opacity-50" />
                  <p>No test cases yet</p>
                  <p className="text-sm">Add test cases to validate your metric implementation</p>
                </div>
              </CardContent>
            </Card>
          )}
        </TabsContent>

        <TabsContent value="results" className="space-y-4">
          {testResult ? (
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  {testResult.success ? (
                    <CheckCircle className="h-5 w-5 text-green-500" />
                  ) : (
                    <XCircle className="h-5 w-5 text-red-500" />
                  )}
                  Test Results
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                {/* Overall Status */}
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                  <div className="text-center">
                    <div className="text-2xl font-bold">
                      {testResult.success ? (
                        <span className="text-green-500">PASS</span>
                      ) : (
                        <span className="text-red-500">FAIL</span>
                      )}
                    </div>
                    <div className="text-sm text-muted-foreground">Status</div>
                  </div>
                  {testResult.test_cases_passed !== undefined && testResult.test_cases_total !== undefined && (
                    <div className="text-center">
                      <div className="text-2xl font-bold">
                        {testResult.test_cases_passed}/{testResult.test_cases_total}
                      </div>
                      <div className="text-sm text-muted-foreground">Cases Passed</div>
                    </div>
                  )}
                  {testResult.execution_time !== undefined && (
                    <div className="text-center">
                      <div className="text-2xl font-bold flex items-center justify-center gap-1">
                        <Clock className="h-5 w-5" />
                        {testResult.execution_time.toFixed(3)}s
                      </div>
                      <div className="text-sm text-muted-foreground">Execution Time</div>
                    </div>
                  )}
                  {testResult.result !== undefined && (
                    <div className="text-center">
                      <div className="text-2xl font-bold">
                        {formatResult(testResult.result)}
                      </div>
                      <div className="text-sm text-muted-foreground">Result</div>
                    </div>
                  )}
                </div>

                {/* Error Details */}
                {!testResult.success && testResult.error && (
                  <Alert variant="destructive">
                    <AlertTriangle className="h-4 w-4" />
                    <AlertDescription>
                      <div className="font-medium mb-2">Test Failed</div>
                      <div className="text-sm font-mono bg-destructive/10 p-2 rounded">
                        {testResult.error}
                      </div>
                    </AlertDescription>
                  </Alert>
                )}

                {/* Success Details */}
                {testResult.success && testResult.result !== undefined && (
                  <Alert>
                    <CheckCircle className="h-4 w-4" />
                    <AlertDescription>
                      <div className="font-medium mb-2">Test Passed Successfully</div>
                      <div className="text-sm">
                        Your metric implementation is working correctly with the provided test cases.
                      </div>
                      {typeof testResult.result === 'object' && (
                        <div className="mt-2 p-2 bg-muted/50 rounded text-xs font-mono">
                          {JSON.stringify(testResult.result, null, 2)}
                        </div>
                      )}
                    </AlertDescription>
                  </Alert>
                )}
              </CardContent>
            </Card>
          ) : (
            <Card>
              <CardContent className="pt-6">
                <div className="text-center text-muted-foreground">
                  <TrendingUp className="mx-auto h-12 w-12 mb-4 opacity-50" />
                  <p>No test results yet</p>
                  <p className="text-sm">Run your test cases to see results here</p>
                  {testCases.length === 0 && (
                    <Button 
                      variant="outline" 
                      className="mt-4"
                      onClick={() => setActiveTab('cases')}
                    >
                      Add Test Cases
                    </Button>
                  )}
                </div>
              </CardContent>
            </Card>
          )}
        </TabsContent>
      </Tabs>
    </div>
  )
}

export default MetricTester