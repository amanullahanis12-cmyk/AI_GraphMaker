# tutorio/security/config.py
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
        r'__.*__',
        r'(exec|eval|compile)\s*\(',
        r'import\s+(os|sys|subprocess|socket|requests|ctypes|multiprocessing)',
        r'from\s+(os|sys|subprocess|socket|requests|ctypes)\s+import',
        r'open\s*\(',
        r'__import__\s*\(',
        r'globals\s*\(',
        r'locals\s*\(',
        r'getattr\s*\(',
        r'setattr\s*\(',
        r'delattr\s*\(',
        r'subprocess\.',
        r'os\.',
        r'socket\.',
        r'chr\s*\(',
        r'ord\s*\(',
        r'base64',
        r'codecs',
    ]
    
    # CSV injection patterns
    CSV_INJECTION_PATTERNS = [
        r'^[\s]*=',
        r'^[\s]*\+',
        r'^[\s]*\-',
        r'^[\s]*@',
        r'DDE',
        r'Excel\.Application',
        r'Shell\.Application',
        r'WScript\.Shell'
    ]
    
    MAX_CODE_LENGTH = 5000
    MAX_PROMPT_LENGTH = 1000
    TIMEOUT_SECONDS = 30
    MAX_DF_ROWS = 100000
    MAX_DF_COLUMNS = 100