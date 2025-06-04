import os, re, google.generativeai as genai
from PIL import Image
from dotenv import load_dotenv
from src.core.config import config

json_dir = 'output/data/awaiting-validation'
consumed_dir = 'output/screenshots/consumed'
model_name = config.get('image_scrape.model')

load_dotenv()
api_key = os.getenv('GOOGLE_GENAI_API_KEY')
genai.configure(api_key=api_key)
model = genai.GenerativeModel(model_name)

def extract_analysis(path: str):
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
    _extract(path, prompt)

def extract_fundamentals(path: str):
    prompt = """
    Extraia da imagem para JSON:
    1. ticker e cotação
    2. rentabiliade
    3. indicadores fundamentalistas
    4. dados sobre a empresa
    5. informações sobre a empresa
    """
    _extract(path, prompt)

def _extract(path: str, prompt: str):
    image = Image.open(path)
    print(f'extracting data, path: {path}')
    response = model.generate_content([prompt, image])
    json_path = f'{json_dir}/{_get_filename_without_extension(path)}.json'
    with open(json_path, "w") as file:
        file.write(response.text)
    consumed_path = f'{consumed_dir}/{_get_filename(path)}'
    _move_file(path, consumed_path)

def _get_filename(path: str):
    return re.match(r'.*/(.*)', path).group(1)

def _get_filename_without_extension(path: str):
    return re.match(r'.*/(.*)\.png', path).group(1)

def _move_file(src_path, dst_path):
    os.makedirs(os.path.dirname(dst_path), exist_ok=True)
    os.rename(src_path, dst_path)
