import pymysql

def get_connection():
    try:
        conn = pymysql.connect(
            host="localhost",
            user="root",
            password="root",
            database="stock_app"
        )
        return conn
    except Exception as e:
        print("Error:", e)
        return None


if __name__ == "__main__":
    conn = get_connection()
    if conn:
        print("✅ Connected successfully!")
        conn.close()
    else:
        print("❌ Failed to connect")