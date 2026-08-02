import requests
import time
import subprocess
import os
import signal

def test_system():
    # 1. تشغيل التطبيق
    print("🚀 بدء تشغيل التطبيق للاختبار...")
    process = subprocess.Popen(
        ['python3', 'app.py'],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        cwd=os.getcwd()
    )
    
    time.sleep(3)  # انتظر حتى يبدأ السيرفر
    
    base_url = "http://127.0.0.1:8000"
    
    try:
        # 2. اختبار الصفحة الرئيسية
        print("🔍 اختبار الصفحة الرئيسية...")
        response = requests.get(base_url)
        if response.status_code == 200:
            print("✅ الصفحة الرئيسية تعمل")
        else:
            print(f"❌ خطأ في الصفحة الرئيسية: {response.status_code}")
            
        # 3. اختبار البحث عن شحنة (1001)
        print("🔍 اختبار البحث عن شحنة 1001...")
        response = requests.post(base_url, data={'order_id': '1001'})
        if "أحمد محمد" in response.text and "data:image/png;base64" in response.text:
            print("✅ البحث عن الشحنة وتوليد QR يعمل")
        else:
            print("❌ خطأ في البحث عن الشحنة")
            
        # 4. اختبار صفحة الدفع للعميل
        print("🔍 اختبار صفحة الدفع للعميل...")
        pay_url = f"{base_url}/pay/client/1001"
        response = requests.get(pay_url)
        if "250.0" in response.text and "بوابة الدفع الآمن" in response.text:
            print("✅ صفحة الدفع للعميل تعمل")
        else:
            print("❌ خطأ في صفحة الدفع")
            
        # 5. اختبار تأكيد الدفع
        print("🔍 اختبار تأكيد الدفع...")
        confirm_url = f"{base_url}/pay/confirm/1001"
        response = requests.post(confirm_url, allow_redirects=True)
        if "تم دفع مبلغ 250.0 جنيه" in response.text:
            print("✅ تأكيد الدفع يعمل")
        else:
            print("❌ خطأ في تأكيد الدفع")
            
        # 6. اختبار التقرير
        print("🔍 اختبار التقرير اليومي...")
        response = requests.get(f"{base_url}/report")
        if "1001" in response.text and "تم الدفع" in response.text:
            print("✅ التقرير اليومي يعمل ويظهر حالة الدفع الصحيحة")
        else:
            print("❌ خطأ في التقرير")
            
    except Exception as e:
        print(f"❌ حدث خطأ أثناء الاختبار: {e}")
        
    finally:
        # إغلاق السيرفر
        print("🛑 إغلاق سيرفر الاختبار...")
        os.kill(process.pid, signal.SIGTERM)
        print("✨ انتهى الاختبار.")

if __name__ == "__main__":
    test_system()
