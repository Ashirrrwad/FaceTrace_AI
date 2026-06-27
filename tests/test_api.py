import requests
import os

url = "https://api.stability.ai/v1/generation/stable-diffusion-xl-1024-v1-0/text-to-image"

headers = {
    "Authorization": f"Bearer {os.getenv('REDACTED_STABILITY_KEY')}",
    "Content-Type": "application/json",
}

payload = {
    "text_prompts": [{"text": "A professional forensic sketch of a suspect."}],
    "cfg_scale": 7,
    "height": 1024,
    "width": 1024,
    "samples": 1,
}

response = requests.post(url, headers=headers, json=payload)