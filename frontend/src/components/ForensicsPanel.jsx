import { useState } from 'react';
import { useApi } from '../hooks/useApi';
import { api } from '../api/client';
import { Shield, Link, Hash, FileCheck, Lock, Eye } from 'lucide-react';

export function ForensicsPanel() {
  const { data, loading } = useApi(api.getEvidence);
  const { data: correlations } = useApi(api.getCorrelations);
  const [tab, setTab] = useState('evidence');

  if (loading) return <div className="loading-container"><div className="spinner" /><div className="loading-text">Loading forensic records...</div></div>;

  const evidence = data?.evidence || [];
  const stats = data?.statistics || {};
  const custodyLog = data?.custody_log || [];
  const corrs = (correlations || []).filter(c => c.correlation_score > 0.3).sort((a, b) => b.correlation_score - a.correlation_score);

  return (
    <div className="animate-in">
      <div className="page-header">
        <h1 className="page-title">Digital Forensics</h1>
        <p className="page-subtitle">Chain of custody, evidence hashing, and cross-platform account correlation</p>
      </div>

      {/* Stats */}
      <div className="stats-grid stagger" style={{ gridTemplateColumns: 'repeat(4, 1fr)' }}>
        <div className="stat-card green">
          <div className="stat-icon"><Shield size={20} /></div>
          <div className="stat-value">{stats.total_evidence || 0}</div>
          <div className="stat-label">Evidence Records</div>
        </div>
        <div className="stat-card blue">
          <div className="stat-icon"><Hash size={20} /></div>
          <div className="stat-value">{stats.total_custody_events || 0}</div>
          <div className="stat-label">Custody Events</div>
        </div>
        <div className="stat-card purple">
          <div className="stat-icon"><Link size={20} /></div>
          <div className="stat-value">{corrs.length}</div>
          <div className="stat-label">Account Correlations</div>
        </div>
        <div className="stat-card amber">
          <div className="stat-icon"><FileCheck size={20} /></div>
          <div className="stat-value">{stats.platforms?.length || 0}</div>
          <div className="stat-label">Platforms Tracked</div>
        </div>
      </div>

      {/* Tabs */}
      <div className="tab-nav" style={{ display: 'inline-flex', marginBottom: '20px' }}>
        <button className={`tab-btn ${tab === 'evidence' ? 'active' : ''}`} onClick={() => setTab('evidence')}>
          Evidence ({evidence.length})
        </button>
        <button className={`tab-btn ${tab === 'custody' ? 'active' : ''}`} onClick={() => setTab('custody')}>
          Chain of Custody
        </button>
        <button className={`tab-btn ${tab === 'correlation' ? 'active' : ''}`} onClick={() => setTab('correlation')}>
          Account Correlation ({corrs.length})
        </button>
      </div>

      {/* Evidence Tab */}
      {tab === 'evidence' && (
        <div className="card animate-slide">
          <div className="card-header">
            <div className="card-title"><Shield size={16} className="icon" /> Collected Evidence</div>
          </div>
          <div className="card-body" style={{ maxHeight: '600px', overflowY: 'auto' }}>
            {evidence.slice(0, 20).map((ev, i) => (
              <div key={i} className="evidence-card">
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                    <span className="evidence-id">{ev.evidence_id}</span>
                    <span className={`platform-badge ${ev.source_platform}`}>{ev.source_platform}</span>
                  </div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                    {ev.is_deleted && <span className="threat-badge high">DELETED</span>}
                    {ev.is_edited && <span className="threat-badge medium">EDITED</span>}
                    {ev.integrity_verified !== false && <span className="threat-badge none"><Lock size={10} /> INTACT</span>}
                  </div>
                </div>

                <div className="evidence-hash">
                  SHA-256: {ev.integrity_hash}
                </div>

                <div style={{ display: 'flex', gap: '16px', marginTop: '8px', fontSize: '11px', color: 'var(--text-muted)' }}>
                  <span>Type: {ev.evidence_type}</span>
                  <span>Collected: {new Date(ev.collected_at).toLocaleString()}</span>
                  <span>Chain: {ev.chain_of_custody?.length || 0} events</span>
                </div>

                {ev.data_snapshot?.content && (
                  <div style={{ marginTop: '8px', fontSize: '12px', color: 'var(--text-secondary)', borderLeft: '2px solid var(--border-primary)', paddingLeft: '10px' }}>
                    {ev.data_snapshot.content.slice(0, 150)}...
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Custody Log Tab */}
      {tab === 'custody' && (
        <div className="card animate-slide">
          <div className="card-header">
            <div className="card-title"><Eye size={16} className="icon" /> Custody Audit Trail</div>
          </div>
          <div className="card-body" style={{ maxHeight: '600px', overflowY: 'auto' }}>
            <div className="timeline-container">
              {custodyLog.slice(0, 30).map((event, i) => (
                <div key={i} className={`timeline-event ${event.action === 'COLLECTED' ? '' : 'medium'}`}>
                  <div className="timeline-event-header">
                    <span className="timeline-time">{new Date(event.timestamp).toLocaleString()}</span>
                    <span className={`threat-badge ${event.action === 'COLLECTED' ? 'none' : event.action === 'VERIFIED' ? 'low' : 'medium'}`}>
                      {event.action}
                    </span>
                  </div>
                  <div className="timeline-event-body">
                    <span className="evidence-id" style={{ fontSize: '10px' }}>{event.evidence_id}</span>
                    {event.notes && <span style={{ marginLeft: '8px', color: 'var(--text-muted)' }}>— {event.notes}</span>}
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Account Correlation Tab */}
      {tab === 'correlation' && (
        <div className="card animate-slide">
          <div className="card-header">
            <div className="card-title"><Link size={16} style={{ color: 'var(--accent-purple)' }} /> Cross-Platform Account Correlation</div>
          </div>
          <div className="card-body" style={{ maxHeight: '600px', overflowY: 'auto' }}>
            {corrs.map((corr, i) => (
              <div key={i} className="evidence-card">
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '10px' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                    <div style={{ textAlign: 'center' }}>
                      <div className={`platform-badge ${corr.profile1?.platform}`}>{corr.profile1?.platform}</div>
                      <div className="username" style={{ marginTop: '4px' }}>@{corr.profile1?.username}</div>
                    </div>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
                      <div style={{ width: '40px', height: '2px', background: 'var(--accent-purple)' }} />
                      <Link size={14} style={{ color: 'var(--accent-purple)' }} />
                      <div style={{ width: '40px', height: '2px', background: 'var(--accent-purple)' }} />
                    </div>
                    <div style={{ textAlign: 'center' }}>
                      <div className={`platform-badge ${corr.profile2?.platform}`}>{corr.profile2?.platform}</div>
                      <div className="username" style={{ marginTop: '4px' }}>@{corr.profile2?.username}</div>
                    </div>
                  </div>
                  <div style={{ textAlign: 'right' }}>
                    <span className={`threat-badge ${corr.risk_assessment === 'HIGH' ? 'critical' : corr.risk_assessment === 'MEDIUM' ? 'medium' : 'low'}`}>
                      {corr.risk_assessment}
                    </span>
                    <div style={{ fontSize: '18px', fontWeight: 700, fontFamily: 'var(--font-mono)', color: 'var(--accent-purple)', marginTop: '4px' }}>
                      {(corr.correlation_score * 100).toFixed(0)}%
                    </div>
                  </div>
                </div>

                {/* Signal breakdown */}
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '8px' }}>
                  {Object.entries(corr.signals || {}).map(([key, val]) => (
                    <div key={key}>
                      <div className="score-label">
                        <span>{key.replace(/_/g, ' ')}</span>
                        <span>{(val * 100).toFixed(0)}%</span>
                      </div>
                      <div className="score-bar-bg">
                        <div className={`score-bar-fill ${val > 0.6 ? 'purple' : val > 0.3 ? 'blue' : 'green'}`}
                          style={{ width: `${val * 100}%` }} />
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            ))}
            {corrs.length === 0 && <div className="empty-state">No significant correlations found</div>}
          </div>
        </div>
      )}
    </div>
  );
}
