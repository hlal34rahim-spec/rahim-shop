from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
import os

app = Flask(__name__)

# مفتاح سري لتأمين الجلسات (يمكنك تغييره لأي نص عشوائي)
app.secret_key = "rahim_super_secret_key_2026"

# معلومات الدخول الخاصة بك (يمكنك تغييرها كما تحب)
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "rahimpassword123"  # غيّر كلمة المرور هنا لتأمين حسابك

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "orders.db")

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
    CREATE TABLE IF NOT EXISTS orders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        phone TEXT,
        city TEXT,
        commune TEXT,
        delivery_type TEXT,
        total_price INTEGER
    )
    """)
    conn.commit()
    conn.close()

init_db()

PRODUCT_NAME = "منتج رائع"
PRODUCT_PRICE = 3500

@app.route("/")
def home():
    return render_template("index.html", product=PRODUCT_NAME, price=PRODUCT_PRICE)

@app.route("/order", methods=["POST"])
def order():
    name = request.form["name"]
    phone = request.form["phone"]
    city = request.form["city"]
    commune = request.form["commune"]
    delivery_type = request.form["delivery_type"]

    delivery_price = 500 if delivery_type == "home" else 300
    total = PRODUCT_PRICE + delivery_price

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        INSERT INTO orders (name, phone, city, commune, delivery_type, total_price)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (name, phone, city, commune, delivery_type, total))
    conn.commit()
    conn.close()

    message = f"""
🛒 طلب جديد
الاسم: {name}
الهاتف: {phone}
الولاية: {city}
البلدية: {commune}
التوصيل: {delivery_type}
المبلغ: {total} دج
"""
    whatsapp = f"https://wa.me/213XXXXXXXXX?text={message}"

    return f"""
    <div style="text-align:center; margin-top:50px; font-family:Arial;">
        <h2>✔ تم تسجيل الطلب بنجاح</h2>
        <a href="{whatsapp}" target="_blank" style="padding:10px 20px; background:#25D366; color:white; text-decoration:none; border-radius:5px; font-weight:bold;">📲 إرسال الطلب إلى WhatsApp</a>
        <br><br>
        <a href="/">رجوع للمتجر</a>
    </div>
    """

# صفحة تسجيل الدخول
@app.route("/login", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        
        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session["logged_in"] = True
            return redirect(url_for("admin"))
        else:
            error = "اسم المستخدم أو كلمة المرور خاطئة لخويا!"
            
    return render_template("login.html", error=error)

# صفحة تسجيل الخروج
@app.route("/logout")
def logout():
    session.pop("logged_in", None)
    return redirect(url_for("login"))

# صفحة الآدمين المحمية
@app.route("/admin")
def admin():
    # التحقق إذا كان الآدمين مسجل دخوله فعلاً
    if not session.get("logged_in"):
        return redirect(url_for("login"))
        
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT * FROM orders ORDER BY id DESC")
    orders = c.fetchall()
    conn.close()
    return render_template("admin.html", orders=orders)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)