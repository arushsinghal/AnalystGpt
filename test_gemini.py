import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

# Configure the Gemini API
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

try:
    # Test the Gemini API
    model = genai.GenerativeModel('gemini-2.5-flash-lite')
    response = model.generate_content("Hello, world!")
    
    print("✅ Gemini API Key Works!")
    print("Response:", response.text)

except Exception as e:
    print("❌ Error using Gemini API key:", e) 