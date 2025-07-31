import { http, HttpResponse } from 'msw'

// Mock API handlers for testing
export const handlers = [
  // Dataset endpoints
  http.post('/api/datasets/upload', () => {
    return HttpResponse.json({
      id: 'dataset-123',
      name: 'test_dataset.csv',
      status: 'processed',
      rows: 100,
      columns: ['input', 'output', 'category'],
      created_at: '2024-01-01T00:00:00Z',
    })
  }),

  http.get('/api/datasets/:id', ({ params }) => {
    return HttpResponse.json({
      id: params.id,
      name: 'test_dataset.csv',
      format: 'csv',
      rows: 100,
      columns: ['input', 'output', 'category'],
      created_at: '2024-01-01T00:00:00Z',
    })
  }),

  http.get('/api/datasets/:id/preview', ({ params, request }) => {
    const url = new URL(request.url)
    const limit = parseInt(url.searchParams.get('limit') || '10')
    const offset = parseInt(url.searchParams.get('offset') || '0')

    return HttpResponse.json({
      rows: [
        { input: 'What is the capital of France?', output: 'Paris', category: 'geography' },
        { input: 'What is 2+2?', output: '4', category: 'math' },
      ].slice(offset, offset + limit),
      total_rows: 100,
      columns: ['input', 'output', 'category'],
      limit,
      offset,
    })
  }),

  http.get('/api/datasets', () => {
    return HttpResponse.json([
      { id: 'dataset-1', name: 'Dataset 1', created_at: '2024-01-01T00:00:00Z' },
      { id: 'dataset-2', name: 'Dataset 2', created_at: '2024-01-02T00:00:00Z' },
    ])
  }),

  http.delete('/api/datasets/:id', () => {
    return HttpResponse.json({ message: 'Dataset deleted successfully' })
  }),

  // Prompt endpoints
  http.post('/api/prompts', () => {
    return HttpResponse.json({
      id: 'prompt-123',
      name: 'Test Prompt',
      system_prompt: 'You are a helpful assistant.',
      user_prompt: 'Answer: {{input}}',
      variables: ['input'],
      created_at: '2024-01-01T00:00:00Z',
    })
  }),

  http.get('/api/prompts/:id', ({ params }) => {
    return HttpResponse.json({
      id: params.id,
      name: 'Test Prompt',
      system_prompt: 'You are a helpful assistant.',
      user_prompt: 'Answer: {{input}}',
      variables: ['input'],
      created_at: '2024-01-01T00:00:00Z',
    })
  }),

  http.put('/api/prompts/:id', ({ params }) => {
    return HttpResponse.json({
      id: params.id,
      name: 'Updated Test Prompt',
      system_prompt: 'You are a helpful assistant.',
      user_prompt: 'Answer: {{input}}',
      variables: ['input'],
      updated_at: '2024-01-01T01:00:00Z',
    })
  }),

  http.post('/api/prompts/:id/preview', () => {
    return HttpResponse.json({
      rendered_system: 'You are a helpful assistant.',
      rendered_user: 'Answer: What is the capital of France?',
      variables_used: { input: 'What is the capital of France?' },
    })
  }),

  http.get('/api/prompts', () => {
    return HttpResponse.json([
      { id: 'prompt-1', name: 'Prompt 1', created_at: '2024-01-01T00:00:00Z' },
      { id: 'prompt-2', name: 'Prompt 2', created_at: '2024-01-02T00:00:00Z' },
    ])
  }),

  // Optimization endpoints
  http.post('/api/optimize/start', () => {
    return HttpResponse.json({
      id: 'task-123',
      status: 'queued',
      progress: 0.0,
      created_at: '2024-01-01T00:00:00Z',
    })
  }),

  http.get('/api/optimize/:taskId/status', ({ params }) => {
    return HttpResponse.json({
      id: params.taskId,
      status: 'running',
      progress: 0.6,
      current_step: 'Running iteration 3/5',
      estimated_completion: '2024-01-01T01:00:00Z',
    })
  }),

  http.get('/api/optimize/:taskId/results', ({ params }) => {
    return HttpResponse.json({
      task_id: params.taskId,
      status: 'completed',
      original_prompt: {
        system_prompt: 'You are a helpful assistant.',
        user_prompt: 'Answer: {{input}}',
      },
      optimized_prompt: {
        system_prompt: 'You are an expert assistant with comprehensive knowledge.',
        user_prompt: 'Provide a detailed answer to: {{input}}',
      },
      metrics: {
        original_accuracy: 0.75,
        optimized_accuracy: 0.92,
        improvement: 0.17,
      },
      individual_results: [
        {
          input: 'What is the capital of France?',
          expected: 'Paris',
          original_output: 'Paris',
          optimized_output: 'Paris',
          original_score: 1.0,
          optimized_score: 1.0,
        },
      ],
    })
  }),

  http.post('/api/optimize/:taskId/cancel', () => {
    return HttpResponse.json({ message: 'Optimization cancelled successfully' })
  }),

  http.get('/api/optimize/history', () => {
    return HttpResponse.json([
      { id: 'task-1', status: 'completed', created_at: '2024-01-01T00:00:00Z' },
      { id: 'task-2', status: 'running', created_at: '2024-01-02T00:00:00Z' },
    ])
  }),

  // Annotation endpoints
  http.post('/api/rubrics/generate', () => {
    return HttpResponse.json({
      id: 'rubric-123',
      name: 'Generated Rubric',
      dimensions: [
        {
          name: 'Accuracy',
          description: 'How accurate is the response?',
          scale: [1, 2, 3, 4, 5],
          criteria: {
            1: 'Completely inaccurate',
            3: 'Partially accurate',
            5: 'Completely accurate',
          },
        },
      ],
      created_at: '2024-01-01T00:00:00Z',
    })
  }),

  http.post('/api/annotations', () => {
    return HttpResponse.json({
      id: 'annotation-123',
      task_id: 'task-123',
      annotator_id: 'user-123',
      scores: { accuracy: 4, completeness: 5 },
      comments: 'Good response overall',
      created_at: '2024-01-01T00:00:00Z',
    })
  }),

  http.get('/api/annotations/tasks/:annotatorId', () => {
    return HttpResponse.json([
      {
        id: 'annotation-task-1',
        optimization_task_id: 'task-123',
        status: 'pending',
        results_to_annotate: [
          { input: 'test1', output: 'result1' },
          { input: 'test2', output: 'result2' },
        ],
      },
    ])
  }),

  // Error handlers for testing error states
  http.get('/api/error/500', () => {
    return new HttpResponse(null, { status: 500 })
  }),

  http.get('/api/error/404', () => {
    return new HttpResponse(null, { status: 404 })
  }),
]