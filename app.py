from flask import Flask, render_template_string, jsonify, request, redirect, url_for
import sqlite3, qrcode, io, base64

app = Flask(__name__)
GLOBAL_URL = "https://Ahmdnoaman.pythonanywhere.com"

def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def home():
    return render_template_string('''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Aman El-Mandoob</title>
        <style>
            body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; background: #f4f5f7; display: flex; justify-content: center; align-items: center; min-height: 100vh; margin: 0; }
            .card { background: white; padding: 25px; border-radius: 16px; box-shadow: 0 10px 25px rgba(0,0,0,0.08); width: 90%; max-width: 380px; text-align: center; }
            .title { font-size: 20px; font-weight: bold; color: #111; margin-bottom: 4px; }
            .subtitle { font-size: 13px; color: #666; margin-bottom: 20px; }
            input { width: 100%; padding: 12px; border: 1px solid #ddd; border-radius: 8px; font-size: 16px; text-align: center; box-sizing: border-box; margin-bottom: 12px; }
            button { width: 100%; padding: 12px; background: #0f172a; color: white; border: none; border-radius: 8px; font-size: 15px; font-weight: 600; cursor: pointer; }
            .qr-container { margin-top: 20px; display: none; }
            .qr-container img { width: 200px; height: 200px; }
            .status-box { margin-top: 15px; padding: 10px; border-radius: 8px; font-size: 14px; font-weight: 600; background: #fef3c7; color: #92400e; }
            .status-success { background: #d1fae5 !important; color: #065f46 !important; }
        </style>
    </head>
    <body>
        <div class="card">
            <div class="title">🛡️ Aman El-Mandoob</div>
            <div class="subtitle">Instant Payment Gateway</div>
            <input type="text" id="orderId" placeholder="Order ID (e.g. 1001)" value="1001">
            <button onclick="generateQR()">Generate Dynamic QR</button>
            
            <div id="qrArea" class="qr-container">
                <img id="qrImg" src="" alt="QR Code">
                <div id="statusBox" class="status-box">⏳ Waiting for Payment...</div>
            </div>
        </div>
        <script>
            let currentOrderId = null;
            let pollInterval = null;

            function generateQR() {
                const orderId = document.getElementById('orderId').value.trim();
                if(!orderId) return alert('Enter Order ID');
                currentOrderId = orderId;
                
                document.getElementById('qrImg').src = '/get_qr/' + orderId;
                document.getElementById('qrArea').style.display = 'block';
                
                const statusBox = document.getElementById('statusBox');
                statusBox.className = 'status-box';
                statusBox.innerText = '⏳ Waiting for Payment...';

                if(pollInterval) clearInterval(pollInterval);
                pollInterval = setInterval(checkStatus, 2000);
            }

            function checkStatus() {
                if(!currentOrderId) return;
                fetch('/check_status/' + currentOrderId)
                    .then(res => res.json())
                    .then(data => {
                        if(data.status === 'paid') {
                            const statusBox = document.getElementById('statusBox');
                            statusBox.className = 'status-box status-success';
                            statusBox.innerText = '✅ Payment Received Successfully!';
                            clearInterval(pollInterval);
                        }
                    });
            }
        </script>
    </body>
    </html>
    ''')
@app.route('/get_qr/<order_id>')
def get_qr(order_id):
    pay_url = f"{GLOBAL_URL}/pay/{order_id}"
    qr = qrcode.QRCode(version=1, box_size=10, border=2)
    qr.add_data(pay_url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    buf = io.BytesIO()
    img.save(buf)
    buf.seek(0)
    return app.response_class(buf.getvalue(), mimetype='image/png')

@app.route('/check_status/<order_id>')
def check_status(order_id):
    conn = get_db_connection()
    order = conn.execute('SELECT status FROM orders WHERE order_id = ?', (order_id,)).fetchone()
    conn.close()
    if order:
        return jsonify({'status': order['status']})
    return jsonify({'status': 'pending'})

@app.route('/pay/<order_id>', methods=['GET', 'POST'])
def pay(order_id):
    conn = get_db_connection()
    if request.method == 'POST':
        conn.execute('UPDATE orders SET status = "paid" WHERE order_id = ?', (order_id,))
        conn.commit()
        conn.close()
        return '''
        <div style="text-align:center; font-family:sans-serif; padding:50px;">
            <h1 style="color:#10b981;">✅ Payment Confirmed!</h1>
            <p>Thank you. Your cash collection has been securely verified.</p>
        </div>
        '''
    
    order = conn.execute('SELECT * FROM orders WHERE order_id = ?', (order_id,)).fetchone()
    conn.close()
    
    price = order['price'] if order else "250.00"
    name = order['customer_name'] if order else "Customer"
    
    return f'''
    <div style="text-align:center; font-family:sans-serif; padding:30px; max-width:350px; margin:auto;">
        <h2>Complete Payment</h2>
        <p>Customer: <b>{name}</b></p>
        <p>Amount: <b style="font-size:24px; color:#0f172a;">{price} EGP</b></p>
        <form method="POST">
            <button style="width:100%; padding:15px; background:#10b981; color:white; border:none; border-radius:8px; font-size:16px; font-weight:bold; cursor:pointer;">
                Confirm Cash Received
            </button>
        </form>
    </div>
    '''

@app.route('/webhook/shopify', methods=['POST'])
def shopify_webhook():
    data = request.get_json()
    if not data:
        return jsonify({'status': 'no data'}), 400
    
    order_id = str(data.get('order_number') or data.get('id'))
    customer_name = data.get('customer', {}).get('first_name', 'Shopify Customer')
    total_price = float(data.get('total_price', 0.0))
    
    conn = get_db_connection()
    conn.execute(
        'INSERT OR REPLACE INTO orders (order_id, customer_name, price, status) VALUES (?, ?, ?, ?)',
        (order_id, customer_name, total_price, 'pending')
    )
    conn.commit()
    conn.close()
    
    return jsonify({'status': 'success', 'order_id': order_id}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

@app.route('/auth')
def shopify_auth():
    shop = request.args.get('shop')
    return f"Aman El-Mandoob Shopify Auth Active for: {shop}", 200
