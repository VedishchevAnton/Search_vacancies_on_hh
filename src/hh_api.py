"""Реализация класса HeadHunterAPI, для получения данных о вакансиях и работодателях с ресурса HeadHunter.ru"""

import requests


class HeadHunterAPI:
    def __init__(self):
        self.url_vacancies = f"https://api.hh.ru/vacancies"  # url hh_api

    def get_vacancies(self, employer_id: str) -> []:
        """
        Метод для получения данных о вакансиях с помощью HeadHunterApi.
        :param employer_id: Поиск ведется по идентификатору работодателя
        :type employer_id: str
        :return список с данными о вакансиях.
        """

        vacancies = []  # список вакансий
        page = 0  # номер страницы на HH

        # Проверяем, что employer_id не пустой
        if not employer_id:
            raise ValueError("Идентификатор работодателя не может быть пустым")

        while True:
            params = {'employer_id': employer_id,
                      'per_page': 100,
                      'area': 113,
                      'page': page
                      }
            # Отправляем запрос к API
            response_vacancies = requests.get(self.url_vacancies, params=params)

            # Проверяем, что запрос выполнен успешно
            if response_vacancies.status_code != 200:
                break

            data_vacancies = response_vacancies.json()

            if not data_vacancies["items"]:
                break
            vacancies_data = data_vacancies['items']

            for vacancy in vacancies_data:
                # Получаем данные о вакансиях
                vacancy = {'id': vacancy['id'],
                           'title': vacancy['name'],
                           'salary': HeadHunterAPI.get_salary(vacancy['salary']),
                           'description': vacancy['snippet']['requirement'],
                           'employer': vacancy['employer']['name'],
                           'url': vacancy['alternate_url']
                           }
                vacancies.append(vacancy)
            # Проверяем, все ли страницы были обработаны
            if page >= data_vacancies['pages'] - 1:
                break
            page += 1
        return vacancies

    def get_employers(self, employer_id: str) -> []:
        """
        Метод для получения данных о работодателях с помощью HeadHunterApi.
        :param employer_id: Поиск ведется по идентификатору работодателя
        :type employer_id: str
        :return список с данными о работодателях.
        """

        employers = []  # список работодателей

        # Проверяем, что employer_id не пустой
        if not employer_id:
            raise ValueError("Идентификатор работодателя не может быть пустым")

        # Отправляем запрос к API
        response_employers = requests.get(f'https://api.hh.ru/employers/{employer_id}')

        # Проверяем, что запрос выполнен успешно
        if response_employers.status_code != 200:
            raise ValueError("Ошибка при получении данных о работодателе")

        data_employer = response_employers.json()
        employer = {'id_company': data_employer['id'],
                    'employer_name': data_employer['name'],
                    'description': data_employer['description'],
                    'site': data_employer['site_url']
                    }
        for vacancy in self.get_vacancies(employer_id):
            employer['id_vacancy'] = vacancy['id']
            employers.append(employer)
        return employers

    @staticmethod
    def get_salary(salary_data):
        if salary_data is None:
            salary = {'from': 0, 'currency': 'RUR'}
        elif 'to' not in salary_data or salary_data['to'] is None:
            salary = {'from': salary_data.get('from', 0), 'currency': salary_data.get('currency', 'RUR')}
        elif 'from' not in salary_data or salary_data['from'] is None:
            salary = {'from': salary_data['to'], 'currency': salary_data.get('currency', 'RUR')}
        else:
            salary = {'from': salary_data['from'], 'to': salary_data['to'],
                      'currency': salary_data.get('currency', 'RUR')}
        return salary
