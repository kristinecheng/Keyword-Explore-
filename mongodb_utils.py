from pymongo import MongoClient
import pandas as pd

mongodb_client = MongoClient("mongodb://localhost:27017")
db = mongodb_client["academicworld"]

# Query 4: By selecting the time period (year), it shows the top 5 popular keywords of current year.
def mongo_get_top_10_keywords(year = 1982):
    query = [
        {"$match": {"year": {"$eq": year}}},
        {"$unwind": "$keywords"},
        {"$group": {"_id": "$keywords.name", "publication count": {"$sum": 1}}},
        {"$sort": {"publication count": -1}},
        {"$limit": 10}
    ]

    result = db["publications"].aggregate(query)

    result_keywords = pd.DataFrame(list(result)).rename(columns={"_id": "keyword", "publication count": "publication count"})

    return result_keywords.to_dict('records')
