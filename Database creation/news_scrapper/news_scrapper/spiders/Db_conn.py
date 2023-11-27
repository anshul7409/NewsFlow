import pymongo

def get_collection():
    client = pymongo.MongoClient(
        'mongodb+srv://anshulrawat74:newsprox@cluster0.fam8ldo.mongodb.net/?retryWrites=true&w=majority'
    )
    db = client['news']
    collection = db['news_tb']
    collection.create_index("description", unique=True)
    return collection