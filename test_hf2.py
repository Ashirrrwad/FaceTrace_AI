from huggingface_hub import InferenceClient
import os
from dotenv import load_dotenv

load_dotenv()
HF_TOKEN = os.getenv("HF_TOKEN")
MODEL_ID = "stabilityai/stable-diffusion-xl-base-1.0"

client = InferenceClient(model=MODEL_ID, token=HF_TOKEN)

try:
    image = client.text_to_image("A test portrait of a dog.")
    print("Success! Image generated.")
except Exception as e:
    print(f"Exception caught: {type(e).__name__} - {e}")
