"""
Metric Validation Service - Tests generated metrics with sample data
"""
import json
import traceback
from typing import Dict, List, Any

class MetricValidator:
    """Validates generated metric code with sample data"""
    
    def validate_metric(self, metric_code: str, sample_data: List[Dict]) -> Dict:
        """
        Test metric with sample data and return validation results
        
        Args:
            metric_code: Generated Python metric code
            sample_data: List of sample data points from dataset
            
        Returns:
            Dict with validation results for non-developers
        """
        validation_result = {
            "is_valid": False,
            "error_message": None,
            "sample_scores": [],
            "score_distribution": {},
            "warnings": [],
            "recommendations": []
        }
        
        try:
            # Execute the metric code
            namespace = {}
            exec(metric_code, namespace)
            
            # Find the metric class
            metric_class = None
            for name, obj in namespace.items():
                if hasattr(obj, '__bases__') and any('MetricAdapter' in str(base) for base in obj.__bases__):
                    metric_class = obj
                    break
            
            if not metric_class:
                validation_result["error_message"] = "❌ No MetricAdapter class found in generated code"
                return validation_result
            
            # Test with sample data
            metric_instance = metric_class()
            scores = []
            
            for i, sample in enumerate(sample_data[:5]):  # Test first 5 samples
                try:
                    # Extract input and expected output
                    y_true = sample.get('answer', sample)
                    
                    # Simulate model output (use ground truth for testing)
                    y_pred = y_true
                    
                    score = metric_instance.apply(y_pred, y_true)
                    scores.append({
                        "sample_index": i + 1,
                        "score": score,
                        "input_preview": str(sample.get('input', ''))[:100] + "..." if len(str(sample.get('input', ''))) > 100 else str(sample.get('input', ''))
                    })
                    
                except Exception as e:
                    scores.append({
                        "sample_index": i + 1,
                        "score": "ERROR",
                        "error": str(e),
                        "input_preview": str(sample.get('input', ''))[:100] + "..."
                    })
            
            validation_result["sample_scores"] = scores
            
            # Analyze score distribution
            valid_scores = [s["score"] for s in scores if isinstance(s["score"], (int, float))]
            if valid_scores:
                validation_result["score_distribution"] = {
                    "min_score": min(valid_scores),
                    "max_score": max(valid_scores),
                    "avg_score": sum(valid_scores) / len(valid_scores),
                    "unique_scores": len(set(valid_scores))
                }
                
                # Add warnings and recommendations
                if all(score == valid_scores[0] for score in valid_scores):
                    validation_result["warnings"].append("⚠️ All samples get the same score - metric may not be discriminating enough")
                
                if all(score == 1.0 for score in valid_scores):
                    validation_result["warnings"].append("⚠️ All samples get perfect score - metric may be too easy")
                    validation_result["recommendations"].append("💡 Consider using more challenging test data")
                
                if all(score == 0.0 for score in valid_scores):
                    validation_result["warnings"].append("⚠️ All samples get zero score - metric may have data structure issues")
                    validation_result["recommendations"].append("💡 Check if metric is looking for correct field names in your data")
                
                if len(set(valid_scores)) > 1:
                    validation_result["recommendations"].append("✅ Good! Metric shows varied scores across samples")
                
                validation_result["is_valid"] = True
            else:
                validation_result["error_message"] = "❌ No valid scores generated - all samples failed"
                
        except Exception as e:
            validation_result["error_message"] = f"❌ Code execution failed: {str(e)}"
            validation_result["technical_details"] = traceback.format_exc()
        
        return validation_result
    
    def format_validation_report(self, validation_result: Dict) -> str:
        """Format validation results for non-developers"""
        
        if not validation_result["is_valid"]:
            return f"""
🔴 **Metric Validation Failed**

**Error:** {validation_result.get('error_message', 'Unknown error')}

**What this means:** The generated metric code has issues and won't work properly for optimization.

**Next steps:** Try creating the metric again or contact support.
"""
        
        report = "🟢 **Metric Validation Passed**\n\n"
        
        # Score summary
        dist = validation_result["score_distribution"]
        report += f"**Score Range:** {dist['min_score']:.3f} to {dist['max_score']:.3f}\n"
        report += f"**Average Score:** {dist['avg_score']:.3f}\n"
        report += f"**Score Variety:** {dist['unique_scores']} different scores\n\n"
        
        # Sample results
        report += "**Sample Test Results:**\n"
        for sample in validation_result["sample_scores"]:
            if isinstance(sample["score"], (int, float)):
                report += f"• Sample {sample['sample_index']}: Score {sample['score']:.3f}\n"
            else:
                report += f"• Sample {sample['sample_index']}: ❌ {sample.get('error', 'Failed')}\n"
        
        # Warnings
        if validation_result["warnings"]:
            report += "\n**⚠️ Warnings:**\n"
            for warning in validation_result["warnings"]:
                report += f"• {warning}\n"
        
        # Recommendations
        if validation_result["recommendations"]:
            report += "\n**💡 Recommendations:**\n"
            for rec in validation_result["recommendations"]:
                report += f"• {rec}\n"
        
        return report
