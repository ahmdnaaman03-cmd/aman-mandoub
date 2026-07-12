# templates.py

MANDOUB_TEMPLATE = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>بوابة المندوب - نظام أمان</title>
    <style>
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f4f6f9; color: #333; margin: 0; padding: 20px; text-align: center; }
        .container { max-width: 500px; background: white; margin: 30px auto; padding: 30px; border-radius: 12px; box-shadow: 0 4px 15px rgba(0,0,0,0.1); }
        h1 { color: #1e3a8a; margin-bottom: 25px; }
        label { font-weight: bold; display: block; margin-bottom: 8px; text-align: right; }
        input[type="text"] { width: 100%; padding: 12px; margin-bottom: 20px; border: 1px solid #ccc; border-radius: 6px; box-sizing: border-box; font-size: 16px; text-align: center; }
        button { background-color: #1e3a8a; color: white; padding: 12px 25px; border: none; border-radius: 6px; cursor: pointer; font-size: 16px; width: 100%; font-weight: bold; }
        button:hover { background-color: #13255c; }
        .error { color: #dc2626; background-color: #fef2f2; padding: 12px; border-radius: 6px; margin-bottom: 20px; font-weight: bold; border: 1px solid #fca5a5; }
        .success-box { background-color: #f0fdf4; border: 1px solid #bbf7d0; padding: 20px; border-radius: 8px; margin-top: 25px; }
        .qr-img { margin-top: 15px; max-width: 200px; border: 4px solid #1e3a8a; border-radius: 8px; }
        .status-badge { display: inline-block; padding: 6px 12px; border-radius: 20px; font-weight: bold; margin-top: 10px; }
        .paid { background-color: #dcfce7; color: #15803d; }
        .unpaid { background-color: #fef3c7; color: #d97706; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🛡️ نظام أمان المندوب</h1>
        
        {% if error %}
            <div class="error">{{ error }}</div>
        {% endif %}

        <form method="POST">
            <label for="order_id">أدخل رقم الشحنة للاستعلام:</label>
            <input type="text" id="order_id" name="order_id" value="{{ order_id }}" placeholder="مثال: 101" required>
            <button type="submit">توليد رمز الدفع (QR Code)</button>
        </form>

        {% if success %}
            <div class="success-box">
                <h3>📋 بيانات الشحنة رقم: {{ order_id }}</h3>
                <p><strong>اسم العميل:</strong> {{ customer_name }}</p>
                <p><strong>المبلغ المطلوب:</strong> {{ price }} جنيه</p>
                
                <p><strong>حالة الدفع الآن:</strong> 
                    {% if paid %}
                        <span class="status-badge paid">✅ تم الدفع بنجاح</span>
                    {% else %}
                        <span class="status-badge unpaid">⏳ في انتظار الدفع</span>
                    {% endif %}
                </p>

                <p style="margin-top:20px; font-weight:bold; color:#4b5563;">دع العميل يمسح الكود لإتمام الدفع:</p>
                <img class="qr-img" src="data:image/png;base64,{{ qr_data }}" alt="QR Code الدفع">
            </div>
        {% endif %}
    </div>
</body>
</html>
"""

CLIENT_TEMPLATE = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>بوابة الدفع الآمن للعميل</title>
    <style>
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f0fdf4; color: #333; margin: 0; padding: 20px; text-align: center; }
        .container { max-width: 450px; background: white; margin: 40px auto; padding: 30px; border-radius: 12px; box-shadow: 0 4px 15px rgba(0,0,0,0.1); border-top: 6px solid #16a34a; }
        h1 { color: #16a34a; margin-bottom: 20px; }
        .price-tag { font-size: 32px; font-weight: bold; color: #16a34a; margin: 20px 0; background: #f0fdf4; padding: 15px; border-radius: 8px; display: inline-block; min-width: 150px; }
        .btn-pay { background-color: #16a34a; color: white; padding: 15px 30px; border: none; border-radius: 6px; cursor: pointer; font-size: 18px; width: 100%; font-weight: bold; transition: 0.2s; }
        .btn-pay:hover { background-color: #15803d; }
        .success-alert { background-color: #dcfce7; color: #15803d; padding: 20px; border-radius: 8px; font-size: 18px; font-weight: bold; border: 1px solid #bbf7d0; }
        p { font-size: 16px; color: #4b5563; line-height: 1.6; }
    </style>
</head>
<body>
    <div class="container">
        <h1>💳 بوابة الدفع الآمن</h1>
        
        {% if already_paid %}
            <div class="success-alert">
                🎉 شكرًا لك! تم دفع مبلغ {{ price }} جنيه للشحنة رقم ({{ order_id }}) بنجاح، وتم تحديث التطبيق لدى المندوب.
            </div>
        {% else %}
            <p>أنت على وشك دفع قيمة الشحنة رقم: <strong>{{ order_id }}</strong></p>
            <p>إجمالي المبلغ المستحق للمندوب:</p>
            <div class="price-tag">{{ price }} ج.م</div>
            
            <form action="/pay/confirm/{{ order_id }}" method="POST">
                <button type="submit" class="btn-pay">💳 اضغط هنا لمحاكاة الدفع الفوري</button>
            </form>
            <p style="font-size: 12px; color: #9ca3af; margin-top: 15px;">🔒 اتصال آمن ومحمي بالكامل بنظام أمان.</p>
        {% endif %}
    </div>
</body>
</html>
"""
