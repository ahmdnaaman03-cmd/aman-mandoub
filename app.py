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
<html dir="rtl" lang="ar">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>أمان المندوب - العرض التجريبي الحي</title>
    <style>
        body { font-family: system-ui, -apple-system, sans-serif; background: #f4f6f8; margin: 0; padding: 20px; text-align: center; }
        .card { background: white; max-width: 450px; margin: 20px auto; padding: 25px; border-radius: 12px; box-shadow: 0 4px 15px rgba(0,0,0,0.1); }
        h2 { color: #1a252c; margin-bottom: 10px; }
        p { color: #637381; font-size: 14px; }
        input { width: 85%; padding: 12px; margin: 10px 0; border: 1px solid #ccc; border-radius: 8px; font-size: 16px; text-align: center; }
        button { background: #008060; color: white; border: none; padding: 12px 24px; border-radius: 8px; font-size: 16px; cursor: pointer; font-weight: bold; width: 90%; }
        button:hover { background: #006e52; }
        #qr-result { margin-top: 20px; display: none; }
        img { width: 180px; height: 180px; border: 1px solid #ddd; padding: 10px; border-radius: 8px; background: #fff; }
        .status-container { margin-top: 20px; font-size: 15px; color: #333; }
        .badge { display: inline-block; padding: 8px 16px; border-radius: 20px; font-weight: bold; margin-top: 8px; font-size: 14px; }
        .pending { background: #fff3cd; color: #856404; border: 1px solid #ffeeba; }
        .paid { background: #d4edda; color: #155724; border: 1px solid #c3e6cb; }
    </style>
</head>
<body>
    <div class="card">
        <h2>🛡️ أمان المندوب - Live Demo</h2>
        <p>أدخل رقم الشحنة لمتابعة حالة الدفع وتوليد الـ QR اللحظي</p>
        <input type="text" id="orderId" placeholder="أدخل رقم الشحنة (مثال: 1001)">
        <button onclick="startDemo()">عرض الشحنة والـ QR</button>
        
        <div id="qr-result">
            <h3>كود التأكيد الخاص بالعميل</h3>
            <img id="qrImg" src="" alt="QR Code">
            
            <div class="status-container">
                <div>حالة الدفع والاستلام اللحظية:</div>
                <span id="statusBadge" class="badge pending">⏳ PENDING - بانتظار مسح الكود والدفع</span>
            </div>
        </div>
    </div>

    <script>
        let currentOrder = "";
        let pollTimer = null;

        function startDemo() {
            currentOrder = document.getElementById('orderId').value.trim();
            if(!currentOrder) { alert('برجاء إدخال رقم الشحنة أولاً'); return; }

            var verifyUrl = "https://Ahmdnoaman.pythonanywhere.com/verify?order=" + encodeURIComponent(currentOrder);
            var qrUrl = "https://api.qrserver.com/v1/create-qr-code/?size=200x200&data=" + encodeURIComponent(verifyUrl);

            document.getElementById('qrImg').src = qrUrl;
            document.getElementById('qr-result').style.display = 'block';

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
                        badge.innerText = '✅ PAID - تم الدفع وتأكيد التسليم بنجاح!';
                    } else {
                        badge.className = 'badge pending';
                        badge.innerText = '⏳ PENDING - بانتظار مسح الكود والدفع';
                    }
                });
        }
    </script>
</body>
</html>
"""
VERIFY_HTML = """
<!DOCTYPE html>
<html dir="rtl" lang="ar">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>تأكيد الدفع والاستلام</title>
    <style>
        body { font-family: system-ui, -apple-system, sans-serif; background: #e8f5e9; text-align: center; padding: 40px 20px; }
        .card { background: white; max-width: 400px; margin: 0 auto; padding: 30px; border-radius: 12px; box-shadow: 0 4px 15px rgba(0,0,0,0.1); }
        h1 { color: #2e7d32; }
        p { color: #333; font-size: 16px; }
    </style>
</head>
<body>
    <div class="card">
        <h1>✅ تم الدفع والتأكيد!</h1>
        <p>شحنة رقم: <strong>{{ order_id }}</strong></p>
        <p>تم تسديد المبلغ وتسجيل حالة "تم الاستلام والتسليم" بنجاح في قاعدة البيانات.</p>
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
    return "<h1>تمت عملية التثبيت والاشتراك بنجاح!</h1>"

if __name__ == '__main__':
    app.run(debug=True)
