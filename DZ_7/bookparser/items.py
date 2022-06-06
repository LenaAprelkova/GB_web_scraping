import json
from lxml.html import fromstring

import scrapy
from scrapy.loader.processors import Compose, Join, MapCompose, TakeFirst

def create_img_urls_array(info_strings):
    infos = json.loads(info_strings[0])
    print()
    return [info["full"] for info in infos]


def clear_string(s):
    return s.strip()


def extract_price(s):
    price = clear_string(s).split()
    return float(price[0])


def get_info_item(html):
    info_title_xpath = './/div[@class="product-prop__title"]/text()'
    info_value_xpath = './/div[@class="product-prop__value"]/descendant::text()'
    dom = fromstring(html)
    items = dom.xpath('.//div[@class="product-prop"]')
    info_dict = {}
    for item in items:
        title = item.xpath(info_title_xpath)[0]
        value = item.xpath(info_value_xpath)
        value = "".join(value).strip().replace('\n', ' ')
        info_dict[title] = value
    return info_dict


class BookparserItem(scrapy.Item):
    url = scrapy.Field(output_processor=TakeFirst())
    title = scrapy.Field(
        input_processor=MapCompose(clear_string),
        output_processor=Join(separator=" ")
    )
    prices = scrapy.Field(input_processor=MapCompose(extract_price))
    item_info = scrapy.Field(input_processor=MapCompose(get_info_item))
    img_urls = scrapy.Field()
    img_info = scrapy.Field()
    print()
