# create_database.py
import psycopg2
from psycopg2 import sql


def create_database():
    try:
        # Подключаемся к стандартной БД postgres
        conn = psycopg2.connect(
            host="localhost",
            database="postgres",
            user="postgres",
            password="postgre",
            port=5432
        )
        conn.autocommit = True  # Важно для создания БД
        cursor = conn.cursor()

        # Имя базы данных для проекта
        db_name = "hh_vacancies"

        # Проверяем, существует ли уже база данных
        cursor.execute("SELECT 1 FROM pg_database WHERE datname = %s", (db_name,))
        exists = cursor.fetchone()

        if exists:
            print(f"База данных '{db_name}' уже существует.")
        else:
            # Создаем новую базу данных
            cursor.execute(sql.SQL("CREATE DATABASE {}").format(
                sql.Identifier(db_name)
            ))
            print(f"✅ База данных '{db_name}' успешно создана!")

        cursor.close()
        conn.close()

        # Тестируем подключение к новой БД
        test_new_db(db_name)

    except Exception as e:
        print(f"❌ Ошибка: {e}")


def test_new_db(db_name):
    try:
        conn = psycopg2.connect(
            host="localhost",
            database=db_name,  # подключаемся к новой БД
            user="postgres",
            password="postgre",
            port=5432
        )
        print(f"✅ Подключение к базе '{db_name}' успешно!")

        cursor = conn.cursor()
        # Создаем простую тестовую таблицу
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS test_table (
                id SERIAL PRIMARY KEY,
                test_text VARCHAR(100)
            )
        """)
        print("✅ Тестовая таблица создана")

        cursor.execute("INSERT INTO test_table (test_text) VALUES (%s)",
                       ("Тестовое подключение работает!",))
        print("✅ Тестовая запись добавлена")

        conn.commit()
        cursor.close()
        conn.close()

    except Exception as e:
        print(f"❌ Ошибка при тестировании БД: {e}")


if __name__ == "__main__":
    create_database()