import scrapy
import uuid

class NewsspiderSpider(scrapy.Spider):
    name = "newsspider"
    allowed_domains = ["timesofindia.indiatimes.com"]
    start_urls = ['https://timesofindia.indiatimes.com/topic/'+'isreal']

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
                
                item = {
                    'unique_id': str(uuid.uuid4())[:8],  # Generate a unique ID for each item and take the first 8 characters
                    'url': response.urljoin(news_sample.css('a').attrib['href']),
                    'headline': meta_.css('div.fHv_i span::text').get(),
                    'Src': srcc,
                    'date_time': date_time,
                }

                yield scrapy.Request(item['url'], callback=self.parse_news_page, meta={'item': item})
        else:
            yield {'unique_id': str(uuid.uuid4())[:8], 'url':'','headline': '','Src':'','date_time': '','description':''}

    def parse_news_page(self, response):
        item = response.meta['item']
        news_content = response.css('div.JuyWl ::text')
        if news_content:
           item['description'] = news_content.getall()
        else:
           item['description'] = ["N/A"] 
        yield item