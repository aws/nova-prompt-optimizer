import React from 'react'
import { Navigation } from './Navigation'
import { ErrorBoundary } from '../ErrorBoundary'
import { Toaster } from '@/components/ui/toaster'

interface AppLayoutProps {
  children: React.ReactNode
}

export const AppLayout: React.FC<AppLayoutProps> = ({ children }) => {
  return (
    <div className="min-h-screen bg-background">
      <Navigation />
      <main className="container mx-auto px-4 py-8 max-w-7xl">
        <ErrorBoundary>
          {children}
        </ErrorBoundary>
      </main>
      <Toaster />
    </div>
  )
}