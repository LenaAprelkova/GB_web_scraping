# 1) Написать приложение(используя lxml, нельзя использовать BeautifulSoup), которое собирает основные новости с сайтов
# news.mail.ru, lenta.ru, yandex news Для парсинга использовать xpath.
# Структура данных должна содержать:
# название источника(mail и яндекс не источники, а аггрегаторы, см. страницу новости),
# наименование новости,
# ссылку на новость,
# дата публикации
# 2) Сложить все новости в БД, новости должны обновляться, т.е. используйте update


import requests
from pprint import pprint
from pymongo import MongoClient
from lxml.html import fromstring
from datetime import datetime


class NewsLentaRu:
    def __init__(self):
        self.url = "https://lenta.ru/"
        self.headers = {
            'User-agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                          "(KHTML, like Gecko) Chrome/100.0.4896.127 Safari/537.36"
        }
        self.items_xpath = "//div[contains (@class, 'topnews')]//div[contains (@class, 'card-mini__text')]"
        self.title_xpath = ".//text()"
        self.href_xpath = "./parent::a/@href"
        self.datetime_xpath = './/span[contains (@class, "js-ago")]//@datetime'
        self.source_xpath = './/a[contains (@class, "breadcrumbs__link")]//@href'

    def get_news(self):
        r = requests.get(self.url, headers=self.headers)
        dom = fromstring(r.text)
        items = dom.xpath(self.items_xpath)

        for item in items:
            info = {}
            title = item.xpath(self.title_xpath)[0]
            datetime = item.xpath(self.title_xpath)[1]
            source = 'lenta.ru'
            url = self.url + item.xpath(self.href_xpath)[0]
            info["title"] = title.replace('\xa0', ' ')
            info["source"] = source
            info["url"] = url
            info["datetime"] = datetime
            mongo.save_with_update(info)


class NewsMailRu:
    def __init__(self):
        self.url = "https://news.mail.ru/"
        self.headers = {
            'User-agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                          "(KHTML, like Gecko) Chrome/100.0.4896.127 Safari/537.36"
        }
        self.items_xpath = '//ul/li[contains(@class, "list__item")][position() > 2]/a'
        self.title_xpath = './/text()'
        self.href_xpath = ".//@href"
        self.datetime_xpath = './/span[contains (@class, "js-ago")]//@datetime'
        self.source_xpath = './/a[contains (@class, "breadcrumbs__link")]//@href'

    def get_news(self):
        r = requests.get(self.url, headers=self.headers)
        dom = fromstring(r.text)
        items = dom.xpath(self.items_xpath)

        for item in items:
            info = {}
            title = item.xpath(self.title_xpath)[0]
            new_url = item.xpath(self.href_xpath)[0]
            new_r = requests.get(new_url, headers=self.headers)
            new_dom = fromstring(new_r.text)
            datetime = new_dom.xpath(self.datetime_xpath)[0]
            source = new_dom.xpath(self.source_xpath)[0]
            info["title"] = title.replace('\xa0', ' ')
            info["url"] = new_url
            info["datetime"] = datetime
            info["source"] = source
            mongo.save_with_update(info)


class Mongo:
    def __init__(self):
        self.mongo_host = "localhost"
        self.mongo_port = 27017
        self.mongo_db = "news"
        self.mongo_collection = "main_news"

    def save_with_update(self, item):
        with MongoClient(self.mongo_host, self.mongo_port) as client:
            db = client[self.mongo_db]
            collection = db[self.mongo_collection]
            collection.update_one(
                {"url": item["url"]},
                {"$set": {"title": item["title"],
                          "datetime": item["datetime"],
                          "source": item["source"]}
                 },
                upsert=True,
            )


if __name__ == "__main__":
    mongo = Mongo()
    mailru = NewsMailRu()
    mailru.get_news()
    lenta = NewsLentaRu()
    lenta.get_news()
