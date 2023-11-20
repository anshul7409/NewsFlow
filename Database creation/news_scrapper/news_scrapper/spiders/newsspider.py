import scrapy


import scrapy

class NewsspiderSpider(scrapy.Spider):
    name = "newsspider"
    allowed_domains = ["timesofindia.indiatimes.com"]
    start_urls = ['https://timesofindia.indiatimes.com/topic/'+'tech']

    def parse(self, response):
        # Your scraping logic to extract data from the initial page
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
                
                    
                # Extracted data from the initial page
                item = {
                    'url': response.urljoin(news_sample.css('a').attrib['href']),
                    'headline': meta_.css('div.fHv_i span::text').get(),
                    'Src': srcc,
                    'date_time': date_time,
                }

                # Follow the URL and parse the news page
                yield scrapy.Request(item['url'], callback=self.parse_news_page, meta={'item': item})
        else:
            yield {'url':'','headline': '','Src':'','date_time': '','description':''}

    def parse_news_page(self, response):
        item = response.meta['item']
        # Add more fields to the item based on the data from the news page
        news_content = response.css('div.JuyWl ::text')
        if news_content:
           item['description'] = news_content.getall()
       # item['additional_field'] = response.css('div.additional_data::text').get()

        yield item
