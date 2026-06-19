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
    """
    Main agent entry point. Runs the FitFindr planning loop for a single
    user interaction and returns the completed session dict.

    Args:
        query:    Natural language user request
                  (e.g., "vintage graphic tee under $30, size M")
        wardrobe: User's wardrobe dict — use get_example_wardrobe() or
                  get_empty_wardrobe() from utils/data_loader.py

    Returns:
        The session dict after the interaction completes. Check session["error"]
        first — if it is not None, the interaction ended early and the other
        output fields (outfit_suggestion, fit_card) will be None.

    TODO — implement this function using the planning loop you designed in planning.md:

        Step 1: Initialize the session with _new_session().

        Step 2: Parse the user's query to extract a description, size, and
                max_price. You can use regex, string splitting, or ask the LLM
                to parse it — document your choice in planning.md.
                Store the result in session["parsed"].

        Step 3: Call search_listings() with the parsed parameters.
                Store results in session["search_results"].
                If no results: set session["error"] to a helpful message and
                return the session early. Do NOT proceed to suggest_outfit
                with empty input.

        Step 4: Select the item to use (e.g., the top result).
                Store it in session["selected_item"].

        Step 5: Call suggest_outfit() with the selected item and wardrobe.
                Store the result in session["outfit_suggestion"].

        Step 6: Call create_fit_card() with the outfit suggestion and selected item.
                Store the result in session["fit_card"].

        Step 7: Return the session.

    Before writing code, complete the Planning Loop and State Management sections
    of planning.md — your implementation should match what you described there.
    """
    # TODO: implement the planning loop
    session = _new_session(query, wardrobe)

    # Step 2: Parse the query with regex
    # Strategy: look for explicit size tokens (XS/S/M/L/XL/XXL or number sizes),
    # price ceilings ("under $30", "$30", "30 dollars"), and treat the rest as
    # the description. Regex is chosen over LLM here — it's deterministic, free,
    # and the patterns are well-defined enough that an LLM adds no value.
    import re

    size_pattern = r"(?:size\s+)?(XXS|XS|S\b|M\b|L\b|XL|XXL|[0-9]+[WTP])\b"
    price_pattern = r"(?:under|below|max|less than)?\s*\$?(\d+(?:\.\d+)?)\s*(?:dollars?)?"

    size_match = re.search(size_pattern, query, re.IGNORECASE)
    price_match = re.search(price_pattern, query, re.IGNORECASE)

    size = size_match.group(1).upper() if size_match else None
    max_price = float(price_match.group(1)) if price_match else None

    # Description: strip out the size/price tokens to get the clothing keywords
    description = query
    if size_match:
        description = description.replace(size_match.group(0), "")
    if price_match:
        description = description.replace(price_match.group(0), "")
    # Clean up filler words that don't help keyword matching
    for filler in ["under", "below", "max", "less than", "looking for",
                   "i want", "find me", "size", "dollars", "$"]:
        description = re.sub(filler, "", description, flags=re.IGNORECASE)
    description = " ".join(description.split())  # collapse whitespace

    session["parsed"] = {
        "description": description,
        "size": size,
        "max_price": max_price,
    }

    # Step 3: Search listings — branch on empty results
    results = search_listings(
        description=session["parsed"]["description"],
        size=session["parsed"]["size"],
        max_price=session["parsed"]["max_price"],
    )
    session["search_results"] = results

    if not results:
        filters = []
        if size:
            filters.append(f"size {size}")
        if max_price is not None:
            filters.append(f"under ${max_price:.0f}")
        filter_str = " and ".join(filters)
        hint = f" Try different keywords, a higher budget, or removing the size filter." if filters else " Try different keywords."
        session["error"] = (
            f"No listings found for '{description}'"
            + (f" ({filter_str})" if filter_str else "")
            + hint
        )
        return session  # ← early exit: suggest_outfit never called

    # Step 4: Select the top result (highest relevance score from search_listings)
    session["selected_item"] = results[0]

    # Step 5: Suggest outfit using selected item and wardrobe
    session["outfit_suggestion"] = suggest_outfit(
        new_item=session["selected_item"],
        wardrobe=session["wardrobe"],
    )

    # Step 6: Create fit card from outfit suggestion and selected item
    session["fit_card"] = create_fit_card(
        outfit=session["outfit_suggestion"],
        new_item=session["selected_item"],
    )

    # Step 7: Return completed session
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
 