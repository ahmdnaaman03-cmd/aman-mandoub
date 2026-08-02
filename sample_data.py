#!/usr/bin/env python3
"""
ملف إضافة البيانات التجريبية لقاعدة البيانات
قم بتشغيل هذا الملف مرة واحدة لتحميل البيانات الأولية
"""

import sqlite3
import os

DB_NAME = 'secure_delivery.db'

def load_sample_data():
    """تحميل بيانات تجريبية"""
    
    # البيانات التجريبية
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
    
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    try:
        for order_id, customer_name, price in sample_orders:
            cursor.execute(
                'INSERT OR IGNORE INTO orders (order_id, customer_name, price, status) VALUES (?, ?, ?, ?)',
                (order_id, customer_name, price, 'pending')
            )
        
        conn.commit()
        print(f"✅ تم تحميل {len(sample_orders)} طلب تجريبي بنجاح!")
        
        # عرض البيانات المضافة
        cursor.execute('SELECT * FROM orders')
        rows = cursor.fetchall()
        print(f"\nإجمالي الطلبات في النظام: {len(rows)}")
        for row in rows:
            print(f"  - الشحنة {row[1]}: {row[2]} ({row[3]} ج.م)")
    
    except Exception as e:
        print(f"❌ خطأ: {e}")
    
    finally:
        conn.close()

if __name__ == '__main__':
    load_sample_data()
