FitFindr
Overview

FitFindr is a multi-tool AI agent that helps users find secondhand clothing items and style them using their existing wardrobe. The agent searches a mock thrift listing dataset, generates outfit suggestions, and creates a short social-media-style fit card. The goal is to simulate how an AI shopping assistant can combine search, reasoning, and content generation through multiple tool calls.

Tool Inventory
Tool 1: search_listings(description, size, max_price)

Purpose:
Searches the secondhand listings dataset for clothing items matching the user's request.

Inputs:

description (str): Item or style the user is looking for.
size (str | None): Desired size.
max_price (float | None): Maximum budget.

Outputs:

list[dict] containing matching listings.
Each listing contains:
id
title
description
category
style_tags
size
condition
price
colors
brand
platform

Failure Mode:
Returns an empty list if no matches are found.

Tool 2: suggest_outfit(new_item, wardrobe)

Purpose:
Uses the selected thrift item and wardrobe information to generate outfit recommendations.

Inputs:

new_item (dict): Selected listing returned by search_listings.
wardrobe (dict): User wardrobe information.

Outputs:

str containing one or more outfit suggestions.

Failure Mode:
If the wardrobe is empty, returns general styling advice rather than personalized recommendations.

Tool 3: create_fit_card(outfit, new_item)

Purpose:
Creates a short social-media-style caption describing the outfit.

Inputs:

outfit (str): Outfit suggestion from suggest_outfit.
new_item (dict): Selected thrift listing.

Outputs:

str containing a shareable fit card caption.

Failure Mode:
If the outfit string is empty, returns an informative error message instead of raising an exception.

Planning Loop

The agent follows a sequential planning process with conditional branching.

Parse the user query to extract:
description
size
max_price
Call search_listings().
If no results are returned:
Store an error message in session state.
Stop execution.
Do not call any additional tools.
If results are found:
Select the top result.
Store it as selected_item.
Call suggest_outfit(selected_item, wardrobe).
Store the returned outfit suggestion.
Call create_fit_card(outfit_suggestion, selected_item).
Return the completed session containing:
selected item
outfit suggestion
fit card

This allows the agent to behave differently depending on the search results instead of always executing the same sequence.

State Management

FitFindr uses a session dictionary as the single source of truth throughout an interaction.

The session stores:

query
parsed query information
search_results
selected_item
wardrobe
outfit_suggestion
fit_card
error

Information returned by one tool becomes input to the next tool.

Example:

search_listings returns a list of matching items.
The top result is stored as selected_item.
selected_item is passed to suggest_outfit.
suggest_outfit returns an outfit suggestion.
outfit_suggestion is passed to create_fit_card.
create_fit_card returns the final caption.

This prevents the user from having to re-enter information between steps.

Error Handling
search_listings

Failure: No matching listings found.

Agent Response:

"I couldn't find any listings that match that item, size, and budget. Try increasing your budget, using a broader description, or relaxing the size filter."

The workflow stops immediately.

suggest_outfit

Failure: Empty wardrobe.

Agent Response:

Returns general styling advice and explains that the recommendation is less personalized because wardrobe information is unavailable.

create_fit_card

Failure: Empty outfit string.

Agent Response:

"I need a complete outfit suggestion before I can create a fit card."

The tool returns the message instead of crashing.

Testing

The project includes pytest tests for all three tools.

Tests cover:

Successful listing search
Empty search results
Price filtering
Successful outfit generation
Empty wardrobe handling
Successful fit card creation
Empty outfit handling

All tests passed successfully.

Example command:

pytest tests/

Result:

7 passed
Spec Reflection
One way the spec helped

The planning document helped define the behavior of each tool before implementation. Writing the tool interfaces, planning loop, and error handling requirements first made it easier to generate and review code because there was already a clear specification to compare against.

One way the implementation diverged

The planning document originally described create_fit_card as accepting only an outfit object. During implementation, the starter code required create_fit_card(outfit, new_item). I updated the implementation to follow the starter code because the fit card needed item-specific information such as title, price, and platform.

AI Usage
Instance 1

What I gave the AI:

The Tool 1 specification from planning.md, including inputs, outputs, and failure handling requirements.

What it produced:

An implementation of search_listings that loaded listings, filtered by size and price, and scored results using keyword overlap.

What I changed:

I reviewed the implementation and verified that it returned an empty list instead of raising exceptions when no results were found.

Instance 2

What I gave the AI:

The Planning Loop, State Management, and Architecture sections from planning.md.

What it produced:

A complete implementation of run_agent() that connected the three tools together using session state.

What I changed:

I verified that the agent stopped when search_listings returned no results and that suggest_outfit and create_fit_card were not called on the failure path.

How to Run

Install dependencies:

pip install -r requirements.txt

Create a .env file:

GROQ_API_KEY=your_key_here

Run the application:

python app.py

Open the URL displayed in the terminal and enter a clothing query such as:

vintage graphic tee under $30

The application will return:

A recommended thrift listing
An outfit suggestion
A generated fit card caption