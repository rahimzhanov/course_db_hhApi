# main.py
"""
Главный модуль проекта - точка входа.
Предоставляет пользовательский интерфейс для работы с базой данных вакансий.
"""
import sys
import os
from typing import List, Tuple

# Настройка путей
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

from src.database.db_manager import DBManager


class UserInterface:
    """Класс для взаимодействия с пользователем"""

    def __init__(self):
        self.db_manager = DBManager()
        self.running = True

    def display_menu(self):
        """Отображает главное меню"""
        print("\n" + "=" * 60)
        print("📊 АНАЛИТИКА ВАКАНСИЙ С HH.RU")
        print("=" * 60)
        print("1. 📋 Список всех компаний и количество вакансий")
        print("2. 🔍 Показать все вакансии")
        print("3. 💰 Узнать среднюю зарплату")
        print("4. 🚀 Найти вакансии с зарплатой выше средней")
        print("5. 🔎 Поиск вакансий по ключевому слову")
        print("6. 📈 Статистика базы данных")
        print("7. 🎯 Поиск по диапазону зарплат")
        print("8. 🏆 Топ компаний по вакансиям")
        print("0. ❌ Выход")
        print("=" * 60)

    def format_salary(self, salary_from, salary_to, currency) -> str:
        """Форматирует зарплату для отображения"""
        if salary_from is None and salary_to is None:
            return "Не указана"

        currency_symbol = ""
        if currency:
            currency_symbol = f" {currency}"

        if salary_from is not None and salary_to is not None:
            return f"{salary_from:,} - {salary_to:,}{currency_symbol}".replace(",", " ")
        elif salary_from is not None:
            return f"от {salary_from:,}{currency_symbol}".replace(",", " ")
        elif salary_to is not None:
            return f"до {salary_to:,}{currency_symbol}".replace(",", " ")

        return "Не указана"

    def print_vacancies(self, vacancies: List[Tuple], title: str, limit: int = 10):
        """Печатает список вакансий в читаемом формате"""
        print(f"\n{title} ({len(vacancies)} найдено):")
        print("-" * 80)

        if not vacancies:
            print("😔 Вакансий не найдено")
            return

        for i, vac in enumerate(vacancies[:limit], 1):
            # Определяем структуру кортежа в зависимости от метода
            if len(vac) >= 6:  # Стандартный формат
                company, name, salary_from, salary_to, currency, url = vac[:6]
                salary_str = self.format_salary(salary_from, salary_to, currency)

                print(f"{i}. 🏢 {company}")
                print(f"   📝 {name}")
                print(f"   💰 {salary_str}")
                print(f"   🔗 {url}")
            elif len(vac) == 2:  # Для списка компаний
                company, count = vac
                print(f"{i}. 🏢 {company}: {count} вакансий")

            if i < min(len(vacancies), limit):
                print("   " + "-" * 40)

        if len(vacancies) > limit:
            print(f"\n📊 ... и еще {len(vacancies) - limit} вакансий")

    def handle_companies_and_vacancies_count(self):
        """Обработчик для пункта 1"""
        print("\n" + "=" * 60)
        print("📊 СПИСОК КОМПАНИЙ И КОЛИЧЕСТВО ВАКАНСИЙ")
        print("=" * 60)

        companies = self.db_manager.get_companies_and_vacancies_count()

        if not companies:
            print("😔 Не удалось получить данные о компаниях")
            return

        total_vacancies = sum(count for _, count in companies)

        print(f"Всего компаний: {len(companies)}")
        print(f"Всего вакансий: {total_vacancies}")
        print("\n" + "-" * 60)

        for i, (company, count) in enumerate(companies, 1):
            percentage = (count / total_vacancies * 100) if total_vacancies > 0 else 0
            print(f"{i:2}. {company:30} {count:4} вакансий ({percentage:5.1f}%)")

        input("\n📝 Нажмите Enter для продолжения...")

    def handle_all_vacancies(self):
        """Обработчик для пункта 2"""
        print("\n" + "=" * 60)
        print("🔍 ВСЕ ВАКАНСИИ В БАЗЕ ДАННЫХ")
        print("=" * 60)

        vacancies = self.db_manager.get_all_vacancies()

        if not vacancies:
            print("😔 В базе данных нет вакансий")
            return

        print(f"Всего вакансий в базе: {len(vacancies)}")

        # Спрашиваем сколько показать
        try:
            limit = int(input("\nСколько вакансий показать? (по умолчанию 10): ") or "10")
            limit = max(1, min(limit, 50))  # Ограничиваем от 1 до 50
        except ValueError:
            limit = 10

        self.print_vacancies(vacancies, f"Первые {limit} вакансий", limit)

        if len(vacancies) > limit:
            print("\n💡 Подсказка: Используйте поиск по ключевому слову для уточнения")

        input("\n📝 Нажмите Enter для продолжения...")

    def handle_avg_salary(self):
        """Обработчик для пункта 3"""
        print("\n" + "=" * 60)
        print("💰 СРЕДНЯЯ ЗАРПЛАТА ПО ВАКАНСИЯМ")
        print("=" * 60)

        avg_salary = self.db_manager.get_avg_salary()

        if avg_salary == 0:
            print("😔 Не удалось рассчитать среднюю зарплату")
            return

        # Получаем дополнительную статистику
        stats = self.db_manager.get_statistics()

        print(f"📊 Средняя зарплата: {avg_salary:,.0f} руб.".replace(",", " "))

        if 'vacancies_with_salary' in stats and 'total_vacancies' in stats:
            with_salary = stats['vacancies_with_salary']
            total = stats['total_vacancies']
            percentage = (with_salary / total * 100) if total > 0 else 0

            print(f"📊 Вакансий с указанной зарплатой: {with_salary} из {total} ({percentage:.1f}%)")

        input("\n📝 Нажмите Enter для продолжения...")

    def handle_higher_salary_vacancies(self):
        """Обработчик для пункта 4"""
        print("\n" + "=" * 60)
        print("🚀 ВАКАНСИИ С ЗАРПЛАТОЙ ВЫШЕ СРЕДНЕЙ")
        print("=" * 60)

        # Сначала получаем среднюю зарплату
        avg_salary = self.db_manager.get_avg_salary()

        if avg_salary == 0:
            print("😔 Не удалось рассчитать среднюю зарплату")
            return

        print(f"📊 Средняя зарплата по рынку: {avg_salary:,.0f} руб.".replace(",", " "))
        print("🔎 Ищем вакансии с зарплатой выше средней...")

        vacancies = self.db_manager.get_vacancies_with_higher_salary()

        if not vacancies:
            print("😔 Вакансий с зарплатой выше средней не найдено")
            return

        print(f"\n✅ Найдено {len(vacancies)} вакансий")

        # Спрашиваем сколько показать
        try:
            limit = int(input(f"Сколько вакансий показать? (по умолчанию {min(10, len(vacancies))}): ") or str(
                min(10, len(vacancies))))
            limit = max(1, min(limit, 20))
        except ValueError:
            limit = min(10, len(vacancies))

        self.print_vacancies(vacancies, f"Вакансии с зарплатой выше {avg_salary:,.0f} руб.".replace(",", " "), limit)

        input("\n📝 Нажмите Enter для продолжения...")

    def handle_keyword_search(self):
        """Обработчик для пункта 5"""
        print("\n" + "=" * 60)
        print("🔎 ПОИСК ВАКАНСИЙ ПО КЛЮЧЕВОМУ СЛОВУ")
        print("=" * 60)

        keyword = input("Введите ключевое слово для поиска (например: python, аналитик): ").strip()

        if not keyword:
            print("⚠️  Ключевое слово не может быть пустым")
            return

        print(f"🔎 Ищем вакансии со словом '{keyword}'...")

        vacancies = self.db_manager.get_vacancies_with_keyword(keyword)

        if not vacancies:
            print(f"😔 Вакансий со словом '{keyword}' не найдено")
            print("\n💡 Попробуйте другие слова: python, java, аналитик, менеджер, разработчик")
            return

        print(f"\n✅ Найдено {len(vacancies)} вакансий")

        # Спрашиваем сколько показать
        try:
            limit = int(input(f"Сколько вакансий показать? (по умолчанию {min(10, len(vacancies))}): ") or str(
                min(10, len(vacancies))))
            limit = max(1, min(limit, 20))
        except ValueError:
            limit = min(10, len(vacancies))

        self.print_vacancies(vacancies, f"Вакансии со словом '{keyword}'", limit)

        input("\n📝 Нажмите Enter для продолжения...")

    def handle_statistics(self):
        """Обработчик для пункта 6"""
        print("\n" + "=" * 60)
        print("📈 СТАТИСТИКА БАЗЫ ДАННЫХ")
        print("=" * 60)

        stats = self.db_manager.get_statistics()

        if not stats:
            print("😔 Не удалось получить статистику")
            return

        print("📊 ОБЩАЯ СТАТИСТИКА:")
        print("-" * 40)
        print(f"🏢 Компаний: {stats.get('total_companies', 0)}")
        print(f"📝 Вакансий: {stats.get('total_vacancies', 0)}")
        print(f"💰 С зарплатой: {stats.get('vacancies_with_salary', 0)}")
        print(f"📈 Средняя зарплата: {stats.get('avg_salary', 0):,.0f} руб.".replace(",", " "))

        # Топ компаний
        if 'top_companies' in stats and stats['top_companies']:
            print("\n🏆 ТОП КОМПАНИЙ ПО ВАКАНСИЯМ:")
            print("-" * 40)
            for i, (company, count, percentage) in enumerate(stats['top_companies'][:5], 1):
                print(f"{i}. {company}: {count} вакансий ({percentage}%)")

        # Популярные позиции
        if 'top_positions' in stats and stats['top_positions']:
            print("\n🎯 ПОПУЛЯРНЫЕ ДОЛЖНОСТИ:")
            print("-" * 40)
            for i, (position, count) in enumerate(stats['top_positions'][:5], 1):
                print(f"{i}. {position}: {count} вакансий")

        input("\n📝 Нажмите Enter для продолжения...")

    def handle_salary_range_search(self):
        """Обработчик для пункта 7"""
        print("\n" + "=" * 60)
        print("🎯 ПОИСК ПО ДИАПАЗОНУ ЗАРПЛАТ")
        print("=" * 60)

        try:
            min_salary = input("Минимальная зарплата (оставьте пустым, если не важно): ").strip()
            max_salary = input("Максимальная зарплата (оставьте пустым, если не важно): ").strip()

            min_salary = int(min_salary) if min_salary else None
            max_salary = int(max_salary) if max_salary else None

            if min_salary is None and max_salary is None:
                print("⚠️  Укажите хотя бы одну границу зарплаты")
                return

            if min_salary is not None and max_salary is not None and min_salary > max_salary:
                print("⚠️  Минимальная зарплата не может быть больше максимальной")
                return

        except ValueError:
            print("⚠️  Пожалуйста, введите числа")
            return

        # Формируем текст запроса
        range_text = ""
        if min_salary is not None and max_salary is not None:
            range_text = f"от {min_salary:,} до {max_salary:,} руб.".replace(",", " ")
        elif min_salary is not None:
            range_text = f"от {min_salary:,} руб.".replace(",", " ")
        elif max_salary is not None:
            range_text = f"до {max_salary:,} руб.".replace(",", " ")

        print(f"🔎 Ищем вакансии с зарплатой {range_text}...")

        vacancies = self.db_manager.get_vacancies_with_salary_range(min_salary, max_salary)

        if not vacancies:
            print(f"😔 Вакансий с зарплатой {range_text} не найдено")
            return

        print(f"\n✅ Найдено {len(vacancies)} вакансий")

        # Спрашиваем сколько показать
        try:
            limit = int(input(f"Сколько вакансий показать? (по умолчанию {min(10, len(vacancies))}): ") or str(
                min(10, len(vacancies))))
            limit = max(1, min(limit, 20))
        except ValueError:
            limit = min(10, len(vacancies))

        self.print_vacancies(vacancies, f"Вакансии с зарплатой {range_text}", limit)

        input("\n📝 Нажмите Enter для продолжения...")

    def handle_top_companies(self):
        """Обработчик для пункта 8"""
        print("\n" + "=" * 60)
        print("🏆 ТОП КОМПАНИЙ ПО КОЛИЧЕСТВУ ВАКАНСИЙ")
        print("=" * 60)

        try:
            limit = input("Сколько компаний показать? (по умолчанию 10): ").strip()
            limit = int(limit) if limit else 10
            limit = max(1, min(limit, 20))
        except ValueError:
            limit = 10

        companies = self.db_manager.get_top_companies_by_vacancies(limit)

        if not companies:
            print("😔 Не удалось получить список компаний")
            return

        total_vacancies = sum(count for _, count, _ in companies)

        print(f"Топ-{limit} компаний по количеству вакансий:")
        print("-" * 60)

        for i, (company, count, percentage) in enumerate(companies, 1):
            print(f"{i:2}. {company:30} {count:4} вакансий ({percentage:5.1f}%)")

        print("-" * 60)
        print(f"Всего вакансий в топе: {total_vacancies}")

        input("\n📝 Нажмите Enter для продолжения...")

    def run(self):
        """Основной цикл программы"""
        print("\n🚀 Запуск системы анализа вакансий с HH.ru")
        print("🔗 Подключение к базе данных...")

        # Проверяем подключение к БД
        if not self.db_manager.connect():
            print("❌ Не удалось подключиться к базе данных!")
            print("Проверьте настройки подключения в файле .env")
            print("Завершение работы...")
            return

        self.db_manager.close()
        print("✅ Подключение успешно!")

        # Главный цикл меню
        while self.running:
            self.display_menu()

            try:
                choice = input("\n📋 Выберите действие (0-8): ").strip()

                if choice == "0":
                    self.running = False
                    print("\n👋 До свидания! Спасибо за использование программы.")

                elif choice == "1":
                    self.handle_companies_and_vacancies_count()

                elif choice == "2":
                    self.handle_all_vacancies()

                elif choice == "3":
                    self.handle_avg_salary()

                elif choice == "4":
                    self.handle_higher_salary_vacancies()

                elif choice == "5":
                    self.handle_keyword_search()

                elif choice == "6":
                    self.handle_statistics()

                elif choice == "7":
                    self.handle_salary_range_search()

                elif choice == "8":
                    self.handle_top_companies()

                else:
                    print("⚠️  Неверный выбор. Пожалуйста, выберите число от 0 до 8.")

            except KeyboardInterrupt:
                print("\n\n👋 Программа прервана пользователем.")
                self.running = False
            except Exception as e:
                print(f"\n❌ Произошла ошибка: {e}")
                print("Попробуйте еще раз или выберите другой пункт меню.")


def main():
    """Основная функция программы"""
    try:
        # Очистка экрана (работает в Windows и Linux/macOS)
        os.system('cls' if os.name == 'nt' else 'clear')

        # Создание и запуск интерфейса
        ui = UserInterface()
        ui.run()

    except Exception as e:
        print(f"❌ Критическая ошибка: {e}")
        print("Проверьте настройки и попробуйте снова.")
    finally:
        print("\n" + "=" * 60)
        print("Завершение работы программы.")


if __name__ == "__main__":
    main()