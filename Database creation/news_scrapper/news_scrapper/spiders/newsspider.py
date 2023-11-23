import scrapy
# from .config import Config
# import openai_summarize
from news_scrapper.items import NewsItem

class NewsspiderSpider(scrapy.Spider):
    name = "newsspider"
    allowed_domains = ["timesofindia.indiatimes.com"]
    topics = [
    "Climate-Change",
    "COVID-19-Updates",
    "Global-Economy",
    "Artificial-Intelligence",
    "Space-Exploration",
    "Cybersecurity",
    "Renewable-Energy",
    "Politics",
    "Vaccination-Campaigns",
    "Social-Media-Trends",
    "Environmental-Conservation",
    "Emerging-Technologies",
    "Healthcare-Policies",
    "Education-Reforms",
    "International-Relations",
    "Stock-Market-Trends",
    "Natural-Disasters",
    "Immigration-Issues",
    "5G-Technology",
    "Sustainable-Living",
    "Human-Rights",
    "Artificial-General-Intelligence",
    "Robotics-Advancements",
    "Wildlife-Conservation",
    "Genetic-Engineering",
    "Future-of-Work",
    "Mental-Health-Awareness",
    "Cryptocurrency-Updates",
    "Climate-Action-Initiatives",
    "Social-Justice-Movements",
    "Data-Privacy-Concerns",
    "Electric-Vehicles",
    "International-Trade-Agreements",
    "Cultural-Events",
    "Health-Tech-Innovations",
    "Quantum-Computing",
    "Internet-of-Things-(IoT)",
    "Artificial-Neural-Networks",
    "Autonomous-Vehicles",
    "Biomedical-Breakthroughs",
    "Geopolitical-Tensions",
    "Augmented-Reality",
    "Mental-Wellness-Programs",
    "Renewable-Energy-Policies",
    "Augmented-Reality",
    "Social-Impact-Initiatives",
    "3D-Printing-Advancements",
    "Aerospace-Developments",
    "Sustainable-Agriculture",
    "Digital-Transformation",
    "Future-of-Transportation",
    "Quantum-Physics-Discoveries",
    "Gaming-Industry-Trends",
    "Nuclear-Energy-Policies",
    "Sustainable-Fashion",
    "Genetic-Privacy-Debates",
    "Smart-Cities-Initiatives",
    "Ocean-Conservation",
    "Future-of-Banking",
    "Artificial-Superintelligence",
    "Behavioral-Economics",
    "Precision-Medicine",
    "Cryptocurrency-Regulations",
    "Mental-Health-in-Tech",
    "Climate-Resilience-Strategies",
    "Telemedicine-Advances",
    "Blockchain-Applications",
    "Green-Technology",
    "Social-Media-Regulation",
    "Quantum-Cryptography",
    ]


    start_urls = ['https://timesofindia.indiatimes.com/topic/'+ topic for topic in topics]
    # openai_summarizer = openai_summarize.OpenAISummarize(Config.OPENAI_KEY)

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

                item = NewsItem()
                item['url'] = response.urljoin(news_sample.css('a').attrib['href'])
                item['headline'] = meta_.css('div.fHv_i span::text').get()
                item['Src'] = srcc
                item['date_time'] = date_time
                if item['date_time'] == '' or item['headline'] == '' or item['Src'] == '':
                    item['date_time'] = None
                    item['headline'] = None
                    item['Src'] = None
                yield scrapy.Request(item['url'], callback=self.parse_news_page, meta={'item': item})

    def parse_news_page(self, response):
        item = response.meta['item']
        news_content = response.css('div.JuyWl ::text')
        if news_content:
            item['description'] = ' '.join(news_content.getall())                                   
            item['len'] = len(item['description'])
        else:
            item['description'] = "premium news"
        yield item

# scrapy crawl newsspider -o news1.csv
# o -> appending , O -> overwriting