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

    # ДОБАВЬТЕ ЭТИ МЕТОДЫ В КЛАСС DBManager

    def get_companies_and_vacancies_count(self) -> List[Tuple]:
        """
        Получает список всех компаний и количество вакансий у каждой компании.

        Returns:
            Список кортежей (название_компании, количество_вакансий)
        """
        if not self.connect():
            return []

        try:
            with self.connection.cursor() as cursor:
                cursor.execute("""
                    SELECT e.name, COUNT(v.vacancy_id) as vacancy_count
                    FROM employers e
                    LEFT JOIN vacancies v ON e.employer_id = v.employer_id
                    GROUP BY e.employer_id, e.name
                    ORDER BY vacancy_count DESC
                """)
                return cursor.fetchall()

        except Exception as e:
            print(f"Ошибка при получении списка компаний: {e}")
            return []
        finally:
            self.close()

    def get_all_vacancies(self) -> List[Tuple]:
        """
        Получает список всех вакансий с указанием названия компании,
        названия вакансии, зарплаты и ссылки на вакансию.

        Returns:
            Список кортежей (компания, вакансия, зарплата_от, зарплата_до, валюта, ссылка)
        """
        if not self.connect():
            return []

        try:
            with self.connection.cursor() as cursor:
                cursor.execute("""
                    SELECT 
                        e.name as company_name,
                        v.name as vacancy_name,
                        v.salary_from,
                        v.salary_to,
                        v.currency,
                        v.url
                    FROM vacancies v
                    JOIN employers e ON v.employer_id = e.employer_id
                    ORDER BY e.name, v.name
                """)
                return cursor.fetchall()

        except Exception as e:
            print(f"Ошибка при получении списка вакансий: {e}")
            return []
        finally:
            self.close()

    def get_avg_salary(self) -> float:
        """
        Получает среднюю зарплату по вакансиям.
        Учитывает обе границы зарплаты (from и to).

        Returns:
            Средняя зарплата (float). Возвращает 0.0, если нет вакансий с зарплатой.
        """
        if not self.connect():
            return 0.0

        try:
            with self.connection.cursor() as cursor:
                # Исправленный расчет средней зарплаты для PostgreSQL
                cursor.execute("""
                    WITH salary_data AS (
                        SELECT 
                            CASE 
                                WHEN salary_from IS NOT NULL AND salary_to IS NOT NULL 
                                    THEN (salary_from::float + salary_to::float) / 2.0
                                WHEN salary_from IS NOT NULL THEN salary_from::float
                                WHEN salary_to IS NOT NULL THEN salary_to::float
                                ELSE NULL
                            END as calculated_salary
                        FROM vacancies
                        WHERE salary_from IS NOT NULL OR salary_to IS NOT NULL
                    )
                    SELECT AVG(calculated_salary)::numeric(10,2)
                    FROM salary_data
                    WHERE calculated_salary IS NOT NULL
                """)
                result = cursor.fetchone()
                return float(result[0]) if result and result[0] else 0.0

        except Exception as e:
            print(f"Ошибка при расчете средней зарплаты: {e}")
            return 0.0
        finally:
            self.close()

    def get_vacancies_with_higher_salary(self) -> List[Tuple]:
        """
        Получает список всех вакансий, у которых зарплата ВЫШЕ средней по всем вакансиям.

        Returns:
            Список кортежей (компания, вакансия, зарплата_от, зарплата_до, валюта, ссылка)
        """
        avg_salary = self.get_avg_salary()
        if avg_salary == 0:
            print(f"Средняя зарплата равна 0 или не удалось ее рассчитать")
            return []

        if not self.connect():
            return []

        try:
            with self.connection.cursor() as cursor:
                # Упрощенная и более точная логика
                cursor.execute("""
                    WITH vacancy_salaries AS (
                        SELECT 
                            v.vacancy_id,
                            v.employer_id,
                            v.name,
                            v.salary_from,
                            v.salary_to,
                            v.currency,
                            v.url,
                            e.name as company_name,
                            CASE 
                                WHEN v.salary_from IS NOT NULL AND v.salary_to IS NOT NULL 
                                    THEN (v.salary_from::float + v.salary_to::float) / 2.0
                                WHEN v.salary_from IS NOT NULL THEN v.salary_from::float
                                WHEN v.salary_to IS NOT NULL THEN v.salary_to::float
                                ELSE NULL
                            END as avg_vacancy_salary
                        FROM vacancies v
                        JOIN employers e ON v.employer_id = e.employer_id
                        WHERE v.salary_from IS NOT NULL OR v.salary_to IS NOT NULL
                    )
                    SELECT 
                        company_name,
                        name,
                        salary_from,
                        salary_to,
                        currency,
                        url
                    FROM vacancy_salaries
                    WHERE avg_vacancy_salary > %s
                    ORDER BY avg_vacancy_salary DESC
                """, (avg_salary,))

                vacancies = cursor.fetchall()
                print(f"Найдено вакансий с зарплатой выше средней ({avg_salary:.0f} руб.): {len(vacancies)}")
                return vacancies

        except Exception as e:
            print(f"Ошибка при поиске вакансий с высокой зарплатой: {e}")
            return []
        finally:
            self.close()

    def get_vacancies_with_keyword(self, keyword: str) -> List[Tuple]:
        """
        Получает список всех вакансий, в названии которых содержатся переданные слова.
        Реализует поиск по нескольким ключевым словам (разделенным пробелом).

        Args:
            keyword: Ключевое слово или несколько слов для поиска

        Returns:
            Список кортежей (компания, вакансия, зарплата_от, зарплата_до, валюта, ссылка)
        """
        if not keyword or not keyword.strip():
            print("Ключевое слово не указано")
            return []

        if not self.connect():
            return []

        try:
            with self.connection.cursor() as cursor:
                # Разбиваем фразу на отдельные слова
                keywords = keyword.strip().lower().split()

                # Создаем условие LIKE для каждого слова
                conditions = []
                params = []

                for kw in keywords:
                    conditions.append("LOWER(v.name) LIKE %s")
                    params.append(f'%{kw}%')

                # Объединяем условия через AND (ищем все слова)
                where_clause = " AND ".join(conditions)

                query = f"""
                    SELECT 
                        e.name as company_name,
                        v.name as vacancy_name,
                        v.salary_from,
                        v.salary_to,
                        v.currency,
                        v.url
                    FROM vacancies v
                    JOIN employers e ON v.employer_id = e.employer_id
                    WHERE {where_clause}
                    ORDER BY e.name, v.name
                """

                cursor.execute(query, params)
                vacancies = cursor.fetchall()
                print(f"Найдено вакансий по ключевому слову '{keyword}': {len(vacancies)}")
                return vacancies

        except Exception as e:
            print(f"Ошибка при поиске вакансий по ключевому слову: {e}")
            return []
        finally:
            self.close()

    def get_vacancies_with_salary_range(self, min_salary: int = None, max_salary: int = None) -> List[Tuple]:
        """
        Получает вакансии в указанном диапазоне зарплат.

        Args:
            min_salary: Минимальная зарплата
            max_salary: Максимальная зарплата

        Returns:
            Список вакансий в указанном диапазоне
        """
        if not self.connect():
            return []

        try:
            with self.connection.cursor() as cursor:
                # Более точная логика для поиска по диапазону
                query = """
                    SELECT 
                        e.name as company_name,
                        v.name as vacancy_name,
                        v.salary_from,
                        v.salary_to,
                        v.currency,
                        v.url
                    FROM vacancies v
                    JOIN employers e ON v.employer_id = e.employer_id
                    WHERE (v.salary_from IS NOT NULL OR v.salary_to IS NOT NULL)
                """

                params = []

                if min_salary is not None:
                    query += " AND (v.salary_to >= %s OR v.salary_from >= %s)"
                    params.extend([min_salary, min_salary])

                if max_salary is not None:
                    query += " AND (v.salary_from <= %s OR v.salary_to <= %s OR v.salary_from IS NULL)"
                    params.extend([max_salary, max_salary])

                query += " ORDER BY COALESCE(v.salary_from, v.salary_to, 0) DESC"

                cursor.execute(query, params)
                return cursor.fetchall()

        except Exception as e:
            print(f"Ошибка при поиске вакансий по диапазону зарплат: {e}")
            return []
        finally:
            self.close()

    def get_top_companies_by_vacancies(self, limit: int = 10) -> List[Tuple]:
        """
        Получает топ компаний по количеству вакансий.

        Args:
            limit: Количество компаний в топе

        Returns:
            Список компаний с количеством вакансий
        """
        if not self.connect():
            return []

        try:
            with self.connection.cursor() as cursor:
                cursor.execute("""
                    SELECT 
                        e.name,
                        COUNT(v.vacancy_id) as vacancy_count,
                        ROUND(COUNT(v.vacancy_id) * 100.0 / (SELECT COUNT(*) FROM vacancies), 2) as percentage
                    FROM employers e
                    LEFT JOIN vacancies v ON e.employer_id = v.employer_id
                    GROUP BY e.employer_id, e.name
                    ORDER BY vacancy_count DESC
                    LIMIT %s
                """, (limit,))
                return cursor.fetchall()

        except Exception as e:
            print(f"Ошибка при получении топ компаний: {e}")
            return []
        finally:
            self.close()

    def get_statistics(self) -> Dict[str, Any]:
        """
        Получает общую статистику по базе данных.

        Returns:
            Словарь со статистикой
        """
        stats = {}

        if not self.connect():
            return stats

        try:
            with self.connection.cursor() as cursor:
                # Общее количество вакансий
                cursor.execute("SELECT COUNT(*) FROM vacancies")
                stats['total_vacancies'] = cursor.fetchone()[0]

                # Количество компаний
                cursor.execute("SELECT COUNT(*) FROM employers")
                stats['total_companies'] = cursor.fetchone()[0]

                # Вакансий с зарплатой
                cursor.execute("SELECT COUNT(*) FROM vacancies WHERE salary_from IS NOT NULL OR salary_to IS NOT NULL")
                stats['vacancies_with_salary'] = cursor.fetchone()[0]

                # Средняя зарплата
                stats['avg_salary'] = self.get_avg_salary()

                # Самые популярные вакансии
                cursor.execute("""
                    SELECT name, COUNT(*) as count
                    FROM vacancies
                    GROUP BY name
                    ORDER BY count DESC
                    LIMIT 5
                """)
                stats['top_positions'] = cursor.fetchall()

                # Компании с наибольшим количеством вакансий
                stats['top_companies'] = self.get_top_companies_by_vacancies(5)

                return stats

        except Exception as e:
            print(f"Ошибка при получении статистики: {e}")
            return stats
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