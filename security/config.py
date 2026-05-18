"""Security configuration"""
class SecurityConfig:
    ALLOWED_IMPORTS = {'pandas', 'numpy', 'matplotlib', 'seaborn', 'plotly', 'plotly.express'}
    DANGEROUS_PATTERNS = [
        r'__.*__', r'(exec|eval|compile)\s*\(', r'import\s+(os|sys|subprocess)',
        r'open\s*\(', r'globals\s*\(', r'locals\s*\(', r'getattr\s*\(', r'setattr\s*\('
    ]
    CSV_INJECTION_PATTERNS = [r'^[\s]*[=+\-@]', r'DDE', r'Excel\.Application', r'Shell\.Application']
    MAX_CODE_LENGTH = 5000
    MAX_DF_ROWS = 100000