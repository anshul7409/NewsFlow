# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from datetime import datetime
import re

class NewsScrapperPipeline:
    def process_item(self, item, spider):
        adapter = ItemAdapter(item)

        # Remove unwanted spaces 
        adapter['description'] = ' '.join(adapter['description'].split())
        adapter['Src'] = ' '.join(adapter['Src'].split())

        # Remove unwanted characters from description
        adapter['description'] = re.sub(r"[^a-zA-Z ]", '', adapter['description'])

        # Convert date_time to datetime object
        date_time_str = adapter['date_time'].strip()
        date_time_str = date_time_str.split(" (")[0] 
        try:
            adapter['date_time'] = datetime.strptime(date_time_str, '%b %d, %Y, %H:%M')
        except ValueError:
            spider.logger.error(f"Unable to parse date: {date_time_str}")

        return item