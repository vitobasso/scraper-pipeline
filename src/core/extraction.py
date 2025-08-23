from pathlib import Path

from PIL import Image

from src.core import paths
from src.core.logs import log
from src.core.paths import extract_ticker_pipeline
from src.services.llm import llm


def extract_json(image_path: Path, prompt_json_properties: str, next_stage: str):
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
    extract(image_path, prompt, next_stage)


def extract(image_path: Path, prompt: str, next_stage: str):
    print(f'extracting data, path: {image_path}')
    try:
        image = Image.open(image_path)
        response = llm().generate_content([prompt, image])
        output, _, processed = paths.split_files(image_path, "extraction", next_stage, "json")
        with output.open(mode="w", encoding="utf-8") as f:
            f.write(response.text)
        image_path.rename(processed)
    except Exception as e:
        ticker, pipeline = extract_ticker_pipeline(image_path)
        log(str(e), ticker, pipeline)


def ask(prompt: str, output_path: Path):
    response = llm().generate_content(prompt)
    with open(output_path, "w") as file:
        file.write(response.text)
