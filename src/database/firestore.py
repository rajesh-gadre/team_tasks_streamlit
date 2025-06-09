import os
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any, Union
try:
    from google.cloud.firestore_v1 import FieldFilter
except ModuleNotFoundError as e:
    raise ModuleNotFoundError('google-cloud-firestore is not installed') from e
import firebase_admin
from firebase_admin import credentials, firestore
from firebase_admin.firestore import SERVER_TIMESTAMP
import traceback
logger = logging.getLogger(__name__)

class FirestoreClient:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(FirestoreClient, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        try:
            project_id = os.environ.get('FIREBASE_PROJECT_ID')
            client_email = os.environ.get('FIREBASE_CLIENT_EMAIL')
            private_key = os.environ.get('FIREBASE_PRIVATE_KEY', '')
            if private_key:
                private_key = private_key.replace('\\n', '\n')
                if not private_key.startswith('-----BEGIN PRIVATE KEY-----'):
                    logger.warning("Private key doesn't have the expected format")
            token_uri = os.environ.get('FIREBASE_TOKEN_URI')
            auth_uri = os.environ.get('FIREBASE_AUTH_URI')
            auth_provider_x509_cert_url = os.environ.get('FIREBASE_AUTH_PROVIDER_X509_CERT_URL')
            client_x509_cert_url = os.environ.get('FIREBASE_CLIENT_X509_CERT_URL')
            if not all([project_id, client_email, private_key, token_uri]):
                raise ValueError('Missing required Firebase credentials in environment variables')
            cred = credentials.Certificate({'type': 'service_account', 'project_id': project_id, 'private_key': private_key, 'client_email': client_email, 'token_uri': token_uri, 'auth_uri': auth_uri, 'auth_provider_x509_cert_url': auth_provider_x509_cert_url, 'client_x509_cert_url': client_x509_cert_url})
            database_name = os.environ.get('FIREBASE_DATABASE_NAME')
            if not firebase_admin._apps:
                if database_name:
                    firebase_admin.initialize_app(cred, {'databaseURL': f'https://{project_id}.firebaseio.com', 'projectId': project_id, 'storageBucket': f'{project_id}.appspot.com'})
                else:
                    firebase_admin.initialize_app(cred)
            if database_name:
                self.db = firestore.client(database_id=database_name)
                logger.info(f'Firestore client initialized with database: {database_name}')
            else:
                self.db = firestore.client()
                logger.info('Firestore client initialized with default database')
            self._initialized = True
        except Exception as e:
            logger.error(f'Failed to initialize Firestore client: {str(e)}')
            raise

    def create(self, collection: str, data: Dict[str, Any]) -> str:
        try:
            logger.debug(f'DB REQUEST [CREATE] - Collection: {collection} - Data: {json.dumps(self._prepare_data_for_logging(data))}')
            if 'createdAt' not in data:
                data['createdAt'] = SERVER_TIMESTAMP
            if 'updatedAt' not in data:
                data['updatedAt'] = SERVER_TIMESTAMP
            doc_ref = self.db.collection(collection).document()
            doc_ref.set(data)
            logger.info(f'DB RESPONSE [CREATE] - Collection: {collection} - Document ID: {doc_ref.id}')
            return doc_ref.id
        except Exception as e:
            logger.error(f'DB ERROR [CREATE] - Collection: {collection} - Error: {str(e)}')
            raise

    def read(self, collection: str, doc_id: str) -> Optional[Dict[str, Any]]:
        try:
            logger.debug(f'DB REQUEST [READ] - Collection: {collection} - Document ID: {doc_id}')
            doc_ref = self.db.collection(collection).document(doc_id)
            doc = doc_ref.get()
            if doc.exists:
                data = doc.to_dict()
                data['id'] = doc.id
                logger.info(f'DB RESPONSE [READ] - Collection: {collection} - Document ID: {doc_id} - Found')
                logger.debug(f'DB RESPONSE DATA [READ] - {json.dumps(self._prepare_data_for_logging(data))}')
                return data
            else:
                logger.warning(f'DB RESPONSE [READ] - Collection: {collection} - Document ID: {doc_id} - Not Found')
                return None
        except Exception as e:
            logger.error(f'DB ERROR [READ] - Collection: {collection} - Document ID: {doc_id} - Error: {str(e)}')
            raise

    def get_all(self, collection: str):
        try:
            docs = self.db.collection(collection).stream()
            results = []
            for doc in docs:
                data = doc.to_dict()
                if data is not None:
                    data['id'] = doc.id
                    results.append(data)
            return results
        except Exception as e:
            logger.error(f'DB ERROR [GET ALL] - Collection: {collection} - Error: {str(e)}')
            raise

    def update(self, collection: str, doc_id: str, data: Dict[str, Any]) -> bool:
        try:
            logger.debug(f'DB REQUEST [UPDATE] - Collection: {collection} - Document ID: {doc_id} - Data: {json.dumps(self._prepare_data_for_logging(data))}')
            data['updatedAt'] = SERVER_TIMESTAMP
            doc_ref = self.db.collection(collection).document(doc_id)
            doc_ref.update(data)
            logger.info(f'DB RESPONSE [UPDATE] - Collection: {collection} - Document ID: {doc_id} - Success')
            return True
        except Exception as e:
            logger.error(f'DB ERROR [UPDATE] - Collection: {collection} - Document ID: {doc_id} - Error: {str(e)}')
            raise

    def delete(self, collection: str, doc_id: str) -> bool:
        try:
            logger.debug(f'DB REQUEST [DELETE] - Collection: {collection} - Document ID: {doc_id}')
            doc_ref = self.db.collection(collection).document(doc_id)
            doc_ref.delete()
            logger.info(f'DB RESPONSE [DELETE] - Collection: {collection} - Document ID: {doc_id} - Success')
            return True
        except Exception as e:
            logger.error(f'DB ERROR [DELETE] - Collection: {collection} - Document ID: {doc_id} - Error: {str(e)}')
            raise

    def delete_all(self, collection: str) -> bool:
        try:
            logger.debug(f'DB REQUEST [DELETE ALL] - Collection: {collection}')
            docs = self.db.collection(collection).stream()
            deleted_count = 0
            for doc in docs:
                doc.reference.delete()
                deleted_count += 1
            logger.info(f'DB RESPONSE [DELETE ALL] - Collection: {collection} - Success - Deleted {deleted_count} documents')
            return True
        except Exception as e:
            logger.error(f'DB ERROR [DELETE ALL] - Collection: {collection} - Error: {str(e)}')
            raise

    def query(self, collection: str, filters: List[tuple]=None, order_by: str=None, direction: str='ASCENDING', limit: int=None) -> List[Dict[str, Any]]:
        try:
            filter_str = ', '.join([f'{f[0]} {f[1]} {f[2]}' for f in filters]) if filters else 'None'
            limit_str = str(limit) if limit else 'None'
            logger.debug(f'DB REQUEST [QUERY] - Collection: {collection} - Filters: {filter_str} - OrderBy: {order_by} - Direction: {direction} - Limit: {limit_str}')
            query_ref = self.db.collection(collection)
            if filters:
                for field, op, value in filters:
                    query_ref = query_ref.where(filter=FieldFilter(field, op, value))
            if order_by:
                direction_obj = firestore.Query.ASCENDING if direction == 'ASCENDING' else firestore.Query.DESCENDING
                query_ref = query_ref.order_by(order_by, direction=direction_obj)
            if limit:
                query_ref = query_ref.limit(limit)
            logger.debug(f'DB REQUEST [QUERY] - Constructed query_ref: {{str(query_ref)}}')
            docs = query_ref.stream()
            results = []
            count = 0
            logger.debug(f"DB RESPONSE [QUERY] - Starting to stream documents from query for collection '{collection}' with filters: {filter_str}")
            for doc in docs:
                count += 1
                logger.debug(f'DB RESPONSE [QUERY] - Streamed doc ID: {doc.id}, Exists: {doc.exists}')
                try:
                    data = doc.to_dict()
                    if data is not None:
                        data['id'] = doc.id
                        results.append(data)
                    else:
                        logger.warning(f'DB RESPONSE [QUERY] - doc.to_dict() returned None for doc ID: {doc.id}. Skipping.')
                except Exception as e_to_dict:
                    logger.error(f'DB RESPONSE [QUERY] - Error calling to_dict() for doc ID: {doc.id}. Error: {str(e_to_dict)}. Traceback: {traceback.format_exc()}. Skipping.')
            logger.debug(f"DB RESPONSE [QUERY] - Finished streaming. Total docs processed from stream: {count}. Total valid results: {len(results)} for collection '{collection}'")
            if results and len(results) <= 10:
                logger.debug(f"DB RESPONSE DATA [QUERY] - First 10 valid result IDs: {[doc_data.get('id', 'unknown') for doc_data in results[:10]]}")
            return results
        except Exception as e:
            logger.error(f'DB ERROR [QUERY] - Collection: {collection} - Error: {str(e)}\nTraceback: {traceback.format_exc()}')
            raise

    def _prepare_data_for_logging(self, data: Dict[str, Any]) -> Dict[str, Any]:
        if not data:
            return {}
        log_data = {}
        for key, value in data.items():
            if value == SERVER_TIMESTAMP:
                log_data[key] = '<SERVER_TIMESTAMP>'
            elif isinstance(value, datetime):
                log_data[key] = value.isoformat()
            elif isinstance(value, dict):
                log_data[key] = self._prepare_data_for_logging(value)
            elif isinstance(value, list):
                if len(value) > 0 and isinstance(value[0], dict):
                    log_data[key] = [self._prepare_data_for_logging(item) if isinstance(item, dict) else item for item in value]
                else:
                    log_data[key] = value
            else:
                try:
                    json.dumps({key: value})
                    log_data[key] = value
                except (TypeError, OverflowError):
                    log_data[key] = f'<{type(value).__name__}>'
        return log_data
_firestore_client: Optional[FirestoreClient] = None

def get_client() -> FirestoreClient:
    global _firestore_client
    if _firestore_client is None:
        _firestore_client = FirestoreClient()
    return _firestore_client
