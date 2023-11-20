import scrapy


import scrapy

class NewsspiderSpider(scrapy.Spider):
    name = "newsspider"
    allowed_domains = ["timesofindia.indiatimes.com"]
    start_urls = ['https://timesofindia.indiatimes.com/topic/'+'tech']

    def parse(self, response):
        # Your scraping logic to extract data from the initial page
        news_data = response.css('div.uwU81')

        for news_sample in news_data:
            meta_ = news_sample.css('div.VXBf7')
            meta_text = meta_.css('div.ZxBIG').get()
            text = meta_text[meta_text.find('>') + 1:meta_text.rfind('<')]
            date_time = ''
            if '/<!-- -->' in text:
                date_time = text.split('/<!-- -->')[1]
            
            # Extracted data from the initial page
            item = {
                'url': response.urljoin(news_sample.css('a').attrib['href']),
                'headline': meta_.css('div.fHv_i span::text').get(),
                'Src': meta_.css('div.ZxBIG::text').get(),
                'date_time': date_time,
            }

            # Follow the URL and parse the news page
            yield item
            
            # scrapy.Request(item['url'], callback=self.parse_news_page, meta={'item': item})

    # def parse_news_page(self, response):
    #     # Your scraping logic to extract data from the news page
    #     # Use response.xpath or response.css to extract data from the news page
    #     # You can access the item passed from the parse method using response.meta['item']
    #     item = response.meta['item']
    #     # Add more fields to the item based on the data from the news page
    #     item['additional_field'] = response.css('div.additional_data::text').get()

    #     yield item
