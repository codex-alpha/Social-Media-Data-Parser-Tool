"""Data models for social media posts and analysis results."""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone
from enum import Enum
import uuid


class Platform(str, Enum):
    TWITTER = "twitter"
    INSTAGRAM = "instagram"
    FACEBOOK = "facebook"
    REDDIT = "reddit"
    UNKNOWN = "unknown"


class SentimentLabel(str, Enum):
    POSITIVE = "positive"
    NEGATIVE = "negative"
    NEUTRAL = "neutral"
    MIXED = "mixed"


class ThreatLevel(str, Enum):
    NONE = "none"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class SocialPost(BaseModel):
    """Unified social media post model."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    platform: Platform
    platform_id: str = ""
    author_id: str = ""
    author_username: str = ""
    author_display_name: str = ""
    content: str = ""
    content_type: str = "text"
    hashtags: List[str] = []
    mentions: List[str] = []
    urls: List[str] = []
    media_urls: List[str] = []
    language: str = "en"
    geolocation: Optional[Dict[str, float]] = None
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    likes: int = 0
    shares: int = 0
    comments: int = 0
    raw_data: Dict[str, Any] = {}
    is_repost: bool = False
    parent_id: Optional[str] = None


class UserProfile(BaseModel):
    """Social media user profile."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    platform: Platform
    platform_user_id: str = ""
    username: str = ""
    display_name: str = ""
    bio: str = ""
    followers_count: int = 0
    following_count: int = 0
    posts_count: int = 0
    account_created: Optional[datetime] = None
    verified: bool = False
    profile_image_url: str = ""
    location: str = ""
    website: str = ""
    is_bot_suspect: bool = False
    bot_score: float = 0.0
    risk_level: ThreatLevel = ThreatLevel.NONE


class SentimentResult(BaseModel):
    """Sentiment analysis result."""
    post_id: str
    label: SentimentLabel
    score: float = 0.0
    compound: float = 0.0
    positive: float = 0.0
    negative: float = 0.0
    neutral: float = 0.0
    confidence: float = 0.0
    aspects: List[Dict[str, Any]] = []


class TopicResult(BaseModel):
    """Topic modeling result."""
    topic_id: int
    label: str
    keywords: List[str]
    score: float = 0.0
    document_count: int = 0


class FakeNewsResult(BaseModel):
    """Fake news detection result."""
    post_id: str
    is_fake: bool = False
    confidence: float = 0.0
    signals: List[Dict[str, Any]] = []
    credibility_score: float = 0.5
    reasoning: str = ""


class BotDetectionResult(BaseModel):
    """Bot detection result."""
    user_id: str
    username: str
    is_bot: bool = False
    bot_score: float = 0.0
    signals: Dict[str, float] = {}
    behavioral_flags: List[str] = []
    confidence: float = 0.0


class AnomalyResult(BaseModel):
    """Anomaly detection result."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    entity_type: str = "post"
    entity_id: str = ""
    anomaly_type: str = ""
    severity: ThreatLevel = ThreatLevel.LOW
    score: float = 0.0
    description: str = ""
    detected_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: Dict[str, Any] = {}


class ForensicRecord(BaseModel):
    """Digital forensic evidence record."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    evidence_type: str = "social_post"
    source_platform: Platform = Platform.UNKNOWN
    collected_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    collector_id: str = "system"
    sha256_hash: str = ""
    data_snapshot: Dict[str, Any] = {}
    chain_of_custody: List[Dict[str, Any]] = []
    is_deleted: bool = False
    is_edited: bool = False
    edit_history: List[Dict[str, Any]] = []
    timeline_events: List[Dict[str, Any]] = []
    related_accounts: List[str] = []
    integrity_verified: bool = True
    notes: str = ""


class AccountCorrelation(BaseModel):
    """Cross-platform account correlation."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    primary_account: str = ""
    correlated_accounts: List[Dict[str, Any]] = []
    correlation_score: float = 0.0
    signals: List[Dict[str, Any]] = []
    behavioral_similarity: float = 0.0
    temporal_overlap: float = 0.0
    linguistic_similarity: float = 0.0
    network_overlap: float = 0.0


class TimelineEvent(BaseModel):
    """Timeline event for forensic reconstruction."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    event_type: str = ""
    platform: Platform = Platform.UNKNOWN
    actor: str = ""
    action: str = ""
    target: str = ""
    content_preview: str = ""
    metadata: Dict[str, Any] = {}
    forensic_hash: str = ""
    severity: ThreatLevel = ThreatLevel.NONE
