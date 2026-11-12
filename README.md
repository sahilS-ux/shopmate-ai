# ShopMate AI

**A conversational shopping assistant that turns a product brief into a shortlist, compares live retailer offers, and demonstrates a PayPal Sandbox checkout.**

- **Live demo:** https://shopmate-ai-sahil.streamlit.app
- **Source:** https://github.com/sahilS-ux/shopmate-ai

ShopMate AI is a hackathon prototype for shoppers who want help narrowing down choices. Describe what you need in everyday language. Gemini extracts requirements and recommends an item from the sample catalogue. Channel3 can search live products and retailer offers. A demo cart can be checked out through PayPal Sandbox.

> **Payment demo:** PayPal checkout converts the INR cart total to USD using a daily reference rate and sends an itemized order to PayPal Sandbox. This is a test transaction — Sandbox does not move real money.

## Features

- **Natural-language product brief:** Enter a product type, budget, preferred brand, and specifications.
- **AI requirement extraction:** Gemini turns the brief into structured shopping requirements.
- **Catalogue recommendations:** ShopMate filters the local sample catalogue and asks Gemini to select a suitable match from those results.
- **Live product discovery:** Search Channel3 for product listings, images, retailer offers, and buy links.
- **Rupee comparison:** USD offers show an approximate INR equivalent using a cached daily reference rate. The original retailer price remains visible.
- **Sample catalogue and cart:** Browse the INR demo catalogue, add items, and review quantities and subtotals.
- **Itemized PayPal checkout:** Convert INR cart prices to USD using a live exchange rate, send product-level line items to PayPal, verify, capture, and show a receipt with both currencies.

## How a shopping session works

1. Enter a natural-language shopping request.
2. Gemini extracts requirements such as category, budget, brand, RAM, and storage.
3. ShopMate filters the products.json catalogue using those requirements.
4. Gemini recommends an item from the matching catalogue products and explains the choice.
5. Optionally search Channel3 for live products and retailer offers. Channel3 uses its default US/USD market in this app; the rupee figure is an estimate for comparison, not the retailer's checkout price. Shipping and taxes may differ.
6. Add sample-catalogue products to the cart.
7. At checkout, ShopMate converts the INR cart total to USD at the daily reference rate and sends an itemized order to PayPal Sandbox. After approval and capture, a receipt shows both the INR and USD totals.

Channel3 live listings are separate from the sample cart and PayPal Sandbox checkout.

## Technology

| Technology | Role |
|---|---|
| Python | Application logic and API integrations |
| Streamlit | Web interface and session state |
| Google Gemini API, gemini-2.5-flash | Extract requirements and recommend a catalogue match |
| Channel3 API | Live product search and retailer offers |
| PayPal REST API, Sandbox | Create itemized orders with converted USD prices, verify, and capture |
| Frankfurter API | Daily USD/INR reference rate for approximate display conversion |
| JSON | Sample product catalogue and pending checkout cart snapshot |
| requests | HTTP calls to external APIs |

## Run locally

### 1. Clone the repository

    git clone https://github.com/sahilS-ux/shopmate-ai.git
    cd shopmate-ai

### 2. Create and activate a virtual environment

**Linux / macOS**

    python3 -m venv .venv
    source .venv/bin/activate

**Windows PowerShell**

    py -m venv .venv
    .venv\Scripts\Activate.ps1

### 3. Install dependencies

    pip install -r requirements.txt

### 4. Configure credentials

Copy .streamlit/secrets.toml.example to .streamlit/secrets.toml, then replace the placeholders with your own credentials:

    GEMINI_API_KEY = "YOUR_GEMINI_API_KEY"
    CHANNEL3_API_KEY = "YOUR_CHANNEL3_API_KEY"

    [paypal]
    client_id = "YOUR_PAYPAL_SANDBOX_CLIENT_ID"
    client_secret = "YOUR_PAYPAL_SANDBOX_CLIENT_SECRET"
    base_url = "https://api-m.sandbox.paypal.com"

The Channel3 key enables live search. The Gemini and PayPal Sandbox credentials enable AI recommendations and the payment demo. Frankfurter does not require a key; if its rate endpoint is unavailable, live offers remain visible in their listed currency.

**Never commit .streamlit/secrets.toml, API keys, PayPal client secrets, or .env files.** The repository's .gitignore excludes local secrets.

### 5. Start ShopMate

    streamlit run app.py

Open the local URL printed by Streamlit, usually http://localhost:8501.

## Deploy on Streamlit Community Cloud

The public demo is hosted at https://shopmate-ai-sahil.streamlit.app.

For a new deployment, select this GitHub repository, the main branch, and app.py as the entrypoint. Add the credential TOML in the app's **Settings → Secrets** area. For an existing deployment connected to this repository, commits to its configured branch trigger an update.

Local .streamlit/secrets.toml is not sent to Streamlit Cloud or GitHub. Configure local and deployed secrets separately.

## Repository layout

    shopmate-ai/
    ├── app.py
    ├── products.json
    ├── requirements.txt
    ├── .streamlit/
    │   └── secrets.toml.example
    └── .gitignore

During checkout, the app writes a pending cart snapshot under pending_paypal_orders/. This folder is excluded from Git.

## Prototype scope and limitations

- The catalogue in products.json is illustrative; it is not a live inventory feed.
- Channel3 currently returns its default US/USD market in this integration. The approximate INR display uses a daily reference exchange rate and is not a quote or a promise that a retailer ships to India.
- The INR cart total is converted to USD at a daily reference rate. Minor rounding differences are possible.
- The PayPal transaction is a Sandbox test and does not charge real money.
- Pending checkout snapshots are stored as local files. A production application should use durable shared storage and a transactional order database.
- Product prices, availability, API behavior, and quotas can change.

## PayPal AI Hackathon demo

For the Devpost entry, include the public demo URL, this public source repository, and a public YouTube walkthrough under three minutes. A clear walkthrough can show the request, AI recommendation, Channel3 results with the approximate rupee display, cart with INR-to-USD conversion, itemized PayPal checkout, and Sandbox confirmation receipt.

## License

This project is released under the MIT License. See LICENSE.
