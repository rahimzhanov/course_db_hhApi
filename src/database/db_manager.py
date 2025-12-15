# src/database/db_manager.py
import psycopg2
from psycopg2 import sql
from typing import List, Dict, Any, Optional, Tuple
import sys
import os

# Добавляем путь для импорта config
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

try:
    from config import DB_CONFIG
except ImportError:
    # Если config не найден, используем значения по умолчанию
    DB_CONFIG = {
        "host": "localhost",
        "database": "hh_vacancies",
        "user": "postgres",
        "password": "postgre",
        "port": 5432
    }


class DBManager:
    """
    Класс для управления базой данных PostgreSQL.
    Реализует все методы, требуемые по заданию.
    """

    def __init__(self, db_config: Dict[str, Any] = None):
        """
        Инициализация менеджера БД

        Args:
            db_config: Конфигурация подключения к БД
        """
        self.db_config = db_config or DB_CONFIG
        self.connection = None

    def connect(self) -> bool:
        """Установка соединения с БД"""
        try:
            self.connection = psycopg2.connect(**self.db_config)
            return True
        except Exception as e:
            print(f"Ошибка подключения к БД: {e}")
            return False

    def close(self):
        """Закрытие соединения с БД"""
        if self.connection:
            self.connection.close()
            self.connection = None

    def create_tables(self) -> bool:
        """
        Создание таблиц employers и vacancies в базе данных.
        Таблица vacancies связана с employers через FOREIGN KEY.

        Returns:
            True если успешно, False если ошибка
        """
        if not self.connect():
            return False

        try:
            with self.connection.cursor() as cursor:
                # Таблица employers (компании)
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS employers (
                        employer_id INTEGER PRIMARY KEY,
                        name VARCHAR(255) NOT NULL,
                        url VARCHAR(500),
                        open_vacancies INTEGER DEFAULT 0,
                        description TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)

                # Таблица vacancies (вакансии)
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS vacancies (
                        vacancy_id INTEGER PRIMARY KEY,
                        employer_id INTEGER REFERENCES employers(employer_id) ON DELETE CASCADE,
                        name VARCHAR(500) NOT NULL,
                        salary_from INTEGER,
                        salary_to INTEGER,
                        currency VARCHAR(10),
                        url VARCHAR(500),
                        experience VARCHAR(100),
                        employment VARCHAR(100),
                        schedule VARCHAR(100),
                        requirements TEXT,
                        responsibility TEXT,
                        published_at VARCHAR(50),
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)

                # Создание индексов для оптимизации запросов
                cursor.execute("""
                    CREATE INDEX IF NOT EXISTS idx_vacancies_employer_id 
                    ON vacancies(employer_id)
                """)
                cursor.execute("""
                    CREATE INDEX IF NOT EXISTS idx_vacancies_salary_from 
                    ON vacancies(salary_from) 
                    WHERE salary_from IS NOT NULL
                """)
                cursor.execute("""
                    CREATE INDEX IF NOT EXISTS idx_vacancies_salary_to 
                    ON vacancies(salary_to) 
                    WHERE salary_to IS NOT NULL
                """)
                cursor.execute("""
                    CREATE INDEX IF NOT EXISTS idx_vacancies_name 
                    ON vacancies(name)
                """)

                self.connection.commit()
                print("✅ Таблицы успешно созданы")
                return True

        except Exception as e:
            print(f"❌ Ошибка при создании таблиц: {e}")
            self.connection.rollback()
            return False
        finally:
            self.close()

    def insert_employer(self, employer_data: Dict[str, Any]) -> bool:
        """
        Вставка или обновление данных компании в таблицу employers

        Args:
            employer_data: Словарь с данными компании

        Returns:
            True если успешно, False если ошибка
        """
        if not self.connect():
            return False

        try:
            with self.connection.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO employers (employer_id, name, url, open_vacancies, description)
                    VALUES (%s, %s, %s, %s, %s)
                    ON CONFLICT (employer_id) DO UPDATE SET
                        name = EXCLUDED.name,
                        url = EXCLUDED.url,
                        open_vacancies = EXCLUDED.open_vacancies,
                        description = EXCLUDED.description
                """, (
                    employer_data['id'],
                    employer_data['name'],
                    employer_data['url'],
                    employer_data['open_vacancies'],
                    employer_data.get('description', '')
                ))

                self.connection.commit()
                return True

        except Exception as e:
            print(f"❌ Ошибка при сохранении компании {employer_data.get('id')}: {e}")
            self.connection.rollback()
            return False
        finally:
            self.close()

    def insert_vacancy(self, vacancy_data: Dict[str, Any]) -> bool:
        """
        Вставка или обновление данных вакансии в таблицу vacancies

        Args:
            vacancy_data: Словарь с данными вакансии

        Returns:
            True если успешно, False если ошибка
        """
        if not self.connect():
            return False

        try:
            with self.connection.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO vacancies 
                    (vacancy_id, employer_id, name, salary_from, salary_to, currency, url, 
                     experience, employment, schedule, requirements, responsibility, published_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (vacancy_id) DO UPDATE SET
                        name = EXCLUDED.name,
                        salary_from = EXCLUDED.salary_from,
                        salary_to = EXCLUDED.salary_to,
                        currency = EXCLUDED.currency,
                        url = EXCLUDED.url,
                        experience = EXCLUDED.experience,
                        employment = EXCLUDED.employment,
                        schedule = EXCLUDED.schedule,
                        requirements = EXCLUDED.requirements,
                        responsibility = EXCLUDED.responsibility,
                        published_at = EXCLUDED.published_at
                """, (
                    vacancy_data['id'],
                    vacancy_data['employer_id'],
                    vacancy_data['name'],
                    vacancy_data['salary_from'],
                    vacancy_data['salary_to'],
                    vacancy_data['currency'],
                    vacancy_data['url'],
                    vacancy_data['experience'],
                    vacancy_data['employment'],
                    vacancy_data['schedule'],
                    vacancy_data['requirements'],
                    vacancy_data['responsibility'],
                    vacancy_data['published_at']
                ))

                self.connection.commit()
                return True

        except Exception as e:
            print(f"❌ Ошибка при сохранении вакансии {vacancy_data.get('id')}: {e}")
            self.connection.rollback()
            return False
        finally:
            self.close()

    def clear_tables(self) -> bool:
        """
        Очистка всех таблиц (удаление данных)

        Returns:
            True если успешно, False если ошибка
        """
        if not self.connect():
            return False

        try:
            with self.connection.cursor() as cursor:
                cursor.execute("DELETE FROM vacancies")
                cursor.execute("DELETE FROM employers")
                self.connection.commit()
                print("✅ Таблицы очищены")
                return True

        except Exception as e:
            print(f"❌ Ошибка при очистке таблиц: {e}")
            self.connection.rollback()
            return False
        finally:
            self.close()


# Простой тест создания таблиц
def main():
    """Тестирование создания таблиц"""
    print("Создание таблиц в базе данных...")
    db = DBManager()

    if db.create_tables():
        print("✅ Таблицы успешно созданы!")

        # Проверяем структуру таблиц
        if db.connect():
            try:
                cursor = db.connection.cursor()

                # Проверяем таблицу employers
                cursor.execute("""
                    SELECT column_name, data_type 
                    FROM information_schema.columns 
                    WHERE table_name = 'employers'
                    ORDER BY ordinal_position
                """)
                print("\nСтруктура таблицы 'employers':")
                for col in cursor.fetchall():
                    print(f"  {col[0]}: {col[1]}")

                # Проверяем таблицу vacancies
                cursor.execute("""
                    SELECT column_name, data_type 
                    FROM information_schema.columns 
                    WHERE table_name = 'vacancies'
                    ORDER BY ordinal_position
                """)
                print("\nСтруктура таблицы 'vacancies':")
                for col in cursor.fetchall():
                    print(f"  {col[0]}: {col[1]}")

                cursor.close()

            except Exception as e:
                print(f"Ошибка при проверке структуры: {e}")
            finally:
                db.close()
    else:
        print("❌ Не удалось создать таблицы")


if __name__ == "__main__":
    main()