import os
import requests
import random
import urllib.parse
import base64
from ..config import settings

def generate_image_freepik(analysis_data, save_path):
    """
    Acts as the 'Painter'. Uses the architect's data to paint a safe background.
    """
    if not settings.FREEPIK_API_KEY: return False
    
    category = analysis_data['category']
    visual_prompt = analysis_data['prompt']
    
    print(f"   🎨 Noirys Engine: Generating background for '{category}'...")

    # SAFETY INJECTION PROMPT
    final_prompt = (
        f"abstract professional showcase background for a {category} app. "
        f"{visual_prompt}. "
        "high quality, 8k, soft studio lighting, minimalist, "
        "defocused, blurry, bokeh effect. "
        "NO text, NO ui elements, NO devices, NO people, NO faces, NO screens."
    )

    url = "https://api.freepik.com/v1/ai/text-to-image"
    headers = {
        "x-freepik-api-key": settings.FREEPIK_API_KEY,
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    
    payload = {
        "prompt": final_prompt,
        "image": {
            "size": "portrait_9_16", 
            "num_imgs": 1
        }
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=60)
        if response.status_code == 200:
            data = response.json()
            if "data" in data and len(data["data"]) > 0:
                b64_data = data["data"][0]["base64"]
                with open(save_path, "wb") as f:
                    f.write(base64.b64decode(b64_data))
                return True
        else:
            print(f"   ⚠️ Freepik Error: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"   ❌ Freepik request failed: {e}")
    return False

def generate_image_flux(analysis_data, save_path):
    print("   ⏳ Falling back to Flux...")
    prompt = analysis_data['prompt']
    full_prompt = f"abstract background texture, {prompt}, soft lighting, 8k, no text --v 6.0"
    safe_prompt = urllib.parse.quote(full_prompt)
    seed = random.randint(0, 99999)
    url = f"https://image.pollinations.ai/prompt/{safe_prompt}?width=1024&height=1792&seed={seed}&nologo=true&model=flux"
    
    try:
        r = requests.get(url, timeout=45)
        if r.status_code == 200:
            with open(save_path, "wb") as f: f.write(r.content)
            return True
    except: return False
    return False
