"""EfficientNet-B0 ImageNet inference baseline for ShilpSetu.

This model is pretrained on ImageNet, NOT specifically on Indian handicrafts.
It returns general ImageNet labels and must not be treated as a reliable
handicraft classifier until fine-tuned and evaluated on a labeled dataset.
"""

from __future__ import annotations

from functools import lru_cache
from typing import Any

import torch
from PIL import Image, UnidentifiedImageError
from torchvision.models import EfficientNet_B0_Weights, efficientnet_b0


@lru_cache(maxsize=1)
def load_model(device_name: str | None = None):
    """Load pretrained EfficientNet-B0 once. First run may download weights."""
    if device_name is None:
        device_name = "mps" if torch.backends.mps.is_available() else "cpu"
    device = torch.device(device_name)
    weights = EfficientNet_B0_Weights.DEFAULT
    model = efficientnet_b0(weights=weights)
    model.eval().to(device)
    return model, weights, device


def classify_image(image_path: str, top_k: int = 5) -> dict[str, Any]:
    """Return top-k ImageNet predictions for an image path."""
    if not 1 <= top_k <= 10:
        raise ValueError("top_k must be between 1 and 10")
    try:
        with Image.open(image_path) as source:
            image = source.convert("RGB")
    except (OSError, UnidentifiedImageError) as exc:
        raise ValueError(f"Could not open a valid image: {exc}") from exc

    model, weights, device = load_model()
    preprocess = weights.transforms()
    tensor = preprocess(image).unsqueeze(0).to(device)
    with torch.inference_mode():
        probabilities = torch.softmax(model(tensor)[0], dim=0)
        scores, indices = torch.topk(probabilities, k=top_k)

    labels = weights.meta["categories"]
    predictions = [
        {"label": labels[int(index)], "confidence": round(float(score), 4)}
        for score, index in zip(scores.cpu(), indices.cpu())
    ]
    return {
        "model": "EfficientNet-B0 ImageNet pretrained",
        "device": str(device),
        "warning": "Generic ImageNet predictions; not handicraft-specific classification.",
        "predictions": predictions,
    }
