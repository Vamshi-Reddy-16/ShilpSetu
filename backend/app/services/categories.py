"""Category labels and prompt templates for ShilpSetu.

CLIP-based category matching is a zero-shot baseline, not a model trained on
Indian handicraft images. Validate predictions with real artisan-product data.
"""

CRAFT_CATEGORIES = {
    "pottery_ceramics": "handmade pottery or ceramic craft",
    "textiles_fabrics": "handwoven textile, fabric, or embroidered cloth craft",
    "jewelry": "handmade jewelry or decorative wearable craft",
    "wooden_crafts": "hand-carved wooden handicraft",
    "paintings": "handmade painting or traditional artwork",
    "metal_crafts": "handmade metal craft or metalwork",
    "basketry": "handwoven basket, cane, or bamboo craft",
    "leather_crafts": "handmade leather craft",
    "stone_crafts": "hand-carved stone craft",
    "other_handicraft": "handmade handicraft that does not fit the other categories",
}


def category_prompts():
    """Return CLIP prompts in stable order, paired with category keys."""
    return [
        (key, f"A clear product photograph of {description}.")
        for key, description in CRAFT_CATEGORIES.items()
    ]


def category_label(category_key: str) -> str:
    """Convert a category key to a readable label."""
    return category_key.replace("_", " ").title()
