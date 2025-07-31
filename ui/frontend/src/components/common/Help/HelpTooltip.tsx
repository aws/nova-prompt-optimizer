import React from 'react';
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from '@/components/ui/tooltip';
import { HelpCircle } from 'lucide-react';
import { cn } from '@/lib/utils';

interface HelpTooltipProps {
  content: string | React.ReactNode;
  children?: React.ReactNode;
  side?: 'top' | 'right' | 'bottom' | 'left';
  className?: string;
  iconClassName?: string;
  showIcon?: boolean;
}

export const HelpTooltip: React.FC<HelpTooltipProps> = ({
  content,
  children,
  side = 'top',
  className,
  iconClassName,
  showIcon = true
}) => {
  return (
    <TooltipProvider>
      <Tooltip>
        <TooltipTrigger asChild>
          {children || (
            showIcon && (
              <HelpCircle 
                className={cn(
                  "h-4 w-4 text-muted-foreground hover:text-foreground cursor-help",
                  iconClassName
                )} 
              />
            )
          )}
        </TooltipTrigger>
        <TooltipContent side={side} className={cn("max-w-xs", className)}>
          {typeof content === 'string' ? (
            <p className="text-sm">{content}</p>
          ) : (
            content
          )}
        </TooltipContent>
      </Tooltip>
    </TooltipProvider>
  );
};

// Predefined help content for common use cases
export const HelpContent = {
  dataset: {
    upload: "Upload CSV or JSON files with your training data. Ensure you have input and output columns clearly defined.",
    columnMapping: "Select which columns contain your input prompts and expected outputs. Multiple columns can be selected.",
    trainTestSplit: "Ratio for splitting data into training (for optimization) and test (for evaluation) sets. Default 80/20 is recommended.",
    preview: "Review your data to ensure it's formatted correctly before processing."
  },
  
  prompt: {
    systemPrompt: "Optional instructions that set the context and behavior for the AI model. This applies to all interactions.",
    userPrompt: "The main prompt template with variables like {{input}} that will be replaced with your data.",
    variables: "Variables in double curly braces {{variable}} that will be replaced with values from your dataset columns.",
    preview: "See how your prompt will look with actual data from your dataset."
  },
  
  optimization: {
    optimizer: "Choose the optimization algorithm. Nova Prompt Optimizer is recommended for most use cases.",
    model: "Select the AI model to use. Nova Pro provides best results, Nova Lite is faster and cheaper.",
    iterations: "Number of optimization rounds. More iterations may improve results but take longer.",
    metrics: "Evaluation criteria used to measure prompt performance. Choose metrics that align with your goals."
  },
  
  metrics: {
    custom: "Write Python code to evaluate predictions. Must implement apply() method returning 0.0-1.0 score.",
    testing: "Test your metric with sample data to ensure it works correctly before using in optimization.",
    batch: "Implement batch_apply() for better performance when evaluating many predictions at once."
  },
  
  annotation: {
    rubric: "AI-generated evaluation criteria based on your dataset. Edit to match your quality standards.",
    agreement: "Measure of how consistently different annotators score the same content.",
    conflicts: "Cases where annotators disagree significantly. Resolve to improve data quality."
  }
};

// Specific help tooltips for common scenarios
export const DatasetUploadHelp = () => (
  <HelpTooltip content={HelpContent.dataset.upload} />
);

export const PromptVariablesHelp = () => (
  <HelpTooltip content={HelpContent.prompt.variables} />
);

export const OptimizationIterationsHelp = () => (
  <HelpTooltip content={HelpContent.optimization.iterations} />
);

export const CustomMetricsHelp = () => (
  <HelpTooltip content={HelpContent.metrics.custom} />
);