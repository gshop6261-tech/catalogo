"""Pricing calculations — replicates getCalculationResult() from admin.html."""


def calculate_sell_price(
    usd_cost: float,
    cat_name: str,
    calc_sub: str,
    weight: float,
    categories: list[dict],
) -> float | None:
    """Replica of admin.html getCalculationResult() (lines 2136-2178).

    Returns usdSell or None if no matching rule found.
    """
    if not usd_cost or usd_cost <= 0:
        return None

    cat = next((c for c in categories if c["name"] == cat_name), None)
    if not cat:
        return None

    rules = cat.get("rules", [])
    subtype_target = calc_sub or "unico"
    type_rules = [r for r in rules if r.get("subtype") == subtype_target]

    matched = None
    for r in type_rules:
        rtype = r.get("type", "none")
        if rtype == "none":
            matched = r
            break
        if rtype == "price":
            op, val = r.get("op"), r.get("val", 0)
            if op == "<=" and usd_cost <= val:
                matched = r; break
            if op == ">=" and usd_cost >= val:
                matched = r; break
            if op == "<" and usd_cost < val:
                matched = r; break
            if op == ">" and usd_cost > val:
                matched = r; break
        if rtype == "weight":
            w = weight or 0
            op, val = r.get("op"), r.get("val", 0)
            if op == "<=" and w <= val:
                matched = r; break
            if op == ">=" and w >= val:
                matched = r; break
            if op == "<" and w < val:
                matched = r; break
            if op == ">" and w > val:
                matched = r; break

    if not matched:
        matched = type_rules[0] if type_rules else None
    if not matched:
        return None

    pct = 1 + (matched["margin"] / 100)
    return (usd_cost * pct) + matched.get("add", 0)


def average_cost(reference_links: list[dict]) -> float | None:
    """Calculate average USD cost from reference links."""
    prices = [
        link["price"]
        for link in reference_links
        if link.get("price") is not None
    ]
    if not prices:
        return None
    return round(sum(prices) / len(prices), 2)
