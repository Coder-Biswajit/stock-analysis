import pymysql
import os

def get_connection():
    try:
        conn = pymysql.connect(
            host=os.getenv("DB_HOST"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            database=os.getenv("DB_NAME"),
            port=int(os.getenv("DB_PORT")),
            ssl={"ssl": {}}
        )
        return conn

    except Exception as e:
        print("DB Error ❌:", e)   # ✅ print error in logs
        return None               # ✅ return None ONLY


# Test connection
if __name__ == "__main__":
    conn = get_connection()
    if conn:
        print("✅ Connected successfully!")
        conn.close()
    else:
        print("❌ Failed to connect")