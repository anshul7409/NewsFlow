from celery import Celery
from flask import  jsonify
from scrapy.crawler import CrawlerProcess
from Db_conn import get_collection
import scrapy
from scrapy.crawler import CrawlerProcess
import re 
import textwrap
from Db_conn import get_collection
import pymongo
from datetime import datetime
from transformers import pipeline
import redis


redis_client = redis.StrictRedis(host='localhost', port=6379, db=0)
app = Celery('tasks', broker='redis://localhost:6379/0')

class NewsSpider(scrapy.Spider):
    name = "newsspider"
    allowed_domains = ["timesofindia.indiatimes.com"]

    def __init__(self, topic=None, username=None,ref_id = None, *args, **kwargs):
        self.collection = get_collection()
        self.username = username
        self.topic = topic
        self.ref_ids = ref_id
        self.summarizer = pipeline('summarization',model="facebook/bart-large-cnn")
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
                        meta_ = news_sample.css('div.VXBf7')
                        meta_text = meta_.css('div.ZxBIG').get()
                        text = meta_text[meta_text.find('>') + 1:meta_text.rfind('<')]
                        date_time = ''
                        if '/<!-- -->' in text:
                            date_time_text = text.split('/<!-- -->')
                            date_time = date_time_text[1]
                            srcc = date_time_text[0]
                            if len(date_time_text) == 1 :
                              date_time = date_time_text[0]
                              srcc = ''
                        item = {}
                        item['url'] = response.urljoin(news_sample.css('a').attrib['href'])
                        item['headline'] = meta_.css('div.fHv_i span::text').get()
                        item['Src'] = srcc
                        item['date_time'] = date_time
                        yield scrapy.Request(item['url'], callback=self.parse_news_page, meta={'item': item})
        except:
            return {}
    
    def parse_news_page(self, response):
        item = response.meta['item']
        news_content = response.css('div.JuyWl ::text')
        if news_content and item['date_time'] and item['headline'] and item['Src'] and item['url']:
            item['description'] = ' '.join(news_content.getall())
            item['len'] = len(item['description'])
            # Remove unwanted spaces and characters
            item['description'] = re.sub(r"\.", " .", item['description'])
            item['description'] = ' '.join(item['description'].split())
            item['Src'] = ' '.join(item['Src'].split())
            item['headline'] = item['headline'].strip()
            item['headline'] = ' '.join(item['headline'].split())
            item['description'] = re.sub(r"[^a-zA-Z. ]", '', item['description'])
            item['headline'] = re.sub(r"[^a-zA-Z ]", '', item['headline'])
            if item['len']>=2000:
                item['description'] = item['description'][0:2000]
                cut_off_index = item['description'].rfind('.')
                if cut_off_index != -1:  
                    item['description'] = item['description'][:cut_off_index+1]
                item['len'] = len(item['description'])
        date_time_str = item['date_time'].strip()
        date_time_str = date_time_str.split(" (")[0] 
        item['date_time'] = datetime.strptime(date_time_str, '%b %d, %Y, %H:%M')
        topicitem = self.collection.find_one({"description": item['description']})
        if topicitem:
                print(f"Item already exists: {item['description']}")
                id = topicitem["_id"]
                if id not in self.ref_ids:
                   self.ref_ids.append(id)
        else:
            # Summarize the description
                description = item['description']
                summary = ""
                t = 3
                while t>0:
                    chunks = textwrap.wrap(description, 800)
                    res = self.summarizer(chunks,max_length = 120,min_length = 30,do_sample = False)
                    summary = ' '.join([summ['summary_text'] for summ in res])
                    description = summary
                    t-=1
                item['summary'] = summary
                item['summary_len'] = len(summary) 

                # Saving data into database
                x =  self.collection.insert_one(dict(item))
                id = x.inserted_id
                if id not in self.ref_ids:
                    self.ref_ids.append(id)
        yield item


@app.task
def scrape_news(topic, email,ref_ids):
    # process = CrawlerProcess(settings={
    #     'FEED_FORMAT': 'json',
    # })
    # process.crawl(NewsSpider, topic=topic, username=username)
    # process.start()
    process = CrawlerProcess(settings={
        'FEED_FORMAT': 'json',
    })
    process.crawl(NewsSpider, topic=topic,username=email,ref_id = ref_ids)
    process.start()
    print(ref_ids)
    redis_client.set('ref_ids', ','.join(ref_ids))
    return ref_ids

