#!/usr/bin/env python3
"""
سكريبت تهيئة قاعدة البيانات والبيانات التجريبية
"""

import sqlite3
import os

DB_NAME = 'secure_delivery.db'

def init_database():
    """إنشاء جداول قاعدة البيانات"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # إنشاء جدول الطلبات
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
    
    # إنشاء جدول المتاجر (للتكامل مع Shopify)
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
    print("✅ تم إنشاء جداول قاعدة البيانات")
    
    # إضافة البيانات التجريبية
    sample_orders = [
        ('1001', 'أحمد محمد', 250.00),
        ('1002', 'فاطمة علي', 150.00),
        ('1003', 'محمود حسن', 500.00),
        ('1004', 'نور الدين', 300.00),
        ('1005', 'ليلى إبراهيم', 200.00),
        ('1006', 'عمر خالد', 450.00),
        ('1007', 'سارة يوسف', 175.00),
        ('1008', 'خالد أحمد', 600.00),
    ]
    
    try:
        for order_id, customer_name, price in sample_orders:
            cursor.execute(
                'INSERT OR IGNORE INTO orders (order_id, customer_name, price, status) VALUES (?, ?, ?, ?)',
                (order_id, customer_name, price, 'pending')
            )
        
        conn.commit()
        print(f"✅ تم تحميل {len(sample_orders)} طلب تجريبي")
        
        # عرض البيانات
        cursor.execute('SELECT * FROM orders')
        rows = cursor.fetchall()
        print(f"\n📊 الطلبات في النظام:")
        for row in rows:
            print(f"  - الشحنة {row[1]}: {row[2]} ({row[3]} ج.م) - الحالة: {row[4]}")
    
    except Exception as e:
        print(f"❌ خطأ: {e}")
    
    finally:
        conn.close()

if __name__ == '__main__':
    init_database()
