import os, google.generativeai as genai
from pathlib import Path
from PIL import Image
from dotenv import load_dotenv
from src.config import output_dir, visual_llm_model as model_name
from src.core.util import mkdir

input_dir = mkdir(f'{output_dir}/screenshots/awaiting-extraction')
data_dir = mkdir(f'{output_dir}/data/awaiting-validation')
consumed_dir = mkdir(f'{output_dir}/screenshots/consumed')

load_dotenv()
api_key = os.getenv('GOOGLE_GENAI_API_KEY')
genai.configure(api_key=api_key)
model = genai.GenerativeModel(model_name)


def extract_json(image_path: str, prompt_json_properties: str):
    prompt = f"""
    Extract the following data as raw JSON.
    Do not use any markdown formatting or backticks.
    Partial data is okay.
    
    {prompt_json_properties}
    
    If extraction fails entirely, give concise feedback instead:
    E.g. "A popup was blocking the view" 
      or "Error: 404 not found"
      or "Found no price forecast data"
    """
    extract(image_path, prompt)


def extract(image_path: str, prompt: str):
    print(f'extracting data, path: {image_path}')
    image = Image.open(image_path)
    response = model.generate_content([prompt, image])
    data_path = f'{data_dir}/{Path(image_path).stem}.json'
    with open(data_path, "w") as file:
        file.write(response.text)
    consumed_path = f'{consumed_dir}/{Path(image_path).name}'
    os.rename(image_path, consumed_path)
