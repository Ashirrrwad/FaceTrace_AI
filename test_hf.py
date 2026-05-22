import requests
import os
from dotenv import load_dotenv

load_dotenv()
token = os.getenv("HF_TOKEN")
url = "https://api.stability.ai/v1/generation/stable-diffusion-xl-1024-v1-0/text-to-image"
headers = {"Authorization": f"Bearer {token}"}
payload = {"inputs": "A test portrait of a dog."}

response = requests.post(url, headers=headers, json=payload)
print(f"Status: {response.status_code}")
try:
    print(response.json())
except:
    print(response.text[:200])
