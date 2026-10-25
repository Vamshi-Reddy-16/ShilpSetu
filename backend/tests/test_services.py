from app.services.price_service import estimate_price
from app.services.catalog_service import make_catalog
from PIL import Image


def test_price_cost_plus():
    out = estimate_price(100, labor_hours=2, labor_rate=50, margin_percent=20)
    assert out["total_cost"] == 200
    assert out["suggested_selling_price"] == 240
    assert out["estimated_profit"] == 40


def test_price_missing_cost():
    assert estimate_price(None)["status"] == "insufficient_data"


def test_catalog_marks_review(tmp_path):
    p = tmp_path / "item.png"
    Image.new("RGB", (30, 30), (200, 20, 20)).save(p)
    out = make_catalog(str(p), "pottery_ceramics", confirmed_material=None)
    assert out["category"] == "pottery_ceramics"
    assert out["requires_artisan_review"] is True
    assert out["material"] is None
