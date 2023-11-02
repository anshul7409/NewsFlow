import requests
from bs4 import BeautifulSoup as bs
from urllib.request import urlopen as uReq

news_cat_url =   "https://timesofindia.indiatimes.com/topic/" + "dehradun"

urlclient = uReq(news_cat_url)

news_page = urlclient.read()

news_html = bs(news_page,'html.parser')

boxes = news_html.findAll("div",{"class":"uwU81"})

lis = []
if (len(boxes))>0:
 for i in range((len(boxes))):
   lis.append(boxes[i].a['href'])
else:
   print("no news available")
   pass

news_html = []
for i in range(0,len(lis)):
   news_req = requests.get(lis[i])
   news_content = bs(news_req.text,'html.parser')
   box = news_content.find("div",{"class":"JuyWl"})
   news_html.append(box)

news_data = []
for element in news_html:
    if element is not None and hasattr(element, 'text'):
        news_data.append(element.text)
    else:
        news_data.append("N/A")

print(lis)
print(news_data)
print('hello')
print('anshul')
print('anshul')
print('anshul')