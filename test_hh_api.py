# test_hh_api.py
import sys
import os

# Получаем абсолютный путь к корню проекта
current_dir = os.path.dirname(os.path.abspath(__file__))
print(f"Текущая директория: {current_dir}")

# Добавляем корень проекта в sys.path
sys.path.insert(0, current_dir)

# Проверяем, что config.py существует
config_path = os.path.join(current_dir, 'config.py')
print(f"Путь к config.py: {config_path}")
print(f"config.py существует: {os.path.exists(config_path)}")

# Проверяем структуру src
src_path = os.path.join(current_dir, 'src', 'api', 'hh_api.py')
print(f"Путь к hh_api.py: {src_path}")
print(f"hh_api.py существует: {os.path.exists(src_path)}")

print("\n" + "=" * 50 + "\n")

try:
    # Теперь импортируем
    from src.api.hh_api import HeadHunterAPI
    from config import COMPANIES

    print("✅ Импорт успешен!")

except ImportError as e:
    print(f"❌ Ошибка импорта: {e}")
    print("\nПроверьте:")
    print("1. Файл config.py в корне проекта")
    print("2. Файл src/api/hh_api.py")

    # Выводим список файлов в корне
    print("\nФайлы в корневой директории:")
    for file in os.listdir(current_dir):
        if file.endswith('.py'):
            print(f"  - {file}")

    sys.exit(1)


def main():
    print("\nТестирование модуля API HH.ru")
    print("=" * 50)

    api = HeadHunterAPI()

    # Тестируем на одной компании для начала
    test_company_id = 1740  # Яндекс
    test_company_name = "Яндекс"

    print(f"Тестируем API на компании: {test_company_name} (ID: {test_company_id})")

    # Получаем информацию о компании
    print("\n1. Получение данных компании...")
    employer = api.get_employer(test_company_id)

    if employer:
        print(f"✅ Успешно!")
        print(f"   Название: {employer['name']}")
        print(f"   Вакансий: {employer['open_vacancies']}")
        print(f"   Ссылка: {employer['url']}")
    else:
        print("❌ Не удалось получить данные компании")
        return

    # Получаем вакансии
    print("\n2. Получение вакансий компании...")
    vacancies = api.get_vacancies_by_employer(test_company_id)

    print(f"✅ Получено вакансий: {len(vacancies)}")

    if vacancies:
        # Показываем несколько примеров
        print("\n3. Примеры вакансий:")
        for i, vacancy in enumerate(vacancies[:3]):  # Первые 3
            print(f"\n   {i + 1}. {vacancy['name']}")
            salary_str = ""
            if vacancy['salary_from'] or vacancy['salary_to']:
                salary_str = f"{vacancy['salary_from'] or '?'} - {vacancy['salary_to'] or '?'} {vacancy['currency'] or ''}"
            else:
                salary_str = "Не указана"
            print(f"      Зарплата: {salary_str}")
            print(f"      Опыт: {vacancy['experience']}")
            print(f"      Тип: {vacancy['employment']}")

    print("\n" + "=" * 50)
    print(f"Тестирование завершено! Всего вакансий: {len(vacancies)}")


if __name__ == "__main__":
    main()