"""
agent.py

The FitFindr planning loop. Orchestrates the three tools in response to a
natural language user query, passing state between them via a session dict.

Complete tools.py and test each tool in isolation before implementing this file.

Usage (once implemented):
    from agent import run_agent
    from utils.data_loader import get_example_wardrobe

    result = run_agent(
        query="vintage graphic tee under $30, size M",
        wardrobe=get_example_wardrobe(),
    )
    print(result["fit_card"])
    print(result["error"])   # None on success
"""
import re
from tools import search_listings, suggest_outfit, create_fit_card


# ── session state ─────────────────────────────────────────────────────────────

def _new_session(query: str, wardrobe: dict) -> dict:
    """
    Initialize and return a fresh session dict for one user interaction.

    The session dict is the single source of truth for everything that happens
    during a run — it stores the original query, parsed parameters, tool results,
    and any error that caused early termination.

    You may add fields to this dict as needed for your implementation.
    """
    return {
        "query": query,              # original user query
        "parsed": {},                # extracted description / size / max_price
        "search_results": [],        # list of matching listing dicts
        "selected_item": None,       # top result, passed into suggest_outfit
        "wardrobe": wardrobe,        # user's wardrobe dict
        "outfit_suggestion": None,   # string returned by suggest_outfit
        "fit_card": None,            # string returned by create_fit_card
        "error": None,               # set if the interaction ended early
    }


# ── planning loop ─────────────────────────────────────────────────────────────

def run_agent(query: str, wardrobe: dict) -> dict:
    session = _new_session(query, wardrobe)

    # Step 2: parse query with simple rules
    query_lower = query.lower()

    max_price = None
    price_match = re.search(r"(?:under|below|less than|\$)\s*\$?(\d+(?:\.\d+)?)", query_lower)
    if price_match:
        max_price = float(price_match.group(1))

    size = None
    size_match = re.search(r"size\s+([a-z0-9/]+)", query_lower)
    if size_match:
        size = size_match.group(1).upper()

    description = query_lower

    # Remove price phrases
    description = re.sub(r"(?:under|below|less than)\s*\$?\d+(?:\.\d+)?", "", description)
    description = re.sub(r"\$\d+(?:\.\d+)?", "", description)

    # Remove size phrases
    description = re.sub(r"size\s+[a-z0-9/]+", "", description)

    # Remove common filler phrases
    filler_phrases = [
        "i'm looking for",
        "im looking for",
        "looking for",
        "find me",
        "show me",
        "what's out there",
        "what is out there",
        "and how would i style it",
        "how would i style it",
    ]

    for phrase in filler_phrases:
        description = description.replace(phrase, "")

    description = description.strip(" ,.")

    session["parsed"] = {
        "description": description,
        "size": size,
        "max_price": max_price,
    }

    # Step 3: search listings
    results = search_listings(
        description=description,
        size=size,
        max_price=max_price,
    )

    session["search_results"] = results

    if not results:
        session["error"] = (
            "I couldn't find any listings that match that item, size, and budget. "
            "Try increasing your budget, using a broader description, or relaxing the size filter."
        )
        return session

    # Step 4: select top item
    selected_item = results[0]
    session["selected_item"] = selected_item

    # Step 5: suggest outfit
    outfit = suggest_outfit(selected_item, wardrobe)
    session["outfit_suggestion"] = outfit

    # Step 6: create fit card
    fit_card = create_fit_card(outfit, selected_item)
    session["fit_card"] = fit_card

    return session


# ── CLI test ──────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    from utils.data_loader import get_example_wardrobe, get_empty_wardrobe

    print("=== Happy path: graphic tee ===\n")
    session = run_agent(
        query="looking for a vintage graphic tee under $30",
        wardrobe=get_example_wardrobe(),
    )
    if session["error"]:
        print(f"Error: {session['error']}")
    else:
        print(f"Found: {session['selected_item']['title']}")
        print(f"\nOutfit: {session['outfit_suggestion']}")
        print(f"\nFit card: {session['fit_card']}")

    print("\n\n=== No-results path ===\n")
    session2 = run_agent(
        query="designer ballgown size XXS under $5",
        wardrobe=get_example_wardrobe(),
    )
    print(f"Error message: {session2['error']}")
