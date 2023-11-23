# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from datetime import datetime
import pymongo
import re

class NewsScrapperPipeline:
    def __init__(self) :
        self.conn = pymongo.MongoClient(
            'localhost',
            27017
        )
        db = self.conn['news']
        self.collection = db['news_tb']
        self.collection.create_index("date_time", unique=True)

    def process_item(self, item, spider):
        adapter = ItemAdapter(item)

        # Remove unwanted spaces 
        try:
            adapter['description'] = ' '.join(adapter['description'].split())
            adapter['Src'] = ' '.join(adapter['Src'].split())
            adapter['headline'] = adapter['headline'].strip()
            adapter['headline'] = ' '.join(adapter['headline'].split())
            # Remove unwanted characters from description
            adapter['description'] = re.sub(r"[^a-zA-Z ]", '', adapter['description'])
        except ValueError:
            print("string is nonetype")
        
        if adapter['len']>=2000:
            adapter['description'] = adapter['description'][0:2000]
            adapter['len'] = 2000

        # Convert date_time to datetime object
        date_time_str = adapter['date_time'].strip()
        date_time_str = date_time_str.split(" (")[0] 
        try:
            adapter['date_time'] = datetime.strptime(date_time_str, '%b %d, %Y, %H:%M')
        except ValueError:
            spider.logger.error(f"Unable to parse date: {date_time_str}")
        
        try:
            self.collection.insert_one(dict(item))
        except pymongo.errors.DuplicateKeyError:
            spider.logger.error(f"Duplicated item found: {item['date_time']}")
        return item