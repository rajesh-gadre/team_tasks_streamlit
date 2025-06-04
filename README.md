# User Task Management System

A Streamlit-based task management application with soft-delete functionality and AI assistance.

## Features

- Task management (create, read, update, delete)
- Soft-delete functionality with task recovery
- Task categorization (Active, Completed, Deleted)
- Google OAuth Authentication
- AI Assistant for task-related queries
- Firebase Firestore integration

## Project Structure

```
team_tasks_streamlit/
├── app.py                      # Main Streamlit application
├── requirements.txt            # Python dependencies
├── README.md                   # Project documentation
├── .env.example                # Example environment variables
├── documentation/              # Documentation files
│   ├── customer_requirements.md
│   ├── PRD.md
│   ├── EDD.md
│   ├── deployment_guide.md
│   └── user_guide.md
└── src/                        # Source code
    ├── auth/                   # Authentication module
    ├── database/               # Database module
    ├── tasks/                  # Task management module
    ├── ai/                     # AI integration module
    └── ui/                     # UI components
```

## Setup and Installation

1. Clone the repository
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Set up environment variables (see `.env.example`)
4. Run the application:
   ```
   streamlit run app.py
   ```

## Environment Variables

Create a `.env` file in the root directory with the following variables:

```
# Firebase
FIREBASE_PROJECT_ID=your-project-id
FIREBASE_CLIENT_EMAIL=your-client-email
FIREBASE_PRIVATE_KEY=your-private-key
FIREBASE_TOKEN_URI=your-token-uri
FIREBASE_AUTH_URI=your-auth-uri
FIREBASE_AUTH_PROVIDER_X509_CERT_URL=your-auth-provider-cert-url
FIREBASE_CLIENT_X509_CERT_URL=your-client-cert-url
FIREBASE_DATABASE_NAME=your-database-name

# OpenAI
OPENAI_API_KEY=your-openai-api-key
OPENAI_MODEL=your-openai-model

# Google OAuth
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret
GOOGLE_REDIRECT_URI=your-google-redirect-uri

# Logging
LOG_LEVEL=INFO  # DEBUG, INFO, WARNING, ERROR, CRITICAL
JWT_SECRET_KEY=your-jwt-secret-key
```

## Documentation

For detailed information, refer to the documentation folder:
- `customer_requirements.md`: Original requirements
- `PRD.md`: Product Requirements Document
- `EDD.md`: Engineering Design Document
- `deployment_guide.md`: Deployment instructions
- `user_guide.md`: User manual

## License

[MIT License](LICENSE)
