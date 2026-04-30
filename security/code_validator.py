"""
AST-based code validator for security
"""

import ast
import re
from typing import Tuple
from .config import SecurityConfig


class SecureCodeValidator:
    """Validates Python code for security vulnerabilities"""
    
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
                if module_name not in SecurityConfig.ALLOWED_IMPORTS:
                    return False, f"Import from '{module_name}' not allowed"
        
        return True, "OK"
    
    @staticmethod
    def check_dangerous_patterns(code: str) -> Tuple[bool, str]:
        """Check for dangerous string patterns"""
        for pattern in SecurityConfig.DANGEROUS_PATTERNS:
            matches = re.findall(pattern, code, re.IGNORECASE)
            if matches:
                return False, f"Dangerous pattern detected: {matches[0]}"
        
        # Check length
        if len(code) > SecurityConfig.MAX_CODE_LENGTH:
            return False, f"Code exceeds maximum length of {SecurityConfig.MAX_CODE_LENGTH} characters"
        
        return True, "OK"
    
    @staticmethod
    def validate_ast(code: str) -> Tuple[bool, str]:
        """Parse and validate AST"""
        try:
            tree = ast.parse(code)
            
            # Validate imports
            valid, msg = SecureCodeValidator.validate_imports(tree)
            if not valid:
                return False, msg
            
            # Check for dangerous function calls
            for node in ast.walk(tree):
                if isinstance(node, ast.Call):
                    if isinstance(node.func, ast.Name):
                        if node.func.id in ['exec', 'eval', 'compile', '__import__']:
                            return False, f"Use of {node.func.id}() is forbidden"
            
            return True, "Valid AST"
            
        except SyntaxError as e:
            return False, f"Syntax error: {str(e)}"
    
    @staticmethod
    def sanitize_prompt(prompt: str) -> str:
        """Remove or block dangerous content in prompts"""
        for pattern in SecurityConfig.DANGEROUS_PATTERNS:
            prompt = re.sub(pattern, '[BLOCKED]', prompt, flags=re.IGNORECASE)
        return prompt