import os
import glob
import google.generativeai as genai
from dotenv import load_dotenv
import time

# 1. Setup
load_dotenv()
os.environ["GOOGLE_API_KEY"] = "AIzaSyD5VWVuIyn981TOZeFycEzoX_QYm2-FYcg"
genai.configure(api_key=os.environ["GOOGLE_API_KEY"])

def analyze_robust():
    print("📂 Looking for Exam Papers...")
    
    request_content = []
    found_count = 0
    
    # Files to look for
    all_files = []
    for ext in ['*.jpg', '*.jpeg', '*.png', '*.pdf', '*.html']:
        all_files.extend(glob.glob(ext))

    if not all_files:
        print("❌ No files found.")
        return

    print(f"👀 Found {len(all_files)} files. Processing one by one...")

    # 2. Process Files (With Safety Nets)
    model = genai.GenerativeModel('models/gemini-2.5-flash')

    for path in all_files:
        print(f"\n   👉 Processing: {path}...")
        
        try:
            # CHECK 1: HTML Files (Read Text Locally)
            if path.lower().endswith(".html") or path.lower().endswith(".htm"):
                with open(path, "r", encoding="utf-8", errors="ignore") as f:
                    text_data = f.read()
                    request_content.append(f"\n\n--- HTML FILE: {path} ---\n{text_data}\n")
                    print("      ✅ Read HTML successfully.")
                    found_count += 1
            
            # CHECK 2: Images & PDFs (Upload to Cloud)
            else:
                # Determine type
                m_type = "application/pdf" if path.lower().endswith(".pdf") else "image/jpeg"
                
                # Upload with a retry loop
                print("      ☁️  Uploading to AI brain... (Please wait)")
                file_ref = genai.upload_file(path=path, mime_type=m_type, display_name=path)
                
                # Wait for the file to be ready (Critical for PDFs)
                while file_ref.state.name == "PROCESSING":
                    print(".", end="", flush=True)
                    time.sleep(1)
                    file_ref = genai.get_file(file_ref.name)

                request_content.append(file_ref)
                request_content.append(f"Above is file: {path}")
                print("      ✅ Upload Complete.")
                found_count += 1

        except Exception as e:
            print(f"      ❌ FAILED to process {path}.")
            print(f"      ⚠️ Reason: {e}")
            print("      ➡️ Skipping this file and moving to the next...")

    # 3. The Analysis
    if found_count == 0:
        print("\n❌ Could not process any files successfully. Check your internet.")
        return

    print(f"\n🚀 Sending {found_count} successful files to the Analyst...")
    
    prompt = """
    You are an expert academic strategist. I have uploaded past questions.
    Some files might be missing if they failed to upload, so work with what you have.
    
    1. TREND ANALYSIS: What topics appear in these specific files?
    2. THE PATTERN SHIFT: Are the questions getting harder?
    3. THE 'CHEAT CODE': What 3 topics strictly guarantee a pass?
    4. 2026 PREDICTION: Generate 3 specific questions likely to appear this year.
    """
    request_content.append(prompt)

    try:
        response = model.generate_content(request_content)
        print("\n" + "="*40)
        print("🔥 THE ULTIMATE STRATEGY REPORT 🔥")
        print("="*40)
        print(response.text)
    except Exception as e:
        print(f"\n❌ Analysis Failed: {e}")

if __name__ == "__main__":
    analyze_robust()