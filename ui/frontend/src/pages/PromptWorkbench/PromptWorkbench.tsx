import React, { useState } from 'react'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Button } from '@/components/ui/button'
import { Plus, FileText, Library } from 'lucide-react'
import { PromptEditor, PromptLibrary, PromptPreview } from '@/components/prompt'
import { Prompt } from '@/types'

export const PromptWorkbench: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'library' | 'editor' | 'preview'>('library')
  const [selectedPrompt, setSelectedPrompt] = useState<Prompt | null>(null)
  const [editingPrompt, setEditingPrompt] = useState<Prompt | null>(null)

  const handleCreateNew = () => {
    setEditingPrompt(null)
    setActiveTab('editor')
  }

  const handleEditPrompt = (prompt: Prompt) => {
    setEditingPrompt(prompt)
    setActiveTab('editor')
  }

  const handlePreviewPrompt = (prompt: Prompt) => {
    setSelectedPrompt(prompt)
    setActiveTab('preview')
  }

  const handlePromptSaved = (prompt: Prompt) => {
    setSelectedPrompt(prompt)
    setActiveTab('library')
  }

  const handleBackToLibrary = () => {
    setEditingPrompt(null)
    setSelectedPrompt(null)
    setActiveTab('library')
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Prompt Workbench</h1>
          <p className="text-muted-foreground">
            Create, edit, and manage prompts for optimization
          </p>
        </div>
        
        <Button onClick={handleCreateNew} className="flex items-center gap-2">
          <Plus className="h-4 w-4" />
          New Prompt
        </Button>
      </div>

      <Tabs value={activeTab} onValueChange={(value) => setActiveTab(value as any)}>
        <TabsList className="grid w-full grid-cols-3">
          <TabsTrigger value="library" className="flex items-center gap-2">
            <Library className="h-4 w-4" />
            Library
          </TabsTrigger>
          <TabsTrigger value="editor" className="flex items-center gap-2">
            <FileText className="h-4 w-4" />
            Editor
          </TabsTrigger>
          <TabsTrigger value="preview" className="flex items-center gap-2" disabled={!selectedPrompt}>
            <FileText className="h-4 w-4" />
            Preview
          </TabsTrigger>
        </TabsList>

        <TabsContent value="library" className="space-y-4">
          <PromptLibrary
            onSelect={setSelectedPrompt}
            onEdit={handleEditPrompt}
            onPreview={handlePreviewPrompt}
            onCreate={handleCreateNew}
            selectedPrompt={selectedPrompt || undefined}
            showActions={true}
          />
        </TabsContent>

        <TabsContent value="editor" className="space-y-4">
          <PromptEditor
            prompt={editingPrompt || undefined}
            onSave={handlePromptSaved}
            onCancel={handleBackToLibrary}
            mode={editingPrompt ? 'edit' : 'create'}
            showVersioning={true}
          />
        </TabsContent>

        <TabsContent value="preview" className="space-y-4">
          {selectedPrompt ? (
            <PromptPreview
              prompt={selectedPrompt}
              onClose={handleBackToLibrary}
              showTemplateEditor={true}
              autoPreview={true}
            />
          ) : (
            <div className="text-center py-12 text-muted-foreground">
              <FileText className="h-12 w-12 mx-auto mb-4 opacity-50" />
              <p>Select a prompt from the library to preview</p>
            </div>
          )}
        </TabsContent>
      </Tabs>
    </div>
  )
}