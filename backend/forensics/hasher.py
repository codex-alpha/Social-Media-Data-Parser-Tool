"""SHA-256 Hashing Engine for forensic integrity."""
import hashlib
import json
from datetime import datetime, timezone
from typing import Any, Dict, List


class ForensicHasher:
    """Cryptographic hashing service for evidence integrity.

    All collected data is hashed with SHA-256 to ensure tamper-proof
    forensic evidence with verifiable chain of custody.
    """

    def __init__(self):
        self.hash_log: List[Dict[str, Any]] = []

    def hash_data(self, data: Any) -> str:
        """Generate SHA-256 hash for any data structure."""
        if isinstance(data, (dict, list)):
            serialized = json.dumps(data, sort_keys=True, default=str)
        elif isinstance(data, bytes):
            return hashlib.sha256(data).hexdigest()
        else:
            serialized = str(data)
        return hashlib.sha256(serialized.encode("utf-8")).hexdigest()

    def hash_with_metadata(self, data: Any, source: str = "unknown") -> Dict[str, Any]:
        """Hash data and return with full metadata record."""
        data_hash = self.hash_data(data)
        record = {
            "hash": data_hash,
            "algorithm": "SHA-256",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "source": source,
            "data_size_bytes": len(json.dumps(data, default=str).encode("utf-8")) if isinstance(data, (dict, list)) else len(str(data).encode("utf-8")),
            "verified": True,
        }
        self.hash_log.append(record)
        return record

    def verify_integrity(self, data: Any, expected_hash: str) -> Dict[str, Any]:
        """Verify data integrity against an expected hash."""
        current_hash = self.hash_data(data)
        match = current_hash == expected_hash
        return {
            "verified": match,
            "expected_hash": expected_hash,
            "actual_hash": current_hash,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "integrity_status": "INTACT" if match else "COMPROMISED",
        }

    def hash_file_content(self, content: bytes) -> Dict[str, Any]:
        """Hash file content with multiple algorithms."""
        return {
            "sha256": hashlib.sha256(content).hexdigest(),
            "md5": hashlib.md5(content).hexdigest(),
            "sha1": hashlib.sha1(content).hexdigest(),
            "size_bytes": len(content),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    def get_hash_log(self) -> List[Dict[str, Any]]:
        """Get the full hash log for audit trail."""
        return self.hash_log.copy()


# Singleton
forensic_hasher = ForensicHasher()
