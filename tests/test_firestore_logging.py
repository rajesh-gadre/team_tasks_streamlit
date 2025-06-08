import sys
from pathlib import Path
from datetime import datetime
sys.path.append(str(Path(__file__).resolve().parents[1] / 'src'))
from database.firestore import FirestoreClient
from firebase_admin.firestore import SERVER_TIMESTAMP

class CustomObject:
    pass

def test_prepare_data_for_logging():
    data = {'timestamp': datetime(2024, 1, 1, 12, 0, 0), 'server_ts': SERVER_TIMESTAMP, 'nested': {'inner': datetime(2023, 12, 31, 23, 59, 59)}, 'list': [{'dt': datetime(2022, 1, 1, 0, 0)}, 3], 'custom': CustomObject()}
    fc = FirestoreClient.__new__(FirestoreClient)
    result = fc._prepare_data_for_logging(data)
    assert result['timestamp'] == '2024-01-01T12:00:00'
    assert result['server_ts'] == '<SERVER_TIMESTAMP>'
    assert result['nested']['inner'] == '2023-12-31T23:59:59'
    assert result['list'][0]['dt'] == '2022-01-01T00:00:00'
    assert result['custom'] == '<CustomObject>'
