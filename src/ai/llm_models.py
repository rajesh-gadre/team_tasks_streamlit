import json
from typing import List, Optional
from pydantic import BaseModel

class FirestoreEncoder(json.JSONEncoder):
    def default(self, obj):
        if hasattr(obj, 'isoformat'):
            return obj.isoformat()
        try:
            return str(obj)
        except:
            return None

class NewTask(BaseModel):
    title: str
    description: Optional[str] = None
    notes: Optional[str] = None
    due_date: Optional[str] = None

class ModifiedTask(BaseModel):
    id: str
    title: Optional[str] = None
    description: Optional[str] = None
    notes: Optional[str] = None
    due_date: Optional[str] = None
    status: Optional[str] = None

class TaskChanges(BaseModel):
    new_tasks: List[NewTask]
    modified_tasks: List[ModifiedTask]
