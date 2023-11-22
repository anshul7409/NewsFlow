import scrapy
import uuid
# from .config import Config
# import openai_summarize
from news_scrapper.items import NewsItem

class NewsspiderSpider(scrapy.Spider):
    name = "newsspider"
    allowed_domains = ["timesofindia.indiatimes.com"]
    start_urls = ['https://timesofindia.indiatimes.com/topic/'+'Business']
    openai_summarizer = openai_summarize.OpenAISummarize(Config.OPENAI_KEY)
    def parse(self, response):
        news_data = response.css('div.uwU81')
        if news_data:
            for news_sample in news_data:
                meta_ = news_sample.css('div.VXBf7')
                meta_text = meta_.css('div.ZxBIG').get()
                text = meta_text[meta_text.find('>') + 1:meta_text.rfind('<')]
                date_time = ''
                srcc = ''
                if '/<!-- -->' in text:
                    date_time_text = text.split('/<!-- -->')
                    date_time = date_time_text[1]
                    srcc = date_time_text[0]
                    if len(date_time_text) == 1 :
                      date_time = date_time_text[0]
                      srcc = ''

                item = NewsItem()
                item['unique_id'] = str(uuid.uuid4())[:13]
                item['url'] = response.urljoin(news_sample.css('a').attrib['href'])
                item['headline'] = meta_.css('div.fHv_i span::text').get()
                item['Src'] = srcc
                item['date_time'] = date_time

                yield scrapy.Request(item['url'], callback=self.parse_news_page, meta={'item': item})

    def parse_news_page(self, response):
        item = response.meta['item']
        news_content = response.css('div.JuyWl ::text')
        if news_content:
            item['description'] = ' '.join(news_content.getall())
            item['len'] = len(item['description'])
            # item['summary'] =  self.openai_summarizer.summarize_text(item['description'])
            # item['len_summary'] = len(item['summary'])
        else:
            item['description'] = "premium news"
        yield item