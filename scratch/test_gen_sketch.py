import os
from dotenv import load_dotenv
from huggingface_hub import InferenceClient

load_dotenv()
HF_TOKEN = os.getenv("HF_TOKEN")

client = InferenceClient(model="stabilityai/stable-diffusion-xl-base-1.0", token=HF_TOKEN)

prompt = (
    "forensic pencil sketch of a male, late 30s, rugged beard, intense dark eyes, short messy hair, wearing a grey hoodie. "
    "graphite drawing, black and white, hand-drawn forensic art, charcoal lines, scanned sketch, neutral expression, "
    "plain white background, close up face shot, highly detailed, looking straight ahead, front view"
)

negative_prompt = (
    "blurry, low quality, distorted face, deformed, ugly, extra limbs, cartoon, anime, watermark, text, logo, "
    "sunglasses, hat, helmet, mask, multiple people, full body, wide shot, looking away, eyes closed, color, colored, painting"
)

try:
    print("Generating test sketch using Hugging Face InferenceClient...")
    image = client.text_to_image(
        prompt,
        negative_prompt=negative_prompt,
        num_inference_steps=30,
        guidance_scale=7.5
    )
    output_path = "/Users/ashirwadborkar/Documents/Main Dir/Projects/Suspect sketch/scratch/test_sketch_7721.png"
    image.save(output_path)
    print(f"Success! Saved test sketch to: {output_path}")
except Exception as e:
    print(f"Failed: {e}")
