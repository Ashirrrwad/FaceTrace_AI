import os
import shutil
import json
from dotenv import load_dotenv
from huggingface_hub import InferenceClient

load_dotenv()
HF_TOKEN = os.getenv("HF_TOKEN")

client = InferenceClient(model="stabilityai/stable-diffusion-xl-base-1.0", token=HF_TOKEN)

cases_dir = "/Users/ashirwadborkar/Documents/Main Dir/Projects/Suspect sketch/static/images/cases"
backup_dir = os.path.join(cases_dir, "backup")
db_path = "/Users/ashirwadborkar/Documents/Main Dir/Projects/Suspect sketch/database.json"

# Create backup directory
os.makedirs(backup_dir, exist_ok=True)

# Load database
with open(db_path, "r") as f:
    criminals = json.load(f)

negative_prompt = (
    "blurry, low quality, distorted face, deformed, ugly, extra limbs, cartoon, anime, watermark, text, logo, "
    "sunglasses, hat, helmet, mask, multiple people, full body, wide shot, looking away, eyes closed, color, colored, painting, "
    "photograph, realistic photo, 3d render"
)

for criminal in criminals:
    cid = criminal["id"]
    desc = criminal["description"]
    id_lower = cid.lower()
    
    sketch_filename = f"{id_lower}_sketch.png"
    src_path = os.path.join(cases_dir, sketch_filename)
    dst_path = os.path.join(backup_dir, sketch_filename)
    
    # 1. Backup original file if it exists
    if os.path.exists(src_path):
        if not os.path.exists(dst_path):
            shutil.copy2(src_path, dst_path)
            print(f"Backed up: {sketch_filename} to backup/")
        else:
            print(f"Backup already exists for: {sketch_filename}")
    
    # 2. Construct prompt
    prompt = (
        f"forensic pencil sketch of a {desc.strip()} "
        "hand-drawn forensic art, graphite drawing, black and white, charcoal lines, scanned sketch, "
        "neutral expression, plain white background, close up face shot, highly detailed, looking straight ahead, front view"
    )
    
    print(f"Generating sketch for {cid} ({criminal['name']})...")
    print(f"Prompt: {prompt}")
    
    try:
        image = client.text_to_image(
            prompt,
            negative_prompt=negative_prompt,
            num_inference_steps=35,
            guidance_scale=8.0
        )
        image.save(src_path)
        print(f"✅ Successfully generated and saved: {sketch_filename}")
    except Exception as e:
        print(f"❌ Failed to generate sketch for {cid}: {e}")

print("All sketches processed!")
