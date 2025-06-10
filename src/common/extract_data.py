import os
from pathlib import Path
from PIL import Image
from src.common.util import mkdir
from src.services.llm import llm

input_dir = lambda x: mkdir(f'{x}/screenshots/awaiting-extraction')
data_dir = lambda x: mkdir(f'{x}/data/awaiting-validation')
consumed_dir = lambda x: mkdir(f'{x}/screenshots/consumed')


def extract_json(image_path: str, prompt_json_properties: str, output_dir: str):
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
    extract(image_path, prompt, output_dir)


def extract(image_path: str, prompt: str, output_dir: str):
    print(f'extracting data, path: {image_path}')
    image = Image.open(image_path)
    response = llm().generate_content([prompt, image])
    data_path = f'{data_dir(output_dir)}/{Path(image_path).stem}.json'
    with open(data_path, "w") as file:
        file.write(response.text)
    consumed_path = f'{consumed_dir(output_dir)}/{Path(image_path).name}'
    os.rename(image_path, consumed_path)


def ask(prompt: str, output_path: str):
    response = llm().generate_content(prompt)
    with open(output_path, "w") as file:
        file.write(response.text)
