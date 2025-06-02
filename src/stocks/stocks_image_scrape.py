import os, google.generativeai as genai
from PIL import Image
from dotenv import load_dotenv
from src.core.config import config

model_name = config.get('image_scrape.model')
load_dotenv()
api_key = os.getenv('GOOGLE_GENAI_API_KEY')
genai.configure(api_key=api_key)
model = genai.GenerativeModel(model_name)

def extract_analysis(filename: str):
    prompt = """
    Extract from image and return JSON with following properties:
    - analyst rating (int values)
        buy
        hold
        sell
        strong buy (optional)
        strong sell (optional)
    - price forecast (float values)
        min (aka low)
        avg
        max (aka high)
    """
    _extract(filename, prompt)

def extract_fundamentals(filename: str):
    prompt = """
    Extraia da imagem para JSON:
    1. ticker e cotação
    2. rentabiliade
    3. indicadores fundamentalistas
    4. dados sobre a empresa
    5. informações sobre a empresa
    """
    _extract(filename, prompt)

def _extract(filename: str, prompt: str):
    img = Image.open(filename)
    response = model.generate_content([prompt, img])
    print(response.text)