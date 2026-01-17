#!/usr/bin/env python3
"""Test Gemini API key configuration"""

from app.core.config import settings
import requests

def test_api_key_loaded():
    """Test that API key is loaded from .env"""
    print("=" * 50)
    print("Testing GEMINI_API_KEY Configuration")
    print("=" * 50)
    
    # Check if key is loaded
    api_key = settings.GEMINI_API_KEY
    
    if not api_key:
        print("❌ ERROR: GEMINI_API_KEY is empty!")
        print("   Make sure you have:")
        print("   1. Created backend/.env file")
        print("   2. Added: GEMINI_API_KEY=AIzaSy...")
        return False
    
    # Show first/last few chars (don't print full key)
    masked_key = f"{api_key[:15]}...{api_key[-10:]}" if len(api_key) > 25 else "***"
    print(f"✅ API Key loaded: {masked_key}")
    print(f"   Key length: {len(api_key)} characters")
    
    return True

def test_gemini_connection():
    """Test actual API call to Gemini using REST API"""
    print("\n" + "=" * 50)
    print("Testing Gemini API Connection")
    print("=" * 50)
    
    try:
        api_key = settings.GEMINI_API_KEY
        
        # Use a known working model - try gemini-2.5-flash or gemini-2.5-pro
        model_to_use = "gemini-2.5-flash"  # Latest fast model
        
        # Now make the actual API call
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_to_use}:generateContent?key={api_key}"
        
        headers = {"Content-Type": "application/json"}
        data = {
            "contents": [{
                "parts": [{
                    "text": "Say 'Hello from Veritas' in one sentence."
                }]
            }]
        }
        
        print(f"📡 Making test API call with model: {model_to_use}...")
        response = requests.post(url, json=data, headers=headers)
        response.raise_for_status()
        
        result = response.json()
        text = result["candidates"][0]["content"]["parts"][0]["text"]
        
        print(f"✅ API call successful!")
        print(f"   Response: {text}")
        print(f"   Model: {model_to_use}")
        
        return True
        
    except requests.exceptions.HTTPError as e:
        print(f"❌ HTTP Error!")
        print(f"   Status: {e.response.status_code if hasattr(e, 'response') else 'N/A'}")
        print(f"   Error: {e}")
        if hasattr(e, 'response') and e.response is not None:
            try:
                error_detail = e.response.json()
                print(f"   Details: {error_detail}")
            except:
                print(f"   Response: {e.response.text[:200]}")
        return False
        
    except Exception as e:
        print(f"❌ Error occurred!")
        print(f"   Error type: {type(e).__name__}")
        print(f"   Error: {e}")
        return False

if __name__ == "__main__":
    print("\n")
    
    # Test 1: Check if key is loaded
    key_loaded = test_api_key_loaded()
    
    if not key_loaded:
        print("\n⚠️  Cannot proceed with API test - key not loaded")
        exit(1)
    
    # Test 2: Test actual API call
    api_works = test_gemini_connection()
    
    print("\n" + "=" * 50)
    if api_works:
        print("✅ ALL TESTS PASSED - Gemini API is configured correctly!")
    else:
        print("❌ TESTS FAILED - Check the errors above")
    print("=" * 50)
    print()
