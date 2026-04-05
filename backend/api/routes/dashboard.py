"""Dashboard API routes - aggregated data for the frontend dashboard."""
from fastapi import APIRouter
from typing import List, Dict, Any
from datetime import datetime, timezone

from mock_data import generate_mock_posts, generate_mock_profiles, generate_mock_timeline_events
from ai.sentiment import sentiment_analyzer
from ai.topic_modeling import topic_modeler
from ai.fake_news import fake_news_detector
from ai.bot_detection import bot_detector
from forensics.chain_of_custody import custody_manager
from forensics.timeline import timeline_reconstructor
from forensics.account_correlation import account_correlator
from forensics.hasher import forensic_hasher
from models.schemas import UserProfile, Platform

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])

# Cache generated data
_cached_data: Dict[str, Any] = {}


def _ensure_data():
    """Generate and cache demo data if not already done."""
    if _cached_data.get("initialized"):
        return

    # Generate mock posts
    posts = generate_mock_posts(60)
    profiles = generate_mock_profiles(20)
    timeline_events = generate_mock_timeline_events(40)
    _cached_data["posts"] = posts
    _cached_data["profiles"] = profiles
    _cached_data["timeline_events"] = timeline_events

    # Run sentiment analysis on all posts
    sentiments = []
    for post in posts:
        result = sentiment_analyzer.analyze(post["content"], post["id"])
        sentiments.append(result.model_dump())
    _cached_data["sentiments"] = sentiments

    # Run topic modeling
    texts = [p["content"] for p in posts]
    topics = topic_modeler.extract_topics(texts, n_topics=6)
    keywords = topic_modeler.get_trending_keywords(texts, top_n=15)
    _cached_data["topics"] = [t.model_dump() for t in topics]
    _cached_data["trending_keywords"] = keywords

    # Run fake news detection on all posts
    fake_results = []
    for post in posts:
        result = fake_news_detector.detect(post["content"], post["id"])
        fake_results.append(result.model_dump())
    _cached_data["fake_news"] = fake_results

    # Run bot detection on all profiles
    bot_results = []
    for profile_data in profiles:
        account_created = None
        if profile_data.get("account_created"):
            try:
                account_created = datetime.fromisoformat(profile_data["account_created"].replace("Z", "+00:00"))
            except (ValueError, TypeError):
                pass

        profile = UserProfile(
            id=profile_data.get("id", ""),
            platform=Platform(profile_data.get("platform", "unknown")),
            username=profile_data.get("username", ""),
            display_name=profile_data.get("display_name", ""),
            bio=profile_data.get("bio", ""),
            followers_count=profile_data.get("followers_count", 0),
            following_count=profile_data.get("following_count", 0),
            posts_count=profile_data.get("posts_count", 0),
            account_created=account_created,
            verified=profile_data.get("verified", False),
        )
        result = bot_detector.detect(profile)
        bot_results.append(result.model_dump())
    _cached_data["bot_detection"] = bot_results

    # Collect forensic evidence for some posts
    for post in posts[:20]:
        custody_manager.collect_evidence(
            data=post,
            source_platform=post["platform"],
            evidence_type="social_post",
        )
    _cached_data["evidence_count"] = 20

    # Add timeline events
    for event in timeline_events:
        try:
            ts = datetime.fromisoformat(event["timestamp"].replace("Z", "+00:00"))
        except (ValueError, TypeError):
            ts = datetime.now(timezone.utc)
        timeline_reconstructor.add_event(
            timestamp=ts,
            event_type=event["event_type"],
            platform=event["platform"],
            actor=event["actor"],
            action=event["action"],
            target=event.get("target", ""),
            content_preview=event.get("content_preview", ""),
            severity=event.get("severity", "none"),
        )

    # Register profiles for correlation
    for profile in profiles:
        account_correlator.register_profile(profile)

    # Run correlations
    correlations = account_correlator.correlate_all()
    _cached_data["correlations"] = correlations

    _cached_data["initialized"] = True


@router.get("/overview")
async def get_dashboard_overview():
    """Get complete dashboard overview with all analytics."""
    _ensure_data()

    sentiments = _cached_data.get("sentiments", [])
    aggregate = sentiment_analyzer.get_aggregate_sentiment(
        [sentiment_analyzer.analyze(p["content"], p["id"]) for p in _cached_data.get("posts", [])[:20]]
    )

    # Threat summary
    fake_news = _cached_data.get("fake_news", [])
    fake_count = sum(1 for f in fake_news if f["is_fake"])

    bots = _cached_data.get("bot_detection", [])
    bot_count = sum(1 for b in bots if b["is_bot"])

    forensic_stats = custody_manager.get_statistics()
    timeline_stats = timeline_reconstructor.get_statistics()
    correlation_stats = account_correlator.get_statistics()

    return {
        "stats": {
            "total_posts_analyzed": len(_cached_data.get("posts", [])),
            "total_profiles_analyzed": len(_cached_data.get("profiles", [])),
            "evidence_collected": forensic_stats["total_evidence"],
            "timeline_events": timeline_stats["total_events"],
            "threats_detected": fake_count + bot_count,
            "active_correlations": correlation_stats["total_correlations"],
        },
        "sentiment_overview": aggregate,
        "threat_summary": {
            "fake_news_detected": fake_count,
            "bots_detected": bot_count,
            "high_risk_correlations": correlation_stats.get("high_risk", 0),
        },
        "system_status": "operational",
        "last_updated": datetime.now(timezone.utc).isoformat(),
    }


@router.get("/sentiments")
async def get_sentiments():
    """Get all sentiment analysis results."""
    _ensure_data()
    return _cached_data.get("sentiments", [])


@router.get("/topics")
async def get_topics():
    """Get topic modeling results."""
    _ensure_data()
    return {
        "topics": _cached_data.get("topics", []),
        "trending_keywords": _cached_data.get("trending_keywords", []),
    }


@router.get("/fake-news")
async def get_fake_news_results():
    """Get fake news detection results."""
    _ensure_data()
    return _cached_data.get("fake_news", [])


@router.get("/bots")
async def get_bot_results():
    """Get bot detection results."""
    _ensure_data()
    return _cached_data.get("bot_detection", [])


@router.get("/posts")
async def get_posts():
    """Get all analyzed posts."""
    _ensure_data()
    return _cached_data.get("posts", [])


@router.get("/profiles")
async def get_profiles():
    """Get all analyzed profiles."""
    _ensure_data()
    return _cached_data.get("profiles", [])


@router.get("/timeline")
async def get_dashboard_timeline():
    """Get forensic timeline for dashboard."""
    _ensure_data()
    events = timeline_reconstructor.get_timeline(limit=200)
    gaps = timeline_reconstructor.detect_gaps(120)
    patterns = timeline_reconstructor.find_patterns()
    return {
        "events": events,
        "gaps": gaps,
        "patterns": patterns,
    }


@router.get("/correlations")
async def get_dashboard_correlations():
    """Get account correlations for dashboard."""
    _ensure_data()
    return _cached_data.get("correlations", [])


@router.get("/evidence")
async def get_dashboard_evidence():
    """Get forensic evidence for dashboard."""
    _ensure_data()
    evidence = custody_manager.get_all_evidence()
    return {
        "evidence": evidence[:30],
        "statistics": custody_manager.get_statistics(),
        "custody_log": custody_manager.get_custody_log()[:50],
    }


@router.get("/social-graph")
async def get_social_graph():
    """Get social graph data for D3.js visualization."""
    _ensure_data()
    posts = _cached_data.get("posts", [])
    profiles = _cached_data.get("profiles", [])
    bots = _cached_data.get("bot_detection", [])
    correlations = _cached_data.get("correlations", [])

    # Build nodes from profiles
    bot_map = {b["user_id"]: b for b in bots}
    nodes = []
    for p in profiles:
        bot_info = bot_map.get(p["id"], {})
        nodes.append({
            "id": p["id"],
            "label": p["username"],
            "platform": p["platform"],
            "followers": p["followers_count"],
            "is_bot": bot_info.get("is_bot", False),
            "bot_score": bot_info.get("bot_score", 0.0),
            "verified": p.get("verified", False),
            "group": p["platform"],
        })

    # Build edges from mentions and correlations
    links = []
    for post in posts:
        for mention in post.get("mentions", []):
            mention_username = mention.replace("@", "")
            source_profile = next((p for p in profiles if p["username"] == post["author_username"]), None)
            target_profile = next((p for p in profiles if p["username"] == mention_username), None)
            if source_profile and target_profile:
                links.append({
                    "source": source_profile["id"],
                    "target": target_profile["id"],
                    "type": "mention",
                    "weight": 1,
                })

    # Add correlation edges
    for corr in correlations:
        if corr.get("correlation_score", 0) > 0.3:
            links.append({
                "source": corr["profile1"]["id"],
                "target": corr["profile2"]["id"],
                "type": "correlation",
                "weight": corr["correlation_score"],
            })

    # Deduplicate links
    seen = set()
    unique_links = []
    for link in links:
        key = f"{link['source']}-{link['target']}-{link['type']}"
        if key not in seen:
            seen.add(key)
            unique_links.append(link)

    return {"nodes": nodes, "links": unique_links}
