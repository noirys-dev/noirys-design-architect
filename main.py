import os
import time
from src.config import settings
from src.utils.logging_utils import ensure_directories_exist, log_transaction
from src.utils.image_utils import assemble_final_image
from src.services.analysis_service import analyze_with_design_intelligence
from src.services.generation_service import generate_image_freepik, generate_image_flux
from PIL import Image

def main():
    ensure_directories_exist()
    
    # Check Screens
    all_files = sorted([f for f in os.listdir(settings.SS_DIR) if f.lower().endswith(('.png', '.jpg', '.jpeg'))])
    ss_files = all_files[:settings.BATCH_LIMIT]
    
    if not ss_files:
        print("No screenshots found in assets/screenshots/")
        return

    # Mockup Check
    if not os.path.exists(settings.MOCKUP_PATH):
        print("⚠️ Mockup frame not found in assets/mockups/. Mockup functionality will be limted.")

    for i, ss_name in enumerate(ss_files):
        print(f"\n🚀 [{i+1}/{len(ss_files)}] Processing: {ss_name}")
        ss_path = os.path.join(settings.SS_DIR, ss_name)
        
        # 1. ANALYZE
        analysis_result, err = analyze_with_design_intelligence(ss_path)
        
        copy_text = analysis_result['headline']
        print(f"   📋 Category: {analysis_result['category']}")
        print(f"   📝 Headline: {copy_text}")
        print(f"   🎨 Vibe Prompt: {analysis_result['prompt'][:60]}...")
        
        # 2. GENERATE
        bg_filename = f"bg_noirys_{ss_name}"
        bg_path = os.path.join(settings.GEN_BG_DIR, bg_filename)
        
        if not os.path.exists(bg_path):
            success = generate_image_freepik(analysis_result, bg_path)
            if not success:
                success = generate_image_flux(analysis_result, bg_path)
                
            if not success:
                print("   ⚠️ Generation failed. Skipping assembly.")
                continue
        else:
             print("   ⚡ Using cached background.")
        
        # 3. ASSEMBLY
        try:
            final_img = assemble_final_image(bg_path, ss_path, settings.MOCKUP_PATH, copy_text)
            
            if final_img:
                final_path = os.path.join(settings.OUT_DIR, f"Noirys_Final_{ss_name}")
                final_img.save(final_path)
                print(f"   ✅ Saved: {final_path}")
                
                log_transaction({
                    "input": ss_name,
                    "category": analysis_result['category'],
                    "status": "success",
                    "error": "none"
                })
            else:
                 print("   ❌ Assembly Failed: Image object is None")

        except Exception as e:
            print(f"   ❌ Assembly Error: {e}")

        if i < len(ss_files) - 1:
            print("⏳ Cooldown... 10s")
            time.sleep(10)

if __name__ == "__main__":
    main()