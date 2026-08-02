import csv
import io
import base64
import qrcode
import sqlite3
import os
from flask import Flask, request, render_template_string, redirect, url_for, jsonify
from templates import MANDOUB_TEMPLATE, CLIENT_TEMPLATE, REPORT_TEMPLATE

app = Flask(__name__)
payment_status = {}

# ضع الرابط الدائم الجديد هنا بعد الرفع:
GLOBAL_URL = os.environ.get('GLOBAL_URL', "https://ahmdnoaman.pythonanywhere.com")
DB_NAME = 'secure_delivery.db'

# ============ قاعدة البيانات ============
def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """تهيئة قاعدة البيانات"""
    if not os.path.exists(DB_NAME):
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                order_id TEXT UNIQUE NOT NULL,
                customer_name TEXT NOT NULL,
                price REAL NOT NULL,
                status TEXT DEFAULT 'pending',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS stores (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                shop_url TEXT UNIQUE NOT NULL,
                access_token TEXT NOT NULL,
                plan_status TEXT DEFAULT 'ACTIVE',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        conn.commit()
        conn.close()

# ============ المسارات الأساسية ============
@app.route('/', methods=['GET', 'POST'])
def index():
    """صفحة المندوب الرئيسية - البحث عن الشحنات وتوليد QR"""
    order_id = ""
    error = None
    success = False
    customer_name = ""
    price = ""
    qr_data = ""
    is_paid = False
    
    if request.method == 'POST':
        order_id = request.form.get('order_id', '').strip()
        
        if order_id:
            # البحث في قاعدة البيانات أولاً
            conn = get_db_connection()
            row = conn.execute('SELECT * FROM orders WHERE order_id = ?', (order_id,)).fetchone()
            conn.close()
            
            if row:
                customer_name = row['customer_name']
                price = row['price']
                is_paid = payment_status.get(order_id, row['status'] == 'paid')
                
                # توليد QR Code
                client_pay_url = f"{GLOBAL_URL}/pay/client/{order_id}"
                qr = qrcode.QRCode(version=1, box_size=10, border=2)
                qr.add_data(client_pay_url)
                qr.make(fit=True)
                img = qr.make_image(fill_color="black", back_color="white")
                img_buffer = io.BytesIO()
                img.save(img_buffer, format="PNG")
                qr_data = base64.b64encode(img_buffer.getvalue()).decode('utf-8')
                
                success = True
            else:
                error = f"❌ الشحنة {order_id} غير مسجلة في النظام!"
    
    return render_template_string(
        MANDOUB_TEMPLATE,
        order_id=order_id,
        error=error,
        success=success,
        customer_name=customer_name,
        price=price,
        qr_data=qr_data,
        paid=is_paid
    )

@app.route('/pay/client/<order_id>')
def client_pay(order_id):
    """صفحة الدفع للعميل"""
    conn = get_db_connection()
    row = conn.execute('SELECT * FROM orders WHERE order_id = ?', (order_id,)).fetchone()
    conn.close()
    
    if not row:
        return render_template_string(CLIENT_TEMPLATE, order_id=order_id, price="0", already_paid=False, error=True)
    
    price = row['price']
    is_paid = payment_status.get(order_id, row['status'] == 'paid')
    
    return render_template_string(
        CLIENT_TEMPLATE,
        order_id=order_id,
        price=price,
        already_paid=is_paid
    )

@app.route('/pay/confirm/<order_id>', methods=['POST'])
def confirm_pay(order_id):
    """تأكيد الدفع - تحديث حالة الطلب"""
    payment_status[order_id] = True
    
    # تحديث قاعدة البيانات
    conn = get_db_connection()
    conn.execute('UPDATE orders SET status = ? WHERE order_id = ?', ('paid', order_id))
    conn.commit()
    conn.close()
    
    return redirect(url_for('client_pay', order_id=order_id))

@app.route('/toggle_status/<order_id>', methods=['POST'])
def toggle_status(order_id):
    """تبديل حالة الدفع يدويًا (للاختبار)"""
    current_status = payment_status.get(order_id, False)
    payment_status[order_id] = not current_status
    
    # تحديث قاعدة البيانات
    conn = get_db_connection()
    new_status = 'paid' if not current_status else 'pending'
    conn.execute('UPDATE orders SET status = ? WHERE order_id = ?', (new_status, order_id))
    conn.commit()
    conn.close()
    
    return redirect(url_for('index'))

@app.route('/report')
def report():
    """التقرير اليومي للشحنات"""
    conn = get_db_connection()
    rows = conn.execute('SELECT * FROM orders ORDER BY created_at DESC').fetchall()
    conn.close()
    
    orders = []
    for row in rows:
        order_dict = dict(row)
        order_dict['paid'] = payment_status.get(row['order_id'], row['status'] == 'paid')
        orders.append(order_dict)
    
    return render_template_string(REPORT_TEMPLATE, orders=orders)

# ============ مسارات الصفحات الثابتة ============
@app.route('/privacy')
def privacy_policy():
    """سياسة الخصوصية"""
    with open('privacy.html', 'r', encoding='utf-8') as f:
        return f.read()

@app.route('/terms')
def terms():
    """شروط الخدمة"""
    with open('terms.html', 'r', encoding='utf-8') as f:
        return f.read()

@app.route('/support')
def support():
    """صفحة الدعم"""
    return render_template_string("""
    <!DOCTYPE html>
    <html lang="ar" dir="rtl">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>الدعم - نظام أمان المندوب</title>
        <style>
            body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f4f6f9; color: #333; margin: 0; padding: 20px; }
            .container { max-width: 600px; background: white; margin: 30px auto; padding: 30px; border-radius: 12px; box-shadow: 0 4px 15px rgba(0,0,0,0.1); }
            h1 { color: #1e3a8a; }
            p { font-size: 16px; line-height: 1.6; }
            .back-link { display: inline-block; margin-top: 20px; color: #1e3a8a; text-decoration: none; font-weight: bold; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>📞 الدعم الفني</h1>
            <p>للتواصل معنا بخصوص أي مشاكل أو استفسارات:</p>
            <p><strong>البريد الإلكتروني:</strong> support@aman-mandoub.com</p>
            <p><strong>الهاتف:</strong> +20 (XXX) XXX-XXXX</p>
            <a href="/" class="back-link">⬅️ العودة للرئيسية</a>
        </div>
    </body>
    </html>
    """)

# ============ API للتحقق من حالة الطلب ============
@app.route('/api/order_status')
def api_order_status():
    """API للتحقق من حالة الطلب (للاستخدام من الواجهات الخارجية)"""
    order_id = request.args.get('order')
    
    if not order_id:
        return jsonify({"error": "Missing order parameter"}), 400
    
    conn = get_db_connection()
    row = conn.execute('SELECT status FROM orders WHERE order_id = ?', (order_id,)).fetchone()
    conn.close()
    
    status = 'paid' if payment_status.get(order_id, False) else (row['status'] if row else 'not_found')
    
    return jsonify({
        "order_id": order_id,
        "status": status
    })

# ============ مسارات إدارة البيانات (للاختبار والإدارة) ============
@app.route('/admin/add_order', methods=['POST'])
def admin_add_order():
    """إضافة طلب جديد (للاختبار)"""
    data = request.get_json()
    
    if not all(k in data for k in ['order_id', 'customer_name', 'price']):
        return jsonify({"error": "Missing required fields"}), 400
    
    conn = get_db_connection()
    try:
        conn.execute(
            'INSERT INTO orders (order_id, customer_name, price) VALUES (?, ?, ?)',
            (data['order_id'], data['customer_name'], data['price'])
        )
        conn.commit()
        return jsonify({"success": True, "message": "Order added successfully"})
    except sqlite3.IntegrityError:
        return jsonify({"error": "Order ID already exists"}), 400
    finally:
        conn.close()

@app.route('/admin/orders')
def admin_orders():
    """عرض جميع الطلبات (للاختبار)"""
    conn = get_db_connection()
    rows = conn.execute('SELECT * FROM orders').fetchall()
    conn.close()
    
    orders = [dict(row) for row in rows]
    return jsonify(orders)

# ============ تهيئة التطبيق ============
if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=8000, debug=False)
