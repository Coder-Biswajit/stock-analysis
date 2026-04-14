import pymysql
import os

def get_connection():
    try:
        conn = pymysql.connect(
            host=os.getenv("gateway01.ap-southeast-1.prod.alicloud.tidbcloud.com"),
            user=os.getenv("hA15cqijeRCKvtm.root"),
            password=os.getenv("LOH1mQykOMKvAyEt"),
            database=os.getenv("test"),
            port=int(os.getenv("4000")),
            ssl={"ssl": {}}
        )
        return conn

    except Exception as e:
        print("DB Error ❌:", e)
        return None


# Test connection
if __name__ == "__main__":
    conn = get_connection()
    if conn:
        print("✅ Connected successfully!")
        conn.close()
    else:
        print("❌ Failed to connect")