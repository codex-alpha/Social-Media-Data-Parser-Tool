import { useApi } from '../hooks/useApi';
import { api } from '../api/client';
import { Clock, AlertTriangle, TrendingUp, BarChart3 } from 'lucide-react';

export function TimelinePanel() {
  const { data, loading } = useApi(api.getTimeline);

  if (loading) return <div className="loading-container"><div className="spinner" /><div className="loading-text">Reconstructing timeline...</div></div>;

  const events = data?.events || [];
  const gaps = data?.gaps || [];
  const patterns = data?.patterns || {};

  const hourlyDist = patterns.hourly_distribution || [];
  const maxHour = Math.max(...hourlyDist, 1);
  const topActors = patterns.top_actors || [];

  return (
    <div className="animate-in">
      <div className="page-header">
        <h1 className="page-title">Forensic Event Timeline</h1>
        <p className="page-subtitle">Chronological reconstruction of all tracked events with gap and burst detection</p>
      </div>

      {/* Stats */}
      <div className="stats-grid stagger" style={{ gridTemplateColumns: 'repeat(4, 1fr)' }}>
        <div className="stat-card blue">
          <div className="stat-icon"><Clock size={20} /></div>
          <div className="stat-value">{events.length}</div>
          <div className="stat-label">Total Events</div>
        </div>
        <div className="stat-card amber">
          <div className="stat-icon"><AlertTriangle size={20} /></div>
          <div className="stat-value">{gaps.length}</div>
          <div className="stat-label">Gaps Detected</div>
        </div>
        <div className="stat-card purple">
          <div className="stat-icon"><TrendingUp size={20} /></div>
          <div className="stat-value">{patterns.bursts_detected || 0}</div>
          <div className="stat-label">Activity Bursts</div>
        </div>
        <div className="stat-card green">
          <div className="stat-icon"><BarChart3 size={20} /></div>
          <div className="stat-value">{patterns.peak_activity_hour != null ? `${patterns.peak_activity_hour}:00` : 'N/A'}</div>
          <div className="stat-label">Peak Hour</div>
        </div>
      </div>

      <div className="grid-2-1">
        {/* Hourly Activity Chart */}
        <div className="card">
          <div className="card-header">
            <div className="card-title"><BarChart3 size={16} className="icon" /> Hourly Activity Distribution</div>
          </div>
          <div className="card-body">
            <div style={{ display: 'flex', alignItems: 'flex-end', gap: '3px', height: '120px' }}>
              {hourlyDist.map((count, hour) => (
                <div key={hour} style={{ flex: 1, display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '4px' }}>
                  <div
                    style={{
                      width: '100%',
                      height: `${(count / maxHour) * 100}px`,
                      background: hour === patterns.peak_activity_hour
                        ? 'var(--gradient-blue)'
                        : 'rgba(59, 130, 246, 0.3)',
                      borderRadius: '3px 3px 0 0',
                      transition: 'height 0.5s ease-out',
                      minHeight: count > 0 ? '4px' : '0',
                    }}
                    title={`${hour}:00 - ${count} events`}
                  />
                  {hour % 4 === 0 && (
                    <span style={{ fontSize: '9px', color: 'var(--text-muted)' }}>{hour}h</span>
                  )}
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Top Actors */}
        <div className="card">
          <div className="card-header">
            <div className="card-title">Top Actors</div>
          </div>
          <div className="card-body">
            {topActors.slice(0, 8).map(([actor, count], i) => (
              <div key={i} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '6px 0', borderBottom: '1px solid var(--border-subtle)' }}>
                <span className="username" style={{ fontSize: '12px' }}>@{actor}</span>
                <span style={{ fontFamily: 'var(--font-mono)', fontSize: '12px', color: 'var(--accent-blue)' }}>{count}</span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Gaps */}
      {gaps.length > 0 && (
        <div className="card" style={{ marginBottom: '20px' }}>
          <div className="card-header">
            <div className="card-title"><AlertTriangle size={16} style={{ color: 'var(--accent-amber)' }} /> Detected Gaps</div>
          </div>
          <div className="card-body">
            <table className="data-table">
              <thead>
                <tr>
                  <th>Gap Start</th>
                  <th>Gap End</th>
                  <th>Duration</th>
                  <th>Status</th>
                </tr>
              </thead>
              <tbody>
                {gaps.slice(0, 10).map((gap, i) => (
                  <tr key={i}>
                    <td style={{ fontFamily: 'var(--font-mono)', fontSize: '11px' }}>{new Date(gap.gap_start).toLocaleString()}</td>
                    <td style={{ fontFamily: 'var(--font-mono)', fontSize: '11px' }}>{new Date(gap.gap_end).toLocaleString()}</td>
                    <td>{gap.duration_hours?.toFixed(1)}h</td>
                    <td>
                      <span className={`threat-badge ${gap.suspicious ? 'high' : 'low'}`}>
                        {gap.suspicious ? 'SUSPICIOUS' : 'NORMAL'}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Event Timeline */}
      <div className="card">
        <div className="card-header">
          <div className="card-title"><Clock size={16} className="icon" /> Event Timeline</div>
          <span style={{ fontSize: '11px', color: 'var(--text-muted)' }}>{events.length} events</span>
        </div>
        <div className="card-body" style={{ maxHeight: '500px', overflowY: 'auto' }}>
          <div className="timeline-container">
            {events.slice(0, 40).map((event, i) => (
              <div key={i} className={`timeline-event ${event.severity}`}>
                <div className="timeline-event-header">
                  <span className="timeline-time">{new Date(event.timestamp).toLocaleString()}</span>
                  <span className={`platform-badge ${event.platform}`}>{event.platform}</span>
                  <span className={`threat-badge ${event.severity}`}>{event.severity}</span>
                </div>
                <div className="timeline-event-body">
                  <span className="timeline-actor">@{event.actor}</span>
                  <span style={{ margin: '0 6px', color: 'var(--text-muted)' }}>→</span>
                  <span>{event.action}</span>
                  {event.target && (
                    <>
                      <span style={{ margin: '0 6px', color: 'var(--text-muted)' }}>→</span>
                      <span className="username">@{event.target}</span>
                    </>
                  )}
                </div>
                {event.content_preview && (
                  <div style={{ fontSize: '11px', color: 'var(--text-muted)', marginTop: '4px', fontStyle: 'italic' }}>
                    "{event.content_preview.slice(0, 100)}..."
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
