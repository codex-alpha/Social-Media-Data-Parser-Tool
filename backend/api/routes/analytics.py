"""Analytics API routes - AI/ML analysis endpoints."""
from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any, Optional
from pydantic import BaseModel

from ai.sentiment import sentiment_analyzer
from ai.topic_modeling import topic_modeler
from ai.fake_news import fake_news_detector
from ai.bot_detection import bot_detector
from ai.anomaly import anomaly_detector
from models.schemas import UserProfile, Platform
from datetime import datetime

router = APIRouter(prefix="/analytics", tags=["AI Analytics"])


class TextInput(BaseModel):
    text: str
    id: str = ""


class BatchTextInput(BaseModel):
    texts: List[Dict[str, str]]


class TopicInput(BaseModel):
    texts: List[str]
    n_topics: int = 5
    method: str = "nmf"


class ProfileInput(BaseModel):
    id: str = ""
    platform: str = "twitter"
    username: str = ""
    display_name: str = ""
    bio: str = ""
    followers_count: int = 0
    following_count: int = 0
    posts_count: int = 0
    account_created: Optional[str] = None
    verified: bool = False


class FakeNewsInput(BaseModel):
    text: str
    post_id: str = ""
    urls: List[str] = []


@router.post("/sentiment")
async def analyze_sentiment(input: TextInput):
    """Analyze sentiment of a text."""
    result = sentiment_analyzer.analyze(input.text, input.id)
    return result.model_dump()


@router.post("/sentiment/batch")
async def analyze_sentiment_batch(input: BatchTextInput):
    """Analyze sentiment of multiple texts."""
    results = sentiment_analyzer.analyze_batch(input.texts)
    aggregate = sentiment_analyzer.get_aggregate_sentiment(results)
    return {
        "results": [r.model_dump() for r in results],
        "aggregate": aggregate,
    }


@router.post("/topics")
async def extract_topics(input: TopicInput):
    """Extract topics from a collection of texts."""
    topics = topic_modeler.extract_topics(input.texts, input.n_topics, input.method)
    keywords = topic_modeler.get_trending_keywords(input.texts)
    return {
        "topics": [t.model_dump() for t in topics],
        "trending_keywords": keywords,
    }


@router.post("/fake-news")
async def detect_fake_news(input: FakeNewsInput):
    """Detect fake news indicators in text."""
    result = fake_news_detector.detect(input.text, input.post_id, input.urls)
    return result.model_dump()


@router.post("/bot-detection")
async def detect_bot(input: ProfileInput):
    """Detect if a user profile exhibits bot-like behavior."""
    account_created = None
    if input.account_created:
        try:
            account_created = datetime.fromisoformat(input.account_created.replace("Z", "+00:00"))
        except (ValueError, TypeError):
            pass

    profile = UserProfile(
        id=input.id or "unknown",
        platform=Platform(input.platform) if input.platform in [e.value for e in Platform] else Platform.UNKNOWN,
        username=input.username,
        display_name=input.display_name,
        bio=input.bio,
        followers_count=input.followers_count,
        following_count=input.following_count,
        posts_count=input.posts_count,
        account_created=account_created,
        verified=input.verified,
    )
    result = bot_detector.detect(profile)
    return result.model_dump()


@router.get("/anomalies/health")
async def get_anomaly_health():
    """Get anomaly detection system health."""
    return anomaly_detector.get_system_health()
