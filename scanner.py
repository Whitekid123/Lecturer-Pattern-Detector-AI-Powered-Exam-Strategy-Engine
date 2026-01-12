import os
import google.generativeai as genai
from dotenv import load_dotenv

# 1. Setup
# PASTE YOUR KEY BELOW inside the quotes
os.environ["GOOGLE_API_KEY"] = "AIzaSyD5VWVuIyn981TOZeFycEzoX_QYm2-FYcg"
genai.configure(api_key=os.environ["GOOGLE_API_KEY"])

def analyze_question_paper(file_path):
    print(f"👀 Analyzing {file_path}...")
    
    # Check if file exists to prevent errors
    if not os.path.exists(file_path):
        print(f"❌ Error: I can't find the file named '{file_path}'")
        print("Make sure the image is in the same folder as this script!")
        return

    # 2. Upload the file to Gemini
    # We use a generic mime_type, Gemini usually figures it out
    sample_file = genai.upload_file(path=file_path, display_name="Past Question")

    # 3. The Model (Flash is fast and cheap)
    model = genai.GenerativeModel('models/gemini-2.5-flash')

    # 4. The Prompt (The Magic)
    prompt = """
Analyze this past question paper image.
1. Extract all the questions text.
2. Identify the top 3 topics that appear most frequently.
3. Note if the questions are mostly 'Calculation' based or 'Theory' based.
4. Predict what might come out next based on these patterns.
"""

    response = model.generate_content([sample_file, prompt])
    
    print("\n--- 🧠 ANALYSIS RESULT ---")
    print(response.text)

# Run it
if __name__ == "__main__":
    # CHANGE 'test.jpg' to the actual name of your image file
    analyze_question_paper("test.jpg")