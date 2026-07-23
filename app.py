import os
import sqlite3
import secrets
import hashlib
import urllib.parse
from flask import Flask, request, jsonify, render_template

app = Flask(__name__)
DB_NAME = "secure_delivery.db"
SHARED_WEBHOOK_SECRET = "my_super_secret"

def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
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
    conn.commit()
    conn.close()

@app.route('/pay/simulate-gateway/<string:order_id>', methods=['POST', 'GET'])
def simulate_gateway(order_id):
    conn = get_db_connection()
    order = conn.execute('SELECT * FROM orders WHERE order_id = ?', (str(order_id),)).fetchone()
    conn.close()

    if order is None:
        return jsonify({"error": "Order not found"}), 404

    data_to_sign = f"{order_id}{SHARED_WEBHOOK_SECRET}"
    signature = hashlib.sha256(data_to_sign.encode()).hexdigest()

    webhook_payload = {
        "order_id": order_id,
        "status": "SUCCESS",
        "signature": signature
    }
    return jsonify(webhook_payload), 200

if __name__ == '__main__':
    init_db()
    app.run(debug=True, host='0.0.0.0')
