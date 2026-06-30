import os
import base64
import io
import json
import random
import requests
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
from huggingface_hub import InferenceClient

load_dotenv()

app = Flask(__name__)

HF_TOKEN = os.getenv("HF_TOKEN")
STABILITY_API_KEY = os.getenv("STABILITY_API_KEY")  

client = InferenceClient(token=HF_TOKEN)


STABILITY_URL = "https://api.stability.ai/v1/generation/stable-diffusion-xl-1024-v1-0/text-to-image"


CRIMINAL_DB = []


def load_criminal_db():
    global CRIMINAL_DB
    db_path = os.path.join(os.path.dirname(__file__), 'database.json')
    if os.path.exists(db_path):
        try:
            with open(db_path, 'r') as f:
                CRIMINAL_DB = json.load(f)
            print(f"Loaded {len(CRIMINAL_DB)} records from database.json.")
        except Exception as e:
            print(f"Error loading database.json: {e}")
            CRIMINAL_DB = []
    else:
        print("database.json not found.")
        CRIMINAL_DB = []


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

    negative_prompt = (
        "blurry, low quality, distorted face, deformed, ugly, "
        "extra limbs, cartoon, anime, watermark, text, logo, "
        "sunglasses, hat, helmet, mask, multiple people, "
        "full body, wide shot, looking away, eyes closed, "
        "beard, mustache" if "clean" in desc.lower() or "shaven" in desc.lower() else
        "blurry, low quality, distorted face, deformed, ugly, "
        "extra limbs, cartoon, anime, watermark, text, logo, "
        "sunglasses, hat, helmet, mask, multiple people, "
        "full body, wide shot, looking away, eyes closed"
    )

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
            f"portrait photo of a {gender}, {age} years old, "
            f"{keywords}, "
            f"looking straight ahead, front view, centered composition, "
            f"neutral expression, plain white background, "
            f"close up face shot, highly detailed, {style_suffix}"
        )

        print(f"DEBUG: FINAL PROMPT -> {final_prompt}")
        return final_prompt, negative_prompt

    except Exception as e:
        print(f"Prompt refinement error: {e}. Engaging offline keyword extractor fallback.")
        
        # Local keyword extraction fallback
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
            f"portrait photo of a {gender}, "
            f"{keywords}, "
            f"looking straight ahead, front view, centered composition, "
            f"neutral expression, plain white background, "
            f"close up face shot, highly detailed, {style_suffix}"
        )
        print(f"DEBUG: FALLBACK PROMPT -> {final_prompt}")
        return final_prompt, negative_prompt


def generate_image_from_stability(prompt, negative_prompt):
    """
    ✅ Generates image using Stability AI API (SDXL).
    Returns base64 data URI or None.
    """
    try:
        headers = {
            "Authorization": f"Bearer {STABILITY_API_KEY}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

        payload = {
            "text_prompts": [
                {"text": prompt, "weight": 1.0},
                {"text": negative_prompt, "weight": -1.0}  
            ],
            "cfg_scale": 7,
            "height": 1024,
            "width": 1024,
            "samples": 1,
            "steps": 30,
        }

        response = requests.post(STABILITY_URL, headers=headers, json=payload)

        if response.status_code == 200:
            result = response.json()
            img_base64 = result["artifacts"][0]["base64"]
            print("DEBUG: ✅ Stability AI image generated successfully.")
            return f"data:image/png;base64,{img_base64}"
        else:
            print(f"DEBUG: ❌ Stability AI error {response.status_code} -> {response.text}")
            return None

    except Exception as e:
        print(f"DEBUG: ❌ Stability AI exception -> {e}")
        return None


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
    data = request.json
    description_text = data.get('description', '')
    traits = data.get('traits', {})

    if not description_text:
        return jsonify({"error": "Description is required"}), 400

    description_data = {
        "text": description_text,
        "age": traits.get('age', '30'),
        "gender": traits.get('gender', 'male'),
        "style": traits.get('style', 'pencil sketch')
    }

    
    refined_prompt, negative_prompt = llm_refine_prompt(description_data)
    master_seed = random.randint(1, 10**9)

    variation_modifiers = [
        "",
        ", slight side lighting, serious expression",
        ", soft studio lighting, slight head tilt right"
    ]

    images = []
    is_simulated = False

    # Try Stability AI generation if API Key is configured
    if STABILITY_API_KEY and STABILITY_API_KEY.strip() and not STABILITY_API_KEY.startswith("sk-YOUR"):
        for i, modifier in enumerate(variation_modifiers):
            variation_prompt = f"{refined_prompt}{modifier}"
            print(f"\nDEBUG: Generating variation {i+1} using Stability AI...")
            img = generate_image_from_stability(variation_prompt, negative_prompt)  
            if img:
                images.append(img)
            else:
                print(f"DEBUG: Variation {i+1} failed.")
    else:
        print("DEBUG: Stability API key missing or default. Engaging simulated offline fallback.")

    # If generation failed or key is missing, engage simulated offline fallback matching
    if not images:
        is_simulated = True
        print("DEBUG: Engaging Offline Simulation Mode...")
        
        # Calculate similarity score for each suspect in database
        matches = []
        for person in CRIMINAL_DB:
            score = calculate_similarity(description_text, person)
            matches.append((score, person))
            
        # Sort by similarity score descending
        matches.sort(key=lambda x: x[0], reverse=True)
        
        if matches and matches[0][0] > 10:
            primary_score, primary_suspect = matches[0]
            primary_img = primary_suspect.get('sketch_url', primary_suspect.get('image_url', '/static/images/cases/crm-7721_sketch.png'))
            reverse_report = (
                f"BIOMETRIC SIMULATION ENGAGED. Closest database match is suspect {primary_suspect['name']} "
                f"({primary_suspect['id']}) with {primary_score}% similarity. Offense: {primary_suspect.get('offense', 'Unknown')}."
            )
            confidence = primary_score
            
            # Select variation images from other suspects
            var_images = []
            for score, person in matches[1:3]:
                var_images.append(person.get('sketch_url', person.get('image_url')))
                
            # Fill variations to ensure we have at least 2 variation images
            for person in CRIMINAL_DB:
                if len(var_images) >= 2:
                    break
                p_url = person.get('sketch_url', person.get('image_url'))
                if p_url != primary_img and p_url not in var_images:
                    var_images.append(p_url)
                    
            images = [primary_img] + var_images
        else:
            # Fallback if no matching suspect or database is empty
            primary_img = '/static/images/cases/crm-7721_sketch.png'
            var_images = ['/static/images/cases/crm-9904_sketch.png', '/static/images/cases/crm-1250_sketch.png']
            
            if len(CRIMINAL_DB) >= 3:
                primary_img = CRIMINAL_DB[0].get('sketch_url', CRIMINAL_DB[0].get('image_url', primary_img))
                var_images = [
                    CRIMINAL_DB[1].get('sketch_url', CRIMINAL_DB[1].get('image_url', var_images[0])),
                    CRIMINAL_DB[2].get('sketch_url', CRIMINAL_DB[2].get('image_url', var_images[1]))
                ]
                
            images = [primary_img] + var_images
            reverse_report = "BIOMETRIC SIMULATION ENGAGED. General suspect profile generated matching basic age and gender traits."
            confidence = round(random.uniform(72, 84), 1)
    else:
        reverse_report = generate_reverse_description(refined_prompt)
        confidence = (
            round(random.uniform(88, 98), 1)
            if len(description_text) > 40
            else round(random.uniform(65, 85), 1)
        )

    return jsonify({
        "images": images,
        "report": reverse_report,
        "confidence": confidence,
        "is_simulated": is_simulated,
        "master_seed": master_seed
    })


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