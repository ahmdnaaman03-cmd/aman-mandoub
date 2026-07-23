<p align="center">
  <img src="banner.png" alt="Aman El-Mandoob Banner" width="100%">
</p>



  <img src="static/og-image.png" alt="Aman El-Mandoob Logo" width="120">
</p>

# 🛡️ Aman El-Mandoob (أمان المندوب)
> **Instant Dynamic QR Payment & Dynamic Delivery Sync for Shopify & COD Merchants**

Aman El-Mandoob is a lightweight, secure dynamic payment gateway simulator and delivery confirmation tool. It bridges the gap between Cash on Delivery (COD) and instant digital payments for Shopify merchants and e-commerce delivery fleets.

---

## 🚀 Key Features

- **Shopify API Integration:** Seamlessly syncs orders and payment statuses directly with Shopify stores via Webhooks and REST API.
- **Dynamic QR Code Generation:** Generates unique, secure QR codes per order instantly.
- **Secure Tokenization:** Protects customer payment pages with single-use cryptographically generated tokens (`secrets.token_hex`).
- **Real-Time Payment Polling:** Mandoub (delivery agent) screen automatically updates upon payment completion without manual page refreshes.
- **Webhook Security (HMAC/SHA-256):** Simulates payment gateway webhooks using HMAC-SHA256 signatures to prevent fraud.
- **Mobile-First Design:** Fully responsive interface tailored for delivery agents on mobile devices.
---

## 🛍️ Shopify Merchant Workflow

1. Order placed on Shopify Store $\rightarrow$ Synced to Aman El-Mandoob.
2. Delivery Agent generates dynamic QR at customer location.
3. Customer scans & pays via mobile browser.
4. System updates Shopify Admin order status to **PAID** instantly via Webhook.

---

## 🛠️ Tech Stack

- **Backend:** Python / Flask
- **Integrations:** Shopify Admin API / Webhooks
- **Database:** SQLite3
- **Security:** Hashlib (SHA-256), Secrets Tokenization
- **Frontend:** HTML5, CSS3, JavaScript (Fetch API / Long-Polling)
- **Deployment:** PythonAnywhere / Linux Alpine (iSH)

---

## 👤 Author & Partnership
Developed by **Ahmed Noaman** — *Shopify Partner | Automated Payment & COD Solutions Developer.*


