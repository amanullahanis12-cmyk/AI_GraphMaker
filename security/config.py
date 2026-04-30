"""
Security configuration and constants
"""

class SecurityConfig:
    """Centralized security configuration"""
    
    # Allowed imports for code generation
    ALLOWED_IMPORTS = {
        'pandas', 'pd', 'numpy', 'np', 'matplotlib', 'plt', 
        'seaborn', 'sns', 'plotly', 'plotly.express', 'px',
        'plotly.graph_objects', 'go'
    }
    
    # Dangerous patterns to block
    DANGEROUS_PATTERNS = [
        r'__.*__',                     # Dunder methods
        r'(exec|eval|compile)\s*\(',   # Code execution
        r'import\s+(os|sys|subprocess|socket|requests)',  # Dangerous imports
        r'from\s+(os|sys|subprocess|socket|requests)\s+import',  # Dangerous imports
        r'open\s*\(',                  # File operations
        r'__import__\s*\(',            # Dynamic imports
        r'globals\s*\(',               # Globals access
        r'locals\s*\(',                # Locals access
        r'getattr\s*\(',               # Attribute access
        r'setattr\s*\(',               # Attribute modification
        r'delattr\s*\(',               # Attribute deletion
        r'(rm|del|remove|delete)\s+',  # Deletion operations
        r'subprocess\.',               # Subprocess calls
        r'os\.',                       # OS operations
        r'socket\.',                   # Network operations
        r'eval\s*\(',                  # Eval calls
    ]
    
    # Excel formula injection patterns for CSV validation
    CSV_INJECTION_PATTERNS = [
        r'^=', r'^\+', r'^\-', r'^@',
        r'=cmd', r'=powershell', r'=python',
        r'!', r'`', r'\$'
    ]
    
    MAX_CODE_LENGTH = 5000  # Characters
    TIMEOUT_SECONDS = 30
    MAX_DF_ROWS = 100000
    MAX_DF_COLUMNS = 100