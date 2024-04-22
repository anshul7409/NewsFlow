from flask import Flask, request, jsonify, session, redirect, url_for
import scrapy
from scrapy.crawler import CrawlerProcess
from scrapy.http import Request
from flask_bcrypt import Bcrypt
from pymongo import MongoClient
from dotenv import load_dotenv
from urllib.parse import quote_plus
from datetime import datetime
import os

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

    def __init__(self, topic=None, username=None, *args, **kwargs):
        self.username = username
        self.topic = topic
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
                            if len(date_time_text) == 1:
                                date_time = date_time_text[0]
                        item = {
                            'url': response.urljoin(news_sample.css('a').attrib['href']),
                            'date_time': date_time
                        }
                        yield Request(item['url'], callback=self.parse_news_page, meta={'item': item})
        except:
            return {}
    def parse_news_page(self, response):
        item = response.meta['item']
        news_content = response.css('div.JuyWl ::text')
        if news_content and item['date_time']:
            date_time_str = item['date_time'].strip()
            date_time_str = date_time_str.split(" (")[0] 
            item['description'] = ' '.join(news_content.getall())
            item['date_time'] = datetime.strptime(date_time_str, '%b %d, %Y, %H:%M')
            #summarize function
            users_collection.update_one({'email': self.username},{'$addToSet': {self.topic: item}},upsert=True)
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
    users_collection.insert_one(user_data)
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

@app.route("/search", methods=['POST'])
def search():
    # TODO: if topic not found return some message
    email = request.form['username']
    topic = request.args.get('topic')
    process = CrawlerProcess(settings={
        'FEED_FORMAT': 'json',
    })
    process.crawl(NewsSpider, topic=topic,username=email)
    process.start()
    user_document = users_collection.find_one({'email':email})
    print(user_document[topic])
    return jsonify({ topic : user_document[topic]})    

if __name__ == "__main__":
    app.run(debug=True)