import mysql.connector

try:
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="sun",
        auth_plugin="caching_sha2_password"
    )
    print("✅ MySQL connection successful")
    conn.close()
except Exception as e:
    print(" Error:", e)
