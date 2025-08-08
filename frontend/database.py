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
                status TEXT,
                progress INTEGER DEFAULT 0,
                improvement TEXT,
                started TEXT,
                completed TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
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
                iteration TEXT NOT NULL,
                user_prompt TEXT NOT NULL,
                score REAL,
                timestamp TEXT NOT NULL,
                FOREIGN KEY (optimization_id) REFERENCES optimizations (id)
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
            
            content = ""
            file_found = False
            for file_path in possible_paths:
                try:
                    with open(file_path, 'r') as f:
                        content = f.read()
                        file_found = True
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
                "variables": row[3],  # Keep as string for now
                "created": row[4],
                "last_used": row[5],
                "performance": row[6]
            }
        return None
    
    def delete_prompt(self, prompt_id: str) -> bool:
        """Delete a prompt"""
        conn = self.get_connection()
        cursor = conn.execute("DELETE FROM prompts WHERE id = ?", (prompt_id,))
        deleted = cursor.rowcount > 0
        conn.commit()
        conn.close()
        return deleted
    
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
                "completed": row[8]
            }
        return None
    
    def create_optimization(self, name: str, prompt_id: str, dataset_id: str) -> str:
        """Create a new optimization run"""
        import uuid
        optimization_id = f"opt_{uuid.uuid4().hex[:8]}"
        
        # Get prompt and dataset names
        prompt = next((p for p in self.get_prompts() if p["id"] == prompt_id), None)
        dataset = next((d for d in self.get_datasets() if d["id"] == dataset_id), None)
        
        if not prompt or not dataset:
            raise ValueError("Prompt or dataset not found")
        
        conn = sqlite3.connect(self.db_path, check_same_thread=False)
        conn.execute("""
            INSERT INTO optimizations (id, name, prompt, dataset, status, progress, improvement, started, completed)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            optimization_id, name, prompt["name"], dataset["name"],
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
    
    def add_prompt_candidate(self, optimization_id: str, iteration: str, user_prompt: str, score: float = None):
        """Add a prompt candidate to track optimization attempts"""
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO prompt_candidates (optimization_id, iteration, user_prompt, score, timestamp)
            VALUES (?, ?, ?, ?, ?)
        """, (optimization_id, iteration, user_prompt, score, datetime.now().isoformat()))
        self.conn.commit()
    
    def get_prompt_candidates(self, optimization_id: str):
        """Get all prompt candidates for an optimization"""
        conn = sqlite3.connect(self.db_path, check_same_thread=False)  # Fresh connection
        cursor = conn.execute("""
            SELECT iteration, user_prompt, score, timestamp
            FROM prompt_candidates 
            WHERE optimization_id = ?
            ORDER BY timestamp ASC
        """, (optimization_id,))
        
        candidates = []
        for row in cursor.fetchall():
            candidates.append({
                "iteration": row[0],
                "user_prompt": row[1],
                "score": row[2],
                "timestamp": row[3]
            })
        conn.close()
        return candidates

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
        conn = self.get_connection()
        conn.execute("DELETE FROM datasets")
        conn.execute("DELETE FROM prompts")
        conn.execute("DELETE FROM optimizations")
        conn.commit()
        conn.close()
        self.seed_initial_data()
        print("✅ Database reset to initial state")

# Global database instance
db = Database()
