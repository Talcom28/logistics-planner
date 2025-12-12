"""
MVP multi-modal fuel pricing service.

In production replace these with connectors to:
- S&P Platts / ClearLynx / OPIS for marine fuels
- Barchart / local fuel price APIs for road diesel
- Jet fuel suppliers / airport fuel suppliers for Jet-A1
- Local rail fuel indices where available
"""
from typing import Optional

# Mock prices (USD per unit)
# marine: USD per ton
MOCK_BUNKER_PRICES = {
    "ROTTERDAM": 600.0,
    "SINGAPORE": 620.0,
    "HONGKONG": 610.0,
    "DEFAULT_BUNKER": 650.0
}

# road & rail: USD per liter
MOCK_DIESEL_PRICE_PER_L = {
    "EU": 1.6,
    "US": 1.1,
    "DEFAULT": 1.5
}

# jet fuel: USD per liter
MOCK_JET_PRICE_PER_L = {
    "GLOBAL": 0.8,
    "DEFAULT": 0.9
}


def get_bunker_price_for_port(port_name: Optional[str]) -> float:
    if not port_name:
        return MOCK_BUNKER_PRICES["DEFAULT_BUNKER"]
    key = port_name.strip().upper()
    return MOCK_BUNKER_PRICES.get(key, MOCK_BUNKER_PRICES["DEFAULT_BUNKER"])


def get_diesel_price_for_region(region_code: Optional[str]) -> float:
    if not region_code:
        return MOCK_DIESEL_PRICE_PER_L["DEFAULT"]
    return MOCK_DIESEL_PRICE_PER_L.get(region_code.upper(), MOCK_DIESEL_PRICE_PER_L["DEFAULT"])


def get_jet_price_for_region(region_code: Optional[str]) -> float:
    if not region_code:
        return MOCK_JET_PRICE_PER_L["DEFAULT"]
    return MOCK_JET_PRICE_PER_L.get(region_code.upper(), MOCK_JET_PRICE_PER_L["DEFAULT"])