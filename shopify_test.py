import os
import requests
import json

SHOPIFY_STORE = os.getenv("SHOPIFY_STORE", "aman-test-store-c9korns0")
SHOPIFY_ACCESS_TOKEN = os.getenv("SHOPIFY_ACCESS_TOKEN", "YOUR_ACCESSTOKEN_HERE")

print("جاري الاتصال بـ Shopify وسحب الطلبات...")

url = f"https://{SHOPIFY_STORE}.myshopify.com/admin/api/2024-01/orders.json"
headers = {
    "X-Shopify-Access-Token": SHOPIFY_ACCESS_TOKEN,
    "Content-Type": "application/json"
}

try:
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        orders = response.json().get("orders", [])
        print(f"تم بنجاح! عدد الطلبات المسترجعة: {len(orders)}")
        for order in orders:
            print(f"- رقم الطلب: {order.get('name')} | الإجمالي: {order.get('total_price')} {order.get('currency')}")
    else:
        print(f"فشل الاتصال. رمز الخطأ: {response.status_code}")
        print(response.text)
except Exception as e:
    print(f"حدث خطأ أثناء الاتصال: {e}")
