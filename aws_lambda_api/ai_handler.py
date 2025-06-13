import json
from src.ai.llm_service import get_llm_service

def _response(status, body):
    return {'statusCode': status, 'body': json.dumps(body)}

def handler(event, context):
    service = get_llm_service()
    if event.get('httpMethod') == 'POST' and event.get('path') == '/chat':
        params = event.get('queryStringParameters') or {}
        user_id = params.get('user_id')
        data = json.loads(event.get('body') or '{}')
        text = data.get('text', '')
        result = service.process_chat(user_id, text)
        return _response(200, result)
    return _response(400, {'message': 'bad request'})

