import React from 'react'

export const AnnotationWorkspace: React.FC = () => {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold">Annotation Workspace</h1>
        <p className="text-muted-foreground">
          Human annotation and quality assessment
        </p>
      </div>
      
      <div className="p-8 border-2 border-dashed rounded-lg text-center">
        <p className="text-muted-foreground">
          Annotation interface will be implemented here
        </p>
      </div>
    </div>
  )
}