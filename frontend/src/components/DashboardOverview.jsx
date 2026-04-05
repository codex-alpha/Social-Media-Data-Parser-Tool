import { useApi } from '../hooks/useApi';
import { api } from '../api/client';
import { BarChart3, Users, Shield, Clock, AlertTriangle, Network, Brain, TrendingUp } from 'lucide-react';

export function DashboardOverview() {
  const { data, loading, error } = useApi(api.getDashboardOverview);
  const sentiments = useApi(api.getSentiments);
  const topics = useApi(api.getTopics);
  const fakeNews = useApi(api.getFakeNews);
  const bots = useApi(api.getBots);

  if (loading) return <Loading />;
  if (error) return <ErrorState message={error} />;
  if (!data) return null;

  const stats = data.stats;
  const threatSummary = data.threat_summary;

  // Compute sentiment distribution
  const sentimentDist = { positive: 0, negative: 0, neutral: 0, mixed: 0 };
  if (sentiments.data) {
    sentiments.data.forEach(s => { sentimentDist[s.label] = (sentimentDist[s.label] || 0) + 1; });
  }
  const totalSent = Object.values(sentimentDist).reduce((a, b) => a + b, 0) || 1;

  // Get top flagged fake news
  const flaggedPosts = (fakeNews.data || []).filter(f => f.is_fake).slice(0, 5);

  // Get top bots
  const topBots = (bots.data || []).filter(b => b.is_bot).sort((a, b) => b.bot_score - a.bot_score).slice(0, 5);

  return (
    <div className="animate-in">
      <div className="page-header">
        <h1 className="page-title">Intelligence Dashboard</h1>
        <p className="page-subtitle">Real-time social media intelligence & forensic analysis overview</p>
      </div>

      {/* Stats Grid */}
      <div className="stats-grid stagger">
        <StatCard color="blue" icon={<BarChart3 size={20} />} value={stats.total_posts_analyzed} label="Posts Analyzed" />
        <StatCard color="purple" icon={<Users size={20} />} value={stats.total_profiles_analyzed} label="Profiles Scanned" />
        <StatCard color="green" icon={<Shield size={20} />} value={stats.evidence_collected} label="Evidence Collected" />
        <StatCard color="amber" icon={<Clock size={20} />} value={stats.timeline_events} label="Timeline Events" />
        <StatCard color="red" icon={<AlertTriangle size={20} />} value={stats.threats_detected} label="Threats Detected" />
        <StatCard color="cyan" icon={<Network size={20} />} value={stats.active_correlations} label="Correlations" />
      </div>

      {/* Sentiment + Topics Row */}
      <div className="grid-2">
        <div className="card">
          <div className="card-header">
            <div className="card-title"><Brain size={16} className="icon" /> Sentiment Distribution</div>
          </div>
          <div className="card-body">
            <div style={{ display: 'flex', gap: '16px', marginBottom: '16px' }}>
              {Object.entries(sentimentDist).map(([key, val]) => (
                <SentimentBar key={key} label={key} count={val} total={totalSent} />
              ))}
            </div>
            <div style={{ display: 'flex', height: '12px', borderRadius: '6px', overflow: 'hidden', gap: '2px' }}>
              <div style={{ width: `${(sentimentDist.positive / totalSent) * 100}%`, background: 'var(--accent-green)', transition: 'width 1s' }} />
              <div style={{ width: `${(sentimentDist.neutral / totalSent) * 100}%`, background: 'var(--text-muted)', transition: 'width 1s' }} />
              <div style={{ width: `${(sentimentDist.mixed / totalSent) * 100}%`, background: 'var(--accent-amber)', transition: 'width 1s' }} />
              <div style={{ width: `${(sentimentDist.negative / totalSent) * 100}%`, background: 'var(--accent-red)', transition: 'width 1s' }} />
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: '8px' }}>
              <span style={{ fontSize: '11px', color: 'var(--accent-green)' }}>Positive</span>
              <span style={{ fontSize: '11px', color: 'var(--text-muted)' }}>Neutral</span>
              <span style={{ fontSize: '11px', color: 'var(--accent-amber)' }}>Mixed</span>
              <span style={{ fontSize: '11px', color: 'var(--accent-red)' }}>Negative</span>
            </div>
          </div>
        </div>

        <div className="card">
          <div className="card-header">
            <div className="card-title"><TrendingUp size={16} className="icon" /> Trending Topics</div>
          </div>
          <div className="card-body">
            {topics.data?.trending_keywords?.slice(0, 12).map((kw, i) => (
              <span key={i} className="topic-tag" style={{ fontSize: `${Math.max(11, 16 - i)}px` }}>
                {kw.keyword}
                <span style={{ opacity: 0.5, marginLeft: '4px', fontSize: '10px' }}>
                  {(kw.score * 100).toFixed(0)}
                </span>
              </span>
            ))}
            {!topics.data && <span className="loading-text">Loading topics...</span>}
          </div>
        </div>
      </div>

      {/* Threats Row */}
      <div className="grid-2">
        <div className="card">
          <div className="card-header">
            <div className="card-title"><AlertTriangle size={16} style={{ color: 'var(--accent-red)' }} /> Fake News Alerts</div>
            <span className="threat-badge critical">{threatSummary.fake_news_detected} Flagged</span>
          </div>
          <div className="card-body" style={{ maxHeight: '300px', overflowY: 'auto' }}>
            {flaggedPosts.length === 0 ? (
              <div className="empty-state">No fake news detected</div>
            ) : flaggedPosts.map((item, i) => (
              <div key={i} className="evidence-card">
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '6px' }}>
                  <span className="threat-badge high">Fake — {(item.confidence * 100).toFixed(0)}%</span>
                  <span style={{ fontSize: '11px', color: 'var(--text-muted)' }}>
                    Credibility: {(item.credibility_score * 100).toFixed(0)}%
                  </span>
                </div>
                <div style={{ fontSize: '12px', color: 'var(--text-secondary)', marginBottom: '6px' }}>
                  {item.reasoning}
                </div>
                <div style={{ display: 'flex', gap: '4px', flexWrap: 'wrap' }}>
                  {item.signals?.map((s, j) => (
                    <span key={j} style={{ fontSize: '10px', color: 'var(--accent-orange)', background: 'rgba(249,115,22,0.1)', padding: '2px 6px', borderRadius: '4px' }}>
                      {s.signal}
                    </span>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="card">
          <div className="card-header">
            <div className="card-title"><Users size={16} style={{ color: 'var(--accent-purple)' }} /> Bot Detection</div>
            <span className="threat-badge medium">{threatSummary.bots_detected} Bots</span>
          </div>
          <div className="card-body" style={{ maxHeight: '300px', overflowY: 'auto' }}>
            {topBots.length === 0 ? (
              <div className="empty-state">No bots detected</div>
            ) : topBots.map((bot, i) => (
              <div key={i} className="evidence-card">
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
                  <span className="username">@{bot.username}</span>
                  <span className="threat-badge high">{(bot.bot_score * 100).toFixed(0)}% Bot</span>
                </div>
                <div className="score-bar-container">
                  <div className="score-bar-bg">
                    <div className="score-bar-fill red" style={{ width: `${bot.bot_score * 100}%` }} />
                  </div>
                </div>
                <div style={{ display: 'flex', gap: '4px', flexWrap: 'wrap', marginTop: '6px' }}>
                  {bot.behavioral_flags?.map((flag, j) => (
                    <span key={j} style={{ fontSize: '10px', color: 'var(--accent-red)', background: 'rgba(239,68,68,0.1)', padding: '2px 6px', borderRadius: '4px' }}>
                      {flag.replace(/_/g, ' ')}
                    </span>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}

function StatCard({ color, icon, value, label }) {
  return (
    <div className={`stat-card ${color}`}>
      <div className="stat-icon">{icon}</div>
      <div className="stat-value">{value}</div>
      <div className="stat-label">{label}</div>
    </div>
  );
}

function SentimentBar({ label, count, total }) {
  const pct = ((count / total) * 100).toFixed(1);
  const colorMap = { positive: 'var(--accent-green)', negative: 'var(--accent-red)', neutral: 'var(--text-muted)', mixed: 'var(--accent-amber)' };
  return (
    <div style={{ flex: 1, textAlign: 'center' }}>
      <div style={{ fontSize: '22px', fontWeight: 700, color: colorMap[label] }}>{count}</div>
      <div style={{ fontSize: '10px', color: 'var(--text-muted)', textTransform: 'capitalize' }}>{label}</div>
      <div style={{ fontSize: '10px', color: colorMap[label] }}>{pct}%</div>
    </div>
  );
}

function Loading() {
  return (
    <div className="loading-container">
      <div className="spinner" />
      <div className="loading-text">Loading intelligence data...</div>
    </div>
  );
}

function ErrorState({ message }) {
  return (
    <div className="loading-container">
      <AlertTriangle size={40} style={{ color: 'var(--accent-red)', opacity: 0.5 }} />
      <div className="loading-text">Error: {message}</div>
      <div style={{ fontSize: '12px', color: 'var(--text-muted)' }}>Make sure the backend is running on port 8000</div>
    </div>
  );
}
