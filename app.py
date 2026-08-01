import sqlite3
from flask import Flask, request, jsonify

app = Flask(__name__)

# مسار استقبال الـ Webhook وتحديث حالة الطلب بـ UPDATE الآمن
@app.route('/webhook', methods=['POST'])
def shopify_webhook():
    order_id = request.json.get('id')
    try:
        conn = sqlite3.connect('orders.db') # اسم قاعدة البيانات الخاصة بك
        cursor = conn.cursor()
        cursor.execute('UPDATE orders SET status = ? WHERE order_id = ?', ('PAID', order_id))
        conn.commit()
    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()
    return jsonify({"status": "success"}), 200

@app.route('/verify', methods=['GET'])
def verify():
    order_id = request.args.get('order')
    try:
        conn = sqlite3.connect('orders.db')
        cursor = conn.cursor()
        row = cursor.execute('SELECT status FROM orders WHERE order_id = ?', (order_id,)).fetchone()
        conn.close()
        if row:
            return f"Order {order_id} Status: {row[0]}"
        return "Order not found", 404
    except Exception as e:
        return f"Error: {e}", 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
