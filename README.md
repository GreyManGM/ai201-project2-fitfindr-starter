# FitFindr — Starter Kit

This starter kit contains everything you need to begin Project 2.

## What's Included

```
ai201-project2-fitfindr-starter/
├── data/
│   ├── listings.json          # 40 mock secondhand listings
│   └── wardrobe_schema.json   # Wardrobe format + example wardrobe
├── utils/
│   └── data_loader.py         # Helper functions for loading the data
├── planning.md                # Your planning template — fill this out first
└── requirements.txt           # Python dependencies
```

## Setup

```bash
pip install -r requirements.txt
```

Set your Groq API key in a `.env` file (get a free key at [console.groq.com](https://console.groq.com)):
```
GROQ_API_KEY=your_key_here
```

## The Mock Listings Dataset

`data/listings.json` contains 40 mock secondhand listings across categories (tops, bottoms, outerwear, shoes, accessories) and styles (vintage, y2k, grunge, cottagecore, streetwear, and more).

Each listing has: `id`, `title`, `description`, `category`, `style_tags`, `size`, `condition`, `price`, `colors`, `brand`, and `platform`.

Load it with:
```python
from utils.data_loader import load_listings
listings = load_listings()
```

## The Wardrobe Schema

`data/wardrobe_schema.json` defines the format your agent uses to represent a user's existing wardrobe. It includes:

- `schema`: field definitions for a wardrobe item
- `example_wardrobe`: a sample wardrobe with 10 items you can use for testing
- `empty_wardrobe`: a starting template for a new user

Load an example wardrobe with:
```python
from utils.data_loader import get_example_wardrobe
wardrobe = get_example_wardrobe()
```

## Where to Start

1. **Read `planning.md` and fill it out before writing any code.**
2. Verify the data loads correctly by running `python utils/data_loader.py`.
3. Build and test each tool individually before connecting them through your planning loop.

Your implementation files go in this same directory. There's no required file structure for your agent code — organize it however makes sense for your design.


## Tools

List every tool your agent will use. For each tool, fill in all four fields.
You must have at least 3 tools. The three required tools are listed — add any additional tools below them.

### Tool 1: search_listings

**What it does:**
<!-- Describe what this tool does in 1–2 sentences --> The search_listings tool searches the dataset for items matching the description, optional size, and optional price ceiling. 

**Input parameters:**
<!-- List each parameter, its type, and what it represents -->
- `description` (str): Keywords describing what the user is looking for
- `size` (str): Size string to filter by
- `max_price` (float): Maximum price (inclusive)

**What it returns:**
<!-- Describe the return value — what fields does a result contain? --> It then returns matching listing dicts. It contains id, title, description, category, style_tags (list), size, condition, price (float), colors (list), brand, platform

**What happens if it fails or returns nothing:**
<!-- What should the agent do if no listings match? --> If it fails or nothing matches, it should return the empty list without raising an exception.

---

### Tool 2: suggest_outfit

**What it does:**
<!-- Describe what this tool does in 1–2 sentences --> Suggest outfit suggests 1–2 complete outfits given a thrifted item and the user's wardrobe.

**Input parameters:**
<!-- List each parameter, its type, and what it represents -->
- `new_item` (dict): A listing dict (the item the user is considering buying).
- `wardrobe` (dict):  A wardrobe dict with an 'items' key containing a list of wardrobe item dicts.

**What it returns:**
<!-- Describe the return value --> Returns a non-empty string with outfit suggestions.

**What happens if it fails or returns nothing:**
<!-- What should the agent do if the wardrobe is empty or no outfit can be suggested? --> If it fails or the wardrobe is empty, it should offer general styling advice for the item rather than raising an exception or returning an empty string.

---

### Tool 3: create_fit_card

**What it does:**
<!-- Describe what this tool does in 1–2 sentences --> The tool generates a short, shareable outfit caption for the thrifted find.

**Input parameters:**
<!-- List each parameter, its type, and what it represents -->
- `outfit` (...): The outfit suggestion string from suggest_outfit().

**What it returns:**
<!-- Describe the return value --> Returns a 2–4 sentence string usable as an Instagram/TikTok caption.

**What happens if it fails or returns nothing:**
<!-- What should the agent do if the outfit data is incomplete? --> If outfit is empty or missing, return a descriptive error message string without raising an exception.

---


## Planning Loop

**How does your agent decide which tool to call next?**
<!-- Describe the logic your planning loop uses. What does it look at? What conditions change its behavior? How does it know when it's done? --> The agent analyzes the user's request to determine whether they are looking for thrifted clothing recommendations. If the user requests clothing items, the agent calls search_listings() with the relevant keywords, size preferences, and price constraints. If matching listings are found, the agent selects the most relevant item(s) and stores them in session state. The agent then calls suggest_outfit() using the selected listing and the user's wardrobe information. After an outfit suggestion is generated, the agent calls create_fit_card() to generate a shareable caption. The agent combines the listing recommendations, outfit suggestions, and fit card into a final response. The process ends once the user receives recommendations and styling advice.

---

## State Management

**How does information from one tool get passed to the next?**
<!-- Describe how your agent stores and accesses state within a session. What data is tracked? How is it passed between tool calls? --> Information passed from one tool to the next sequentially. Each tool's output is stored in state and becomes input for the next tool.

---

## Error Handling

For each tool, describe the specific failure mode you're handling and what the agent does in response.

| Tool | Failure mode | Agent response |
|------|-------------|----------------|
| search_listings | No results match the query | Inform the user that no matches were found and suggest broadening the search criteria (different keywords, larger budget, or removing size filters). |
| suggest_outfit | Wardrobe is empty | Generate general styling advice using the thrifted item and explain that recommendations would improve with wardrobe details. |
| create_fit_card | Outfit input is missing or incomplete | Return an error message explaining that a valid outfit recommendation is required before creating a fit card. |

---

## Spec Reflection

**One way the spec helped**
The error handling table in planning.md was the most directly useful part of the spec. Having the three failure modes written out before implementation meant the search_listings returning [] instead of raising, suggest_outfit branching on empty wardrobe, and create_fit_card checking for a whitespace-only outfit string were all written correctly on the first pass because the spec said exactly what each function should do when things go wrong.

**One way implementation diverged**
The spec's query parsing description said "the agent analyzes the user's request" without committing to a method. During implementation, regex was chosen over an LLM call — the spec implied the LLM would handle parsing since the whole system uses one, but regex turned out to be more reliable and free. This also revealed a bug the spec couldn't have anticipated: the numeric size pattern [0-9]+ matched price digits before the price pattern could claim them, so "under $30" parsed 30 as a size. The fix (requiring a W/T/P suffix on numeric sizes, and running price extraction before size extraction) diverged from anything the spec described because the spec never got specific enough about parsing order.

---

## AI Usage
**Instance 1:** I gave Claude the Tool 1 spec block (inputs, return value, failure mode) and the data_loader.py source and asked to implement the function. The generated code was reviewed against the spec before running: parameters matched, [] was returned on failure, and the keyword scoring logic covered all the listing fields. 

**Instance 2:** I gave Claude the Tool 2 spec block and asked to implement suggest_outfit(). The spec said: "if the wardrobe is empty, offer general styling advice rather than raising an exception or returning an empty string." The generated code handled the branch correctly and checked wardrobe.get("items", []) and built a different prompt for the empty case.

---

## A Complete Interaction (Step by Step)

Write out what a full user interaction looks like from start to finish — tool call by tool call. Use a specific example query.

**Example user query:** "I'm looking for a vintage graphic tee under $30. I mostly wear baggy jeans and chunky sneakers. What's out there and how would I style it?"

**Step 1:**
<!-- What does the agent do first? Which tool is called? With what input? --> The agent first receives the user's request and determines what information it needs to answer the query. The search_listing tool is called.
The input is:
{
    "category": "tops",
    "style_tags": ["graphic tee", "vintage"],
    "price": 30.00
}

**Step 2:**
<!-- What happens next? What was returned from step 1? What tool is called now? --> The search_listing tool returns matching items: shirts, prices, brands, and descriptions. 

**Step 3:**
<!-- Continue until the full interaction is complete --> The agent reviews the retrieved listings and user's preferences, determining there is enough information to provide recommendations.

**Final output to user:**
<!-- What does the user actually see at the end? --> The suggest_outfit tool returns recommendations, explaining why they work for the user.
