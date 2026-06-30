import os
import requests
from dotenv import load_dotenv

load_dotenv()
STABILITY_API_KEY = os.getenv("STABILITY_API_KEY")
HF_TOKEN = os.getenv("HF_TOKEN")

print(f"STABILITY_API_KEY: {STABILITY_API_KEY[:10] if STABILITY_API_KEY else None}...")
print(f"HF_TOKEN: {HF_TOKEN[:10] if HF_TOKEN else None}...")

# Test Stability
STABILITY_URL = "https://api.stability.ai/v1/generation/stable-diffusion-xl-1024-v1-0/text-to-image"
headers = {
    "Authorization": f"Bearer {STABILITY_API_KEY}",
    "Content-Type": "application/json",
    "Accept": "application/json",
}
payload = {
    "text_prompts": [{"text": "A pencil sketch of a man", "weight": 1.0}],
    "cfg_scale": 7,
    "height": 1024,
    "width": 1024,
    "samples": 1,
    "steps": 10,
}
try:
    response = requests.post(STABILITY_URL, headers=headers, json=payload)
    print(f"Stability response status: {response.status_code}")
    if response.status_code != 200:
        print(f"Stability response: {response.text}")
except Exception as e:
    print(f"Stability test failed: {e}")

# Test HF
from huggingface_hub import InferenceClient
try:
    client = InferenceClient(model="stabilityai/stable-diffusion-xl-base-1.0", token=HF_TOKEN)
    image = client.text_to_image("A pencil sketch of a man", num_inference_steps=5)
    print("HF SDXL test success!")
except Exception as e:
    print(f"HF SDXL test failed: {e}")
