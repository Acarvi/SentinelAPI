import os
import urllib.request
from urllib.error import URLError, HTTPError
from security_audit import safe_print

def verify_gemini_api():
    """
    Checks if the GEMINI_API_KEY is present and valid.
    Uses urllib to keep dependencies minimal (zero-config).
    """
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        safe_print("❌ SentinelAPI: GEMINI_API_KEY NOT FOUND in environment!")
        return False
    
    # Lightweight check: list models using the API key
    url = f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}"
    
    try:
        with urllib.request.urlopen(url, timeout=10) as response:
            if response.getcode() == 200:
                safe_print("✅ SentinelAPI: Gemini API Connectivity Verified.")
                return True
    except HTTPError as e:
        status_code = e.code
        if status_code == 400:
            safe_print("❌ SentinelAPI: Gemini API Key INVALID or MALFORMED (400).")
        elif status_code == 401:
            safe_print("❌ SentinelAPI: Gemini API Key UNAUTHORIZED (401).")
        elif status_code == 403:
            safe_print("❌ SentinelAPI: Gemini API Key FORBIDDEN (403) - Check billing/quotas.")
        elif status_code == 429:
            safe_print("⚠️ SentinelAPI: Gemini API Rate Limit reached (429). Proceeding with caution.")
            return True # Not a key failure per se
        else:
            safe_print(f"❌ SentinelAPI: Gemini API Error ({status_code}).")
    except URLError as e:
        safe_print(f"⚠️ SentinelAPI: Network Connectivity Error (Gemini check failed): {e.reason}")
        return False
    except Exception as e:
        safe_print(f"❌ SentinelAPI: Unexpected error during Gemini check: {e}")
        
    return False

def validate_all_apis():
    """
    Orchestrates all external API health checks.
    """
    safe_print("[SENTINEL] SentinelAPI: Pre-flight API Health Check...")
    
    gemini_ok = verify_gemini_api()
    
    if not gemini_ok:
        safe_print("🛑 SentinelAPI: Critical API Health Check Failed.")
        return False
    
    safe_print("[SENTINEL] SentinelAPI: API Health Check Passed.")
    return True

if __name__ == "__main__":
    # For manual testing
    from dotenv import load_dotenv
    load_dotenv()
    validate_all_apis()
