import json
from src.tasks.task_service import get_task_service

def _response(status, body):
    return {'statusCode': status, 'body': json.dumps(body)}

def handler(event, context):
    service = get_task_service()
    method = event.get('httpMethod')
    path = event.get('path', '')
    params = event.get('queryStringParameters') or {}
    user_id = params.get('user_id')
    if path == '/tasks' and method == 'GET':
        tasks = [t.to_dict() for t in service.get_all_tasks_for_user(user_id)]
        return _response(200, tasks)
    if path == '/tasks' and method == 'POST':
        data = json.loads(event.get('body') or '{}')
        task_id = service.create_task(user_id, data)
        return _response(200, {'id': task_id})
    if path.startswith('/tasks/'):
        task_id = path.split('/')[-1]
        if method == 'GET':
            task = service.get_task(user_id, task_id)
            if task:
                return _response(200, task.to_dict())
            return _response(404, {'message': 'not found'})
        if method == 'PUT':
            data = json.loads(event.get('body') or '{}')
            ok = service.update_task(user_id, task_id, data)
            return _response(200, {'success': ok})
        if method == 'DELETE':
            ok = service.delete_task(user_id, task_id)
            return _response(200, {'success': ok})
    return _response(400, {'message': 'bad request'})

