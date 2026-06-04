from pathlib import Path

from app.ingestion_service import ingestion_service
from app.schemas import IngestionRecord


def test_json_ingestion_summary():
    summary = ingestion_service.process_json_records(
        [
            IngestionRecord(
                sku="FOODS_9_001",
                store_id="CA_1",
                category="FOODS",
                date="2026-06-03",
                current_stock=15,
                price=4.2,
                snap_day=1,
                event_day=0,
                sales=12,
            )
        ]
    )
    assert summary["rows_valid"] == 1
    assert summary["status"] in {"success", "partial_success"}
