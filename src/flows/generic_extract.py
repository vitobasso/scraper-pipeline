import os, google.generativeai as genai
from PIL import Image
from dotenv import load_dotenv
from src.config import output_dir, visual_llm_model as model_name
from src.core.util import mkdir

data_dir = mkdir(f'{output_dir}/data/awaiting-validation')
consumed_dir = mkdir(f'{output_dir}/screenshots/consumed')

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
    print(f'extracting data, path: {image_path}')
    image = Image.open(image_path)
    response = model.generate_content([prompt, image])
    json_path = f'{data_dir}/{_filename_without_extension(image_path)}.json'
    with open(json_path, "w") as file:
        file.write(response.text)
    consumed_path = f'{consumed_dir}/{os.path.basename(image_path)}'
    os.rename(image_path, consumed_path)

def _filename_without_extension(path: str):
    return os.path.splitext(os.path.basename(path))[0]

