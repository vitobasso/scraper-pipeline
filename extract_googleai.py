import google.generativeai as genai
from PIL import Image
from dotenv import load_dotenv
import os

load_dotenv()
api_key = os.getenv("GOOGLE_GENAI_API_KEY")
genai.configure(api_key=api_key)
# model = genai.GenerativeModel("gemini-1.5-flash")
model = genai.GenerativeModel("gemini-2.0-flash-lite")

def extract(filename: str):
    img = Image.open(filename)
    prompt = """
    Extract buy/hold/sell values and low/average/high price forecasts from this image.
    Return JSON with plain ints or floats.
    """
    response = model.generate_content([prompt, img])
    print(response.text)