import React from 'react'
import { Label } from '@/components/ui/label'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Card, CardContent } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Zap, Brain, Target } from 'lucide-react'
import { OptimizerType } from '@/types'

interface OptimizerSelectorProps {
  value?: OptimizerType
  optimizers?: Record<OptimizerType, any>
  onChange: (optimizer: OptimizerType) => void
  disabled?: boolean
}

const OPTIMIZER_INFO = {
  nova: {
    name: 'Nova Prompt Optimizer',
    description: 'Advanced meta-prompting with MIPROv2 integration',
    icon: Zap,
    features: ['Meta-prompting', 'Few-shot optimization', 'Automatic evaluation'],
    recommended: true
  },
  miprov2: {
    name: 'MIPROv2',
    description: 'Multi-step instruction prompt optimization',
    icon: Brain,
    features: ['Multi-step reasoning', 'Instruction optimization', 'Performance tracking'],
    recommended: false
  },
  'meta-prompter': {
    name: 'Meta Prompter',
    description: 'Automated prompt engineering with meta-learning',
    icon: Target,
    features: ['Meta-learning', 'Automated engineering', 'Context optimization'],
    recommended: false
  }
}

export const OptimizerSelector: React.FC<OptimizerSelectorProps> = ({
  value,
  optimizers,
  onChange,
  disabled = false
}) => {
  const handleChange = (newValue: string) => {
    onChange(newValue as OptimizerType)
  }

  return (
    <div className="space-y-3">
      <Label htmlFor="optimizer-select">Optimizer Type</Label>
      
      <Select
        value={value}
        onValueChange={handleChange}
        disabled={disabled}
      >
        <SelectTrigger id="optimizer-select">
          <SelectValue placeholder="Select an optimizer" />
        </SelectTrigger>
        <SelectContent>
          {Object.entries(OPTIMIZER_INFO).map(([key, info]) => (
            <SelectItem key={key} value={key}>
              <div className="flex items-center gap-2">
                <info.icon className="h-4 w-4" />
                <span>{info.name}</span>
                {info.recommended && (
                  <Badge variant="secondary" className="text-xs">
                    Recommended
                  </Badge>
                )}
              </div>
            </SelectItem>
          ))}
        </SelectContent>
      </Select>

      {/* Optimizer Details */}
      {value && (
        <Card className="border-muted">
          <CardContent className="pt-4">
            <div className="space-y-3">
              <div className="flex items-start gap-3">
                {React.createElement(OPTIMIZER_INFO[value].icon, {
                  className: "h-5 w-5 mt-0.5 text-primary"
                })}
                <div className="flex-1 space-y-1">
                  <div className="flex items-center gap-2">
                    <h4 className="font-medium">{OPTIMIZER_INFO[value].name}</h4>
                    {OPTIMIZER_INFO[value].recommended && (
                      <Badge variant="secondary" className="text-xs">
                        Recommended
                      </Badge>
                    )}
                  </div>
                  <p className="text-sm text-muted-foreground">
                    {OPTIMIZER_INFO[value].description}
                  </p>
                </div>
              </div>

              <div className="space-y-2">
                <h5 className="text-sm font-medium">Key Features:</h5>
                <div className="flex flex-wrap gap-1">
                  {OPTIMIZER_INFO[value].features.map((feature, index) => (
                    <Badge key={index} variant="outline" className="text-xs">
                      {feature}
                    </Badge>
                  ))}
                </div>
              </div>

              {/* Show optimizer-specific configuration if available */}
              {optimizers?.[value] && (
                <div className="space-y-2">
                  <h5 className="text-sm font-medium">Configuration:</h5>
                  <div className="text-xs text-muted-foreground space-y-1">
                    {optimizers[value].description && (
                      <p>{optimizers[value].description}</p>
                    )}
                    {optimizers[value].parameters && (
                      <p>
                        Parameters: {Object.keys(optimizers[value].parameters).join(', ')}
                      </p>
                    )}
                  </div>
                </div>
              )}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  )
}