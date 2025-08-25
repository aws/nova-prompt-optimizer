"""
Unit tests for prompt builder database operations
"""

import pytest
import tempfile
import os
import json
from database import Database
from migrations.add_prompt_builder import run_migration


class TestPromptBuilderDatabase:
    """Test prompt builder database operations"""
    
    @pytest.fixture
    def test_db(self):
        """Create a temporary test database"""
        # Create temporary database file
        db_fd, db_path = tempfile.mkstemp(suffix='.db')
        os.close(db_fd)
        
        # Run migration to create tables
        run_migration(db_path)
        
        # Create database instance
        from pathlib import Path
        db = Database(db_path=Path(db_path))
        
        yield db
        
        # Cleanup
        db.conn.close()
        os.unlink(db_path)
    
    def test_create_prompt_template_returns_id(self, test_db):
        """Test that create_prompt_template returns a valid ID"""
        builder_data = {
            "task": "Test task",
            "context": ["Test context"],
            "instructions": ["Test instruction"],
            "response_format": ["Test format"],
            "variables": ["test_var"],
            "metadata": {"author": "test"}
        }
        
        template_id = test_db.create_prompt_template(
            name="Test Template",
            description="Test description",
            builder_data=builder_data
        )
        
        assert template_id is not None
        assert template_id.startswith("template_")
        assert len(template_id) > 10  # Should have UUID suffix
    
    def test_get_prompt_template_returns_correct_data(self, test_db):
        """Test that get_prompt_template returns the correct data"""
        builder_data = {
            "task": "Analyze sentiment",
            "context": ["Customer feedback", "Product reviews"],
            "instructions": ["MUST classify", "DO NOT guess"],
            "response_format": ["JSON format"],
            "variables": ["input_text", "category"],
            "metadata": {"version": "1.0"}
        }
        
        # Create template
        template_id = test_db.create_prompt_template(
            name="Sentiment Analysis",
            description="Analyze customer sentiment",
            builder_data=builder_data
        )
        
        # Retrieve template
        retrieved = test_db.get_prompt_template(template_id)
        
        assert retrieved is not None
        assert retrieved["id"] == template_id
        assert retrieved["name"] == "Sentiment Analysis"
        assert retrieved["description"] == "Analyze customer sentiment"
        assert retrieved["builder_data"]["task"] == "Analyze sentiment"
        assert "Customer feedback" in retrieved["builder_data"]["context"]
        assert "MUST classify" in retrieved["builder_data"]["instructions"]
        assert "JSON format" in retrieved["builder_data"]["response_format"]
        assert "input_text" in retrieved["builder_data"]["variables"]
        assert retrieved["builder_data"]["metadata"]["version"] == "1.0"
    
    def test_get_nonexistent_template_returns_none(self, test_db):
        """Test that get_prompt_template returns None for nonexistent template"""
        result = test_db.get_prompt_template("nonexistent_id")
        assert result is None
    
    def test_list_prompt_templates_pagination(self, test_db):
        """Test that list_prompt_templates supports pagination"""
        # Create multiple templates
        for i in range(5):
            builder_data = {
                "task": f"Task {i}",
                "context": [f"Context {i}"],
                "instructions": [f"Instruction {i}"],
                "response_format": [],
                "variables": [],
                "metadata": {}
            }
            test_db.create_prompt_template(
                name=f"Template {i}",
                description=f"Description {i}",
                builder_data=builder_data
            )
        
        # Test pagination
        page1 = test_db.list_prompt_templates(limit=3, offset=0)
        page2 = test_db.list_prompt_templates(limit=3, offset=3)
        
        assert len(page1) == 3
        assert len(page2) >= 2  # At least 2 more (plus any sample templates)
        
        # Verify no overlap
        page1_ids = {t["id"] for t in page1}
        page2_ids = {t["id"] for t in page2}
        assert len(page1_ids.intersection(page2_ids)) == 0
    
    def test_list_prompt_templates_ordering(self, test_db):
        """Test that list_prompt_templates returns templates in correct order"""
        import time
        
        # Create templates with slight delay to ensure different timestamps
        template_ids = []
        for i in range(3):
            builder_data = {
                "task": f"Task {i}",
                "context": [],
                "instructions": [],
                "response_format": [],
                "variables": [],
                "metadata": {}
            }
            template_id = test_db.create_prompt_template(
                name=f"Template {i}",
                description="",
                builder_data=builder_data
            )
            template_ids.append(template_id)
            time.sleep(0.01)  # Small delay to ensure different timestamps
        
        # List templates
        templates = test_db.list_prompt_templates()
        
        # Find our created templates in the results
        our_templates = [t for t in templates if t["id"] in template_ids]
        
        # Should be ordered by last_modified DESC (most recent first)
        assert len(our_templates) == 3
        assert our_templates[0]["name"] == "Template 2"  # Most recent
        assert our_templates[1]["name"] == "Template 1"
        assert our_templates[2]["name"] == "Template 0"  # Oldest
    
    def test_update_prompt_template_modifies_existing(self, test_db):
        """Test that update_prompt_template modifies existing template"""
        # Create initial template
        initial_data = {
            "task": "Initial task",
            "context": ["Initial context"],
            "instructions": ["Initial instruction"],
            "response_format": [],
            "variables": [],
            "metadata": {}
        }
        
        template_id = test_db.create_prompt_template(
            name="Initial Name",
            description="Initial description",
            builder_data=initial_data
        )
        
        # Update template
        updated_data = {
            "task": "Updated task",
            "context": ["Updated context", "Additional context"],
            "instructions": ["Updated instruction"],
            "response_format": ["JSON format"],
            "variables": ["new_var"],
            "metadata": {"version": "2.0"}
        }
        
        success = test_db.update_prompt_template(
            template_id=template_id,
            name="Updated Name",
            description="Updated description",
            builder_data=updated_data
        )
        
        assert success is True
        
        # Verify update
        retrieved = test_db.get_prompt_template(template_id)
        assert retrieved["name"] == "Updated Name"
        assert retrieved["description"] == "Updated description"
        assert retrieved["builder_data"]["task"] == "Updated task"
        assert len(retrieved["builder_data"]["context"]) == 2
        assert "Additional context" in retrieved["builder_data"]["context"]
        assert "JSON format" in retrieved["builder_data"]["response_format"]
        assert "new_var" in retrieved["builder_data"]["variables"]
        assert retrieved["builder_data"]["metadata"]["version"] == "2.0"
    
    def test_update_nonexistent_template_returns_false(self, test_db):
        """Test that updating nonexistent template returns False"""
        result = test_db.update_prompt_template(
            template_id="nonexistent",
            name="Name",
            description="Description",
            builder_data={}
        )
        assert result is False
    
    def test_delete_prompt_template_removes_record(self, test_db):
        """Test that delete_prompt_template removes the record"""
        # Create template
        builder_data = {
            "task": "Task to delete",
            "context": [],
            "instructions": [],
            "response_format": [],
            "variables": [],
            "metadata": {}
        }
        
        template_id = test_db.create_prompt_template(
            name="Template to Delete",
            description="",
            builder_data=builder_data
        )
        
        # Verify it exists
        assert test_db.get_prompt_template(template_id) is not None
        
        # Delete it
        success = test_db.delete_prompt_template(template_id)
        assert success is True
        
        # Verify it's gone
        assert test_db.get_prompt_template(template_id) is None
    
    def test_delete_nonexistent_template_returns_false(self, test_db):
        """Test that deleting nonexistent template returns False"""
        result = test_db.delete_prompt_template("nonexistent")
        assert result is False
    
    def test_save_builder_session_stores_state(self, test_db):
        """Test that save_builder_session stores session state"""
        builder_data = {
            "task": "Session task",
            "context": ["Session context"],
            "instructions": ["Session instruction"],
            "response_format": [],
            "variables": ["session_var"],
            "metadata": {"session": True}
        }
        
        session_id = test_db.save_builder_session(
            session_name="Test Session",
            template_id=None,
            builder_data=builder_data
        )
        
        assert session_id is not None
        assert session_id.startswith("session_")
    
    def test_load_builder_session_retrieves_state(self, test_db):
        """Test that load_builder_session retrieves correct state"""
        builder_data = {
            "task": "Session task",
            "context": ["Session context"],
            "instructions": ["Session instruction"],
            "response_format": ["Session format"],
            "variables": ["session_var"],
            "metadata": {"test": "session"}
        }
        
        # Save session
        session_id = test_db.save_builder_session(
            session_name="Test Session",
            template_id=None,
            builder_data=builder_data
        )
        
        # Load session
        loaded = test_db.load_builder_session(session_id)
        
        assert loaded is not None
        assert loaded["id"] == session_id
        assert loaded["session_name"] == "Test Session"
        assert loaded["template_id"] is None
        assert loaded["builder_data"]["task"] == "Session task"
        assert "Session context" in loaded["builder_data"]["context"]
        assert "Session instruction" in loaded["builder_data"]["instructions"]
        assert "session_var" in loaded["builder_data"]["variables"]
        assert loaded["builder_data"]["metadata"]["test"] == "session"
    
    def test_load_nonexistent_session_returns_none(self, test_db):
        """Test that loading nonexistent session returns None"""
        result = test_db.load_builder_session("nonexistent")
        assert result is None
    
    def test_list_builder_sessions_returns_recent(self, test_db):
        """Test that list_builder_sessions returns recent sessions"""
        import time
        
        # Create multiple sessions
        session_ids = []
        for i in range(3):
            builder_data = {"task": f"Session {i}"}
            session_id = test_db.save_builder_session(
                session_name=f"Session {i}",
                template_id=None,
                builder_data=builder_data
            )
            session_ids.append(session_id)
            time.sleep(0.01)  # Small delay for different timestamps
        
        # List sessions
        sessions = test_db.list_builder_sessions()
        
        # Find our sessions
        our_sessions = [s for s in sessions if s["id"] in session_ids]
        
        assert len(our_sessions) == 3
        # Should be ordered by last_accessed DESC
        assert our_sessions[0]["session_name"] == "Session 2"  # Most recent
    
    def test_session_with_template_id_association(self, test_db):
        """Test session association with template ID"""
        # Create template first
        template_data = {
            "task": "Template task",
            "context": [],
            "instructions": [],
            "response_format": [],
            "variables": [],
            "metadata": {}
        }
        
        template_id = test_db.create_prompt_template(
            name="Associated Template",
            description="",
            builder_data=template_data
        )
        
        # Create session associated with template
        session_data = {
            "task": "Modified template task",
            "context": ["Added context"],
            "instructions": [],
            "response_format": [],
            "variables": [],
            "metadata": {}
        }
        
        session_id = test_db.save_builder_session(
            session_name="Template Session",
            template_id=template_id,
            builder_data=session_data
        )
        
        # Load session and verify association
        loaded = test_db.load_builder_session(session_id)
        assert loaded["template_id"] == template_id
        
        # Delete template should also delete associated sessions
        test_db.delete_prompt_template(template_id)
        
        # Session should be gone too
        assert test_db.load_builder_session(session_id) is None
    
    def test_json_serialization_handling(self, test_db):
        """Test that complex data structures are properly serialized/deserialized"""
        complex_data = {
            "task": "Complex task with unicode: 测试",
            "context": [
                "Context with special chars: !@#$%^&*()",
                "Multi-line context:\nLine 1\nLine 2"
            ],
            "instructions": [
                "Instruction with quotes: 'single' and \"double\"",
                "Instruction with JSON: {\"key\": \"value\"}"
            ],
            "response_format": [
                "Format with newlines:\n- Item 1\n- Item 2"
            ],
            "variables": ["var_with_underscore", "varWithCamelCase"],
            "metadata": {
                "nested": {
                    "deep": {
                        "value": "test"
                    }
                },
                "array": [1, 2, 3],
                "boolean": True,
                "null_value": None
            }
        }
        
        # Create template with complex data
        template_id = test_db.create_prompt_template(
            name="Complex Template",
            description="Template with complex data",
            builder_data=complex_data
        )
        
        # Retrieve and verify
        retrieved = test_db.get_prompt_template(template_id)
        
        assert retrieved["builder_data"]["task"] == "Complex task with unicode: 测试"
        assert "Context with special chars: !@#$%^&*()" in retrieved["builder_data"]["context"]
        assert "Multi-line context:\nLine 1\nLine 2" in retrieved["builder_data"]["context"]
        assert "Instruction with quotes: 'single' and \"double\"" in retrieved["builder_data"]["instructions"]
        assert retrieved["builder_data"]["metadata"]["nested"]["deep"]["value"] == "test"
        assert retrieved["builder_data"]["metadata"]["array"] == [1, 2, 3]
        assert retrieved["builder_data"]["metadata"]["boolean"] is True
        assert retrieved["builder_data"]["metadata"]["null_value"] is None
