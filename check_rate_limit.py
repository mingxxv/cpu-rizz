#!/usr/bin/env python3
"""
Quick script to check API rate limit headers
"""
import os
import requests
from dotenv import load_dotenv
from datetime import datetime, timezone

# Load environment variables
load_dotenv()

api_key = os.getenv("SAMBANOVA_API_KEY")
if not api_key:
    print("❌ SAMBANOVA_API_KEY not found in .env file")
    exit(1)

# Make a minimal request to check headers
url = "https://api.sambanova.ai/v1/chat/completions"
headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json"
}

payload = {
    "model": "Meta-Llama-3.1-8B-Instruct",
    "messages": [{"role": "user", "content": "Hi"}],
    "max_tokens": 10
}

print("Making request to Sambanova API...")
response = requests.post(url, headers=headers, json=payload)

print(f"\n📊 Response Status: {response.status_code}")
print("\n" + "="*60)
print("RATE LIMIT HEADERS:")
print("="*60)

# Display all rate limit related headers
rate_limit_headers = {k: v for k, v in response.headers.items() if 'ratelimit' in k.lower()}

if rate_limit_headers:
    for header, value in rate_limit_headers.items():
        print(f"{header}: {value}")

        # If this is the reset header, convert timestamp to readable format
        if 'reset' in header.lower() and value.isdigit():
            timestamp = int(value)
            reset_time = datetime.fromtimestamp(timestamp, tz=timezone.utc)
            now = datetime.now(timezone.utc)
            time_until_reset = reset_time - now

            print(f"  └─ Resets at: {reset_time.strftime('%Y-%m-%d %H:%M:%S UTC')}")
            print(f"  └─ Time until reset: {time_until_reset}")
else:
    print("No rate limit headers found in response")
    print("\nAll response headers:")
    for header, value in response.headers.items():
        print(f"{header}: {value}")

print("="*60)
