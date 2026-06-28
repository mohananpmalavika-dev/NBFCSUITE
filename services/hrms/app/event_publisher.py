from typing import Dict, Any
import logging

logger = logging.getLogger("hrms.event_publisher")


class EventPublisher:
    """Simple pluggable event publisher interface.

    Implementations can push to Kafka, RabbitMQ, Redis Streams, or HTTP webhooks.
    For now this module logs events; swap with a real publisher in production.
    """

    def publish(self, topic: str, event: Dict[str, Any]) -> None:
        raise NotImplementedError()


class LoggingEventPublisher(EventPublisher):
    def publish(self, topic: str, event: Dict[str, Any]) -> None:
        logger.info("Publish event %s: %s", topic, event)


class RabbitMQEventPublisher(EventPublisher):
    def __init__(self, url: str, exchange: str = 'hrms.events'):
        try:
            import pika
        except Exception as e:
            raise RuntimeError("pika library is required for RabbitMQ publisher") from e
        params = pika.URLParameters(url)
        self._connection = pika.BlockingConnection(params)
        self._channel = self._connection.channel()
        self._exchange = exchange
        self._channel.exchange_declare(exchange=self._exchange, exchange_type='topic', durable=True)

    def publish(self, topic: str, event: Dict[str, Any]) -> None:
        import json

        body = json.dumps(event, default=str)
        self._channel.basic_publish(exchange=self._exchange, routing_key=topic, body=body)

    def close(self) -> None:
        try:
            self._connection.close()
        except Exception:
            pass


# module-level default publisher, can be replaced by app startup wiring
_default_publisher: EventPublisher = LoggingEventPublisher()


def get_publisher() -> EventPublisher:
    return _default_publisher


def set_publisher(publisher: EventPublisher) -> None:
    global _default_publisher
    _default_publisher = publisher
