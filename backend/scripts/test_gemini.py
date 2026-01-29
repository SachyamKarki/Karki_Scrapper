#!/usr/bin/env python3
"""Quick test to verify Gemini API is responding. Run from backend/ directory."""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv()

def test_gemini():
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        print("FAIL: GEMINI_API_KEY not found in .env")
        return False

    print("Testing Gemini API...")

    try:
        import google.generativeai as genai
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-3-flash-preview')
        response = model.generate_content("Reply with exactly: Gemini is working!")
        text = getattr(response, 'text', None)
        if text:
            print("SUCCESS: Gemini responded!")
            print(f"Response: {text.strip()}")
            return True
        else:
            print("FAIL: Gemini returned empty response")
            return False
    except ImportError as e:
        print(f"FAIL: google-generativeai not installed: {e}")
        return False
    except Exception as e:
        print(f"FAIL: {type(e).__name__}: {e}")
        return False

if __name__ == '__main__':
    ok = test_gemini()
    sys.exit(0 if ok else 1)
