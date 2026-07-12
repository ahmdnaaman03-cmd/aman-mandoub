import csv, io, base64, qrcode
from flask import Flask, request, render_template_string, redirect, url_for
from templates import MANDOUB_TEMPLATE, CLIENT_TEMPLATE

app = Flask(__name__)
payment_status = {}

# ضع الرابط الدائم الجديد هنا بعد الرفع:
GLOBAL_URL = "https://aman-mandoub.koyeb.app" 

@app.route('/', methods=['GET', 'POST'])
def index():
    order_id = ""
    if request.method == 'POST':
        order_id = request.form.get('order_id')
        with open('data.csv', mode='r') as f:
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
    with open('data.csv', mode='r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row['order_id'] == order_id: price = row['price']; break
    is_paid = payment_status.get(order_id, False)
    return render_template_string(CLIENT_TEMPLATE, order_id=order_id, price=price, already_paid=is_paid)

@app.route('/pay/confirm/<order_id>', methods=['POST'])
def confirm_pay(order_id):
    payment_status[order_id] = True
    return redirect(url_for('client_pay', order_id=order_id))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
