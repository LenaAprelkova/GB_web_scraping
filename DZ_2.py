# Необходимо собрать информацию о вакансиях на вводимую должность (используем input) с сайтов Superjob(необязательно)
# и HH(обязательно). Приложение должно анализировать несколько страниц сайта (также вводим через input).
# Получившийся список должен содержать в себе минимум:
# 1) Наименование вакансии.
# 2) Предлагаемую зарплату (отдельно минимальную и максимальную; дополнительно - собрать валюту;
# можно использовать regexp или if'ы).
# 3) Ссылку на саму вакансию.
# 4) Сайт, откуда собрана вакансия.
#
# По желанию можно добавить ещё параметры вакансии (например, работодателя и расположение).
# Структура должна быть одинаковая для вакансий с обоих сайтов. Сохраните результат в json-файл


import time
import json
import requests
from bs4 import BeautifulSoup

URL = 'https://hh.ru/search/vacancy'
PARAMS = {
    'text': '',
    'page': 0,
}
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/100.0.4896.127 Safari/537.36",
    "Accept": "*/*",
}
save_vacancy = 'vacancy.json'


class VacancyHH:
    def __init__(self, url, vacancy, page):
        self.url = url
        self.vacancy = vacancy
        self.page_number = page
        self.headers = HEADERS
        self.params = self.create_params()
        self.vacancy_list = []

    def create_params(self):
        PARAMS['text'] = self.vacancy
        return PARAMS

    def get_info(self):
        try:
            a = requests.get(self.url, params=self.params, headers=self.headers)
            a.raise_for_status()
            time.sleep(1)
        except Exception as error:
            print(error)
            time.sleep(1)
            return None
        return a.text

    @staticmethod
    def get_dom(html_string):
        return BeautifulSoup(html_string, "html.parser")

    @staticmethod
    def get_salary(salary):
        if salary:
            salary = salary.text.replace('\u202f', '')
            salary = salary.split(' ')
            if salary[0] == 'от':
                min_salary = salary[1]
                max_salary = None
                currency = salary[2]
            else:
                if salary[0] == 'до':
                    min_salary = None
                    max_salary = salary[1]
                    currency = salary[2]
                else:
                    min_salary = salary[0]
                    max_salary = salary[2]
                    currency = salary[3]
        else:
            min_salary = None
            max_salary = None
            currency = None
        return min_salary, max_salary, currency

    def get_info_vacancy_hh(self, soup):
        vacancy_elements = soup.find_all('div', class_='vacancy-serp-item__layout')
        for el in vacancy_elements:
            title = el.find('a', class_='bloko-link').text.strip()
            salary = el.find('span', class_='bloko-header-section-3')
            min_salary, max_salary, currency = self.get_salary(salary)
            link = el.find('a', class_='bloko-link').get('href')
            vacancy = dict(title=title, min_salary=min_salary, max_salary=max_salary,
                           currency=currency, link=link, source='https://hh.ru/')
            self.vacancy_list.append(vacancy)

    def pipeline(self):
        for page in range(0, self.page_number):
            self.params['page'] = page
            response = self.get_info()
            soup = self.get_dom(response)
            self.get_info_vacancy_hh(soup)
        return self.vacancy_list

    @staticmethod
    def save_json(data, path):
        with open(path, "w", encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f'Информация о списке вакансий сохранена в файл {path}.')


if __name__ == "__main__":
    try:
        vacancy_input = input("Введите название вакансии: ")
        page_number = int(input("Введите число страниц: "))
        scraper_hh = VacancyHH(URL, vacancy_input, page_number)
        data_vacancy = scraper_hh.pipeline()
        scraper_hh.save_json(data_vacancy, save_vacancy)
    except Exception as e:
        print(e)
