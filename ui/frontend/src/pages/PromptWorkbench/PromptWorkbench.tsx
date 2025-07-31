import React from 'react'

export const PromptWorkbench: React.FC = () => {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold">Prompt Workbench</h1>
        <p className="text-muted-foreground">
          Create and edit prompts for optimization
        </p>
      </div>
      
      <div className="p-8 border-2 border-dashed rounded-lg text-center">
        <p className="text-muted-foreground">
          Prompt editor interface will be implemented here
        </p>
      </div>
    </div>
  )
}