import React from 'react'

export const Dashboard: React.FC = () => {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold">Dashboard</h1>
        <p className="text-muted-foreground">
          Welcome to Nova Prompt Optimizer
        </p>
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <div className="p-6 border rounded-lg">
          <h3 className="text-lg font-semibold mb-2">Datasets</h3>
          <p className="text-sm text-muted-foreground">
            Upload and manage your datasets
          </p>
        </div>
        
        <div className="p-6 border rounded-lg">
          <h3 className="text-lg font-semibold mb-2">Prompts</h3>
          <p className="text-sm text-muted-foreground">
            Create and edit prompts
          </p>
        </div>
        
        <div className="p-6 border rounded-lg">
          <h3 className="text-lg font-semibold mb-2">Optimization</h3>
          <p className="text-sm text-muted-foreground">
            Run prompt optimization
          </p>
        </div>
      </div>
    </div>
  )
}