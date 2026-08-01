import csv, io, base64, qrcode
from flask import Flask, request, render_template_string, redirect, url_for
from templates import MANDOUB_TEMPLATE, CLIENT_TEMPLATE

app = Flask(__name__)
payment_status = {}

# ضع الرابط الدائم الجديد هنا بعد الرفع:
GLOBAL_URL = "https://ahmdnoaman.pythonanywhere.com" 

@app.route('/', methods=['GET', 'POST'])
def index():
    order_id = ""
    if request.method == 'POST':
        order_id = request.form.get('order_id')
        with open('data.csv', mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row['order_id'] == order_id:
                    client_pay_url = f"{GLOBAL_URL}/pay/client/{order_id}"
                    qr = qrcode.QRCode(version=1, box_size=10, border=2)
                    qr.add_data(client_pay_url)
                    qr.make(fit=True)
                    img = qr.make_image(fill_color="black", back_color="white")
                    img_buffer = io.BytesIO()
                    img.save(img_buffer, format="PNG")
                    qr_base64 = base64.b64encode(img_buffer.getvalue()).decode('utf-8')
                    is_paid = payment_status.get(order_id, False)
                    return render_template_string(MANDOUB_TEMPLATE, success=True, order_id=order_id, paid=is_paid,
                                                 customer_name=row['customer_name'], price=row['price'], qr_data=qr_base64)
            return render_template_string(MANDOUB_TEMPLATE, error=f"❌ الشحنة {order_id} غير مسجلة!", order_id=order_id)
    return render_template_string(MANDOUB_TEMPLATE, order_id=order_id)

@app.route('/pay/client/<order_id>')
def client_pay(order_id):
    price = ""
    with open('data.csv', mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row['order_id'] == order_id: price = row['price']; break
    is_paid = payment_status.get(order_id, False)
    return render_template_string(CLIENT_TEMPLATE, order_id=order_id, price=price, already_paid=is_paid)

@app.route('/pay/confirm/<order_id>', methods=['POST'])
def confirm_pay(order_id):
    payment_status[order_id] = True
    return redirect(url_for('client_pay', order_id=order_id))

@app.route('/toggle_status/<order_id>', methods=['POST'])
def toggle_status(order_id):
    current_status = payment_status.get(order_id, False)
    payment_status[order_id] = not current_status
    return redirect(url_for('index'))

@app.route('/report')
def report():
    orders = []
    with open('data.csv', mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            row['paid'] = payment_status.get(row['order_id'], False)
            orders.append(row)
    
    from templates import REPORT_TEMPLATE
    return render_template_string(REPORT_TEMPLATE, orders=orders)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
Instant Payment Gateway</div>
        
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


@app.route('/terms')
def terms():
    return render_template('terms.html')

@app.route('/support')
def support():
    return render_template('support.html')

if __name__ == '__main__':
    app.run(debug=True)

@app.route('/privacy')
def privacy_policy():
    return render_template('privacy.html')
