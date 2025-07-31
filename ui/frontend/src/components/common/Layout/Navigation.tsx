import React from 'react'
import { Link, useLocation } from 'react-router-dom'
import { cn } from '@/lib/utils'
import { Button } from '@/components/ui/button'
import { Sheet, SheetContent, SheetTrigger } from '@/components/ui/sheet'
import { Badge } from '@/components/ui/badge'
import { Menu, Sparkles } from 'lucide-react'
import { ThemeToggle } from '../ThemeToggle'

const navigationItems = [
  { path: '/', label: 'Dashboard', icon: '📊' },
  { path: '/datasets', label: 'Datasets', icon: '📁' },
  { path: '/prompts', label: 'Prompts', icon: '✏️' },
  { path: '/optimize', label: 'Optimize', icon: '🚀' },
  { path: '/annotate', label: 'Annotate', icon: '📝' },
  { path: '/results', label: 'Results', icon: '📈' },
]

export const Navigation: React.FC = () => {
  const location = useLocation()

  const NavItems = () => (
    <>
      {navigationItems.map((item) => (
        <Link
          key={item.path}
          to={item.path}
          className={cn(
            "flex items-center gap-2 text-sm font-medium transition-colors hover:text-primary px-3 py-2 rounded-md",
            location.pathname === item.path
              ? "text-primary bg-primary/10"
              : "text-muted-foreground hover:bg-accent"
          )}
        >
          <span className="text-base">{item.icon}</span>
          {item.label}
        </Link>
      ))}
    </>
  )

  return (
    <nav className="sticky top-0 z-50 border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
      <div className="container mx-auto px-4">
        <div className="flex h-16 items-center justify-between">
          <div className="flex items-center space-x-8">
            <Link to="/" className="flex items-center gap-2 text-xl font-bold text-primary">
              <Sparkles className="h-6 w-6" />
              Nova Prompt Optimizer
              <Badge variant="secondary" className="text-xs">
                Preview
              </Badge>
            </Link>
            
            {/* Desktop Navigation */}
            <div className="hidden md:flex space-x-2">
              <NavItems />
            </div>
          </div>

          <div className="flex items-center space-x-2">
            {/* Theme Toggle */}
            <ThemeToggle />
            
            {/* Mobile Navigation */}
            <div className="md:hidden">
              <Sheet>
                <SheetTrigger asChild>
                  <Button variant="ghost" size="sm">
                    <Menu className="h-5 w-5" />
                    <span className="sr-only">Toggle navigation menu</span>
                  </Button>
                </SheetTrigger>
                <SheetContent side="right" className="w-64">
                  <div className="flex flex-col space-y-2 mt-6">
                    <NavItems />
                  </div>
                </SheetContent>
              </Sheet>
            </div>
          </div>
        </div>
      </div>
    </nav>
  )
}