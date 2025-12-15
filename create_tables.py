# create_tables.py
import sys
import os

# Настройка путей
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

from src.database.db_manager import DBManager


def main():
    print("Создание таблиц в базе данных PostgreSQL")
    print("=" * 50)

    # Инициализируем DBManager
    db_manager = DBManager()

    # Создаем таблицы
    print("\n1. Создание таблиц employers и vacancies...")
    success = db_manager.create_tables()

    if success:
        print("✅ Таблицы успешно созданы!")

        # Дополнительная проверка
        print("\n2. Проверка структуры БД...")

        if db_manager.connect():
            try:
                cursor = db_manager.connection.cursor()

                # Проверяем существование таблиц
                cursor.execute("""
                    SELECT table_name 
                    FROM information_schema.tables 
                    WHERE table_schema = 'public'
                    AND table_name IN ('employers', 'vacancies')
                """)

                tables = cursor.fetchall()
                print(f"   Найдено таблиц: {len(tables)}")

                for table in tables:
                    print(f"   - {table[0]}")

                # Проверяем foreign key связь
                cursor.execute("""
                    SELECT
                        tc.table_name, 
                        kcu.column_name, 
                        ccu.table_name AS foreign_table_name,
                        ccu.column_name AS foreign_column_name 
                    FROM 
                        information_schema.table_constraints AS tc 
                        JOIN information_schema.key_column_usage AS kcu
                          ON tc.constraint_name = kcu.constraint_name
                        JOIN information_schema.constraint_column_usage AS ccu
                          ON ccu.constraint_name = tc.constraint_name
                    WHERE tc.constraint_type = 'FOREIGN KEY' 
                    AND tc.table_name = 'vacancies'
                """)

                fk_info = cursor.fetchone()
                if fk_info:
                    print(f"\n   Foreign Key связь: {fk_info[1]} -> {fk_info[2]}.{fk_info[3]}")
                    print("   ✅ Связь между таблицами установлена")

                cursor.close()

            except Exception as e:
                print(f"   ❌ Ошибка при проверке: {e}")
            finally:
                db_manager.close()
    else:
        print("❌ Не удалось создать таблицы. Проверьте:")
        print("   - Запущен ли PostgreSQL")
        print("   - Правильность данных в .env файле")
        print("   - Существует ли база данных 'hh_vacancies'")

    print("\n" + "=" * 50)
    print("Создание таблиц завершено!")


if __name__ == "__main__":
    main()