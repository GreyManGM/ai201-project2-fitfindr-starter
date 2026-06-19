# FitFindr — planning.md

> Complete this document before writing any implementation code.
> Your spec and agent diagram are what you'll use to direct AI tools (Claude, Copilot, etc.) to generate your implementation — the more specific they are, the more useful the generated code will be.
> Your planning.md will be reviewed as part of your submission.
> Update it before starting any stretch features.

---

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

### Additional Tools (if any)

<!-- Copy the block above for any tools beyond the required three -->

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

## Architecture

<!-- Draw a diagram of your agent showing how the components connect:
     User input → Planning Loop → Tools (search_listings, suggest_outfit, create_fit_card)
                                                                          ↕
                                                                   State / Session
     Show what triggers each tool, how state flows between them, and where error paths branch off.
     ASCII art, a Mermaid diagram (https://mermaid.js.org/syntax/flowchart.html), or an embedded
     sketch are all fine. You'll share this diagram with an AI tool when asking it to implement
     the planning loop and each individual tool. -->

     +----------------+
       | User Input |
     +--------+-------+
              | 
              v 
     +----------------+ 
     | Planning Loop | 
     +--------+-------+
                | 
Search Request? | 
                v 
     +------------------+ 
     | search_listings | 
     +--------+---------+ 
          | 
 Results Found? 
  /          \ 
 No          Yes 
 |            | 
 v            v 
Suggest New  Store Results 
 Search       | 
              v 
+----------------+ 
| Session State | 
+--------+-------+ 
          | 
          v 
+----------------+ 
| suggest_outfit | 
+--------+-------+ 
         | 
         v
+----------------+ 
| create_fit_card| 
+--------+-------+ 
          | 
          v 
+----------------+ 
| Final Response | 
+----------------+
     

---

## AI Tool Plan

<!-- For each part of the implementation below, describe:
     - Which AI tool you plan to use (Claude, Copilot, ChatGPT, etc.)
     - What you'll give it as input (which sections of this planning.md, your agent diagram)
     - What you expect it to produce
     - How you'll verify the output matches your spec before moving on

     "I'll use AI to help me code" is not a plan.
     "I'll give Claude my Tool 1 spec (inputs, return value, failure mode) and ask it to implement
     search_listings() using load_listings() from the data loader — then test it against 3 queries
     before trusting it" is a plan. -->

**Milestone 3 — Individual tool implementations:** 
search_listings
AI Tool: Claude
Input: Tool specification (inputs, outputs, failure behavior)
Expected Output: Python function that filters listing data based on keywords, size, and price.
Verification: Test with multiple search queries and confirm matching results are returned.

suggest_outfit
AI Tool: Claude
Input: Tool specification and sample wardrobe data.
Expected Output: Function that generates outfit recommendations from wardrobe items.
Verification: Test with both populated and empty wardrobes.

create_fit_card
AI Tool: Claude
Input: Tool specification and sample outfit suggestions.
Expected Output: Function that creates short social-media-style captions.
Verification: Ensure outputs are 2–4 sentences and remain readable.

**Milestone 4 — Planning loop and state management:**
AI Tool: Claude
Input: Full planning document and architecture diagram.
Expected Output: Main agent loop that routes requests between tools and manages session state.
Verification:
Test normal workflow.
Test empty search results.
Test empty wardrobe.
Confirm state passes correctly between all tools.

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
