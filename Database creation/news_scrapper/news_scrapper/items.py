# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class NewsScrapperItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass

class NewsItem(scrapy.Item):
    unique_id = scrapy.Field()
    url = scrapy.Field()
    headline = scrapy.Field()
    Src = scrapy.Field()
    date_time = scrapy.Field()
    description = scrapy.Field()
    len = scrapy.Field()
    len_summary = scrapy.Field()