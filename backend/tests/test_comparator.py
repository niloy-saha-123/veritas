# Test suite for comparator service - validates discrepancy detection logic

"""Tests for the Comparator service."""

import pytest
from app.services.comparator import Comparator
from app.models.schemas import DiscrepancyType


class TestComparator:
    """Test cases for Comparator."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.comparator = Comparator()
    
    def test_detect_missing_documentation(self):
        """Test detection of undocumented functions."""
        code_data = {
            "functions": [
                {"name": "documented_func", "line_number": 1},
                {"name": "undocumented_func", "line_number": 5}
            ]
        }
        
        doc_data = {
            "api_references": [
                {"name": "documented_func", "line": 10}
            ]
        }
        
        discrepancies = self.comparator.compare(code_data, doc_data)
        
        assert len(discrepancies) == 1
        assert discrepancies[0].type == DiscrepancyType.MISSING_DOCUMENTATION
        assert "undocumented_func" in discrepancies[0].description
    
    def test_detect_obsolete_documentation(self):
        """Test detection of documentation for non-existent functions."""
        code_data = {
            "functions": [
                {"name": "current_func", "line_number": 1}
            ]
        }
        
        doc_data = {
            "api_references": [
                {"name": "current_func", "line": 10},
                {"name": "old_func", "line": 20}
            ]
        }
        
        discrepancies = self.comparator.compare(code_data, doc_data)
        
        assert len(discrepancies) == 1
        assert discrepancies[0].type == DiscrepancyType.OUTDATED_EXAMPLE
        assert "old_func" in discrepancies[0].description
    
    def test_no_discrepancies(self):
        """Test when code and docs are in sync."""
        code_data = {
            "functions": [
                {"name": "func1", "line_number": 1},
                {"name": "func2", "line_number": 5}
            ]
        }
        
        doc_data = {
            "api_references": [
                {"name": "func1", "line": 10},
                {"name": "func2", "line": 20}
            ]
        }
        
        discrepancies = self.comparator.compare(code_data, doc_data)
        
        assert len(discrepancies) == 0
