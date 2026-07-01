from google import genai
from app.core import config

def get_gemini_model():
    client = genai.Client(api_key=config.GOOGLE_API_KEY)
    return client