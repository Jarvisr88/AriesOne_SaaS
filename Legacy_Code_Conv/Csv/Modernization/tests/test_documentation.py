"""
Documentation tests for CSV module
"""
import pytest
import inspect
from typing import get_type_hints
import doctest

from csv_reader import CSVReader, ParseErrorAction
from cached_csv_reader import CachedCSVReader
from csv_validator import CSVValidator, ValidationRule
from csv_profiler import CSVProfiler

def test_docstrings_present():
    """Test presence and quality of docstrings."""
    modules = [CSVReader, CachedCSVReader, CSVValidator, CSVProfiler]
    
    for cls in modules:
        # Class docstring
        assert cls.__doc__ is not None, f"Missing docstring for {cls.__name__}"
        
        # Method docstrings
        for name, method in inspect.getmembers(cls, inspect.isfunction):
            if not name.startswith('_'):  # Skip private methods
                assert method.__doc__ is not None, f"Missing docstring for {cls.__name__}.{name}"
                
def test_type_hints():
    """Test presence and correctness of type hints."""
    modules = [CSVReader, CachedCSVReader, CSVValidator, CSVProfiler]
    
    for cls in modules:
        for name, method in inspect.getmembers(cls, inspect.isfunction):
            if not name.startswith('_'):
                hints = get_type_hints(method)
                assert hints, f"Missing type hints for {cls.__name__}.{name}"
                
def test_examples():
    """Test code examples in docstrings."""
    modules = [CSVReader, CachedCSVReader, CSVValidator, CSVProfiler]
    
    for cls in modules:
        # Run doctests on class
        results = doctest.testmod(inspect.getmodule(cls))
        assert results.failed == 0, f"Doctest failures in {cls.__name__}"
        
def test_parameter_documentation():
    """Test parameter documentation completeness."""
    modules = [CSVReader, CachedCSVReader, CSVValidator, CSVProfiler]
    
    for cls in modules:
        for name, method in inspect.getmembers(cls, inspect.isfunction):
            if not name.startswith('_'):
                doc = method.__doc__
                sig = inspect.signature(method)
                
                # Check each parameter is documented
                for param in sig.parameters:
                    if param != 'self':
                        assert param in doc, f"Parameter {param} not documented in {cls.__name__}.{name}"
                        
def test_return_value_documentation():
    """Test return value documentation."""
    modules = [CSVReader, CachedCSVReader, CSVValidator, CSVProfiler]
    
    for cls in modules:
        for name, method in inspect.getmembers(cls, inspect.isfunction):
            if not name.startswith('_'):
                doc = method.__doc__
                sig = inspect.signature(method)
                
                # Check return value documentation if method returns something
                if sig.return_annotation != inspect.Signature.empty:
                    assert 'Returns:' in doc or 'Return:' in doc, \
                        f"Missing return value documentation in {cls.__name__}.{name}"
                        
def test_exception_documentation():
    """Test exception documentation."""
    modules = [CSVReader, CachedCSVReader, CSVValidator, CSVProfiler]
    
    for cls in modules:
        for name, method in inspect.getmembers(cls, inspect.isfunction):
            if not name.startswith('_'):
                source = inspect.getsource(method)
                doc = method.__doc__
                
                # If method raises exceptions, they should be documented
                if 'raise' in source:
                    assert 'Raises:' in doc, \
                        f"Missing exception documentation in {cls.__name__}.{name}"
                        
def test_usage_examples():
    """Test presence of usage examples."""
    modules = [CSVReader, CachedCSVReader, CSVValidator, CSVProfiler]
    
    for cls in modules:
        doc = cls.__doc__
        assert 'Example:' in doc or 'Examples:' in doc, \
            f"Missing usage examples in {cls.__name__}"
            
def test_api_reference():
    """Test API reference documentation."""
    modules = [CSVReader, CachedCSVReader, CSVValidator, CSVProfiler]
    
    for cls in modules:
        # Check class documentation
        assert cls.__doc__, f"Missing API reference for {cls.__name__}"
        
        # Check public methods
        for name, method in inspect.getmembers(cls, inspect.isfunction):
            if not name.startswith('_'):
                assert method.__doc__, f"Missing API reference for {cls.__name__}.{name}"
                
                # Check documentation sections
                doc = method.__doc__
                sections = ['Args:', 'Returns:', 'Raises:', 'Example:']
                found_sections = [section for section in sections if section in doc]
                assert found_sections, f"Missing documentation sections in {cls.__name__}.{name}"
