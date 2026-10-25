"""Transparent cost-plus price suggestion; not a market-price prediction model."""

def estimate_price(production_cost: float | None, labor_hours: float | None = None,
                   labor_rate: float = 0.0, margin_percent: float = 30.0) -> dict:
    if production_cost is None or production_cost < 0:
        return {"status": "insufficient_data", "message": "Provide a non-negative production_cost to estimate a price."}
    if labor_hours is not None and labor_hours < 0:
        raise ValueError("labor_hours must be non-negative")
    if labor_rate < 0 or margin_percent < 0:
        raise ValueError("labor_rate and margin_percent must be non-negative")
    labor_cost = (labor_hours or 0.0) * labor_rate
    total_cost = production_cost + labor_cost
    suggested = round(total_cost * (1 + margin_percent / 100), 2)
    return {"status": "estimated", "method": "transparent_cost_plus_margin", "production_cost": round(production_cost, 2),
            "labor_cost": round(labor_cost, 2), "total_cost": round(total_cost, 2),
            "margin_percent": round(margin_percent, 2), "suggested_selling_price": suggested,
            "estimated_profit": round(suggested - total_cost, 2),
            "warning": "This is not a live market valuation. Validate against comparable products and customer demand."}
