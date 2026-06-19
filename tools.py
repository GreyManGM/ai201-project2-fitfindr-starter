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
    """
    Search the mock listings dataset for items matching the description,
    optional size, and optional price ceiling.

    Args:
        description: Keywords describing what the user is looking for
                     (e.g., "vintage graphic tee").
        size:        Size string to filter by, or None to skip size filtering.
                     Matching is case-insensitive (e.g., "M" matches "S/M").
        max_price:   Maximum price (inclusive), or None to skip price filtering.

    Returns:
        A list of matching listing dicts, sorted by relevance (best match first).
        Returns an empty list if nothing matches — does NOT raise an exception.

    Each listing dict has the following fields:
        id, title, description, category, style_tags (list), size,
        condition, price (float), colors (list), brand, platform

    TODO:
        1. Load all listings with load_listings().
        2. Filter by max_price and size (if provided).
        3. Score each remaining listing by keyword overlap with `description`.
        4. Drop any listings with a score of 0 (no relevant matches).
        5. Sort by score, highest first, and return the listing dicts.

    Before writing code, fill in the Tool 1 section of planning.md.
    """
    # Replace this with your implementation
    try:
        listings = load_listings()
    except Exception:
        return []

    # Step 2: Filter by max_price and size
    filtered = []
    for listing in listings:
        if max_price is not None and listing.get("price", 0) > max_price:
            continue
        if size is not None:
            listing_size = listing.get("size", "")
            if size.lower() not in listing_size.lower():
                continue
        filtered.append(listing)

    # Step 3: Score by keyword overlap with description
    keywords = [kw.lower() for kw in description.split()]

    def score(listing):
        # Build a searchable text blob from all relevant string fields
        blob = " ".join([
            listing.get("title", ""),
            listing.get("description", ""),
            listing.get("category", ""),
            listing.get("brand", "") or "",
            " ".join(listing.get("style_tags", []) or []),
            " ".join(listing.get("colors", []) or []),
        ]).lower()
        return sum(1 for kw in keywords if kw in blob)

    scored = [(score(listing), listing) for listing in filtered]

    # Step 4: Drop zero-score listings
    scored = [(s, listing) for s, listing in scored if s > 0]

    # Step 5: Sort by score descending, return listing dicts
    scored.sort(key=lambda x: x[0], reverse=True)
    return [listing for _, listing in scored]

# ── Tool 2: suggest_outfit ────────────────────────────────────────────────────

def suggest_outfit(new_item: dict, wardrobe: dict) -> str:
    """
    Given a thrifted item and the user's wardrobe, suggest 1–2 complete outfits.

    Args:
        new_item: A listing dict (the item the user is considering buying).
        wardrobe: A wardrobe dict with an 'items' key containing a list of
                  wardrobe item dicts. May be empty — handle this gracefully.

    Returns:
        A non-empty string with outfit suggestions.
        If the wardrobe is empty, offer general styling advice for the item
        rather than raising an exception or returning an empty string.

    TODO:
        1. Check whether wardrobe['items'] is empty.
        2. If empty: call the LLM with a prompt for general styling ideas
           (what kinds of items pair well, what vibe it suits, etc.).
        3. If not empty: format the wardrobe items into a prompt and ask
           the LLM to suggest specific outfit combinations using the new item
           and named pieces from the wardrobe.
        4. Return the LLM's response as a string.

    Before writing code, fill in the Tool 2 section of planning.md.
    """
    client = _get_groq_client()

    item_summary = (
        f"Item: {new_item.get('title', 'Unknown item')}\n"
        f"Category: {new_item.get('category', '')}\n"
        f"Style tags: {', '.join(new_item.get('style_tags', []))}\n"
        f"Colors: {', '.join(new_item.get('colors', []))}\n"
        f"Brand: {new_item.get('brand', '')}\n"
        f"Condition: {new_item.get('condition', '')}\n"
        f"Description: {new_item.get('description', '')}"
    )

    wardrobe_items = wardrobe.get("items", [])

    # Step 1-2: Empty wardrobe → general styling advice
    if not wardrobe_items:
        prompt = (
            f"A user just thrifted this item:\n{item_summary}\n\n"
            "Their wardrobe details aren't available. Give them general styling advice: "
            "what types of bottoms, shoes, and accessories pair well with this piece, "
            "what vibe or aesthetic it suits, and 1–2 example outfit ideas using common wardrobe staples."
        )
    else:
        # Step 3: Format wardrobe and ask for specific combos
        wardrobe_lines = []
        for i, piece in enumerate(wardrobe_items, 1):
            wardrobe_lines.append(
                f"{i}. {piece.get('title', piece.get('name', 'item'))} "
                f"({piece.get('category', '')} — {piece.get('colors', piece.get('color', ''))})"
            )
        wardrobe_text = "\n".join(wardrobe_lines)

        prompt = (
            f"A user just thrifted this item:\n{item_summary}\n\n"
            f"Here are the pieces already in their wardrobe:\n{wardrobe_text}\n\n"
            "Suggest 1–2 complete outfits using the thrifted item and specific named pieces "
            "from the wardrobe above. For each outfit, briefly explain why the combination works."
        )

    # Step 4: Call LLM and return response
    try:
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=400,
        )
        result = response.choices[0].message.content.strip()
        return result if result else "This piece has a lot of versatility — try pairing it with neutral basics to let it stand out."
    except Exception as e:
        return f"Could not generate outfit suggestions right now ({e}). As a general tip, this item pairs well with neutral basics and simple accessories."


# ── Tool 3: create_fit_card ───────────────────────────────────────────────────

def create_fit_card(outfit: str, new_item: dict) -> str:
    """
    Generate a short, shareable outfit caption for the thrifted find.

    Args:
        outfit:   The outfit suggestion string from suggest_outfit().
        new_item: The listing dict for the thrifted item.

    Returns:
        A 2–4 sentence string usable as an Instagram/TikTok caption.
        If outfit is empty or missing, return a descriptive error message
        string — do NOT raise an exception.

    The caption should:
    - Feel casual and authentic (like a real OOTD post, not a product description)
    - Mention the item name, price, and platform naturally (once each)
    - Capture the outfit vibe in specific terms
    - Sound different each time for different inputs (use higher LLM temperature)

    TODO:
        1. Guard against an empty or whitespace-only outfit string.
        2. Build a prompt that gives the LLM the item details and the outfit,
           and asks for a caption matching the style guidelines above.
        3. Call the LLM and return the response.

    Before writing code, fill in the Tool 3 section of planning.md.
    """
    # Step 1: Guard against empty/missing outfit
    if not outfit or not outfit.strip():
        return "Error: a valid outfit recommendation is required before creating a fit card. Please run suggest_outfit() first."

    client = _get_groq_client()

    item_name = new_item.get("title", "this thrifted find")
    price = new_item.get("price", "")
    platform = new_item.get("platform", "")

    price_str = f"${price:.2f}" if isinstance(price, (int, float)) else str(price)

    # Step 2: Build the prompt
    prompt = (
        f"Write a 2–4 sentence Instagram/TikTok OOTD caption for this thrifted outfit.\n\n"
        f"Item: {item_name}\n"
        f"Price: {price_str}\n"
        f"Platform: {platform}\n"
        f"Outfit details: {outfit}\n\n"
        "Guidelines:\n"
        "- Sound casual and authentic, like a real person posting their outfit — not a product description\n"
        "- Mention the item name, price, and platform naturally, each exactly once\n"
        "- Capture the specific vibe of the outfit (don't be generic)\n"
        "- Keep it 2–4 sentences total"
    )

    # Step 3: Call LLM with higher temperature for variety
    try:
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": prompt}],
            temperature=1.0,
            max_tokens=150,
        )
        result = response.choices[0].message.content.strip()
        return result if result else f"Thrifted this {item_name} for {price_str} on {platform} and I'm obsessed. Sometimes the best fits come from unexpected places. 🤍"
    except Exception as e:
        return f"Error generating fit card: {e}"
