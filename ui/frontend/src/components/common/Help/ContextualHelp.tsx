import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Separator } from '@/components/ui/separator';
import { 
  HelpCircle, 
  BookOpen, 
  ExternalLink, 
  ChevronRight,
  X,
  Lightbulb
} from 'lucide-react';
import { cn } from '@/lib/utils';

interface ContextualHelpProps {
  section: string;
  className?: string;
}

interface HelpSection {
  title: string;
  description: string;
  tips: string[];
  links: Array<{
    title: string;
    url: string;
    external?: boolean;
  }>;
  examples?: Array<{
    title: string;
    content: string;
  }>;
}

const helpSections: Record<string, HelpSection> = {
  'dataset-upload': {
    title: 'Dataset Upload',
    description: 'Upload and configure your training data for prompt optimization.',
    tips: [
      'Use CSV or JSON format with clear column headers',
      'Ensure at least 50-100 examples for meaningful optimization',
      'Remove duplicates and inconsistent entries before upload',
      'Keep file size under 100MB for best performance'
    ],
    links: [
      { title: 'Dataset Management Guide', url: '/docs-static/user-guide/dataset-management.md' },
      { title: 'Data Quality Best Practices', url: '/docs-static/user-guide/getting-started.md#dataset-quality' }
    ],
    examples: [
      {
        title: 'CSV Format',
        content: 'input,output,category\n"What is AI?","Artificial Intelligence","tech"\n"How to cook pasta?","Boil water, add pasta","cooking"'
      },
      {
        title: 'JSON Format',
        content: '{"input": "What is AI?", "output": "Artificial Intelligence", "category": "tech"}'
      }
    ]
  },
  
  'prompt-editor': {
    title: 'Prompt Editor',
    description: 'Create and edit prompts with template variables for optimization.',
    tips: [
      'Use {{variable}} syntax for dynamic content',
      'Be specific and clear in your instructions',
      'Include examples in your prompt for better results',
      'Test with preview before optimization'
    ],
    links: [
      { title: 'Prompt Editing Guide', url: '/docs-static/user-guide/prompt-editing.md' },
      { title: 'Best Practices', url: '/docs-static/user-guide/prompt-editing.md#best-practices' }
    ],
    examples: [
      {
        title: 'Classification Prompt',
        content: 'Classify the following text into one of these categories: positive, negative, neutral.\n\nText: {{input}}\n\nCategory:'
      },
      {
        title: 'Question Answering',
        content: 'Answer the following question based on the context provided.\n\nContext: {{context}}\nQuestion: {{question}}\n\nAnswer:'
      }
    ]
  },
  
  'optimization-config': {
    title: 'Optimization Configuration',
    description: 'Configure optimization parameters for best results.',
    tips: [
      'Start with Nova Prompt Optimizer for general use',
      'Use 10-20 iterations for most cases',
      'Choose metrics that align with your business goals',
      'Test with smaller datasets first'
    ],
    links: [
      { title: 'Optimization Workflow', url: '/docs-static/user-guide/optimization-workflow.md' },
      { title: 'Optimizer Comparison', url: '/docs-static/user-guide/optimization-workflow.md#available-optimizers' }
    ]
  },
  
  'custom-metrics': {
    title: 'Custom Metrics',
    description: 'Define domain-specific evaluation criteria for your use case.',
    tips: [
      'Return scores between 0.0 and 1.0 (higher is better)',
      'Handle edge cases like empty strings',
      'Test thoroughly with sample data',
      'Use batch_apply() for better performance'
    ],
    links: [
      { title: 'Custom Metrics Guide', url: '/docs-static/user-guide/custom-metrics.md' },
      { title: 'Metric Examples', url: '/docs-static/user-guide/custom-metrics.md#example-implementations' }
    ],
    examples: [
      {
        title: 'Exact Match',
        content: 'def apply(self, prediction: str, ground_truth: str, **kwargs) -> float:\n    return 1.0 if prediction.strip().lower() == ground_truth.strip().lower() else 0.0'
      }
    ]
  },
  
  'annotation-workspace': {
    title: 'Annotation Workspace',
    description: 'Human annotation and quality assurance for optimization results.',
    tips: [
      'Review AI-generated rubrics before use',
      'Ensure consistent scoring across annotators',
      'Resolve conflicts to improve data quality',
      'Use annotation feedback to refine metrics'
    ],
    links: [
      { title: 'Human Annotation Guide', url: '/docs-static/user-guide/human-annotation.md' },
      { title: 'AI Rubric Generation', url: '/docs-static/user-guide/ai-rubric-generation.md' }
    ]
  }
};

export const ContextualHelp: React.FC<ContextualHelpProps> = ({
  section,
  className
}) => {
  const [isExpanded, setIsExpanded] = useState(false);
  const helpData = helpSections[section];

  if (!helpData) {
    return null;
  }

  return (
    <Card className={cn("border-blue-200 bg-blue-50/50 dark:border-blue-800 dark:bg-blue-950/20", className)}>
      <CardHeader className="pb-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <HelpCircle className="h-5 w-5 text-blue-600 dark:text-blue-400" />
            <CardTitle className="text-lg text-blue-900 dark:text-blue-100">
              {helpData.title}
            </CardTitle>
          </div>
          <Button
            variant="ghost"
            size="sm"
            onClick={() => setIsExpanded(!isExpanded)}
            className="text-blue-600 hover:text-blue-700 dark:text-blue-400"
          >
            {isExpanded ? <X className="h-4 w-4" /> : <ChevronRight className="h-4 w-4" />}
          </Button>
        </div>
        <p className="text-sm text-blue-800 dark:text-blue-200">
          {helpData.description}
        </p>
      </CardHeader>

      {isExpanded && (
        <CardContent className="pt-0 space-y-4">
          {/* Tips Section */}
          <div>
            <div className="flex items-center gap-2 mb-2">
              <Lightbulb className="h-4 w-4 text-amber-600" />
              <h4 className="font-medium text-sm">Tips</h4>
            </div>
            <ul className="space-y-1 text-sm text-muted-foreground">
              {helpData.tips.map((tip, index) => (
                <li key={index} className="flex items-start gap-2">
                  <span className="text-blue-600 mt-1">•</span>
                  <span>{tip}</span>
                </li>
              ))}
            </ul>
          </div>

          <Separator />

          {/* Examples Section */}
          {helpData.examples && helpData.examples.length > 0 && (
            <>
              <div>
                <div className="flex items-center gap-2 mb-2">
                  <BookOpen className="h-4 w-4 text-green-600" />
                  <h4 className="font-medium text-sm">Examples</h4>
                </div>
                <div className="space-y-3">
                  {helpData.examples.map((example, index) => (
                    <div key={index} className="space-y-1">
                      <Badge variant="outline" className="text-xs">
                        {example.title}
                      </Badge>
                      <pre className="text-xs bg-muted p-2 rounded border overflow-x-auto">
                        <code>{example.content}</code>
                      </pre>
                    </div>
                  ))}
                </div>
              </div>
              <Separator />
            </>
          )}

          {/* Links Section */}
          <div>
            <div className="flex items-center gap-2 mb-2">
              <ExternalLink className="h-4 w-4 text-purple-600" />
              <h4 className="font-medium text-sm">Learn More</h4>
            </div>
            <div className="space-y-1">
              {helpData.links.map((link, index) => (
                <a
                  key={index}
                  href={link.url}
                  target={link.external ? "_blank" : "_self"}
                  rel={link.external ? "noopener noreferrer" : undefined}
                  className="flex items-center gap-2 text-sm text-blue-600 hover:text-blue-700 dark:text-blue-400 hover:underline"
                >
                  <ChevronRight className="h-3 w-3" />
                  {link.title}
                  {link.external && <ExternalLink className="h-3 w-3" />}
                </a>
              ))}
            </div>
          </div>
        </CardContent>
      )}
    </Card>
  );
};

// Quick help component for inline use
export const QuickHelp: React.FC<{
  title: string;
  content: string;
  className?: string;
}> = ({ title, content, className }) => {
  return (
    <div className={cn("flex items-start gap-2 p-3 bg-blue-50 dark:bg-blue-950/20 rounded-lg border border-blue-200 dark:border-blue-800", className)}>
      <HelpCircle className="h-4 w-4 text-blue-600 dark:text-blue-400 mt-0.5 flex-shrink-0" />
      <div className="space-y-1">
        <h4 className="font-medium text-sm text-blue-900 dark:text-blue-100">
          {title}
        </h4>
        <p className="text-sm text-blue-800 dark:text-blue-200">
          {content}
        </p>
      </div>
    </div>
  );
};