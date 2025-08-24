from pathlib import Path

from PIL import Image

from src import config
from src.core import paths
from src.core.logs import log
from src.core.paths import extract_ticker_pipeline
from src.services.llm import llm

this_stage = "extraction"


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
    output, failed, processed = paths.split_files(image_path, this_stage, next_stage, "json")
    try:
        image = Image.open(image_path)
        response = llm().generate_content([prompt, image])
        with output.open(mode="w", encoding="utf-8") as f:
            f.write(response.text)
        image_path.rename(processed) if config.keep_debug_images else image_path.unlink()
    except Exception as e:
        ticker, pipeline = extract_ticker_pipeline(image_path)
        log(str(e), ticker, pipeline)
        image_path.rename(failed) if config.keep_debug_images else (image_path.unlink() and failed.with_stem("stamp").touch())


def ask(prompt: str, output_path: Path):
    response = llm().generate_content(prompt)
    with open(output_path, "w") as file:
        file.write(response.text)
