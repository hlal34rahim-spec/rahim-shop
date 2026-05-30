from flask import Flask, render_template, request
import sqlite3

app = Flask(__name__)

# قاعدة البيانات
def init_db():
    conn = sqlite3.connect("orders.db")
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

    conn = sqlite3.connect("orders.db")
    c = conn.cursor()
    c.execute("""
        INSERT INTO orders (name, phone, city, commune, delivery_type, total_price)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (name, phone, city, commune, delivery_type, total))
    conn.commit()
    conn.close()

    message = f"""
🛒 طلب جديد
----------------
الاسم: {name}
الهاتف: {phone}
الولاية: {city}
البلدية: {commune}
التوصيل: {delivery_type}
المبلغ: {total} دج
"""

    whatsapp = f"https://wa.me/213XXXXXXXXX?text={message}"

    return f"""
    <h2>✔ تم تسجيل الطلب بنجاح</h2>
    <a href="{whatsapp}" target="_blank">📲 إرسال الطلب إلى WhatsApp</a>
    <br><br>
    <a href="/">رجوع</a>
    """

@app.route("/admin")
def admin():
    conn = sqlite3.connect("orders.db")
    c = conn.cursor()
    c.execute("SELECT * FROM orders ORDER BY id DESC")
    orders = c.fetchall()
    conn.close()

    return render_template("admin.html", orders=orders)

if __name__ == "__main__":
    print("SERVER STARTED")
    app.run(host="0.0.0.0", port=10000)