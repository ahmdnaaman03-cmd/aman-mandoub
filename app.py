import os, sqlite3, requests
from flask import Flask, request, jsonify, redirect, render_template_string
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

DB_NAME = "secure_delivery.db"
SHOPIFY_API_KEY = os.getenv("SHOPIFY_API_KEY")
SHOPIFY_API_SECRET = os.getenv("SHOPIFY_API_SECRET")
APP_URL = "https://Ahmdnoaman.pythonanywhere.com"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS orders (
            order_id TEXT PRIMARY KEY,
            status TEXT DEFAULT 'PENDING'
        )
    ''')
    conn.commit()
    conn.close()

init_db()

def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

DEMO_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Aman El-Mandoob</title>
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; background-color: #f6f6f7; margin: 0; padding: 20px; display: flex; justify-content: center; align-items: center; min-height: 90vh; }
        .card { background: white; padding: 30px 20px; border-radius: 16px; box-shadow: 0 4px 20px rgba(0, 0, 0, 0.05); text-align: center; width: 100%; max-width: 360px; }
        .logo-box { background: #e6cfb3; width: 60px; height: 38px; margin: 0 auto 12px; border-radius: 4px; display: flex; justify-content: center; align-items: center; }
        .shield-icon { color: #2e7d32; font-size: 18px; }
        h2 { margin: 0; font-size: 22px; font-weight: 700; color: #1a1a1a; }
        .subtitle { color: #6d7175; font-size: 13px; margin-top: 4px; margin-bottom: 20px; }
        input { width: 100%; padding: 12px; border: 1px solid #d2d5d8; border-radius: 8px; font-size: 16px; font-weight: 600; text-align: center; box-sizing: border-box; margin-bottom: 12px; outline: none; }
        button { width: 100%; background: #1c2434; color: white; border: none; padding: 14px; border-radius: 8px; font-size: 15px; font-weight: 600; cursor: pointer; }
        #qr-container { margin-top: 20px; display: none; }
        .qr-box { border: 1px solid #f0f0f0; border-radius: 12px; padding: 15px; background: #fafafa; display: inline-block; }
        .qr-box img { width: 210px; height: 210px; display: block; }
        .badge { display: inline-block; width: 100%; padding: 10px 0; border-radius: 8px; font-weight: 600; font-size: 14px; margin-top: 15px; box-sizing: border-box; }
        .pending { background: #fdf3d8; color: #5c4200; }
        .paid { background: #d4edda; color: #155724; }
        .scan-text { color: #6d7175; font-size: 13px; margin-top: 12px; }
    </style>
</head>
<body>
    <div class="card">
        <div class="logo-box"><span class="shield-icon">🛡️</span></div>
        <h2>Aman El-Mandoob</h2>
        <div class="subtitle">Instant Payment Gateway</div>
        
        <input type="text" id="orderId" value="1002" placeholder="Order ID">
        <button onclick="generateQR()">Generate Dynamic QR</button>
        
        <div id="qr-container">
            <div class="qr-box">
                <img id="qrImg" src="" alt="QR Code">
            </div>
            <div id="statusBadge" class="badge pending">⏳ Waiting for Payment...</div>
            <div class="scan-text">Ask customer to scan with phone camera</div>
        </div>
    </div>

    <script>
        let currentOrder = "";
        let pollTimer = null;

        function generateQR() {
            currentOrder = document.getElementById('orderId').value.trim();
            if(!currentOrder) return;

            var verifyUrl = "https://Ahmdnoaman.pythonanywhere.com/verify?order=" + encodeURIComponent(currentOrder);
            var qrUrl = "https://api.qrserver.com/v1/create-qr-code/?size=250x250&data=" + encodeURIComponent(verifyUrl);

            document.getElementById('qrImg').src = qrUrl;
            document.getElementById('qr-container').style.display = 'block';

            checkStatus();
            if(pollTimer) clearInterval(pollTimer);
            pollTimer = setInterval(checkStatus, 2000);
        }

        function checkStatus() {
            if(!currentOrder) return;
            fetch('/api/order_status?order=' + encodeURIComponent(currentOrder))
                .then(res => res.json())
                .then(data => {
                    let badge = document.getElementById('statusBadge');
                    if(data.status === 'PAID') {
                        badge.className = 'badge paid';
                        badge.innerText = '✅ Payment Completed!';
                    } else {
                        badge.className = 'badge pending';
                        badge.innerText = '⏳ Waiting for Payment...';
                    }
                });
        }
    </script>
</body>
</html>
"""
VERIFY_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Payment Confirmation</title>
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, sans-serif; background: #e8f5e9; text-align: center; padding: 40px 20px; }
        .card { background: white; max-width: 350px; margin: 40px auto; padding: 30px; border-radius: 16px; box-shadow: 0 4px 15px rgba(0,0,0,0.05); }
        h2 { color: #2e7d32; margin-bottom: 10px; }
        p { color: #444; font-size: 15px; }
    </style>
</head>
<body>
    <div class="card">
        <h2>✅ Payment Confirmed!</h2>
        <p>Order ID: <strong>#{{ order_id }}</strong></p>
        <p>Delivery status updated successfully in system database.</p>
    </div>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(DEMO_HTML)

@app.route('/api/order_status')
def order_status():
    order_id = request.args.get('order')
    if not order_id: return jsonify({"error": "Missing order"}), 400
    conn = get_db_connection()
    row = conn.execute('SELECT status FROM orders WHERE order_id = ?', (order_id,)).fetchone()
    conn.close()
    status = row['status'] if row else 'PENDING'
    return jsonify({"order_id": order_id, "status": status})

@app.route('/verify')
def verify():
    order_id = request.args.get('order')
    if order_id:
        conn = get_db_connection()
        conn.execute('INSERT OR REPLACE INTO orders (order_id, status) VALUES (?, ?)', (order_id, 'PAID'))
        conn.commit()
        conn.close()
    return render_template_string(VERIFY_HTML, order_id=order_id)

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
    return jsonify({"status": "ready_for_billing"})

@app.route('/billing/confirm')
def billing_confirm():
    shop = request.args.get('shop')
    if shop:
        conn = get_db_connection()
        conn.execute('UPDATE stores SET plan_status = "ACTIVE" WHERE shop_url = ?', (shop,))
        conn.commit(); conn.close()
    return "<h1>Installation & Subscription Completed Successfully!</h1>"

if __name__ == '__main__':
    app.run(debug=True)

@app.route('/privacy')
def privacy_policy():
    return render_template('privacy.html')
