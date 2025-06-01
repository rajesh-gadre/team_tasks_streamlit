# Product Requirements Document (PRD)
# User Task Management System with Soft-Delete

## 1. Introduction

### 1.1 Purpose
This document outlines the product requirements for a Streamlit-based User Task Management System with soft-delete functionality. The system will allow users to create, manage, and organize their tasks while providing the ability to recover accidentally deleted tasks.

### 1.2 Scope
The system will be a web application built using Streamlit and Firebase Firestore as the database. It will include task management features, authentication via Google OAuth, and an AI assistant for task-related queries.

### 1.3 Target Audience
- Individual users who need to manage personal tasks
- Team members who need to track their assigned tasks
- Anyone looking for a simple, intuitive task management solution

## 2. Product Overview

### 2.1 Product Description
A Streamlit-based task management application that allows users to:
- Create, view, edit, and delete tasks
- View completed and deleted tasks
- Restore deleted tasks
- Interact with an AI assistant for task-related help

### 2.2 Key Features
1. Task Management (Create, Read, Update, Delete)
2. Soft-delete functionality with task recovery
3. Task categorization (Active, Completed, Deleted)
4. Google OAuth Authentication
5. AI Assistant for task-related queries

## 3. User Stories

### 3.1 Authentication
- As a user, I want to log in using my Google account so that I can securely access my tasks.
- As a user, I want to remain logged in across sessions so that I don't have to authenticate each time.

### 3.2 Task Management
- As a user, I want to create new tasks with titles, descriptions, and due dates.
- As a user, I want to view all my active tasks in a list.
- As a user, I want to mark tasks as completed when I finish them.
- As a user, I want to edit task details if information changes.
- As a user, I want to add notes to my tasks for additional context.
- As a user, I want to view the history of updates made to a task.

### 3.3 Task Organization
- As a user, I want to view my completed tasks separately from active tasks.
- As a user, I want to view my deleted tasks in case I need to recover them.
- As a user, I want to permanently delete tasks I no longer need.

### 3.4 AI Assistant
- As a user, I want to ask questions about my tasks to an AI assistant.
- As a user, I want to get intelligent suggestions related to task management.

## 4. Functional Requirements

### 4.1 Authentication System
- Google OAuth integration
- JWT token management
- Session persistence

### 4.2 Task Management
- Task creation with required fields (title) and optional fields (description, due date)
- Task viewing with appropriate filters
- Task editing with update history
- Soft-delete functionality
- Task restoration capability

### 4.3 User Interface
- Navigation between different task views (Active, Completed, Deleted)
- Task creation and editing forms
- Task list displays with relevant information
- AI chat interface

### 4.4 AI Assistant
- Text input for user queries
- Integration with OpenAI via Langchain
- Contextual responses based on predefined prompts

## 5. Non-Functional Requirements

### 5.1 Performance
- Task operations should complete within 2 seconds
- Application should load within 3 seconds

### 5.2 Security
- All data access must be authenticated
- Users can only access their own tasks
- Secure handling of API keys and credentials

### 5.3 Usability
- Intuitive interface requiring minimal training
- Responsive design for various screen sizes
- Clear feedback for all user actions

### 5.4 Reliability
- Proper error handling for all operations
- Data consistency across all views
- Logging of all critical operations

## 6. Data Requirements

### 6.1 Task Data
- id: Unique identifier
- userId: Owner identifier
- title: Task title
- description: Task description (optional)
- dueDate: Task due date (optional)
- status: Task status (active, completed, deleted)
- createdAt, updatedAt: Timestamps
- completionDate: When task was completed
- deletionDate: When task was deleted
- notes: Additional user notes
- updates: History of changes

### 6.2 AI Chat Data
- user_id: User identifier
- inputText: User query
- createdAt, updated_at: Timestamps
- Response: AI-generated response

### 6.3 AI Prompts Data
- prompt_name: Identifier for the prompt
- text: Prompt content
- status: active or inactive

## 7. Constraints and Limitations

### 7.1 Technical Constraints
- Must use Streamlit for frontend
- Must use Firebase Firestore for database
- Must implement Google OAuth authentication
- Must use Langchain for OpenAI integration

### 7.2 Business Constraints
- MVP features must be implemented first
- System must be secure and protect user data
- System must be maintainable and extensible

## 8. Appendices

### 8.1 Glossary
- **Task**: A unit of work that a user wants to track
- **Soft-delete**: Marking a task as deleted without permanently removing it
- **JWT**: JSON Web Token, used for authentication
- **OAuth**: Open standard for access delegation

### 8.2 References
- Firebase Firestore documentation
- Streamlit documentation
- Google OAuth documentation
- Langchain documentation
