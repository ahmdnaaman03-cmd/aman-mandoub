import os
import requests
import qrcode

SHOPIFY_STORE = os.getenv("SHOPIFY_STORE", "aman-test-store-c9korns0")
SHOPIFY_ACCESS_TOKEN = os.getenv("SHOPIFY_ACCESS_TOKEN", "YOUR_ACCESSTOKEN_HERE")

print("جاري الاتصال بـ Shopify وسحب الطلبات المعلقة...")
# Shopify Integration logic
