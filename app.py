import streamlit as st
import google.generativeai as genai
import os
from dotenv import load_dotenv
import time
from PIL import Image
import io
from google.api_core import exceptions
from bs4 import BeautifulSoup

# 1. Page Config
st.set_page_config(page_title="Lecturer Pattern Detector", page_icon="🎓")

# 2. Setup API Key
with st.sidebar:
    st.header("🔑 Setup")
    load_dotenv()
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        api_key = st.text_input("Enter Google API Key", type="password")
    if api_key:
        genai.configure(api_key=api_key)
        st.success("API Key Loaded! ✅")

# 3. App Title
st.title("🎓 Lecturer Pattern Detector")
st.write("Upload past questions. (Now with Safety Unlocks & Better Cleaning)")

# 4. File Uploader
uploaded_files = st.file_uploader(
    "Drop her exam papers here:", 
    accept_multiple_files=True, 
    type=['pdf', 'jpg', 'png', 'jpeg', 'html', 'htm']
)

# 5. Analyze Button
analyze_clicked = st.button("🚀 Analyze Patterns")

if analyze_clicked:
    if not uploaded_files:
        st.warning("Please upload at least one file first! 📂")
    elif not api_key:
        st.error("Please provide an API Key in the sidebar first! 🔑")
    else:
        with st.spinner("Analyzing... (Unlocking safety filters)"):
            
            model = genai.GenerativeModel('models/gemini-2.5-flash')
            request_content = []
            
            # --- FILE PROCESSING ---
            for file in uploaded_files:
                bytes_data = file.getvalue()
                
              # A. Images (Now with Auto-Resize!)
                if file.type in ["image/jpeg", "image/png"]:
                    image = Image.open(io.BytesIO(bytes_data))
                    
                    # Resize if the image is massive (over 1024px)
                    if image.width > 1024 or image.height > 1024:
                        image.thumbnail((1024, 1024)) # Shrinks it while keeping quality
                        
                    request_content.append(image)
                    request_content.append(f"Image filename: {file.name}")
                # B. PDFs
                elif file.type == "application/pdf":
                    with open(file.name, "wb") as f:
                        f.write(bytes_data)
                    
                    uploaded_ref = genai.upload_file(file.name, mime_type="application/pdf")
                    while uploaded_ref.state.name == "PROCESSING":
                        time.sleep(1)
                        uploaded_ref = genai.get_file(uploaded_ref.name)
                        
                    request_content.append(uploaded_ref)
                    request_content.append(f"PDF filename: {file.name}")

                # C. HTML (Smart Clean)
                elif "html" in file.type or file.name.endswith(('.html', '.htm')):
                    raw_html = bytes_data.decode("utf-8", errors="ignore")
                    soup = BeautifulSoup(raw_html, 'html.parser')
                    
                    # Kill all script and style elements
                    for script in soup(["script", "style", "header", "footer", "nav", "iframe"]):
                        script.decompose()
                        
                    clean_text = soup.get_text(separator="\n").strip()
                    
                    # Only add if it actually has text!
                    if len(clean_text) > 50:
                        request_content.append(f"\n--- CONTENTS OF {file.name} ---\n{clean_text[:50000]}\n") # Limit to 50k chars to prevent overload
                    else:
                        st.warning(f"⚠️ {file.name} seems empty (it might be images-only). Skipping it.")

            # --- PROMPT ---
            prompt = """
            You are an expert academic strategist. Analyze these uploaded past questions.
            
            1. 📊 TOPIC FREQUENCY: Which topics appear in EVERY paper?
            2. ⚠️ THE PATTERN SHIFT: Are questions getting harder or more theoretical?
            3. 🎯 THE 'CHEAT CODE': What 3 topics strictly guarantee a pass?
            4. 🔮 2026 PREDICTION: Generate 3 likely questions for the next exam.
            
            Format the output nicely with headers and bullet points.
            """
            request_content.append(prompt)

            # --- SAFETY SETTINGS (THE FIX) ---
            # We explicitly tell Google NOT to block content 
            safety_settings = [
                {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
                {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
                {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
                {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
            ]

            # --- GENERATION ---
            try:
                response = model.generate_content(request_content, safety_settings=safety_settings)
                st.markdown("---")
                st.subheader("🔥 The Strategy Report")
                st.markdown(response.text)
                
            except exceptions.ResourceExhausted:
                st.error("🚦 Too much data! Try uploading fewer files.")
            except Exception as e:
                st.error(f"An error occurred: {e}")
                # Print extra debug info if it fails
                if "response" in locals() and hasattr(response, "prompt_feedback"):
                    st.write("Debug info:", response.prompt_feedback)
            
            # Cleanup PDFs
            for file in uploaded_files:
                if file.type == "application/pdf" and os.path.exists(file.name):
                    os.remove(file.name)