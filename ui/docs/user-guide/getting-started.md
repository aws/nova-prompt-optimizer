# Getting Started

This guide will help you get started with the Nova Prompt Optimizer Frontend.

## Accessing the Application

1. Open your web browser and navigate to the application URL
2. The application will load with the main dashboard
3. You'll see a navigation bar with different workflow steps

## Understanding the Interface

### Navigation Bar
The top navigation shows the main workflow steps:
- **Dashboard**: Overview of your projects and recent activity
- **Dataset Management**: Upload and manage your datasets
- **Prompt Workbench**: Create and edit prompts
- **Metric Workbench**: Define custom evaluation metrics
- **Optimization Workflow**: Configure and run optimizations
- **Annotation Workspace**: Human annotation and quality assurance
- **Results Analysis**: View and analyze optimization results

### Theme Toggle
- Click the theme toggle in the top-right corner to switch between light and dark modes
- Your preference will be saved for future sessions

### Status Indicators
- **Green**: Completed steps or successful operations
- **Blue**: Current or in-progress operations
- **Yellow**: Warnings or items requiring attention
- **Red**: Errors or failed operations

## Your First Optimization

Follow these steps to run your first prompt optimization:

### Step 1: Prepare Your Data
Before starting, ensure you have:
- A dataset in CSV or JSON format
- Clear input and output columns
- At least 20-50 examples for meaningful optimization

### Step 2: Upload Dataset
1. Navigate to **Dataset Management**
2. Click **Upload Dataset**
3. Drag and drop your file or click to browse
4. Specify input and output columns
5. Review the preview and click **Process Dataset**

### Step 3: Create a Prompt
1. Go to **Prompt Workbench**
2. Click **New Prompt**
3. Enter a descriptive name
4. Write your system prompt (optional)
5. Write your user prompt with variables like `{{input}}`
6. Preview with sample data
7. Save your prompt

### Step 4: Run Optimization
1. Navigate to **Optimization Workflow**
2. Select your dataset and prompt
3. Choose an optimizer (Nova Prompt Optimizer recommended for beginners)
4. Select a model (Nova Pro for best results)
5. Configure parameters or use defaults
6. Click **Start Optimization**

### Step 5: Monitor Progress
- Watch the real-time progress bar
- View current optimization step
- Check estimated completion time
- Cancel if needed

### Step 6: Review Results
1. Once complete, view the results comparison
2. See before/after performance metrics
3. Review individual prediction improvements
4. Export the optimized prompt

## Tips for Success

### Dataset Quality
- **Clean Data**: Remove duplicates and inconsistent entries
- **Balanced Examples**: Include diverse examples across your use case
- **Clear Labels**: Ensure output labels are consistent and accurate

### Prompt Design
- **Clear Instructions**: Be specific about what you want the model to do
- **Variable Usage**: Use descriptive variable names like `{{question}}` instead of `{{input}}`
- **Context**: Provide necessary context in the system prompt

### Optimization Settings
- **Start Simple**: Use default settings for your first optimization
- **Iterate**: Run multiple optimizations with different configurations
- **Compare**: Use the results analysis to compare different approaches

## Next Steps

Once you've completed your first optimization:
1. Explore [Custom Metrics](./custom-metrics.md) for domain-specific evaluation
2. Learn about [AI Rubric Generation](./ai-rubric-generation.md) for quality assurance
3. Try [Human Annotation](./human-annotation.md) for additional validation
4. Dive deeper into [Results Analysis](./results-analysis.md) for insights

## Common First-Time Issues

### Dataset Upload Fails
- Check file format (CSV or JSON only)
- Ensure file size is under the limit
- Verify column names don't contain special characters

### Prompt Variables Not Detected
- Use double curly braces: `{{variable_name}}`
- Avoid spaces in variable names
- Check for typos in variable references

### Optimization Takes Too Long
- Start with fewer iterations (5-10)
- Use a smaller dataset for testing
- Try Nova Lite model for faster results

### No Improvement in Results
- Check if your baseline prompt is already well-optimized
- Ensure your dataset has room for improvement
- Try different optimizers or parameters

For more detailed troubleshooting, see the [Troubleshooting Guide](./troubleshooting.md).