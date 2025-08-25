import os
from functools import cache

import google.generativeai as genai
from dotenv import load_dotenv

from src.config import visual_llm_model as model_name


@cache
def llm():
    load_dotenv()
    api_key = os.getenv("GOOGLE_GENAI_API_KEY")
    if not api_key:
        raise ValueError("GOOGLE_GENAI_API_KEY not found")
    genai.configure(api_key=api_key)
    return genai.GenerativeModel(model_name)
