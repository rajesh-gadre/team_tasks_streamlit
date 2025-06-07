Agents should follow these guidelines when updating this repository:

**Frameworks and dependencies**
- Python 3.11
- Streamlit for the UI
- Firebase Firestore via firebase-admin
- OpenAI and Langchain for AI integration
- Pydantic models
- Google OAuth and Auth0 authentication

**Code style**
- Split large functions into smaller pieces
- No comments or docstrings in new code
- Keep imports grouped by standard library, third party, and local
- Provide tests with pytest for new functionality or bug fixes

**Testing**
- Install requirements with `pip install -r requirements.txt`
- Run tests using `pytest -v`

**Commit messages**
- Include the entire prompt that generated the code
