# ShilpSetu Deep Learning Backend

A backend-only starter for the ShilpSetu artisan cataloging demo. It intentionally does not include a frontend.

## What is implemented

- **CLIP zero-shot category matching** (`POST /api/classify`, `method=clip`) using `openai/clip-vit-base-patch32`. On first use, Transformers downloads model weights. This is a baseline, not a model trained on Indian handicrafts. CLIP scores are relative similarities, not calibrated probabilities.
- **EfficientNet-B0 ImageNet inference** (`POST /api/classify`, `method=effnet`) as a general-purpose baseline. It is not handicraft-specific.
- **Image background removal** (`POST /api/beautify`) with `rembg` if its model can be installed/downloaded. If `rembg` is unavailable, a labeled resize-only fallback is returned; it does not remove the background.
- **Conservative catalog draft** (`POST /api/catalog`). Generates a template and simple dominant-color hints; it is not a generative vision-language model. Material is included only if explicitly supplied.
- **Transparent cost-plus estimate** (`POST /api/price-estimate`). This is not trained market-price prediction and not live market data.
- **Combined processing and SQLite drafts** (`POST /api/process`, `GET /api/products`, `GET /api/products/{id}`).
- API documentation at `/docs`.

## macOS setup (Apple Silicon or Intel)

Use Python 3.11 if possible. Model libraries are large; install can take a while.

```bash
cd shilpsetu-dl-complete
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r backend/requirements.txt
```

Start the API from the project root:

```bash
uvicorn backend.app.main:app --reload
```

If that import path fails, run from the `backend` directory instead:

```bash
cd backend
uvicorn app.main:app --reload
```

Then visit <http://127.0.0.1:8000/docs>. The first CLIP/EfficientNet/rembg use may download weights and require internet access. If PyTorch/torchvision installation fails on your macOS/Python combination, use the official PyTorch install selector and a supported Python version.

## API examples

### Health
```bash
curl http://127.0.0.1:8000/api/health
```

### Classify with CLIP
```bash
curl -X POST http://127.0.0.1:8000/api/classify \
  -F 'file=@/absolute/path/to/handicraft.jpg' \
  -F 'method=clip'
```

### Classify with EfficientNet
```bash
curl -X POST http://127.0.0.1:8000/api/classify \
  -F 'file=@/absolute/path/to/handicraft.jpg' \
  -F 'method=effnet'
```

### Beautify
```bash
curl -X POST http://127.0.0.1:8000/api/beautify \
  -F 'file=@/absolute/path/to/handicraft.jpg'
```
The response includes a `download_url`; open it in a browser while the server is running.

### Catalog draft
```bash
curl -X POST http://127.0.0.1:8000/api/catalog \
  -F 'file=@/absolute/path/to/handicraft.jpg' \
  -F 'category=pottery_ceramics' \
  -F 'confirmed_material=clay'
```

### Price estimate
```bash
curl -X POST http://127.0.0.1:8000/api/price-estimate \
  -H 'Content-Type: application/json' \
  -d '{"production_cost":500,"labor_hours":3,"labor_rate":100,"margin_percent":25}'
```

### End-to-end process
```bash
curl -X POST http://127.0.0.1:8000/api/process \
  -F 'file=@/absolute/path/to/handicraft.jpg' \
  -F 'production_cost=500' -F 'labor_hours=3' -F 'labor_rate=100' \
  -F 'artisan_name=Demo Artisan' -F 'confirmed_material=clay'
```

### Saved drafts
```bash
curl http://127.0.0.1:8000/api/products
curl http://127.0.0.1:8000/api/products/1
```

## Tests

From the `backend` directory:

```bash
pytest -q
```
Tests cover deterministic price and catalog helpers. They do **not** download or validate real neural-network weights. Run classification manually with representative labeled handicraft images before making any accuracy claims.

## Important limitations

1. CLIP and EfficientNet are pretrained general models, not trained specifically on your own handicraft dataset.
2. The catalog module uses conservative templates, not a generative vision-language model.
3. The price endpoint is cost-plus arithmetic; no market data or learned price model is included.
4. `rembg` background removal depends on its model package/weights being available. A fallback is clearly marked.
5. Treat all output as an editable draft that an artisan must review.
