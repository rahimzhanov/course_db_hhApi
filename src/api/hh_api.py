# src/api/hh_api.py
import requests
import time
from typing import Dict, List, Optional, Tuple, Any
from config import API_BASE_URL, USER_AGENT


class HeadHunterAPI:
    """Класс для работы с API HeadHunter"""

    def __init__(self):
        self.base_url = API_BASE_URL
        self.headers = {'User-Agent': USER_AGENT}

    def get_employer(self, employer_id: int) -> Optional[Dict[str, Any]]:
        """
        Получает информацию о компании по её ID

        Args:
            employer_id: ID компании на hh.ru

        Returns:
            Словарь с данными компании или None в случае ошибки
        """
        url = f"{self.base_url}/employers/{employer_id}"

        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()

            data = response.json()

            # Извлекаем только нужные поля
            employer_info = {
                'id': data.get('id'),
                'name': data.get('name'),
                'url': data.get('alternate_url'),
                'open_vacancies': data.get('open_vacancies', 0),
                'description': data.get('description', '')[:500]  # Обрезаем длинное описание
            }

            return employer_info

        except requests.exceptions.RequestException as e:
            print(f"Ошибка при получении данных компании {employer_id}: {e}")
            return None

    def get_vacancies_by_employer(self, employer_id: int) -> List[Dict[str, Any]]:
        """
        Получает все вакансии компании

        Args:
            employer_id: ID компании

        Returns:
            Список словарей с данными вакансий
        """
        vacancies = []
        page = 0
        per_page = 100  # Максимальное количество вакансий на странице

        while True:
            params = {
                'employer_id': employer_id,
                'page': page,
                'per_page': per_page,
                'only_with_salary': False  # Получаем все вакансии, даже без зарплаты
            }

            try:
                response = requests.get(
                    f"{self.base_url}/vacancies",
                    params=params,
                    headers=self.headers
                )
                response.raise_for_status()

                data = response.json()
                page_vacancies = data.get('items', [])

                if not page_vacancies:
                    break

                # Обрабатываем каждую вакансию
                for vacancy in page_vacancies:
                    parsed_vacancy = self._parse_vacancy(vacancy, employer_id)
                    if parsed_vacancy:
                        vacancies.append(parsed_vacancy)

                # Проверяем, есть ли следующая страница
                pages = data.get('pages', 0)
                if page >= pages - 1:
                    break

                page += 1

                # Пауза между запросами (уважаем API)
                time.sleep(0.1)

            except requests.exceptions.RequestException as e:
                print(f"Ошибка при получении вакансий компании {employer_id}: {e}")
                break

        return vacancies

    def _parse_vacancy(self, vacancy_data: Dict[str, Any], employer_id: int) -> Optional[Dict[str, Any]]:
        """
        Парсит данные вакансии, извлекая нужные поля

        Args:
            vacancy_data: Сырые данные вакансии из API
            employer_id: ID компании-работодателя

        Returns:
            Отформатированный словарь с данными вакансии
        """
        try:
            # Обрабатываем зарплату
            salary_data = vacancy_data.get('salary')
            salary_from, salary_to, currency = self._parse_salary(salary_data)

            # Безопасное извлечение вложенных полей
            experience_dict = vacancy_data.get('experience') or {}
            employment_dict = vacancy_data.get('employment') or {}
            schedule_dict = vacancy_data.get('schedule') or {}
            snippet_dict = vacancy_data.get('snippet') or {}

            # Извлекаем данные
            parsed_vacancy = {
                'id': vacancy_data.get('id'),
                'employer_id': employer_id,
                'name': vacancy_data.get('name', 'Без названия'),
                'salary_from': salary_from,
                'salary_to': salary_to,
                'currency': currency,
                'url': vacancy_data.get('alternate_url'),
                'experience': experience_dict.get('name', 'Не указан'),
                'employment': employment_dict.get('name', 'Не указан'),
                'schedule': schedule_dict.get('name', 'Не указан'),
                'requirements': (snippet_dict.get('requirement') or '')[:1000],
                'responsibility': (snippet_dict.get('responsibility') or '')[:1000],
                'published_at': vacancy_data.get('published_at', '')
            }

            return parsed_vacancy

        except Exception as e:
            print(f"Ошибка при парсинге вакансии {vacancy_data.get('id', 'unknown')}: {e}")
            return None

    def _parse_salary(self, salary_data: Optional[Dict]) -> Tuple[Optional[int], Optional[int], Optional[str]]:
        """
        Обрабатывает поле зарплаты из API

        Args:
            salary_data: Данные о зарплате из API

        Returns:
            Кортеж (salary_from, salary_to, currency)
        """
        if not salary_data:
            return None, None, None

        salary_from = salary_data.get('from')
        salary_to = salary_data.get('to')
        currency = salary_data.get('currency')

        return salary_from, salary_to, currency

    def get_multiple_employers(self, employer_ids: List[int]) -> Dict[int, Dict[str, Any]]:
        """
        Получает информацию о нескольких компаниях

        Args:
            employer_ids: Список ID компаний

        Returns:
            Словарь {employer_id: employer_data}
        """
        employers = {}

        for emp_id in employer_ids:
            print(f"Получение данных компании {emp_id}...")
            employer_data = self.get_employer(emp_id)

            if employer_data:
                employers[emp_id] = employer_data

            # Пауза между запросами
            time.sleep(0.05)

        return employers


# Функция для быстрого тестирования
def test_api():
    """Тестирование работы API"""
    api = HeadHunterAPI()

    # Тест с Яндексом (ID: 1740)
    print("Тест 1: Получение информации о компании...")
    employer = api.get_employer(1740)

    if employer:
        print(f"✅ Получена компания: {employer['name']}")
        print(f"   Открытых вакансий: {employer['open_vacancies']}")

        print("\nТест 2: Получение вакансий компании...")
        vacancies = api.get_vacancies_by_employer(1740)
        print(f"✅ Получено вакансий: {len(vacancies)}")

        if vacancies:
            print(f"Пример вакансии: {vacancies[0]['name']}")
            print(f"Зарплата: {vacancies[0]['salary_from']} - {vacancies[0]['salary_to']} {vacancies[0]['currency']}")

    else:
        print("❌ Не удалось получить данные компании")


if __name__ == "__main__":
    test_api()