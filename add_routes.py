with open('app.py', 'r') as f:
    content = f.read()

# المسارات الجديدة المطلوبة
new_routes = """
@app.route('/terms')
def terms():
    return render_template('terms.html')

@app.route('/support')
def support():
    return render_template('support.html')
"""

# البحث عن مكان سطر التشغيل أو إضافة المسارات قبله
target = "if __name__ == '__main__':"
if target in content and "/terms" not in content:
    updated_content = content.replace(target, new_routes + "\n" + target)
    with open('app.py', 'w') as f:
        f.write(updated_content)
    print("✅ Successfully injected terms and support routes before __main__")
else:
    print("⚠️ Target not found or routes already exist.")
