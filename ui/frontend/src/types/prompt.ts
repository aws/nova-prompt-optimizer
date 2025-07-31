import { BaseEntity } from './common'

export interface Prompt extends BaseEntity {
  name: string
  description?: string
  system_prompt: string
  user_prompt: string
  variables: string[]
  version: number
  is_template: boolean
  metadata: Record<string, any>
}

export interface PromptPreview {
  rendered_system_prompt: string
  rendered_user_prompt: string
  variables_used: Record<string, any>
  validation_errors: string[]
}

export interface PromptCreateRequest {
  name: string
  description?: string
  system_prompt: string
  user_prompt: string
}

export interface PromptUpdateRequest extends Partial<PromptCreateRequest> {
  version?: number
}

export interface PromptLibrary {
  prompts: Prompt[]
  categories: string[]
  tags: string[]
}

export interface PromptValidation {
  is_valid: boolean
  errors: string[]
  warnings: string[]
  detected_variables: string[]
}