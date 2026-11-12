import streamlit as st
import json
import os
import re
import requests
import uuid
from pathlib import Path
from google import genai


# --------------------------------------------------
# 1. PAGE CONFIGURATION
# --------------------------------------------------

st.set_page_config(
    page_title="ShopMate AI",
    page_icon="🛍️",
    layout="wide"
)


# --------------------------------------------------
# CUSTOM UI STYLING
# --------------------------------------------------

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Manrope:wght@500;600;700;800&display=swap');

:root {
    --ink: #132238;
    --muted: #65758b;
    --line: #e6edf3;
    --paper: #ffffff;
    --canvas: #f5f8fb;
    --teal: #0e9f8a;
    --teal-dark: #087c70;
    --mint: #d8f5eb;
}

.stApp {
    background:
        radial-gradient(ellipse at 8% 0%, rgba(202, 245, 230, .5), transparent 34rem),
        var(--canvas);
    color: var(--ink);
    font-family: 'DM Sans', sans-serif;
}

.block-container {
    max-width: 1380px;
    padding-top: 1.4rem;
    padding-bottom: 4rem;
}

h1, h2, h3, h4, h5, h6,
.stMarkdown h1, .stMarkdown h2, .stMarkdown h3 {
    color: var(--ink) !important;
    font-family: 'Manrope', sans-serif !important;
    letter-spacing: -.035em;
}

p, label, .stMarkdown { color: #334155; }
.stCaption, [data-testid="stCaptionContainer"] { color: var(--muted) !important; }

.hero {
    position: relative;
    overflow: hidden;
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 2rem;
    min-height: 285px;
    margin: .4rem 0 1.5rem;
    padding: clamp(2rem, 5vw, 4.1rem);
    border: 1px solid rgba(255,255,255,.12);
    border-radius: 30px;
    color: white;
    background:
        radial-gradient(circle at 80% 25%, rgba(22, 188, 159, .42), transparent 22rem),
        linear-gradient(118deg, #10243a 0%, #173a50 56%, #086c68 100%);
    box-shadow: 0 22px 54px rgba(16, 36, 58, .16);
}

.hero::after {
    content: '';
    position: absolute;
    width: 280px;
    height: 280px;
    right: 7%;
    bottom: -205px;
    border: 1px solid rgba(255,255,255,.22);
    border-radius: 50%;
    box-shadow: 0 0 0 28px rgba(255,255,255,.04), 0 0 0 58px rgba(255,255,255,.035);
}

.hero-copy { position: relative; z-index: 1; max-width: 720px; }
.hero-kicker {
    display: inline-flex;
    align-items: center;
    gap: .55rem;
    margin-bottom: 1rem;
    color: #b9f4e0;
    font-size: .73rem;
    font-weight: 700;
    letter-spacing: .14em;
    text-transform: uppercase;
}
.hero-copy h1 {
    margin: 0 0 .7rem;
    color: white !important;
    font-size: clamp(2.5rem, 5vw, 4.2rem);
    line-height: 1.04;
}
.hero-copy p {
    max-width: 630px;
    margin: 0;
    color: rgba(240, 249, 255, .82);
    font-size: 1.05rem;
    line-height: 1.65;
}
.hero-aside {
    position: relative;
    z-index: 1;
    min-width: 220px;
    padding: 1.2rem 1.35rem;
    border: 1px solid rgba(255,255,255,.18);
    border-radius: 20px;
    background: rgba(255,255,255,.08);
    backdrop-filter: blur(10px);
}
.hero-aside small { color: #b9f4e0; font-weight: 700; letter-spacing: .1em; text-transform: uppercase; }
.hero-step { display: flex; gap: .75rem; align-items: center; margin-top: .9rem; color: white; font-weight: 600; }
.hero-step span {
    display: grid; place-items: center; width: 28px; height: 28px; border-radius: 50%;
    color: #0d4a4a; background: #b9f4e0; font-size: .75rem; font-weight: 800;
}

.sample-product-visual {
    display: flex;
    align-items: center;
    justify-content: space-between;
    min-height: 112px;
    margin-bottom: .9rem;
    padding: 1rem 1.2rem;
    border-radius: 15px;
    background: linear-gradient(125deg, #e1f5ed, #eff5fb 58%, #e1edf8);
}
.sample-product-visual span { font-size: 3rem; line-height: 1; }
.sample-product-visual small {
    padding: .4rem .7rem;
    border: 1px solid rgba(14,159,138,.16);
    border-radius: 999px;
    color: #087c70;
    background: rgba(255,255,255,.72);
    font-size: .68rem;
    font-weight: 800;
    letter-spacing: .08em;
    text-transform: uppercase;
}

.section-kicker {
    margin: 0 0 .25rem;
    color: var(--teal-dark);
    font-size: .72rem;
    font-weight: 800;
    letter-spacing: .13em;
    text-transform: uppercase;
}

.stButton > button, .stLinkButton > a {
    min-height: 2.8rem;
    border: 1px solid transparent;
    border-radius: 12px;
    color: white;
    background: var(--teal);
    font-weight: 700;
    transition: transform .16s ease, background .16s ease, box-shadow .16s ease;
    box-shadow: 0 5px 14px rgba(14, 159, 138, .16);
}
.stButton > button:hover, .stLinkButton > a:hover {
    border-color: transparent;
    color: white;
    background: var(--teal-dark);
    transform: translateY(-1px);
    box-shadow: 0 8px 18px rgba(14, 159, 138, .23);
}

.stTextInput input, .stTextArea textarea, .stSelectbox [data-baseweb="select"] > div {
    border-radius: 12px;
    border-color: #dbe5ec;
    background-color: white;
}
.stTextArea textarea:focus, .stTextInput input:focus {
    border-color: #35b8a1;
    box-shadow: 0 0 0 3px rgba(53,184,161,.12);
}

div[data-testid="stVerticalBlockBorderWrapper"] {
    padding: 1rem;
    border: 1px solid var(--line);
    border-radius: 20px;
    background: var(--paper);
    box-shadow: 0 7px 24px rgba(19, 34, 56, .045);
    transition: transform .16s ease, box-shadow .16s ease;
}
div[data-testid="stVerticalBlockBorderWrapper"]:hover {
    box-shadow: 0 13px 32px rgba(19, 34, 56, .085);
}

div[data-testid="stMetric"] {
    padding: .8rem 1rem;
    border: 1px solid var(--line);
    border-radius: 16px;
    background: rgba(255,255,255,.88);
}
div[data-testid="stMetricLabel"] { color: var(--muted); }
div[data-testid="stMetricValue"] { color: var(--ink); font-family: 'Manrope', sans-serif; }
div[data-testid="stAlert"] { border-radius: 14px; }
hr { border-color: var(--line); margin: 1.5rem 0; }

@media (max-width: 760px) {
    .hero { align-items: flex-start; flex-direction: column; padding: 1.7rem; border-radius: 22px; }
    .hero-aside { width: 100%; }
}
</style>
""", unsafe_allow_html=True)


# --------------------------------------------------
# 2. LOAD PRODUCT CATALOGUE
# --------------------------------------------------

def load_products():
    with open("products.json", "r", encoding="utf-8") as file:
        return json.load(file)


products = load_products()

required_product_fields = {
    "id", "name", "brand", "category", "price", "description"
}

if not isinstance(products, list):
    st.error("The product catalogue must contain a JSON list.")
    st.stop()

for product_number, product in enumerate(products, start=1):

    if not isinstance(product, dict):
        st.error(f"Product #{product_number} must be a JSON object.")
        st.stop()

    missing_fields = required_product_fields - set(product.keys())

    if missing_fields:
        st.error(
            f"Product #{product_number} is missing: "
            f"{', '.join(sorted(missing_fields))}"
        )
        st.stop()

    if (
        isinstance(product["price"], bool)
        or not isinstance(product["price"], (int, float))
        or product["price"] < 0
    ):
        st.error(f"Product #{product_number} has an invalid price.")
        st.stop()


valid_categories = sorted({
    product["category"] for product in products
})

valid_brands = sorted({
    product["brand"] for product in products
})


# --------------------------------------------------
# 3. SESSION STATE INITIALIZATION
# --------------------------------------------------

if "cart" not in st.session_state:
    st.session_state.cart = []

if "pending_paypal_cart_snapshot" not in st.session_state:
    st.session_state.pending_paypal_cart_snapshot = None

if "shopping_results" not in st.session_state:
    st.session_state.shopping_results = None

if "shopping_error" not in st.session_state:
    st.session_state.shopping_error = None

if "pending_paypal_order_id" not in st.session_state:
    st.session_state.pending_paypal_order_id = None

if "pending_paypal_approval_url" not in st.session_state:
    st.session_state.pending_paypal_approval_url = None

if "pending_paypal_capture_request_id" not in st.session_state:
    st.session_state.pending_paypal_capture_request_id = None

if "paypal_payment_success" not in st.session_state:
    st.session_state.paypal_payment_success = None

if "paypal_payment_cancelled" not in st.session_state:
    st.session_state.paypal_payment_cancelled = False

if "channel3_results" not in st.session_state:
    st.session_state.channel3_results = None

if "channel3_error" not in st.session_state:
    st.session_state.channel3_error = None

if "channel3_user_id" not in st.session_state:
    st.session_state.channel3_user_id = str(uuid.uuid4())

# --------------------------------------------------
# 4. HELPER FUNCTIONS
# --------------------------------------------------

def optional_number(value, field_name):

    if value is None:
        return None

    if isinstance(value, bool):
        raise ValueError(
            f"Invalid value received for {field_name}."
        )

    try:
        number = float(value)

    except (TypeError, ValueError):
        raise ValueError(
            f"Invalid value received for {field_name}."
        )

    if not number.is_integer() or number < 0:
        raise ValueError(
            f"Invalid value received for {field_name}."
        )

    return int(number)


def extract_json(response_text):

    if not response_text:
        raise ValueError("Gemini returned an empty response.")

    json_match = re.search(
        r"\{.*\}",
        response_text,
        re.DOTALL
    )

    if not json_match:
        raise ValueError("Gemini did not return valid JSON.")

    return json.loads(json_match.group())


def add_to_cart(product):

    st.session_state.cart.append(product)


def product_icon(product):

    category_icons = {
        "Electronics": "⌘",
        "Fashion": "✦",
        "Home Appliances": "⌂",
        "Accessories": "◈",
        "Furniture": "▱"
    }
    return category_icons.get(product.get("category"), "✧")


def get_channel3_api_key():

    try:
        return st.secrets.get("CHANNEL3_API_KEY") or os.getenv("CHANNEL3_API_KEY")
    except Exception:
        return os.getenv("CHANNEL3_API_KEY")


def search_channel3(query, api_key, user_id):

    response = requests.post(
        "https://api.trychannel3.com/v1/search",
        headers={
            "x-api-key": api_key,
            "x-user-id": user_id,
            "Content-Type": "application/json"
        },
        json={
            "query": query,
            "limit": 6,
            "config": {
                "mode": "agentic"
            }
        },
        timeout=30
    )
    response.raise_for_status()
    payload = response.json()
    if not isinstance(payload, dict):
        raise ValueError("Channel3 returned an unexpected product response.")

    results = payload.get("products")
    if results is None:
        results = payload.get("items")
    if results is None:
        results = payload.get("data", [])
    if isinstance(results, dict):
        results = results.get("products", results.get("items", []))
    if not isinstance(results, list):
        raise ValueError("Channel3 returned an unexpected product response.")
    return results


def best_channel3_offer(product):

    offers = product.get("offers") or []
    valid_offers = []
    for offer in offers:
        price = offer.get("price")
        if not offer.get("url") or not isinstance(price, dict):
            continue
        try:
            numeric_price = float(price.get("price"))
        except (TypeError, ValueError):
            continue
        valid_offers.append((numeric_price, offer))

    return min(valid_offers, key=lambda item: item[0])[1] if valid_offers else None


def format_channel3_price(offer):

    price = offer.get("price", {})
    amount = price.get("price")
    currency = price.get("currency", "")
    if amount is None:
        return "Price unavailable"

    try:
        amount = float(amount)
    except (TypeError, ValueError):
        return "Price unavailable"

    symbol = {"INR": "₹", "USD": "$", "EUR": "€", "GBP": "£"}.get(currency)
    formatted_amount = f"{amount:,.2f}".rstrip("0").rstrip(".")
    return f"{symbol}{formatted_amount}" if symbol else f"{currency} {formatted_amount}".strip()


@st.cache_data(ttl=86400, show_spinner=False)
def get_usd_inr_reference_rate():

    response = requests.get(
        "https://api.frankfurter.dev/v2/rate/USD/INR",
        timeout=10
    )
    response.raise_for_status()
    rate_data = response.json()
    rate = float(rate_data["rate"])
    if rate <= 0:
        raise ValueError("The USD to INR reference rate was invalid.")
    return rate, rate_data.get("date")


# --------------------------------------------------
# PAYPAL SANDBOX HELPER FUNCTIONS
# --------------------------------------------------

def get_paypal_access_token():

    paypal_settings = st.secrets["paypal"]

    response = requests.post(
        f'{paypal_settings["base_url"]}/v1/oauth2/token',
        auth=(
            paypal_settings["client_id"],
            paypal_settings["client_secret"]
        ),
        headers={
            "Accept": "application/json",
            "Accept-Language": "en_US"
        },
        data={"grant_type": "client_credentials"},
        timeout=30
    )

    response.raise_for_status()

    return response.json()["access_token"]


def create_paypal_order():

    paypal_settings = st.secrets["paypal"]
    access_token = get_paypal_access_token()

    response = requests.post(
        f'{paypal_settings["base_url"]}/v2/checkout/orders',
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {access_token}",
            "PayPal-Request-Id": str(uuid.uuid4())
        },
        json={
            "intent": "CAPTURE",
            "purchase_units": [
                {
                    "amount": {
                        "currency_code": "USD",
                        "value": "1.00"
                    },
                    "description": "ShopMate AI hackathon demo payment"
                }
            ],
            "application_context": {
                "brand_name": "ShopMate AI",
                "user_action": "PAY_NOW",
                "return_url": "https://shopmate-ai-sahil.streamlit.app/?paypal=success",
                "cancel_url": "https://shopmate-ai-sahil.streamlit.app/?paypal=cancel"
            }
        },
        timeout=30
    )

    response.raise_for_status()

    order_data = response.json()

    approval_url = None

    for link in order_data.get("links", []):
        if link.get("rel") in ("payer-action", "approve"):
            approval_url = link.get("href")
            break

    if not approval_url:
        raise ValueError("PayPal did not return an approval link.")

    return order_data["id"], approval_url


def capture_paypal_order(order_id, request_id):

    paypal_settings = st.secrets["paypal"]
    access_token = get_paypal_access_token()

    response = requests.post(
        f'{paypal_settings["base_url"]}/v2/checkout/orders/{order_id}/capture',
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {access_token}",
            "PayPal-Request-Id": request_id
        },
        json={},
        timeout=30
    )

    response.raise_for_status()

    return response.json()

def get_paypal_order_details(order_id):

    paypal_settings = st.secrets["paypal"]
    access_token = get_paypal_access_token()

    response = requests.get(
        f'{paypal_settings["base_url"]}/v2/checkout/orders/{order_id}',
        headers={
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        },
        timeout=30
    )

    response.raise_for_status()

    return response.json()


# --------------------------------------------------
# HANDLE PAYPAL RETURN / CANCELLATION
# --------------------------------------------------

# --------------------------------------------------
# HANDLE PAYPAL RETURN / CANCELLATION
# --------------------------------------------------

paypal_result = st.query_params.get("paypal")
returned_order_id = st.query_params.get("token")

if paypal_result == "success" and returned_order_id:

    try:
    # Load the original cart snapshot using the PayPal order ID
        receipt_file = (
            Path("pending_paypal_orders")
            / f"{returned_order_id}.json"
        )

        if not receipt_file.exists():
            raise ValueError(
                "The saved cart receipt was not found for this PayPal order."
            )

        pending_cart_snapshot = json.loads(
            receipt_file.read_text(encoding="utf-8")
        )

                # Retrieve the order details directly from PayPal
        order_data = get_paypal_order_details(returned_order_id)

    # Step 1: Verify the order directly with PayPal.

        # Step 2: Verify the order is for our demo payment.
        purchase_units = order_data.get("purchase_units", [])

        if not purchase_units:
            raise ValueError("PayPal order has no purchase details.")

        purchase_unit = purchase_units[0]
        amount = purchase_unit.get("amount", {})

        if order_data.get("intent") != "CAPTURE":
            raise ValueError("Unexpected PayPal payment intent.")

        if amount.get("currency_code") != "USD" or amount.get("value") != "1.00":
            raise ValueError("PayPal order amount does not match our $1.00 demo payment.")

        if purchase_unit.get("description") != "ShopMate AI hackathon demo payment":
            raise ValueError("This PayPal order does not match ShopMate AI.")

        order_status = order_data.get("status")

        # Step 3: Capture only if PayPal says the buyer approved it.
        if order_status == "APPROVED":

            # Use a consistent request ID for this specific order.
            capture_request_id = str(
                uuid.uuid5(
                    uuid.NAMESPACE_URL,
                    f"shopmate-ai-capture-{returned_order_id}"
                )
            )

            capture_data = capture_paypal_order(
                returned_order_id,
                capture_request_id
            )

        elif order_status == "COMPLETED":

            # Payment was already captured.
            capture_data = order_data

        else:
            raise ValueError(
                f"PayPal order is not approved. Current status: {order_status}"
            )

        # Step 4: Find the completed capture.
        capture_details = {}

        for unit in capture_data.get("purchase_units", []):

            payments = unit.get("payments", {})
            captures = payments.get("captures", [])

            for capture in captures:

                if capture.get("status") == "COMPLETED":
                    capture_details = capture
                    break

            if capture_details:
                break

        # Step 5: Confirm payment.
        if (
            capture_data.get("status") == "COMPLETED"
            and capture_details
            and capture_details.get("status") == "COMPLETED"
        ):

            captured_amount = capture_details.get("amount", {})

            if (
                captured_amount.get("currency_code") != "USD"
                or captured_amount.get("value") != "1.00"
            ):
                raise ValueError("Captured payment amount does not match.")

            st.session_state.paypal_payment_success = {
                "order_id": returned_order_id,
                "capture_id": capture_details.get("id"),
                "amount": captured_amount.get("value"),
                "currency": captured_amount.get("currency_code")
            }

            # Save purchased products for the receipt
            receipt_items = {}

            for product in pending_cart_snapshot:

                product_id = str(product["id"])

                if product_id not in receipt_items:
                    receipt_items[product_id] = {
                        "Product": product["name"],
                        "Brand": product["brand"],
                        "Quantity": 0,
                        "Unit Price (INR)": product["price"],
                        "Subtotal (INR)": 0
                    }

                receipt_items[product_id]["Quantity"] += 1

                receipt_items[product_id]["Subtotal (INR)"] += product["price"]

            # Calculate the original cart total
            receipt_total = sum(
                item["Subtotal (INR)"]
                for item in receipt_items.values()
            )

            st.session_state.paypal_order_receipt = {
                "items": list(receipt_items.values()),
                "total": receipt_total
            }

            receipt_file.unlink(missing_ok=True)


            

            st.session_state.cart = []
            st.session_state.show_checkout = False
            st.session_state.pending_paypal_order_id = None
            st.session_state.pending_paypal_approval_url = None
            st.session_state.pending_paypal_capture_request_id = None
            st.session_state.paypal_payment_cancelled = False

            st.query_params.clear()

        else:
            st.error(
                "PayPal returned, but the payment has not been confirmed as completed."
            )

    except requests.RequestException as error:
        st.error(f"Could not verify or capture the PayPal payment: {error}")

    except (KeyError, ValueError, IndexError) as error:
        st.error(f"Could not confirm the PayPal payment: {error}")

elif paypal_result == "cancel":

    st.session_state.paypal_payment_cancelled = True

    st.session_state.pending_paypal_order_id = None
    st.session_state.pending_paypal_approval_url = None
    st.session_state.pending_paypal_capture_request_id = None

    st.query_params.clear()

# --------------------------------------------------
# 5. HEADER
# --------------------------------------------------

st.markdown("""
<section class="hero">
  <div class="hero-copy">
    <div class="hero-kicker">✦ ShopMate AI · your personal shopping guide</div>
    <h1>Find what fits<br>your life.</h1>
    <p>Tell us what matters. Get a thoughtful shortlist from your budget, preferences, and the products available.</p>
  </div>
  <div class="hero-aside">
    <small>Your shopping, simplified</small>
    <div class="hero-step"><span>1</span> Share what you need</div>
    <div class="hero-step"><span>2</span> Compare good matches</div>
    <div class="hero-step"><span>3</span> Try PayPal Sandbox checkout</div>
  </div>
</section>
""", unsafe_allow_html=True)

metric_columns = st.columns(3)
with metric_columns[0]:
    st.metric("Sample products", len(products))
with metric_columns[1]:
    st.metric("Product categories", len(valid_categories))
with metric_columns[2]:
    st.metric("PayPal demo checkout", "$1 USD · Sandbox")

st.divider()

if st.session_state.paypal_payment_success:

    payment = st.session_state.paypal_payment_success

    st.success("🎉 PayPal Sandbox payment completed successfully!")

    st.write(f'**Paid amount:** ${payment["amount"]} {payment["currency"]}')
    st.write(f'**PayPal Order ID:** `{payment["order_id"]}`')
    st.write(f'**Capture ID:** `{payment["capture_id"]}`')

    st.caption(
        "This is a successful PayPal Sandbox test transaction. "
        "No real money was charged."
    )


        # Display purchase receipt
    receipt = st.session_state.paypal_order_receipt

    if receipt:

        st.divider()

        st.subheader("🧾 Your Purchase Receipt")

        st.table(receipt["items"])

        st.markdown(
            f"### Cart Total: ₹{receipt['total']:,}"
        )

        st.caption(
            "Product prices are illustrative catalogue prices. "
            "The actual PayPal Sandbox payment was $1.00 USD."
        )


# --------------------------------------------------
# 6. AI SHOPPING ASSISTANT
# --------------------------------------------------

st.divider()

st.markdown('<p class="section-kicker">01 · Personalized shopping</p>', unsafe_allow_html=True)
st.header("What are you looking for?")

st.write(
    "Describe the item, budget, brand, or specifications. ShopMate will turn your request into a shortlist you can compare."
)


user_request = st.text_area(
    "What are you looking for?",
    placeholder=(
        "Example: I need a laptop under ₹60,000 for Python "
        "programming with at least 16GB RAM and 512GB SSD."
    ),
    key="user_request"
)


# --------------------------------------------------
# 7. PROCESS CUSTOMER REQUEST
# --------------------------------------------------

if st.button("Ask ShopMate AI", key="ask_shopmate"):

    if not user_request.strip():

        st.session_state.shopping_error = (
            "Please describe what you're looking for."
        )

        st.session_state.shopping_results = None

    else:

        # Clear previous AI results, but preserve the cart.
        st.session_state.shopping_results = None
        st.session_state.shopping_error = None

        client = None

        try:

            api_key = st.secrets["GEMINI_API_KEY"]

            client = genai.Client(api_key=api_key)

            # ------------------------------------------
            # 7A. UNDERSTAND CUSTOMER REQUIREMENTS
            # ------------------------------------------

            prompt = f"""
            You are ShopMate AI.

            Understand the customer's shopping request.

            Return ONLY valid JSON in this format:

            {{
                "category": "Electronics",
                "product_type": "Laptop",
                "brand": "HP",
                "max_budget": 60000,
                "min_ram_gb": 16,
                "min_storage_gb": 512
            }}

            Rules:

            - Category must be one of: {valid_categories}
            - Brand must be one of: {valid_brands}
            - Identify the specific product type.
            - If no brand is specified, use null.
            - If no budget is mentioned, use null.
            - If category cannot be identified, use null.
            - Identify minimum RAM in GB if mentioned.
            - Identify minimum storage in GB if mentioned.
            - Numeric values must be numbers or null.
            - Do not include explanations outside JSON.

            Customer request:

            {user_request}
            """

            with st.spinner("Understanding your requirements..."):

                response = client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=prompt
                )

            requirements = extract_json(response.text)

            # ------------------------------------------
            # 7B. EXTRACT REQUIREMENTS
            # ------------------------------------------

            category = requirements.get("category")

            product_type = requirements.get("product_type")

            brand = requirements.get("brand")

            max_budget = optional_number(
                requirements.get("max_budget"),
                "maximum budget"
            )

            min_ram_gb = optional_number(
                requirements.get("min_ram_gb"),
                "minimum RAM"
            )

            min_storage_gb = optional_number(
                requirements.get("min_storage_gb"),
                "minimum storage"
            )

            # Validate category and brand.

            if category not in valid_categories:
                category = None

            if brand not in valid_brands:
                brand = None

            if product_type is not None:
                product_type = str(product_type).strip() or None

            # ------------------------------------------
            # 7C. FILTER PRODUCT CATALOGUE
            # ------------------------------------------

            matching_products = products.copy()

            if category:

                matching_products = [
                    product for product in matching_products
                    if product["category"] == category
                ]

            else:

                matching_products = []

            # Product type filter.

            if product_type:

                product_type_lower = product_type.lower()

                matching_products = [
                    product for product in matching_products
                    if (
                        product_type_lower in product["name"].lower()
                        or product_type_lower in product["description"].lower()
                    )
                ]

            # Brand filter.

            if brand:

                matching_products = [
                    product for product in matching_products
                    if product["brand"].lower() == brand.lower()
                ]

            # Budget filter.

            if max_budget is not None:

                matching_products = [
                    product for product in matching_products
                    if product["price"] <= max_budget
                ]

            # RAM filter.

            if min_ram_gb is not None:

                matching_products = [
                    product for product in matching_products
                    if product.get("specifications", {}).get(
                        "ram_gb", 0
                    ) >= min_ram_gb
                ]

            # Storage filter.

            if min_storage_gb is not None:

                matching_products = [
                    product for product in matching_products
                    if product.get("specifications", {}).get(
                        "storage_gb", 0
                    ) >= min_storage_gb
                ]

            # ------------------------------------------
            # 7D. PREPARE AI RECOMMENDATION
            # ------------------------------------------

            recommended_product = None

            recommendation_explanation = None

            if matching_products:

                products_for_ai = []

                for product in matching_products:

                    products_for_ai.append({
                        "id": product["id"],
                        "name": product["name"],
                        "brand": product["brand"],
                        "price": product["price"],
                        "description": product["description"],
                        "specifications": product.get(
                            "specifications", {}
                        )
                    })

                recommendation_prompt = f"""
                You are ShopMate AI, an intelligent shopping assistant.

                Customer request:

                {user_request}

                Extracted requirements:

                {json.dumps(requirements, indent=2)}

                Available matching products:

                {json.dumps(products_for_ai, indent=2)}

                Your task:

                1. Compare available products.
                2. Select the most suitable product.
                3. Explain why you selected it.
                4. Mention relevant specifications and price.
                5. Briefly compare other products if appropriate.

                Important rules:

                - Recommend ONLY products from the supplied catalogue.
                - Copy the exact product ID.
                - Never invent specifications or features.
                - Use only the supplied catalogue information.
                - Do not change product prices.
                - Do not claim to have checked live prices or reviews.
                - Keep the explanation clear and concise.
                - Do not mention product IDs in the explanation.
                - Return ONLY valid JSON.

                Return this JSON structure:

                {{
                    "recommended_product_id": "product_id",
                    "explanation": "Your recommendation explanation."
                }}
                """

                # --------------------------------------
                # 7E. GEMINI PRODUCT COMPARISON
                # --------------------------------------

                try:

                    with st.spinner(
                        "Comparing products and preparing your recommendation..."
                    ):

                        recommendation_response = (
                            client.models.generate_content(
                                model="gemini-2.5-flash",
                                contents=recommendation_prompt
                            )
                        )

                    recommendation_data = extract_json(
                        recommendation_response.text
                    )

                    recommended_id = str(
                        recommendation_data.get(
                            "recommended_product_id", ""
                        )
                    )

                    # Validate recommended product ID.

                    recommended_product = next(
                        (
                            product for product in matching_products
                            if str(product["id"]) == recommended_id
                        ),
                        None
                    )

                    recommendation_explanation = (
                        recommendation_data.get("explanation", "")
                    )

                except Exception:

                    # Product matching still works if the
                    # recommendation API request fails.

                    recommended_product = None

                    recommendation_explanation = None

            # ------------------------------------------
            # 7F. SAVE RESULTS IN SESSION STATE
            # ------------------------------------------

            st.session_state.shopping_results = {

                "user_request": user_request,

                "requirements": {
                    "category": category,
                    "product_type": product_type,
                    "brand": brand,
                    "max_budget": max_budget,
                    "min_ram_gb": min_ram_gb,
                    "min_storage_gb": min_storage_gb
                },

                "matching_products": matching_products,

                "recommended_product": recommended_product,

                "recommendation_explanation": recommendation_explanation
            }

        except json.JSONDecodeError:

            st.session_state.shopping_error = (
                "Gemini returned invalid JSON. Please try again."
            )

        except Exception as e:

            st.session_state.shopping_error = (
                f"Something went wrong: {e}"
            )

        finally:

            if client is not None:
                client.close()


# --------------------------------------------------
# 8. DISPLAY AI SHOPPING RESULTS
# --------------------------------------------------

if st.session_state.shopping_error:

    st.error(st.session_state.shopping_error)


if st.session_state.shopping_results:

    results = st.session_state.shopping_results

    requirements = results["requirements"]

    matching_products = results["matching_products"]

    recommended_product = results["recommended_product"]

    recommendation_explanation = (
        results["recommendation_explanation"]
    )

    # ----------------------------------------------
    # 8A. DISPLAY UNDERSTOOD REQUIREMENTS
    # ----------------------------------------------

    st.markdown('<p class="section-kicker">Your brief · understood</p>', unsafe_allow_html=True)
    st.subheader("A shortlist shaped around you")

    requirement_columns = st.columns(3)
    with requirement_columns[0]:
        st.metric(
            "Looking for",
            requirements["product_type"] or requirements["category"] or "A good match"
        )
    with requirement_columns[1]:
        st.metric(
            "Budget",
            f"₹{requirements['max_budget']:,}"
            if requirements["max_budget"] is not None else "Flexible"
        )
    with requirement_columns[2]:
        specs = []
        if requirements["brand"]:
            specs.append(requirements["brand"])
        if requirements["min_ram_gb"] is not None:
            specs.append(f'{requirements["min_ram_gb"]} GB RAM')
        if requirements["min_storage_gb"] is not None:
            specs.append(f'{requirements["min_storage_gb"]} GB storage')
        st.metric("Preferences", " · ".join(specs) if specs else "Open to ideas")

    # ----------------------------------------------
    # 8B. DISPLAY MATCHING PRODUCTS
    # ----------------------------------------------

    st.divider()

    st.subheader("🛍️ Recommended Products")

    if matching_products:

        st.success(
            f"Found {len(matching_products)} matching products!"
        )

        # ------------------------------------------
        # 8C. DISPLAY AI RECOMMENDATION
        # ------------------------------------------

        if recommended_product:

            st.markdown("### 🧠 ShopMate AI's Recommendation")

            if recommendation_explanation:
                st.markdown(recommendation_explanation)

            with st.container(border=True):

                st.markdown(
                    '<div class="sample-product-visual">'
                    f'<span>{product_icon(recommended_product)}</span>'
                    '<small>Recommended match</small></div>',
                    unsafe_allow_html=True
                )

                st.subheader(
                    recommended_product["name"]
                )

                st.caption(
                    f'{recommended_product["brand"]} | '
                    f'{recommended_product["category"]}'
                )

                st.write(
                    recommended_product["description"]
                )

                st.markdown(
                    f"### ₹{recommended_product['price']:,}"
                )

                if st.button(
                    "🛒 Add Recommended Product to Cart",
                    key=f"add_ai_recommendation_{recommended_product['id']}"
                ):

                    add_to_cart(recommended_product)

                    st.success(
                        f'{recommended_product["name"]} added to your cart!'
                    )

        else:

            st.info(
                "AI comparison is unavailable. "
                "You can still choose from the matching products below."
            )

        # ------------------------------------------
        # 8D. DISPLAY OTHER MATCHING PRODUCTS
        # ------------------------------------------

        other_matching_products = [

            product for product in matching_products

            if not (
                recommended_product is not None
                and str(product["id"]) == str(recommended_product["id"])
            )
        ]

        if other_matching_products:

            st.markdown("### Other Matching Products")

            cols = st.columns(3)

            for index, product in enumerate(other_matching_products):

                with cols[index % 3]:

                    with st.container(border=True):

                        st.markdown(
                            '<div class="sample-product-visual">'
                            f'<span>{product_icon(product)}</span>'
                            f'<small>{product["category"]}</small></div>',
                            unsafe_allow_html=True
                        )

                        st.subheader(product["name"])

                        st.caption(
                            f'{product["brand"]} | '
                            f'{product["category"]}'
                        )

                        st.write(product["description"])

                        st.markdown(
                            f"### ₹{product['price']:,}"
                        )

                        if st.button(
                            "Add to Cart",
                            key=f"add_other_{product['id']}"
                        ):

                            add_to_cart(product)

                            st.success(
                                f'{product["name"]} added to your cart!'
                            )

    else:

        st.warning(
            "No matching products found in our catalogue. "
            "Try changing your budget, brand or specifications."
        )


st.divider()
st.markdown('<p class="section-kicker">02 · Live marketplace</p>', unsafe_allow_html=True)
st.header("Explore products across the web")
st.write(
    "Search live product listings, current offers, and retailer links with Channel3."
)
st.caption(
    "Live offers use Channel3's default US/USD market. USD offers show an approximate ₹ equivalent using a daily reference rate; final price, shipping, and taxes may differ."
)

channel3_api_key = get_channel3_api_key()

if not channel3_api_key:
    with st.container(border=True):
        st.markdown("#### Connect Channel3 product search")
        st.write(
            "Add a Channel3 API key as CHANNEL3_API_KEY in Streamlit Secrets to enable live products."
        )
        st.link_button(
            "Get a free Channel3 API key",
            "https://trychannel3.com/developers",
            use_container_width=False
        )
else:
    channel3_columns = st.columns([4, 1])
    with channel3_columns[0]:
        channel3_query = st.text_input(
            "What should we find?",
            value=user_request.strip(),
            placeholder="Try: lightweight laptop for travel",
            key="channel3_query"
        )
    with channel3_columns[1]:
        st.write("")
        st.write("")
        search_live = st.button(
            "Search live",
            type="primary",
            use_container_width=True,
            key="search_channel3"
        )

    if search_live:
        st.session_state.channel3_error = None
        st.session_state.channel3_results = None
        if not channel3_query.strip():
            st.session_state.channel3_error = "Enter a product or shopping need to search."
        else:
            try:
                with st.spinner("Finding live products and retailer offers..."):
                    st.session_state.channel3_results = search_channel3(
                        channel3_query.strip(),
                        channel3_api_key,
                        st.session_state.channel3_user_id
                    )
            except requests.RequestException as error:
                error_response = getattr(error, "response", None)
                status_code = getattr(error_response, "status_code", None)
                suffix = f" (HTTP {status_code})" if status_code else ""
                provider_detail = ""
                if error_response is not None:
                    try:
                        error_payload = error_response.json()
                        if isinstance(error_payload, dict):
                            detail = (
                                error_payload.get("detail")
                                or error_payload.get("message")
                                or error_payload.get("error")
                            )
                            if isinstance(detail, dict):
                                detail = detail.get("message") or detail.get("detail")
                            if detail:
                                provider_detail = f" Details: {str(detail)[:240]}"
                    except (ValueError, requests.exceptions.JSONDecodeError):
                        pass
                st.session_state.channel3_error = (
                    f"Live product search is unavailable right now{suffix}.{provider_detail} "
                    "You can still browse the sample catalogue below."
                )
            except (KeyError, ValueError):
                st.session_state.channel3_error = (
                    "Channel3 returned a response ShopMate could not read. "
                    "You can still browse the sample catalogue below."
                )

    if st.session_state.channel3_error:
        st.warning(st.session_state.channel3_error)

    if st.session_state.channel3_results is not None:
        live_products = st.session_state.channel3_results
        if not live_products:
            st.info("No live matches found. Try a broader search.")
        else:
            st.caption(
                f"{len(live_products)} live matches · Prices and availability can change."
            )
            live_columns = st.columns(3)
            for index, product in enumerate(live_products):
                with live_columns[index % 3]:
                    with st.container(border=True):
                        images = product.get("images") or []
                        if images:
                            image_url = images[0].get("cleaned_url") or images[0].get("url")
                            if image_url:
                                st.image(image_url, use_container_width=True)

                        brands = product.get("brands") or []
                        brand_name = brands[0].get("name") if brands else None
                        if brand_name:
                            st.caption(brand_name)
                        st.subheader(product.get("title", "Product"))

                        offer = best_channel3_offer(product)
                        if offer:
                            offer_currency = str(
                                (offer.get("price") or {}).get("currency", "")
                            ).upper()
                            offer_amount = (offer.get("price") or {}).get("price")
                            if offer_currency == "USD" and offer_amount is not None:
                                try:
                                    usd_inr_rate, rate_date = get_usd_inr_reference_rate()
                                    approx_inr = float(offer_amount) * usd_inr_rate
                                    st.markdown(f"### ≈ ₹{approx_inr:,.0f}")
                                    date_label = f" ({rate_date})" if rate_date else ""
                                    st.caption(
                                        f"Retailer price: {format_channel3_price(offer)} · "
                                        f"estimated at the USD/INR reference rate{date_label}"
                                    )
                                except (requests.RequestException, KeyError, TypeError, ValueError):
                                    st.markdown(f"### {format_channel3_price(offer)}")
                                    st.caption("Rupee estimate unavailable; showing the retailer's listed price.")
                            else:
                                st.markdown(f"### {format_channel3_price(offer)}")
                            st.caption(
                                f'{offer.get("domain", "Retailer")} · '
                                f'{offer.get("availability", "Availability varies")}'
                            )
                            st.link_button(
                                "View retailer offer",
                                offer["url"],
                                use_container_width=True
                            )
                        else:
                            st.caption("Retailer pricing is not available for this result.")

            st.caption(
                "Live products and tracked retailer links are provided by Channel3. "
                "They are separate from the PayPal Sandbox cart."
            )

# --------------------------------------------------
# 9. EXPLORE SAMPLE CATALOGUE
# --------------------------------------------------

st.divider()

st.markdown('<p class="section-kicker">03 · Curated sample catalogue</p>', unsafe_allow_html=True)
st.header("Explore the sample catalogue")

search_query = st.text_input(
    "Search products",
    placeholder="Example: Laptop, headphones, shoes..."
)

categories = ["All Categories"] + valid_categories

selected_category = st.selectbox(
    "Choose a category",
    categories
)

filtered_products = products.copy()

if selected_category != "All Categories":

    filtered_products = [
        product for product in filtered_products
        if product["category"] == selected_category
    ]

if search_query:

    search_text = search_query.lower()

    filtered_products = [
        product for product in filtered_products
        if (
            search_text in product["name"].lower()
            or search_text in product["brand"].lower()
            or search_text in product["description"].lower()
        )
    ]


st.divider()

st.subheader(
    f"Available Products ({len(filtered_products)})"
)

if filtered_products:

    cols = st.columns(3)

    for index, product in enumerate(filtered_products):

        with cols[index % 3]:

            with st.container(border=True):

                st.markdown(
                    '<div class="sample-product-visual">'
                    f'<span>{product_icon(product)}</span>'
                    f'<small>{product["category"]}</small></div>',
                    unsafe_allow_html=True
                )

                st.subheader(product["name"])

                st.caption(
                    f'{product["brand"]} | '
                    f'{product["category"]}'
                )

                st.write(product["description"])

                st.markdown(
                    f"### ₹{product['price']:,}"
                )

                if st.button(
                    "Add to Cart",
                    key=f"add_to_cart_{product['id']}"
                ):

                    add_to_cart(product)

                    st.success(
                        f'{product["name"]} added to your cart!'
                    )

else:

    st.warning(
        "No products found. Try another search."
    )


# --------------------------------------------------
# 10. SHOPPING CART
# --------------------------------------------------

# --------------------------------------------------
# 6. SHOPPING CART AND CHECKOUT SUMMARY
# --------------------------------------------------

st.divider()
st.header("🛒 My Shopping Cart")

if st.session_state.cart:

    # Group identical products together
    cart_summary = {}

    for product in st.session_state.cart:

        product_id = str(product["id"])

        if product_id not in cart_summary:
            cart_summary[product_id] = {
                "product": product,
                "quantity": 0
            }

        cart_summary[product_id]["quantity"] += 1

    total_amount = 0

    st.subheader("Your Order")

    for product_id, item in cart_summary.items():

        product = item["product"]
        quantity = item["quantity"]

        unit_price = product["price"]
        subtotal = unit_price * quantity

        total_amount += subtotal

        with st.container(border=True):

            col1, col2, col3 = st.columns([3, 1, 2])

            with col1:
                st.write(f"**{product['name']}**")
                st.caption(product["brand"])

            with col2:
                st.write(f"Quantity: {quantity}")

            with col3:
                st.write(f"Unit price: ₹{unit_price:,}")
                st.write(f"**Subtotal: ₹{subtotal:,}**")

            if st.button(
                "Remove one",
                key=f"remove_one_{product_id}"
            ):

                for index, cart_product in enumerate(
                    st.session_state.cart
                ):

                    if str(cart_product["id"]) == product_id:
                        st.session_state.cart.pop(index)
                        break

                st.rerun()

    # Final bill
    st.divider()

    st.subheader("💰 Order Summary")

    st.write(f"Total items: {len(st.session_state.cart)}")

    st.markdown(
        f"## Grand Total: ₹{total_amount:,}"
    )

    st.caption("Prices are based on our demo product catalogue.")

    st.divider()

    if st.button(
        "Proceed to Checkout",
        type="primary",
        use_container_width=True
    ):
        st.session_state.show_checkout = True

    if st.session_state.get("show_checkout", False):

        st.success("Your checkout summary is ready!")

        st.warning(
            "Hackathon demo mode: PayPal will charge a fixed $1.00 USD, "
            "regardless of your cart total in INR. This is a Sandbox test payment."
        )

        st.write("**Demo payment amount: $1.00 USD**")

        if st.session_state.pending_paypal_approval_url:
            st.info(
                "A PayPal order is already waiting for approval. "
                "Use the button below to continue."
            )

            st.link_button(
                "Continue to PayPal",
                st.session_state.pending_paypal_approval_url,
                type="primary",
                use_container_width=True
            )

        elif st.button(
            "Pay $1.00 with PayPal Sandbox",
            type="primary",
            use_container_width=True
        ):

            try:
                order_id, approval_url = create_paypal_order()


                # Save cart snapshot in a local file
                pending_folder = Path("pending_paypal_orders")
                pending_folder.mkdir(exist_ok=True)

                cart_snapshot = [
                    {
                        "id": product["id"],
                        "name": product["name"],
                        "brand": product["brand"],
                        "price": product["price"]
                    }
                    for product in st.session_state.cart
                ]

                receipt_file = pending_folder / f"{order_id}.json"

                receipt_file.write_text(
                    json.dumps(cart_snapshot, indent=4),
                    encoding="utf-8"
                )

                st.session_state.pending_paypal_cart_snapshot = cart_snapshot

                st.session_state.pending_paypal_order_id = order_id
                st.session_state.pending_paypal_approval_url = approval_url
                st.session_state.pending_paypal_capture_request_id = str(uuid.uuid4())

                st.rerun()

            except requests.RequestException as error:
                st.error(
                    f"PayPal could not create the order. "
                    f"Please check your Sandbox configuration. Details: {error}"
                )

            except (KeyError, ValueError) as error:
                st.error(f"PayPal setup issue: {error}")

    if st.session_state.paypal_payment_cancelled:
        st.warning(
            "PayPal checkout was cancelled. Your cart is still saved."
        )
        st.session_state.paypal_payment_cancelled = False

else:

    st.session_state.show_checkout = False

    st.info(
        "Your shopping cart is empty. Add some products to get started!"
    )


# --------------------------------------------------
# 11. FOOTER
# --------------------------------------------------

st.divider()

st.caption(
    "ShopMate AI | Intelligent Shopping, Simplified"
)

st.caption(
    "Note: Product listings and prices are illustrative demo data."
)
