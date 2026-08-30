"""
Thin wrapper around kafka-python so the rest of the app can call
`producer.publish(topic, payload)` without caring whether a real broker is
reachable. In dev/demo mode (no KAFKA_BOOTSTRAP_SERVERS set) it just logs.
"""
from __future__ import annotations

import json
import logging
from typing import Any, Optional

from app.core.config import get_settings

logger = logging.getLogger("kafka_producer")


class CdrStreamProducer:
    def __init__(self) -> None:
        self._settings = get_settings()
        self._producer: Optional[Any] = None
        if self._settings.KAFKA_BOOTSTRAP_SERVERS:
            try:
                from kafka import KafkaProducer  # imported lazily — optional dep

                self._producer = KafkaProducer(
                    bootstrap_servers=self._settings.KAFKA_BOOTSTRAP_SERVERS.split(","),
                    value_serializer=lambda v: json.dumps(v).encode("utf-8"),
                )
                logger.info("Connected to Kafka at %s", self._settings.KAFKA_BOOTSTRAP_SERVERS)
            except Exception as exc:  # noqa: BLE001 — degrade gracefully in dev
                logger.warning("Kafka unavailable (%s); falling back to log-only mode", exc)
                self._producer = None

    def publish(self, payload: dict, topic: Optional[str] = None) -> None:
        topic = topic or self._settings.KAFKA_RAW_CRIMES_TOPIC
        if self._producer is not None:
            self._producer.send(topic, payload)
            self._producer.flush()
        else:
            logger.info("[kafka:%s] %s", topic, json.dumps(payload)[:500])


cdr_producer = CdrStreamProducer()
