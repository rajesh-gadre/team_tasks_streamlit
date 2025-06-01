# Deployment Guide
# User Task Management System with Soft-Delete

## 1. Prerequisites

Before deploying the User Task Management System, ensure you have the following:

- Python 3.8 or higher installed
- pip package manager
- A Firebase project with Firestore database
- Google OAuth credentials
- OpenAI API key

## 2. Environment Setup

### 2.1 Clone the Repository

```bash
git clone <repository-url>
cd team_tasks_streamlit
```

### 2.2 Create a Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows
venv\Scripts\activate
# On macOS/Linux
source venv/bin/activate
```

### 2.3 Install Dependencies

```bash
pip install -r requirements.txt
```

## 3. Firebase Setup

### 3.1 Create a Firebase Project

1. Go to the [Firebase Console](https://console.firebase.google.com/)
2. Click "Add project" and follow the setup wizard
3. Enable Firestore database in your project

### 3.2 Set Up Service Account

1. In the Firebase Console, go to Project Settings > Service Accounts
2. Click "Generate new private key"
3. Save the JSON file securely

### 3.3 Configure Firestore Security Rules

Add the following security rules to your Firestore database:

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

## 4. Google OAuth Setup

### 4.1 Create OAuth Credentials

1. Go to the [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Navigate to APIs & Services > Credentials
4. Click "Create Credentials" > "OAuth client ID"
5. Set up the OAuth consent screen
6. Create a Web application OAuth client ID
7. Add authorized redirect URIs:
   - For local development: `http://localhost:8501/callback`
   - For production: `https://your-domain.com/callback`
8. Save the client ID and client secret

## 5. Environment Variables

Create a `.env` file in the root directory with the following variables:

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

# JWT
JWT_SECRET_KEY=your-jwt-secret-key

# Logging
LOG_LEVEL=INFO  # DEBUG, INFO, WARNING, ERROR, CRITICAL
```

## 6. Initialize Firestore Collections

### 6.1 Create AI_prompts Collection

Create a document in the `AI_prompts` collection with the following fields:
- `prompt_name`: "AI_Tasks"
- `text`: Your system prompt for the AI assistant
- `status`: "active"

You can use the Firebase Console or the following Python script:

```python
import firebase_admin
from firebase_admin import credentials, firestore
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Firebase
cred = credentials.Certificate({
    "type": "service_account",
    "project_id": os.environ.get("FIREBASE_PROJECT_ID"),
    "private_key": os.environ.get("FIREBASE_PRIVATE_KEY").replace("\\n", "\n"),
    "client_email": os.environ.get("FIREBASE_CLIENT_EMAIL")
})
firebase_admin.initialize_app(cred)
db = firestore.client()

# Create AI_prompts document
db.collection("AI_prompts").add({
    "prompt_name": "AI_Tasks",
    "text": "You are an AI assistant for a task management system. You can help users manage their tasks, provide suggestions, and answer questions about task management best practices.",
    "status": "active"
})

print("AI_prompts collection initialized successfully.")
```

## 7. Local Deployment

### 7.1 Run the Application

```bash
streamlit run app.py
```

The application will be available at `http://localhost:8501`.

## 8. Production Deployment

### 8.1 Streamlit Cloud

1. Push your code to a GitHub repository
2. Go to [Streamlit Cloud](https://streamlit.io/cloud)
3. Connect your GitHub repository
4. Configure the deployment:
   - Main file path: `app.py`
   - Add all environment variables from your `.env` file
5. Deploy the application

### 8.2 Heroku

1. Create a `Procfile` in the root directory:
   ```
   web: streamlit run app.py
   ```
2. Create a `runtime.txt` file:
   ```
   python-3.9.7
   ```
3. Deploy to Heroku:
   ```bash
   heroku create your-app-name
   heroku config:set FIREBASE_PROJECT_ID=your-project-id
   heroku config:set FIREBASE_CLIENT_EMAIL=your-client-email
   heroku config:set FIREBASE_PRIVATE_KEY=your-private-key
   heroku config:set OPENAI_API_KEY=your-openai-api-key
   heroku config:set GOOGLE_CLIENT_ID=your-google-client-id
   heroku config:set GOOGLE_CLIENT_SECRET=your-google-client-secret
   heroku config:set JWT_SECRET_KEY=your-jwt-secret-key
   heroku config:set LOG_LEVEL=INFO
   git push heroku main
   ```

### 8.3 Docker

1. Create a `Dockerfile` in the root directory:
   ```dockerfile
   FROM python:3.9-slim
   
   WORKDIR /app
   
   COPY requirements.txt .
   RUN pip install -r requirements.txt
   
   COPY . .
   
   EXPOSE 8501
   
   CMD ["streamlit", "run", "app.py"]
   ```
2. Build and run the Docker container:
   ```bash
   docker build -t task-management-system .
   docker run -p 8501:8501 --env-file .env task-management-system
   ```

## 9. Troubleshooting

### 9.1 Common Issues

#### Firebase Connection Issues
- Verify that your Firebase credentials are correct
- Check that your project ID matches the one in your Firebase console
- Ensure the private key is properly formatted (replace `\\n` with `\n`)

#### Google OAuth Issues
- Verify that your redirect URIs are correctly configured
- Check that your client ID and client secret are correct
- Ensure the OAuth consent screen is properly configured

#### OpenAI API Issues
- Verify that your API key is correct
- Check that you have sufficient credits in your OpenAI account

### 9.2 Logging

Adjust the `LOG_LEVEL` environment variable to get more detailed logs:
- `DEBUG`: Most verbose, includes all debug information
- `INFO`: General information about application flow
- `WARNING`: Only warnings and errors
- `ERROR`: Only errors
- `CRITICAL`: Only critical errors

## 10. Maintenance

### 10.1 Updating Dependencies

Periodically update dependencies to ensure security and performance:

```bash
pip install -U -r requirements.txt
```

### 10.2 Monitoring

Monitor your application using:
- Streamlit Cloud dashboard
- Firebase Console for database usage
- OpenAI dashboard for API usage

### 10.3 Backups

Regularly back up your Firestore data using Firebase's export functionality.
