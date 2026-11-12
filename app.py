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

.stApp { background: var(--canvas); color: var(--ink); font-family: 'DM Sans', sans-serif; }
.block-container { max-width: 1380px; padding-top: 1rem; padding-bottom: 3rem; }

h1,h2,h3,h4,h5,h6,
.stMarkdown h1,.stMarkdown h2,.stMarkdown h3 {
    color: var(--ink) !important; font-family: 'Manrope', sans-serif !important; letter-spacing: -.035em;
}
p, label, .stMarkdown { color: #334155; }
.stCaption, [data-testid="stCaptionContainer"] { color: var(--muted) !important; }

/* ── Compact banner ── */
.store-banner {
    display: flex; align-items: center; justify-content: space-between; gap: 1.5rem;
    padding: 1.4rem 2rem; margin-bottom: 1.2rem;
    border-radius: 18px; color: white;
    background: linear-gradient(118deg, #10243a 0%, #173a50 56%, #086c68 100%);
    box-shadow: 0 10px 30px rgba(16,36,58,.14);
}
.store-banner h1 { margin: 0; color: white !important; font-size: 1.8rem; line-height: 1.1; }
.store-banner p { margin: .3rem 0 0; color: rgba(240,249,255,.78); font-size: .92rem; }
.store-banner-badge {
    padding: .45rem .9rem; border-radius: 999px; font-size: .7rem; font-weight: 800;
    letter-spacing: .1em; text-transform: uppercase; white-space: nowrap;
    color: #0d4a4a; background: #b9f4e0;
}

/* ── Sponsors grid ── */
.sponsors-row { display: flex; gap: .75rem; margin: 0 0 1.2rem; flex-wrap: wrap; }
.sponsor-card {
    flex: 1 1 0; min-width: 140px; padding: .9rem 1rem; text-align: center;
    border: 1px solid var(--line); border-radius: 14px; background: var(--paper);
    box-shadow: 0 2px 8px rgba(19,34,56,.04);
}
.sponsor-card .sp-icon { font-size: 1.6rem; line-height: 1; margin-bottom: .35rem; }
.sponsor-card .sp-name { font-weight: 800; font-size: .82rem; color: var(--ink); }
.sponsor-card .sp-role { font-size: .7rem; color: var(--muted); margin-top: .15rem; }

/* ── Product cards ── */
.prod-tag {
    display: inline-block; padding: .2rem .55rem; border-radius: 999px; font-size: .65rem;
    font-weight: 700; letter-spacing: .06em; text-transform: uppercase;
    color: #087c70; background: #e0f5ed; border: 1px solid rgba(14,159,138,.12);
}

/* ── Buttons ── */
.stButton > button, .stLinkButton > a {
    min-height: 2.6rem; border: 1px solid transparent; border-radius: 10px;
    color: white; background: var(--teal); font-weight: 700;
    transition: transform .14s ease, background .14s ease, box-shadow .14s ease;
    box-shadow: 0 4px 12px rgba(14,159,138,.14);
}
.stButton > button:hover, .stLinkButton > a:hover {
    border-color: transparent; color: white; background: var(--teal-dark);
    transform: translateY(-1px); box-shadow: 0 6px 16px rgba(14,159,138,.2);
}

/* ── Inputs ── */
.stTextInput input, .stTextArea textarea, .stSelectbox [data-baseweb="select"] > div {
    border-radius: 10px; border-color: #dbe5ec; background-color: white;
}
.stTextInput input:focus, .stTextArea textarea:focus {
    border-color: #35b8a1; box-shadow: 0 0 0 3px rgba(53,184,161,.12);
}

/* ── Cards ── */
div[data-testid="stVerticalBlockBorderWrapper"] {
    padding: .9rem; border: 1px solid var(--line); border-radius: 16px;
    background: var(--paper); box-shadow: 0 4px 16px rgba(19,34,56,.04);
    transition: box-shadow .14s ease;
}
div[data-testid="stVerticalBlockBorderWrapper"]:hover {
    box-shadow: 0 8px 24px rgba(19,34,56,.08);
}

div[data-testid="stMetric"] { padding: .7rem .9rem; border: 1px solid var(--line); border-radius: 12px; background: rgba(255,255,255,.88); }
div[data-testid="stMetricLabel"] { color: var(--muted); }
div[data-testid="stMetricValue"] { color: var(--ink); font-family: 'Manrope', sans-serif; }
div[data-testid="stAlert"] { border-radius: 12px; }
hr { border-color: var(--line); margin: 1.2rem 0; }

/* ── Sidebar ── */
section[data-testid="stSidebar"] { background: var(--paper); border-right: 1px solid var(--line); }
section[data-testid="stSidebar"] .block-container { padding-top: .5rem; }

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"] { gap: .5rem; }
.stTabs [data-baseweb="tab"] {
    border-radius: 10px 10px 0 0; font-weight: 600; font-size: .88rem;
}

@media (max-width: 760px) {
    .store-banner { flex-direction: column; padding: 1.2rem; border-radius: 14px; }
    .sponsors-row { flex-direction: column; }
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

cart_summary = {}
for _p in st.session_state.cart:
    _pid = str(_p["id"])
    if _pid not in cart_summary:
        cart_summary[_pid] = {"product": _p, "quantity": 0}
    cart_summary[_pid]["quantity"] += 1

total_amount_inr = sum(
    e["product"]["price"] * e["quantity"] for e in cart_summary.values()
)

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


def _app_base_url():
    try:
        host = st.context.headers.get("Host", "localhost:8501")
    except AttributeError:
        host = "localhost:8501"
    protocol = "https" if not host.startswith("localhost") else "http"
    return f"{protocol}://{host}"


def create_paypal_order(cart_summary, usd_inr_rate):

    paypal_settings = st.secrets["paypal"]
    access_token = get_paypal_access_token()
    base = _app_base_url()

    paypal_items = []
    item_total = 0.0

    for product_id, entry in cart_summary.items():
        product = entry["product"]
        quantity = entry["quantity"]
        unit_usd = round(product["price"] / usd_inr_rate, 2)
        item_total += round(unit_usd * quantity, 2)

        paypal_items.append({
            "name": product["name"][:127],
            "quantity": str(quantity),
            "unit_amount": {
                "currency_code": "USD",
                "value": f"{unit_usd:.2f}"
            },
            "category": "PHYSICAL_GOODS"
        })

    item_total_str = f"{round(item_total, 2):.2f}"

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
                        "value": item_total_str,
                        "breakdown": {
                            "item_total": {
                                "currency_code": "USD",
                                "value": item_total_str
                            }
                        }
                    },
                    "description": "ShopMate AI purchase",
                    "items": paypal_items
                }
            ],
            "application_context": {
                "brand_name": "ShopMate AI",
                "user_action": "PAY_NOW",
                "return_url": f"{base}/?paypal=success",
                "cancel_url": f"{base}/?paypal=cancel"
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

    return order_data["id"], approval_url, item_total_str


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

paypal_result = st.query_params.get("paypal")
returned_order_id = st.query_params.get("token")

if paypal_result == "success" and returned_order_id:

    try:
        if not re.fullmatch(r"[A-Za-z0-9]+", returned_order_id):
            raise ValueError("Invalid PayPal order ID format.")

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

        expected_usd = pending_cart_snapshot["expected_usd_total"]
        snapshot_items = pending_cart_snapshot["items"]

        order_data = get_paypal_order_details(returned_order_id)

        purchase_units = order_data.get("purchase_units", [])

        if not purchase_units:
            raise ValueError("PayPal order has no purchase details.")

        purchase_unit = purchase_units[0]
        amount = purchase_unit.get("amount", {})

        if order_data.get("intent") != "CAPTURE":
            raise ValueError("Unexpected PayPal payment intent.")

        if amount.get("currency_code") != "USD" or amount.get("value") != expected_usd:
            raise ValueError("PayPal order amount does not match the expected total.")

        if purchase_unit.get("description") != "ShopMate AI purchase":
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
                or captured_amount.get("value") != expected_usd
            ):
                raise ValueError("Captured payment amount does not match.")

            st.session_state.paypal_payment_success = {
                "order_id": returned_order_id,
                "capture_id": capture_details.get("id"),
                "amount": captured_amount.get("value"),
                "currency": captured_amount.get("currency_code")
            }

            receipt_items = {}

            for product in snapshot_items:

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
                "total_inr": receipt_total,
                "total_usd": captured_amount.get("value"),
                "usd_inr_rate": pending_cart_snapshot.get("usd_inr_rate"),
                "rate_date": pending_cart_snapshot.get("rate_date")
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

# ==================================================
# SIDEBAR — SHOPPING CART
# ==================================================

with st.sidebar:
    st.markdown(
        '<div style="text-align:center;padding:.2rem 0 .6rem">'
        '<h2 style="margin:0;font-family:Manrope,sans-serif;letter-spacing:-.03em">🛍️ ShopMate AI</h2>'
        '<p style="margin:.2rem 0 0;color:#65758b;font-size:.78rem">Intelligent Shopping, Simplified</p>'
        '</div>', unsafe_allow_html=True
    )
    st.divider()

    if st.session_state.paypal_payment_success:
        payment = st.session_state.paypal_payment_success
        st.success("Payment completed!")
        st.write(f'**${payment["amount"]} {payment["currency"]}**')
        st.caption(f'Order `{payment["order_id"][:16]}…`')

        receipt = st.session_state.get("paypal_order_receipt")
        if receipt:
            st.markdown(f'**Cart:** ₹{receipt["total_inr"]:,}')
            rate_info = ""
            if receipt.get("usd_inr_rate"):
                rate_info = f' @ {receipt["usd_inr_rate"]:.2f}'
            st.markdown(f'**Paid:** ${receipt["total_usd"]} USD{rate_info}')
            st.caption("Sandbox — no real money charged.")

            with st.expander("Receipt details"):
                st.table(receipt["items"])

        st.divider()

    st.markdown("### 🛒 Cart")

    if st.session_state.cart:
        cart_table = []
        for _pid, _entry in cart_summary.items():
            _prod = _entry["product"]
            _qty = _entry["quantity"]
            cart_table.append({
                "Product": _prod["name"][:28],
                "Qty": _qty,
                "Subtotal": f"₹{_prod['price'] * _qty:,}"
            })

        st.table(cart_table)
        st.markdown(f"### ₹{total_amount_inr:,}")
        st.caption(f"{len(st.session_state.cart)} items")

        with st.expander("Remove items"):
            for _pid in list(cart_summary.keys()):
                _pname = cart_summary[_pid]["product"]["name"]
                if st.button(f"✕ {_pname[:30]}", key=f"sb_rm_{_pid}"):
                    for _i, _cp in enumerate(st.session_state.cart):
                        if str(_cp["id"]) == _pid:
                            st.session_state.cart.pop(_i)
                            break
                    st.rerun()

        st.divider()

        if st.button("Proceed to Checkout", type="primary", use_container_width=True, key="sb_checkout"):
            st.session_state.show_checkout = True

        if st.session_state.get("show_checkout", False):

            if st.session_state.pending_paypal_approval_url:
                st.link_button(
                    "Continue to PayPal",
                    st.session_state.pending_paypal_approval_url,
                    type="primary", use_container_width=True
                )
            else:
                checkout_rate = None
                total_usd_preview = 0.0
                rate_date = None

                try:
                    checkout_rate, rate_date = get_usd_inr_reference_rate()
                    total_usd_preview = sum(
                        round(e["product"]["price"] / checkout_rate, 2) * e["quantity"]
                        for e in cart_summary.values()
                    )
                    total_usd_preview = round(total_usd_preview, 2)
                    date_lbl = f" ({rate_date})" if rate_date else ""
                    st.info(f"₹{total_amount_inr:,} ≈ **${total_usd_preview:.2f}**{date_lbl}")
                    st.caption("Sandbox test — no real money charged.")
                except (requests.RequestException, KeyError, TypeError, ValueError):
                    st.error("Exchange rate unavailable.")

                if checkout_rate is not None and st.button(
                    f"Pay ${total_usd_preview:.2f} via PayPal",
                    type="primary", use_container_width=True, key="sb_pay"
                ):
                    try:
                        order_id, approval_url, expected_usd = create_paypal_order(
                            cart_summary, checkout_rate
                        )
                        pending_folder = Path("pending_paypal_orders")
                        pending_folder.mkdir(exist_ok=True)
                        cart_snapshot = {
                            "expected_usd_total": expected_usd,
                            "usd_inr_rate": checkout_rate,
                            "rate_date": rate_date,
                            "items": [
                                {"id": p["id"], "name": p["name"], "brand": p["brand"], "price": p["price"]}
                                for p in st.session_state.cart
                            ]
                        }
                        (pending_folder / f"{order_id}.json").write_text(
                            json.dumps(cart_snapshot, indent=4), encoding="utf-8"
                        )
                        st.session_state.pending_paypal_cart_snapshot = cart_snapshot
                        st.session_state.pending_paypal_order_id = order_id
                        st.session_state.pending_paypal_approval_url = approval_url
                        st.session_state.pending_paypal_capture_request_id = str(uuid.uuid4())
                        st.rerun()
                    except requests.RequestException as error:
                        st.error(f"PayPal order failed: {error}")
                    except (KeyError, ValueError) as error:
                        st.error(f"PayPal setup issue: {error}")

        if st.session_state.paypal_payment_cancelled:
            st.warning("Checkout cancelled. Cart saved.")
            st.session_state.paypal_payment_cancelled = False

    else:
        st.session_state.show_checkout = False
        st.caption("Your cart is empty. Browse products and add items!")

    st.divider()
    st.caption("🔐 Secured by PayPal Sandbox")


# ==================================================
# MAIN — BANNER
# ==================================================

st.markdown(
    '<div class="store-banner">'
    '<div>'
    '<h1>ShopMate AI</h1>'
    '<p>Describe what you need. Get AI recommendations, compare live prices, and check out with PayPal.</p>'
    '</div>'
    '<span class="store-banner-badge">✦ AI-Powered</span>'
    '</div>',
    unsafe_allow_html=True
)


# ==================================================
# MAIN — SPONSORS / INTEGRATIONS GRID
# ==================================================

st.markdown(
    '<div class="sponsors-row">'
    '<div class="sponsor-card"><div class="sp-icon">💳</div><div class="sp-name">PayPal</div><div class="sp-role">Itemized Checkout</div></div>'
    '<div class="sponsor-card"><div class="sp-icon">🧠</div><div class="sp-name">Google Gemini</div><div class="sp-role">AI Recommendations</div></div>'
    '<div class="sponsor-card"><div class="sp-icon">🔍</div><div class="sp-name">Channel3</div><div class="sp-role">Live Product Search</div></div>'
    '<div class="sponsor-card"><div class="sp-icon">💱</div><div class="sp-name">Frankfurter</div><div class="sp-role">Exchange Rates</div></div>'
    '</div>',
    unsafe_allow_html=True
)


# ==================================================
# MAIN — AI SEARCH BAR
# ==================================================

search_cols = st.columns([5, 1])
with search_cols[0]:
    user_request = st.text_input(
        "What are you looking for?",
        placeholder="I need a laptop under ₹60,000 with 16GB RAM for programming…",
        key="user_request"
    )
with search_cols[1]:
    st.write("")
    ask_pressed = st.button("Ask ShopMate AI", type="primary", use_container_width=True, key="ask_shopmate")

if ask_pressed:
    if not user_request.strip():
        st.session_state.shopping_error = "Please describe what you're looking for."
        st.session_state.shopping_results = None
    else:
        st.session_state.shopping_results = None
        st.session_state.shopping_error = None
        client = None
        try:
            api_key = st.secrets["GEMINI_API_KEY"]
            client = genai.Client(api_key=api_key)

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
                response = client.models.generate_content(model="gemini-2.5-flash", contents=prompt)
            requirements = extract_json(response.text)

            category = requirements.get("category")
            product_type = requirements.get("product_type")
            brand = requirements.get("brand")
            max_budget = optional_number(requirements.get("max_budget"), "maximum budget")
            min_ram_gb = optional_number(requirements.get("min_ram_gb"), "minimum RAM")
            min_storage_gb = optional_number(requirements.get("min_storage_gb"), "minimum storage")

            if category not in valid_categories:
                category = None
            if brand not in valid_brands:
                brand = None
            if product_type is not None:
                product_type = str(product_type).strip() or None

            matching_products = products.copy()
            if category:
                matching_products = [p for p in matching_products if p["category"] == category]
            else:
                matching_products = []
            if product_type:
                pt = product_type.lower()
                matching_products = [p for p in matching_products if pt in p["name"].lower() or pt in p["description"].lower()]
            if brand:
                matching_products = [p for p in matching_products if p["brand"].lower() == brand.lower()]
            if max_budget is not None:
                matching_products = [p for p in matching_products if p["price"] <= max_budget]
            if min_ram_gb is not None:
                matching_products = [p for p in matching_products if p.get("specifications", {}).get("ram_gb", 0) >= min_ram_gb]
            if min_storage_gb is not None:
                matching_products = [p for p in matching_products if p.get("specifications", {}).get("storage_gb", 0) >= min_storage_gb]

            recommended_product = None
            recommendation_explanation = None

            if matching_products:
                products_for_ai = [
                    {"id": p["id"], "name": p["name"], "brand": p["brand"], "price": p["price"],
                     "description": p["description"], "specifications": p.get("specifications", {})}
                    for p in matching_products
                ]
                recommendation_prompt = f"""
                You are ShopMate AI, an intelligent shopping assistant.
                Customer request: {user_request}
                Extracted requirements: {json.dumps(requirements, indent=2)}
                Available matching products: {json.dumps(products_for_ai, indent=2)}
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
                - Keep the explanation clear and concise.
                - Do not mention product IDs in the explanation.
                - Return ONLY valid JSON.
                Return this JSON structure:
                {{
                    "recommended_product_id": "product_id",
                    "explanation": "Your recommendation explanation."
                }}
                """
                try:
                    with st.spinner("Comparing products…"):
                        rec_response = client.models.generate_content(model="gemini-2.5-flash", contents=recommendation_prompt)
                    rec_data = extract_json(rec_response.text)
                    rec_id = str(rec_data.get("recommended_product_id", ""))
                    recommended_product = next((p for p in matching_products if str(p["id"]) == rec_id), None)
                    recommendation_explanation = rec_data.get("explanation", "")
                except Exception:
                    recommended_product = None
                    recommendation_explanation = None

            st.session_state.shopping_results = {
                "user_request": user_request,
                "requirements": {
                    "category": category, "product_type": product_type, "brand": brand,
                    "max_budget": max_budget, "min_ram_gb": min_ram_gb, "min_storage_gb": min_storage_gb
                },
                "matching_products": matching_products,
                "recommended_product": recommended_product,
                "recommendation_explanation": recommendation_explanation
            }
        except json.JSONDecodeError:
            st.session_state.shopping_error = "Gemini returned invalid JSON. Please try again."
        except Exception as e:
            st.session_state.shopping_error = f"Something went wrong: {e}"
        finally:
            if client is not None:
                client.close()


# ==================================================
# MAIN — TABBED SHOPPING EXPERIENCE
# ==================================================

if st.session_state.shopping_error:
    st.error(st.session_state.shopping_error)

tab_browse, tab_ai, tab_live = st.tabs(["🛍️ All Products", "🧠 AI Picks", "🌐 Live Deals"])


# ── TAB 1: AI PICKS ──

with tab_ai:
    if st.session_state.shopping_results:
        results = st.session_state.shopping_results
        req = results["requirements"]
        ai_products = results["matching_products"]
        rec_product = results["recommended_product"]
        rec_explanation = results["recommendation_explanation"]

        req_cols = st.columns(3)
        with req_cols[0]:
            st.metric("Looking for", req["product_type"] or req["category"] or "A good match")
        with req_cols[1]:
            st.metric("Budget", f'₹{req["max_budget"]:,}' if req["max_budget"] is not None else "Flexible")
        with req_cols[2]:
            specs = []
            if req["brand"]:
                specs.append(req["brand"])
            if req["min_ram_gb"] is not None:
                specs.append(f'{req["min_ram_gb"]} GB RAM')
            if req["min_storage_gb"] is not None:
                specs.append(f'{req["min_storage_gb"]} GB storage')
            st.metric("Preferences", " · ".join(specs) if specs else "Open to ideas")

        st.divider()

        if ai_products:
            st.success(f"Found {len(ai_products)} matching products!")

            if rec_product:
                st.markdown("#### 🧠 Top Recommendation")
                if rec_explanation:
                    st.markdown(rec_explanation)

                with st.container(border=True):
                    rc1, rc2 = st.columns([3, 1])
                    with rc1:
                        st.markdown(f'<span class="prod-tag">{rec_product["category"]}</span>', unsafe_allow_html=True)
                        st.subheader(rec_product["name"])
                        st.caption(rec_product["brand"])
                        st.write(rec_product["description"])
                    with rc2:
                        st.markdown(f"### ₹{rec_product['price']:,}")
                        if st.button("Add to Cart", key=f"ai_rec_{rec_product['id']}"):
                            add_to_cart(rec_product)
                            st.rerun()

            other_ai = [p for p in ai_products if not (rec_product and str(p["id"]) == str(rec_product["id"]))]
            if other_ai:
                st.markdown("#### Other Matches")
                cols = st.columns(3)
                for idx, product in enumerate(other_ai):
                    with cols[idx % 3]:
                        with st.container(border=True):
                            st.markdown(f'<span class="prod-tag">{product["category"]}</span>', unsafe_allow_html=True)
                            st.subheader(product["name"])
                            st.caption(product["brand"])
                            st.write(product["description"])
                            st.markdown(f"### ₹{product['price']:,}")
                            if st.button("Add to Cart", key=f"ai_other_{product['id']}"):
                                add_to_cart(product)
                                st.rerun()
        else:
            st.warning("No matching products. Try different requirements.")
    else:
        st.info("Use the search bar above to get AI-powered product recommendations.")


# ── TAB 2: ALL PRODUCTS ──

with tab_browse:
    filter_cols = st.columns([3, 2])
    with filter_cols[0]:
        search_query = st.text_input("Search products", placeholder="Laptop, headphones, shoes…", key="browse_search")
    with filter_cols[1]:
        selected_category = st.selectbox("Category", ["All Categories"] + valid_categories, key="browse_cat")

    filtered_products = products.copy()
    if selected_category != "All Categories":
        filtered_products = [p for p in filtered_products if p["category"] == selected_category]
    if search_query:
        q = search_query.lower()
        filtered_products = [p for p in filtered_products if q in p["name"].lower() or q in p["brand"].lower() or q in p["description"].lower()]

    st.caption(f"{len(filtered_products)} products")

    if filtered_products:
        cols = st.columns(3)
        for idx, product in enumerate(filtered_products):
            with cols[idx % 3]:
                with st.container(border=True):
                    st.markdown(f'<span class="prod-tag">{product["category"]}</span>', unsafe_allow_html=True)
                    st.subheader(product["name"])
                    st.caption(product["brand"])
                    st.write(product["description"])
                    st.markdown(f"### ₹{product['price']:,}")
                    if st.button("Add to Cart", key=f"browse_{product['id']}"):
                        add_to_cart(product)
                        st.rerun()
    else:
        st.warning("No products found. Try another search.")


# ── TAB 3: LIVE DEALS ──

with tab_live:
    st.caption(
        "Live offers via Channel3's US/USD market. "
        "USD prices show an approximate ₹ equivalent using a daily reference rate."
    )

    channel3_api_key = get_channel3_api_key()

    if not channel3_api_key:
        with st.container(border=True):
            st.markdown("#### Connect Channel3")
            st.write("Add a Channel3 API key as CHANNEL3_API_KEY in Streamlit Secrets.")
            st.link_button("Get a free Channel3 API key", "https://trychannel3.com/developers")
    else:
        ch3_cols = st.columns([4, 1])
        with ch3_cols[0]:
            channel3_query = st.text_input(
                "Search live products",
                value=user_request.strip() if user_request else "",
                placeholder="lightweight laptop for travel",
                key="channel3_query"
            )
        with ch3_cols[1]:
            st.write("")
            search_live = st.button("Search", type="primary", use_container_width=True, key="ch3_search")

        if search_live:
            st.session_state.channel3_error = None
            st.session_state.channel3_results = None
            if not channel3_query.strip():
                st.session_state.channel3_error = "Enter a product to search."
            else:
                try:
                    with st.spinner("Finding live products…"):
                        st.session_state.channel3_results = search_channel3(
                            channel3_query.strip(), channel3_api_key, st.session_state.channel3_user_id
                        )
                except requests.RequestException as error:
                    err_resp = getattr(error, "response", None)
                    status = getattr(err_resp, "status_code", None)
                    suffix = f" (HTTP {status})" if status else ""
                    detail = ""
                    if err_resp is not None:
                        try:
                            ep = err_resp.json()
                            if isinstance(ep, dict):
                                d = ep.get("detail") or ep.get("message") or ep.get("error")
                                if isinstance(d, dict):
                                    d = d.get("message") or d.get("detail")
                                if d:
                                    detail = f" {str(d)[:240]}"
                        except (ValueError, requests.exceptions.JSONDecodeError):
                            pass
                    st.session_state.channel3_error = f"Live search unavailable{suffix}.{detail}"
                except (KeyError, ValueError):
                    st.session_state.channel3_error = "Unexpected Channel3 response."

        if st.session_state.channel3_error:
            st.warning(st.session_state.channel3_error)

        if st.session_state.channel3_results is not None:
            live_products = st.session_state.channel3_results
            if not live_products:
                st.info("No live matches. Try a broader search.")
            else:
                st.caption(f"{len(live_products)} live matches · Prices may change.")
                live_cols = st.columns(3)
                for idx, lp in enumerate(live_products):
                    with live_cols[idx % 3]:
                        with st.container(border=True):
                            images = lp.get("images") or []
                            if images:
                                img_url = images[0].get("cleaned_url") or images[0].get("url")
                                if img_url:
                                    st.image(img_url, use_container_width=True)
                            brands = lp.get("brands") or []
                            brand_name = brands[0].get("name") if brands else None
                            if brand_name:
                                st.caption(brand_name)
                            st.subheader(lp.get("title", "Product"))

                            offer = best_channel3_offer(lp)
                            if offer:
                                o_cur = str((offer.get("price") or {}).get("currency", "")).upper()
                                o_amt = (offer.get("price") or {}).get("price")
                                if o_cur == "USD" and o_amt is not None:
                                    try:
                                        usd_inr_rate, rd = get_usd_inr_reference_rate()
                                        approx = float(o_amt) * usd_inr_rate
                                        st.markdown(f"### ≈ ₹{approx:,.0f}")
                                        dl = f" ({rd})" if rd else ""
                                        st.caption(f"Retailer: {format_channel3_price(offer)} · rate{dl}")
                                    except (requests.RequestException, KeyError, TypeError, ValueError):
                                        st.markdown(f"### {format_channel3_price(offer)}")
                                else:
                                    st.markdown(f"### {format_channel3_price(offer)}")
                                st.caption(f'{offer.get("domain", "Retailer")} · {offer.get("availability", "Check site")}')
                                st.link_button("View offer", offer["url"], use_container_width=True)
                            else:
                                st.caption("Pricing unavailable.")


# ==================================================
# FOOTER
# ==================================================

st.divider()
st.caption("ShopMate AI — Intelligent Shopping, Simplified · Product listings are illustrative demo data.")
