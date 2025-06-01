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
    A imagem contem fundamentos de uma acao
    Extraia os seguintes valores DA IMAGEM, nao do seu conhecimento do passado, e retorne JSON:
        ticker
        cotacao
        P/L
        P/VP
        DY
    """
    _extract(filename, prompt)

def _extract(filename: str, prompt: str):
    img = Image.open(filename)
    response = model.generate_content([prompt, img])
    print(response.text)