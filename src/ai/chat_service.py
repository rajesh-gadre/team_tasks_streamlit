import logging

from src.database.firestore import get_client

logger = logging.getLogger(__name__)


def delete_all_chats_one_by_one(n: int):
    try:
        client = get_client()
        source = 'AI_chats'
        archive = 'AI_chats_archive'
        docs = client.db.collection(source).stream()
        count = 0
        for doc in docs:
            data = doc.to_dict()
            client.db.collection(archive).document(doc.id).set(data)
            doc.reference.delete()
            count += 1
            if count >= n:
                break
        logger.info(f"Archived and deleted {count} documents from {source}")
    except Exception as e:
        logger.error(f"Error archiving and deleting AI chats: {str(e)}")
        raise


def get_all_chats():
    try:
        return get_client().get_all('AI_chats')
    except Exception as e:
        logger.error(f"Error getting all AI chats: {str(e)}")
        raise
