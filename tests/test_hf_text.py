from huggingface_hub import InferenceClient
import os
from dotenv import load_dotenv
load_dotenv()
token = os.getenv("HF_TOKEN")
client = InferenceClient(model="mistralai/Mistral-7B-Instruct-v0.3", token=token)
try:
    print(client.text_generation("Hello"))
except Exception as e:
    print(f"Error: {e}")
