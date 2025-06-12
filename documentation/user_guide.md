# User Guide
# User Task Management System with Soft-Delete

## 1. Introduction

Welcome to the User Task Management System! This guide will help you navigate and use all the features of the application effectively.

## 2. Getting Started

### 2.1 Accessing the Application

Open your web browser and navigate to the application URL:
- Local development: `http://localhost:8501`
- Production: The URL provided by your administrator

### 2.2 Authentication

1. On the welcome page, click the login button
2. You will be redirected to either Google or Auth0 for authentication
3. Grant the necessary permissions
4. After successful authentication, you will be redirected back to the application

## 3. Navigation

The application has a sidebar with a navigation menu:

### 3.1 Sidebar

The sidebar displays:
- Your profile information (name and profile picture)
- A logout button

### 3.2 Navigation Sections

The navigation menu contains grouped sections:
- **🧑‍💼 User**: Active Tasks, Completed Tasks, Deleted Tasks, AI Assistant
- **🧭 Nav**: Settings
- **🛠️ Admin**: System Management, Evals, View Tables, Danger Zone

## 4. Managing Tasks

### 4.1 Viewing Tasks

Tasks are organized into three categories:
- **Active Tasks**: Tasks you're currently working on
- **Completed Tasks**: Tasks you've finished
- **Deleted Tasks**: Tasks you've removed (but can still restore)

Each task is displayed in an expandable container showing:
- Task title
- Detailed information when expanded (description, due date, notes)
- Task history showing all updates

### 4.2 Creating a New Task

1. Navigate to the "Add Task" tab
2. Fill in the task form:
   - **Title** (required): A short, descriptive name for your task
   - **Description** (optional): Detailed information about the task
   - **Due Date** (optional): When the task needs to be completed
   - **Notes** (optional): Any additional information or context
3. Click "Save Task" to create the task
4. Click "Cancel" to discard the new task

### 4.3 Editing a Task

1. Navigate to the "Active Tasks" tab
2. Find the task you want to edit
3. Click the "Edit" button for that task
4. Modify the task details in the form
5. Click "Save Task" to save your changes
6. Click "Cancel" to discard your changes

### 4.4 Completing a Task

1. Navigate to the "Active Tasks" tab
2. Find the task you want to mark as completed
3. Click the "Complete" button for that task
4. The task will move to the "Completed Tasks" tab

### 4.5 Deleting a Task

1. Navigate to either the "Active Tasks" or "Completed Tasks" tab
2. Find the task you want to delete
3. Click the "Delete" button for that task
4. The task will move to the "Deleted Tasks" tab

### 4.6 Restoring a Deleted Task

1. Navigate to the "Deleted Tasks" tab
2. Find the task you want to restore
3. Click the "Restore" button for that task
4. The task will move back to the "Active Tasks" tab

### 4.7 Task History

Each task maintains a history of all changes:
1. Expand a task by clicking on its title
2. Click on "Task History" to see all updates
3. Each entry shows the timestamp and the action performed

## 5. Using the AI Assistant

The AI Assistant can help you with task management advice and answer questions.

### 5.1 Asking Questions

1. Navigate to the "AI Assistant" tab
2. Type your question in the text area
3. Click the "Submit" button
4. Wait for the AI to process your question and provide a response

### 5.2 Example Questions

You can ask questions like:
- "How can I prioritize my tasks effectively?"
- "What are some productivity techniques for completing tasks?"
- "How can I manage my time better?"
- "What's the best way to organize my tasks?"
- "How can I avoid procrastination?"

### 5.3 Clearing Responses

After receiving a response:
1. Read the information provided
2. Click "Clear Response" to remove the current response and ask a new question

## 6. Account Management

### 6.1 Viewing Your Profile

Your profile information is displayed in the sidebar, including:
- Your name
- Your profile picture (if available)

### 6.2 Logging Out

To log out of the application:
1. Click the "Logout" button in the sidebar
2. You will be redirected to the login page

## 7. Privacy and Security

### 7.1 Data Privacy

- All your tasks are private and can only be accessed by you
- Authentication is handled securely through Google OAuth or Auth0
- Your data is stored in a secure Firestore database

### 7.2 AI Assistant Privacy

- Your conversations with the AI assistant are stored in the database
- These conversations are only accessible to you
- The AI uses OpenAI's services, which have their own privacy policies

## 8. Troubleshooting

### 8.1 Common Issues

#### Login Problems
- Ensure you're using a valid account for the configured provider
- Check your internet connection
- Clear your browser cookies and try again

#### Task Not Appearing
- Refresh the page
- Check that you're on the correct tab (Active/Completed/Deleted)
- Verify that you're logged in with the correct account

#### AI Assistant Not Responding
- Check your internet connection
- Verify that your question is not empty
- Try refreshing the page

### 8.2 Getting Help

If you encounter issues not covered in this guide, please contact your system administrator for assistance.

## 9. Tips and Best Practices

### 9.1 Task Management

- Keep task titles short and descriptive
- Use the description field for detailed information
- Set due dates for time-sensitive tasks
- Use notes to add context or references
- Regularly review and update your tasks

### 9.2 Using the AI Assistant

- Ask specific questions for more helpful responses
- Use the AI for productivity advice and task management strategies
- The AI can help with prioritization and organization techniques

## 10. Keyboard Shortcuts

For power users, the application supports several keyboard shortcuts:

- `Ctrl + Enter` (or `Cmd + Enter` on Mac): Submit forms
- `Esc`: Cancel current form
- `Tab`: Navigate between form fields
