"""AST-based code validator"""
import ast
import re
from typing import Tuple
from .config import SecurityConfig

class SecureCodeValidator:
    DANGEROUS_FUNCTIONS = {'exec', 'eval', 'compile', '__import__', 'open', 'globals', 'locals', 'getattr', 'setattr'}
    DANGEROUS_ATTRIBUTES = {'__class__', '__bases__', '__subclasses__', '__globals__', '__builtins__'}
    
    @staticmethod
    def check_dangerous_patterns(code: str) -> Tuple[bool, str]:
        if len(code) > SecurityConfig.MAX_CODE_LENGTH:
            return False, "Code too long"
        for pattern in SecurityConfig.DANGEROUS_PATTERNS:
            if re.search(pattern, code, re.IGNORECASE):
                return False, f"Dangerous pattern detected"
        return True, "OK"
    
    @staticmethod
    def validate_ast(code: str) -> Tuple[bool, str]:
        try:
            tree = ast.parse(code)
            for node in ast.walk(tree):
                if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
                    if node.func.id in SecureCodeValidator.DANGEROUS_FUNCTIONS:
                        return False, f"Forbidden function: {node.func.id}"
                if isinstance(node, ast.Attribute) and node.attr in SecureCodeValidator.DANGEROUS_ATTRIBUTES:
                    return False, f"Forbidden attribute: {node.attr}"
            return True, "Valid AST"
        except SyntaxError as e:
            return False, f"Syntax error: {e}"
    
    @staticmethod
    def sanitize_prompt(prompt: str) -> str:
        prompt = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', prompt)
        for pattern in SecurityConfig.DANGEROUS_PATTERNS:
            prompt = re.sub(pattern, '[BLOCKED]', prompt, flags=re.IGNORECASE)
        return prompt[:1000]