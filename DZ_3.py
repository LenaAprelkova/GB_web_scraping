# 1) Развернуть у себя на компьютере/виртуальной машине/хостинге MongoDB и реализовать функцию, записывающую собранные
# вакансии в созданную БД(добавление данных в БД по ходу сбора данных).
# 2) Написать функцию, которая будет добавлять в вашу базу данных только новые вакансии с сайта.
# 3) Написать функцию, которая производит поиск и выводит на экран вакансии с заработной платой больше введённой суммы.
# Необязательно - возможность выбрать вакансии без указанных зарплат.


import time
import requests
from pprint import pprint
from pymongo import DESCENDING, MongoClient
from bs4 import BeautifulSoup


MONGO_HOST = "localhost"
MONGO_PORT = 27017
MONGO_DB = "vacancies"
MONGO_COLLECTION = "hh"

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


class HHScrapper:
    def __init__(self, url, vacancy, page):
        self.url = url
        self.vacancy = vacancy
        self.page_number = page
        self.headers = HEADERS
        self.params = self.create_params()
        self.count_new_vacancy = 0

    def create_params(self):
        PARAMS['text'] = self.vacancy
        return PARAMS

    def get_html(self):
        try:
            response = requests.get(self.url, params=self.params, headers=self.headers)
            response.raise_for_status()
            time.sleep(1)
        except Exception as error:
            print(error)
            time.sleep(1)
            return None
        return response.text

    @staticmethod
    def get_dom(html_string):
        return BeautifulSoup(html_string, "html.parser")

    @staticmethod
    def get_salary(salary):
        if salary:
            salary = salary.text.replace('\u202f', '')
            salary = salary.split(' ')
            if salary[0] == 'от':
                min_salary = int(salary[1])
                max_salary = None
                currency = salary[2]
            else:
                if salary[0] == 'до':
                    min_salary = None
                    max_salary = int(salary[1])
                    currency = salary[2]
                else:
                    min_salary = int(salary[0])
                    max_salary = int(salary[2])
                    currency = salary[3]
        else:
            min_salary = None
            max_salary = None
            currency = None
        return min_salary, max_salary, currency

    def get_info_vacancy_hh(self, soup):
        vacancy_elements = soup.find_all('div', class_='vacancy-serp-item__layout')
        for element in vacancy_elements:
            title = element.find('a', class_='bloko-link').text.strip()
            salary = element.find('span', class_='bloko-header-section-3')
            min_salary, max_salary, currency = self.get_salary(salary)
            link = element.find('a', class_='bloko-link').get('href')
            vacancy = dict(title=title, min_salary=min_salary, max_salary=max_salary,
                           currency=currency, link=link, source='https://hh.ru/')
            self.insert_db(vacancy)

    def insert_db(self, item):
        with MongoClient(MONGO_HOST, MONGO_PORT) as client:
            db = client[MONGO_DB]
            collection = db[MONGO_COLLECTION]
            if not list(collection.find(item)):
                collection.insert_one(item)
                self.count_new_vacancy += 1

    @staticmethod
    def find_salary(level_salary):
        with MongoClient(MONGO_HOST, MONGO_PORT) as client:
            db = client[MONGO_DB]
            collection = db[MONGO_COLLECTION]
            pprint(list(collection.find({
                "$or": [
                    {"max_salary": {"$gte": level_salary}},
                    {"max_salary": None}
                ]
            }).sort(
                [
                    ("max_salary", DESCENDING),
                    ("min_salary", DESCENDING),
                ])))

    def pipeline(self):
        for page in range(0, self.page_number):
            self.params['page'] = page
            response = self.get_html()
            soup = self.get_dom(response)
            self.get_info_vacancy_hh(soup)
        print(f'{self.count_new_vacancy} вакансии добавлены в банк вакансий')


if __name__ == "__main__":
    try:
        vacancy_input = input("Введите название вакансии: ")
        page_number = int(input("Введите число страниц: "))
        scraper_hh = HHScrapper(URL, vacancy_input, page_number)
        scraper_hh.pipeline()
        level_salary_input = int(input("Введите нижнюю границу ЗП в руб.: "))
        scraper_hh.find_salary(level_salary_input)
    except Exception as e:
        print(e)
