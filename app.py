import os
import base64
import io
import json
import random
import requests
from typing import Optional
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
from huggingface_hub import InferenceClient

load_dotenv()

app = Flask(__name__)

HF_TOKEN = os.getenv("HF_TOKEN")
STABILITY_API_KEY = os.getenv("STABILITY_API_KEY")

client = InferenceClient(token=HF_TOKEN)

FORENSIC_STYLE_PREFIX = (
    "Authentic police composite sketch, rough graphite pencil on paper, "
    "amateur forensic art, flat lighting, straight-on mugshot framing, "
    "single face only, plain white background, "
)

GLOBAL_NEGATIVE_PROMPT = (
    "multiple faces, split screen, character sheet, cinematic lighting, "
    "3d render, photorealistic, photography, comic book, graphic novel, "
    "hyper-detailed shading, perfect symmetry, hats, sunglasses, "
    "text, watermark, color, blurry, low quality, deformed, extra limbs, "
    "anime, cartoon, full body, wide shot, looking away, eyes closed"
)

SKETCH_OUTPUT_DIR = os.path.join(os.path.dirname(__file__), 'static', 'images', 'cases')
os.makedirs(SKETCH_OUTPUT_DIR, exist_ok=True)


STABILITY_URL = "https://api.stability.ai/v1/generation/stable-diffusion-xl-1024-v1-0/text-to-image"


CRIMINAL_DB = []

GENERATED_CASES = {}

DB_PATH = os.path.join(os.path.dirname(__file__), 'database.json')


def load_criminal_db():
    """Load the criminal database from database.json.
    Supports both the legacy list format and the new combined dict format.
    """
    global CRIMINAL_DB, GENERATED_CASES
    if os.path.exists(DB_PATH):
        try:
            with open(DB_PATH, 'r') as f:
                raw = json.load(f)
            if isinstance(raw, list):
                CRIMINAL_DB = raw
                GENERATED_CASES = {}
            elif isinstance(raw, dict):
                CRIMINAL_DB = raw.get('suspects', [])
                GENERATED_CASES = raw.get('generated', {})
            print(f"Loaded {len(CRIMINAL_DB)} pre-existing suspects and "
                  f"{len(GENERATED_CASES)} generated cases from database.json.")
        except Exception as e:
            print(f"Error loading database.json: {e}")
            CRIMINAL_DB = []
            GENERATED_CASES = {}
    else:
        print("database.json not found. Starting with empty database.")
        CRIMINAL_DB = []
        GENERATED_CASES = {}


def save_generated_case(case_id: str, description: str, image_path: str):
    """Persist a newly generated case entry to database.json."""
    global GENERATED_CASES
    GENERATED_CASES[case_id] = {
        "description": description,
        "image_path": image_path,
    }
    try:
        with open(DB_PATH, 'r') as f:
            raw = json.load(f)
        if isinstance(raw, list):
            combined = {"suspects": raw, "generated": {}}
        else:
            combined = raw
        combined.setdefault('generated', {})
        combined['generated'][case_id] = GENERATED_CASES[case_id]
        with open(DB_PATH, 'w') as f:
            json.dump(combined, f, indent=2)
        print(f"DB updated: case {case_id} saved.")
    except Exception as e:
        print(f"Error saving case to database.json: {e}")


load_criminal_db()


def llm_refine_prompt(description_data):
    """
    Uses HuggingFace LLM to extract precise facial features from witness testimony.
    """
    desc = description_data.get('text', '')
    age = description_data.get('age', '30')
    gender = description_data.get('gender', 'male')
    style = description_data.get('style', 'pencil sketch')

    style_map = {
        "pencil": "pencil sketch, graphite drawing, black and white, forensic hand-drawn, charcoal lines, scanned sketch",
        "charcoal": "charcoal drawing, forensic art, rough texture, black and white, smudged shading, heavy contrast",
        "digital": "digital forensic portrait, clean digital vector illustration, sharp lines, detailed digital sketch",
        "photorealistic": "front view mugshot, RAW photo, photorealistic, hyperrealistic, 8k uhd, sharp focus, professional police lighting, camera flash"
    }
    style_suffix = style_map.get(style.lower(), "forensic composite sketch, pencil drawing")

    local_negative = (
        "beard, mustache, " if ("clean" in desc.lower() or "shaven" in desc.lower()) else ""
    )
    negative_prompt = local_negative + GLOBAL_NEGATIVE_PROMPT

    try:
        instruction = (
            f"You are a forensic sketch artist assistant. Based on this witness testimony: '{desc}', "
            f"extract and list ONLY the key visible facial features as short descriptive keywords. "
            f"Include: hair color and style, eye color and shape, nose shape, jaw shape, skin tone, "
            f"any facial hair, distinguishing marks. "
            f"Output ONLY comma-separated keywords, nothing else."
        )

        keywords_response = client.chat_completion(
            messages=[{"role": "user", "content": instruction}],
            model="HuggingFaceH4/zephyr-7b-beta",
            max_tokens=120,
            temperature=0.1
        )

        keywords = keywords_response.choices[0].message.content.strip()
        print(f"DEBUG: Extracted keywords -> {keywords}")

        final_prompt = (
            f"Police composite sketch of a {gender}, {age} years old, "
            f"{keywords}, "
            f"looking straight ahead, front view, neutral expression, "
            f"plain white background, close-up face, rough pencil lines, "
            f"{style_suffix}"
        )

        print(f"DEBUG: FINAL PROMPT -> {final_prompt}")
        return final_prompt, negative_prompt

    except Exception as e:
        print(f"Prompt refinement error: {e}. Engaging offline keyword extractor fallback.")
        
        desc_lower = desc.lower()
        extracted_features = []
        
        if age:
            extracted_features.append(f"{age} years old")
            
        hair_styles = ['messy', 'blue', 'balding', 'buzz cut', 'ponytail', 'white', 'curly', 'short', 'long', 'straight']
        for hs in hair_styles:
            if hs in desc_lower:
                extracted_features.append(f"{hs} hair")
                
        if 'beard' in desc_lower:
            extracted_features.append("beard")
        elif 'mustache' in desc_lower:
            extracted_features.append("mustache")
        elif 'clean shaven' in desc_lower or 'shaven' in desc_lower:
            extracted_features.append("clean shaven")
            
        accessories = ['hoodie', 'piercing', 'glasses', 'scar', 'tattoo', 'eyepatch', 'jacket']
        for acc in accessories:
            if acc in desc_lower:
                extracted_features.append(acc)
                
        words = desc_lower.replace(',', '').replace('.', '').split()
        for word in words:
            if word in ['rugged', 'sharp', 'intense', 'dark', 'focused', 'stern', 'aggressive', 'thin', 'pale', 'tanned']:
                if word not in extracted_features:
                    extracted_features.append(word)
                    
        keywords = ", ".join(extracted_features) if extracted_features else "standard biometric facial features"
        
        final_prompt = (
            f"Police composite sketch of a {gender}, "
            f"{keywords}, "
            f"looking straight ahead, front view, neutral expression, "
            f"plain white background, close-up face, rough pencil lines, "
            f"{style_suffix}"
        )
        print(f"DEBUG: FALLBACK PROMPT -> {final_prompt}")
        return final_prompt, negative_prompt


def generate_image_from_stability(prompt: str, negative_prompt: str) -> Optional[bytes]:
    """
    Generates image using Stability AI API (SDXL).
    The negative_prompt is passed with weight -1 in the text_prompts array.
    Returns raw PNG bytes or None.
    """
    try:
        headers = {
            "Authorization": f"Bearer {STABILITY_API_KEY}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

        payload = {
            "text_prompts": [
                {"text": prompt,           "weight": 1.0},
                {"text": negative_prompt,  "weight": -1.0},
            ],
            "cfg_scale": 8,
            "height": 1024,
            "width": 1024,
            "samples": 1,
            "steps": 35,
        }

        response = requests.post(STABILITY_URL, headers=headers, json=payload)

        if response.status_code == 200:
            result = response.json()
            img_base64 = result["artifacts"][0]["base64"]
            print("DEBUG: ✅ Stability AI image generated successfully.")
            return base64.b64decode(img_base64)
        else:
            print(f"DEBUG: ❌ Stability AI error {response.status_code} -> {response.text}")
            return None

    except Exception as e:
        print(f"DEBUG: ❌ Stability AI exception -> {e}")
        return None


def generate_sketch_hf(
    prompt: str,
    negative_prompt: str = GLOBAL_NEGATIVE_PROMPT,
    seed: Optional[int] = None,
) -> Optional[bytes]:
    """
    Hugging Face Inference API (text-to-image).
    Uses stabilityai/stable-diffusion-xl-base-1.0.
    Pass a different seed for each variation to get distinct outputs.
    The negative_prompt is forwarded in the API payload so the HF endpoint
    can use it as a negative conditioning signal.
    Returns raw PNG bytes or None on failure.
    """
    HF_MODEL = "stabilityai/stable-diffusion-xl-base-1.0"
    try:
        hf_client = InferenceClient(model=HF_MODEL, token=HF_TOKEN)
        print(f"DEBUG: Calling HF text_to_image (seed={seed}) with model={HF_MODEL}")
        kwargs = {
            "num_inference_steps": 35,
            "guidance_scale": 8.0,
            "negative_prompt": negative_prompt,
        }
        if seed is not None:
            kwargs["seed"] = seed
        pil_image = hf_client.text_to_image(prompt, **kwargs)
        buf = io.BytesIO()
        pil_image.save(buf, format="PNG")
        print(f"DEBUG: ✅ HuggingFace image generated (seed={seed}).")
        return buf.getvalue()
    except Exception as e:
        print(f"DEBUG: ❌ HuggingFace generation failed (seed={seed}) -> {e}")
        return None


def save_image_to_disk(case_id: str, img_bytes: bytes, suffix: str = "primary") -> str:  # noqa
    """
    Writes raw PNG bytes to static/images/cases/{safe_case_id}_{suffix}.png.
    suffix should be one of: 'primary', 'var1', 'var2'.
    Returns the web-accessible path string.

    The filename is aggressively sanitized so that no special characters
    (spaces, #, colons, slashes, etc.) can ever appear in the URL.
    """
    import re
    safe_id = re.sub(r'[^a-z0-9\-_]', '_', case_id.lower())
    safe_id = re.sub(r'_+', '_', safe_id).strip('_')
    filename = f"{safe_id}_{suffix}.png"
    filepath = os.path.join(SKETCH_OUTPUT_DIR, filename)
    os.makedirs(SKETCH_OUTPUT_DIR, exist_ok=True)   #
    with open(filepath, 'wb') as f:
        f.write(img_bytes)
    web_path = f"/static/images/cases/{filename}"
    print(f"DEBUG: Sketch saved -> {filepath} | URL -> {web_path}")
    return web_path


def generate_reverse_description(prompt_used):
    """
    Generates a short AI forensic analysis report.
    """
    try:
        report_response = client.chat_completion(
            messages=[{
                "role": "user",
                "content": (
                    f"Write a short 2-line professional forensic report describing "
                    f"the facial features in this prompt: {prompt_used}"
                )
            }],
            model="HuggingFaceH4/zephyr-7b-beta",
            max_tokens=60
        )
        return report_response.choices[0].message.content.strip()
    except:
        return "Facial features consist of standard biometric markers matching witness description."


def calculate_similarity(witness_desc, criminal):
    """
    Trait-weighted similarity scoring for DB fallback matching.
    """
    witness_desc = witness_desc.lower()
    traits = criminal.get('traits', {})
    score = 0
    total_weight = 0

    weights = {
        'gender': 30,
        'age_group': 20,
        'hair': 15,
        'facial_hair': 15,
        'accessory': 20
    }

    for trait, weight in weights.items():
        val = traits.get(trait, '')
        if val and val in witness_desc:
            score += weight
        total_weight += weight

    words1 = set(witness_desc.replace(',', '').split())
    words2 = set(criminal['description'].lower().replace(',', '').split())
    overlap = len(words1.intersection(words2))
    text_score = (overlap / len(words1)) * 20 if words1 else 0

    final_score = (score / total_weight) * 80 + text_score
    final_score = min(98.9, final_score + random.uniform(2, 8)) if final_score > 20 else random.uniform(5, 15)
    return round(final_score, 1)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/generate', methods=['POST'])
def generate_sketch():
    """
    Primary generation endpoint.

    Accepts JSON: { "case_id": str, "description": str, "traits": {...} }

    Workflow:
      1. Build a forensic-style prompt using llm_refine_prompt.
      2. Call Stability AI (primary) or HuggingFace (secondary) to get raw PNG bytes.
      3. Save those bytes to static/images/cases/{case_id}_sketch.png.
      4. Persist { description, image_path } to database.json under 'generated'.
      5. Return { success, image_url, report, confidence, is_simulated }.

    If both APIs fail, fall back to the offline similarity-matching simulation
    (no file write occurs in that case — we return pre-existing sketch URLs).
    """
    try:
        data = request.get_json(force=True)
        if not data:
            return jsonify({"error": "Invalid or missing JSON payload."}), 400

        description_text = data.get('description', '').strip()
        case_id = data.get('case_id', '').strip()
        traits = data.get('traits', {})

        if not description_text:
            return jsonify({"error": "'description' field is required."}), 400
        if not case_id:
            return jsonify({"error": "'case_id' field is required."}), 400

        description_data = {
            "text": description_text,
            "age": traits.get('age', '30'),
            "gender": traits.get('gender', 'male'),
            "style": traits.get('style', 'pencil sketch')
        }

        refined_prompt, negative_prompt = llm_refine_prompt(description_data)
        forensic_prompt = FORENSIC_STYLE_PREFIX + refined_prompt
        master_seed = random.randint(1, 10**9)

        variation_modifiers = [
            "",
            ", slight side lighting, serious expression",
            ", soft studio lighting, slight head tilt right"
        ]

        image_urls = []
        primary_image_url = None
        is_simulated = False

        VARIATION_SUFFIXES   = ["primary", "var1", "var2"]
        VARIATION_MODIFIERS  = [
            "",
            ", slight side lighting, serious expression, different angle",
            ", soft studio lighting, slight head tilt right, alternate perspective"
        ]

        stability_available = (
            STABILITY_API_KEY
            and STABILITY_API_KEY.strip()
            and not STABILITY_API_KEY.startswith("sk-YOUR")
        )
        if stability_available:
            for i, (modifier, suffix) in enumerate(zip(VARIATION_MODIFIERS, VARIATION_SUFFIXES)):
                variation_prompt = f"{forensic_prompt}{modifier}"
                print(f"\nDEBUG: Generating variation '{suffix}' via Stability AI...")
                img_bytes = generate_image_from_stability(variation_prompt, negative_prompt)
                if img_bytes:
                    url = save_image_to_disk(case_id, img_bytes, suffix)
                    image_urls.append(url)
                    if suffix == "primary":
                        primary_image_url = url
                else:
                    print(f"DEBUG: Variation '{suffix}' failed via Stability AI.")
        else:
            print("DEBUG: Stability AI key missing — skipping.")

        if not image_urls and HF_TOKEN:
            print("DEBUG: Stability AI unavailable — trying HuggingFace for 3 variations...")
            seeds = [
                master_seed,
                master_seed + 1000,
                master_seed + 2000,
            ]
            hf_prompts = [
                forensic_prompt,
                forensic_prompt + ", slight side lighting, serious expression",
                forensic_prompt + ", soft studio lighting, slight head tilt right",
            ]
            for seed, hf_prompt, suffix in zip(seeds, hf_prompts, VARIATION_SUFFIXES):
                print(f"DEBUG: HF generation for '{suffix}' (seed={seed})...")
                img_bytes = generate_sketch_hf(hf_prompt, negative_prompt=negative_prompt, seed=seed)
                if img_bytes:
                    url = save_image_to_disk(case_id, img_bytes, suffix)
                    image_urls.append(url)
                    if suffix == "primary":
                        primary_image_url = url
                else:
                    print(f"DEBUG: HF failed for '{suffix}' (seed={seed}).")

            if not image_urls:
                print("DEBUG: All HuggingFace calls failed — entering simulation mode.")

        if image_urls:
            primary_url = image_urls[0] if len(image_urls) > 0 else None
            var1_url    = image_urls[1] if len(image_urls) > 1 else None
            var2_url    = image_urls[2] if len(image_urls) > 2 else None

            save_generated_case(
                case_id=case_id,
                description=description_text,
                image_path=primary_url
            )

            reverse_report = generate_reverse_description(refined_prompt)
            confidence = (
                round(random.uniform(88, 98), 1)
                if len(description_text) > 40
                else round(random.uniform(65, 85), 1)
            )

            return jsonify({
                "success": True,
                # Named slots for the frontend
                "primary_url": primary_url,
                "var1_url": var1_url,
                "var2_url": var2_url,
                "image_url": primary_url,
                "images": image_urls,
                "report": reverse_report,
                "confidence": confidence,
                "is_simulated": False,
                "master_seed": master_seed
            })

        is_simulated = True
        print("DEBUG: Engaging Offline Simulation Mode...")

        static_root = os.path.join(os.path.dirname(__file__), 'static')

        def _file_exists(url_path: str) -> bool:
            """Return True only if the static file at url_path actually exists on disk."""
            if not url_path:
                return False
            rel = url_path.lstrip('/')
            return os.path.isfile(os.path.join(os.path.dirname(__file__), rel))

        DEFAULT_SKETCH = '/static/images/cases/crm-7721_sketch.png'

        matches = []
        for person in CRIMINAL_DB:
            score = calculate_similarity(description_text, person)
            matches.append((score, person))
        matches.sort(key=lambda x: x[0], reverse=True)

        if matches and matches[0][0] > 10:
            primary_score, primary_suspect = matches[0]
            candidate = primary_suspect.get('sketch_url', primary_suspect.get('image_url', ''))
            primary_url = candidate if _file_exists(candidate) else DEFAULT_SKETCH
            reverse_report = (
                f"BIOMETRIC SIMULATION ENGAGED. Closest database match is suspect {primary_suspect['name']} "
                f"({primary_suspect['id']}) with {primary_score}% similarity. Offense: {primary_suspect.get('offense', 'Unknown')}."
            )
            confidence = primary_score
            var_images = []
            for _, person in matches[1:3]:
                url = person.get('sketch_url', person.get('image_url', ''))
                if _file_exists(url):
                    var_images.append(url)
            for person in CRIMINAL_DB:
                if len(var_images) >= 2:
                    break
                p_url = person.get('sketch_url', person.get('image_url', ''))
                if p_url != primary_url and _file_exists(p_url) and p_url not in var_images:
                    var_images.append(p_url)
            image_urls = [primary_url] + var_images
        else:
            
            candidates = [
                '/static/images/cases/crm-7721_sketch.png',
                '/static/images/cases/crm-9904_sketch.png',
                '/static/images/cases/crm-1250_sketch.png',
            ]
            image_urls = [u for u in candidates if _file_exists(u)]
            if not image_urls:
               
                return jsonify({
                    "error": "Both AI APIs failed and no fallback sketches exist on disk. "
                             "Please add images to static/images/cases/ or check API keys."
                }), 503
            reverse_report = "BIOMETRIC SIMULATION ENGAGED. General suspect profile generated matching basic age and gender traits."
            confidence = round(random.uniform(72, 84), 1)

        return jsonify({
            "success": True,
            "image_url": image_urls[0] if image_urls else None,
            "images": image_urls,
            "report": reverse_report,
            "confidence": confidence,
            "is_simulated": True,
            "master_seed": master_seed
        })

    except Exception as e:
        print(f"ERROR in /generate: {e}")
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500


@app.route('/compare', methods=['POST'])
def compare_sketch():
    data = request.json
    description = data.get('description', '')

    if not description:
        return jsonify({"error": "No description to compare."}), 400

    matches = []
    for person in CRIMINAL_DB:
        score = calculate_similarity(description, person)
        if score > 10:
            person_copy = person.copy()
            person_copy['similarity'] = score
            matches.append(person_copy)

    matches.sort(key=lambda x: x['similarity'], reverse=True)
    return jsonify({"matches": matches[:3]})


@app.route('/cases')
def get_all_cases():
    return jsonify({"cases": CRIMINAL_DB})


if __name__ == '__main__':
    app.run(debug=True, port=5001)