import React from 'react';
import { cn } from '@/lib/utils';

import { Separator } from '@/components/ui/separator';

interface PageHeaderProps {
  title: string;
  description?: string;
  children?: React.ReactNode;
  actions?: React.ReactNode;
  className?: string;
}

export const PageHeader: React.FC<PageHeaderProps> = ({
  title,
  description,
  children,
  actions,
  className,
}) => {
  return (
    <div className={cn('space-y-6', className)}>
      <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
        <div className="space-y-1">
          <h1 className="text-3xl font-bold tracking-tight">{title}</h1>
          {description && (
            <p className="text-muted-foreground max-w-2xl">{description}</p>
          )}
        </div>
        {actions && (
          <div className="flex flex-col gap-2 sm:flex-row sm:items-center">
            {actions}
          </div>
        )}
      </div>
      {children}
      <Separator />
    </div>
  );
};