# tutorio/security/code_validator.py
"""
AST-based code validator for security with enhanced checks
"""

import ast
import re
from typing import Tuple, Set
from .config import SecurityConfig


class SecureCodeValidator:
    """Validates Python code for security vulnerabilities"""
    
    # Additional dangerous functions to check
    DANGEROUS_FUNCTIONS = {
        'exec', 'eval', 'compile', '__import__', 'open', 'breakpoint',
        'globals', 'locals', 'vars', 'getattr', 'setattr', 'delattr',
        'hasattr', 'input', 'raw_input'
    }
    
    # Dangerous attributes that shouldn't be accessed
    DANGEROUS_ATTRIBUTES = {
        '__class__', '__bases__', '__mro__', '__subclasses__',
        '__globals__', '__code__', '__closure__', '__builtins__',
        '__import__', '__loader__', '__spec__'
    }
    
    @staticmethod
    def validate_imports(tree: ast.AST) -> Tuple[bool, str]:
        """Check imports against whitelist"""
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    module_name = alias.name.split('.')[0]
                    if module_name not in SecurityConfig.ALLOWED_IMPORTS:
                        return False, f"Import of '{module_name}' not allowed"
            
            elif isinstance(node, ast.ImportFrom):
                module_name = node.module.split('.')[0] if node.module else ''
                if module_name and module_name not in SecurityConfig.ALLOWED_IMPORTS:
                    return False, f"Import from '{module_name}' not allowed"
        
        return True, "OK"
    
    @staticmethod
    def check_dangerous_patterns(code: str) -> Tuple[bool, str]:
        """Check for dangerous string patterns with improved detection"""
        
        # Check length first
        if len(code) > SecurityConfig.MAX_CODE_LENGTH:
            return False, f"Code exceeds maximum length of {SecurityConfig.MAX_CODE_LENGTH} characters"
        
        # Check for dangerous patterns
        for pattern in SecurityConfig.DANGEROUS_PATTERNS:
            matches = re.findall(pattern, code, re.IGNORECASE)
            if matches:
                return False, f"Dangerous pattern detected: {matches[0]}"
        
        # Additional checks for attribute chains
        attribute_chain_pattern = r'__\w+__\.__\w+__'
        if re.search(attribute_chain_pattern, code):
            return False, "Suspicious attribute chain detected"
        
        # Check for excessive string operations (potential obfuscation)
        if code.count('chr(') > 5 or code.count('ord(') > 5:
            return False, "Excessive use of chr/ord functions detected"
        
        return True, "OK"
    
    @staticmethod
    def validate_ast(code: str) -> Tuple[bool, str]:
        """Parse and validate AST with enhanced security checks"""
        try:
            tree = ast.parse(code)
            
            # Validate imports
            valid, msg = SecureCodeValidator.validate_imports(tree)
            if not valid:
                return False, msg
            
            # Walk the AST
            for node in ast.walk(tree):
                # Check function calls
                if isinstance(node, ast.Call):
                    if isinstance(node.func, ast.Name):
                        if node.func.id in SecureCodeValidator.DANGEROUS_FUNCTIONS:
                            return False, f"Use of {node.func.id}() is forbidden"
                    elif isinstance(node.func, ast.Attribute):
                        # Check for dangerous method calls
                        if node.func.attr in SecureCodeValidator.DANGEROUS_FUNCTIONS:
                            return False, f"Use of {node.func.attr}() is forbidden"
                
                # Check attribute access
                elif isinstance(node, ast.Attribute):
                    if node.attr in SecureCodeValidator.DANGEROUS_ATTRIBUTES:
                        return False, f"Access to {node.attr} is forbidden"
                
                # Check for suspicious operations
                elif isinstance(node, ast.BinOp):
                    if isinstance(node.op, ast.MatMult):
                        if hasattr(node.left, 'id') and hasattr(node.right, 'id'):
                            if node.left.id == '__builtins__' or node.right.id == '__builtins__':
                                return False, "Access to __builtins__ is forbidden"
            
            return True, "Valid AST"
            
        except SyntaxError as e:
            return False, f"Syntax error: {str(e)}"
    
    @staticmethod
    def sanitize_prompt(prompt: str) -> str:
        """Enhanced prompt sanitization"""
        if not prompt:
            return ""
        
        # Remove control characters
        prompt = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', prompt)
        
        # Block dangerous patterns
        for pattern in SecurityConfig.DANGEROUS_PATTERNS:
            prompt = re.sub(pattern, '[BLOCKED]', prompt, flags=re.IGNORECASE)
        
        # Limit prompt length
        if len(prompt) > 1000:
            prompt = prompt[:1000] + "..."
        
        return prompt.strip()