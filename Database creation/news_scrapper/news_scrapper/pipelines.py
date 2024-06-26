# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from datetime import datetime
from .spiders.Db_conn import get_collection
import pymongo
import textwrap
from transformers import pipeline
import re


class NewsScrapperPipeline:
    def __init__(self):
        self.collection = get_collection()
        # summarizer = pipeline('summarization',model="sshleifer/distilbart-cnn-12-6")
        self.summarizer = pipeline('summarization',model="facebook/bart-large-cnn")
    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        length = self.collection.count_documents({})
        # Remove unwanted spaces and characters
        try:
            adapter['description'] = re.sub(r"\.", " .", adapter['description'])
            adapter['description'] = ' '.join(adapter['description'].split())
            adapter['Src'] = ' '.join(adapter['Src'].split())
            adapter['headline'] = adapter['headline'].strip()
            adapter['headline'] = ' '.join(adapter['headline'].split())
            adapter['description'] = re.sub(r"[^a-zA-Z. ]", '', adapter['description'])
            adapter['headline'] = re.sub(r"[^a-zA-Z ]", '', adapter['headline'])
        except ValueError:
            print("string is None-type")
        
        if adapter['len']>=2000:
            adapter['description'] = adapter['description'][0:2000]
            cut_off_index = adapter['description'].rfind('.')
            if cut_off_index != -1:  
                adapter['description'] = adapter['description'][:cut_off_index+1]
            adapter['len'] = len(adapter['description'])
 
        # Convert date_time to datetime object
        date_time_str = adapter['date_time'].strip()
        date_time_str = date_time_str.split(" (")[0] 
        try:
            adapter['date_time'] = datetime.strptime(date_time_str, '%b %d, %Y, %H:%M')
        except ValueError:
            spider.logger.error(f"Unable to parse date: {date_time_str}")
        
        #check if description already present or not
        if self.collection.find_one({"description": adapter['description']}):
                spider.logger.info(f"Item already exists: {adapter['description']}")
                return item,length  # Skip this item
        
        # Summarize the description
        description = adapter['description']
        summary = ""
        t = 3
        while t>0:
            chunks = textwrap.wrap(description, 800)
            res = self.summarizer(chunks,max_length = 120,min_length = 30,do_sample = False)
            summary = ' '.join([summ['summary_text'] for summ in res])
            description = summary
            t-=1
        adapter['summary'] = summary
        adapter['summary_len'] = len(summary) 
        
        # Saving data into database
        try:
            self.collection.insert_one(dict(item))
        except pymongo.errors.DuplicateKeyError:
            spider.logger.error(f"Duplicated item found: {item['date_time']}")
        return  length
    
    # 'mongodb+srv://anshulrawat74:newsprox@cluster0.fam8ldo.mongodb.net/?retryWrites=true&w=majority'