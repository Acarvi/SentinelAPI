# SentinelAPI 🛡️

**Professional Security & Resilience Layer for Python Microservices.**

SentinelAPI provides a standardized, shared security barrier to prevent API key exposure, audit project integrity, and redact sensitive information from logs in real-time.

## Core Features

-   **🔍 Security Auditor**: Automatic pre-flight scanning for hardcoded secrets and `.gitignore` compliance. Startup is blocked if vulnerabilities are found.
-   **🔒 Log Sanitizer**: Global monkey-patching of `stdout`, `stderr`, and `logging` to automatically redact all sensitive environment variables from terminal output and log files.
-   **🚀 Zero-Config Bootstrap**: Integrate into any sibling project with just two lines of code.

## Integration Guide

To protect a new project located in the same root directory as `SentinelAPI`, add the following snippet at the **very top** of your main entry point:

```python
import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "SentinelAPI")))
from bootstrap import activate_security
activate_security()
```

## Security Policies

SentinelAPI enforces the following by default:
1.  **Strict Git Hygiene**: Detects if `.env`, `client_secrets.json`, or `.pickle` files are untracked.
2.  **Secret Redaction**: Any environment variable containing `KEY`, `SECRET`, `TOKEN`, `PASSWORD`, or `API` in its name is automatically added to the redaction list.
3.  **Startup Guardianship**: The application will exit with code `1` if the audit fails, ensuring no insecure code ever runs in production.

---
*Maintained by Antigravity AI Software Engineer.*
