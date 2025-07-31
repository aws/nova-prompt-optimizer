import React from 'react';
import { Badge } from '@/components/ui/badge';
import { cn } from '@/lib/utils';
import { 
  CheckCircle, 
  XCircle, 
  Clock, 
  AlertCircle, 
  Loader2,
  Pause
} from 'lucide-react';

export type StatusType = 
  | 'success' 
  | 'error' 
  | 'warning' 
  | 'info' 
  | 'pending' 
  | 'running' 
  | 'paused' 
  | 'cancelled';

interface StatusIndicatorProps {
  status: StatusType;
  text?: string;
  showIcon?: boolean;
  size?: 'sm' | 'md' | 'lg';
  className?: string;
}

const statusConfig = {
  success: {
    variant: 'default' as const,
    icon: CheckCircle,
    color: 'text-green-600',
    bgColor: 'bg-green-50 border-green-200',
  },
  error: {
    variant: 'destructive' as const,
    icon: XCircle,
    color: 'text-red-600',
    bgColor: 'bg-red-50 border-red-200',
  },
  warning: {
    variant: 'secondary' as const,
    icon: AlertCircle,
    color: 'text-yellow-600',
    bgColor: 'bg-yellow-50 border-yellow-200',
  },
  info: {
    variant: 'secondary' as const,
    icon: AlertCircle,
    color: 'text-blue-600',
    bgColor: 'bg-blue-50 border-blue-200',
  },
  pending: {
    variant: 'outline' as const,
    icon: Clock,
    color: 'text-gray-600',
    bgColor: 'bg-gray-50 border-gray-200',
  },
  running: {
    variant: 'default' as const,
    icon: Loader2,
    color: 'text-blue-600',
    bgColor: 'bg-blue-50 border-blue-200',
  },
  paused: {
    variant: 'secondary' as const,
    icon: Pause,
    color: 'text-orange-600',
    bgColor: 'bg-orange-50 border-orange-200',
  },
  cancelled: {
    variant: 'outline' as const,
    icon: XCircle,
    color: 'text-gray-600',
    bgColor: 'bg-gray-50 border-gray-200',
  },
};

const sizeClasses = {
  sm: 'h-3 w-3',
  md: 'h-4 w-4',
  lg: 'h-5 w-5',
};

export const StatusIndicator: React.FC<StatusIndicatorProps> = ({
  status,
  text,
  showIcon = true,
  size = 'md',
  className,
}) => {
  const config = statusConfig[status];
  const Icon = config.icon;

  return (
    <Badge variant={config.variant} className={cn('flex items-center gap-1', className)}>
      {showIcon && (
        <Icon 
          className={cn(
            sizeClasses[size],
            status === 'running' && 'animate-spin'
          )} 
        />
      )}
      {text || status.charAt(0).toUpperCase() + status.slice(1)}
    </Badge>
  );
};