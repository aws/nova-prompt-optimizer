import React, { useState } from 'react'
import { OptimizationConfig } from '@/components/optimization'
import { useDataset, usePrompt, useOptimization } from '@/hooks'
import { OptimizationConfig as OptimizationConfigType } from '@/types'
import { useToast } from '@/hooks/use-toast'

export const OptimizationWorkflow: React.FC = () => {
  const { datasets } = useDataset()
  const { prompts } = usePrompt()
  const { startOptimization } = useOptimization()
  const { toast } = useToast()
  
  const [selectedDataset] = useState(datasets.data?.items?.[0])
  const [selectedPrompt] = useState(prompts.data?.items?.[0])
  const [isStarting, setIsStarting] = useState(false)

  const handleStartOptimization = async (config: OptimizationConfigType) => {
    setIsStarting(true)
    
    try {
      const task = await startOptimization(config)
      
      toast({
        title: "Optimization Started",
        description: `Task ${task.id} has been started successfully.`,
      })
      
      // TODO: Navigate to optimization progress view
      console.log('Optimization task started:', task)
      
    } catch (error) {
      console.error('Failed to start optimization:', error)
      
      toast({
        title: "Failed to Start Optimization",
        description: error instanceof Error ? error.message : "An unexpected error occurred.",
        variant: "destructive",
      })
    } finally {
      setIsStarting(false)
    }
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold">Optimization Workflow</h1>
        <p className="text-muted-foreground">
          Configure and run prompt optimization experiments
        </p>
      </div>
      
      <OptimizationConfig
        dataset={selectedDataset}
        prompt={selectedPrompt}
        onStart={handleStartOptimization}
        disabled={isStarting}
      />
    </div>
  )
}