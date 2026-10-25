from pathlib import Path
from uuid import uuid4
import os
from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from .database import init_db, save_product, get_product, list_products
from .services.image_service import validate_image, beautify_image
from .services.catalog_service import make_catalog
from .services.price_service import estimate_price

BASE = Path(__file__).resolve().parents[2]
UPLOADS = BASE / "uploads"
OUTPUTS = BASE / "outputs"
UPLOADS.mkdir(exist_ok=True); OUTPUTS.mkdir(exist_ok=True)
MAX_BYTES = 12 * 1024 * 1024
app = FastAPI(title="ShilpSetu Deep Learning API", version="1.0.0", description="AI-assisted catalog tools for artisan products. Model predictions require validation on real handicraft images.")
app.add_middleware(CORSMiddleware, allow_origins=os.getenv("CORS_ORIGINS", "http://localhost:3000,http://127.0.0.1:5500").split(","), allow_credentials=False, allow_methods=["GET", "POST"], allow_headers=["*"])

@app.on_event("startup")
def startup(): init_db()

class PriceRequest(BaseModel):
    production_cost: float | None = Field(default=None, ge=0)
    labor_hours: float | None = Field(default=None, ge=0)
    labor_rate: float = Field(default=0, ge=0)
    margin_percent: float = Field(default=30, ge=0, le=500)

async def store_upload(file: UploadFile) -> Path:
    suffix = Path(file.filename or "").suffix.lower()
    if suffix not in {".jpg", ".jpeg", ".png", ".webp"}:
        raise HTTPException(400, "Upload a JPG, PNG, or WEBP image.")
    data = await file.read(MAX_BYTES + 1)
    if not data or len(data) > MAX_BYTES:
        raise HTTPException(413, "Image must be non-empty and at most 12 MB.")
    path = UPLOADS / f"{uuid4().hex}{suffix}"
    path.write_bytes(data)
    try: validate_image(str(path))
    except ValueError as e:
        path.unlink(missing_ok=True)
        raise HTTPException(400, str(e))
    return path

@app.get("/")
def root(): return {"project": "ShilpSetu", "purpose": "Deep Learning backend", "docs": "/docs"}

@app.get("/api/health")
def health():
    return {"status": "ok", "classification": "models load on first request; downloads may be required", "beautification": "rembg optional; fallback does not remove background", "price": "cost-plus estimate, not live market prediction"}

@app.post("/api/classify")
async def classify(file: UploadFile = File(...), method: str = Form("clip")):
    path = await store_upload(file)
    try:
        if method == "clip":
            from .services.clip_service import classify_handicraft
            return classify_handicraft(str(path), top_k=3)
        if method == "effnet":
            from .services.effnet import classify_image
            return classify_image(str(path), top_k=5)
        raise HTTPException(400, "method must be 'clip' or 'effnet'")
    except HTTPException: raise
    except Exception as e: raise HTTPException(503, f"Model inference failed: {type(e).__name__}: {e}. Check dependencies and model download access.")
    finally: path.unlink(missing_ok=True)

@app.post("/api/beautify")
async def beautify(file: UploadFile = File(...)):
    path = await store_upload(file); output = OUTPUTS / f"{uuid4().hex}.png"
    try:
        result = beautify_image(str(path), str(output))
        return {**result, "download_url": f"/api/files/{output.name}"}
    except Exception as e: raise HTTPException(500, str(e))
    finally: path.unlink(missing_ok=True)

@app.get("/api/files/{filename}")
def download_output(filename: str):
    from fastapi.responses import FileResponse
    safe = Path(filename).name
    path = OUTPUTS / safe
    if not path.exists(): raise HTTPException(404, "Output not found")
    return FileResponse(path, media_type="image/png", filename=safe)

@app.post("/api/catalog")
async def catalog(file: UploadFile = File(...), category: str | None = Form(None), artisan_name: str | None = Form(None), region: str | None = Form(None), confirmed_material: str | None = Form(None), artisan_story: str | None = Form(None)):
    path = await store_upload(file)
    try: return make_catalog(str(path), category, artisan_name, region, confirmed_material, artisan_story)
    finally: path.unlink(missing_ok=True)

@app.post("/api/price-estimate")
def price(req: PriceRequest):
    try: return estimate_price(req.production_cost, req.labor_hours, req.labor_rate, req.margin_percent)
    except ValueError as e: raise HTTPException(422, str(e))

@app.post("/api/process")
async def process(file: UploadFile = File(...), production_cost: float | None = Form(None, ge=0), labor_hours: float | None = Form(None, ge=0), labor_rate: float = Form(0, ge=0), margin_percent: float = Form(30, ge=0, le=500), artisan_name: str | None = Form(None), region: str | None = Form(None), confirmed_material: str | None = Form(None)):
    path = await store_upload(file)
    try:
        # CLIP is used as the default category baseline; no false claim of custom training.
        from .services.clip_service import classify_handicraft
        classification = classify_handicraft(str(path), top_k=3)
        category = classification["predictions"][0]["category"]
        catalog_data = make_catalog(str(path), category, artisan_name, region, confirmed_material)
        price_data = estimate_price(production_cost, labor_hours, labor_rate, margin_percent)
        result = {"classification": classification, "catalog": catalog_data, "price": price_data, "original_filename": file.filename, "status": "draft_requires_review"}
        return save_product(result)
    except Exception as e: raise HTTPException(503, f"Processing failed: {type(e).__name__}: {e}")
    finally: path.unlink(missing_ok=True)

@app.get("/api/products")
def products(): return list_products()

@app.get("/api/products/{product_id}")
def product(product_id: int):
    item = get_product(product_id)
    if item is None: raise HTTPException(404, "Product not found")
    return item
