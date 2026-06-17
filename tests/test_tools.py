import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from tools import search_listings, suggest_outfit, create_fit_card
from utils.data_loader import get_example_wardrobe, get_empty_wardrobe
def test_search_returns_results():
    results = search_listings("vintage graphic tee", size=None, max_price=50)

    assert isinstance(results, list)
    assert len(results) > 0
    assert all(item["price"] <= 50 for item in results)


def test_search_empty_results():
    results = search_listings("designer ballgown", size="XXS", max_price=5)

    assert results == []


def test_search_price_filter():
    results = search_listings("jacket", size=None, max_price=10)

    assert all(item["price"] <= 10 for item in results)


def test_suggest_outfit_returns_string():
    item = search_listings("graphic tee", size=None, max_price=50)[0]
    wardrobe = get_example_wardrobe()

    outfit = suggest_outfit(item, wardrobe)

    assert isinstance(outfit, str)
    assert len(outfit.strip()) > 0


def test_suggest_outfit_empty_wardrobe():
    item = search_listings("graphic tee", size=None, max_price=50)[0]
    wardrobe = get_empty_wardrobe()

    outfit = suggest_outfit(item, wardrobe)

    assert isinstance(outfit, str)
    assert len(outfit.strip()) > 0
    assert "less personalized" in outfit.lower() or "wardrobe" in outfit.lower()


def test_create_fit_card_returns_string():
    item = search_listings("graphic tee", size=None, max_price=50)[0]
    outfit = "Pair this graphic tee with baggy jeans and chunky sneakers for a casual Y2K streetwear look."

    fit_card = create_fit_card(outfit, item)

    assert isinstance(fit_card, str)
    assert len(fit_card.strip()) > 0


def test_create_fit_card_empty_outfit():
    result = create_fit_card("", {"title": "Test Item"})

    assert isinstance(result, str)
    assert "complete outfit" in result.lower()