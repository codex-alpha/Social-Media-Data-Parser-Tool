"""Forensics API routes - Digital forensics endpoints."""
from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from datetime import datetime, timezone

from forensics.chain_of_custody import custody_manager
from forensics.hasher import forensic_hasher
from forensics.timeline import timeline_reconstructor
from forensics.account_correlation import account_correlator

router = APIRouter(prefix="/forensics", tags=["Digital Forensics"])


class EvidenceInput(BaseModel):
    data: Dict[str, Any]
    source_platform: str = "unknown"
    collector_id: str = "analyst"
    evidence_type: str = "social_post"
    notes: str = ""


class HashInput(BaseModel):
    data: Any


class VerifyInput(BaseModel):
    evidence_id: str


class TransferInput(BaseModel):
    evidence_id: str
    from_actor: str
    to_actor: str
    reason: str = ""


class TimelineEventInput(BaseModel):
    timestamp: str
    event_type: str
    platform: str
    actor: str
    action: str
    target: str = ""
    content_preview: str = ""
    severity: str = "none"


class CorrelationInput(BaseModel):
    profiles: List[Dict[str, Any]]


class ProfilePairInput(BaseModel):
    profile1_id: str
    profile2_id: str


# ---- Chain of Custody ----

@router.post("/evidence/collect")
async def collect_evidence(input: EvidenceInput):
    """Collect and register new forensic evidence."""
    result = custody_manager.collect_evidence(
        data=input.data,
        source_platform=input.source_platform,
        collector_id=input.collector_id,
        evidence_type=input.evidence_type,
        notes=input.notes,
    )
    return result


@router.get("/evidence")
async def list_evidence(platform: str = None, evidence_type: str = None):
    """List all collected evidence."""
    if platform or evidence_type:
        return custody_manager.search_evidence(platform, evidence_type)
    return custody_manager.get_all_evidence()


@router.get("/evidence/{evidence_id}")
async def get_evidence(evidence_id: str):
    """Get a specific evidence record."""
    record = custody_manager.get_evidence(evidence_id)
    if not record:
        raise HTTPException(status_code=404, detail=f"Evidence {evidence_id} not found")
    return record


@router.post("/evidence/verify")
async def verify_evidence(input: VerifyInput):
    """Verify evidence integrity."""
    result = custody_manager.verify_evidence(input.evidence_id)
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])
    return result


@router.post("/evidence/transfer")
async def transfer_evidence(input: TransferInput):
    """Transfer custody of evidence."""
    result = custody_manager.transfer_custody(
        input.evidence_id, input.from_actor, input.to_actor, input.reason
    )
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])
    return result


@router.get("/custody-log")
async def get_custody_log():
    """Get the full custody audit log."""
    return custody_manager.get_custody_log()


@router.get("/statistics")
async def get_forensic_stats():
    """Get forensic module statistics."""
    return custody_manager.get_statistics()


# ---- Hashing ----

@router.post("/hash")
async def hash_data(input: HashInput):
    """Generate SHA-256 hash for data."""
    result = forensic_hasher.hash_with_metadata(input.data, "api")
    return result


@router.get("/hash-log")
async def get_hash_log():
    """Get the hash audit log."""
    return forensic_hasher.get_hash_log()


# ---- Timeline ----

@router.post("/timeline/event")
async def add_timeline_event(input: TimelineEventInput):
    """Add an event to the forensic timeline."""
    try:
        ts = datetime.fromisoformat(input.timestamp.replace("Z", "+00:00"))
    except (ValueError, TypeError):
        ts = datetime.now(timezone.utc)

    event = timeline_reconstructor.add_event(
        timestamp=ts,
        event_type=input.event_type,
        platform=input.platform,
        actor=input.actor,
        action=input.action,
        target=input.target,
        content_preview=input.content_preview,
        severity=input.severity,
    )
    return event


@router.get("/timeline")
async def get_timeline(
    platform: str = None, actor: str = None,
    event_type: str = None, limit: int = 100
):
    """Get the forensic timeline."""
    return timeline_reconstructor.get_timeline(
        platform=platform, actor=actor,
        event_type=event_type, limit=limit,
    )


@router.get("/timeline/gaps")
async def detect_timeline_gaps(interval_minutes: int = 60):
    """Detect gaps in the timeline."""
    return timeline_reconstructor.detect_gaps(interval_minutes)


@router.get("/timeline/patterns")
async def get_timeline_patterns():
    """Identify patterns in the timeline."""
    return timeline_reconstructor.find_patterns()


@router.get("/timeline/actor/{actor}")
async def get_actor_timeline(actor: str):
    """Get timeline for a specific actor."""
    return timeline_reconstructor.get_actor_timeline(actor)


@router.get("/timeline/statistics")
async def get_timeline_stats():
    """Get timeline statistics."""
    return timeline_reconstructor.get_statistics()


# ---- Account Correlation ----

@router.post("/correlation/register")
async def register_profiles(input: CorrelationInput):
    """Register profiles for correlation analysis."""
    ids = []
    for profile in input.profiles:
        pid = account_correlator.register_profile(profile)
        ids.append(pid)
    return {"registered": len(ids), "profile_ids": ids}


@router.post("/correlation/analyze")
async def correlate_profiles(input: ProfilePairInput):
    """Correlate two specific profiles."""
    result = account_correlator.correlate(input.profile1_id, input.profile2_id)
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])
    return result


@router.post("/correlation/analyze-all")
async def correlate_all():
    """Correlate all registered profiles."""
    return account_correlator.correlate_all()


@router.get("/correlation/results")
async def get_correlations():
    """Get all correlation results."""
    return account_correlator.get_correlations()


@router.get("/correlation/statistics")
async def get_correlation_stats():
    """Get correlation statistics."""
    return account_correlator.get_statistics()
