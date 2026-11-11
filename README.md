# ShopMate AI

**An AI-powered shopping assistant that helps users find products, compare options, build a cart, and experience a PayPal checkout flow.**

🌐 **Live demo:** https://shopmate-ai-sahil.streamlit.app  
💻 **Source code:** https://github.com/sahilS-ux/shopmate-ai

ShopMate AI is a hackathon prototype built with Python and Streamlit. A user describes what they need in natural language; Gemini extracts the shopping requirements, the app filters its sample product catalogue, and Gemini helps select a suitable match. Users can also browse the catalogue, add products to a cart, and complete a PayPal Sandbox checkout demonstration.

> **Payment demo notice:** Checkout currently creates a fixed **$1.00 USD PayPal Sandbox payment**. It does not charge the INR cart total. Product prices and the cart total are illustrative catalogue values. Sandbox payments do not move real money.

## Features

- **Natural-language shopping requests:** Describe a product, budget, brand preference, or minimum specifications in everyday language.
- **AI requirement extraction:** Gemini converts the request into structured fields such as category, product type, brand, maximum budget, RAM, and storage.
- **Catalogue matching:** Python filters the local sample catalogue against the extracted requirements.
- **AI-assisted recommendation:** Gemini compares the matching catalogue entries and selects a recommendation using the supplied product data.
- **Product exploration:** Search the catalogue and browse by category.
- **Shopping cart:** Add products, review quantities and subtotals, and remove items.
- **PayPal Sandbox checkout:** Create a PayPal order, redirect the buyer to PayPal for approval, verify the returned order, and capture the payment.
- **Payment receipt:** Display the PayPal order ID, capture ID, Sandbox payment status, and a summary of the cart.

## Technology stack

| Technology | Purpose |
|---|---|
| Python | Application logic and integrations |
| Streamlit | Web application interface and session state |
| Google Gemini API (gemini-2.5-flash) | Extract shopping requirements and explain product recommendations |
| PayPal REST API (Sandbox) | Create, approve, verify, and capture the demo checkout |
| JSON | Store the sample product catalogue and pending cart snapshots |
| requests | Send HTTP requests to PayPal |

## How it works

1. The user enters a shopping request, for example: “Find a laptop under ₹60,000 with at least 16GB RAM and 512GB storage.”
2. Gemini returns structured shopping requirements in JSON.
3. The Python application validates the extracted category and brand, then filters products.json using the budget and available specifications.
4. Gemini receives only the matching catalogue entries and selects a recommendation with an explanation. The app validates that the selected product ID belongs to the matching results.
5. The user adds products to the cart and proceeds to checkout.
6. The app creates a **$1.00 USD Sandbox order** through the PayPal REST API and sends the buyer to PayPal to approve it.
7. When the buyer returns, the app retrieves the order from PayPal, checks the expected intent, amount, and description, and captures the order if it is approved.
8. The app checks for a completed capture, then displays the receipt and clears the cart.

## Run locally

### 1. Clone the repository

~~~bash
git clone https://github.com/sahilS-ux/shopmate-ai.git
cd shopmate-ai
~~~

### 2. Create and activate a virtual environment

**Linux / macOS:**

~~~bash
python3 -m venv .venv
source .venv/bin/activate
~~~

**Windows PowerShell:**

~~~powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
~~~

### 3. Install dependencies

~~~bash
pip install -r requirements.txt
~~~

### 4. Configure API credentials

Create a folder named .streamlit in the project directory, then create a file named secrets.toml inside it.

Add your own credentials using this structure:

~~~toml
GEMINI_API_KEY = "YOUR_GEMINI_API_KEY"

[paypal]
client_id = "YOUR_PAYPAL_SANDBOX_CLIENT_ID"
client_secret = "YOUR_PAYPAL_SANDBOX_CLIENT_SECRET"
base_url = "https://api-m.sandbox.paypal.com"
~~~

Replace the placeholders with your own Gemini API key and PayPal **Sandbox** app credentials.

**Keep credentials private.** Never commit .streamlit/secrets.toml, API keys, PayPal client secrets, or .env files to GitHub. The repository's .gitignore excludes local secrets.

### 5. Start the application

~~~bash
streamlit run app.py
~~~

Streamlit will print a local address (usually http://localhost:8501) that you can open in your browser.

## PayPal Sandbox testing

- Use PayPal Developer Sandbox credentials and a Sandbox buyer account.
- The current demo checkout amount is always **$1.00 USD**, regardless of the products or INR total in the cart.
- The app displays the INR cart total as an illustrative product total; it is not the amount sent to PayPal.
- A Sandbox payment is a test transaction and does not charge real money.
- Do not use Live PayPal credentials for this prototype.

## Deployment

The current public Streamlit Community Cloud deployment is:

**https://shopmate-ai-sahil.streamlit.app**

The deployed app uses Streamlit's Secrets settings for the Gemini and PayPal Sandbox credentials. Do not put secrets in source code or the public repository.

## Project structure

~~~text
shopmate-ai/
├── app.py                 # Streamlit application, Gemini and PayPal logic
├── products.json          # Sample product catalogue
├── requirements.txt       # Python dependencies
├── README.md              # Project documentation
└── .gitignore             # Excludes local secrets and generated files
~~~

At runtime, the app also creates a pending_paypal_orders/ folder to store a cart snapshot while a Sandbox order is awaiting the buyer's return.

## Prototype scope and limitations

- This is a hackathon prototype, not a production e-commerce platform.
- Product listings, specifications, and prices come from a sample JSON catalogue; the app does not fetch live inventory or market prices.
- PayPal checkout is a fixed-value Sandbox demonstration, not a real purchase of the cart contents.
- Pending cart snapshots are currently stored as local files. A production deployment should use durable shared storage and a more robust order database before relying on this flow at scale.
- API availability, quotas, and Sandbox account configuration can affect external service calls.

## Security notes

- Keep Gemini and PayPal credentials in Streamlit Secrets or a local secrets file that is excluded from version control.
- Use Sandbox credentials for testing.
- Never publish buyer credentials, client secrets, access tokens, or private keys.
- Do not treat the demo receipt as proof of a real-money transaction.

---

Built as a PayPal hackathon project: **ShopMate AI — Intelligent Shopping, Simplified.**
