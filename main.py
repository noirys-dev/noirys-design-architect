import os
import time
import json
import random
import requests
import datetime
import google.generativeai as genai
from PIL import Image, ImageDraw, ImageOps, ImageFont
import urllib.parse
from dotenv import load_dotenv

# --- CONFIGURATION ---
load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    print("❌ ERROR: API Key not found!")
    exit()

BASE_DIR = "/Users/yaseminkir/projects/noirys-design-architect"
ASSETS_DIR = os.path.join(BASE_DIR, "assets")
OUT_DIR = os.path.join(BASE_DIR, "outputs")
DATA_DIR = os.path.join(BASE_DIR, "data", "logs")
GEN_BG_DIR = os.path.join(ASSETS_DIR, "backgrounds", "ai_generated")
SS_DIR = os.path.join(ASSETS_DIR, "screenshots")
MOCKUP_PATH = os.path.join(ASSETS_DIR, "mockups", "device_frame.png")

# --- MODEL SETUP (BANANA PRO) ---
genai.configure(api_key=API_KEY)
MODEL_NAME = 'models/nano-banana-pro-preview' 
model = genai.GenerativeModel(MODEL_NAME)

CANVAS_WIDTH, CANVAS_HEIGHT = 1290, 2796
SCALE_RATIO, RADIUS = 0.95, 110 
BATCH_LIMIT = 3

# --- LOGGING ---
def log_transaction(data):
    if not os.path.exists(DATA_DIR): os.makedirs(DATA_DIR)
    log_file = os.path.join(DATA_DIR, "history.json")
    try:
        with open(log_file, "r", encoding="utf-8") as f: history = json.load(f)
    except: history = [] 
    data["timestamp"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    history.append(data)
    with open(log_file, "w", encoding="utf-8") as f:
        json.dump(history, f, indent=4, ensure_ascii=False)

def add_text_to_image(image, text):
    """Adds high-positioned minimalist text."""
    if not text: return image
    draw = ImageDraw.Draw(image)
    font_path = "/System/Library/Fonts/SFNS.ttf" 
    if not os.path.exists(font_path): font_path = "/Library/Fonts/Helvetica.ttc"
    
    try:
        font = ImageFont.truetype(font_path, 95)
    except:
        font = ImageFont.load_default()

    text = text.replace('"', '').replace("'", "").strip()
    bbox = draw.textbbox((0, 0), text, font=font)
    w = bbox[2] - bbox[0]
    # Positioned at 7% height for that "high-header" look
    pos = ((CANVAS_WIDTH - w) // 2, int(CANVAS_HEIGHT * 0.07))
    draw.text(pos, text, font=font, fill=(50, 50, 55, 255))
    return image

def analyze_with_banana_stealth(image_path):
    """Analyzes UI with image resizing to avoid 429 errors."""
    print("🧠 Banana Pro: Optimized Analysis...")
    prompt = "Act as a Senior Product Designer. Analyze this UI. 1. Background: describe a minimal airy pastel abstract prompt. 2. Title: 3-4 word professional title (Title Case). Output ONLY: PROMPT: [text] COPY: [text]"
    
    try:
        img = Image.open(image_path)
        # RESIZING: Reduces token usage significantly to stay under quota
        img.thumbnail((800, 800)) 
        
        response = model.generate_content([prompt, img])
        res = response.text
        bg_p = res.split("PROMPT:")[1].split("COPY:")[0].strip()
        copy_t = res.split("COPY:")[1].strip()
        return bg_p, copy_t, None
    except Exception as e:
        return "soft white abstract gradient", "Minimal Design", str(e)

def generate_image_flux(prompt, save_path):
    """Generates the background via Pollinations."""
    safe_prompt = prompt.replace("\n", " ")[:250]
    encoded = urllib.parse.quote(safe_prompt)
    seed = random.randint(0, 99999)
    url = f"https://image.pollinations.ai/prompt/{encoded}?width=1024&height=1792&seed={seed}&nologo=true&model=flux"
    try:
        r = requests.get(url, timeout=45)
        if r.status_code == 200:
            with open(save_path, "wb") as f: f.write(r.content)
            return True
    except: return False
    return False

def main():
    if not os.path.exists(OUT_DIR): os.makedirs(OUT_DIR)
    if not os.path.exists(GEN_BG_DIR): os.makedirs(GEN_BG_DIR)
    
    all_files = sorted([f for f in os.listdir(SS_DIR) if f.lower().endswith(('.png', '.jpg'))])
    ss_files = all_files[:BATCH_LIMIT]
    
    frame = Image.open(MOCKUP_PATH).convert("RGBA")

    for i, ss_name in enumerate(ss_files):
        print(f"\n🚀 [{i+1}/{len(ss_files)}] Processing: {ss_name}")
        ss_path = os.path.join(SS_DIR, ss_name)
        start_time = time.time()
        
        # 1. ANALYZE (Optimized)
        bg_prompt, copy_text, err = analyze_with_banana_stealth(ss_path)
        
        # 2. GENERATE BACKGROUND
        bg_filename = f"bg_banana_{ss_name}"
        bg_path = os.path.join(GEN_BG_DIR, bg_filename)
        
        if not os.path.exists(bg_path):
            generate_image_flux(bg_prompt, bg_path)
            time.sleep(5) 
        
        # 3. ASSEMBLY
        status = "failed"
        try:
            bg = Image.open(bg_path).convert("RGBA")
            bg = ImageOps.fit(bg, (CANVAS_WIDTH, CANVAS_HEIGHT))
            bg = add_text_to_image(bg, copy_text)
            
            ss = Image.open(ss_path).convert("RGBA")
            target_h = int(frame.height * 0.96)
            ss_resized = ss.resize((int(ss.width * (target_h/ss.height)), target_h), Image.Resampling.LANCZOS)
            
            mask = Image.new("L", ss_resized.size, 0)
            ImageDraw.Draw(mask).rounded_rectangle((0,0)+ss_resized.size, radius=RADIUS, fill=255)
            ss_resized.putalpha(mask)
            
            comp = Image.new("RGBA", frame.size, (0,0,0,0))
            offset_x, offset_y = (frame.width - ss_resized.width) // 2, (frame.height - ss_resized.height) // 2
            comp.paste(ss_resized, (offset_x, offset_y), ss_resized)
            comp.paste(frame, (0,0), frame)
            
            render_w = int(CANVAS_WIDTH * SCALE_RATIO) 
            final_h = int(comp.height * (render_w/comp.width))
            final_mock = comp.resize((render_w, final_h), Image.Resampling.LANCZOS)
            
            bg.alpha_composite(final_mock, ((CANVAS_WIDTH - render_w)//2, (CANVAS_HEIGHT - final_h)//2 + 150))
            
            bg.save(os.path.join(OUT_DIR, f"Noirys_Final_{ss_name}"))
            print(f"✅ Success: {copy_text}")
            status = "success"
        except Exception as e:
            print(f"❌ Assembly Error: {e}")
            err = str(e)

        log_transaction({
            "input": ss_name,
            "copy": copy_text,
            "status": status,
            "error": err if err else "none"
        })

        if i < len(ss_files) - 1:
            print("⏳ Cooldown to prevent 429... 60 seconds.")
            time.sleep(60)

if __name__ == "__main__":
    main()