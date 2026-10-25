"""Zero-shot handicraft category matching with OpenAI CLIP via Transformers.

CLIP compares an image with text descriptions; it is a useful baseline but is
not a substitute for validation on representative Indian handicraft photos.
"""

from __future__ import annotations

from functools import lru_cache
from typing import Any

import torch
from PIL import Image, UnidentifiedImageError
from transformers import CLIPModel, CLIPProcessor

from .categories import category_prompts, category_label

MODEL_ID = "openai/clip-vit-base-patch32"


@lru_cache(maxsize=1)
def load_clip(device_name: str | None = None):
    """Load the pretrained CLIP model and processor once; first run downloads weights."""
    if device_name is None:
        device_name = "mps" if torch.backends.mps.is_available() else "cpu"
    device = torch.device(device_name)
    model = CLIPModel.from_pretrained(MODEL_ID).eval().to(device)
    processor = CLIPProcessor.from_pretrained(MODEL_ID)
    return model, processor, device


def classify_handicraft(image_path: str, top_k: int = 3) -> dict[str, Any]:
    """Rank ShilpSetu category descriptions against an uploaded image."""
    prompts = category_prompts()
    if not 1 <= top_k <= len(prompts):
        raise ValueError(f"top_k must be between 1 and {len(prompts)}")
    try:
        with Image.open(image_path) as source:
            image = source.convert("RGB")
    except (OSError, UnidentifiedImageError) as exc:
        raise ValueError(f"Could not open a valid image: {exc}") from exc

    model, processor, device = load_clip()
    keys = [key for key, _ in prompts]
    texts = [prompt for _, prompt in prompts]
    inputs = processor(text=texts, images=image, return_tensors="pt", padding=True)
    inputs = {key: value.to(device) for key, value in inputs.items()}
    with torch.inference_mode():
        logits = model(**inputs).logits_per_image[0]
        probabilities = torch.softmax(logits, dim=0)
        scores, indices = torch.topk(probabilities, k=top_k)

    results = [
        {
            "category": keys[int(index)],
            "label": category_label(keys[int(index)]),
            "confidence": round(float(score), 4),
        }
        for score, index in zip(scores.cpu(), indices.cpu())
    ]
    return {
        "model": MODEL_ID,
        "device": str(device),
        "method": "zero-shot image-text similarity",
        "warning": "Scores are relative similarities, not calibrated probabilities or proof of accuracy.",
        "predictions": results,
    }
