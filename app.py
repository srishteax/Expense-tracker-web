from flask import Flask, render_template, request, redirect, session
import sqlite3
from datetime import datetime

app = Flask(__name__)
app.secret_key = "secret123"

def get_db():
    return sqlite3.connect("expense_tracker.db")

# Create tables
with get_db() as conn:
    cur = conn.cursor()
    cur.execute("""CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT,
        budget REAL
    )""")
    cur.execute("""CREATE TABLE IF NOT EXISTS expenses(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        date TEXT,
        amount REAL,
        category TEXT
    )""")
    conn.commit()

@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        u = request.form["username"]
        p = request.form["password"]

        conn = get_db()
        cur = conn.cursor()
        cur.execute("SELECT * FROM users WHERE username=? AND password=?", (u, p))
        user = cur.fetchone()

        if user:
            session["user_id"] = user[0]
            return redirect("/dashboard")

    return render_template("login.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        u = request.form["username"]
        p = request.form["password"]
        b = request.form["budget"]

        conn = get_db()
        cur = conn.cursor()
        cur.execute("INSERT INTO users(username,password,budget) VALUES(?,?,?)", (u,p,b))
        conn.commit()
        return redirect("/")

    return render_template("register.html")

@app.route("/dashboard", methods=["GET", "POST"])
def dashboard():
    if "user_id" not in session:
        return redirect("/")

    conn = get_db()
    cur = conn.cursor()

    if request.method == "POST":
        amt = request.form["amount"]
        cat = request.form["category"]
        date = datetime.now().strftime("%Y-%m-%d")

        cur.execute("INSERT INTO expenses(user_id,date,amount,category) VALUES(?,?,?,?)",
                    (session["user_id"], date, amt, cat))
        conn.commit()

    cur.execute("SELECT category, SUM(amount) FROM expenses WHERE user_id=? GROUP BY category",
                (session["user_id"],))
    data = cur.fetchall()

    return render_template("dashboard.html", data=data)

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

if __name__ == "__main__":
    app.run(debug=True)
