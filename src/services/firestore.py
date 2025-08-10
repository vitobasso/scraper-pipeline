from google.cloud import firestore

_db = None


def db():
    global _db
    if not _db:
        _db = firestore.Client.from_service_account_json('gcp-secret.json', database="stocks-scraper-db")
    return _db


doc = db.collection('test').document("test")
doc.set({"hi": 1234})

for col in db.collections():
    print(col)
