"""Chain of Custody management for digital forensic evidence."""
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from forensics.hasher import forensic_hasher
import uuid
import json


class ChainOfCustodyManager:
    """Manages immutable chain of custody records for collected evidence.

    Every piece of collected data gets:
    - Unique evidence ID
    - SHA-256 integrity hash
    - Timestamped custody transfers
    - Append-only audit trail
    """

    def __init__(self):
        self.evidence_records: Dict[str, Dict[str, Any]] = {}
        self.custody_log: List[Dict[str, Any]] = []

    def collect_evidence(
        self, data: Any, source_platform: str = "unknown",
        collector_id: str = "system", evidence_type: str = "social_post",
        notes: str = ""
    ) -> Dict[str, Any]:
        """Collect and register new evidence with chain of custody."""
        evidence_id = f"EVD-{uuid.uuid4().hex[:12].upper()}"
        hash_result = forensic_hasher.hash_with_metadata(data, source_platform)
        timestamp = datetime.now(timezone.utc).isoformat()

        record = {
            "evidence_id": evidence_id,
            "evidence_type": evidence_type,
            "source_platform": source_platform,
            "collected_at": timestamp,
            "collector_id": collector_id,
            "integrity_hash": hash_result["hash"],
            "hash_algorithm": "SHA-256",
            "data_size_bytes": hash_result["data_size_bytes"],
            "data_snapshot": data if isinstance(data, dict) else {"raw": str(data)},
            "chain_of_custody": [
                {
                    "action": "COLLECTED",
                    "actor": collector_id,
                    "timestamp": timestamp,
                    "notes": notes or f"Evidence collected from {source_platform}",
                    "integrity_hash": hash_result["hash"],
                }
            ],
            "status": "active",
            "is_deleted": False,
            "is_edited": False,
            "edit_history": [],
            "tags": [],
        }

        self.evidence_records[evidence_id] = record
        self._log_custody_event(evidence_id, "COLLECTED", collector_id, notes)

        return record

    def transfer_custody(
        self, evidence_id: str, from_actor: str, to_actor: str,
        reason: str = ""
    ) -> Dict[str, Any]:
        """Transfer custody of evidence to another actor."""
        record = self.evidence_records.get(evidence_id)
        if not record:
            return {"error": f"Evidence {evidence_id} not found"}

        timestamp = datetime.now(timezone.utc).isoformat()
        transfer = {
            "action": "TRANSFERRED",
            "from_actor": from_actor,
            "to_actor": to_actor,
            "timestamp": timestamp,
            "reason": reason,
            "integrity_hash": record["integrity_hash"],
        }
        record["chain_of_custody"].append(transfer)
        self._log_custody_event(evidence_id, "TRANSFERRED", to_actor, reason)

        return {"evidence_id": evidence_id, "transfer": transfer}

    def verify_evidence(self, evidence_id: str) -> Dict[str, Any]:
        """Verify integrity of collected evidence."""
        record = self.evidence_records.get(evidence_id)
        if not record:
            return {"error": f"Evidence {evidence_id} not found"}

        verification = forensic_hasher.verify_integrity(
            record["data_snapshot"], record["integrity_hash"]
        )

        timestamp = datetime.now(timezone.utc).isoformat()
        record["chain_of_custody"].append({
            "action": "VERIFIED",
            "actor": "system",
            "timestamp": timestamp,
            "result": verification["integrity_status"],
            "integrity_hash": verification["actual_hash"],
        })

        return {
            "evidence_id": evidence_id,
            "integrity_status": verification["integrity_status"],
            "verification": verification,
            "chain_length": len(record["chain_of_custody"]),
        }

    def mark_deleted(self, evidence_id: str, detected_by: str = "system") -> Dict[str, Any]:
        """Mark evidence as having been deleted from source."""
        record = self.evidence_records.get(evidence_id)
        if not record:
            return {"error": f"Evidence {evidence_id} not found"}

        record["is_deleted"] = True
        timestamp = datetime.now(timezone.utc).isoformat()
        record["chain_of_custody"].append({
            "action": "SOURCE_DELETED",
            "actor": detected_by,
            "timestamp": timestamp,
            "notes": "Original content no longer available at source",
        })
        return {"evidence_id": evidence_id, "status": "marked_deleted"}

    def mark_edited(
        self, evidence_id: str, new_data: Any, detected_by: str = "system"
    ) -> Dict[str, Any]:
        """Record that source content was edited."""
        record = self.evidence_records.get(evidence_id)
        if not record:
            return {"error": f"Evidence {evidence_id} not found"}

        new_hash = forensic_hasher.hash_data(new_data)
        timestamp = datetime.now(timezone.utc).isoformat()

        record["is_edited"] = True
        record["edit_history"].append({
            "timestamp": timestamp,
            "previous_hash": record["integrity_hash"],
            "new_hash": new_hash,
            "detected_by": detected_by,
            "new_snapshot": new_data if isinstance(new_data, dict) else {"raw": str(new_data)},
        })
        record["chain_of_custody"].append({
            "action": "EDIT_DETECTED",
            "actor": detected_by,
            "timestamp": timestamp,
            "notes": f"Content modified. Previous hash: {record['integrity_hash'][:16]}...",
        })

        return {"evidence_id": evidence_id, "status": "edit_recorded", "edit_count": len(record["edit_history"])}

    def get_evidence(self, evidence_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve evidence record."""
        return self.evidence_records.get(evidence_id)

    def get_all_evidence(self) -> List[Dict[str, Any]]:
        """Get all evidence records."""
        return list(self.evidence_records.values())

    def search_evidence(self, platform: str = None, evidence_type: str = None) -> List[Dict[str, Any]]:
        """Search evidence by criteria."""
        results = list(self.evidence_records.values())
        if platform:
            results = [r for r in results if r["source_platform"] == platform]
        if evidence_type:
            results = [r for r in results if r["evidence_type"] == evidence_type]
        return results

    def _log_custody_event(self, evidence_id: str, action: str, actor: str, notes: str = ""):
        """Internal custody event logging."""
        self.custody_log.append({
            "evidence_id": evidence_id,
            "action": action,
            "actor": actor,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "notes": notes,
        })

    def get_custody_log(self) -> List[Dict[str, Any]]:
        """Get the full custody audit log."""
        return self.custody_log.copy()

    def get_statistics(self) -> Dict[str, Any]:
        """Get forensics statistics."""
        records = list(self.evidence_records.values())
        return {
            "total_evidence": len(records),
            "active": sum(1 for r in records if r["status"] == "active"),
            "deleted_detected": sum(1 for r in records if r["is_deleted"]),
            "edited_detected": sum(1 for r in records if r["is_edited"]),
            "platforms": list(set(r["source_platform"] for r in records)),
            "total_custody_events": len(self.custody_log),
        }


# Singleton
custody_manager = ChainOfCustodyManager()
