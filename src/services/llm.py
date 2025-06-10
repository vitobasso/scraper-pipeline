import os, google.generativeai as genai
from dotenv import load_dotenv
from src.config import visual_llm_model as model_name

_model = None


def llm():
    if not _model:
        _init()
    return _model


def _init():
    load_dotenv()
    api_key = os.getenv('GOOGLE_GENAI_API_KEY')
    genai.configure(api_key=api_key)
    global _model
    _model = genai.GenerativeModel(model_name)
