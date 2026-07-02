from groq import Groq
from app.core import config

def get_groq_client():
    client = Groq(api_key=config.GROQ_API_KEY)
    return client