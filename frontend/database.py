"""
SQLite database management for Nova Prompt Optimizer
Simple, file-based persistence without external dependencies
"""

import sqlite3
import json
from pathlib import Path
from typing import List, Dict, Optional, Any
from datetime import datetime

# Database file location
DB_PATH = Path("nova_optimizer.db")

class Database:
    def __init__(self, db_path: Path = DB_PATH):
        self.db_path = db_path
        self.init_database()
        self.seed_initial_data()
    
    def get_connection(self):
        """Get database connection"""
        if not hasattr(self, 'conn') or self.conn is None:
            self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        return self.conn
    
    def init_database(self):
        """Initialize database tables"""
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        conn = self.conn
        
        # Datasets table
        conn.execute("""
            CREATE TABLE IF NOT EXISTS datasets (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                dataset_type TEXT,
                size TEXT,
                rows INTEGER,
                created TEXT,
                status TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Prompts table
        conn.execute("""
            CREATE TABLE IF NOT EXISTS prompts (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                prompt_type TEXT,
                variables TEXT, -- JSON array
                created TEXT,
                last_used TEXT,
                performance TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Optimizations table
        conn.execute("""
            CREATE TABLE IF NOT EXISTS optimizations (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                prompt TEXT,
                dataset TEXT,
                metric_id TEXT,
                status TEXT,
                progress INTEGER DEFAULT 0,
                improvement TEXT,
                started TEXT,
                completed TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (metric_id) REFERENCES metrics (id)
            )
        """)
        
        # Migration: Add metric_id column if it doesn't exist
        try:
            conn.execute("ALTER TABLE optimizations ADD COLUMN metric_id TEXT")
        except sqlite3.OperationalError:
            # Column already exists
            pass
        
        # Optimization logs table
        conn.execute("""
            CREATE TABLE IF NOT EXISTS optimization_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                optimization_id TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                log_type TEXT NOT NULL,
                message TEXT NOT NULL,
                data TEXT,
                FOREIGN KEY (optimization_id) REFERENCES optimizations (id)
            )
        """)
        
        # Prompt candidates table
        conn.execute("""
            CREATE TABLE IF NOT EXISTS prompt_candidates (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                optimization_id TEXT NOT NULL,
                candidate_number INTEGER NOT NULL,
                prompt_text TEXT NOT NULL,
                model_response TEXT,
                score REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (optimization_id) REFERENCES optimizations (id)
            )
        """)
        
        # Migration: Update prompt_candidates table structure if needed
        try:
            # Check if old columns exist and migrate
            cursor = conn.execute("PRAGMA table_info(prompt_candidates)")
            columns = [row[1] for row in cursor.fetchall()]
            
            if 'iteration' in columns and 'candidate_number' not in columns:
                # Migrate old table structure
                conn.execute("ALTER TABLE prompt_candidates RENAME TO prompt_candidates_old")
                conn.execute("""
                    CREATE TABLE prompt_candidates (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        optimization_id TEXT NOT NULL,
                        candidate_number INTEGER NOT NULL,
                        prompt_text TEXT NOT NULL,
                        model_response TEXT,
                        score REAL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (optimization_id) REFERENCES optimizations (id)
                    )
                """)
                # Copy data with column mapping
                conn.execute("""
                    INSERT INTO prompt_candidates (optimization_id, candidate_number, prompt_text, score, created_at)
                    SELECT optimization_id, 
                           CAST(SUBSTR(iteration, INSTR(iteration, '_') + 1) AS INTEGER) as candidate_number,
                           user_prompt as prompt_text, 
                           score, 
                           timestamp as created_at
                    FROM prompt_candidates_old
                """)
                conn.execute("DROP TABLE prompt_candidates_old")
            elif 'model_response' not in columns:
                # Add model_response column if missing
                conn.execute("ALTER TABLE prompt_candidates ADD COLUMN model_response TEXT")
        except sqlite3.OperationalError:
            # Table doesn't exist yet or migration not needed
            pass
        
        # Metrics table
        conn.execute("""
            CREATE TABLE IF NOT EXISTS metrics (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                description TEXT,
                dataset_format TEXT NOT NULL,
                scoring_criteria TEXT NOT NULL,
                generated_code TEXT NOT NULL,
                natural_language_input TEXT,
                created TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_used TIMESTAMP,
                usage_count INTEGER DEFAULT 0
            )
        """)
        
        conn.commit()
        # Don't close the connection - keep it for seed_initial_data()
        print(f"✅ Database initialized: {self.db_path}")
    
    def seed_initial_data(self):
        """Add initial sample data if tables are empty"""
        conn = self.conn  # Use the persistent connection
        
        # Check if we already have data (check all tables)
        datasets_count = conn.execute("SELECT COUNT(*) FROM datasets").fetchone()[0]
        prompts_count = conn.execute("SELECT COUNT(*) FROM prompts").fetchone()[0]
        optimizations_count = conn.execute("SELECT COUNT(*) FROM optimizations").fetchone()[0]
        
        if datasets_count > 0 or prompts_count > 0 or optimizations_count > 0:
            # Don't close - keep connection alive
            print("✅ Database already contains data, skipping initial seed")
            return  # Data already exists, don't reseed
        
        print("📊 Database is empty, adding initial sample data...")
        
        # Insert sample datasets
        datasets = [
            {
                "id": "dataset_1",
                "name": "Customer Support Emails",
                "type": "CSV",
                "size": "2.3 MB",
                "rows": 1250,
                "created": "2024-01-15",
                "status": "Ready"
            },
            {
                "id": "dataset_2",
                "name": "Product Reviews",
                "type": "JSON",
                "size": "5.1 MB",
                "rows": 3400,
                "created": "2024-01-10",
                "status": "Processing"
            }
        ]
        
        for dataset in datasets:
            conn.execute("""
                INSERT INTO datasets (id, name, dataset_type, size, rows, created, status)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                dataset["id"], dataset["name"], dataset["type"], 
                dataset["size"], dataset["rows"], dataset["created"], dataset["status"]
            ))
        
        # Insert sample prompts
        prompts = [
            {
                "id": "prompt_1",
                "name": "Email Classification Prompt",
                "type": "System + User",
                "variables": ["email_content", "categories"],
                "created": "2024-01-15",
                "last_used": "2024-01-20",
                "performance": "85%"
            },
            {
                "id": "prompt_2",
                "name": "Sentiment Analysis Prompt",
                "type": "User Only",
                "variables": ["text_input"],
                "created": "2024-01-12",
                "last_used": "2024-01-18",
                "performance": "92%"
            }
        ]
        
        for prompt in prompts:
            conn.execute("""
                INSERT INTO prompts (id, name, prompt_type, variables, created, last_used, performance)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                prompt["id"], prompt["name"], prompt["type"],
                json.dumps(prompt["variables"]), prompt["created"], 
                prompt["last_used"], prompt["performance"]
            ))
        
        # Insert sample optimizations
        optimizations = [
            {
                "id": "opt_1",
                "name": "Email Classification Optimization",
                "prompt": "Email Classification Prompt",
                "dataset": "Customer Support Emails",
                "status": "Completed",
                "progress": 100,
                "improvement": "+12%",
                "started": "2024-01-20 10:30",
                "completed": "2024-01-20 11:45"
            },
            {
                "id": "opt_2",
                "name": "Sentiment Analysis Optimization",
                "prompt": "Sentiment Analysis Prompt",
                "dataset": "Product Reviews",
                "status": "Running",
                "progress": 65,
                "improvement": "+8%",
                "started": "2024-01-21 09:15",
                "completed": "In Progress"
            }
        ]
        
        for opt in optimizations:
            conn.execute("""
                INSERT INTO optimizations (id, name, prompt, dataset, status, progress, improvement, started, completed)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                opt["id"], opt["name"], opt["prompt"], opt["dataset"],
                opt["status"], opt["progress"], opt["improvement"], 
                opt["started"], opt["completed"]
            ))
        
        # Insert sample metrics
        metrics = [
            {
                "id": "accuracy_metric_1",
                "name": "Accuracy Score",
                "description": "Measures exact match accuracy between predicted and expected outputs",
                "dataset_format": "JSON",
                "scoring_criteria": "Exact string match with partial credit for similarity",
                "generated_code": '''
class AccuracyMetric(MetricAdapter):
    def apply(self, y_pred, y_true):
        try:
            import json
            import re
            
            # Parse JSON from prediction if needed
            if isinstance(y_pred, str):
                json_match = re.search(r'\\{.*\\}', y_pred)
                if json_match:
                    try:
                        pred_data = json.loads(json_match.group())
                        y_pred = pred_data.get('answer', y_pred)
                    except:
                        pass
            
            # Simple string comparison
            pred_str = str(y_pred).strip().lower()
            true_str = str(y_true).strip().lower()
            
            # Exact match
            if pred_str == true_str:
                return 1.0
            
            # Partial match
            if pred_str in true_str or true_str in pred_str:
                return 0.7
            
            # No match
            return 0.0
            
        except Exception as e:
            print(f"Metric evaluation error: {e}")
            return 0.0
''',
                "natural_language_input": "Measure how accurately the model predicts the correct answer"
            },
            {
                "id": "relevance_metric_1", 
                "name": "Relevance Score",
                "description": "Evaluates how relevant the response is to the input query",
                "dataset_format": "JSON",
                "scoring_criteria": "Semantic relevance and topic alignment",
                "generated_code": '''
class RelevanceMetric(MetricAdapter):
    def apply(self, y_pred, y_true):
        try:
            import json
            import re
            
            # Extract text from JSON if needed
            pred_text = str(y_pred).lower()
            true_text = str(y_true).lower()
            
            # Simple keyword overlap scoring
            pred_words = set(re.findall(r'\\w+', pred_text))
            true_words = set(re.findall(r'\\w+', true_text))
            
            if not true_words:
                return 0.0
                
            overlap = len(pred_words.intersection(true_words))
            total = len(true_words)
            
            return min(overlap / total, 1.0)
            
        except Exception as e:
            print(f"Relevance metric error: {e}")
            return 0.0
''',
                "natural_language_input": "Score how relevant the response is to the question"
            }
        ]
        
        for metric in metrics:
            conn.execute("""
                INSERT INTO metrics (id, name, description, dataset_format, scoring_criteria, 
                                   generated_code, natural_language_input, created)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                metric["id"], metric["name"], metric["description"], 
                metric["dataset_format"], metric["scoring_criteria"],
                metric["generated_code"], metric["natural_language_input"],
                "2024-01-15"
            ))

        conn.commit()
        # Don't close - keep connection alive for the app
        print("✅ Initial sample data inserted")
    
    # Dataset operations
    def get_datasets(self) -> List[Dict]:
        """Get all datasets"""
        conn = sqlite3.connect(self.db_path, check_same_thread=False)
        cursor = conn.execute("SELECT * FROM datasets ORDER BY created_at DESC")
        
        datasets = []
        for row in cursor.fetchall():
            datasets.append({
                "id": row[0],
                "name": row[1],
                "type": row[2],  # dataset_type from database
                "size": row[3],
                "rows": row[4],
                "created": row[5],
                "status": row[6]
            })
        
        conn.close()
        return datasets
    
    def get_dataset(self, dataset_identifier: str) -> Optional[Dict]:
        """Get a single dataset by ID or name"""
        conn = sqlite3.connect(self.db_path, check_same_thread=False)
        
        # Try by ID first, then by name
        cursor = conn.execute("SELECT * FROM datasets WHERE id = ? OR name = ?", (dataset_identifier, dataset_identifier))
        row = cursor.fetchone()
        
        if row:
            # Get the actual content from file - try multiple naming patterns
            possible_paths = [
                f"uploads/{row[1]}_{row[0]}.jsonl",  # name_id.jsonl
                f"uploads/{row[0]}.jsonl",           # id.jsonl
                f"uploads/{row[1]}.jsonl"            # name.jsonl
            ]
            
            # Also try pattern matching for generated files
            import os
            import glob
            if os.path.exists("uploads/"):
                # Look for files containing the dataset name or ID
                pattern_files = []
                pattern_files.extend(glob.glob(f"uploads/*{row[0]}*.jsonl"))
                pattern_files.extend(glob.glob(f"uploads/*{row[1].replace(' ', '_')}*.jsonl"))
                possible_paths.extend(pattern_files)
            
            content = ""
            file_found = False
            for file_path in possible_paths:
                try:
                    with open(file_path, 'r') as f:
                        content = f.read()
                        file_found = True
                        print(f"✅ Found dataset file: {file_path}")
                        break
                except:
                    continue
            
            if not file_found:
                # Log available files for debugging
                import os
                try:
                    available_files = os.listdir("uploads/")
                    print(f"❌ Dataset file not found. Available files: {available_files}")
                except:
                    print(f"❌ Dataset file not found and uploads directory not accessible")
            
            conn.close()
            return {
                "id": row[0],
                "name": row[1],
                "type": row[2],
                "size": row[3],
                "rows": row[4],
                "created": row[5],
                "status": row[6],
                "content": content
            }
        
        conn.close()
        return None
    
    def update_dataset_name(self, dataset_id: str, name: str) -> bool:
        """Update a dataset name"""
        with self.get_connection() as conn:
            cursor = conn.execute("""
                UPDATE datasets 
                SET name = ?, updated_at = ?
                WHERE id = ?
            """, (name, datetime.now().isoformat(), dataset_id))
            
            return cursor.rowcount > 0

    def delete_dataset(self, dataset_id: str) -> bool:
        """Delete a dataset"""
        conn = self.get_connection()
        cursor = conn.execute("DELETE FROM datasets WHERE id = ?", (dataset_id,))
        deleted = cursor.rowcount > 0
        conn.commit()
        conn.close()
        return deleted
    
    # Prompt operations
    def get_prompts(self) -> List[Dict]:
        """Get all prompts"""
        conn = sqlite3.connect(self.db_path, check_same_thread=False)
        cursor = conn.execute("SELECT * FROM prompts ORDER BY created_at DESC")
        
        prompts = []
        for row in cursor.fetchall():
            prompts.append({
                "id": row[0],
                "name": row[1],
                "type": row[2],  # prompt_type from database
                "variables": json.loads(row[3]) if row[3] else [],
                "created": row[4],
                "last_used": row[5],
                "performance": row[6]
            })
        
        conn.close()
        return prompts
    
    def get_prompt(self, prompt_identifier: str) -> Optional[Dict]:
        """Get a single prompt by ID or name"""
        conn = sqlite3.connect(self.db_path, check_same_thread=False)
        
        # Try by ID first, then by name
        cursor = conn.execute("SELECT * FROM prompts WHERE id = ? OR name = ?", (prompt_identifier, prompt_identifier))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return {
                "id": row[0],
                "name": row[1],
                "type": row[2],
                "variables": json.loads(row[3]) if row[3] else {},  # Parse JSON properly
                "created": row[4],
                "last_used": row[5],
                "performance": row[6]
            }
        return None
    
    def update_prompt(self, prompt_id: str, name: str, system_prompt: str, user_prompt: str) -> bool:
        """Update a prompt"""
        with self.get_connection() as conn:
            # Determine prompt type
            if system_prompt and user_prompt:
                prompt_type = "System + User"
            elif system_prompt:
                prompt_type = "System Only"
            elif user_prompt:
                prompt_type = "User Only"
            else:
                return False
            
            # Store prompts as JSON in variables field
            variables = json.dumps({
                "system_prompt": system_prompt,
                "user_prompt": user_prompt
            })
            
            cursor = conn.execute("""
                UPDATE prompts 
                SET name = ?, prompt_type = ?, variables = ?, last_used = ?
                WHERE id = ?
            """, (name, prompt_type, variables, datetime.now().isoformat(), prompt_id))
            
            return cursor.rowcount > 0

    def delete_prompt(self, prompt_id: str) -> bool:
        """Delete a prompt"""
        conn = self.get_connection()
        cursor = conn.execute("DELETE FROM prompts WHERE id = ?", (prompt_id,))
        deleted = cursor.rowcount > 0
        conn.commit()
        conn.close()
        return deleted
    
    # === METRICS OPERATIONS ===
    
    def create_metric(self, name: str, description: str, dataset_format: str, 
                     scoring_criteria: str, generated_code: str, 
                     natural_language_input: str = None) -> str:
        """Create a new metric"""
        import uuid
        metric_id = f"metric_{uuid.uuid4().hex[:8]}"
        
        conn = sqlite3.connect(self.db_path, check_same_thread=False)
        conn.execute("""
            INSERT INTO metrics (id, name, description, dataset_format, scoring_criteria, 
                               generated_code, natural_language_input)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (metric_id, name, description, dataset_format, scoring_criteria, 
              generated_code, natural_language_input))
        conn.commit()
        conn.close()
        return metric_id
    
    def get_metrics(self) -> List[Dict]:
        """Get all metrics"""
        conn = sqlite3.connect(self.db_path, check_same_thread=False)
        cursor = conn.execute("SELECT * FROM metrics ORDER BY created DESC")
        rows = cursor.fetchall()
        conn.close()
        
        return [{
            "id": row[0],
            "name": row[1],
            "description": row[2],
            "dataset_format": row[3],
            "scoring_criteria": row[4],
            "generated_code": row[5],
            "natural_language_input": row[6],
            "created": row[7],
            "last_used": row[8],
            "usage_count": row[9]
        } for row in rows]
    
    def get_metric(self, metric_id: str) -> Optional[Dict]:
        """Get a single metric by ID"""
        conn = sqlite3.connect(self.db_path, check_same_thread=False)
        cursor = conn.execute("SELECT * FROM metrics WHERE id = ?", (metric_id,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return {
                "id": row[0],
                "name": row[1],
                "description": row[2],
                "dataset_format": row[3],
                "scoring_criteria": row[4],
                "generated_code": row[5],
                "natural_language_input": row[6],
                "created": row[7],
                "last_used": row[8],
                "usage_count": row[9]
            }
        return None
    
    def update_metric_usage(self, metric_id: str):
        """Update metric usage statistics"""
        conn = sqlite3.connect(self.db_path, check_same_thread=False)
        conn.execute("""
            UPDATE metrics 
            SET usage_count = usage_count + 1, last_used = CURRENT_TIMESTAMP 
            WHERE id = ?
        """, (metric_id,))
        conn.commit()
        conn.close()
    
    def delete_metric(self, metric_id: str) -> bool:
        """Delete a metric"""
        conn = sqlite3.connect(self.db_path, check_same_thread=False)
        cursor = conn.execute("DELETE FROM metrics WHERE id = ?", (metric_id,))
        deleted = cursor.rowcount > 0
        conn.commit()
        conn.close()
        return deleted
    
    def get_metric_by_id(self, metric_id: str) -> Dict:
        """Get a single metric by ID"""
        conn = sqlite3.connect(self.db_path, check_same_thread=False)
        cursor = conn.execute("SELECT * FROM metrics WHERE id = ?", (metric_id,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return {
                "id": row[0],
                "name": row[1],
                "description": row[2],
                "dataset_format": row[3],
                "scoring_criteria": row[4],
                "generated_code": row[5],
                "natural_language_input": row[6],
                "created": row[7],
                "usage_count": row[8],
                "last_used": row[9]
            }
        return None
    
    def update_metric(self, metric_id: str, name: str, description: str, generated_code: str, natural_language_input: str) -> bool:
        """Update an existing metric"""
        conn = sqlite3.connect(self.db_path, check_same_thread=False)
        cursor = conn.execute("""
            UPDATE metrics 
            SET name = ?, description = ?, generated_code = ?, natural_language_input = ?
            WHERE id = ?
        """, (name, description, generated_code, natural_language_input, metric_id))
        
        updated = cursor.rowcount > 0
        conn.commit()
        conn.close()
        return updated
    
    # Optimization operations
    def get_optimizations(self) -> List[Dict]:
        """Get all optimizations"""
        conn = sqlite3.connect(self.db_path, check_same_thread=False)
        cursor = conn.execute("SELECT * FROM optimizations ORDER BY created_at DESC")
        
        optimizations = []
        for row in cursor.fetchall():
            optimizations.append({
                "id": row[0],
                "name": row[1],
                "prompt": row[2],
                "dataset": row[3],
                "status": row[4],
                "progress": row[5],
                "improvement": row[6],
                "started": row[7],
                "completed": row[8]
            })
        
        conn.close()
        return optimizations
    
    def delete_optimization(self, optimization_id: str) -> bool:
        """Delete an optimization"""
        conn = sqlite3.connect(self.db_path, check_same_thread=False)
        cursor = conn.execute("DELETE FROM optimizations WHERE id = ?", (optimization_id,))
        deleted = cursor.rowcount > 0
        conn.commit()
        conn.close()
        return deleted
    
    def update_optimization_status(self, optimization_id: str, status: str, progress: int = None, improvement: str = None) -> bool:
        """Update optimization status and progress"""
        conn = sqlite3.connect(self.db_path, check_same_thread=False)
        
        update_parts = ["status = ?"]
        params = [status]
        
        if progress is not None:
            update_parts.append("progress = ?")
            params.append(progress)
            
        if improvement is not None:
            update_parts.append("improvement = ?")
            params.append(improvement)
            
        if status == "Completed":
            update_parts.append("completed = ?")
            params.append(datetime.now().strftime("%Y-%m-%d %H:%M"))
            
        params.append(optimization_id)
        
        query = f"UPDATE optimizations SET {', '.join(update_parts)} WHERE id = ?"
        cursor = conn.execute(query, params)
        updated = cursor.rowcount > 0
        conn.commit()
        conn.close()
        return updated
    
    def get_optimization_by_id(self, optimization_id: str) -> Optional[Dict]:
        """Get a specific optimization by ID"""
        conn = sqlite3.connect(self.db_path, check_same_thread=False)
        cursor = conn.execute("SELECT * FROM optimizations WHERE id = ?", (optimization_id,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return {
                "id": row[0],
                "name": row[1],
                "prompt": row[2],
                "dataset": row[3],
                "status": row[4],
                "progress": row[5],
                "improvement": row[6],
                "started": row[7],
                "completed": row[8],
                "metric_id": row[10] if len(row) > 10 else None  # metric_id is the 11th column (index 10)
            }
        return None
    
    def save_prompt_candidates(self, optimization_id: str, candidates: list):
        """Save prompt candidates for an optimization"""
        conn = sqlite3.connect(self.db_path, check_same_thread=False)
        
        # Clear existing candidates for this optimization
        conn.execute("DELETE FROM prompt_candidates WHERE optimization_id = ?", (optimization_id,))
        
        # Insert new candidates
        for candidate in candidates:
            conn.execute("""
                INSERT INTO prompt_candidates (optimization_id, candidate_number, prompt_text, score)
                VALUES (?, ?, ?, ?)
            """, (
                optimization_id,
                candidate['candidate_number'],
                candidate['prompt_text'],
                candidate['score']
            ))
        
        conn.commit()
        conn.close()

    def get_prompt_candidates(self, optimization_id: str) -> list:
        """Get prompt candidates for an optimization"""
        conn = sqlite3.connect(self.db_path, check_same_thread=False)
        cursor = conn.execute("""
            SELECT candidate_number, prompt_text, model_response, score 
            FROM prompt_candidates 
            WHERE optimization_id = ? 
            ORDER BY candidate_number
        """, (optimization_id,))
        
        candidates = []
        for row in cursor.fetchall():
            candidates.append({
                'candidate_number': row[0],
                'prompt_text': row[1],
                'model_response': row[2],
                'score': row[3]
            })
        
        conn.close()
        return candidates
    
    def delete_optimization(self, optimization_id: str) -> bool:
        """Delete an optimization and clean up all related files"""
        import os
        import shutil
        from pathlib import Path
        
        try:
            # Delete from database
            conn = self.get_connection()
            
            # Delete optimization logs
            conn.execute("DELETE FROM optimization_logs WHERE optimization_id = ?", (optimization_id,))
            
            # Delete prompt candidates
            conn.execute("DELETE FROM prompt_candidates WHERE optimization_id = ?", (optimization_id,))
            
            # Delete optimization record
            cursor = conn.execute("DELETE FROM optimizations WHERE id = ?", (optimization_id,))
            
            conn.commit()
            conn.close()
            
            if cursor.rowcount == 0:
                return False  # Optimization not found
            
            # Clean up temp dataset file
            temp_dataset_file = f"data/temp_dataset_{optimization_id}.jsonl"
            if os.path.exists(temp_dataset_file):
                os.remove(temp_dataset_file)
                print(f"🗑️ Cleaned up temp dataset: {temp_dataset_file}")
            
            # Clean up optimized prompts directory
            prompts_dir = Path(f"optimized_prompts/{optimization_id}")
            if prompts_dir.exists():
                shutil.rmtree(prompts_dir)
                print(f"🗑️ Cleaned up prompts directory: {prompts_dir}")
            
            print(f"✅ Successfully deleted optimization: {optimization_id}")
            return True
            
        except Exception as e:
            print(f"❌ Error deleting optimization {optimization_id}: {e}")
            return False

    def create_optimization(self, name: str, prompt_id: str, dataset_id: str, metric_id: str = None) -> str:
        """Create a new optimization run with optional metric"""
        import uuid
        optimization_id = f"opt_{uuid.uuid4().hex[:8]}"
        
        # Get prompt and dataset names
        prompt = next((p for p in self.get_prompts() if p["id"] == prompt_id), None)
        dataset = next((d for d in self.get_datasets() if d["id"] == dataset_id), None)
        
        if not prompt or not dataset:
            raise ValueError("Prompt or dataset not found")
        
        conn = sqlite3.connect(self.db_path, check_same_thread=False)
        conn.execute("""
            INSERT INTO optimizations (id, name, prompt, dataset, metric_id, status, progress, improvement, started, completed)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            optimization_id, name, prompt_id, dataset["name"], metric_id,  # Store prompt_id, not prompt["name"]
            "Starting", 0, "0%", datetime.now().strftime("%Y-%m-%d %H:%M"), "In Progress"
        ))
        conn.commit()
        conn.close()
        return optimization_id
    
    def create_dataset(self, name: str, file_type: str, file_size: str, row_count: int, file_path: str = None) -> str:
        """Create a new dataset"""
        import uuid
        dataset_id = f"dataset_{uuid.uuid4().hex[:8]}"
        
        conn = self.get_connection()
        conn.execute("""
            INSERT INTO datasets (id, name, dataset_type, size, rows, created, status)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            dataset_id, name, file_type, file_size, row_count,
            datetime.now().strftime("%Y-%m-%d"), "Ready"
        ))
        conn.commit()
        conn.close()
        return dataset_id
    
    def get_dataset_file_path(self, dataset_id: str) -> str:
        """Get the file path for a dataset"""
        datasets = self.get_datasets()
        dataset = next((d for d in datasets if d["id"] == dataset_id), None)
        if dataset:
            # Check multiple possible file path patterns
            from pathlib import Path
            
            # Pattern 1: name_datasetid.extension
            safe_name = dataset["name"].replace(" ", "_").lower()
            extension = ".csv" if dataset["type"] == "CSV" else ".jsonl"
            patterns = [
                f"uploads/{safe_name}_{dataset_id}{extension}",
                f"uploads/{dataset['name']}_{dataset_id}{extension}",
                f"uploads/{dataset_id}{extension}",
                f"uploads/{dataset['name']}{extension}"
            ]
            
            # Try each pattern
            for pattern in patterns:
                if Path(pattern).exists():
                    return pattern
            
            # If no exact match, look for any file containing the dataset_id
            uploads_dir = Path("uploads")
            if uploads_dir.exists():
                for file_path in uploads_dir.glob("*"):
                    if dataset_id in file_path.name:
                        return str(file_path)
        
        return None
    
    def add_prompt_candidate(self, optimization_id: str, candidate_number: int, prompt_text: str, model_response: str = None, score: float = None):
        """Add a prompt candidate to track optimization attempts"""
        conn = sqlite3.connect(self.db_path, check_same_thread=False)
        conn.execute("""
            INSERT INTO prompt_candidates (optimization_id, candidate_number, prompt_text, model_response, score)
            VALUES (?, ?, ?, ?, ?)
        """, (optimization_id, candidate_number, prompt_text, model_response, score))
        conn.commit()
        conn.close()
    
    def get_optimization(self, optimization_id: str):
        """Get a single optimization by ID"""
        conn = sqlite3.connect(self.db_path, check_same_thread=False)
        cursor = conn.execute("""
            SELECT id, name, prompt, dataset, metric_id, status, progress, started, completed
            FROM optimizations 
            WHERE id = ?
        """, (optimization_id,))
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return {
                "id": row[0],
                "name": row[1], 
                "prompt": row[2],
                "dataset": row[3],
                "metric_id": row[4],
                "status": row[5],
                "progress": row[6],
                "started": row[7],
                "completed": row[8]
            }
        return None





    def add_optimization_log(self, optimization_id: str, log_type: str, message: str, data: dict = None):
        """Add a log entry for an optimization"""
        conn = sqlite3.connect(self.db_path, check_same_thread=False)
        conn.execute("""
            INSERT INTO optimization_logs (optimization_id, timestamp, log_type, message, data)
            VALUES (?, ?, ?, ?, ?)
        """, (
            optimization_id,
            datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3],  # Include milliseconds
            log_type,
            message,
            json.dumps(data) if data else None
        ))
        conn.commit()
        conn.close()
    
    def get_optimization_logs(self, optimization_id: str):
        """Get all logs for an optimization"""
        conn = sqlite3.connect(self.db_path, check_same_thread=False)  # Fresh connection
        cursor = conn.execute("""
            SELECT timestamp, log_type, message, data
            FROM optimization_logs 
            WHERE optimization_id = ?
            ORDER BY timestamp ASC
        """, (optimization_id,))
        
        logs = []
        for row in cursor.fetchall():
            log_data = None
            if row[3]:  # data column
                try:
                    log_data = json.loads(row[3])
                except:
                    log_data = None
                    
            logs.append({
                "timestamp": row[0],
                "log_type": row[1],
                "message": row[2],
                "data": log_data
            })
        
        conn.close()
        return logs

    def create_prompt(self, name: str, system_prompt: str = None, user_prompt: str = None) -> str:
        """Create a new prompt"""
        import uuid
        prompt_id = f"prompt_{uuid.uuid4().hex[:8]}"
        
        # Determine prompt type
        if system_prompt and user_prompt:
            prompt_type = "System + User"
        elif system_prompt:
            prompt_type = "System Only"
        elif user_prompt:
            prompt_type = "User Only"
        else:
            raise ValueError("At least one prompt (system or user) must be provided")
        
        # For now, we'll store the prompts as JSON in variables field
        # In a real implementation, you'd have separate fields or tables
        variables = json.dumps({
            "system_prompt": system_prompt,
            "user_prompt": user_prompt
        })
        
        conn = self.get_connection()
        conn.execute("""
            INSERT INTO prompts (id, name, prompt_type, variables, created, last_used, performance)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            prompt_id, name, prompt_type, variables,
            datetime.now().strftime("%Y-%m-%d"), "Never", "Not tested"
        ))
        conn.commit()
        conn.close()
        return prompt_id
    
    def reset_database(self):
        """Reset database to initial state (for development)"""
        conn = sqlite3.connect(self.db_path, check_same_thread=False)
        conn.execute("DELETE FROM datasets")
        conn.execute("DELETE FROM prompts")
        conn.execute("DELETE FROM optimizations")
        conn.execute("DELETE FROM prompt_candidates")
        conn.commit()
        conn.close()
        
        # Reinitialize with fresh connection
        self.init_database()
        print("✅ Database reset to initial state")

# Global database instance
db = Database()
