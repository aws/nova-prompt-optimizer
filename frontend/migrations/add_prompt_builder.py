"""
Database migration for Prompt Builder tables
"""

import sqlite3
import json
from datetime import datetime


def create_prompt_builder_tables(db_path: str):
    """Create prompt builder tables in the database"""
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Create prompt_templates table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS prompt_templates (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                description TEXT,
                task TEXT NOT NULL,
                context_items TEXT,  -- JSON array
                instructions TEXT,   -- JSON array
                response_format TEXT, -- JSON array
                variables TEXT,      -- JSON array
                metadata TEXT,       -- JSON object
                created_date TEXT NOT NULL,
                last_modified TEXT NOT NULL,
                created_by TEXT,
                version INTEGER DEFAULT 1
            )
        """)
        
        # Create prompt_builder_sessions table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS prompt_builder_sessions (
                id TEXT PRIMARY KEY,
                template_id TEXT,
                current_state TEXT NOT NULL,  -- JSON object
                created_date TEXT NOT NULL,
                last_accessed TEXT NOT NULL,
                session_name TEXT,
                FOREIGN KEY (template_id) REFERENCES prompt_templates(id)
            )
        """)
        
        # Create indexes for better performance
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_prompt_templates_name 
            ON prompt_templates(name)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_prompt_templates_created_date 
            ON prompt_templates(created_date)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_prompt_builder_sessions_template_id 
            ON prompt_builder_sessions(template_id)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_prompt_builder_sessions_last_accessed 
            ON prompt_builder_sessions(last_accessed)
        """)
        
        conn.commit()
        print("✅ Prompt builder tables created successfully")
        
    except Exception as e:
        conn.rollback()
        print(f"❌ Error creating prompt builder tables: {e}")
        raise
    finally:
        conn.close()


def insert_sample_templates(db_path: str):
    """Insert sample prompt templates for testing"""
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        sample_templates = [
            {
                "id": "template_sentiment_analysis",
                "name": "Customer Sentiment Analysis",
                "description": "Analyze customer feedback sentiment with confidence scoring",
                "task": "Analyze customer feedback sentiment and provide confidence scores",
                "context_items": json.dumps([
                    "Customer support emails and chat logs",
                    "Product review comments from e-commerce platforms",
                    "Social media mentions and feedback"
                ]),
                "instructions": json.dumps([
                    "MUST classify sentiment as positive, negative, or neutral",
                    "DO NOT include personal opinions or bias in analysis",
                    "MUST provide confidence score between 0.0 and 1.0",
                    "Include key phrases that influenced the classification"
                ]),
                "response_format": json.dumps([
                    "JSON format with sentiment, confidence, and key_phrases fields",
                    "Sentiment must be one of: positive, negative, neutral",
                    "Confidence must be a float between 0.0 and 1.0"
                ]),
                "variables": json.dumps(["customer_feedback", "product_name"]),
                "metadata": json.dumps({
                    "category": "sentiment_analysis",
                    "difficulty": "intermediate",
                    "use_cases": ["customer_support", "product_reviews"]
                }),
                "created_date": datetime.now().isoformat(),
                "last_modified": datetime.now().isoformat(),
                "created_by": "system"
            },
            {
                "id": "template_text_classification",
                "name": "General Text Classification",
                "description": "Classify text into predefined categories with reasoning",
                "task": "Classify input text into the most appropriate category from provided options",
                "context_items": json.dumps([
                    "Text classification requirements and guidelines",
                    "Available category definitions and examples",
                    "Classification accuracy and consistency requirements"
                ]),
                "instructions": json.dumps([
                    "MUST select exactly one category from the provided options",
                    "DO NOT create new categories not in the provided list",
                    "MUST provide clear reasoning for the classification decision",
                    "Include confidence level for the classification"
                ]),
                "response_format": json.dumps([
                    "Selected category name and confidence score",
                    "Brief explanation of reasoning behind the classification",
                    "Key text features that influenced the decision"
                ]),
                "variables": json.dumps(["input_text", "available_categories"]),
                "metadata": json.dumps({
                    "category": "text_classification",
                    "difficulty": "beginner",
                    "use_cases": ["content_moderation", "document_routing"]
                }),
                "created_date": datetime.now().isoformat(),
                "last_modified": datetime.now().isoformat(),
                "created_by": "system"
            },
            {
                "id": "template_data_extraction",
                "name": "Structured Data Extraction",
                "description": "Extract structured information from unstructured text",
                "task": "Extract specific data points from unstructured text and format as structured output",
                "context_items": json.dumps([
                    "Data extraction requirements and field definitions",
                    "Expected output format and validation rules",
                    "Handling of missing or ambiguous information"
                ]),
                "instructions": json.dumps([
                    "MUST extract all available information for specified fields",
                    "DO NOT invent or guess information not present in the text",
                    "MUST mark fields as null or empty when information is not available",
                    "Validate extracted data against expected formats"
                ]),
                "response_format": json.dumps([
                    "JSON object with extracted fields as key-value pairs",
                    "Include confidence scores for each extracted field",
                    "Mark uncertain extractions with appropriate flags"
                ]),
                "variables": json.dumps(["input_text", "extraction_fields"]),
                "metadata": json.dumps({
                    "category": "data_extraction",
                    "difficulty": "advanced",
                    "use_cases": ["document_processing", "form_parsing"]
                }),
                "created_date": datetime.now().isoformat(),
                "last_modified": datetime.now().isoformat(),
                "created_by": "system"
            }
        ]
        
        for template in sample_templates:
            cursor.execute("""
                INSERT OR REPLACE INTO prompt_templates 
                (id, name, description, task, context_items, instructions, 
                 response_format, variables, metadata, created_date, last_modified, created_by)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                template["id"], template["name"], template["description"],
                template["task"], template["context_items"], template["instructions"],
                template["response_format"], template["variables"], template["metadata"],
                template["created_date"], template["last_modified"], template["created_by"]
            ))
        
        conn.commit()
        print(f"✅ Inserted {len(sample_templates)} sample templates")
        
    except Exception as e:
        conn.rollback()
        print(f"❌ Error inserting sample templates: {e}")
        raise
    finally:
        conn.close()


def run_migration(db_path: str):
    """Run the complete migration"""
    print("🚀 Running prompt builder migration...")
    create_prompt_builder_tables(db_path)
    insert_sample_templates(db_path)
    print("✅ Prompt builder migration completed successfully!")


if __name__ == "__main__":
    # Run migration on the main database
    import os
    db_path = os.path.join(os.path.dirname(__file__), "..", "nova_optimizer.db")
    run_migration(db_path)
