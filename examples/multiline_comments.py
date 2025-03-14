#!/usr/bin/env python3

"""
This is a module docstring.
It spans multiple lines.
All of these lines should be counted as comments.
"""

# This is a single line comment

def example_function():
    """
    This is a function docstring.
    It also spans multiple lines.
    These should all be counted as comments too.
    """
    # Another single line comment
    x = 1  # Inline comment
    y = 2
    
    '''
    This is a multiline comment using single quotes.
    It should also be counted as comments.
    '''
    
    return x + y

class ExampleClass:
    """
    This is a class docstring.
    It should be counted as comments.
    """
    
    def __init__(self):
        self.value = 42
        
    def get_value(self):
        """Return the value."""
        return self.value 