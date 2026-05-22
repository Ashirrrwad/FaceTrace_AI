from huggingface_hub import InferenceClient
import os

token = "REDACTED_HF_TOKEN"

models_to_test = [
    "runwayml/stable-diffusion-v1-5",
    "prompthero/openjourney",
    "stabilityai/stable-diffusion-2-1"
]

for model in models_to_test:
    print(f"Testing {model}...")
    client = InferenceClient(model=model, token=token)
    try:
        image = client.text_to_image("A test portrait of a dog.", num_inference_steps=2)
        print(f"Success! {model} generated an image.")
    except Exception as e:
        print(f"Failed {model}: {type(e).__name__} - {e}")
