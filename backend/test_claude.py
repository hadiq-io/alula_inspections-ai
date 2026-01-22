import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()

endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
api_key = os.getenv("AZURE_OPENAI_KEY")

print(f"🔗 Endpoint: {endpoint}")
print(f"🔑 API Key: {api_key[:20]}...")

# Test 1: Messages API (Anthropic style)
print("\n" + "="*60)
print("TEST 1: Anthropic Messages API")
print("="*60)

url = f"{endpoint}/v1/messages"
headers = {
    "Content-Type": "application/json",
    "api-key": api_key,
    "anthropic-version": "2023-06-01"
}

payload = {
    "model": "claude-sonnet-4-5",
    "max_tokens": 100,
    "messages": [
        {
            "role": "user",
            "content": "Hello, how are you?"
        }
    ]
}

print(f"URL: {url}")
print(f"Payload: {json.dumps(payload, indent=2)}")

try:
    response = requests.post(url, headers=headers, json=payload, timeout=30)
    print(f"\n✅ Status Code: {response.status_code}")
    print(f"📥 Response: {response.text}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"\n🎉 SUCCESS!")
        print(f"Response: {result}")
except Exception as e:
    print(f"\n❌ Error: {str(e)}")

# Test 2: Chat Completions API (OpenAI style)
print("\n" + "="*60)
print("TEST 2: OpenAI Chat Completions API")
print("="*60)

url2 = f"{endpoint}/v1/chat/completions"
headers2 = {
    "Content-Type": "application/json",
    "api-key": api_key
}

payload2 = {
    "model": "claude-sonnet-4-5",
    "max_tokens": 100,
    "messages": [
        {
            "role": "user",
            "content": "Hello, how are you?"
        }
    ]
}

print(f"URL: {url2}")

try:
    response = requests.post(url2, headers=headers2, json=payload2, timeout=30)
    print(f"\n✅ Status Code: {response.status_code}")
    print(f"📥 Response: {response.text}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"\n🎉 SUCCESS!")
        print(f"Response: {result}")
except Exception as e:
    print(f"\n❌ Error: {str(e)}")

# Test 3: Try with x-api-key header
print("\n" + "="*60)
print("TEST 3: Using x-api-key header")
print("="*60)

headers3 = {
    "Content-Type": "application/json",
    "x-api-key": api_key,
    "anthropic-version": "2023-06-01"
}

try:
    response = requests.post(url, headers=headers3, json=payload, timeout=30)
    print(f"\n✅ Status Code: {response.status_code}")
    print(f"📥 Response: {response.text}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"\n🎉 SUCCESS!")
        print(f"Response: {result}")
except Exception as e:
    print(f"\n❌ Error: {str(e)}")

print("\n" + "="*60)
print("TESTING COMPLETE")
print("="*60)
