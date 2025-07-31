# Prompt Creation and Editing

Learn how to create, edit, and manage prompts using the Prompt Workbench.

## Understanding Prompts

### System vs User Prompts

#### System Prompt
- **Purpose**: Sets the overall context and behavior for the AI model
- **Content**: Instructions, role definitions, general guidelines
- **Example**: "You are a helpful assistant that provides accurate and concise answers."
- **Optional**: Can be left empty for simple use cases

#### User Prompt
- **Purpose**: Contains the specific question or task for each interaction
- **Content**: The actual input that varies between examples
- **Variables**: Uses template variables like `{{input}}` for dynamic content
- **Required**: Must be provided for optimization

### Template Variables

Variables allow you to create dynamic prompts that work with your dataset:
- **Syntax**: Use double curly braces `{{variable_name}}`
- **Naming**: Use descriptive names like `{{question}}`, `{{context}}`
- **Dataset Mapping**: Variables must match column names in your dataset

## Creating a New Prompt

### Step 1: Access Prompt Workbench
1. Navigate to **Prompt Workbench** in the main navigation
2. Click **New Prompt** to start creating
3. You'll see the prompt editor interface

### Step 2: Basic Information
1. **Prompt Name**: Enter a descriptive name
   - Use clear, specific names like "Customer Support Classifier"
   - Avoid generic names like "Prompt 1"
2. **Description**: Add optional description for future reference
3. **Tags**: Add tags for organization (optional)

### Step 3: System Prompt (Optional)
1. Click the **System Prompt** tab
2. Enter instructions that apply to all interactions
3. Examples of good system prompts:
   ```
   You are an expert customer service representative. 
   Analyze customer inquiries and classify them into categories.
   Always be helpful and professional in your responses.
   ```

### Step 4: User Prompt (Required)
1. Click the **User Prompt** tab
2. Create your template with variables
3. Example user prompt:
   ```
   Please classify the following customer inquiry:
   
   Customer Message: {{message}}
   
   Classify into one of these categories:
   - Technical Support
   - Billing Question
   - Product Information
   - Complaint
   - Other
   
   Category:
   ```

### Step 5: Variable Detection
- The system automatically detects variables in your prompts
- Variables appear as badges below the editor
- Ensure all variables match your dataset columns

### Step 6: Preview and Test
1. Click **Preview** to see how your prompt renders
2. Select sample data from your dataset
3. Review the rendered output
4. Make adjustments as needed

### Step 7: Save
1. Click **Save Prompt** when satisfied
2. Your prompt is added to the prompt library
3. It's now available for optimization

## Editing Existing Prompts

### Opening for Edit
1. Go to **Prompt Workbench**
2. Find your prompt in the library
3. Click **Edit** or double-click the prompt card

### Version Management
- Each save creates a new version
- Previous versions are preserved
- You can revert to earlier versions if needed

### Making Changes
1. Modify system or user prompts as needed
2. Add or remove variables
3. Update descriptions or tags
4. Preview changes before saving

## Prompt Library Management

### Organizing Prompts
- **Search**: Find prompts by name or description
- **Filter**: Filter by tags, creation date, or usage
- **Sort**: Sort by name, date, or performance

### Prompt Actions

#### Duplicate Prompt
- Creates a copy with "(Copy)" suffix
- Useful for creating variations
- Maintains original while allowing experimentation

#### Export Prompt
- Download prompt as JSON file
- Share with team members
- Backup important prompts

#### Import Prompt
- Upload previously exported prompts
- Restore from backups
- Share prompts between environments

#### Delete Prompt
- Permanently removes prompt
- Cannot be undone
- Will affect any optimizations using this prompt

## Best Practices

### Writing Effective Prompts

#### Be Specific and Clear
```
❌ Bad: "Analyze this: {{input}}"
✅ Good: "Analyze the sentiment of this customer review and classify it as positive, negative, or neutral: {{review}}"
```

#### Provide Context
```
❌ Bad: "{{question}}"
✅ Good: "You are a medical expert. Answer this patient question accurately and compassionately: {{question}}"
```

#### Use Examples (Few-Shot Learning)
```
✅ Good:
Here are some examples:
Input: "Great product, fast shipping!"
Output: Positive

Input: "Terrible quality, waste of money"
Output: Negative

Now classify: {{review}}
```

#### Structure Your Output
```
✅ Good:
Analyze the following text: {{text}}

Provide your analysis in this format:
- Main Topic: [topic]
- Sentiment: [positive/negative/neutral]
- Confidence: [high/medium/low]
- Reasoning: [brief explanation]
```

### Variable Best Practices

#### Use Descriptive Names
```
❌ Bad: {{input}}, {{data}}, {{x}}
✅ Good: {{customer_message}}, {{product_description}}, {{user_question}}
```

#### Match Dataset Columns
- Ensure variable names exactly match your dataset column names
- Case-sensitive matching
- Use underscores instead of spaces

#### Handle Missing Data
- Consider what happens if a variable is empty
- Provide fallback instructions
- Test with incomplete data

### Common Patterns

#### Classification Tasks
```
Classify the following {{item_type}} into one of these categories:
{{categories}}

{{item_type}}: {{input}}

Category:
```

#### Question Answering
```
Answer the following question based on the provided context.
If the answer cannot be found in the context, say "I don't know."

Context: {{context}}
Question: {{question}}

Answer:
```

#### Content Generation
```
Generate a {{content_type}} with the following requirements:
- Topic: {{topic}}
- Tone: {{tone}}
- Length: {{length}}

Content:
```

#### Summarization
```
Summarize the following {{content_type}} in {{max_words}} words or less.
Focus on the main points and key takeaways.

{{content_type}}: {{input_text}}

Summary:
```

## Advanced Features

### Conditional Logic
While not directly supported in templates, you can use prompts to handle conditions:
```
If the {{input_type}} is a question, provide a direct answer.
If it's a statement, provide relevant information or ask for clarification.

Input: {{input}}
```

### Multi-Step Reasoning
Structure prompts to encourage step-by-step thinking:
```
Solve this problem step by step:

Problem: {{problem}}

Step 1: Understand the problem
Step 2: Identify relevant information
Step 3: Apply appropriate method
Step 4: Calculate the result
Step 5: Verify the answer

Solution:
```

### Error Handling
Include instructions for edge cases:
```
Analyze the sentiment of: {{text}}

If the text is unclear or ambiguous, respond with "Neutral" and explain why.
If the text contains mixed sentiments, identify the dominant sentiment.

Sentiment:
```

## Testing and Validation

### Preview Testing
1. Always preview prompts with real data
2. Test with edge cases and unusual inputs
3. Verify variable substitution works correctly

### A/B Testing
1. Create multiple versions of similar prompts
2. Run optimizations on each version
3. Compare results to find the best approach

### Iterative Improvement
1. Start with a basic prompt
2. Run optimization to see results
3. Analyze what works and what doesn't
4. Refine and test again

## Integration with Optimization

### Prompt Selection
- Choose prompts that align with your optimization goals
- Consider the complexity vs. performance trade-off
- Test prompts manually before optimization

### Variable Mapping
- Ensure all prompt variables exist in your dataset
- Check for typos in variable names
- Verify data types match expectations

### Optimization Compatibility
- Some optimizers work better with certain prompt styles
- Consider the target model's capabilities
- Test with different optimizers for best results

## Troubleshooting

### Variable Issues
1. **Variables Not Detected**: Check syntax `{{variable}}`
2. **Missing Variables**: Ensure variables exist in dataset
3. **Case Sensitivity**: Variable names must match exactly

### Preview Problems
1. **No Sample Data**: Upload a dataset first
2. **Rendering Errors**: Check for syntax issues
3. **Missing Output**: Verify variable mapping

### Save Failures
1. **Network Issues**: Check internet connection
2. **Validation Errors**: Fix any syntax or format issues
3. **Permission Problems**: Contact system administrator

For more help, see the [Troubleshooting Guide](./troubleshooting.md).