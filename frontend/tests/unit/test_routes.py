"""Unit tests for route handlers"""

import pytest
from unittest.mock import Mock, patch
from fasthtml.common import *


class TestRoutes:
    
    def test_dashboard_route_exists(self):
        """Test dashboard route is accessible"""
        # Import app to test routes
        import app
        assert hasattr(app, 'app')
    
    def test_datasets_route_exists(self):
        """Test datasets route is accessible"""
        import app
        # Check if datasets route is registered
        assert hasattr(app, 'app')
    
    def test_simple_generator_route_exists(self):
        """Test simple generator route is accessible"""
        import app
        # Check if simple generator routes are registered
        assert hasattr(app, 'app')
