import React, { useState } from 'react';
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Separator } from '@/components/ui/separator';
import { Skeleton } from '@/components/ui/skeleton';
import { LoadingSpinner, ProgressBar } from '../Loading';
import { StatusIndicator } from '../StatusIndicator';
import { DataTable } from '../DataDisplay';
import { GridLayout, FlexLayout, PageHeader } from '../Layout';
import { AlertCircle, Info } from 'lucide-react';

// Sample data for DataTable
const sampleData = [
  { id: 1, name: 'Dataset 1', status: 'active', rows: 1000, created: '2024-01-15' },
  { id: 2, name: 'Dataset 2', status: 'processing', rows: 2500, created: '2024-01-16' },
  { id: 3, name: 'Dataset 3', status: 'error', rows: 0, created: '2024-01-17' },
];

const columns = [
  { key: 'name', header: 'Name' },
  { key: 'status', header: 'Status', render: (value: string) => <StatusIndicator status={value as any} /> },
  { key: 'rows', header: 'Rows' },
  { key: 'created', header: 'Created' },
];

export const ComponentShowcase: React.FC = () => {
  const [progress] = useState(65);
  const [loading, setLoading] = useState(false);

  const handleLoadingDemo = () => {
    setLoading(true);
    setTimeout(() => setLoading(false), 2000);
  };

  return (
    <div className="space-y-8 p-6">
      <PageHeader
        title="Shadcn/UI Component Showcase"
        description="A demonstration of all the custom components built on Shadcn/UI primitives for the Nova Prompt Optimizer"
        actions={
          <Button onClick={handleLoadingDemo} disabled={loading}>
            {loading ? <LoadingSpinner size="sm" /> : 'Demo Loading'}
          </Button>
        }
      />

      <Tabs defaultValue="basic" className="w-full">
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="basic">Basic Components</TabsTrigger>
          <TabsTrigger value="data">Data Display</TabsTrigger>
          <TabsTrigger value="feedback">Feedback</TabsTrigger>
          <TabsTrigger value="layout">Layout</TabsTrigger>
        </TabsList>

        <TabsContent value="basic" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Basic UI Components</CardTitle>
              <CardDescription>
                Core Shadcn/UI components with consistent styling
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex flex-wrap gap-2">
                <Button>Primary Button</Button>
                <Button variant="secondary">Secondary</Button>
                <Button variant="outline">Outline</Button>
                <Button variant="ghost">Ghost</Button>
                <Button variant="destructive">Destructive</Button>
              </div>
              
              <Separator />
              
              <div className="space-y-2">
                <Input placeholder="Enter your text here..." />
                <div className="flex gap-2">
                  <Badge>Default</Badge>
                  <Badge variant="secondary">Secondary</Badge>
                  <Badge variant="outline">Outline</Badge>
                  <Badge variant="destructive">Destructive</Badge>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="data" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Data Display Components</CardTitle>
              <CardDescription>
                Custom components for displaying data with consistent formatting
              </CardDescription>
            </CardHeader>
            <CardContent>
              <DataTable
                data={sampleData}
                columns={columns}
                loading={loading}
                emptyMessage="No datasets found"
              />
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="feedback" className="space-y-6">
          <GridLayout columns={2} gap="lg">
            <Card>
              <CardHeader>
                <CardTitle>Status Indicators</CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <div className="flex flex-wrap gap-2">
                  <StatusIndicator status="success" text="Completed" />
                  <StatusIndicator status="error" text="Failed" />
                  <StatusIndicator status="warning" text="Warning" />
                  <StatusIndicator status="running" text="Processing" />
                  <StatusIndicator status="pending" text="Queued" />
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Progress Indicators</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <LoadingSpinner text="Loading data..." />
                <ProgressBar 
                  value={progress} 
                  label="Optimization Progress" 
                  showPercentage 
                />
                <Progress value={33} className="w-full" />
              </CardContent>
            </Card>
          </GridLayout>

          <div className="space-y-4">
            <Alert>
              <Info className="h-4 w-4" />
              <AlertTitle>Information</AlertTitle>
              <AlertDescription>
                This is an informational alert using Shadcn/UI components.
              </AlertDescription>
            </Alert>

            <Alert variant="destructive">
              <AlertCircle className="h-4 w-4" />
              <AlertTitle>Error</AlertTitle>
              <AlertDescription>
                Something went wrong. Please try again.
              </AlertDescription>
            </Alert>
          </div>
        </TabsContent>

        <TabsContent value="layout" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Layout Components</CardTitle>
              <CardDescription>
                Responsive layout utilities built on Tailwind CSS
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <div>
                <h4 className="text-sm font-medium mb-3">Grid Layout (3 columns)</h4>
                <GridLayout columns={3} gap="md">
                  <Card className="p-4">
                    <div className="text-center">Grid Item 1</div>
                  </Card>
                  <Card className="p-4">
                    <div className="text-center">Grid Item 2</div>
                  </Card>
                  <Card className="p-4">
                    <div className="text-center">Grid Item 3</div>
                  </Card>
                </GridLayout>
              </div>

              <Separator />

              <div>
                <h4 className="text-sm font-medium mb-3">Flex Layout</h4>
                <FlexLayout justify="between" align="center" className="p-4 border rounded-md">
                  <div>Left Content</div>
                  <div>Center Content</div>
                  <div>Right Content</div>
                </FlexLayout>
              </div>

              <Separator />

              <div>
                <h4 className="text-sm font-medium mb-3">Loading Skeletons</h4>
                <div className="space-y-2">
                  <Skeleton className="h-4 w-full" />
                  <Skeleton className="h-4 w-3/4" />
                  <Skeleton className="h-4 w-1/2" />
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
};