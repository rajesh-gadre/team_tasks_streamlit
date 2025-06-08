import sys
from pathlib import Path
root = Path(__file__).resolve().parents[1]
sys.path.append(str(root / 'src'))
from database.firestore import FirestoreClient

class DummyFilter:

    def __init__(self, field, op, value):
        self.field = field
        self.op_string = op
        self.value = value

class DummyDoc:

    def __init__(self, doc_id, data):
        self.id = doc_id
        self._data = data
        self.exists = True

    def to_dict(self):
        return self._data

class DummyQuery:

    def __init__(self, docs):
        self.docs = docs
        self.calls = []

    def where(self, filter=None):
        self.calls.append(('where', filter.field, filter.op_string, filter.value))
        return self

    def order_by(self, field, direction=None):
        self.calls.append(('order_by', field, direction))
        return self

    def limit(self, n):
        self.calls.append(('limit', n))
        return self

    def stream(self):
        return self.docs

class DummyDB:

    def __init__(self, docs):
        self.docs = docs
        self.query_obj = DummyQuery(docs)

    def collection(self, name):
        self.last_collection = name
        return self.query_obj

def test_query_builds(monkeypatch):
    fc = FirestoreClient.__new__(FirestoreClient)
    fc.db = DummyDB([DummyDoc('1', {'a': 1})])
    monkeypatch.setattr('database.firestore.FieldFilter', DummyFilter)
    monkeypatch.setattr('database.firestore.firestore', type('F', (), {'Query': type('Q', (), {'ASCENDING': 'ASC', 'DESCENDING': 'DESC'})}))
    result = fc.query('c', filters=[('f', '==', 'v')], order_by='ts', direction='DESCENDING', limit=1)
    assert result == [{'a': 1, 'id': '1'}]
    calls = fc.db.query_obj.calls
    assert calls[0][:3] == ('where', 'f', '==')
    assert calls[1] == ('order_by', 'ts', 'DESC')
    assert calls[2] == ('limit', 1)
