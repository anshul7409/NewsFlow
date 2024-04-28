from flask import Flask, request, jsonify, session
import scrapy
import re 
from Db_conn import get_collection
from scrapy.utils.project import get_project_settings
from scrapy.crawler import CrawlerProcess
import numpy as np
from sklearn.cluster import KMeans
from langchain_community.embeddings import HuggingFaceBgeEmbeddings

app = Flask(__name__)

model_name = "BAAI/bge-large-en-v1.5"
model_kwargs =  {"device" : "cpu"}
encode_kwargs  = {"normalize_embeddings":False}

embeddings = HuggingFaceBgeEmbeddings(
    model_name = model_name,
    model_kwargs = model_kwargs,
    encode_kwargs = encode_kwargs
)

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
    item = descriptions
    x=getdata(item)
    return jsonify({topic: x})


def getdata(item):

    vectors = embeddings.embed_documents([item for item in item])
    num_clusters = 4

    # Perform K-means clustering
    kmeans = KMeans(n_clusters=num_clusters, random_state=42).fit(vectors)
    # Find the closest embeddings to the centroids

    # Create an empty list that will hold your closest points
    closest_indices = []
    st = ""

    # Loop through the number of clusters you have
    for i in range(num_clusters):
        
        # Get the list of distances from that particular cluster center
        distances = np.linalg.norm(vectors - kmeans.cluster_centers_[i], axis=1)
        
        # Find the list position of the closest one (using argmin to find the smallest distance)
        closest_index = np.argmin(distances)
        
        # Append that position to your closest indices list
        closest_indices.append(closest_index)
    selected_indices = sorted(closest_indices)
    print(selected_indices)
    for i in selected_indices:
      st +=" "+ item[i]
    print(st)
    return st



if __name__ == "__main__": 
    app.run(debug=True)