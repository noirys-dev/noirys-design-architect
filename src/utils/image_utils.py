import os
import io
import base64
from PIL import Image, ImageDraw, ImageFont, ImageOps
from ..config import settings

def encode_image(image_path):
    """Resizes and encodes image to base64 for API efficiency."""
    with Image.open(image_path) as img:
        img = img.convert("RGB") 
        img.thumbnail((1024, 1024)) 
        buffered = io.BytesIO()
        img.save(buffered, format="JPEG", quality=85)
        return base64.b64encode(buffered.getvalue()).decode('utf-8')

def add_text_to_image(image, text):
    """Adds high-positioned minimalist text."""
    if not text: return image
    draw = ImageDraw.Draw(image)
    
    font_path = settings.TEXT_FONT_PATH_MACOS
    if not os.path.exists(font_path): font_path = settings.TEXT_FONT_PATH_FALLBACK
    
    try:
        font = ImageFont.truetype(font_path, settings.TEXT_FONT_SIZE)
    except:
        font = ImageFont.load_default()

    text = text.replace('"', '').replace("'", "").strip()
    bbox = draw.textbbox((0, 0), text, font=font)
    w = bbox[2] - bbox[0]
    
    # Position
    pos_y = int(settings.CANVAS_HEIGHT * settings.TEXT_POS_Y_RATIO)
    pos = ((settings.CANVAS_WIDTH - w) // 2, pos_y)
    
    # Shadow for text readability
    shadow_pos = (pos[0] + 4, pos[1] + 4)
    draw.text(shadow_pos, text, font=font, fill=(0, 0, 0, 80))
    draw.text(pos, text, font=font, fill=(255, 255, 255, 255)) # White text
    return image

def assemble_final_image(background_path, screenshot_path, mockup_path, text):
    """
    Assembles the final marketing asset:
    1. Background
    2. Text
    3. Mockup Frame
    4. Screenshot fitted inside Mockup
    """
    try:
        # A. Prepare Background or Create Fallback
        if os.path.exists(background_path):
             bg = Image.open(background_path).convert("RGBA")
        else:
             print("⚠️ Background not found for assembly test. Creating dummy.")
             bg = Image.new("RGBA", (settings.CANVAS_WIDTH, settings.CANVAS_HEIGHT), (50, 50, 50, 255))

        bg = ImageOps.fit(bg, (settings.CANVAS_WIDTH, settings.CANVAS_HEIGHT))
        
        # B. Add Text
        bg = add_text_to_image(bg, text)
        
        # C. Load Screenshot & Mockup
        ss = Image.open(screenshot_path).convert("RGBA")
        
        if os.path.exists(mockup_path):
            frame = Image.open(mockup_path).convert("RGBA")
        else:
            # Create a dummy frame if not exists (for testing)
            frame = Image.new("RGBA", (1200, 2400), (0,0,0,0))
            draw = ImageDraw.Draw(frame)
            draw.rectangle((0,0,1200,2400), outline="black", width=20)

        # --- MOCKUP FITTING LOGIC ---
        MOCKUP_SCREEN_W = int(frame.width * settings.MOCKUP_SCREEN_W_RATIO)
        MOCKUP_SCREEN_H = int(frame.height * settings.MOCKUP_SCREEN_H_RATIO)
        
        # Resize Screenshot to Fit Frame
        ss_resized = ss.resize((MOCKUP_SCREEN_W, MOCKUP_SCREEN_H), Image.Resampling.LANCZOS)
        
        # Rounded Corners
        mask = Image.new("L", ss_resized.size, 0)
        ImageDraw.Draw(mask).rounded_rectangle((0,0)+ss_resized.size, radius=settings.RADIUS, fill=255)
        ss_resized.putalpha(mask)
        
        # Composition
        comp = Image.new("RGBA", frame.size, (0,0,0,0))
        
        # Center Screenshot in Frame
        offset_x = (frame.width - ss_resized.width) // 2
        
        # Vertical Adjustment (Manual Offset)
        base_offset_y = (frame.height - ss_resized.height) // 2
        offset_y = int(base_offset_y) + settings.MOCKUP_OFFSET_Y 
        
        comp.paste(ss_resized, (offset_x, offset_y), ss_resized)
        
        # Overlay Frame
        comp.paste(frame, (0,0), frame)
        
        # Resize Composition for Canvas
        render_w = int(settings.CANVAS_WIDTH * settings.SCALE_RATIO) 
        render_h = int(comp.height * (render_w/comp.width))
        final_mock = comp.resize((render_w, render_h), Image.Resampling.LANCZOS)
        
        # Place Composition on Canvas
        paste_x = (settings.CANVAS_WIDTH - render_w) // 2
        paste_y = (settings.CANVAS_HEIGHT - render_h) // 2 + 150 # Shift down slightly
        
        bg.alpha_composite(final_mock, (paste_x, paste_y))
        
        return bg
        
    except Exception as e:
        print(f"❌ Image Assembly Error: {e}")
        return None
