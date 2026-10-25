"""Conservative catalog metadata: visual tags are suggestions, not verified facts."""
from collections import Counter
from PIL import Image
from .categories import CRAFT_CATEGORIES, category_label


def make_catalog(image_path: str, category: str | None = None, artisan_name: str | None = None,
                 region: str | None = None, confirmed_material: str | None = None,
                 artisan_story: str | None = None) -> dict:
    with Image.open(image_path) as im:
        rgb = im.convert("RGB").resize((100, 100))
        colors = Counter(rgb.getdata()).most_common(3)
    color_names = []
    for (r, g, b), _ in colors:
        if max(r, g, b) - min(r, g, b) < 25:
            name = "neutral"
        elif r >= g and r >= b:
            name = "red-toned"
        elif g >= r and g >= b:
            name = "green-toned"
        else:
            name = "blue-toned"
        if name not in color_names:
            color_names.append(name)
    key = category if category in CRAFT_CATEGORIES else "other_handicraft"
    label = category_label(key)
    title = f"Handmade {label}"
    tags = [label.lower(), "handmade", "artisan-made"] + color_names[:2]
    return {
        "title": title,
        "description": f"A handmade item categorized as {label.lower()}. Please review and edit this draft to add verified details about its design, use, and craftsmanship.",
        "category": key,
        "visible_color_suggestions": color_names,
        "tags": list(dict.fromkeys(tags)),
        "material": confirmed_material.strip() if confirmed_material and confirmed_material.strip() else None,
        "artisan_name": artisan_name,
        "region": region,
        "artisan_story": artisan_story,
        "requires_artisan_review": True,
        "generation_method": "conservative local metadata template; not a vision-language model",
    }
