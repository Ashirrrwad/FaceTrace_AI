from huggingface_hub import InferenceClient
from dotenv import load_dotenv
import os
import io

load_dotenv()

token = os.getenv("REDACTED_HF_TOKEN")  
MODEL_ID = "stabilityai/stable-diffusion-xl-base-1.0"

client = InferenceClient(model=MODEL_ID, token=token)

try:
    print("Testing Hugging Face Image Gen...")
    image = client.text_to_image(
        "A test portrait of a dog.",
        num_inference_steps=5,
        guidance_scale=7.5
    )
    image.save("test_output.png") 
    print("Success! Image saved as test_output.png")
except Exception as e:
    print(f"Exception caught: {type(e).__name__} - {e}")
