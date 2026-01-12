import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
os.environ["GOOGLE_API_KEY"] = "AIzaSyD5VWVuIyn981TOZeFycEzoX_QYm2-FYcg"
genai.configure(api_key=os.environ["GOOGLE_API_KEY"])

print("🔎 Checking available models...")
for m in genai.list_models():
    if 'generateContent' in m.supported_generation_methods:
        print(m.name)