# Engineering Design Document (EDD)
# User Task Management System with Soft-Delete

## 1. System Architecture

### 1.1 Overview
The User Task Management System will be built using Streamlit for the frontend and Firebase Firestore as the backend database. The system will follow a client-server architecture where Streamlit serves as both the UI framework and the server-side application.

### 1.2 Architecture Diagram
```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│                 │     │                 │     │                 │
│  Streamlit UI   │◄────┤  Streamlit      │◄────┤  Firebase       │
│  Components     │     │  Backend Logic  │     │  Firestore      │
│                 │     │                 │     │                 │
└─────────────────┘     └─────────────────┘     └─────────────────┘
        ▲                       ▲                       ▲
        │                       │                       │
        │                       │                       │
        ▼                       ▼                       ▼
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│                 │     │                 │     │                 │
│  Google OAuth   │     │  OpenAI API     │     │  Langchain      │
│  Authentication │     │  (via Langchain)│     │  Framework      │
│                 │     │                 │     │                 │
└─────────────────┘     └─────────────────┘     └─────────────────┘
```

### 1.3 Technology Stack
- **Frontend**: Streamlit
- **Backend**: Python with Streamlit
- **Database**: Firebase Firestore
- **Authentication**: Google OAuth
- **AI Integration**: Langchain with OpenAI

## 2. Database Design

### 2.1 Firestore Collections

#### 2.1.1 Tasks Collection
```
Collection: tasks
Document:
{
  id: string (Firestore auto-generated),
  userId: string,
  title: string,
  description: string (optional),
  dueDate: timestamp (optional),
  status: string (enum: 'active', 'completed', 'deleted'),
  createdAt: timestamp,
  updatedAt: timestamp,
  completionDate: timestamp (optional),
  deletionDate: timestamp (optional),
  notes: string (optional),
  updates: [
    {
      timestamp: timestamp,
      user: string,
      updateText: string
    }
  ]
}
```

#### 2.1.2 AI_chats Collection
```
Collection: AI_chats
Document:
{
  user_id: string,
  inputText: string,
  createdAt: timestamp,
  updated_at: timestamp,
  Response: string,
  prompt_name: string,
  prompt_version: number
}
```

#### 2.1.3 AI_prompts Collection
```
Collection: AI_prompts
Document:
{
  prompt_name: string,
  text: string,
  status: string (enum: 'active', 'inactive')
}
```

### 2.2 Indexes and Query Optimization
- Create composite index on `tasks` collection for `userId` and `status` fields
- Create index on `AI_prompts` collection for `prompt_name` and `status` fields

## 3. Component Design

### 3.1 Authentication Module
- Implement Google OAuth authentication
- Generate and manage JWT tokens
- Store tokens in browser local storage
- Validate tokens for all API requests
- Implement session management

### 3.2 Task Management Module
- Task creation and validation
- Task retrieval with filtering
- Task update with history tracking
- Soft-delete implementation
- Task restoration

### 3.3 UI Components
- Navigation bar with tabs for different views
- Task list component with filtering
- Task detail component
- Task form component for creation/editing
- AI chat interface

### 3.4 AI Integration Module
- OpenAI integration via Langchain
- Prompt management
- Response processing
- Chat history storage

## 4. API Design

### 4.1 Streamlit Backend Functions

#### 4.1.1 Authentication Functions
```python
def login_with_google():
    # Implement Google OAuth login
    pass

def validate_token(token):
    # Validate JWT token
    pass

def get_current_user():
    # Get current authenticated user
    pass
```

#### 4.1.2 Task Management Functions
```python
def get_active_tasks(user_id):
    # Query tasks where userId == user_id and status == 'active'
    pass

def get_completed_tasks(user_id):
    # Query tasks where userId == user_id and status == 'completed'
    pass

def get_deleted_tasks(user_id):
    # Query tasks where userId == user_id and status == 'deleted'
    pass

def create_task(user_id, task_data):
    # Add new task document to tasks collection
    pass

def update_task(user_id, task_id, task_data):
    # Update task document if userId matches
    pass

def delete_task(user_id, task_id):
    # Set status to 'deleted', update updatedAt and deletionDate
    pass

def restore_task(user_id, task_id):
    # Set status to 'active', update updatedAt
    pass
```

#### 4.1.3 AI Functions
```python
def process_ai_chat(user_id, input_text):
    # Store chat in AI_chats collection
    # Get prompt from AI_prompts collection
    # Process with OpenAI via Langchain
    # Update chat record with response
    # Return response
    pass

def get_ai_prompt(prompt_name):
    # Get active prompt by name
    pass
```

## 5. Firestore Integration

### 5.1 Initialization
```python
def initialize_firestore():
    # Load credentials from environment variables
    # Initialize Firestore client
    pass
```

### 5.2 CRUD Operations
```python
def firestore_create(collection, document_data):
    # Create document in collection
    pass

def firestore_read(collection, document_id=None, query=None):
    # Read document(s) from collection
    pass

def firestore_update(collection, document_id, update_data):
    # Update document in collection
    pass

def firestore_delete(collection, document_id):
    # Delete document from collection
    pass
```

## 6. Security Implementation

### 6.1 Authentication Security
- Implement proper token validation
- Secure storage of tokens
- Regular token refresh

### 6.2 Data Access Security
- Validate user ownership of tasks before all operations
- Implement Firestore security rules
- Sanitize all user inputs

### 6.3 Environment Variable Management
- Securely store Firebase credentials
- Securely store OpenAI API keys
- Implement proper environment variable loading

## 7. Error Handling and Logging

### 7.1 Error Handling Strategy
- Implement try-except blocks for all Firestore operations
- Provide clear error messages to users
- Implement fallback mechanisms where appropriate

### 7.2 Logging Implementation
```python
def setup_logging(level):
    # Configure logging based on level
    pass

def log_operation(operation, user_id, details, error=None):
    # Log operation with details
    pass
```

## 8. Testing Strategy

### 8.1 Unit Testing
- Test individual functions and components
- Mock Firestore and OpenAI interactions
- Validate data transformations

### 8.2 Integration Testing
- Test authentication flow
- Test task CRUD operations
- Test AI chat functionality

### 8.3 End-to-End Testing
- Test complete user flows
- Validate UI interactions
- Test error scenarios

## 9. Deployment Considerations

### 9.1 Environment Setup
- Python environment with required dependencies
- Firebase project configuration
- Environment variables configuration

### 9.2 Deployment Options
- Local deployment for development
- Cloud deployment options (Streamlit Cloud, Heroku, etc.)
- Docker containerization option

## 10. Implementation Plan

### 10.1 Phase 1: Core Infrastructure
- Set up project structure
- Implement Firestore integration
- Implement authentication

### 10.2 Phase 2: Task Management
- Implement task CRUD operations
- Implement UI components for task management
- Implement soft-delete functionality

### 10.3 Phase 3: AI Integration
- Implement OpenAI integration
- Create AI chat interface
- Set up prompt management

### 10.4 Phase 4: Testing and Refinement
- Implement comprehensive testing
- Refine UI/UX
- Optimize performance

## 11. File Structure
```
team_tasks_streamlit/
├── app.py                      # Main Streamlit application
├── requirements.txt            # Python dependencies
├── README.md                   # Project documentation
├── .env.example                # Example environment variables
├── .gitignore                  # Git ignore file
├── documentation/              # Documentation files
│   ├── customer_requirements.md
│   ├── PRD.md
│   ├── EDD.md
│   ├── deployment_guide.md
│   └── user_guide.md
├── src/                        # Source code
│   ├── auth/                   # Authentication module
│   │   ├── __init__.py
│   │   ├── google_auth.py      # Google OAuth implementation
│   │   └── session.py          # Session management
│   ├── database/               # Database module
│   │   ├── __init__.py
│   │   ├── firestore.py        # Firestore integration
│   │   └── models.py           # Data models
│   ├── tasks/                  # Task management module
│   │   ├── __init__.py
│   │   ├── task_service.py     # Task business logic
│   │   └── task_repository.py  # Task data access
│   ├── ai/                     # AI integration module
│   │   ├── __init__.py
│   │   ├── llm_service.py   # OpenAI integration
│   │   └── prompt_repository.py # Prompt management
│   └── ui/                     # UI components
│       ├── __init__.py
│       ├── navigation.py       # Navigation components
│       ├── task_list.py        # Task list components
│       ├── task_form.py        # Task form components
│       └── ai_chat.py          # AI chat components
└── tests/                      # Test files
    ├── __init__.py
    ├── test_auth.py
    ├── test_tasks.py
    └── test_ai.py
```

## 12. Dependencies
- streamlit
- firebase-admin
- google-auth
- google-auth-oauthlib
- python-jwt
- langchain
- openai
- python-dotenv
- pytest (for testing)

## 13. Appendices

### 13.1 Firestore Security Rules
```
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    match /tasks/{taskId} {
      allow read, update, delete: if request.auth != null && resource.data.userId == request.auth.uid;
      allow create: if request.auth != null && request.resource.data.userId == request.auth.uid;
    }
    match /AI_chats/{chatId} {
      allow read, write: if request.auth != null && resource.data.user_id == request.auth.uid;
    }
    match /AI_prompts/{promptId} {
      allow read: if request.auth != null;
      allow write: if false;  // Admin-only via backend
    }
  }
}
```

### 13.2 Environment Variables
```
# Firebase
FIREBASE_PROJECT_ID=your-project-id
FIREBASE_CLIENT_EMAIL=your-client-email
FIREBASE_PRIVATE_KEY=your-private-key

# OpenAI
OPENAI_API_KEY=your-openai-api-key

# Google OAuth
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret
```

### 13.3 Repo Contribution Guidelines
- Follow AGENTS.md for contribution rules
