from transformers import pipeline
import os
import numpy as np
import scrapy
import re
from flask import Flask, request, jsonify
from transformers import AutoTokenizer
from sklearn.cluster import KMeans
from sentence_transformers import SentenceTransformer
from flask_cors import CORS
from multiprocessing import Process, Queue
from twisted.internet import reactor
from scrapy.utils.log import configure_logging
import scrapy.crawler as crawler



os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'
model = SentenceTransformer('all-mpnet-base-v2')
tokenizer = AutoTokenizer.from_pretrained("tokenizer")
pipe = pipeline("summarization", model="Multinews-summ-model",tokenizer=tokenizer)
model_name = "BAAI/bge-large-en-v1.5"


app = Flask(__name__)
CORS(app)

class NewsSpider(scrapy.Spider):
    name = "newsspider"
    allowed_domains = ["timesofindia.indiatimes.com"]

    def __init__(self, topic=None, descriptions=None, *args, **kwargs):
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
            if len(item['description'])>=500:
                item['description'] = item['description'][0:500]
                cut_off_index = item['description'].rfind('.')
                if cut_off_index != -1:  
                    item['description'] = item['description'][:cut_off_index+1]
            item['description'] = re.sub(r"\.", " .", item['description'])
            item['description'] = ' '.join(item['description'].split())
            item['description'] = re.sub(r"[^a-zA-Z. ]", '', item['description'])
            self.description.append(item['description'])
        yield item

def summarize(description):
    gen_kwargs = {"length_penalty": 0.9, "num_beams":8, "max_length": 128}
    summ = pipe(description, **gen_kwargs)[0]["summary_text"]
    return summ


def run_spider(topic,descriptions,q):
    try:
        configure_logging()
        runner = crawler.CrawlerRunner()
        deferred = runner.crawl(NewsSpider,topic=topic, descriptions=descriptions)
        deferred.addBoth(lambda _: reactor.stop())
        reactor.run()
        q.put(descriptions)
    except Exception as e:
        q.put(e)

def Map_reduce_and_clustering(item):
    vec = model.encode([item for item in item])
    vec.tolist()
    num_clusters = 5
    kmeans = KMeans(n_clusters=num_clusters, random_state=42).fit(vec)
    closest_indices = []
    for i in range(num_clusters):
        # Get the list of distances from that particular cluster center
        distances = np.linalg.norm(vec - kmeans.cluster_centers_[i], axis=1)
        # Find the list position of the closest one (using argmin to find the smallest distance)
        closest_index = np.argmin(distances)
        # Append that position to your closest indices list
        closest_indices.append(closest_index)
    selected_indices = sorted(closest_indices)
    text = ""
    for i in selected_indices:
        text +=  item[i]
    return text 

@app.route("/get_summ", methods=['POST'])
def get_summ():
    descriptions = []
    topic = request.args.get('topic')
    #handline multiple requests
    q = Queue()
    p = Process(target=run_spider, args=(topic,descriptions,q))
    p.start()
    p.join()
    descriptions = q.get()
    #Map reduce and clustering
    text = Map_reduce_and_clustering(descriptions)
    #Summarization:
    summ = summarize(text)
    return jsonify({"description":text,"summary":summ})
    
if __name__ == '__main__':
    app.run(debug=True)