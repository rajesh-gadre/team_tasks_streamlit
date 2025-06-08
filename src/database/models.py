from datetime import datetime
from typing import Dict, List, Optional, Any, Union
from enum import Enum

class TaskStatus(str, Enum):
    ACTIVE = 'active'
    COMPLETED = 'completed'
    DELETED = 'deleted'

class PromptStatus(str, Enum):
    ACTIVE = 'active'
    INACTIVE = 'inactive'

class Task:

    def __init__(self, id: Optional[str]=None, user_id: str=None, title: str=None, description: str=None, due_date: Optional[datetime]=None, status: str=TaskStatus.ACTIVE, created_at: Optional[datetime]=None, updated_at: Optional[datetime]=None, completion_date: Optional[datetime]=None, deletion_date: Optional[datetime]=None, notes: str=None, updates: List[Dict[str, Any]]=None):
        self.id = id
        self.user_id = user_id
        self.title = title
        self.description = description
        self.due_date = due_date
        self.status = status
        self.created_at = created_at
        self.updated_at = updated_at
        self.completion_date = completion_date
        self.deletion_date = deletion_date
        self.notes = notes
        self.updates = updates or []

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Task':
        return cls(id=data.get('id'), user_id=data.get('userId'), title=data.get('title'), description=data.get('description'), due_date=data.get('dueDate'), status=data.get('status', TaskStatus.ACTIVE), created_at=data.get('createdAt'), updated_at=data.get('updatedAt'), completion_date=data.get('completionDate'), deletion_date=data.get('deletionDate'), notes=data.get('notes'), updates=data.get('updates', []))

    def to_dict(self) -> Dict[str, Any]:
        data = {'userId': self.user_id, 'title': self.title, 'status': self.status}
        if self.id:
            data['id'] = self.id
        if self.description:
            data['description'] = self.description
        if self.due_date:
            data['dueDate'] = self.due_date
        if self.completion_date:
            data['completionDate'] = self.completion_date
        if self.deletion_date:
            data['deletionDate'] = self.deletion_date
        if self.notes:
            data['notes'] = self.notes
        if self.updates:
            data['updates'] = self.updates
        return data

    def validate(self) -> bool:
        if not self.user_id:
            raise ValueError('User ID is required')
        if not self.title:
            raise ValueError('Title is required')
        if self.status not in [s.value for s in TaskStatus]:
            raise ValueError(f'Invalid status: {self.status}')
        return True

class AIChat:

    def __init__(self, id: Optional[str]=None, user_id: str=None, input_text: str=None, created_at: Optional[datetime]=None, updated_at: Optional[datetime]=None, response: Optional[str]=None, feedback_rating: Optional[str]=None, feedback_text: Optional[str]=None, prompt_name: Optional[str]=None, prompt_version: Optional[int]=None):
        self.id = id
        self.user_id = user_id
        self.input_text = input_text
        self.created_at = created_at
        self.updated_at = updated_at
        self.response = response
        self.feedback_rating = feedback_rating
        self.feedback_text = feedback_text
        self.prompt_name = prompt_name
        self.prompt_version = prompt_version

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AIChat':
        return cls(id=data.get('id'), user_id=data.get('user_id'), input_text=data.get('inputText'), created_at=data.get('createdAt'), updated_at=data.get('updated_at'), response=data.get('Response'), feedback_rating=data.get('feedbackRating'), feedback_text=data.get('feedbackText'), prompt_name=data.get('prompt_name'), prompt_version=data.get('prompt_version'))

    def to_dict(self) -> Dict[str, Any]:
        data = {'user_id': self.user_id, 'inputText': self.input_text}
        if self.response:
            data['Response'] = self.response
        if self.feedback_rating is not None:
            data['feedbackRating'] = self.feedback_rating
        if self.feedback_text is not None:
            data['feedbackText'] = self.feedback_text
        if self.prompt_name is not None:
            data['prompt_name'] = self.prompt_name
        if self.prompt_version is not None:
            data['prompt_version'] = self.prompt_version
        return data

    def validate(self) -> bool:
        if not self.user_id:
            raise ValueError('User ID is required')
        if not self.input_text:
            raise ValueError('Input text is required')
        return True

class AIPrompt:

    def __init__(self, id: Optional[str]=None, prompt_name: str=None, text: str=None, status: str=PromptStatus.ACTIVE, version: int=1, created_at: Optional[datetime]=None, updated_at: Optional[datetime]=None):
        self.id = id
        self.prompt_name = prompt_name
        self.text = text
        self.status = status
        self.version = version
        self.created_at = created_at
        self.updated_at = updated_at

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AIPrompt':
        return cls(id=data.get('id'), prompt_name=data.get('prompt_name'), text=data.get('text'), status=data.get('status', PromptStatus.ACTIVE), version=data.get('version', 1), created_at=data.get('createdAt'), updated_at=data.get('updatedAt'))

    def to_dict(self) -> Dict[str, Any]:
        return {'prompt_name': self.prompt_name, 'text': self.text, 'status': self.status, 'version': self.version}

    def validate(self) -> bool:
        if not self.prompt_name:
            raise ValueError('Prompt name is required')
        if not self.text:
            raise ValueError('Prompt text is required')
        if self.status not in [s.value for s in PromptStatus]:
            raise ValueError(f'Invalid status: {self.status}')
        if self.version < 1:
            raise ValueError('Version must be >= 1')
        return True

class EvalStatus(str, Enum):
    ACTIVE = 'active'
    ARCHIVED = 'archived'

class AIEvalInput:

    def __init__(self, id: Optional[str]=None, user_id: str=None, input_text: str=None, response: Optional[str]=None, eval_prompt: str | None=None, status: str=EvalStatus.ACTIVE, created_at: Optional[datetime]=None, updated_at: Optional[datetime]=None):
        self.id = id
        self.user_id = user_id
        self.input_text = input_text
        self.response = response
        self.eval_prompt = eval_prompt
        self.status = status
        self.created_at = created_at
        self.updated_at = updated_at

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AIEvalInput':
        return cls(id=data.get('id'), user_id=data.get('user_id'), input_text=data.get('inputText'), response=data.get('Response'), eval_prompt=data.get('evalPrompt'), status=data.get('status', EvalStatus.ACTIVE), created_at=data.get('createdAt'), updated_at=data.get('updatedAt'))

    def to_dict(self) -> Dict[str, Any]:
        data = {'user_id': self.user_id, 'inputText': self.input_text, 'status': self.status}
        if self.response is not None:
            data['Response'] = self.response
        if self.eval_prompt is not None:
            data['evalPrompt'] = self.eval_prompt
        return data

    def validate(self) -> bool:
        if not self.user_id:
            raise ValueError('User ID is required')
        if not self.input_text:
            raise ValueError('Input text is required')
        if self.status not in [s.value for s in EvalStatus]:
            raise ValueError(f'Invalid status: {self.status}')
        return True

class AIEvalResult:

    def __init__(self, id: Optional[str]=None, eval_input_id: str | None=None, prompt_name: str | None=None, prompt_version: int | None=None, result: str | None=None, llm_judge_says: str | None=None, input_text: str | None=None, created_at: Optional[datetime]=None):
        self.id = id
        self.eval_input_id = eval_input_id
        self.prompt_name = prompt_name
        self.prompt_version = prompt_version
        self.result = result
        self.llm_judge_says = llm_judge_says
        self.input_text = input_text
        self.created_at = created_at

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AIEvalResult':
        return cls(id=data.get('id'), eval_input_id=data.get('eval_input_id'), prompt_name=data.get('prompt_name'), prompt_version=data.get('prompt_version'), result=data.get('result'), llm_judge_says=data.get('LLMJudgeSays'), input_text=data.get('inputText'), created_at=data.get('createdAt'))

    def to_dict(self) -> Dict[str, Any]:
        data = {'eval_input_id': self.eval_input_id, 'prompt_name': self.prompt_name, 'prompt_version': self.prompt_version, 'result': self.result}
        if self.llm_judge_says is not None:
            data['LLMJudgeSays'] = self.llm_judge_says
        if self.input_text is not None:
            data['inputText'] = self.input_text
        return data
