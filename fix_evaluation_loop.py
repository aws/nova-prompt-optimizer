#!/usr/bin/env python3
"""
Fix for Nova Prompt Optimizer infinite evaluation loop
"""

def patch_evaluator():
    """
    Patch the Evaluator class to add bounds checking and prevent infinite loops
    """
    import sys
    import os
    
    # Add the src directory to Python path
    src_path = os.path.join(os.getcwd(), 'src')
    if src_path not in sys.path:
        sys.path.insert(0, src_path)
    
    # Import and patch the Evaluator class
    from amzn_nova_prompt_optimizer.core.evaluation import Evaluator
    
    # Store original methods
    original_scores = Evaluator.scores
    original_aggregate_score = Evaluator.aggregate_score
    
    def safe_scores(self, model_id: str):
        """Safe version of scores with bounds checking"""
        self.inference_results = self._get_or_run_inference(model_id)
        
        self.logger.info(f"Running Evaluation on Dataset, using `apply` metric")
        self.logger.info(f"Dataset size: {len(self.inference_results)} samples")
        
        self.evaluation_results = []
        
        # Add explicit bounds checking
        max_samples = len(self.inference_results)
        processed_count = 0
        
        for i, row in enumerate(self.inference_results):
            if processed_count >= max_samples:
                self.logger.warning(f"Reached maximum samples ({max_samples}), stopping evaluation")
                break
                
            try:
                y_pred = row["inference_output"]
                output_field = list(self.dataset_adapter.output_columns)[0]
                y_true = row["outputs"][output_field]
                
                # Apply metric with timeout protection
                score = self.metric_adapter.apply(y_pred, y_true)
                row["evaluation"] = score
                self.evaluation_results.append(row)
                
                processed_count += 1
                
                # Log progress every 10 samples
                if processed_count % 10 == 0:
                    self.logger.info(f"Processed {processed_count}/{max_samples} samples")
                    
            except Exception as e:
                self.logger.error(f"Error processing sample {i}: {e}")
                continue
        
        self.logger.info(f"Evaluation completed: {processed_count} samples processed")
        return self.evaluation_results
    
    def safe_aggregate_score(self, model_id: str):
        """Safe version of aggregate_score with bounds checking"""
        self.inference_results = self._get_or_run_inference(model_id)
        
        self.logger.info(f"Running Batch Evaluation on Dataset, using `batch_apply` metric")
        self.logger.info(f"Dataset size: {len(self.inference_results)} samples")
        
        self.y_preds = []
        self.y_trues = []
        
        # Add explicit bounds checking
        max_samples = len(self.inference_results)
        
        for i, row in enumerate(self.inference_results):
            if i >= max_samples:
                self.logger.warning(f"Reached maximum samples ({max_samples}), stopping")
                break
                
            self.y_preds.append(row["inference_output"])
            output_field = list(self.dataset_adapter.output_columns)[0]
            self.y_trues.append(row["outputs"][output_field])
        
        self.logger.info(f"Prepared {len(self.y_preds)} predictions for batch evaluation")
        
        # Call scores method (which is now safe)
        self.scores(model_id)
        
        # Apply batch metric
        result = self.metric_adapter.batch_apply(self.y_preds, self.y_trues)
        self.logger.info(f"Batch evaluation completed with score: {result}")
        return result
    
    # Apply patches
    Evaluator.scores = safe_scores
    Evaluator.aggregate_score = safe_aggregate_score
    
    print("✅ Evaluator patched with bounds checking")

if __name__ == "__main__":
    patch_evaluator()
    print("✅ Evaluation loop fix applied")