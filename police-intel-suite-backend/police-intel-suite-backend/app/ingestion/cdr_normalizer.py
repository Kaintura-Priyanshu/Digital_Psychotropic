"""
Phase 1 CDR stream processor. Different telecom operators export call
detail records with different column names/orders/date formats — this
normalizes any of them into `CdrRecord` and streams each row onto the
`raw-crimes-stream` Kafka topic (or logs, in dev mode — see app.core.kafka).
"""
from __future__ import annotations

import csv
import io
import logging
from datetime import datetime
from typing import Iterator, List

from app.core.kafka import cdr_producer
from app.models.schemas import CdrRecord

logger = logging.getLogger("cdr_normalizer")

# Each carrier's raw column name -> our canonical field name.
_CARRIER_SCHEMAS = {
    "airtel": {
        "columns": {"A_PARTY": "caller", "B_PARTY": "callee", "CALL_DATE_TIME": "timestamp",
                    "DURATION": "duration_seconds", "CELL_ID": "tower_id"},
        "timestamp_format": "%d-%m-%Y %H:%M:%S",
    },
    "jio": {
        "columns": {"MSISDN": "caller", "OTHER_PARTY": "callee", "START_TIME": "timestamp",
                    "CALL_DURATION": "duration_seconds", "TOWER_ID": "tower_id"},
        "timestamp_format": "%Y-%m-%d %H:%M:%S",
    },
    "vi": {
        "columns": {"CALLING_NUM": "caller", "CALLED_NUM": "callee", "TIMESTAMP": "timestamp",
                    "DUR_SEC": "duration_seconds", "SITE_ID": "tower_id"},
        "timestamp_format": "%Y/%m/%d %H:%M",
    },
}


def detect_carrier(header: List[str]) -> str:
    header_set = set(h.strip().upper() for h in header)
    for carrier, schema in _CARRIER_SCHEMAS.items():
        if set(schema["columns"].keys()).issubset(header_set):
            return carrier
    raise ValueError(
        f"Unrecognized CDR header {header!r} — add a schema mapping in "
        "app.ingestion.cdr_normalizer._CARRIER_SCHEMAS"
    )


def normalize_csv(csv_bytes: bytes, carrier: str | None = None) -> Iterator[CdrRecord]:
    """Parses a raw carrier CSV export and yields unified CdrRecord rows."""
    text = csv_bytes.decode("utf-8-sig", errors="replace")
    reader = csv.DictReader(io.StringIO(text))
    if reader.fieldnames is None:
        return

    resolved_carrier = carrier or detect_carrier(reader.fieldnames)
    schema = _CARRIER_SCHEMAS[resolved_carrier]
    col_map = schema["columns"]
    ts_format = schema["timestamp_format"]

    for row in reader:
        try:
            raw_ts = row[_find_key(row, "timestamp", col_map)]
            parsed_ts = datetime.strptime(raw_ts.strip(), ts_format).isoformat()
            record = CdrRecord(
                caller=row[_find_key(row, "caller", col_map)].strip(),
                callee=row[_find_key(row, "callee", col_map)].strip(),
                timestamp=parsed_ts,
                duration_seconds=int(float(row[_find_key(row, "duration_seconds", col_map)] or 0)),
                tower_id=(row.get(_find_key(row, "tower_id", col_map)) or "").strip() or None,
                carrier=resolved_carrier,
            )
            yield record
        except (KeyError, ValueError) as exc:
            logger.warning("Skipping malformed CDR row %r (%s)", row, exc)
            continue


def _find_key(row: dict, canonical: str, col_map: dict) -> str:
    for raw_key, mapped in col_map.items():
        if mapped == canonical:
            return raw_key
    raise KeyError(canonical)


def normalize_and_stream(csv_bytes: bytes, carrier: str | None = None) -> int:
    """Normalizes a CSV upload and publishes each record to Kafka. Returns
    the count of records streamed."""
    count = 0
    for record in normalize_csv(csv_bytes, carrier=carrier):
        cdr_producer.publish(record.model_dump())
        count += 1
    return count
