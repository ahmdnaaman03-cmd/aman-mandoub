import os
import requests
from flask import Flask, request, jsonify, redirect

app = Flask(__name__)

SHOPIFY_API_KEY = "اككتب_المفتاح_هنا_مرة_واحدة"
SHOPIFY_API_SECRET = os.environ.get('SHOPIFY_API_SECRET')
APP_URL = "https://ahmndnaaman03-cmd.pythonanywhere.com"

@app.route('/')
def home():
    return "Aman Mandoub Shopify App is Running!"

if __name__ == '__main__':
    app.run(port=5000)
