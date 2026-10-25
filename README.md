# ShilpSetu — AI-Driven Artisan Cataloging

A Deep Learning case-study project that explores how image processing, pretrained vision models, product catalog generation, and transparent price estimation can help artisans prepare digital product listings.

ShilpSetu provides a **FastAPI backend** for processing product images and creating editable catalog drafts. It is designed as a backend prototype and does not currently include a frontend.

## Project Overview

Traditional artisans may face challenges when preparing product photographs, describing handcrafted products, creating digital catalogs, and estimating selling prices.

ShilpSetu explores a workflow that brings these tasks together:

**PHOTO → BEAUTIFY → STORY → PRICE → SELL**

The backend provides image classification, optional background removal, catalog drafting, cost-plus price estimation, and SQLite-based draft storage.

## Features

| Feature | Endpoint | Description |
|---|---|---|
| Health check | `GET /api/health` | Checks the API service |
| Image classification | `POST /api/classify` | Uses CLIP or EfficientNet-B0 |
| Image beautification | `POST /api/beautify` | Attempts background removal when `rembg` is available |
| Catalog generation | `POST /api/catalog` | Creates a conservative product catalog draft |
| Price estimation | `POST /api/price-estimate` | Calculates a cost-plus estimate |
| Combined processing | `POST /api/process` | Combines supported processing steps |
| List saved drafts | `GET /api/products` | Retrieves saved product drafts |
| Retrieve a draft | `GET /api/products/{id}` | Retrieves an individual saved draft |
| API documentation | `/docs` | Interactive Swagger UI |

## Technology Stack

- **Language:** Python
- **Backend framework:** FastAPI
- **API server:** Uvicorn
- **Deep learning:** PyTorch and Transformers, as required by the model implementations
- **Vision models:** CLIP and EfficientNet-B0
- **Image processing:** Pillow and optional `rembg`
- **Database:** SQLite
- **Testing:** pytest

Refer to `backend/requirements.txt` for the project's actual Python dependencies.

## Project Structure

```text
ShilpSetu/
├── README.md
├── .gitignore
├── .env.example
└── backend/
    ├── requirements.txt
    ├── app/
    │   ├── __init__.py
    │   ├── main.py
    │   ├── database.py
    │   └── services/
    │       ├── catalog_service.py
    │       ├── categories.py
    │       ├── clip_service.py
    │       ├── effnet.py
    │       ├── image_service.py
    │       └── price_service.py
    └── tests/
        ├── conftest.py
        └── test_services.py
```

## Prerequisites

Install the following before starting:

1. **Python 3.11 recommended.**
2. **Git**, if cloning the repository.
3. A terminal: PowerShell on Windows, or Terminal on macOS.
4. An internet connection for installing packages and downloading model weights when required.

Model libraries and weights can require considerable disk space and memory. First-time inference may take longer than subsequent requests.

## Installation and Setup

### Option A — Windows 10/11

#### 1. Install Python

Download Python from [python.org](https://www.python.org/downloads/).

During installation, enable **Add Python to PATH** if the installer offers that option.

Open PowerShell and check:

```powershell
py --version
```

If `py` is unavailable, try:

```powershell
python --version
```

#### 2. Download the project

Clone the repository:

```powershell
git clone https://github.com/Vamshi-Reddy-16/ShilpSetu.git
cd ShilpSetu
```

Alternatively, download the ZIP from GitHub, extract it, and open PowerShell in the extracted project folder.

#### 3. Create a virtual environment

Run these commands from the project root:

```powershell
py -3.11 -m venv .venv
```

Activate it:

```powershell
.\.venv\Scripts\Activate.ps1
```

If PowerShell blocks activation because of its execution policy, you can use Command Prompt instead:

```bat
.venv\Scripts\activate.bat
```

You can also invoke the virtual environment's Python directly without activating it.

#### 4. Install dependencies

```powershell
python -m pip install --upgrade pip
python -m pip install -r backend\requirements.txt
```

If installation fails, check the error message and confirm that your Python version is supported by the installed PyTorch and torchvision versions.

#### 5. Start the API

From the project root:

```powershell
python -m uvicorn backend.app.main:app --reload
```

If the import path fails, try running from the backend directory:

```powershell
cd backend
python -m uvicorn app.main:app --reload
```

#### 6. Open the API documentation

Open this address in your browser:

http://127.0.0.1:8000/docs

Keep the terminal running while using the API.

### Option B — macOS

These instructions apply to both Apple Silicon and Intel Macs, provided the installed Python and ML-library versions are compatible.

#### 1. Check Python

Open Terminal:

```bash
python3 --version
```

Python 3.11 is recommended. Install it from [python.org](https://www.python.org/downloads/) if needed.

#### 2. Download the project

```bash
git clone https://github.com/Vamshi-Reddy-16/ShilpSetu.git
cd ShilpSetu
```

Alternatively, download and extract the repository ZIP from GitHub.

#### 3. Create and activate a virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

#### 4. Install dependencies

```bash
python -m pip install --upgrade pip
python -m pip install -r backend/requirements.txt
```

#### 5. Start the API

From the project root:

```bash
python -m uvicorn backend.app.main:app --reload
```

If the import path fails, try:

```bash
cd backend
python -m uvicorn app.main:app --reload
```

#### 6. Open the API documentation

Visit:

http://127.0.0.1:8000/docs

Keep Terminal running while using the API.

## Using the API

FastAPI provides interactive documentation at `/docs`. You can use the **Try it out** button to submit requests without writing curl commands.

### 1. Health check

```bash
curl http://127.0.0.1:8000/api/health
```

### 2. Classify a product image with CLIP

```bash
curl -X POST http://127.0.0.1:8000/api/classify \
  -F "file=@handicraft.jpg" \
  -F "method=clip"
```

Replace `handicraft.jpg` with the path to an actual image on your computer.

On Windows, PowerShell users can run the same request using `curl.exe` and a suitable file path, for example:

```powershell
curl.exe -X POST http://127.0.0.1:8000/api/classify -F "file=@C:\Images\handicraft.jpg" -F "method=clip"
```

### 3. Classify an image with EfficientNet-B0

```bash
curl -X POST http://127.0.0.1:8000/api/classify \
  -F "file=@handicraft.jpg" \
  -F "method=effnet"
```

### 4. Beautify an image

```bash
curl -X POST http://127.0.0.1:8000/api/beautify \
  -F "file=@handicraft.jpg"
```

If background removal is available, the response may provide a `download_url`. Open it while the API server is running.

### 5. Generate a catalog draft

```bash
curl -X POST http://127.0.0.1:8000/api/catalog \
  -F "file=@handicraft.jpg" \
  -F "category=pottery_ceramics" \
  -F "confirmed_material=clay"
```

The catalog is a draft for review, not a guaranteed accurate description of the object.

### 6. Estimate a selling price

```bash
curl -X POST http://127.0.0.1:8000/api/price-estimate \
  -H "Content-Type: application/json" \
  -d '{"production_cost":500,"labor_hours":3,"labor_rate":100,"margin_percent":25}'
```

This example uses illustrative inputs. The endpoint performs cost-plus arithmetic rather than learned market-price prediction.

### 7. Run combined processing

```bash
curl -X POST http://127.0.0.1:8000/api/process \
  -F "file=@handicraft.jpg" \
  -F "production_cost=500" \
  -F "labor_hours=3" \
  -F "labor_rate=100" \
  -F "artisan_name=Demo Artisan" \
  -F "confirmed_material=clay"
```

### 8. Retrieve saved drafts

List drafts:

```bash
curl http://127.0.0.1:8000/api/products
```

Retrieve a draft by ID:

```bash
curl http://127.0.0.1:8000/api/products/1
```

The example ID `1` is illustrative; it works only if a draft with that ID exists.

## How the AI Components Work

### CLIP

The project uses `openai/clip-vit-base-patch32` for zero-shot category matching. It compares image representations with text descriptions or category labels.

CLIP is pretrained on general image-text data and is not specifically trained on Indian handicrafts. Its similarity scores are relative scores, not calibrated probabilities.

### EfficientNet-B0

EfficientNet-B0 is used as a general-purpose image-classification baseline. Its ImageNet classes are not a dedicated taxonomy of traditional handicrafts.

### Image beautification

The backend attempts to use `rembg` for background removal when its package and model weights are available. If unavailable, the application may return a clearly labelled resize-only fallback, which does not remove the background.

### Catalog drafting

The catalog module generates a conservative template and simple image-color hints. It is not a generative vision-language model. Material information should be explicitly provided rather than assumed from an image.

### Price estimation

The pricing endpoint calculates an estimate from production cost, labour, and margin inputs. It does not use a trained market-price prediction model or live market data.

## Testing

Activate the virtual environment and run the tests from the project root:

```bash
python -m pytest backend/tests -q
```

The included tests cover deterministic catalog and pricing helpers. They do not establish the accuracy of CLIP or EfficientNet on handicraft images.

For meaningful model evaluation, test representative labelled images and document the dataset, evaluation procedure, and results before reporting any accuracy figures.

## Troubleshooting

**`python` or `python3` is not recognized**

Install Python and ensure it is available in your terminal's PATH. On Windows, try `py --version`.

**Virtual environment activation fails on Windows**

Use Command Prompt and run:

```bat
.venv\Scripts\activate.bat
```

**`uvicorn` is not recognized**

Activate the virtual environment and run:

```bash
python -m uvicorn backend.app.main:app --reload
```

**PyTorch or torchvision installation fails**

Check your Python version, operating system, and the compatibility of the installed package versions. Consult the official [PyTorch installation guide](https://pytorch.org/get-started/locally/).

**The first image request is slow**

Model weights may need to be downloaded on first use. Check your internet connection and allow sufficient time for loading.

**Background removal does not work**

Check whether `rembg` is installed and its required model weights can be downloaded. A resize-only fallback does not remove the background.

**The `/docs` page does not open**

Confirm the server started without an error, check that port `8000` is available, and open `http://127.0.0.1:8000/docs`.

## Limitations

- CLIP and EfficientNet-B0 are general pretrained models, not models trained on a dedicated Indian handicraft dataset.
- Classification performance on handicrafts has not been established by the included tests.
- Catalog output is template-based rather than generated by a dedicated vision-language model.
- Pricing is based on cost-plus arithmetic, not a validated market-price model.
- Background removal depends on the availability of `rembg` and its model weights.
- A frontend, production hosting, and real-world artisan usability validation are outside this backend starter's current scope.

Treat all generated output as an editable draft that must be reviewed by the artisan.

## Future Scope

Potential extensions include a dedicated handicraft image dataset, model fine-tuning and evaluation, regional-language and voice-based listing, verified market-price data, an artisan-facing frontend, and production deployment.

These are future possibilities and should not be interpreted as completed features.

## Repository

GitHub: https://github.com/Vamshi-Reddy-16/ShilpSetu

## Academic Context

**Subject:** Deep Learning  
**Subject Code:** 22CAC08N  
**Project Guide:** Mr. Panigrahi Srikanth, Assistant Professor

**Team Members:**
- Kotha Vamshi Reddy — 160124748115
- Marri Sri Shlok Reddy — 160124748117
