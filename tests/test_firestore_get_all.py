import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[1] / 'src'))
from database.firestore import FirestoreClient

class DummyDoc:

    def __init__(self, doc_id, data):
        self.id = doc_id
        self._data = data

    def to_dict(self):
        return self._data

class DummyDB:

    def __init__(self, docs):
        self._docs = docs

    def collection(self, _):
        return self

    def stream(self):
        for doc in self._docs:
            yield doc

def test_get_all_adds_id():
    docs = [DummyDoc('1', {'a': 1}), DummyDoc('2', {'b': 2})]
    fc = FirestoreClient.__new__(FirestoreClient)
    fc.db = DummyDB(docs)
    result = fc.get_all('c')
    assert result == [{'a': 1, 'id': '1'}, {'b': 2, 'id': '2'}]
