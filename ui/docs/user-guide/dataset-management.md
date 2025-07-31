# Dataset Management

Learn how to upload, manage, and work with datasets in the Nova Prompt Optimizer Frontend.

## Supported Formats

### CSV Files
- **Requirements**: Must have header row with column names
- **Encoding**: UTF-8 recommended
- **Size Limit**: 100MB maximum
- **Example Structure**:
```csv
input,output,category
"What is the capital of France?","Paris","geography"
"Solve: 2 + 2","4","math"
```

### JSON Files
- **Format**: JSON Lines (.jsonl) or standard JSON array
- **Structure**: Each record should be an object with consistent keys
- **Example JSONL**:
```json
{"input": "What is the capital of France?", "output": "Paris", "category": "geography"}
{"input": "Solve: 2 + 2", "output": "4", "category": "math"}
```

- **Example JSON Array**:
```json
[
  {"input": "What is the capital of France?", "output": "Paris", "category": "geography"},
  {"input": "Solve: 2 + 2", "output": "4", "category": "math"}
]
```

## Uploading a Dataset

### Step 1: Access Dataset Management
1. Click **Dataset Management** in the navigation bar
2. You'll see a list of existing datasets (if any)
3. Click **Upload New Dataset** to begin

### Step 2: File Upload
1. **Drag and Drop**: Drag your file into the upload area
2. **Browse**: Click the upload area to open file browser
3. **Validation**: The system will validate file format and size
4. **Preview**: See the first few rows of your data

### Step 3: Column Mapping
1. **Input Columns**: Select which columns contain the input data
   - These are the prompts or questions you want to optimize
   - You can select multiple columns (they'll be combined)
2. **Output Columns**: Select which columns contain the expected outputs
   - These are the correct answers or desired responses
   - Multiple output columns will be treated as alternatives

### Step 4: Configuration
1. **Dataset Name**: Enter a descriptive name
2. **Description**: Add optional description for future reference
3. **Train/Test Split**: Choose the ratio (default: 80/20)
   - Training data is used for optimization
   - Test data is used for final evaluation

### Step 5: Processing
1. Click **Process Dataset**
2. Wait for validation and processing to complete
3. Review the dataset summary
4. Click **Save** to add to your dataset library

## Managing Datasets

### Dataset List View
- **Name and Description**: Identify your datasets
- **Statistics**: Row count, column information, upload date
- **Status**: Processing status and any errors
- **Actions**: Preview, edit, duplicate, delete

### Dataset Preview
1. Click **Preview** on any dataset
2. View paginated data with search and filtering
3. See column statistics and data types
4. Check for data quality issues

### Dataset Actions

#### Edit Dataset
- Modify name and description
- Update column mappings
- Adjust train/test split
- Re-process if needed

#### Duplicate Dataset
- Create a copy with different settings
- Useful for testing different configurations
- Maintains original data while allowing modifications

#### Delete Dataset
- Permanently removes dataset and associated files
- Cannot be undone
- Will affect any optimizations using this dataset

## Data Quality Guidelines

### Best Practices

#### Data Consistency
- **Uniform Format**: Keep input/output formats consistent
- **Complete Records**: Avoid missing or empty values
- **Balanced Distribution**: Include diverse examples across your use case

#### Input Quality
- **Clear Questions**: Inputs should be well-formed and specific
- **Appropriate Length**: Not too short (ambiguous) or too long (overwhelming)
- **Representative**: Cover the full range of expected use cases

#### Output Quality
- **Correct Answers**: Ensure outputs are accurate and appropriate
- **Consistent Style**: Maintain consistent tone and format
- **Complete Responses**: Outputs should be complete, not truncated

### Common Issues and Solutions

#### Inconsistent Column Names
**Problem**: Column names vary between files or contain special characters
**Solution**: 
- Standardize column names before upload
- Use simple names like "input", "output", "category"
- Avoid spaces, special characters, or very long names

#### Mixed Data Types
**Problem**: Columns contain mixed data types (numbers and text)
**Solution**:
- Convert all data to strings before upload
- Ensure consistent formatting within columns
- Use separate columns for different data types

#### Duplicate Records
**Problem**: Same input appears multiple times with different outputs
**Solution**:
- Remove exact duplicates before upload
- For legitimate variations, ensure outputs are consistent
- Consider using multiple output columns for valid alternatives

#### Insufficient Data
**Problem**: Too few examples for meaningful optimization
**Solution**:
- Aim for at least 50-100 examples
- Include diverse examples across your domain
- Consider data augmentation techniques

## Advanced Features

### Column Statistics
- **Data Types**: Automatic detection of text, numeric, categorical data
- **Value Distributions**: See most common values and patterns
- **Quality Metrics**: Missing values, duplicates, outliers

### Data Validation
- **Format Checking**: Ensures data meets requirements
- **Consistency Validation**: Checks for inconsistent patterns
- **Quality Scoring**: Overall data quality assessment

### Batch Operations
- **Multiple Uploads**: Upload several datasets at once
- **Bulk Actions**: Apply operations to multiple datasets
- **Export/Import**: Share datasets between environments

## Integration with Optimization

### Dataset Selection
- Choose appropriate datasets for your optimization goals
- Consider data size vs. optimization time trade-offs
- Use representative samples for faster iterations

### Train/Test Splits
- **Training Data**: Used by optimizers to improve prompts
- **Test Data**: Used for unbiased evaluation of results
- **Validation**: Some optimizers use additional validation splits

### Performance Considerations
- **Large Datasets**: May require longer processing times
- **Memory Usage**: Very large datasets may need special handling
- **Optimization Speed**: More data generally means better results but longer optimization

## Troubleshooting

### Upload Failures
1. **Check File Format**: Ensure CSV or JSON format
2. **Verify Size**: Must be under 100MB limit
3. **Encoding Issues**: Try UTF-8 encoding
4. **Network Problems**: Check internet connection

### Processing Errors
1. **Column Mapping**: Verify input/output columns are correct
2. **Data Format**: Check for malformed JSON or CSV
3. **Missing Values**: Handle empty cells appropriately
4. **Special Characters**: May cause parsing issues

### Performance Issues
1. **Large Files**: Consider splitting into smaller chunks
2. **Complex Data**: Simplify data structure if possible
3. **Browser Memory**: Try refreshing page or using different browser
4. **Server Load**: Wait and retry during off-peak hours

For more help, see the [Troubleshooting Guide](./troubleshooting.md).