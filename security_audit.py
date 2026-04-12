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

def check_gitignore():
    """Checks if mandatory secrets are in .gitignore."""
    if not os.path.exists('.gitignore'):
        # Some small scrapers might not have it, but we warn
        print("⚠️ Warning: NO .gitignore FOUND!")
        return True # Don't block if intentionally not using git
    
    with open('.gitignore', 'r') as f:
        content = f.read()
        
    all_present = True
    for item in MANDATORY_GITIGNORE:
        if item not in content:
            print(f"❌ '{item}' is NOT in .gitignore!")
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
        print("❌ SentinelAPI: SECRET EXPOSURE DETECTED!")
        for secret in found_secrets:
            print(f"   - {secret}")
        return False
    return True

def validate_environment():
    """Main entry point for security verification."""
    print("[SENTINEL] SentinelAPI: Pre-flight Audit...")
    
    gi_ok = check_gitignore()
    sec_ok = scan_for_secrets()
    
    if not (gi_ok and sec_ok):
        print("\n[SENTINEL] STARTUP BLOCKED: Security vulnerabilities detected.")
        print("Please resolve the issues above before running the application.")
        sys.exit(1)
    
    print("[SENTINEL] SentinelAPI: Security Audit Passed.")

if __name__ == "__main__":
    validate_environment()
