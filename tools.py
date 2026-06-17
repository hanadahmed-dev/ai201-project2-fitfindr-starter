"""
tools.py

The three required FitFindr tools. Each tool is a standalone function that
can be called and tested independently before being wired into the agent loop.

Complete and test each tool before moving to agent.py.

Tools:
    search_listings(description, size, max_price)  → list[dict]
    suggest_outfit(new_item, wardrobe)              → str
    create_fit_card(outfit, new_item)               → str
"""

import os

from dotenv import load_dotenv
from groq import Groq

from utils.data_loader import load_listings

load_dotenv()

MODEL_NAME = "llama-3.3-70b-versatile"

# ── Groq client ───────────────────────────────────────────────────────────────

def _get_groq_client():
    """Initialize and return a Groq client using GROQ_API_KEY from .env."""
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        raise ValueError(
            "GROQ_API_KEY not set. Add it to a .env file in the project root."
        )
    return Groq(api_key=api_key)


# ── Tool 1: search_listings ───────────────────────────────────────────────────

def search_listings(
    description: str,
    size: str | None = None,
    max_price: float | None = None,
) -> list[dict]:
    
    listings = load_listings()

    if not description or not description.strip():
        return []

    query_terms = set(description.lower().replace("-", " ").split())
    matches = []

    for listing in listings:
        if max_price is not None and listing["price"] > max_price:
            continue

        if size is not None:
            requested_size = size.lower()
            listing_size = listing["size"].lower()
            if requested_size not in listing_size:
                continue

        searchable_text = " ".join([
            listing.get("title") or "",
            listing.get("description") or "",
            listing.get("category") or "",
            " ".join(listing.get("style_tags") or []),
            " ".join(listing.get("colors") or []),
            listing.get("brand") or "",
            listing.get("platform") or "",
        ]).lower().replace("-", " ")

        score = sum(1 for term in query_terms if term in searchable_text)

        if score > 0:
            item = listing.copy()
            item["_score"] = score
            matches.append(item)

    matches.sort(key=lambda item: item["_score"], reverse=True)

    for item in matches:
        item.pop("_score", None)

    return matches


# ── Tool 2: suggest_outfit ────────────────────────────────────────────────────

def suggest_outfit(new_item: dict, wardrobe: dict) -> str:
    client = _get_groq_client()

    item_title = new_item.get("title", "this item")
    item_details = f"""
Title: {new_item.get("title")}
Description: {new_item.get("description")}
Category: {new_item.get("category")}
Style tags: {new_item.get("style_tags")}
Colors: {new_item.get("colors")}
Price: {new_item.get("price")}
Platform: {new_item.get("platform")}
"""

    wardrobe_items = wardrobe.get("items", []) if wardrobe else []

    if not wardrobe_items:
        prompt = f"""
You are FitFindr, a helpful secondhand styling assistant.

The user is considering this thrifted item:

{item_details}

The user's wardrobe is empty or unavailable.

Give 1-2 general outfit ideas using common basics someone might own.
Be honest that the suggestion is less personalized because no wardrobe items were provided.
Keep it concise and practical.
"""
    else:
        formatted_wardrobe = "\n".join(
            f"- {item.get('name')} | Category: {item.get('category')} | "
            f"Colors: {item.get('colors')} | Style tags: {item.get('style_tags')} | "
            f"Notes: {item.get('notes')}"
            for item in wardrobe_items
        )

        prompt = f"""
You are FitFindr, a helpful secondhand styling assistant.

The user is considering this thrifted item:

{item_details}

The user's wardrobe contains:

{formatted_wardrobe}

Suggest 1-2 complete outfits using the thrifted item and specific named pieces from the wardrobe.
Explain briefly why each outfit works.
Keep the tone casual and useful.
"""

    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {"role": "system", "content": "You are a practical fashion styling assistant."},
            {"role": "user", "content": prompt},
        ],
        temperature=0.6,
    )

    return response.choices[0].message.content.strip()


# ── Tool 3: create_fit_card ───────────────────────────────────────────────────

def create_fit_card(outfit: str, new_item: dict) -> str:
    if not outfit or not outfit.strip():
        return "I need a complete outfit suggestion before I can create a fit card."

    client = _get_groq_client()

    prompt = f"""
You are FitFindr, creating a short shareable outfit caption.

Thrifted item:
Title: {new_item.get("title")}
Price: ${new_item.get("price")}
Platform: {new_item.get("platform")}
Condition: {new_item.get("condition")}
Colors: {new_item.get("colors")}
Style tags: {new_item.get("style_tags")}

Outfit suggestion:
{outfit}

Write a 2-4 sentence caption that:
- Sounds casual and authentic, like an OOTD post
- Mentions the item name, price, and platform naturally once
- Captures the outfit vibe with specific style language
- Does not sound like a product description
"""

    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {"role": "system", "content": "You write short, stylish outfit captions."},
            {"role": "user", "content": prompt},
        ],
        temperature=0.9,
    )

    return response.choices[0].message.content.strip()