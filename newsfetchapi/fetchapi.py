from flask import Flask, request, jsonify, session, redirect, url_for
import scrapy
from scrapy.crawler import CrawlerProcess
from scrapy.http import Request
from flask_bcrypt import Bcrypt
from pymongo import MongoClient
from dotenv import load_dotenv
from urllib.parse import quote_plus
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

    def __init__(self, topic=None, *args, **kwargs):
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
            return None
    def parse_news_page(self, response):
        item = response.meta['item']
        news_content = response.css('div.JuyWl ::text')
        if news_content:
            item['description'] = ' '.join(news_content.getall())
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

async def checkTopicName(topic):
    # Your implementation to check if the topic exists
    return True  # Return True for demonstration

async def getSummary(topic):
    # Your implementation to get the summary of the topic
    return f"Summary of {topic}"


@app.route("/search", methods=['POST'])
def search():
    # TODO: if topic not found return some message
    topic = request.args.get('topic')
    process = CrawlerProcess(settings={
        'FEED_FORMAT': 'json',
        'FEED_URI': 'output.json'
    })
    process.crawl(NewsSpider, topic=topic)
    process.start()
    with open('output.json', 'r') as f:
        data = f.read()

    return jsonify({'result': data})
    # exists = await checkTopicName(topic)
    # if not exists:
    #     return jsonify({'message' : "Topic not Found"}), 401
    
    # if 'email' in session:
    #     # TODO: If the user is logged in, save the topic name in its Topic array
    #     print("Topic is saved in User Data")

    # # Return the summary of the topic
    # summary = await getSummary(topic)
    # return jsonify({'message' : 'Topic is being searched', 'summary': summary}), 201

if __name__ == "__main__":
    app.run(debug=True)