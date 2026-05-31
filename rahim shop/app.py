from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import sqlite3
import os

app = Flask(__name__)

app.secret_key = "rahim_super_secret_key_2026"

ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "rahimpassword123"

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
        total_price INTEGER,
        status TEXT DEFAULT 'قيد الانتظار'
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
        INSERT INTO orders (name, phone, city, commune, delivery_type, total_price, status)
        VALUES (?, ?, ?, ?, ?, ?, 'قيد الانتظار')
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
    <div style="text-align:center; margin-top:50px; font-family:Arial, sans-serif;">
        <h2>✔ تم تسجيل الطلب بنجاح</h2>
        <a href="{whatsapp}" target="_blank" style="padding:10px 20px; background:#25D366; color:white; text-decoration:none; border-radius:5px; font-weight:bold;">📲 إرسال الطلب إلى WhatsApp</a>
        <br><br>
        <a href="/">رجوع للمتجر</a>
    </div>
    """

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

@app.route("/logout")
def logout():
    session.pop("logged_in", None)
    return redirect(url_for("login"))

@app.route("/admin")
def admin():
    if not session.get("logged_in"):
        return redirect(url_for("login"))
        
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT * FROM orders ORDER BY id DESC")
    orders = c.fetchall()
    
    c.execute("SELECT SUM(total_price) FROM orders WHERE status = 'تم التوصيل'")
    total_revenue = c.fetchone()[0] or 0
    
    conn.close()
    return render_template("admin.html", orders=orders, total_revenue=total_revenue)

# مسار خاص للتحقق التلقائي من عدد الطلبات (يستخدمه الجافاسكريبت في الخلفية)
@app.route("/check_orders_count")
def check_orders_count():
    if not session.get("logged_in"):
        return jsonify({"count": 0})
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM orders")
    count = c.fetchone()[0]
    conn.close()
    return jsonify({"count": count})

@app.route("/update_status/<int:order_id>", methods=["POST"])
def update_status(order_id):
    if not session.get("logged_in"):
        return redirect(url_for("login"))
    
    new_status = request.form["status"]
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("UPDATE orders SET status = ? WHERE id = ?", (new_status, order_id))
    conn.commit()
    conn.close()
    return redirect(url_for("admin"))

@app.route("/delete_order/<int:order_id>", methods=["POST"])
def delete_order(order_id):
    if not session.get("logged_in"):
        return redirect(url_for("login"))
        
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("DELETE FROM orders WHERE id = ?", (order_id,))
    conn.commit()
    conn.close()
    return redirect(url_for("admin"))

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)