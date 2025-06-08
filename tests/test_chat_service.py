import sys
from pathlib import Path
from types import SimpleNamespace

sys.path.append(str(Path(__file__).resolve().parents[1]))
sys.path.append(str(Path(__file__).resolve().parents[1] / 'src'))

from ai.chat_service import delete_all_chats_one_by_one, get_all_chats


class DummyDoc:
    def __init__(self, doc_id, data, deleted, archive_calls):
        self.id = doc_id
        self._data = data
        self.reference = SimpleNamespace(delete=lambda: deleted.append(doc_id))
        self._archive_calls = archive_calls

    def to_dict(self):
        return self._data


class DummyCollection:
    def __init__(self, docs, archive_calls, deleted):
        self._docs = [DummyDoc(d[0], d[1], deleted, archive_calls) for d in docs]
        self.archive_calls = archive_calls

    def stream(self):
        for doc in self._docs:
            yield doc

    def document(self, doc_id):
        return SimpleNamespace(set=lambda data: self.archive_calls.append((doc_id, data)))


class DummyDB:
    def __init__(self, docs):
        self.deleted = []
        self.archive_calls = []
        self._source = DummyCollection(docs, self.archive_calls, self.deleted)
        self.archive = DummyCollection([], self.archive_calls, self.deleted)

    def collection(self, name):
        if name == 'AI_chats':
            return self._source
        return self.archive


def test_delete_all_chats(monkeypatch):
    docs = [('1', {'a': 1}), ('2', {'b': 2}), ('3', {'c': 3})]
    dummy_db = DummyDB(docs)
    monkeypatch.setattr('ai.chat_service.get_client', lambda: SimpleNamespace(db=dummy_db))
    delete_all_chats_one_by_one(2)
    assert dummy_db.deleted == ['1', '2']
    assert dummy_db.archive_calls == [('1', {'a': 1}), ('2', {'b': 2})]


def test_get_all_chats(monkeypatch):
    monkeypatch.setattr('ai.chat_service.get_client', lambda: SimpleNamespace(get_all=lambda c: [1, 2, 3]))
    result = get_all_chats()
    assert result == [1, 2, 3]
