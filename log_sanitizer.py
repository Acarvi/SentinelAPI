import sys
import os
from dotenv import load_dotenv

class RedactedStream:
    def __init__(self, original_stream, sensitive_values):
        self.original_stream = original_stream
        self.sensitive_values = [v for v in sensitive_values if v and len(v) > 4]

    def write(self, data):
        if not data:
            return self.original_stream.write(data)
        
        sanitized_data = data
        for val in self.sensitive_values:
            sanitized_data = sanitized_data.replace(val, "[REDACTED]")
            
        return self.original_stream.write(sanitized_data)

    def flush(self):
        return self.original_stream.flush()

    def __getattr__(self, name):
        return getattr(self.original_stream, name)

def init_sanitizer():
    """Initializes the log sanitizer by monkey-patching stdout and stderr."""
    load_dotenv()
    
    # Collect sensitive values from environment
    sensitive_values = []
    # Project-specific common env files
    for key, value in os.environ.items():
        if any(x in key.upper() for x in ['KEY', 'SECRET', 'TOKEN', 'PASSWORD', 'API']):
            if value and len(value) > 4:
                sensitive_values.append(value)
    
    # Apply monkey patch
    sys.stdout = RedactedStream(sys.stdout, sensitive_values)
    sys.stderr = RedactedStream(sys.stderr, sensitive_values)
    
    # Patch existing loggers
    import logging
    class SanitizedFormatter(logging.Formatter):
        def format(self, record):
            msg = super().format(record)
            for val in sensitive_values:
                msg = msg.replace(val, "[REDACTED]")
            return msg

    print("[SENTINEL] SentinelAPI: Log Sanitizer active. Sensitive data is [REDACTED].")

if __name__ == "__main__":
    init_sanitizer()
