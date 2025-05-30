from transformers import LayoutLMv3Processor, LayoutLMv3ForTokenClassification
from PIL import Image
import re
import numpy as np
from pprint import pprint

def extract(image: str):

    # Load image
    image = Image.open(image).convert("RGB")

    # Load processor and model
    processor = LayoutLMv3Processor.from_pretrained("microsoft/layoutlmv3-base", apply_ocr=True)
    model = LayoutLMv3ForTokenClassification.from_pretrained("microsoft/layoutlmv3-base")

    # Preprocess image
    encoding = processor(image, return_tensors="pt")
    outputs = model(**encoding)

    # Get predicted labels
    logits = outputs.logits
    predicted_class_idx = logits.argmax(-1)
    tokens = processor.tokenizer.convert_ids_to_tokens(encoding["input_ids"][0])
    labels = [model.config.id2label[idx.item()] for idx in predicted_class_idx[0]]

    # # Reconstruct labeled tokens
    # labeled_data = list(zip(tokens, labels))
    #
    # # --- Optional: Simple rule-based label-value matcher ---
    # keywords = ["buy", "hold", "sell", "average", "lowest", "highest"]
    # extracted = {}
    #
    # for i, (token, label) in enumerate(labeled_data):
    #     token_clean = token.lower().replace("Ġ", "")
    #     for key in keywords:
    #         if key in token_clean:
    #             # Look ahead for a number-like token
    #             for j in range(i+1, min(i+4, len(labeled_data))):
    #                 val_token = labeled_data[j][0].replace("Ġ", "")
    #                 if val_token.replace('.', '', 1).isdigit():
    #                     extracted[key] = val_token
    #                     break
    #
    # # Output extracted values
    # print("Extracted values:", extracted)
    extract_values_from_layout(tokens, encoding["bbox"][0], ['Buy', 'Hold', 'Sell', 'High', 'Average', 'Low'])

def center(box):
    """Calcula o centro de uma bounding box [x0, y0, x1, y1]."""
    return [(box[0] + box[2]) / 2, (box[1] + box[3]) / 2]


def extract_values_from_layout(tokens, boxes, label_keywords):
    numeric_tokens = []

    # Identifica rótulos e candidatos a valores numéricos
    labels = {label: [] for label in label_keywords}

    for i, token in enumerate(tokens):
        # Normaliza e tenta identificar como rótulo
        for label in label_keywords:
            if token.strip().lower() == label.lower():
                labels[label].append((i, center(boxes[i])))

        # Candidatos numéricos
        if re.match(r'^\$?\d+([.,]\d+)?$', token.strip()):
            numeric_tokens.append((i, center(boxes[i]), token.strip()))

    result = {}

    for label, label_entries in labels.items():
        if not label_entries:
            continue  # pula se o rótulo não foi encontrado

        closest_token = None
        min_dist = float('inf')

        for label_idx, label_center in label_entries:
            for num_idx, num_center, num_value in numeric_tokens:
                dist = np.linalg.norm(np.array(label_center) - np.array(num_center))
                if dist < min_dist:
                    min_dist = dist
                    closest_token = num_value

        if closest_token:
            result[label.lower()] = closest_token

    print(result)
    pprint(result)