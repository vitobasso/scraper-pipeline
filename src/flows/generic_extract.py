import os, re, google.generativeai as genai
from PIL import Image
from dotenv import load_dotenv
from src.core.config import config

json_dir = 'output/data/awaiting-validation'
consumed_dir = 'output/screenshots/consumed'
model_name = config.get('image_extract.model')

load_dotenv()
api_key = os.getenv('GOOGLE_GENAI_API_KEY')
genai.configure(api_key=api_key)
model = genai.GenerativeModel(model_name)

def extract_analysis(image_path: str):
    prompt = f"""
    1. analyst_rating (int):
       - strong_buy (optional)
       - buy
       - hold
       - sell
       - strong_sell (optional)
    2. price_forecast (float values)
       - min (aka low)
       - avg
       - max (aka high)
    """
    _extract_json(image_path, prompt)

def _extract_json(image_path: str, prompt_json_properties: str):
    prompt = f"""
    Extract the following data as raw JSON.
    Do not use any markdown formatting or backticks.
    Partial data is okay.
    
    {prompt_json_properties}
    
    If extraction fails entirely, reply with:
    ERROR: <reason, 5 or less words>
    """
    _extract(image_path, prompt)

def _extract(image_path: str, prompt: str):
    image = Image.open(image_path)
    print(f'extracting data, path: {image_path}')
    response = model.generate_content([prompt, image])
    json_path = f'{json_dir}/{_get_filename_without_extension(image_path)}.json'
    with open(json_path, "w") as file:
        file.write(response.text)
    consumed_path = f'{consumed_dir}/{_get_filename(image_path)}'
    _move_file(image_path, consumed_path)

def _get_filename(path: str):
    return re.match(r'.*/(.*)', path).group(1)

def _get_filename_without_extension(path: str):
    return re.match(r'.*/(.*)\.png', path).group(1)

def _move_file(src_path, dst_path):
    os.makedirs(os.path.dirname(dst_path), exist_ok=True)
    os.rename(src_path, dst_path)
