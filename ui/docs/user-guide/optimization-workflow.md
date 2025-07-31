# Optimization Workflow

Learn how to configure and run prompt optimizations to improve your model's performance.

## Understanding Optimization

### What is Prompt Optimization?
Prompt optimization is the process of automatically improving your prompts to achieve better performance on your specific task. The system uses various algorithms to refine your prompts based on your dataset and evaluation metrics.

### How It Works
1. **Baseline Evaluation**: Your original prompt is tested on your dataset
2. **Iterative Improvement**: The optimizer generates variations of your prompt
3. **Performance Testing**: Each variation is evaluated using your metrics
4. **Selection**: The best-performing variations are kept and refined further
5. **Final Result**: You get an optimized prompt that performs better than the original

## Available Optimizers

### Nova Prompt Optimizer (Recommended)
- **Best For**: General-purpose optimization, beginners
- **Approach**: Combines meta-prompting with MIPROv2 techniques
- **Strengths**: Balanced performance, good for most use cases
- **Time**: Moderate (10-30 minutes for typical datasets)

### MIPROv2
- **Best For**: Advanced users, research applications
- **Approach**: Multi-step instruction, proposition, and reasoning optimization
- **Strengths**: Excellent for complex reasoning tasks
- **Time**: Longer (30-60 minutes for typical datasets)

### Nova Meta Prompter
- **Best For**: Simple classification and generation tasks
- **Approach**: Meta-prompting with automatic instruction generation
- **Strengths**: Fast, good for straightforward tasks
- **Time**: Fast (5-15 minutes for typical datasets)

## Running an Optimization

### Step 1: Access Optimization Workflow
1. Navigate to **Optimization Workflow** in the main navigation
2. You'll see the optimization configuration interface
3. Ensure you have a dataset and prompt ready

### Step 2: Select Components

#### Dataset Selection
1. Choose from your uploaded datasets
2. Review dataset statistics (size, columns, split ratio)
3. Consider dataset size vs. optimization time trade-offs

#### Prompt Selection
1. Select from your prompt library
2. Preview the prompt to ensure it's correct
3. Verify all variables match your dataset columns

#### Metric Selection
1. Choose evaluation metrics (built-in or custom)
2. Select primary metric for optimization guidance
3. Add secondary metrics for comprehensive evaluation

### Step 3: Configure Optimizer

#### Optimizer Type
1. Select your preferred optimizer
2. Review the description and recommended use cases
3. Consider your time constraints and performance needs

#### Model Selection
1. **Nova Pro**: Best performance, higher cost
2. **Nova Lite**: Faster, lower cost, good for testing
3. **Claude 3**: Alternative model for comparison

#### Advanced Parameters
- **Max Iterations**: Number of optimization rounds (default: 10)
- **Population Size**: Number of prompt variations per iteration
- **Temperature**: Creativity level for prompt generation
- **Evaluation Budget**: Maximum number of model calls

### Step 4: Review Configuration
1. Check the configuration summary
2. Verify all selections are correct
3. Review estimated time and cost
4. Make any final adjustments

### Step 5: Start Optimization
1. Click **Start Optimization**
2. The system creates a background task
3. You'll see the progress tracking interface
4. Optimization begins immediately

## Monitoring Progress

### Real-Time Updates
- **Progress Bar**: Shows completion percentage
- **Current Step**: Displays what the optimizer is currently doing
- **Time Estimates**: Shows elapsed time and estimated completion
- **Live Metrics**: Updates performance metrics as they're calculated

### Progress Stages
1. **Initialization**: Setting up the optimization environment
2. **Baseline Evaluation**: Testing your original prompt
3. **Generation**: Creating prompt variations
4. **Evaluation**: Testing variations on your dataset
5. **Selection**: Choosing best-performing variations
6. **Refinement**: Improving selected variations
7. **Final Evaluation**: Testing the optimized prompt

### Control Options
- **Pause**: Temporarily stop optimization (resume later)
- **Cancel**: Stop optimization permanently
- **View Logs**: See detailed progress information

## Understanding Results

### Performance Comparison
- **Before/After Metrics**: Side-by-side comparison of original vs. optimized
- **Improvement Percentage**: Quantified improvement for each metric
- **Statistical Significance**: Whether improvements are meaningful

### Detailed Analysis
- **Individual Predictions**: See how specific examples improved
- **Error Analysis**: Understand what types of errors were fixed
- **Performance Breakdown**: Metrics by category or data subset

### Optimized Prompt
- **Final Prompt**: The best-performing prompt found
- **Changes Made**: Highlights of what was modified
- **Usage Instructions**: How to implement the optimized prompt

## Advanced Configuration

### Custom Optimization Settings

#### Iteration Control
```
Max Iterations: 20          # More iterations = better results, longer time
Early Stopping: Enabled     # Stop if no improvement for N iterations
Patience: 3                 # Number of iterations to wait before stopping
```

#### Population Management
```
Population Size: 10         # Number of variations per iteration
Selection Pressure: 0.5     # How aggressively to select best performers
Mutation Rate: 0.3          # How much to change prompts between iterations
```

#### Evaluation Strategy
```
Evaluation Split: 0.8       # Fraction of data for optimization vs. validation
Cross Validation: 3-fold    # Use cross-validation for robust evaluation
Bootstrap Samples: 100      # Number of bootstrap samples for confidence intervals
```

### Multi-Objective Optimization
When using multiple metrics, you can configure how they're combined:

#### Weighted Combination
```
Primary Metric: Accuracy (weight: 0.6)
Secondary Metric: F1-Score (weight: 0.3)
Tertiary Metric: Response Length (weight: 0.1)
```

#### Pareto Optimization
- Find prompts that are optimal across multiple metrics
- Explore trade-offs between different objectives
- Get multiple candidate prompts for different use cases

### Constraint-Based Optimization
Set constraints on the optimization process:

#### Prompt Length Constraints
```
Max System Prompt Length: 500 tokens
Max User Prompt Length: 200 tokens
Preserve Original Structure: Yes
```

#### Content Constraints
```
Required Keywords: ["please", "thank you"]
Forbidden Words: ["urgent", "immediately"]
Tone Requirements: Professional, Helpful
```

## Optimization Strategies

### For Different Use Cases

#### Classification Tasks
- Use accuracy and F1-score as primary metrics
- Include class-specific metrics for imbalanced data
- Consider precision vs. recall trade-offs

#### Generation Tasks
- Use BLEU, ROUGE, or custom quality metrics
- Balance creativity with accuracy
- Consider length and style constraints

#### Question Answering
- Use exact match and semantic similarity metrics
- Include coverage and completeness measures
- Consider response time if relevant

### Iterative Improvement

#### Multi-Round Optimization
1. **Round 1**: Basic optimization with default settings
2. **Analysis**: Identify remaining issues and opportunities
3. **Round 2**: Targeted optimization with refined metrics
4. **Validation**: Test on held-out data or new examples

#### A/B Testing
1. Run multiple optimizations with different configurations
2. Compare results across different approaches
3. Select the best overall strategy
4. Validate with real-world testing

## Best Practices

### Before Optimization

#### Data Preparation
- Ensure high-quality, representative training data
- Remove duplicates and inconsistencies
- Balance classes if doing classification
- Reserve held-out test data for final validation

#### Baseline Establishment
- Test your original prompt manually
- Understand current performance levels
- Identify specific areas for improvement
- Set realistic improvement targets

#### Metric Selection
- Choose metrics that align with business goals
- Include both primary and secondary metrics
- Consider metric stability and interpretability
- Test metrics on sample data first

### During Optimization

#### Monitoring
- Check progress regularly but don't micromanage
- Look for signs of overfitting or instability
- Monitor resource usage and costs
- Be prepared to stop if issues arise

#### Patience
- Allow sufficient time for meaningful optimization
- Don't stop too early unless there are clear issues
- Consider running overnight for complex optimizations
- Plan for longer times with larger datasets

### After Optimization

#### Validation
- Test optimized prompts on held-out data
- Compare with human evaluation when possible
- Validate on real-world examples
- Check for edge cases and failure modes

#### Implementation
- Gradually roll out optimized prompts
- Monitor performance in production
- Keep original prompts as fallback
- Document changes and rationale

## Troubleshooting

### Common Issues

#### Optimization Doesn't Improve Performance
**Possible Causes:**
- Original prompt is already well-optimized
- Dataset is too small or low quality
- Metrics don't capture what you care about
- Optimizer settings are too conservative

**Solutions:**
- Try different optimizers or settings
- Increase iteration count or population size
- Review and improve your dataset
- Consider different or additional metrics

#### Optimization Takes Too Long
**Possible Causes:**
- Dataset is very large
- Too many iterations configured
- Complex metrics or model calls
- Resource constraints

**Solutions:**
- Use a smaller sample for initial testing
- Reduce iteration count or population size
- Optimize metric computation
- Try faster models (Nova Lite vs. Nova Pro)

#### Results Are Inconsistent
**Possible Causes:**
- High variance in dataset or metrics
- Insufficient evaluation data
- Unstable optimization algorithm
- Random seed effects

**Solutions:**
- Use cross-validation for more stable results
- Increase evaluation data size
- Run multiple optimizations and average results
- Set random seeds for reproducibility

#### Optimized Prompt Doesn't Work in Production
**Possible Causes:**
- Training/production data mismatch
- Overfitting to training data
- Different model or API version
- Context or environment differences

**Solutions:**
- Validate on production-like data
- Use held-out test data for final validation
- Test with current model versions
- Consider domain adaptation techniques

### Getting Help

#### Log Analysis
- Review optimization logs for error messages
- Check for warnings about data quality
- Look for convergence patterns
- Identify bottlenecks or failures

#### Support Resources
- Check the [Troubleshooting Guide](./troubleshooting.md)
- Review example optimizations in the documentation
- Contact your system administrator
- Join user forums or communities

For more detailed troubleshooting, see the [Troubleshooting Guide](./troubleshooting.md).