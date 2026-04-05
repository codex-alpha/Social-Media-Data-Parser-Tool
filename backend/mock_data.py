"""Mock data generator for development and demonstration."""
import random
import uuid
from datetime import datetime, timedelta, timezone
from typing import List, Dict, Any


# Realistic usernames
USERNAMES = [
    "alex_tech42", "sara_codes", "news_watch_bot", "marketguru99",
    "data_wizard_", "jane_analyst", "crypto_king_x", "bot_farm_001",
    "research_pro", "whistleblower_anon", "truth_seeker_21", "digital_nomad",
    "info_warrior", "science_nerd", "political_pulse", "media_critic_77",
    "deepfake_hunter", "cyber_sleuth", "osint_master", "privacy_hawk",
]

DISPLAY_NAMES = [
    "Alex Thompson", "Sara Chen", "News Watch 24/7", "Market Analysis",
    "Data Wizard", "Jane Rivera", "Crypto Insider", "Automated Updates",
    "Dr. Research", "Anonymous Source", "Truth Seeker", "Digital Nomad",
    "Info Wars Daily", "Science & Facts", "Political Pulse", "Media Watchdog",
    "DeepFake Hunter", "Cyber Detective", "OSINT Expert", "Privacy Advocate",
]

PLATFORMS = ["twitter", "instagram", "facebook", "reddit"]

REAL_POSTS = [
    "Just completed our annual security audit. The results highlight the need for stronger authentication measures across all platforms. #cybersecurity #infosec",
    "BREAKING: Scientists discover new deep-sea species off the coast of Japan. The bioluminescent creature was found at 3,000 meters depth. #science #discovery",
    "The new AI regulation framework passed today will reshape how companies develop and deploy machine learning models. Here's what you need to know 🧵",
    "Can't believe how amazing the sunset looked today from the rooftop! Sometimes you just need to stop and appreciate the beauty around us 🌅",
    "Hot take: Most 'productivity hacks' are just procrastination with extra steps. Just do the work. #unpopularopinion",
    "Our team just shipped v2.0! Months of work, hundreds of bug fixes, and a completely redesigned UI. So proud of everyone involved 🚀",
    "The data doesn't lie — renewable energy adoption grew 35% year over year. Solar panel costs dropped another 12%. The future is green ♻️",
    "Just finished reading 'The Alignment Problem' by Brian Christian. Essential reading for anyone working in AI safety. Highly recommend! 📚",
    "Unpacking the latest data breach: 2.3M records exposed due to misconfigured cloud storage. Companies MUST invest in security training. 🔒",
    "Morning workout done ✅ Cold shower ✅ Meditation ✅ Ready to conquer the day! Who else is up early grinding? 💪 #hustle #motivation",
]

FAKE_POSTS = [
    "SHOCKING: Government secretly spraying chemicals!! Scientists confirm 100% of clouds are artificial!! WAKE UP SHEEPLE!! They don't want you to know the TRUTH!!! 🚨🚨🚨",
    "URGENT BREAKING: Anonymous sources reveal that the entire stock market is a HOAX!! 95% of experts agree this is the biggest coverup in history!!!",
    "YOU WON'T BELIEVE what this insider just leaked!!! The mainstream media is HIDING this from you!! Share before they delete this!!! 😱😱",
    "EXCLUSIVE: Secret documents PROVE that all social media companies are selling your DNA to aliens. This is NOT a conspiracy theory. FACT: They admitted it!!!",
]

BOT_POSTS = [
    "Check out this amazing deal! Click link in bio!! 🔥🔥 #crypto #forex #earnmoney #freemoney",
    "Follow me for daily tips! DM for exclusive content! #followback #follow4follow",
    "Retweet if you agree! Like and subscribe for more! Share with 10 friends for good luck! 🍀",
    "Buy now!! Limited time offer!! 99% discount!! Visit www.totally-legit-site.com 🤑🤑🤑",
]

HASHTAGS_POOL = [
    "#cybersecurity", "#AI", "#datascience", "#infosec", "#privacy",
    "#machinelearning", "#deeplearning", "#tech", "#security", "#hacking",
    "#OSINT", "#forensics", "#investigation", "#breaking", "#news",
    "#python", "#coding", "#data", "#analysis", "#intelligence",
]


def generate_mock_posts(count: int = 50) -> List[Dict[str, Any]]:
    """Generate realistic mock social media posts."""
    posts = []
    base_time = datetime.now(timezone.utc) - timedelta(days=7)

    all_content = REAL_POSTS * 3 + FAKE_POSTS + BOT_POSTS

    for i in range(count):
        timestamp = base_time + timedelta(
            hours=random.randint(0, 168),
            minutes=random.randint(0, 59),
            seconds=random.randint(0, 59),
        )
        user_idx = random.randint(0, len(USERNAMES) - 1)
        content = random.choice(all_content)
        platform = random.choice(PLATFORMS)

        # Extract hashtags from content
        hashtags = [w for w in content.split() if w.startswith("#")]
        if not hashtags:
            hashtags = random.sample(HASHTAGS_POOL, random.randint(0, 3))

        post = {
            "id": str(uuid.uuid4()),
            "platform": platform,
            "platform_id": f"{platform}_{random.randint(100000, 999999)}",
            "author_id": f"user_{user_idx}",
            "author_username": USERNAMES[user_idx],
            "author_display_name": DISPLAY_NAMES[user_idx],
            "content": content,
            "content_type": "text",
            "hashtags": hashtags,
            "mentions": [f"@{random.choice(USERNAMES)}" for _ in range(random.randint(0, 2))],
            "urls": [],
            "language": "en",
            "timestamp": timestamp.isoformat(),
            "likes": random.randint(0, 5000) if user_idx < 15 else random.randint(0, 5),
            "shares": random.randint(0, 1000),
            "comments": random.randint(0, 500),
            "is_repost": random.random() < 0.15,
            "geolocation": random.choice([
                None,
                {"lat": round(random.uniform(25, 48), 4), "lon": round(random.uniform(-122, -73), 4)},
            ]),
        }
        posts.append(post)

    return sorted(posts, key=lambda x: x["timestamp"])


def generate_mock_profiles(count: int = 20) -> List[Dict[str, Any]]:
    """Generate mock user profiles for analysis."""
    profiles = []

    for i in range(min(count, len(USERNAMES))):
        is_bot = i in [2, 7, 16]  # Mark some as bots
        is_suspicious = i in [6, 10, 12]  # Mark some as suspicious

        days_old = random.randint(7 if is_bot else 90, 365 * 5)
        created = datetime.now(timezone.utc) - timedelta(days=days_old)
        posts_count = random.randint(500, 50000) if is_bot else random.randint(50, 5000)

        profile = {
            "id": f"user_{i}",
            "platform": random.choice(PLATFORMS),
            "platform_user_id": f"plat_{random.randint(10000, 99999)}",
            "username": USERNAMES[i],
            "display_name": DISPLAY_NAMES[i],
            "bio": random.choice([
                "AI researcher | Data scientist | Coffee lover ☕",
                "Breaking news and analysis 24/7",
                "Follow back! DM for collabs! 🔥 #crypto #forex",
                "Investigative journalist. Truth matters.",
                "Software engineer @BigTech. Views are my own.",
                "🤖 Automated news aggregator",
                "OSINT analyst | Digital forensics | Privacy advocate",
                "",
            ]),
            "followers_count": random.randint(10, 50) if is_bot else random.randint(100, 500000),
            "following_count": random.randint(5000, 50000) if is_bot else random.randint(50, 5000),
            "posts_count": posts_count,
            "account_created": created.isoformat(),
            "verified": not is_bot and random.random() < 0.3,
            "location": random.choice(["New York, USA", "London, UK", "Tokyo, Japan", "Berlin, DE", "", "Unknown"]),
            # Correlation metadata
            "posts_per_day": round(posts_count / max(days_old, 1), 2),
            "active_hours": sorted(random.sample(range(24), random.randint(4, 12))),
            "languages": random.sample(["en", "es", "fr", "de", "ja", "ar"], random.randint(1, 3)),
            "frequent_hashtags": random.sample(HASHTAGS_POOL, random.randint(2, 6)),
            "vocabulary_sample": random.sample([
                "data", "analysis", "security", "threat", "network",
                "intelligence", "privacy", "breach", "crypto", "malware",
                "forensics", "investigation", "evidence", "suspect", "track",
                "algorithm", "model", "training", "deploy", "monitor",
            ], random.randint(5, 12)),
            "device_fingerprint": {
                "os": random.choice(["iOS 18", "Android 15", "Windows 11", "macOS 15"]),
                "browser": random.choice(["Chrome 130", "Safari 19", "Firefox 135"]),
                "timezone": random.choice(["UTC-5", "UTC+0", "UTC+1", "UTC+9"]),
                "language": random.choice(["en-US", "en-GB", "es-ES"]),
            },
            "is_bot_suspect": is_bot,
            "is_suspicious": is_suspicious,
        }
        profiles.append(profile)

    # Create linked accounts (same person, different platforms)
    if len(profiles) >= 4:
        # Link user_0 and user_5 (same person)
        profiles[5]["username"] = "alex_tech"
        profiles[5]["platform"] = "instagram" if profiles[0]["platform"] != "instagram" else "reddit"
        profiles[5]["active_hours"] = profiles[0]["active_hours"]
        profiles[5]["languages"] = profiles[0]["languages"]
        profiles[5]["vocabulary_sample"] = profiles[0]["vocabulary_sample"]
        profiles[5]["device_fingerprint"] = profiles[0]["device_fingerprint"]

    return profiles


def generate_mock_timeline_events(count: int = 40) -> List[Dict[str, Any]]:
    """Generate mock timeline events for forensic analysis."""
    events = []
    base_time = datetime.now(timezone.utc) - timedelta(days=7)

    event_types = [
        ("post_created", "Created post", "none"),
        ("post_deleted", "Deleted post", "medium"),
        ("post_edited", "Edited post", "low"),
        ("account_created", "New account registered", "low"),
        ("login_detected", "Login from new device", "medium"),
        ("mass_follow", "Mass follow event detected", "high"),
        ("content_flagged", "Content flagged by AI", "high"),
        ("data_collected", "Evidence collected", "none"),
        ("suspicious_activity", "Unusual activity pattern", "high"),
        ("bot_detected", "Bot behavior detected", "critical"),
    ]

    for i in range(count):
        timestamp = base_time + timedelta(
            hours=random.randint(0, 168),
            minutes=random.randint(0, 59),
        )
        event_type, action, severity = random.choice(event_types)
        actor = random.choice(USERNAMES)

        events.append({
            "timestamp": timestamp.isoformat(),
            "event_type": event_type,
            "platform": random.choice(PLATFORMS),
            "actor": actor,
            "action": action,
            "target": random.choice(USERNAMES),
            "content_preview": random.choice(REAL_POSTS + FAKE_POSTS)[:100],
            "severity": severity,
            "metadata": {"source": "mock_data", "index": i},
        })

    return sorted(events, key=lambda x: x["timestamp"])
