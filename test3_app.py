import os
from src.database.firestore import FirestoreClient
import streamlit as st

import os
from src.database.firestore import FirestoreClient
import streamlit as st

firestore_client = FirestoreClient()

# Print some sample documents (just 10)
print("📄 Previewing all tasks (limit 20)...")
sample_docs = firestore_client.db.collection("tasks").limit(20).stream()
for doc in sample_docs:
    data = doc.to_dict()
    print(f" - {doc.id}: userId={data.get('userId')} | status={data.get('status')}")

# Check user-specific query
print("\n🔍 Now filtering by userid and status...")
query = (
    firestore_client.db.collection("tasks")
    .where("userId", "==", "amitamit@gmail.com")
    .where("status", "==", "completed")
)

results = [doc.to_dict() for doc in query.stream()]
print(f"✅ Found {len(results)} completed tasks for user.")
for r in results:
    print(f"  - Task: {r.get('title', '(no title)')} | Status: {r.get('status')}")