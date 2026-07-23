import os
import sqlite3
import secrets
import hashlib
import urllib.parse
from flask import Flask, request, jsonify, url_for, render_template

app = Flask(__name__)
DB_NAME = "secure_delivery.db"
SHARED_WEBHOOK_SECRET = "my_super_secret_gateway_key_2026"

def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    if os.path.exists(DB_NAME):
        os.remove(DB_NAME)

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS orders (
            order_id TEXT PRIMARY KEY,
            customer_name TEXT NOT NULL,
            amount REAL NOT NULL,
            payment_status TEXT DEFAULT 'PENDING',
            secure_token TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    sample_orders = [
        ('ORD1001', 'Ahmed Noaman', 2500.00, 'PENDING', secrets.token_hex(16)),
        ('ORD1002', 'Mohamed Ali', 1200.50, 'PENDING', secrets.token_hex(16))
    ]

    cursor.executemany('''
        INSERT INTO orders (order_id, customer_name, amount, payment_status, secure_token)
        VALUES (?, ?, ?, ?, ?)
    ''', sample_orders)
    conn.commit()
    conn.close()

init_db()

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/generate_qr', methods=['POST'])
def generate_qr():
    order_id = request.form.get('order_id', '').strip()
    search_id = f"ORD{order_id}" if not order_id.upper().startswith('ORD') else order_id.upper()

    conn = get_db_connection()
    order = conn.execute('SELECT * FROM orders WHERE order_id = ?', (search_id,)).fetchone()
    conn.close()

    if order is None:
        return jsonify({"error": "Order ID not found."}), 404

    token = order['secure_token']
    customer_pay_url = url_for('customer_view', order_id=search_id, token=token, _external=True)
    encoded_url = urllib.parse.quote(customer_pay_url)
    qr_image_url = f"https://api.qrserver.com/v1/create-qr-code/?size=250x250&data={encoded_url}"

    return jsonify({
        "qr_image": qr_image_url,
        "customer_pay_url": customer_pay_url,
        "order_id": search_id,
        "status": order['payment_status'],
        "message": "QR Generated Successfully"
    })

@app.route('/check_status/<order_id>')
def check_status(order_id):
    conn = get_db_connection()
    order = conn.execute('SELECT payment_status FROM orders WHERE order_id = ?', (order_id,)).fetchone()
    conn.close()
    if order:
        return jsonify({"status": order['payment_status']})
    return jsonify({"error": "Order not found"}), 404

@app.route('/pay/customer/<order_id>')
def customer_view(order_id):
    provided_token = request.args.get('token')
    conn = get_db_connection()
    order = conn.execute('SELECT * FROM orders WHERE order_id = ?', (order_id,)).fetchone()
    conn.close()

    if order is None:
        return jsonify({"error": "Order not found"}), 404
    if not provided_token or provided_token != order['secure_token']:
        return jsonify({"error": "Unauthorized"}), 403

    confirm_url = url_for('simulate_gateway', order_id=order_id)
    return render_template('customer.html', customer_name=order['customer_name'], amount_to_pay=order['amount'], confirm_url=confirm_url)

@app.route('/pay/simulate-gateway/<order_id>', methods=['POST', 'GET'])
def simulate_gateway(order_id):
    conn = get_db_connection()
    order = conn.execute('SELECT * FROM orders WHERE order_id = ?', (order_id,)).fetchone()
    conn.close()
    if order is None:
        return jsonify({"error": "Order not found"}), 404

    data_to_sign = f"{order_id}{SHARED_WEBHOOK_SECRET}"
    signature = hashlib.sha256(data_to_sign.encode()).hexdigest()

    webhook_payload = {
        "order_id": order_id,
        "status": "SUCCESS",
        "amount_paid": order['amount'],
        "gateway_signature": signature
    }
    return handle_gateway_webhook(webhook_payload)

def handle_gateway_webhook(payload):
    order_id = payload.get("order_id")
    status = payload.get("status")
    received_signature = payload.get("gateway_signature")

    expected_data = f"{order_id}{SHARED_WEBHOOK_SECRET}"
    expected_signature = hashlib.sha256(expected_data.encode()).hexdigest()

    if received_signature != expected_signature:
        return jsonify({"error": "Security Alert: Invalid Webhook Signature!"}), 403

    if status == "SUCCESS":
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('UPDATE orders SET payment_status = ? WHERE order_id = ?', ('PAID', order_id))
        conn.commit()
        conn.close()

        return jsonify({
            "status": "processed",
            "message": f"Payment successful! Order {order_id} marked as PAID."
        }), 200

    return jsonify({"status": "failed", "message": "Payment status not success"}), 400

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
