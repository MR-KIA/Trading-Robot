from pymongo import MongoClient
import datetime


def db():
    client = MongoClient('mongodb://localhost:27017/')
    db = client['trading_db']

    return db
