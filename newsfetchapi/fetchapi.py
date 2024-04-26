from flask import Flask, request, jsonify, session, redirect, url_for
import scrapy
import re 
import textwrap
from flask_bcrypt import Bcrypt
from Db_conn import get_collection
from pymongo import MongoClient
from dotenv import load_dotenv
from urllib.parse import quote_plus
from datetime import datetime
import os
from transformers import pipeline
from scrapy.utils.project import get_project_settings
from multiprocessing import Process, Queue
from twisted.internet import reactor
import scrapy.crawler as crawler
from scrapy.utils.log import configure_logging


app = Flask(__name__)
bcrypt = Bcrypt(app)
load_dotenv()
username = os.getenv('USERNAME')
password = os.getenv('PASSWORD')
DATABASE_URI = "mongodb+srv://{}:{}@cluster0.dqwgi9f.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0".format(quote_plus(username), quote_plus(password))
app.secret_key = os.getenv('SECRET_KEY')
mongo_database = DATABASE_URI
client = MongoClient(mongo_database)
db = client['mydatabase']
users_collection = db['users']


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

@app.route("/register", methods=['POST'])
def register():
    email = request.form.get('email')
    password = request.form.get('password')
    print("Normal : " + password)
    if users_collection.find_one({'email': email}):
        return jsonify({'message': 'User already exists!'}), 400
    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
    print("hashed : " + hashed_password)
    user_data = {'email': email, 'password': hashed_password}
    user = users_collection.insert_one(user_data)
    print(user.inserted_id)
    return jsonify({'message': 'User registered successfully!'})

@app.route("/login", methods=['POST'])
def login():
    email = request.form.get('email')
    password = request.form.get('password')
    user = users_collection.find_one({'email': email})
    if user and bcrypt.check_password_hash(user['password'], password):
        session['email'] = email
        return jsonify({'message': 'Login successful!'})
    return jsonify({'message': 'Invalid email or password'}), 401

@app.route("/logout", methods=['POST'])
def logout():
    session.pop('email', None)
    return jsonify({'message': 'Logged out successfully!'})

@app.route("/profile", methods=['GET'])
def profile():
    if 'email' in session:
        return jsonify({'message': f'Welcome, {session["email"]}!'})
    return jsonify({'message': 'You are not logged in'}), 401

def run_spider(topic,email,ref_ids,q):
    try:
        configure_logging()
        runner = crawler.CrawlerRunner()
        deferred = runner.crawl(NewsSpider,topic=topic, username=email, ref_id=ref_ids)
        deferred.addBoth(lambda _: reactor.stop())
        reactor.run()
        q.put(ref_ids)
    except Exception as e:
        q.put(e)

@app.route("/search", methods=['POST'])
def search():
    ref_ids = []
    topic = request.args.get('topic')
    email = session.get('email')
    q = Queue()
    p = Process(target=run_spider, args=(topic,email,ref_ids,q))
    p.start()
    p.join()
    ref_ids = q.get()
    # print(ref_ids)
    if isinstance(ref_ids, Exception):
        raise ref_ids  
    x = users_collection.find_one({"email": email})
    notpresent = 1
    if 'topics' in x:
        dbtopic = x['topics']
        for topic_dict in dbtopic:
            if topic_dict['topic_name'] == topic:
                users_collection.update_one(
                    {'email': email, 'topics.topic_name': topic},
                    {'$set': {'topics.$.topic_id': ref_ids}}
                )
                notpresent = 0
                break  
    # If 'topics' field doesn't exist, create a new document with the specified email and topic
    if notpresent:
        users_collection.update_one(
            {'email': email},
            {'$addToSet': {"topics": {"topic_id": ref_ids, "topic_name": topic}}},
                upsert=True
        )
    print("Crawling done")
    if email is None:
        return jsonify({"error": "User not authenticated"}), 401
    print(ref_ids)
    return jsonify({"topic_name": topic, "topic_id": [str(ref_id) for ref_id in ref_ids]})

if __name__ == "__main__": 
    app.run(debug=True)