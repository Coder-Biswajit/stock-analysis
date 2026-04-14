from flask import Flask, render_template, request, redirect, session
from db import get_connection
from werkzeug.security import generate_password_hash, check_password_hash
import pymysql
import yfinance as yf
from analysis import get_signal
from analysis import (
    get_stock_data,
    plot_closing_price,
    plot_moving_averages,
    plot_daily_returns,
    plot_volume,
    get_summary_stats
)

app = Flask(__name__)

# ✅ Secret key (required)
app.secret_key = "supersecret123"


# ================= HOME =================
@app.route("/")
def home():
    return render_template("index.html")


# ================= REGISTER =================
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        # ✅ Hash password
        hashed_password = generate_password_hash(password)

        conn = get_connection()
        if conn is None:
            return "DB Error ❌"

        cursor = conn.cursor(pymysql.cursors.DictCursor)

        # 🔍 Check if user exists
        cursor.execute("SELECT * FROM users WHERE username=%s", (username,))
        existing_user = cursor.fetchone()

        if existing_user:
            conn.close()
            return "Username already exists ❌"

        # ✅ Insert user
        cursor.execute(
            "INSERT INTO users (username, password) VALUES (%s, %s)",
            (username, hashed_password)
        )

        conn.commit()
        conn.close()

        return redirect("/login")

    return render_template("register.html")


# ================= LOGIN =================
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        conn = get_connection()
        if conn is None:
            return "DB Error ❌"

        cursor = conn.cursor(pymysql.cursors.DictCursor)

        # 🔍 Fetch user
        cursor.execute("SELECT * FROM users WHERE username=%s", (username,))
        user = cursor.fetchone()

        conn.close()

        # ✅ Check password (IMPORTANT FIX)
        if user and check_password_hash(user["password"], password):
            session["user_id"] = user["id"]
            session["username"] = user["username"]
            return redirect("/dashboard")

        else:
            return "Invalid username or password ❌"

    return render_template("login.html")


# ================= LOGOUT =================
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

#============dashboard====================
@app.route("/dashboard")
def dashboard():
    
    # Step 1 — check if user is logged in
    if "user_id" not in session:
        return redirect("/login")

    # Step 2 — get user_id from session
    user_id = session["user_id"]

    # Step 3 — connect to DB
    conn = get_connection()
    if conn is None:
        return "DB Error ❌"

    cursor = conn.cursor(pymysql.cursors.DictCursor)

    # Step 4 — fetch all tickers for this user
    query = "SELECT ticker FROM watchlist WHERE user_id=%s"
    cursor.execute(query, (user_id,))
    tickers = cursor.fetchall()

    # Step 5 — pass tickers to dashboard.html
    conn.close()

    # Step 6 — return template
    return render_template("dashboard.html", tickers=tickers)

@app.route("/add_stock", methods=["POST"])
def add_stock():

    # Step 1 — check if user is logged in
    if "user_id" not in session:
        return redirect("/login")

    # Step 2 — get user_id
    user_id = session["user_id"]

    # Step 3 — get ticker
    ticker = request.form["ticker"].upper()

    # 🔥 Step 4 — validate ticker using yfinance
    stock = yf.Ticker(ticker)
    data = stock.history(period="1d")

    if data.empty:
        return "Invalid ticker ❌"

    # Step 5 — connect DB
    conn = get_connection()
    cursor = conn.cursor()

    # Step 6 — check duplicate
    cursor.execute(
        "SELECT * FROM watchlist WHERE user_id=%s AND ticker=%s",
        (user_id, ticker)
    )
    existing = cursor.fetchone()

    if existing:
        conn.close()
        return "Ticker already in watchlist ⚠️"

    # Step 7 — insert
    cursor.execute(
        "INSERT INTO watchlist (user_id, ticker) VALUES (%s, %s)",
        (user_id, ticker)
    )

    conn.commit()
    conn.close()

    # Step 8 — redirect
    return redirect("/dashboard")

@app.route("/remove_stock", methods=["POST"])
def remove_stock():

    if "user_id" not in session:
        return redirect("/login")

    user_id = session["user_id"]
    ticker = request.form["ticker"]

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "DELETE FROM watchlist WHERE user_id=%s AND ticker=%s",
        (user_id, ticker)
    )

    conn.commit()
    conn.close()

    return redirect("/dashboard")


@app.route("/stock/<ticker>")
def stock_detail(ticker):

    # Step 1 — check login
    if "user_id" not in session:
        return redirect("/login")

    # Step 2 — get stock data
    df = get_stock_data(ticker)

    # Step 3 — handle invalid ticker
    if df is None or df.empty:
        return "Invalid ticker ❌"

    # Step 4 — generate charts
    close_chart = plot_closing_price(df, ticker)
    ma_chart = plot_moving_averages(df, ticker)
    returns_chart = plot_daily_returns(df, ticker)
    volume_chart = plot_volume(df, ticker)

    # 🔥 Step 5 — BUY/SELL SIGNAL (NEW)
    signal = get_signal(df)

    # Step 6 — summary stats
    stats = get_summary_stats(df, ticker)

    # 👉 Convert to relative path for Flask static
    close_chart = close_chart.replace("static/", "")
    ma_chart = ma_chart.replace("static/", "")
    returns_chart = returns_chart.replace("static/", "")
    volume_chart = volume_chart.replace("static/", "")

    # Step 7 — render template
    return render_template(
        "stock_detail.html",
        ticker=ticker,
        close_chart=close_chart,
        ma_chart=ma_chart,
        returns_chart=returns_chart,
        volume_chart=volume_chart,
        stats=stats,
        signal=signal 
    )


# ================= RUN =================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)