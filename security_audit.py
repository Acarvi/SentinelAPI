import os
import re
import sys

# Regular expressions for common secrets
SECRET_PATTERNS = {
    "Gemini/Google API Key": r"AIzaSy[A-Za-z0-9_-]{33}",
    # Add more as needed
}

MANDATORY_GITIGNORE = [".env", "client_secrets.json", "*.pickle"]
# Files that are allowed to contain patterns (the auditor itself and its documentation)
WHITELISTED_FILES = ["security_audit.py", "log_sanitizer.py", "README.md", "bootstrap.py", "init_sentinel.py"]

# Directories that should never be scanned for real secrets (mocks/tests)
IGNORED_DIRS = ["tests", "venv", ".venv", "__pycache__", ".git", "scratch", "SentinelAPI"]

def safe_print(msg):
    """Prints message handling potential encoding issues in Windows environments."""
    try:
        print(msg)
    except UnicodeEncodeError:
        safe_msg = msg.encode('ascii', errors='replace').decode('ascii')
        print(safe_msg)

def check_gitignore():
    """Checks if mandatory secrets are in .gitignore."""
    if not os.path.exists('.gitignore'):
        # Some small scrapers might not have it, but we warn
        safe_print("⚠️ Warning: NO .gitignore FOUND!")
        return True # Don't block if intentionally not using git
    
    content = ""
    # Try common encodings for Windows/Unix compatibility
    for encoding in ['utf-8', 'utf-8-sig', 'utf-16']:
        try:
            with open('.gitignore', 'r', encoding=encoding) as f:
                content = f.read()
                if content: break
        except (UnicodeDecodeError, Exception):
            continue
            
    if not content:
        # Fallback to binary read and decode with ignore
        try:
            with open('.gitignore', 'rb') as f:
                content = f.read().decode('utf-8', errors='ignore')
        except:
            safe_print("⚠️ Warning: Could not read .gitignore properly.")
            return True
        
    all_present = True
    for item in MANDATORY_GITIGNORE:
        if item not in content:
            safe_print(f"❌ '{item}' is NOT in .gitignore!")
            all_present = False
            
    return all_present

def scan_for_secrets(project_root='.'):
    """Scans for hardcoded secrets in the project."""
    found_secrets = []
    
    for root, dirs, files in os.walk(project_root):
        # In-place modification to skip ignored directories
        dirs[:] = [d for d in dirs if d not in IGNORED_DIRS]
        
        for file in files:
            if file.endswith('.py') or file.endswith('.json') or file.endswith('.bat'):
                if file in WHITELISTED_FILES:
                    continue
                    
                path = os.path.join(root, file)
                try:
                    with open(path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        for name, pattern in SECRET_PATTERNS.items():
                            matches = re.findall(pattern, content)
                            for match in matches:
                                # Double check it's not a placeholder
                                if "MOCK" not in match.upper() and "DUMMY" not in match.upper():
                                    found_secrets.append(f"{path} ({name})")
                except Exception:
                    continue
                    
    if found_secrets:
        safe_print("❌ SentinelAPI: SECRET EXPOSURE DETECTED!")
        for secret in found_secrets:
            safe_print(f"   - {secret}")
        return False
    return True

def validate_environment(check_apis=True):
    """Main entry point for security verification."""
    safe_print("[SENTINEL] SentinelAPI: Pre-flight Audit...")
    
    gi_ok = check_gitignore()
    sec_ok = scan_for_secrets()
    
    if not (gi_ok and sec_ok):
        safe_print("\n[SENTINEL] STARTUP/PUSH BLOCKED: Security vulnerabilities detected.")
        safe_print("Please resolve the issues above before proceeding.")
        sys.exit(1)
    
    if check_apis:
        try:
            from api_checker import validate_all_apis
            if not validate_all_apis():
                safe_print("[SENTINEL] Warning: Some API Health Checks failed. Fallbacks may be triggered.")
        except ImportError:
            safe_print("⚠️ Warning: api_checker not found. Skipping API health check.")
            
    safe_print("[SENTINEL] SentinelAPI: Security Audit Passed.")

if __name__ == "__main__":
    validate_environment()
