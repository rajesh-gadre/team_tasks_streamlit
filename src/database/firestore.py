"""
Firestore integration module for the Task Management System.
Handles connection and CRUD operations with Firebase Firestore.
"""
import os
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any, Union

import firebase_admin
from firebase_admin import credentials, firestore
from firebase_admin.firestore import SERVER_TIMESTAMP

# Configure logging
logger = logging.getLogger(__name__)

class FirestoreClient:
    """Firestore client for database operations."""
    
    _instance = None
    
    def __new__(cls):
        """Singleton pattern to ensure only one Firestore client instance."""
        if cls._instance is None:
            cls._instance = super(FirestoreClient, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        """Initialize Firestore client with credentials from environment variables."""
        if self._initialized:
            return
            
        try:
            # Get Firebase credentials from environment variables
            project_id = os.environ.get('FIREBASE_PROJECT_ID')
            client_email = os.environ.get('FIREBASE_CLIENT_EMAIL')
            private_key = os.environ.get('FIREBASE_PRIVATE_KEY', '').replace('\\n', '\n')
            token_uri = os.environ.get('FIREBASE_TOKEN_URI')
            auth_uri = os.environ.get('FIREBASE_AUTH_URI')
            auth_provider_x509_cert_url = os.environ.get('FIREBASE_AUTH_PROVIDER_X509_CERT_URL')
            client_x509_cert_url = os.environ.get('FIREBASE_CLIENT_X509_CERT_URL')
            
            if not all([project_id, client_email, private_key, token_uri]):
                raise ValueError("Missing required Firebase credentials in environment variables")
            
            # Initialize Firebase app with credentials
            cred = credentials.Certificate({
                'type': 'service_account',
                'project_id': project_id,
                'private_key': private_key,
                'client_email': client_email,
                'token_uri': token_uri,
                'auth_uri': auth_uri,
                'auth_provider_x509_cert_url': auth_provider_x509_cert_url,
                'client_x509_cert_url': client_x509_cert_url
            })
            
            # Check if Firebase app is already initialized
            if not firebase_admin._apps:
                firebase_admin.initialize_app(cred)
            
            # Initialize Firestore client
            self.db = firestore.client()
            self._initialized = True
            logger.info("Firestore client initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Firestore client: {str(e)}")
            raise
    
    def create(self, collection: str, data: Dict[str, Any]) -> str:
        """
        Create a new document in the specified collection.
        
        Args:
            collection: Collection name
            data: Document data
            
        Returns:
            Document ID of the created document
        """
        try:
            # Add server timestamp for createdAt and updatedAt if not provided
            if 'createdAt' not in data:
                data['createdAt'] = SERVER_TIMESTAMP
            if 'updatedAt' not in data:
                data['updatedAt'] = SERVER_TIMESTAMP
                
            # Add document to collection
            doc_ref = self.db.collection(collection).document()
            doc_ref.set(data)
            logger.info(f"Document created in {collection} with ID: {doc_ref.id}")
            return doc_ref.id
        except Exception as e:
            logger.error(f"Error creating document in {collection}: {str(e)}")
            raise
    
    def read(self, collection: str, doc_id: str) -> Optional[Dict[str, Any]]:
        """
        Read a document from the specified collection.
        
        Args:
            collection: Collection name
            doc_id: Document ID
            
        Returns:
            Document data or None if not found
        """
        try:
            doc_ref = self.db.collection(collection).document(doc_id)
            doc = doc_ref.get()
            
            if doc.exists:
                data = doc.to_dict()
                data['id'] = doc.id
                return data
            else:
                logger.warning(f"Document {doc_id} not found in {collection}")
                return None
        except Exception as e:
            logger.error(f"Error reading document {doc_id} from {collection}: {str(e)}")
            raise
    
    def update(self, collection: str, doc_id: str, data: Dict[str, Any]) -> bool:
        """
        Update a document in the specified collection.
        
        Args:
            collection: Collection name
            doc_id: Document ID
            data: Updated document data
            
        Returns:
            True if update was successful, False otherwise
        """
        try:
            # Add server timestamp for updatedAt
            data['updatedAt'] = SERVER_TIMESTAMP
            
            doc_ref = self.db.collection(collection).document(doc_id)
            doc_ref.update(data)
            logger.info(f"Document {doc_id} updated in {collection}")
            return True
        except Exception as e:
            logger.error(f"Error updating document {doc_id} in {collection}: {str(e)}")
            raise
    
    def delete(self, collection: str, doc_id: str) -> bool:
        """
        Delete a document from the specified collection.
        
        Args:
            collection: Collection name
            doc_id: Document ID
            
        Returns:
            True if deletion was successful, False otherwise
        """
        try:
            doc_ref = self.db.collection(collection).document(doc_id)
            doc_ref.delete()
            logger.info(f"Document {doc_id} deleted from {collection}")
            return True
        except Exception as e:
            logger.error(f"Error deleting document {doc_id} from {collection}: {str(e)}")
            raise
    
    def query(self, collection: str, filters: List[tuple] = None, order_by: str = None, 
              direction: str = 'ASCENDING', limit: int = None) -> List[Dict[str, Any]]:
        """
        Query documents from the specified collection with filters.
        
        Args:
            collection: Collection name
            filters: List of filter tuples (field, operator, value)
            order_by: Field to order by
            direction: Direction to order by ('ASCENDING' or 'DESCENDING')
            limit: Maximum number of documents to return
            
        Returns:
            List of document data
        """
        try:
            # Start with collection reference
            query_ref = self.db.collection(collection)
            
            # Apply filters if provided
            if filters:
                for field, op, value in filters:
                    query_ref = query_ref.where(field, op, value)
            
            # Apply ordering if provided
            if order_by:
                direction_obj = firestore.Query.ASCENDING if direction == 'ASCENDING' else firestore.Query.DESCENDING
                query_ref = query_ref.order_by(order_by, direction=direction_obj)
            
            # Apply limit if provided
            if limit:
                query_ref = query_ref.limit(limit)
            
            # Execute query
            docs = query_ref.stream()
            
            # Process results
            results = []
            for doc in docs:
                data = doc.to_dict()
                data['id'] = doc.id
                results.append(data)
            
            logger.info(f"Query executed on {collection}, returned {len(results)} documents")
            return results
        except Exception as e:
            logger.error(f"Error querying documents from {collection}: {str(e)}")
            raise

# Create a singleton instance
firestore_client = FirestoreClient()
