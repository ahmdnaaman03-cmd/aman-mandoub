from flask import Flask, request, jsonify
import qrcode
import os

app = Flask(__name__)

@app.route('/webhook/orders/create', methods=['POST'])
def handle_cod_order():
    order_data = request.json
    if not order_data:
        return jsonify({"status": "no data"}), 400

    order_id = order_data.get('id')
    order_name = order_data.get('name', f"#{order_id}")
    total_price = order_data.get('total_price')
    currency = order_data.get('currency', 'EGP')
    
    print(f"معالجة طلب COD رقم: {order_name} بمبلغ: {total_price} {currency}")
    
    payment_payload = f"AmanCOD:{order_name}:{total_price}:{currency}"
    
    img = qrcode.make(payment_payload)
    os.makedirs('static/qrs', exist_ok=True)
    qr_path = f"static/qrs/order_{order_id}.png"
    img.save(qr_path)
    
    print(f"تم حفظ QR التحصيل بنجاح في: {qr_path}")
    return jsonify({"status": "success", "order_id": order_id, "qr_path": qr_path}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
