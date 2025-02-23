import dbm
import pickle


class DBMHelper:
    DB_PATH = "./data/crawled_comps"
    
    def __init__(self) -> None:
        pass
    
    @staticmethod
    def is_visited(url):
        with dbm.open(DBMHelper.DB_PATH, 'c') as db:
            return url.encode('utf-8') in db
    
    @staticmethod
    def mark_as_visited(url, data):
        with dbm.open(DBMHelper.DB_PATH, 'c') as db:
            db[url.encode('utf-8')] = pickle.dumps(data)

