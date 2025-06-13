import sys
import json
from pathlib import Path
root = Path(__file__).resolve().parents[1]
sys.path.append(str(root))
sys.path.append(str(root / 'aws_lambda_api'))
from ai_handler import handler

class DummyService:
    def __init__(self):
        self.calls = []
    def process_chat(self, uid, text):
        self.calls.append((uid, text))
        return {'chat_id': 'c', 'response': 'ok'}

def _run(event, monkeypatch, service):
    monkeypatch.setattr('ai_handler.get_llm_service', lambda: service)
    return handler(event, None)

def test_chat(monkeypatch):
    service = DummyService()
    event = {
        'httpMethod': 'POST',
        'path': '/chat',
        'queryStringParameters': {'user_id': 'u'},
        'body': json.dumps({'text': 'hi'})
    }
    result = _run(event, monkeypatch, service)
    assert json.loads(result['body']) == {'chat_id': 'c', 'response': 'ok'}
    assert service.calls == [('u', 'hi')]

