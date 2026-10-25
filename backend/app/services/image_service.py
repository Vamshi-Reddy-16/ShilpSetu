"""Image utilities. rembg is optional; fallback only performs basic resizing."""
from pathlib import Path
from PIL import Image, UnidentifiedImageError

MAX_IMAGE_BYTES = 12 * 1024 * 1024
ALLOWED_FORMATS = {"JPEG", "PNG", "WEBP"}


def validate_image(path: str) -> Image.Image:
    p = Path(path)
    if not p.exists() or p.stat().st_size > MAX_IMAGE_BYTES:
        raise ValueError("Image is missing or exceeds the 12 MB limit.")
    try:
        im = Image.open(p)
        if im.format not in ALLOWED_FORMATS:
            raise ValueError("Upload a JPEG, PNG, or WEBP image.")
        im.verify()
        im = Image.open(p).convert("RGB")
        if im.width > 6000 or im.height > 6000:
            raise ValueError("Image dimensions must be 6000 x 6000 pixels or smaller.")
        return im
    except (OSError, UnidentifiedImageError) as exc:
        raise ValueError("The uploaded file is not a valid image.") from exc


def beautify_image(input_path: str, output_path: str) -> dict:
    """Try real rembg background removal; report a clear fallback if unavailable."""
    image = validate_image(input_path)
    try:
        from rembg import remove
        raw = Path(input_path).read_bytes()
        result = remove(raw)
        Path(output_path).write_bytes(result)
        with Image.open(output_path) as out:
            has_alpha = "A" in out.getbands()
        return {"output_path": output_path, "method": "rembg", "background_removed": True, "has_alpha": has_alpha}
    except ImportError:
        # A simple white-background copy is not segmentation and is labelled honestly.
        rgb = image.convert("RGB")
        rgb.thumbnail((1600, 1600))
        rgb.save(output_path, format="PNG")
        return {"output_path": output_path, "method": "resize_fallback", "background_removed": False, "warning": "rembg is not installed; this fallback does not remove the background."}
