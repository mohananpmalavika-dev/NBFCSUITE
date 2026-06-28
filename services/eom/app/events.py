import json
import os
from datetime import datetime, timezone
from urllib import request, error

# Placeholder event publisher. In production this should push to Kafka/Rabbit/HTTP bus.
EVENT_LOG = os.path.join(os.path.dirname(__file__), '..', '..', 'var', 'events.log')


def _ensure_dir():
    d = os.path.dirname(EVENT_LOG)
    os.makedirs(d, exist_ok=True)


def _http_post(url: str, payload: dict):
    data = json.dumps(payload).encode('utf-8')
    req = request.Request(url, data=data, headers={'Content-Type': 'application/json'})
    try:
        with request.urlopen(req, timeout=5) as resp:
            return resp.status, resp.read()
    except error.HTTPError as e:
        return e.code, None
    except Exception:
        return None, None


def publish_event(event_type: str, payload: dict):
    _ensure_dir()
    record = {
        'ts': datetime.now(timezone.utc).isoformat(),
        'type': event_type,
        'payload': payload,
    }
    # append JSON line to log as a simple durable sink
    with open(EVENT_LOG, 'a', encoding='utf-8') as f:
        f.write(json.dumps(record) + '\n')

    # Try HTTP delivery if EVENT_BUS_URL is configured
    bus = os.getenv('EVENT_BUS_URL')
    if bus:
        try:
            status, _ = _http_post(bus, record)
            print('EVENT HTTP POST', status)
        except Exception:
            pass

    # For local dev it's useful to also print
    print('EVENT:', record)
    return True
