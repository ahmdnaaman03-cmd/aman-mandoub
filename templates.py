MANDOUB_TEMPLATE = """
<!DOCTYPE html>
<html dir="rtl" lang="ar">
<head><meta charset="UTF-8"><title>نظام المندوب</title></head>
<body>
    <h1>نظام تتبع الشحنات - المندوب</h1>
    {% if error %}<p style="color:red;">{{ error }}</p>{% endif %}
    <form method="post">
        رقم الشحنة: <input type="text" name="order_id" value="{{ order_id }}">
        <button type="submit">بحث</button>
    </form>
    {% if success %}
        <hr>
        <h3>تفاصيل الشحنة {{ order_id }}</h3>
        <p>العميل: {{ customer_name }}</p>
        <p>السعر: {{ price }}</p>
        <p>حالة الدفع: {{ 'تم الدفع ✅' if paid else 'لم يتم الدفع ❌' }}</p>
        <img src="data:image/png;base64,{{ qr_data }}" alt="QR Code">
    {% endif %}
</body>
</html>
"""

CLIENT_TEMPLATE = """
<!DOCTYPE html>
<html dir="rtl" lang="ar">
<head><meta charset="UTF-8"><title>دفع العميل</title></head>
<body>
    <h1>صفحة الدفع</h1>
    <p>رقم الشحنة: {{ order_id }}</p>
    <p>المبلغ المطلوب: {{ price }}</p>
    {% if already_paid %}
        <h2 style="color:green;">تم الدفع بنجاح! شكراً لك.</h2>
    {% else %}
        <form action="/pay/confirm/{{ order_id }}" method="post">
            <button type="submit" style="padding:10px 20px; background:blue; color:white;">تأكيد الدفع</button>
        </form>
    {% endif %}
</body>
</html>
"""
