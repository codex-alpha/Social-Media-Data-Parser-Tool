import { useState } from 'react';
import { useApi } from '../hooks/useApi';
import { api } from '../api/client';
import { AlertTriangle, Bot, ShieldAlert, Eye } from 'lucide-react';

export function ThreatPanel() {
  const { data: fakeNews, loading: fnLoading } = useApi(api.getFakeNews);
  const { data: bots, loading: botLoading } = useApi(api.getBots);
  const { data: posts } = useApi(api.getPosts);
  const [tab, setTab] = useState('fake');

  if (fnLoading || botLoading) return <div className="loading-container"><div className="spinner" /><div className="loading-text">Scanning for threats...</div></div>;

  const flaggedPosts = (fakeNews || []).filter(f => f.is_fake);
  const detectedBots = (bots || []).filter(b => b.is_bot).sort((a, b) => b.bot_score - a.bot_score);
  const allPosts = posts || [];

  return (
    <div className="animate-in">
      <div className="page-header">
        <h1 className="page-title">Threat Detection</h1>
        <p className="page-subtitle">AI-powered fake news detection & bot identification</p>
      </div>

      {/* Summary Stats */}
      <div className="stats-grid stagger" style={{ gridTemplateColumns: 'repeat(4, 1fr)' }}>
        <div className="stat-card red">
          <div className="stat-icon"><AlertTriangle size={20} /></div>
          <div className="stat-value">{flaggedPosts.length}</div>
          <div className="stat-label">Fake News Flagged</div>
        </div>
        <div className="stat-card purple">
          <div className="stat-icon"><Bot size={20} /></div>
          <div className="stat-value">{detectedBots.length}</div>
          <div className="stat-label">Bots Detected</div>
        </div>
        <div className="stat-card amber">
          <div className="stat-icon"><ShieldAlert size={20} /></div>
          <div className="stat-value">{(fakeNews || []).length}</div>
          <div className="stat-label">Posts Scanned</div>
        </div>
        <div className="stat-card blue">
          <div className="stat-icon"><Eye size={20} /></div>
          <div className="stat-value">{(bots || []).length}</div>
          <div className="stat-label">Profiles Analyzed</div>
        </div>
      </div>

      {/* Tab Navigation */}
      <div className="tab-nav" style={{ display: 'inline-flex', marginBottom: '20px' }}>
        <button className={`tab-btn ${tab === 'fake' ? 'active' : ''}`} onClick={() => setTab('fake')}>
          Fake News Detection ({flaggedPosts.length})
        </button>
        <button className={`tab-btn ${tab === 'bots' ? 'active' : ''}`} onClick={() => setTab('bots')}>
          Bot Detection ({detectedBots.length})
        </button>
        <button className={`tab-btn ${tab === 'all' ? 'active' : ''}`} onClick={() => setTab('all')}>
          All Scanned Posts
        </button>
      </div>

      {/* Fake News Tab */}
      {tab === 'fake' && (
        <div className="card animate-slide">
          <div className="card-header">
            <div className="card-title"><AlertTriangle size={16} style={{ color: 'var(--accent-red)' }} /> Flagged Misinformation</div>
          </div>
          <div className="card-body">
            {flaggedPosts.map((item, i) => {
              const post = allPosts.find(p => p.id === item.post_id);
              return (
                <div key={i} className="evidence-card">
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                      {post && <span className={`platform-badge ${post.platform}`}>{post.platform}</span>}
                      {post && <span className="username">@{post.author_username}</span>}
                    </div>
                    <span className="threat-badge critical">
                      {(item.confidence * 100).toFixed(0)}% Fake
                    </span>
                  </div>

                  {post && (
                    <div style={{ fontSize: '13px', color: 'var(--text-secondary)', marginBottom: '10px', lineHeight: 1.5, borderLeft: '3px solid var(--accent-red)', paddingLeft: '12px' }}>
                      {post.content?.slice(0, 250)}
                    </div>
                  )}

                  <div style={{ marginBottom: '8px' }}>
                    <div className="score-label">
                      <span>Credibility Score</span>
                      <span>{(item.credibility_score * 100).toFixed(0)}%</span>
                    </div>
                    <div className="score-bar-bg">
                      <div className="score-bar-fill green" style={{ width: `${item.credibility_score * 100}%` }} />
                    </div>
                  </div>

                  <div style={{ fontSize: '12px', color: 'var(--text-muted)', marginBottom: '6px' }}>
                    {item.reasoning}
                  </div>

                  <div style={{ display: 'flex', gap: '6px', flexWrap: 'wrap' }}>
                    {item.signals?.map((s, j) => (
                      <div key={j} style={{
                        fontSize: '11px', background: 'rgba(239,68,68,0.1)', border: '1px solid rgba(239,68,68,0.2)',
                        borderRadius: '6px', padding: '4px 8px', color: 'var(--accent-red)',
                      }}>
                        <strong>{s.signal.replace(/_/g, ' ')}</strong>
                        <span style={{ opacity: 0.7 }}> ({(s.score * 100).toFixed(0)}%)</span>
                      </div>
                    ))}
                  </div>
                </div>
              );
            })}
            {flaggedPosts.length === 0 && <div className="empty-state">No misinformation detected</div>}
          </div>
        </div>
      )}

      {/* Bot Detection Tab */}
      {tab === 'bots' && (
        <div className="card animate-slide">
          <div className="card-header">
            <div className="card-title"><Bot size={16} style={{ color: 'var(--accent-purple)' }} /> Detected Bots</div>
          </div>
          <div className="card-body">
            {detectedBots.map((bot, i) => (
              <div key={i} className="evidence-card">
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '10px' }}>
                  <span className="username" style={{ fontSize: '14px' }}>@{bot.username}</span>
                  <span className="threat-badge critical">{(bot.bot_score * 100).toFixed(0)}% Bot</span>
                </div>

                {/* Signal Scores */}
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '8px', marginBottom: '10px' }}>
                  {Object.entries(bot.signals || {}).map(([key, val]) => (
                    <div key={key}>
                      <div className="score-label">
                        <span>{key.replace(/_/g, ' ')}</span>
                        <span>{(val * 100).toFixed(0)}%</span>
                      </div>
                      <div className="score-bar-bg">
                        <div className={`score-bar-fill ${val > 0.6 ? 'red' : val > 0.3 ? 'amber' : 'green'}`}
                          style={{ width: `${val * 100}%` }} />
                      </div>
                    </div>
                  ))}
                </div>

                <div style={{ display: 'flex', gap: '4px', flexWrap: 'wrap' }}>
                  {bot.behavioral_flags?.map((flag, j) => (
                    <span key={j} style={{
                      fontSize: '10px', padding: '2px 8px', borderRadius: '4px',
                      background: 'rgba(139,92,246,0.1)', color: 'var(--accent-purple)',
                      border: '1px solid rgba(139,92,246,0.2)',
                    }}>
                      {flag.replace(/_/g, ' ')}
                    </span>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* All Posts Tab */}
      {tab === 'all' && (
        <div className="card animate-slide">
          <div className="card-header">
            <div className="card-title"><Eye size={16} className="icon" /> All Scanned Posts</div>
          </div>
          <div className="card-body" style={{ maxHeight: '600px', overflowY: 'auto' }}>
            <table className="data-table">
              <thead>
                <tr>
                  <th>Platform</th>
                  <th>Content</th>
                  <th>Credibility</th>
                  <th>Status</th>
                </tr>
              </thead>
              <tbody>
                {(fakeNews || []).slice(0, 40).map((item, i) => {
                  const post = allPosts.find(p => p.id === item.post_id);
                  return (
                    <tr key={i}>
                      <td><span className={`platform-badge ${post?.platform || ''}`}>{post?.platform || '?'}</span></td>
                      <td style={{ maxWidth: '400px', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                        {post?.content?.slice(0, 80)}...
                      </td>
                      <td>
                        <div className="score-bar-bg" style={{ width: '80px' }}>
                          <div className={`score-bar-fill ${item.credibility_score > 0.7 ? 'green' : item.credibility_score > 0.4 ? 'amber' : 'red'}`}
                            style={{ width: `${item.credibility_score * 100}%` }} />
                        </div>
                      </td>
                      <td>
                        <span className={`threat-badge ${item.is_fake ? 'critical' : 'none'}`}>
                          {item.is_fake ? 'FLAGGED' : 'CLEAN'}
                        </span>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}
