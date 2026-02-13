from groq import Groq
from ..config import settings
from ..utils.image_utils import encode_image
import json

client = Groq(api_key=settings.GROQ_API_KEY)

def analyze_with_design_intelligence(image_path):
    """
    Acts as the 'Architect'. Looks at UI, decides the Category and Vibe.
    """
    print("🧠 Noirys Intelligence (Groq): Analyzing Category & Vibe...")
    
    system_prompt = """
    You are an Expert AI Art Director for App Store Optimization.
    TASK:
    1. Look at the UI screenshot. Identify the App Category (e.g., Chat, Fintech, Fitness).
    2. Identify the Primary Color vibe.
    3. Generate a 'Background Generation Prompt' for an image generator.

    CRITICAL RULES:
    - The background prompt must be for an ABSTRACT texture/environment.
    - NEVER describe the UI elements (no "phone", "buttons", "text", "people").
    - Focus on the *feeling* of the category.

    OUTPUT JSON ONLY:
    {
        "app_category": "string (e.g., 'Messenger App')",
        "background_prompt": "string (The abstract prompt for the AI generator)",
        "headline": "string (Marketing hook, max 4 words)"
    }
    """
    
    try:
        base64_image = encode_image(image_path)
        messages = [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": system_prompt},
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"},
                    },
                ],
            }
        ]

        chat_completion = client.chat.completions.create(
            messages=messages,
            model=settings.GROQ_MODEL, 
            temperature=0.5, 
            max_tokens=512,
            response_format={"type": "json_object"},
        )
        
        content = chat_completion.choices[0].message.content
        data = json.loads(content)
        
        return {
            "category": data.get("app_category", "App"),
            "prompt": data.get("background_prompt", "soft abstract gradient"),
            "headline": data.get("headline", "App Showcase")
        }, None

    except Exception as e:
        print(f"⚠️ Analysis Failed: {e}")
        return {"category": "General", "prompt": "soft studio lighting abstract background", "headline": "App View"}, str(e)
