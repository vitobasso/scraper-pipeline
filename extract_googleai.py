import os, google.generativeai as genai
from PIL import Image
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GOOGLE_GENAI_API_KEY")
genai.configure(api_key=api_key)
# model = genai.GenerativeModel("gemini-1.5-flash")
model = genai.GenerativeModel("gemini-2.0-flash-lite")

def extract(filename: str):
    img = Image.open(filename)
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
    response = model.generate_content([prompt, img])
    print(response.text)