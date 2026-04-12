import sys
import os

def activate_security():
    """
    Enables the full SentinelAPI stack: Audit + Sanitizer.
    Call this as the first line in your main script.
    """
    # Self-inject the directory containing this script into sys.path
    current_dir = os.path.dirname(os.path.abspath(__file__))
    if current_dir not in sys.path:
        sys.path.insert(0, current_dir)
    
    try:
        from security_audit import validate_environment
        from log_sanitizer import init_sanitizer
        
        # --- EXECUTION ---
        validate_environment()
        init_sanitizer()
    except ImportError as e:
        print(f"🛑 SentinelAPI Bootstrap Failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    activate_security()
