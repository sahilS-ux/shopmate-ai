# ShopMate AI

An AI-powered shopping assistant built with Python and Streamlit. Users can describe what they want, receive product recommendations, explore a sample catalogue, manage a cart, and complete a PayPal Sandbox demo checkout.

## Features

- AI-assisted product recommendations using the Gemini API.
- Product catalogue with category browsing and search.
- Shopping cart with quantity management.
- PayPal Sandbox checkout demonstration.
- Purchase receipt after a successful Sandbox payment.

## Tech stack

- Python
- Streamlit
- Google Gemini API
- PayPal REST API (Sandbox)

## Run locally

1. Clone this repository:

   ```bash
   git clone https://github.com/sahilS-ux/shopmate-ai.git
   cd shopmate-ai
   ```

2. Create and activate a virtual environment:

   ```bash
   python -m venv .venv
   source .venv/bin/activate
   ```

   On Windows, activate it with:

   ```powershell
   .venv\Scripts\Activate.ps1
   ```

3. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. Create `.streamlit/secrets.toml` and add your own credentials. Do not commit this file.

   Configure the Gemini key as `GEMINI_API_KEY` and the PayPal Sandbox credentials under the `paypal` section, using the exact key names expected by `app.py`.

5. Start the app:

   ```bash
   streamlit run app.py
   ```

## PayPal Sandbox demo note

The current checkout is a hackathon demonstration: it charges a fixed **$1.00 USD Sandbox amount**, not the INR value of the shopping cart. The INR cart total shown on the receipt is an illustrative catalogue total and is not the amount charged by PayPal. Sandbox transactions do not move real money.

The PayPal return and cancel URLs in the app are configured for local development. They must be changed to the deployed app URL before using a hosted deployment.

## Security

- Never commit API keys, PayPal client secrets, `.env` files, or `.streamlit/secrets.toml`.
- Use PayPal Sandbox credentials only for this demo.
- The repository's `.gitignore` excludes local secrets, virtual environments, and pending local order snapshots.

## Project status

This is a hackathon prototype. Product information is sample catalogue data, and checkout is a Sandbox demonstration rather than a production payment system.
