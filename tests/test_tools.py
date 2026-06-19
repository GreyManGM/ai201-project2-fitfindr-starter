# tests/test_tools.py
import pytest
from tools import search_listings, suggest_outfit, create_fit_card
from utils.data_loader import get_example_wardrobe, get_empty_wardrobe

# ── search_listings ───────────────────────────────────────────────────────────

def test_search_returns_results():
    results = search_listings("vintage graphic tee", size=None, max_price=50)
    assert isinstance(results, list)
    assert len(results) > 0

def test_search_empty_results():
    results = search_listings("designer ballgown", size="XXS", max_price=5)
    assert results == []   # empty list, no exception

def test_search_price_filter():
    results = search_listings("jacket", size=None, max_price=10)
    assert all(item["price"] <= 10 for item in results)

# ── suggest_outfit ────────────────────────────────────────────────────────────

SAMPLE_ITEM = {
    "title": "Vintage Levi's Denim Jacket",
    "category": "outerwear",
    "style_tags": ["vintage", "denim", "90s"],
    "colors": ["blue"],
    "brand": "Levi's",
    "condition": "good",
    "description": "Classic 90s trucker jacket.",
}

def test_suggest_outfit_with_wardrobe():
    """Normal path: wardrobe has items, should return outfit combos."""
    wardrobe = get_example_wardrobe()
    result = suggest_outfit(SAMPLE_ITEM, wardrobe)
    assert isinstance(result, str)
    assert len(result) > 0          # never empty

def test_suggest_outfit_empty_wardrobe():
    """Failure mode: empty wardrobe returns general advice, not an exception."""
    empty = get_empty_wardrobe()
    result = suggest_outfit(SAMPLE_ITEM, empty)
    assert isinstance(result, str)
    assert len(result) > 0          # graceful fallback, not ""

# ── create_fit_card ───────────────────────────────────────────────────────────

SAMPLE_OUTFIT = (
    "Pair the Levi's jacket with wide-leg jeans and chunky sneakers "
    "for a relaxed 90s streetwear look."
)

def test_create_fit_card_returns_caption():
    """Normal path: valid outfit + item produces a caption string."""
    result = create_fit_card(SAMPLE_OUTFIT, SAMPLE_ITEM)
    assert isinstance(result, str)
    assert len(result) > 0

def test_create_fit_card_empty_outfit():
    """Failure mode: empty outfit string returns an error message, not an exception."""
    result = create_fit_card("", SAMPLE_ITEM)
    assert isinstance(result, str)
    assert "error" in result.lower()   # descriptive error, not a crash

def test_create_fit_card_whitespace_outfit():
    """Failure mode: whitespace-only outfit also triggers the guard."""
    result = create_fit_card("   ", SAMPLE_ITEM)
    assert isinstance(result, str)
    assert "error" in result.lower()