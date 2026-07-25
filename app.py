import os, sqlite3, requests
from flask import Flask, request, jsonify, redirect
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

DB_NAME = "secure_delivery.db"
SHOPIFY_API_KEY = os.getenv("SHOPIFY_API_KEY")
SHOPIFY_API_SECRET = os.getenv("SHOPIFY_API_SECRET")
APP_URL = "https://Ahmdnoaman.pythonanywhere.com"

def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def home():
    return "<h1>Aman El-Mandoob Server is Running</h1>"

@app.route('/auth')
def auth():
    shop = request.args.get('shop')
    if not shop: return jsonify({"error": "Missing shop"}), 400
    redirect_uri = f"{APP_URL}/auth/callback"
    return redirect(f"https://{shop}/admin/oauth/authorize?client_id={SHOPIFY_API_KEY}&scope=write_orders,read_orders&redirect_uri={redirect_uri}")

@app.route('/auth/callback')
def auth_callback():
    shop, code = request.args.get('shop'), request.args.get('code')
    res = requests.post(f"https://{shop}/admin/oauth/access_token", json={
        "client_id": SHOPIFY_API_KEY, "client_secret": SHOPIFY_API_SECRET, "code": code
    }).json()
    token = res.get('access_token')
    if token:
        conn = get_db_connection()
        conn.execute('INSERT OR REPLACE INTO stores (shop_url, access_token) VALUES (?, ?)', (shop, token))
        conn.commit(); conn.close()
        return redirect(f"/billing/subscribe?shop={shop}")
    return jsonify({"error": "Failed token exchange"}), 400

@app.route('/billing/subscribe')
def subscribe():
    shop = request.args.get('shop')
    conn = get_db_connection()
    store = conn.execute('SELECT access_token FROM stores WHERE shop_url = ?', (shop,)).fetchone()
    conn.close()
    if not store: return jsonify({"error": "Store not found"}), 404

    headers = {"X-Shopify-Access-Token": store['access_token'], "Content-Type": "application/json"}
    mutation = """
    mutation {
      appSubscriptionCreate(
        name: "Aman El-Mandoob Standard"
        lineItems: [{ plan: { appRecurringPricingDetails: { price: { amount: 19.0, currencyCode: USD }, interval: EVERY_30_DAYS } } }]
        returnUrl: "https://Ahmdnoaman.pythonanywhere.com/billing/confirm?shop="
      ) {
        confirmationUrl
        userErrors { field message }
      }
    }
    """
    return jsonify({"status": "ready_for_billing"})

@app.route('/billing/confirm')
def billing_confirm():
    shop = request.args.get('shop')
    if shop:
        conn = get_db_connection()
        conn.execute('UPDATE stores SET plan_status = "ACTIVE" WHERE shop_url = ?', (shop,))
        conn.commit(); conn.close()
    return "<h1>تمت عملية التثبيت والاشتراك بنجاح!</h1>"

if __name__ == '__main__':
    app.run(debug=True)
