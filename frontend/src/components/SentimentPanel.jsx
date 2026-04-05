import { useState } from 'react';
import { useApi } from '../hooks/useApi';
import { api } from '../api/client';
import { Brain, TrendingUp, MessageCircle } from 'lucide-react';

export function SentimentPanel() {
  const { data: sentiments, loading } = useApi(api.getSentiments);
  const { data: topics } = useApi(api.getTopics);
  const { data: posts } = useApi(api.getPosts);
  const [filter, setFilter] = useState('all');

  if (loading) return <div className="loading-container"><div className="spinner" /><div className="loading-text">Analyzing sentiment...</div></div>;

  const distribution = { positive: 0, negative: 0, neutral: 0, mixed: 0 };
  (sentiments || []).forEach(s => { distribution[s.label] = (distribution[s.label] || 0) + 1; });
  const total = sentiments?.length || 1;

  // Merge post content with sentiment
  const merged = (sentiments || []).map(s => {
    const post = (posts || []).find(p => p.id === s.post_id);
    return { ...s, content: post?.content || '', author: post?.author_username || '', platform: post?.platform || '' };
  });

  const filtered = filter === 'all' ? merged : merged.filter(s => s.label === filter);

  return (
    <div className="animate-in">
      <div className="page-header">
        <h1 className="page-title">Sentiment Analysis</h1>
        <p className="page-subtitle">AI-powered sentiment scoring using VADER + emoji analysis</p>
      </div>

      {/* Overview Row */}
      <div className="grid-2" style={{ marginBottom: '20px' }}>
        <div className="card">
          <div className="card-header">
            <div className="card-title"><Brain size={16} className="icon" /> Sentiment Breakdown</div>
          </div>
          <div className="card-body">
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
              <GaugeMeter label="Positive" value={distribution.positive} total={total} color="var(--accent-green)" />
              <GaugeMeter label="Negative" value={distribution.negative} total={total} color="var(--accent-red)" />
              <GaugeMeter label="Neutral" value={distribution.neutral} total={total} color="var(--text-muted)" />
              <GaugeMeter label="Mixed" value={distribution.mixed} total={total} color="var(--accent-amber)" />
            </div>
          </div>
        </div>

        <div className="card">
          <div className="card-header">
            <div className="card-title"><TrendingUp size={16} className="icon" /> Discovered Topics</div>
          </div>
          <div className="card-body">
            {topics?.topics?.map((topic, i) => (
              <div key={i} style={{ marginBottom: '12px' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '4px' }}>
                  <span style={{ fontSize: '13px', fontWeight: 600, color: 'var(--text-primary)' }}>{topic.label}</span>
                  <span style={{ fontSize: '11px', color: 'var(--text-muted)' }}>{topic.document_count} docs</span>
                </div>
                <div className="score-bar-bg">
                  <div className="score-bar-fill blue" style={{ width: `${Math.min(100, topic.score * 10)}%` }} />
                </div>
                <div style={{ display: 'flex', gap: '4px', flexWrap: 'wrap', marginTop: '4px' }}>
                  {topic.keywords?.slice(0, 5).map((kw, j) => (
                    <span key={j} className="topic-tag" style={{ fontSize: '10px', padding: '2px 6px' }}>{kw}</span>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Filter + Post List */}
      <div className="card">
        <div className="card-header">
          <div className="card-title"><MessageCircle size={16} className="icon" /> Analyzed Posts ({filtered.length})</div>
          <div className="tab-nav">
            {['all', 'positive', 'negative', 'neutral', 'mixed'].map(f => (
              <button key={f} className={`tab-btn ${filter === f ? 'active' : ''}`} onClick={() => setFilter(f)}>
                {f.charAt(0).toUpperCase() + f.slice(1)}
              </button>
            ))}
          </div>
        </div>
        <div className="card-body" style={{ maxHeight: '500px', overflowY: 'auto' }}>
          {filtered.slice(0, 30).map((item, i) => (
            <div key={i} className="evidence-card" style={{ animationDelay: `${i * 30}ms` }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '6px' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <span className={`platform-badge ${item.platform}`}>{item.platform}</span>
                  <span className="username">@{item.author}</span>
                </div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <span className={`sentiment-badge ${item.label}`}>{item.label}</span>
                  <span style={{ fontFamily: 'var(--font-mono)', fontSize: '12px', color: scoreColor(item.compound) }}>
                    {item.compound > 0 ? '+' : ''}{item.compound?.toFixed(3)}
                  </span>
                </div>
              </div>
              <div style={{ fontSize: '13px', color: 'var(--text-secondary)', lineHeight: 1.5 }}>
                {item.content?.slice(0, 200)}
              </div>
              <div style={{ display: 'flex', gap: '16px', marginTop: '6px', fontSize: '11px', color: 'var(--text-muted)' }}>
                <span>Pos: {(item.positive * 100).toFixed(0)}%</span>
                <span>Neg: {(item.negative * 100).toFixed(0)}%</span>
                <span>Neu: {(item.neutral * 100).toFixed(0)}%</span>
                <span>Confidence: {(item.confidence * 100).toFixed(0)}%</span>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

function GaugeMeter({ label, value, total, color }) {
  const pct = ((value / total) * 100).toFixed(1);
  const circumference = 2 * Math.PI * 38;
  const offset = circumference - (circumference * value) / total;

  return (
    <div className="gauge-container">
      <svg width="90" height="90" viewBox="0 0 90 90">
        <circle cx="45" cy="45" r="38" fill="none" stroke="rgba(255,255,255,0.06)" strokeWidth="6" />
        <circle
          cx="45" cy="45" r="38" fill="none" stroke={color} strokeWidth="6"
          strokeLinecap="round" strokeDasharray={circumference} strokeDashoffset={offset}
          transform="rotate(-90 45 45)"
          style={{ transition: 'stroke-dashoffset 1s ease-out' }}
        />
        <text x="45" y="42" textAnchor="middle" fill={color} fontSize="18" fontWeight="700" fontFamily="var(--font-mono)">
          {value}
        </text>
        <text x="45" y="56" textAnchor="middle" fill="var(--text-muted)" fontSize="9">
          {pct}%
        </text>
      </svg>
      <div className="gauge-label">{label}</div>
    </div>
  );
}

function scoreColor(score) {
  if (score > 0.3) return 'var(--accent-green)';
  if (score < -0.3) return 'var(--accent-red)';
  return 'var(--text-muted)';
}
