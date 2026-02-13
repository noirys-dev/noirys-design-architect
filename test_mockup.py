import os
import time
from src.config import settings
from src.utils.logging_utils import ensure_directories_exist
from src.utils.image_utils import assemble_final_image
from PIL import Image, ImageDraw

def test_mockup_fit():
    """
    Test mockup fitting without using external APIs.
    Creates dummy assets and assembles them.
    """
    print("\n🧪 STARTING MOCKUP FIT TEST (OFFLINE MODE)\n")
    ensure_directories_exist()
    
    # 1. Use Real Screenshot (ss2.png)
    dummy_ss_path = os.path.join(settings.SS_DIR, "ss2.png")
    
    if not os.path.exists(dummy_ss_path):
        print(f"❌ ERROR: {dummy_ss_path} not found!")
        return

    print(f"   📱 Using Screenshot: {dummy_ss_path}")
    
    # 2. Create Dummy Background
    dummy_bg_path = "test_background.png"
    print("   🎨 Creating Dummy Background...")
    bg = Image.new("RGB", (settings.CANVAS_WIDTH, settings.CANVAS_HEIGHT), (30, 30, 30)) # Dark Grey
    bg.save(dummy_bg_path)
    
    # 3. Assemble
    print("   🔧 Assembling Mockup...")
    try:
        final_img = assemble_final_image(
            dummy_bg_path, 
            dummy_ss_path, 
            settings.MOCKUP_PATH, 
            "MOCKUP FIT TEST"
        )
        
        if final_img:
            output_path = "test_output_fit.png"
            final_img.save(output_path)
            print(f"   ✅ TEST SUCCESS: Saved to {output_path}")
            print("   👉 Please check 'test_output_fit.png' to verify fitting.")
        else:
            print("   ❌ TEST FAILED: Assembly returned None.")
            
    except Exception as e:
        print(f"   ❌ TEST ERROR: {e}")
    finally:
        # Cleanup
        if os.path.exists(dummy_bg_path): os.remove(dummy_bg_path)

if __name__ == "__main__":
    test_mockup_fit()
