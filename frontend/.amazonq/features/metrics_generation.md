# 📊 Metric Generation Capabilities by Use Case

The Nova Prompt Optimizer's metric generation system can create custom evaluation metrics for virtually any AI task. Here are the possible metrics organized by use case:

## 🎯 Classification Tasks
- **Accuracy Score** - Overall correctness percentage
- **F1 Score** - Balanced precision and recall
- **Precision/Recall** - Individual component scores
- **Category-wise F1** - Per-category performance
- **Multi-label Accuracy** - For multiple categories
- **Cohen's Kappa** - Inter-rater agreement measure

## 📝 Text Generation & Analysis
- **Semantic Similarity** - Content meaning comparison
- **BLEU Score** - Translation/generation quality
- **Rouge Score** - Summarization quality
- **Sentiment Accuracy** - Emotional tone correctness
- **Readability Score** - Text complexity assessment
- **Length Compliance** - Output length requirements

## 🏷️ Structured Output (JSON/XML)
- **Format Validation** - Correct structure adherence
- **Field Completeness** - All required fields present
- **Schema Compliance** - Matches expected format
- **Nested Structure Accuracy** - Complex object validation
- **Data Type Validation** - Correct field types

## 🔢 Numerical & Quantitative
- **Mean Absolute Error (MAE)** - Average prediction error
- **Root Mean Square Error (RMSE)** - Squared error penalty
- **R-squared** - Variance explanation
- **Percentage Error** - Relative accuracy measure
- **Range Compliance** - Values within bounds

## 🎨 Creative & Subjective
- **Creativity Score** - Novelty and originality
- **Coherence Rating** - Logical flow assessment
- **Style Consistency** - Tone and voice matching
- **Relevance Score** - Topic adherence
- **Engagement Quality** - User interest level

## 🔍 Information Extraction
- **Entity Recognition Accuracy** - Named entity extraction
- **Relationship Extraction** - Connection identification
- **Key Information Recall** - Important detail capture
- **Fact Verification** - Accuracy of extracted facts
- **Completeness Score** - Information coverage

## 💬 Conversational AI
- **Response Appropriateness** - Context-aware replies
- **Helpfulness Rating** - User assistance quality
- **Safety Compliance** - Harmful content avoidance
- **Personality Consistency** - Character maintenance
- **Turn-taking Quality** - Conversation flow

## 🏢 Business-Specific
- **Compliance Score** - Regulatory adherence
- **Brand Voice Alignment** - Company tone matching
- **Customer Satisfaction** - Service quality measure
- **Risk Assessment** - Potential issue identification
- **Process Adherence** - Workflow compliance

## 🔧 Technical Metrics
- **API Response Validation** - Correct format/structure
- **Error Rate** - Failure frequency
- **Latency Compliance** - Speed requirements
- **Resource Usage** - Efficiency measures
- **Scalability Score** - Performance under load

## 🎯 Composite Metrics
The system can combine multiple metrics into sophisticated composite scores:
- **Weighted Averages** - Different importance levels
- **Multi-dimensional Scoring** - Multiple quality aspects
- **Conditional Logic** - Context-dependent evaluation
- **Threshold-based** - Pass/fail with nuanced scoring

## 🤖 AI-Generated Custom Metrics
The system can create entirely new metrics based on:
- **Dataset Analysis** - Automatically inferred from data patterns
- **Natural Language Descriptions** - User-described evaluation criteria
- **Domain-Specific Requirements** - Industry or use-case tailored
- **Hybrid Approaches** - Combining multiple evaluation methods

## 🛠️ Technical Implementation

### Metric Generation Process
1. **Dataset Analysis** - AI analyzes your data structure and patterns
2. **Intent Understanding** - Determines what the prompt is asking for
3. **Code Generation** - Creates executable Python MetricAdapter classes
4. **Validation** - Tests the metric with sample data
5. **Integration** - Ready for use in optimization workflows

### Available Libraries
- **Standard**: json, re, math, typing (built-in)
- **Scientific**: numpy (arrays, statistics, linear algebra)
- **Data**: pandas (dataframes, data manipulation)
- **ML**: sklearn.metrics (F1, precision, recall, kappa, ROC-AUC, etc.)

### Metric Features
- **Robust JSON Parsing** - Handles both direct JSON and markdown code blocks
- **Granular Scoring** - Precise decimal scores (0.0-1.0) with partial credit
- **Error Handling** - Graceful failure with meaningful error information
- **Batch Processing** - Efficient evaluation of multiple samples
- **Component Breakdown** - Detailed scoring for debugging and analysis

**The Nova Prompt Optimizer can generate virtually any evaluation metric by analyzing your specific dataset and requirements!** 🎯
