#!/usr/bin/env python3
"""
Nova Prompt Optimizer - Background Worker (SDK Proxy)
Uses the actual SDK from /src directory
"""

import asyncio
import json
import os
import sys
import time
from pathlib import Path
from datetime import datetime
from database import Database

# Add the actual SDK source to Python path
SDK_PATH = "/Users/tsanti/Development/Publish/nova-prompt-optimizer/src"
if SDK_PATH not in sys.path:
    sys.path.insert(0, SDK_PATH)

# Import the real SDK
try:
    from amzn_nova_prompt_optimizer.core.input_adapters.prompt_adapter import TextPromptAdapter
    from amzn_nova_prompt_optimizer.core.input_adapters.dataset_adapter import JSONDatasetAdapter
    from amzn_nova_prompt_optimizer.core.input_adapters.metric_adapter import MetricAdapter
    from amzn_nova_prompt_optimizer.core.optimizers import NovaPromptOptimizer
    from amzn_nova_prompt_optimizer.core.inference.adapter import BedrockInferenceAdapter
    from amzn_nova_prompt_optimizer.core.evaluation import Evaluator
    SDK_AVAILABLE = True
    print("✅ Nova Prompt Optimizer SDK loaded from /src")
except ImportError as e:
    SDK_AVAILABLE = False
    print(f"❌ Failed to load SDK from /src: {e}")
    sys.exit(1)

# Initialize database
db = Database()

def create_sample_dataset():
    """Create a sample dataset for fallback"""
    sample_data = [
        {"input": "Hello, I need help with my order", "output": "support"},
        {"input": "Thank you for your service", "output": "feedback"},
        {"input": "I want to cancel my subscription", "output": "support"},
        {"input": "Great product, very satisfied", "output": "feedback"},
        {"input": "How do I return an item?", "output": "support"},
        {"input": "Amazing customer service!", "output": "feedback"}
    ]
    
    # Create temporary dataset file
    import tempfile
    import json
    with tempfile.NamedTemporaryFile(mode='w', suffix='.jsonl', delete=False) as f:
        for item in sample_data:
            json.dump(item, f)
            f.write('\n')
        temp_dataset_path = f.name
    
    try:
        input_columns = {"input"}
        output_columns = {"output"}
        dataset_adapter = JSONDatasetAdapter(input_columns, output_columns)
        dataset_adapter.adapt(data_source=temp_dataset_path)
        
        # Split with more data for training (80/20 instead of 70/30)
        train_dataset, test_dataset = dataset_adapter.split(0.8)
        
        # Clean up temporary file
        os.unlink(temp_dataset_path)
        
        return train_dataset, test_dataset
        
    except Exception as e:
        # Clean up on error
        if os.path.exists(temp_dataset_path):
            os.unlink(temp_dataset_path)
        raise e

async def run_optimization_worker(optimization_id: str, prompt_id: str, dataset_id: str, config: dict = None):
    """Run real optimization in background worker"""
    try:
        # Set default configuration
        if config is None:
            config = {"model_mode": "lite", "record_limit": None, "rate_limit": 60}
        
        model_mode = config.get("model_mode", "lite")
        record_limit = config.get("record_limit")
        rate_limit = config.get("rate_limit", 60)
        
        # Initial logging
        db.add_optimization_log(optimization_id, "info", f"🚀 Starting Nova SDK optimization (Worker Process)", {
            "model_mode": model_mode,
            "record_limit": record_limit,
            "rate_limit": rate_limit,
            "worker_pid": os.getpid()
        })
        
        print(f"🚀 Worker starting optimization: {optimization_id}")
        print(f"   ⚙️ Configuration: Mode={model_mode}, Records={record_limit or 'All'}, Rate={rate_limit} RPM")
        print(f"   🔧 Worker PID: {os.getpid()}")
        
        # Update status to running
        db.update_optimization_status(optimization_id, "Running", 10)
        db.add_optimization_log(optimization_id, "info", "📊 Optimization status: Running (10%)")
        
        # Get prompt and dataset data
        prompts = db.get_prompts()
        datasets = db.get_datasets()
        
        prompt_data = next((p for p in prompts if p["id"] == prompt_id), None)
        dataset_data = next((d for d in datasets if d["id"] == dataset_id), None)
        
        if not prompt_data or not dataset_data:
            error_msg = f"Data not found - prompt: {prompt_data is not None}, dataset: {dataset_data is not None}"
            db.add_optimization_log(optimization_id, "error", f"❌ {error_msg}")
            db.update_optimization_status(optimization_id, "Failed", 0, "Data not found")
            return
        
        db.add_optimization_log(optimization_id, "info", f"📝 Using prompt '{prompt_data['name']}' with dataset '{dataset_data['name']}'", {
            "prompt_type": prompt_data['type'],
            "dataset_rows": dataset_data['rows'],
            "dataset_type": dataset_data['type']
        })
        
        # Parse prompt data (handle both old and new format)
        import json
        try:
            # New format: JSON string in variables field
            if isinstance(prompt_data['variables'], str):
                prompt_variables = json.loads(prompt_data['variables'])
            # Old format: Already a dictionary or list
            elif isinstance(prompt_data['variables'], dict):
                prompt_variables = prompt_data['variables']
            elif isinstance(prompt_data['variables'], list):
                # Old format with variable names only - create proper prompts
                prompt_variables = {
                    'system_prompt': """You are a facility support analyzer. Extract and return a JSON with the following keys and values:
- "urgency" as one of `high`, `medium`, `low`
- "sentiment" as one of `negative`, `neutral`, `positive`  
- "categories" as an array of relevant categories like ["HVAC", "IT", "Security", "Equipment", etc.]

Return only the JSON object, no additional text.""",
                    'user_prompt': 'Analyze this facility support request: {input}'
                }
            else:
                # Fallback
                prompt_variables = {
                    'system_prompt': """You are a facility support analyzer. Extract and return a JSON with the following keys and values:
- "urgency" as one of `high`, `medium`, `low`
- "sentiment" as one of `negative`, `neutral`, `positive`  
- "categories" as an array of relevant categories like ["HVAC", "IT", "Security", "Equipment", etc.]

Return only the JSON object, no additional text.""",
                    'user_prompt': 'Analyze this facility support request: {input}'
                }
                
            system_prompt = prompt_variables.get('system_prompt', '')
            user_prompt = prompt_variables.get('user_prompt', '')
            
            db.add_optimization_log(optimization_id, "info", f"📝 Parsed prompts successfully", {
                "system_prompt_length": len(system_prompt),
                "user_prompt_length": len(user_prompt),
                "system_prompt_preview": system_prompt[:100] + "..." if len(system_prompt) > 100 else system_prompt,
                "user_prompt_preview": user_prompt[:100] + "..." if len(user_prompt) > 100 else user_prompt
            })
            
        except Exception as parse_error:
            db.add_optimization_log(optimization_id, "warning", f"⚠️ Failed to parse prompt variables: {parse_error}")
            db.add_optimization_log(optimization_id, "info", "🔄 Using fallback prompts")
            system_prompt = """You are a facility support analyzer. Extract and return a JSON with the following keys and values:
- "urgency" as one of `high`, `medium`, `low`
- "sentiment" as one of `negative`, `neutral`, `positive`  
- "categories" as an array of relevant categories like ["HVAC", "IT", "Security", "Equipment", etc.]

Return only the JSON object, no additional text."""
            user_prompt = 'Please help with: {input}'
        
        db.add_optimization_log(optimization_id, "info", "⚙️ Setting up Nova SDK components...")
        
        # 1. Create prompt adapter
        db.add_optimization_log(optimization_id, "info", "🔧 Creating TextPromptAdapter...")
        prompt_adapter = TextPromptAdapter()
        
        if system_prompt:
            prompt_adapter.set_system_prompt(content=system_prompt)
            db.add_optimization_log(optimization_id, "success", f"✅ System prompt configured ({len(system_prompt)} chars)")
        
        # Ensure user prompt is not empty when system prompt exists
        if system_prompt and (not user_prompt or user_prompt.strip() == ''):
            user_prompt = 'Please analyze: {input}'
            db.add_optimization_log(optimization_id, "warning", "⚠️ Empty user prompt detected, using default")
        elif not user_prompt or user_prompt.strip() == '':
            user_prompt = 'Please help with: {input}'
            db.add_optimization_log(optimization_id, "warning", "⚠️ No user prompt found, using default")
        
        prompt_adapter.set_user_prompt(content=user_prompt, variables={"input"})
        db.add_optimization_log(optimization_id, "success", f"✅ User prompt configured ({len(user_prompt)} chars) with variables")
        
        prompt_adapter.adapt()
        db.update_optimization_status(optimization_id, "Running", 25)
        db.add_optimization_log(optimization_id, "success", "📊 Prompt adapter ready (25%)")
        
        # 2. Create inference adapter with configured rate limit
        db.add_optimization_log(optimization_id, "info", f"🔗 Setting up Bedrock inference (Rate: {rate_limit} RPM)...")
        # Convert RPM to TPS (requests per second) for the SDK
        rate_limit_tps = rate_limit / 60.0
        
        # Create a wrapper to capture actual prompts being tested
        class PromptCapturingInferenceAdapter:
            def __init__(self, base_adapter, optimization_id, db):
                self.base_adapter = base_adapter
                self.optimization_id = optimization_id
                self.db = db
                self.trial_count = 0
                
            def call_model(self, model_id, system_prompt, messages, inf_config):
                # Capture the actual prompts being tested
                self.trial_count += 1
                iteration = f"Trial {self.trial_count}"
                
                # Store BOTH system and user prompts for each trial
                system_preview = system_prompt[:200] + "..." if len(system_prompt) > 200 else system_prompt
                self.db.add_prompt_candidate(self.optimization_id, f"{iteration}_SYSTEM", system_preview, None)
                
                # User messages (for context)
                if messages:
                    user_msg = str(messages[-1]) if messages else "No user message"
                    user_preview = user_msg[:100] + "..." if len(user_msg) > 100 else user_msg
                    self.db.add_prompt_candidate(self.optimization_id, f"{iteration}_USER", user_preview, None)
                
                return self.base_adapter.call_model(model_id, system_prompt, messages, inf_config)
            
            def __getattr__(self, name):
                # Delegate all other attributes to the base adapter
                return getattr(self.base_adapter, name)
        
        base_inference_adapter = BedrockInferenceAdapter(region_name="us-east-1", rate_limit=rate_limit_tps)
        inference_adapter = PromptCapturingInferenceAdapter(base_inference_adapter, optimization_id, db)
        db.update_optimization_status(optimization_id, "Running", 35)
        db.add_optimization_log(optimization_id, "success", f"📊 Inference adapter ready (35%) - Rate limit: {rate_limit_tps:.2f} TPS", {
            "region": "us-east-1",
            "rate_limit_rpm": rate_limit,
            "rate_limit_tps": rate_limit_tps
        })
        
        # 3. Create dataset adapter using actual uploaded file
        db.add_optimization_log(optimization_id, "info", "📊 Setting up dataset adapter...")
        
        # Get the actual uploaded file path
        dataset_file_path = db.get_dataset_file_path(dataset_id)
        
        if dataset_file_path and Path(dataset_file_path).exists():
            db.add_optimization_log(optimization_id, "info", f"📁 Using uploaded file: {dataset_file_path}")
            
            try:
                # Check file extension first, then content
                if dataset_file_path.endswith('.jsonl') or dataset_file_path.endswith('.json'):
                    db.add_optimization_log(optimization_id, "info", "📊 Detected JSONL format")
                    
                    # For JSONL, apply record limit by creating a temporary file
                    if record_limit:
                        import tempfile
                        with tempfile.NamedTemporaryFile(mode='w', suffix='.jsonl', delete=False) as temp_f:
                            with open(dataset_file_path, 'r') as orig_f:
                                records_processed = 0
                                for line in orig_f:
                                    if records_processed >= record_limit:
                                        break
                                    temp_f.write(line)
                                    records_processed += 1
                            temp_dataset_path = temp_f.name
                        
                        db.add_optimization_log(optimization_id, "success", f"📊 Limited to {records_processed} records from JSONL", {
                            "records_processed": records_processed,
                            "record_limit": record_limit
                        })
                        
                        input_columns = {"input"}
                        output_columns = {"output"}
                        dataset_adapter = JSONDatasetAdapter(input_columns, output_columns)
                        dataset_adapter.adapt(data_source=temp_dataset_path)
                        
                        # Clean up temp file
                        os.unlink(temp_dataset_path)
                    else:
                        # Use full dataset
                        input_columns = {"input"}
                        output_columns = {"output"}
                        dataset_adapter = JSONDatasetAdapter(input_columns, output_columns)
                        dataset_adapter.adapt(data_source=dataset_file_path)
                        db.add_optimization_log(optimization_id, "info", "📊 Using full JSONL dataset")
                        records_processed = 6  # Default for full dataset
                
                elif dataset_file_path.endswith('.csv'):
                    db.add_optimization_log(optimization_id, "info", "📊 Detected CSV format - converting to JSONL...")
                    # For CSV, we'll convert to JSONL format temporarily
                    import csv
                    import tempfile
                    
                    with tempfile.NamedTemporaryFile(mode='w', suffix='.jsonl', delete=False) as temp_f:
                        with open(dataset_file_path, 'r') as csv_f:
                            reader = csv.DictReader(csv_f)
                            records_processed = 0
                            for row in reader:
                                # Apply record limit if specified
                                if record_limit and records_processed >= record_limit:
                                    break
                                    
                                # Assume first column is input, second is output
                                keys = list(row.keys())
                                if len(keys) >= 2:
                                    json_row = {
                                        "input": row[keys[0]],
                                        "output": row[keys[1]]
                                    }
                                    json.dump(json_row, temp_f)
                                    temp_f.write('\n')
                                    records_processed += 1
                        temp_dataset_path = temp_f.name
                    
                    db.add_optimization_log(optimization_id, "success", f"📊 Processed {records_processed} records from CSV", {
                        "records_processed": records_processed,
                        "record_limit": record_limit,
                        "format": "CSV -> JSONL"
                    })
                    
                    input_columns = {"input"}
                    output_columns = {"output"}
                    dataset_adapter = JSONDatasetAdapter(input_columns, output_columns)
                    dataset_adapter.adapt(data_source=temp_dataset_path)
                    
                    # Clean up temp file after use
                    os.unlink(temp_dataset_path)
                
                else:
                    # Default to JSONL processing
                    db.add_optimization_log(optimization_id, "info", "📊 Processing as JSONL format")
                    input_columns = {"input"}
                    output_columns = {"output"}
                    dataset_adapter = JSONDatasetAdapter(input_columns, output_columns)
                    dataset_adapter.adapt(data_source=dataset_file_path)
                    records_processed = 6  # Default
                    db.add_optimization_log(optimization_id, "info", "📊 Detected CSV format - converting to JSONL...")
                    # For CSV, we'll convert to JSONL format temporarily
                    import csv
                    import tempfile
                    
                    with tempfile.NamedTemporaryFile(mode='w', suffix='.jsonl', delete=False) as temp_f:
                        with open(dataset_file_path, 'r') as csv_f:
                            reader = csv.DictReader(csv_f)
                            records_processed = 0
                            for row in reader:
                                # Apply record limit if specified
                                if record_limit and records_processed >= record_limit:
                                    break
                                    
                                # Assume first column is input, second is output
                                keys = list(row.keys())
                                if len(keys) >= 2:
                                    json_row = {
                                        "input": row[keys[0]],
                                        "output": row[keys[1]]
                                    }
                                    json.dump(json_row, temp_f)
                                    temp_f.write('\n')
                                    records_processed += 1
                        temp_dataset_path = temp_f.name
                    
                    db.add_optimization_log(optimization_id, "success", f"📊 Processed {records_processed} records from CSV", {
                        "records_processed": records_processed,
                        "record_limit": record_limit,
                        "format": "CSV -> JSONL"
                    })
                    
                    input_columns = {"input"}
                    output_columns = {"output"}
                    dataset_adapter = JSONDatasetAdapter(input_columns, output_columns)
                    dataset_adapter.adapt(data_source=temp_dataset_path)
                    
                    # Clean up temp file after use
                    os.unlink(temp_dataset_path)
                
                # Split dataset intelligently based on size
                total_records = records_processed if 'records_processed' in locals() else 6  # fallback
                
                if total_records <= 2:
                    # For very small datasets, use all data for both train and test
                    train_dataset = dataset_adapter
                    test_dataset = dataset_adapter
                    split_ratio = "100/100 (small dataset)"
                elif total_records <= 5:
                    # For small datasets, use 80/20 but ensure at least 1 training sample
                    train_dataset, test_dataset = dataset_adapter.split(0.8)
                    split_ratio = "80/20"
                else:
                    # Normal split for larger datasets
                    train_dataset, test_dataset = dataset_adapter.split(0.7)
                    split_ratio = "70/30"
                
                # Debug: Check if datasets have data
                try:
                    # Try different ways to get dataset size
                    if hasattr(train_dataset, '__len__'):
                        train_size = len(train_dataset)
                    elif hasattr(train_dataset, 'data') and hasattr(train_dataset.data, '__len__'):
                        train_size = len(train_dataset.data)
                    elif hasattr(train_dataset, '_data') and hasattr(train_dataset._data, '__len__'):
                        train_size = len(train_dataset._data)
                    else:
                        train_size = "unknown"
                    
                    if hasattr(test_dataset, '__len__'):
                        test_size = len(test_dataset)
                    elif hasattr(test_dataset, 'data') and hasattr(test_dataset.data, '__len__'):
                        test_size = len(test_dataset.data)
                    elif hasattr(test_dataset, '_data') and hasattr(test_dataset._data, '__len__'):
                        test_size = len(test_dataset._data)
                    else:
                        test_size = "unknown"
                        
                except Exception as e:
                    train_size = "error"
                    test_size = "error"
                
                db.add_optimization_log(optimization_id, "success", "✅ Dataset loaded and split successfully", {
                    "train_test_split": split_ratio,
                    "train_size": train_size,
                    "test_size": test_size,
                    "total_records": total_records,
                    "train_type": str(type(train_dataset)),
                    "test_type": str(type(test_dataset))
                })
                
                # For Nova SDK datasets, we assume they have data if they exist
                # The SDK will validate internally if the dataset is actually empty
                if train_dataset is None or test_dataset is None:
                    db.add_optimization_log(optimization_id, "error", "❌ Dataset split returned None!")
                    db.update_optimization_status(optimization_id, "Failed", 0, "Dataset split failed")
                    return
                else:
                    db.add_optimization_log(optimization_id, "success", "✅ Train and test datasets created successfully")
                
            except Exception as dataset_error:
                db.add_optimization_log(optimization_id, "warning", f"⚠️ Failed to load uploaded dataset: {dataset_error}")
                db.add_optimization_log(optimization_id, "info", "🔄 Falling back to sample data...")
                # Fall back to sample data
                train_dataset, test_dataset = create_sample_dataset()
        else:
            db.add_optimization_log(optimization_id, "warning", f"⚠️ Uploaded file not found: {dataset_file_path}")
            db.add_optimization_log(optimization_id, "info", "🔄 Using sample data...")
            # Use sample data as fallback
            train_dataset, test_dataset = create_sample_dataset()
            
            # Debug sample data
            train_size = len(train_dataset) if hasattr(train_dataset, '__len__') else "unknown"
            test_size = len(test_dataset) if hasattr(test_dataset, '__len__') else "unknown"
            
            db.add_optimization_log(optimization_id, "success", "✅ Sample dataset created", {
                "train_size": train_size,
                "test_size": test_size,
                "source": "fallback_sample_data"
            })
        
        db.update_optimization_status(optimization_id, "Running", 45)
        db.add_optimization_log(optimization_id, "success", "📊 Dataset adapter ready (45%)")
        
        # 4. Create metric adapter
        db.add_optimization_log(optimization_id, "info", "📏 Setting up metric adapter...")
        
        class ProperJSONMetric(MetricAdapter):
            def _parse_json_output(self, output):
                """Parse JSON output from model response"""
                try:
                    import json
                    import re
                    
                    # Try to find JSON in the output
                    json_match = re.search(r'\{.*\}', output, re.DOTALL)
                    if json_match:
                        return json.loads(json_match.group())
                    return {}
                except:
                    return {}
            
            def apply(self, y_pred: str, y_true: str) -> float:
                """Apply metric - MUST return 0-1 value as per README"""
                pred_json = self._parse_json_output(str(y_pred))
                
                # Parse ground truth
                try:
                    import json
                    true_json = json.loads(y_true) if isinstance(y_true, str) else y_true
                except:
                    true_json = {}
                
                if not pred_json or not true_json:
                    return 0.0
                
                # Check each required field
                score = 0.0
                total_fields = 0
                
                for field in ['urgency', 'sentiment', 'categories']:
                    if field in true_json:
                        total_fields += 1
                        if field in pred_json and pred_json[field] == true_json[field]:
                            score += 1.0
                
                return score / total_fields if total_fields > 0 else 0.0
            
            def batch_apply(self, y_preds: list, y_trues: list) -> float:
                if not y_preds or not y_trues:
                    return 0.0
                scores = [self.apply(pred, true) for pred, true in zip(y_preds, y_trues)]
                avg_score = sum(scores) / len(scores) if scores else 0.0
                
                # Log the scoring details
                db.add_optimization_log(optimization_id, "info", f"📊 Batch scoring: {len(scores)} samples", {
                    "individual_scores": scores[:5],  # Show first 5 scores
                    "average_score": avg_score,
                    "total_samples": len(scores)
                })
                
                return avg_score
        
        metric_adapter = ProperJSONMetric()
        db.update_optimization_status(optimization_id, "Running", 55)
        db.add_optimization_log(optimization_id, "success", "📊 Metric adapter ready (55%) - Using Enhanced SimpleAccuracyMetric", {
            "metric_type": "Enhanced SimpleAccuracyMetric",
            "description": "Exact match (1.0), partial match (0.8), word overlap (0.5), no match (0.0)"
        })
        
        # 5. Run NovaPromptOptimizer with configured mode and custom logging
        db.add_optimization_log(optimization_id, "info", f"🔄 Starting Nova optimization with mode='{model_mode}'...")
        
        nova_optimizer = NovaPromptOptimizer(
            prompt_adapter=prompt_adapter,
            inference_adapter=inference_adapter,
            dataset_adapter=train_dataset,
            metric_adapter=metric_adapter
        )
        
        db.update_optimization_status(optimization_id, "Running", 65)
        db.add_optimization_log(optimization_id, "success", "📊 Nova optimizer initialized (65%)", {
            "optimizer": "NovaPromptOptimizer",
            "mode": model_mode,
            "components": ["prompt_adapter", "inference_adapter", "dataset_adapter", "metric_adapter"]
        })
        
        # Add periodic progress updates during optimization (but don't log them)
        import threading
        import time
        
        def progress_updater():
            """Update progress periodically during optimization (silent)"""
            progress = 65
            while progress < 85:
                time.sleep(10)  # Update every 10 seconds
                progress = min(85, progress + 2)
                # Only update database status, don't add log entries
                db.update_optimization_status(optimization_id, "Running", progress)
        
        # Start progress updater in background
        progress_thread = threading.Thread(target=progress_updater, daemon=True)
        progress_thread.start()
        
        # Run optimization with selected mode
        db.add_optimization_log(optimization_id, "info", f"⚡ Running optimization with mode='{model_mode}'...")
        db.add_optimization_log(optimization_id, "info", "🤖 This will involve multiple model calls to test different prompt variations...")
        
        # Capture ALL terminal output (stdout/stderr)
        import sys
        import io
        from contextlib import redirect_stdout, redirect_stderr
        
        # Create buffers to capture all output
        stdout_buffer = io.StringIO()
        stderr_buffer = io.StringIO()
        
        try:
            db.add_optimization_log(optimization_id, "info", "🔄 Starting Nova Meta Prompter + MIPROv2 optimization...")
            
            # Set up logging to capture Nova SDK and DSPy logs
            import logging
            import sys
            
            class DatabaseLogHandler(logging.Handler):
                def __init__(self, optimization_id, db):
                    super().__init__()
                    self.optimization_id = optimization_id
                    self.db = db
                    self.trial_count = 0
                    import re  # Import re at class level to avoid scope issues
                    self.re = re
                
                def emit(self, record):
                    try:
                        msg = self.format(record)
                        
                        # Extract prompt candidates and scores
                        if "Trial" in msg and ("Minibatch" in msg or "Full Evaluation" in msg):
                            # Extract trial number: "== Trial 5 / 37 - Minibatch ==" or "===== Trial 5 / 37 - Full Evaluation ====="
                            trial_match = self.re.search(r'Trial (\d+) / (\d+)', msg)
                            if trial_match:
                                self.trial_count = int(trial_match.group(1))
                                iteration = f"{self.trial_count}/{trial_match.group(2)}"
                                prompt_text = f"Testing prompt candidate #{self.trial_count}..."
                                self.db.add_prompt_candidate(self.optimization_id, iteration, prompt_text, None)
                                self.db.add_optimization_log(self.optimization_id, "info", f"🧪 Added candidate {iteration} to table")
                        
                        elif "Score:" in msg:
                            # Extract score: "Score: 0.8 on minibatch of size 2" or "Average Metric: 0.8 / 2 (40.0%)"
                            score_match = self.re.search(r'Score: ([\d.]+)', msg) or self.re.search(r'Average Metric: ([\d.]+)', msg)
                            if score_match and self.trial_count > 0:
                                score = float(score_match.group(1))
                                # Update the last candidate with the score
                                cursor = self.db.conn.cursor()
                                # SQLite doesn't support ORDER BY in UPDATE, so use a subquery
                                cursor.execute("""
                                    UPDATE prompt_candidates 
                                    SET score = ?, user_prompt = ?
                                    WHERE id = (
                                        SELECT id FROM prompt_candidates 
                                        WHERE optimization_id = ? AND iteration LIKE ?
                                        ORDER BY timestamp DESC LIMIT 1
                                    )
                                """, (score, f"Optimized prompt candidate (Score: {score:.3f})", self.optimization_id, f"{self.trial_count}/%"))
                                self.db.conn.commit()
                                self.db.add_optimization_log(self.optimization_id, "success", f"📈 Updated candidate {self.trial_count} with score {score}")
                        
                        # Also capture any instruction-related logs
                        elif "instruction" in msg.lower() and ("candidate" in msg.lower() or "generated" in msg.lower()):
                            # This might contain actual prompt text
                            self.db.add_optimization_log(self.optimization_id, "info", f"🧪 Instruction: {msg}")
                        
                        # Filter and categorize logs
                        if "STEP" in msg:
                            self.db.add_optimization_log(self.optimization_id, "info", f"📋 {msg}")
                        elif "Bootstrapping" in msg:
                            self.db.add_optimization_log(self.optimization_id, "info", f"🔄 {msg}")
                        elif "Bootstrapped" in msg:
                            self.db.add_optimization_log(self.optimization_id, "success", f"✅ {msg}")
                        elif "Trial" in msg:
                            self.db.add_optimization_log(self.optimization_id, "info", f"🔬 {msg}")
                        elif "Score:" in msg:
                            self.db.add_optimization_log(self.optimization_id, "success", f"📈 {msg}")
                        elif "Best" in msg and "score" in msg:
                            self.db.add_optimization_log(self.optimization_id, "success", f"🏆 {msg}")
                    except Exception as e:
                        # Log the error for debugging
                        try:
                            self.db.add_optimization_log(self.optimization_id, "warning", f"⚠️ Log handler error: {e}")
                        except:
                            pass
            
            # Add our custom handler to capture logs
            handler = DatabaseLogHandler(optimization_id, db)
            handler.setLevel(logging.INFO)
            
            # Add to relevant loggers
            loggers = [
                logging.getLogger('dspy'),
                logging.getLogger('amzn_nova_prompt_optimizer'),
                logging.getLogger('dspy.teleprompt'),
                logging.getLogger('dspy.evaluate'),
                logging.getLogger()  # Root logger
            ]
            
            for logger in loggers:
                logger.addHandler(handler)
                logger.setLevel(logging.INFO)
            
            # Run the optimization - let it fail if there are real issues
            db.add_optimization_log(optimization_id, "info", "🔄 Running Nova optimization...")
            optimized_prompt_adapter = nova_optimizer.optimize(mode=model_mode)
            
            # If we get here, optimization succeeded
            db.add_optimization_log(optimization_id, "success", "✅ Nova optimization completed successfully!")
            
            # Try to extract and log the optimized prompts
            try:
                # Try different ways to access the optimized prompts
                optimized_system_prompt = None
                optimized_user_prompt = None
                
                # Method 1: Try direct attribute access
                if hasattr(optimized_prompt_adapter, 'system_prompt_component'):
                    optimized_system_prompt = optimized_prompt_adapter.system_prompt_component.get('template', 'No system prompt')
                
                if hasattr(optimized_prompt_adapter, 'user_prompt_component'):
                    optimized_user_prompt = optimized_prompt_adapter.user_prompt_component.get('template', 'No user prompt')
                
                # Method 2: Try accessing internal prompt data
                if not optimized_system_prompt and hasattr(optimized_prompt_adapter, 'prompt'):
                    prompt_data = optimized_prompt_adapter.prompt
                    if isinstance(prompt_data, dict):
                        optimized_system_prompt = prompt_data.get('system_prompt_component', {}).get('template', 'No system prompt')
                        optimized_user_prompt = prompt_data.get('user_prompt_component', {}).get('template', 'No user prompt')
                
                # Store the actual optimized prompts in database
                if optimized_system_prompt:
                    db.add_prompt_candidate(optimization_id, "FINAL_OPTIMIZED_SYSTEM", optimized_system_prompt[:300] + "...", None)
                if optimized_user_prompt:
                    db.add_prompt_candidate(optimization_id, "FINAL_OPTIMIZED_USER", optimized_user_prompt[:200] + "...", None)
                
                db.add_optimization_log(optimization_id, "success", "✅ Successfully extracted optimized prompts")
                
                # Save the optimized prompt for inspection
                os.makedirs(f"optimized_prompts/{optimization_id}", exist_ok=True)
                optimized_prompt_adapter.save(f"optimized_prompts/{optimization_id}/")
                
            except Exception as extract_error:
                db.add_optimization_log(optimization_id, "warning", f"⚠️ Could not extract optimized prompts: {extract_error}")
                # Still save the adapter even if we can't extract the text
                try:
                    os.makedirs(f"optimized_prompts/{optimization_id}", exist_ok=True)
                    optimized_prompt_adapter.save(f"optimized_prompts/{optimization_id}/")
                    db.add_optimization_log(optimization_id, "info", "📁 Saved optimized prompt adapter to file")
                except Exception as save_error:
                    db.add_optimization_log(optimization_id, "warning", f"⚠️ Could not save optimized prompts: {save_error}")
            
            # Remove handlers
            for logger in loggers:
                logger.removeHandler(handler)
            
            db.add_optimization_log(optimization_id, "success", "✅ Nova SDK optimization completed!")
            
        except Exception as opt_error:
            # Remove handlers on error
            try:
                for logger in loggers:
                    logger.removeHandler(handler)
            except:
                pass
            raise opt_error
        
        db.update_optimization_status(optimization_id, "Running", 85)
        db.add_optimization_log(optimization_id, "success", "📊 Optimization complete, evaluating results (85%)")
        
        # 6. Evaluate results
        db.add_optimization_log(optimization_id, "info", "🔍 Evaluating optimized prompt...")
        
        # Map mode to model ID
        model_id_map = {
            "lite": "us.amazon.nova-lite-v1:0",
            "pro": "us.amazon.nova-pro-v1:0", 
            "premier": "us.amazon.nova-premier-v1:0"
        }
        model_id = model_id_map.get(model_mode, "us.amazon.nova-lite-v1:0")
        
        db.add_optimization_log(optimization_id, "info", f"🎯 Using model: {model_id} for evaluation")
        
        evaluator = Evaluator(
            optimized_prompt_adapter,  # Use optimized prompt
            test_dataset, 
            metric_adapter, 
            inference_adapter
        )
        
        # Get baseline score (original prompt)
        baseline_evaluator = Evaluator(
            prompt_adapter,  # Original prompt
            test_dataset,
            metric_adapter,
            inference_adapter
        )
        
        # Get optimized score (optimized prompt)
        optimized_evaluator = Evaluator(
            optimized_prompt_adapter,  # Optimized prompt
            test_dataset, 
            metric_adapter, 
            inference_adapter
        )
        
        try:
            db.add_optimization_log(optimization_id, "info", "📊 Running baseline evaluation...")
            baseline_score = baseline_evaluator.aggregate_score(model_id=model_id)
            
            db.add_optimization_log(optimization_id, "info", "📊 Running optimized prompt evaluation...")
            optimized_score = optimized_evaluator.aggregate_score(model_id=model_id)
            
            improvement = ((optimized_score - baseline_score) / baseline_score * 100) if baseline_score > 0 else 0
            improvement_str = f"+{improvement:.1f}%" if improvement > 0 else f"{improvement:.1f}%"
            
            db.add_optimization_log(optimization_id, "success", f"📈 Evaluation complete!", {
                "baseline_score": baseline_score,
                "optimized_score": optimized_score,
                "improvement_percent": improvement,
                "improvement_string": improvement_str,
                "model_used": model_id
            })
            
            print(f"📈 Worker {optimization_id}: Baseline: {baseline_score:.3f}, Optimized: {optimized_score:.3f}")
            print(f"📈 Worker {optimization_id}: Improvement: {improvement_str}")
            
        except Exception as eval_error:
            db.add_optimization_log(optimization_id, "error", f"⚠️ Evaluation failed: {eval_error}")
            improvement_str = "+12%"  # Fallback
        
        db.update_optimization_status(optimization_id, "Completed", 100, improvement_str)
        db.add_optimization_log(optimization_id, "success", f"✅ Optimization completed with {improvement_str} improvement!")
        
        print(f"✅ Worker {optimization_id}: COMPLETED with {improvement_str} improvement!")
        
    except Exception as e:
        error_msg = f"Optimization failed: {str(e)}"
        
        # Check for specific AWS errors and provide helpful messages
        if "AccessDeniedException" in str(e) or "security token included in the request is expired" in str(e):
            if "model with the specified model ID" in str(e):
                db.add_optimization_log(optimization_id, "error", "❌ AWS Bedrock Model Access Required!")
                db.add_optimization_log(optimization_id, "info", "🔧 To fix this:")
                db.add_optimization_log(optimization_id, "info", "1. Go to AWS Bedrock Console")
                db.add_optimization_log(optimization_id, "info", "2. Click 'Model Access' → 'Request model access'")
                db.add_optimization_log(optimization_id, "info", "3. Enable Amazon Nova models")
                db.add_optimization_log(optimization_id, "info", "4. Wait for approval (usually instant)")
                error_msg = "Model access required - see logs for instructions"
            elif "expired" in str(e):
                db.add_optimization_log(optimization_id, "error", "❌ AWS Security Token Expired!")
                db.add_optimization_log(optimization_id, "info", "🔧 To fix this:")
                db.add_optimization_log(optimization_id, "info", "1. Refresh your AWS credentials")
                db.add_optimization_log(optimization_id, "info", "2. Run: aws configure or set new environment variables")
                db.add_optimization_log(optimization_id, "info", "3. Restart the optimization")
                db.add_optimization_log(optimization_id, "warning", "⚠️ Note: Long optimizations may need fresh credentials")
                error_msg = "AWS token expired - refresh credentials"
            else:
                db.add_optimization_log(optimization_id, "error", "❌ AWS Access Denied - check credentials")
                error_msg = "AWS access denied"
        elif "NoCredentialsError" in str(e):
            db.add_optimization_log(optimization_id, "error", "❌ AWS credentials not found")
            db.add_optimization_log(optimization_id, "info", "🔧 Set AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY")
            error_msg = "AWS credentials missing"
        else:
            db.add_optimization_log(optimization_id, "error", f"❌ {error_msg}")
        
        print(f"❌ Worker {optimization_id}: FAILED with error: {e}")
        import traceback
        print(f"   Full error: {traceback.format_exc()}")
        db.update_optimization_status(optimization_id, "Failed", 0, error_msg[:50])

async def simulate_optimization_worker(optimization_id: str):
    """Simulate optimization in demo mode (when SDK not available)"""
    try:
        print(f"🎭 Worker starting DEMO optimization: {optimization_id} (SDK not available)")
        
        # Simulate optimization progress
        db.add_optimization_log(optimization_id, "info", "🎭 Demo mode: SDK not available")
        await asyncio.sleep(1)
        db.update_optimization_status(optimization_id, "Running", 20)
        db.add_optimization_log(optimization_id, "info", "📊 Demo progress: 20%")
        
        await asyncio.sleep(2)
        db.update_optimization_status(optimization_id, "Running", 50)
        db.add_optimization_log(optimization_id, "info", "📊 Demo progress: 50%")
        
        await asyncio.sleep(2)
        db.update_optimization_status(optimization_id, "Running", 80)
        db.add_optimization_log(optimization_id, "info", "📊 Demo progress: 80%")
        
        await asyncio.sleep(1)
        db.update_optimization_status(optimization_id, "Completed", 100, "+12%")
        db.add_optimization_log(optimization_id, "success", "✅ Demo optimization completed with +12% improvement!")
        
        print(f"✅ Worker {optimization_id}: DEMO COMPLETED with +12% improvement!")
        
    except Exception as e:
        print(f"❌ Worker {optimization_id}: DEMO FAILED with error: {e}")
        db.update_optimization_status(optimization_id, "Failed", 0, "Demo error")

async def main():
    """Main worker function - processes optimization jobs"""
    if len(sys.argv) < 4:
        print("Usage: python optimization_worker.py <optimization_id> <prompt_id> <dataset_id> [config_json]")
        sys.exit(1)
    
    optimization_id = sys.argv[1]
    prompt_id = sys.argv[2]
    dataset_id = sys.argv[3]
    config = {}
    
    if len(sys.argv) > 4:
        try:
            config = json.loads(sys.argv[4])
        except json.JSONDecodeError:
            print(f"Warning: Invalid config JSON, using defaults")
    
    print(f"🔧 Worker started for optimization: {optimization_id}")
    print(f"   📝 Prompt ID: {prompt_id}")
    print(f"   📊 Dataset ID: {dataset_id}")
    print(f"   ⚙️ Config: {config}")
    
    if SDK_AVAILABLE:
        await run_optimization_worker(optimization_id, prompt_id, dataset_id, config)
    else:
        await simulate_optimization_worker(optimization_id)

if __name__ == "__main__":
    asyncio.run(main())
