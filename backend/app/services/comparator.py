# Comparator - compares parsed code vs docs to find missing/outdated documentation

from typing import Dict, List, Any
from app.models.schemas import DiscrepancyReport, DiscrepancyType


class Comparator:
    """
    Service for comparing code and documentation structures
    to identify inconsistencies and discrepancies.
    """
    
    def __init__(self):
        """Initialize the comparator."""
        self.discrepancies: List[DiscrepancyReport] = []
    
    def compare(
        self, 
        code_data: Dict[str, Any], 
        doc_data: Dict[str, Any]
    ) -> List[DiscrepancyReport]:
        """
        Compare code and documentation data.
        
        Args:
            code_data: Parsed code structure
            doc_data: Parsed documentation structure
            
        Returns:
            List of detected discrepancies
        """
        self.discrepancies = []
        
        # Compare functions
        if "functions" in code_data and "api_references" in doc_data:
            self._compare_functions(
                code_data["functions"], 
                doc_data["api_references"]
            )
        
        # TODO: Add more comparison strategies
        # - Compare class methods with documented APIs
        # - Check parameter types
        # - Validate return types
        # - Check for deprecated functions
        
        return self.discrepancies
    
    def _compare_functions(
        self, 
        code_functions: List[Dict], 
        doc_functions: List[Dict]
    ) -> None:
        """
        Compare function definitions in code vs documentation.
        
        Args:
            code_functions: Functions extracted from code
            doc_functions: Functions referenced in documentation
        """
        code_func_names = {f["name"] for f in code_functions}
        doc_func_names = {f["name"] for f in doc_functions}
        
        # Find functions in code but not documented
        undocumented = code_func_names - doc_func_names
        for func_name in undocumented:
            func = next(f for f in code_functions if f["name"] == func_name)
            self.discrepancies.append(
                DiscrepancyReport(
                    type=DiscrepancyType.MISSING_DOCUMENTATION,
                    severity="medium",
                    location=f"Line {func.get('line_number', 'unknown')}",
                    description=f"Function '{func_name}' is not documented",
                    code_snippet=f"def {func_name}(...)",
                    suggestion=f"Add documentation for function '{func_name}'"
                )
            )
        
        # Find documented functions not in code
        obsolete_docs = doc_func_names - code_func_names
        for func_name in obsolete_docs:
            func = next(f for f in doc_functions if f["name"] == func_name)
            self.discrepancies.append(
                DiscrepancyReport(
                    type=DiscrepancyType.OUTDATED_EXAMPLE,
                    severity="high",
                    location=f"Documentation line {func.get('line', 'unknown')}",
                    description=f"Documented function '{func_name}' not found in code",
                    doc_snippet=f"`{func_name}(...)`",
                    suggestion=f"Remove or update documentation for '{func_name}'"
                )
            )
