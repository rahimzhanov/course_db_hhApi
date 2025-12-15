# test_connection.py
import psycopg2

try:
    conn = psycopg2.connect(
        host="localhost",
        database="postgres",  # подключаемся к стандартной БД
        user="postgres",
        password="postgre",  # ваш пароль
        port=5432
    )

    cursor = conn.cursor()

    # Проверяем версию PostgreSQL
    cursor.execute("SELECT version();")
    version = cursor.fetchone()
    print(f"✅ Подключение успешно!")
    print(f"Версия PostgreSQL: {version[0]}")

    # Проверяем существующие базы данных
    cursor.execute("SELECT datname FROM pg_database;")
    databases = cursor.fetchall()
    print("\nСуществующие базы данных:")
    for db in databases:
        print(f"  - {db[0]}")

    cursor.close()
    conn.close()

except Exception as e:
    print(f"❌ Ошибка подключения: {e}")