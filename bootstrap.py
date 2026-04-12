import sys
import os

def activate_security():
    """
    Enables the full SentinelAPI stack: Audit + Sanitizer + API Health.
    Call this as the first line in your main script.
    """
    # Self-inject the directory containing this script into sys.path
    current_dir = os.path.dirname(os.path.abspath(__file__))
    if current_dir not in sys.path:
        sys.path.insert(0, current_dir)
    
    # Try to load .env from the current working directory to ensure API keys are available
    try:
        from dotenv import load_dotenv
        import os
        cwd = os.getcwd()
        env_path = os.path.join(cwd, ".env")
        if os.path.exists(env_path):
            load_dotenv(env_path)
        else:
            # Try to find .env in the parent directory if we are inside a subfolder
            parent_env = os.path.join(os.path.dirname(cwd), ".env")
            if os.path.exists(parent_env):
                load_dotenv(parent_env)
    except ImportError:
        pass 

    try:
        from security_audit import validate_environment
        from log_sanitizer import init_sanitizer
        from api_checker import validate_all_apis
        
        # --- EXECUTION ---
        # 1. Audit files and secrets (Security Layer)
        validate_environment()
        
        # 2. Check external API connectivity (Resilience Layer)
        if not validate_all_apis():
            sys.exit(1)
            
        # 3. Initialize log redaction (Privacy Layer)
        init_sanitizer()
    except ImportError as e:
        print(f"🛑 SentinelAPI Bootstrap Failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    activate_security()
