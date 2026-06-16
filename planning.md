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
<!-- Describe what this tool does in 1–2 sentences -->
Searches the mock secondhand listings dataset for items that match the user's requested description, size, and maximum price. It filters listings using fields such as title, description, category, style tags, size, colors, brand, platform, condition, and price.

**Input parameters:**
<!-- List each parameter, its type, and what it represents -->
- `description` (str): The item or style the user is looking for, such as "vintage graphic tee" or "black leather jacket".
- `size` (str): The user's desired size, such as "S", "M", "L", or a shoe size if applicable.
- `max_price` (float): The highest price the user is willing to pay.

**What it returns:**
<!-- Describe the return value — what fields does a result contain? -->
A list of matching listing dictionaries. Each result should include fields such as id, title, description, category, style_tags, size, condition, price, colors, brand, and platform.
**What happens if it fails or returns nothing:**
<!-- What should the agent do if no listings match? -->
If no listings match, the tool should return an empty list or a clear no-results response. The agent should explain that no matching items were found and suggest changing the search, such as increasing the budget, broadening the description, or relaxing the size filter. The agent should not call suggest_outfit if there is no item to style.
---

### Tool 2: suggest_outfit

**What it does:**
<!-- Describe what this tool does in 1–2 sentences -->
Suggests one or more outfit combinations using the newly found item and the user's current wardrobe. It should choose wardrobe pieces that match the new item's category, colors, and style tags.
**Input parameters:**
<!-- List each parameter, its type, and what it represents -->
- `new_item` (dict): The listing selected from search_listings, including its title, category, colors, price, platform, and style tags.
- `wardrobe` (dict): The user's wardrobe data containing owned clothing items and their fields, such as category, colors, style tags, and notes.

**What it returns:**
<!-- Describe the return value -->
An outfit suggestion that includes the new item, selected wardrobe pieces, and a short styling explanation. The return value should be structured enough for create_fit_card to use in the next step.
**What happens if it fails or returns nothing:**
<!-- What should the agent do if the wardrobe is empty or no outfit can be suggested? -->
If the wardrobe is empty or too minimal, the tool should still suggest a simple outfit using generic basics, or ask the user to add wardrobe details. It should not crash if the wardrobe has no usable items.
---

### Tool 3: create_fit_card

**What it does:**
<!-- Describe what this tool does in 1–2 sentences -->
Creates a short, shareable outfit description based on the selected thrifted item and the outfit suggestion. The output should sound like a social caption rather than a technical product description.
**Input parameters:**
<!-- List each parameter, its type, and what it represents -->
- `outfit` (...): The outfit suggestion returned by suggest_outfit, including the new item, wardrobe pieces, and styling notes.

**What it returns:**
<!-- Describe the return value -->
A short fit card or caption describing the completed outfit. The fit card should highlight the overall style and outfit combination in a way that is easy to share.
**What happens if it fails or returns nothing:**
<!-- What should the agent do if the outfit data is incomplete? -->
If the outfit data is missing or incomplete, the tool should return a clear message explaining that a complete outfit is required before a fit card can be generated. The agent should ask the user for more information instead of creating a misleading caption.
---

### Additional Tools (if any)

<!-- Copy the block above for any tools beyond the required three -->

---

## Planning Loop

**How does your agent decide which tool to call next?**
<!-- Describe the logic your planning loop uses. What does it look at? What conditions change its behavior? How does it know when it's done? -->
The agent first determines whether the user is searching for an item. If so, it calls search_listings. If a matching item is found, the agent stores the selected listing and calls suggest_outfit. If an outfit is successfully generated, the agent calls create_fit_card. The loop ends when either a complete recommendation is produced or a failure condition is encountered.
---

## State Management

**How does information from one tool get passed to the next?**
<!-- Describe how your agent stores and accesses state within a session. What data is tracked? How is it passed between tool calls? -->
The agent stores information from previous tool calls in session state. The selected item returned by search_listings is stored and passed to suggest_outfit. The outfit returned by suggest_outfit is stored and passed to create_fit_card. This allows the user to complete a multi-step workflow without re-entering information.
---

## Error Handling

For each tool, describe the specific failure mode you're handling and what the agent does in response.

| Tool | Failure mode | Agent response |
|------|-------------|----------------|
| search_listings | No results match the query | Inform the user that no listings were found and suggest adjusting filters.|
| suggest_outfit | Wardrobe is empty | Explain that the wardrobe is empty and provide a generic styling suggestion or request more information.|
| create_fit_card | Outfit input is missing or incomplete | Explain that a complete outfit is required before generating a fit card.|

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

     ```text
User Request
     |
     v
Planning Loop
     |
     |-- If user is searching for an item:
     v
search_listings(description, size, max_price)
     |
     |-- If no results:
     |      -> Tell user no matches were found
     |      -> Suggest broadening search
     |      -> Stop
     |
     |-- If results found:
     v
Save selected_item in Session State
     |
     v
suggest_outfit(new_item, wardrobe)
     |
     |-- If wardrobe is empty:
     |      -> Give limited/basic styling suggestion
     |      -> Ask user to add wardrobe details
     |
     |-- If outfit created:
     v
Save outfit in Session State
     |
     v
create_fit_card(outfit)
     |
     v
Final Response to User
     |
     |-- Recommended listing
     |-- Outfit suggestion
     |-- Shareable fit card
```

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

**Milestone 4 — Planning loop and state management:**

---

## A Complete Interaction (Step by Step)

Write out what a full user interaction looks like from start to finish — tool call by tool call. Use a specific example query.

**Example user query:** "I'm looking for a vintage graphic tee under $30. I mostly wear baggy jeans and chunky sneakers. What's out there and how would I style it?"

**Step 1:**
<!-- What does the agent do first? Which tool is called? With what input? -->
The agent reads the request and identifies that the user wants to search for a clothing item. It extracts the item description, size if available, and maximum price. The agent calls:

search_listings(
    description="vintage graphic tee",
    size="M",
    max_price=30.0
)

The tool searches data/listings.json using fields such as title, description, category, style tags, size, price, colors, brand, and platform.
**Step 2:**
<!-- What happens next? What was returned from step 1? What tool is called now? -->
If matching listings are found, the agent selects the best result and saves it in session state as selected_item. For example, the selected item might be a graphic tee from Depop under the user's budget. The agent then calls:

suggest_outfit(
    new_item=selected_item,
    wardrobe=user_wardrobe
)

The wardrobe comes from the user's wardrobe data, using the same structure shown in data/wardrobe_schema.json.
**Step 3:**
<!-- Continue until the full interaction is complete -->
The outfit suggestion returned by suggest_outfit is stored in session state as outfit. The agent then calls:

create_fit_card(
    outfit=outfit
)

The tool generates a short, shareable caption based on the completed outfit.
**Final output to user:**
<!-- What does the user actually see at the end? -->
The user receives:

The recommended thrift listing
A suggested outfit using their wardrobe
A short social-style fit card caption

If search_listings returns no results, the agent explains that no matching items were found and suggests adjusting the budget, size, or item description. The agent then stops and does not call suggest_outfit or create_fit_card.