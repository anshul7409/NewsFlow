from flask import Flask, request, jsonify, session
import scrapy
import re 
from Db_conn import get_collection
from scrapy.utils.project import get_project_settings
from scrapy.crawler import CrawlerProcess

app = Flask(__name__)

class NewsSpider(scrapy.Spider):
    name = "newsspider"
    allowed_domains = ["timesofindia.indiatimes.com"]

    def __init__(self, topic=None, descriptions=None, *args, **kwargs):
        self.collection = get_collection()
        self.topic = topic
        self.description = descriptions
        super(NewsSpider, self).__init__(*args, **kwargs)
        self.start_urls = [
            'https://timesofindia.indiatimes.com/topic/' + topic
        ]

    def parse(self, response):
        try:
            if str(response)[5:].startswith("https://timesofindia"):
                news_data = response.css('div.uwU81')
                if news_data:
                    for news_sample in news_data:
                        item = {}
                        item['url'] = response.urljoin(news_sample.css('a').attrib['href'])
                        yield scrapy.Request(item['url'], callback=self.parse_news_page, meta={'item': item})
        except:
            return {}
    
    def parse_news_page(self, response):
        item = response.meta['item']
        news_content = response.css('div.JuyWl ::text')
        if news_content:
            item['description'] = ' '.join(news_content.getall())
            # Remove unwanted spaces and characters
            item['description'] = re.sub(r"\.", " .", item['description'])
            item['description'] = ' '.join(item['description'].split())
            item['description'] = re.sub(r"[^a-zA-Z. ]", '', item['description'])
            self.description.append(item['description'])
        yield item

@app.route("/search", methods=['POST'])
def search():
    descriptions = []
    topic = request.args.get('topic')
    process = CrawlerProcess(settings=get_project_settings())
    process.crawl(NewsSpider, topic=topic, descriptions=descriptions)
    process.start()
    item = {topic : descriptions}
    getdata(item)
    return jsonify({topic: descriptions})

def getdata(item):
    print(item)

if __name__ == "__main__": 
    app.run(debug=True)