import json
import os
from datetime import datetime

# Placeholder event publisher. In production this should push to Kafka/Rabbit/HTTP bus.
EVENT_LOG = os.path.join(os.path.dirname(__file__), '..', '..', 'var', 'events.log')


def _ensure_dir():
    d = os.path.dirname(EVENT_LOG)
    os.makedirs(d, exist_ok=True)


def publish_event(event_type: str, payload: dict):
    _ensure_dir()
    record = {
        'ts': datetime.utcnow().isoformat() + 'Z',
        'type': event_type,
        'payload': payload,
    }
    # append JSON line to log as a simple durable sink
    with open(EVENT_LOG, 'a', encoding='utf-8') as f:
        f.write(json.dumps(record) + '\n')
    # For local dev it's useful to also print
    print('EVENT:', record)
    return True
