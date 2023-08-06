""" Модуль отвечающий за сбор данных с HeadHunter'a через его API"""
import requests  # Для запросов по API
from vacancy import Vacancy

# Использованная литература
# https://api.hh.ru/openapi/
# https://habr.com/ru/articles/666062/


class HeadHunter:
    __employer_url = 'https://api.hh.ru/employers?only_with_vacancies=true'
    __dictionary_url = 'https://api.hh.ru/dictionaries'
    __area_url = 'https://api.hh.ru/areas'
    __vacancy_url = 'https://api.hh.ru/vacancies'

    def __init__(self):
        self.dictionaries = requests.get(self.__dictionary_url).json()

    def get_experience(self):
        return self.dictionaries['experience']

    def get_employment(self):
        return self.dictionaries['employment']

    def get_schedule(self):
        return self.dictionaries['schedule']

    def get_areas(self):
        areas = requests.get(self.__area_url).json()
        result = []
        for area in areas:
            for i in range(len(area['areas'])):
                # Если у зоны есть внутренние зоны
                if len(area['areas'][i]['areas']) != 0:
                    for j in range(len(area['areas'][i]['areas'])):
                        result.append({'country_id': area['id'],
                                       'country_name': area['name'],
                                       'city_id': area['areas'][i]['areas'][j]['id'],
                                       'city_name': area['areas'][i]['areas'][j]['name']})
                else:
                    # Если у зоны нет внутренних зон
                    result.append({'country_id': area['id'],
                                   'country_name': area['name'],
                                   'city_id': area['areas'][i]['id'],
                                   'city_name': area['areas'][i]['name']})
        return result

    @staticmethod
    def get_countries():
        countries = requests.get('https://api.hh.ru/areas/countries').json()
        return countries

    def get_employers(self, key_word, area_id):
        """
        Метод позволяет получить информацию о 10 компаниях по ключевому слову в имени компании
        :param key_word: Ключевое слово, которое будет использоваться для поиска в наименовании компании или ее описании
        :param area_id: ид области/города в котором расположена компания
        """
        params = {'text': key_word.lower(),
                  'area': area_id,
                  'per_page': 10}
        response = requests.get(self.__employer_url, params=params).json()['items']
        employers = [{'employer_id': employer['id'], 'employer_name': employer['name']} for employer in response]
        return employers

    def get_vacancies(self, params):
        vacancies = requests.get(self.__vacancy_url, params=params).json()
        result = []
        if 'items' in vacancies:
            for vacancy in vacancies['items']:
                salary = vacancy['salary']
                if salary is not None:
                    salary_from = salary.get('from')
                    salary_to = salary.get('to')
                else:
                    salary_from = None
                    salary_to = None

                new_vacancy = Vacancy(
                    id=vacancy['id'],
                    employer_name=vacancy.get('employer').get('name'),
                    url=vacancy['alternate_url'],
                    name=vacancy['name'],
                    salary_from=salary_from,
                    salary_to=salary_to,
                    description=vacancy['snippet']['responsibility'],
                    requirements=vacancy['snippet']['requirement'],
                )
                result.append(new_vacancy)
        else:
            print(vacancies['errors'])
        return result
