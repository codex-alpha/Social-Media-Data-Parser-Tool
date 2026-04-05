import { useState } from 'react';
import { api } from '../api/client';
import { Search, Brain, AlertTriangle, Bot, CheckCircle } from 'lucide-react';

export function ManualAnalysisPanel() {
  const [tab, setTab] = useState('text');
  
  // Text analysis state
  const [textInput, setTextInput] = useState('');
  const [textAnalyzing, setTextAnalyzing] = useState(false);
  const [sentimentResult, setSentimentResult] = useState(null);
  const [fakeNewsResult, setFakeNewsResult] = useState(null);

  // Profile analysis state
  const [profileInput, setProfileInput] = useState({
    username: '', platform: 'twitter', bio: '', followers_count: 0, following_count: 0, posts_count: 0
  });
  const [profileAnalyzing, setProfileAnalyzing] = useState(false);
  const [botResult, setBotResult] = useState(null);

  const handleTextAnalysis = async () => {
    if (!textInput.trim()) return;
    setTextAnalyzing(true);
    setSentimentResult(null);
    setFakeNewsResult(null);
    try {
      const [sent, fake] = await Promise.all([
        api.analyzeSentiment(textInput),
        api.detectFakeNews(textInput),
      ]);
      setSentimentResult(sent);
      setFakeNewsResult(fake);
    } catch (err) {
      console.error(err);
      alert('Analysis failed. Check console for details.');
    } finally {
      setTextAnalyzing(false);
    }
  };

  const handleProfileAnalysis = async () => {
    if (!profileInput.username.trim()) return;
    setProfileAnalyzing(true);
    setBotResult(null);
    try {
      const res = await api.detectBot(profileInput);
      setBotResult(res);
    } catch (err) {
      console.error(err);
      alert('Profile analysis failed.');
    } finally {
      setProfileAnalyzing(false);
    }
  };

  return (
    <div className="animate-in">
      <div className="page-header">
        <h1 className="page-title">Live Manual Analysis</h1>
        <p className="page-subtitle">Instantly analyze raw text or social profiles using the SMDPIS AI engines.</p>
      </div>

      <div className="tab-nav" style={{ display: 'inline-flex', marginBottom: '20px' }}>
        <button className={`tab-btn ${tab === 'text' ? 'active' : ''}`} onClick={() => setTab('text')}>
          Content Analysis
        </button>
        <button className={`tab-btn ${tab === 'profile' ? 'active' : ''}`} onClick={() => setTab('profile')}>
          Profile Bot Detection
        </button>
      </div>

      {tab === 'text' && (
        <div className="grid-2">
          {/* Input column */}
          <div className="card">
            <div className="card-header">
              <div className="card-title">Paste Text / Post Content</div>
            </div>
            <div className="card-body">
              <textarea 
                value={textInput}
                onChange={e => setTextInput(e.target.value)}
                placeholder="Enter social media post, article text, or any content to analyze for sentiment and fake news..."
                style={{ width: '100%', height: '180px', padding: '12px', background: 'var(--bg-card)', border: '1px solid var(--border-subtle)', borderRadius: '8px', color: 'var(--text-primary)', fontFamily: 'inherit', resize: 'none', marginBottom: '16px' }}
              />
              <button 
                onClick={handleTextAnalysis} 
                className="tab-btn active" 
                style={{ width: '100%', display: 'flex', justifyContent: 'center', gap: '8px', padding: '10px' }}
                disabled={textAnalyzing || !textInput.trim()}
              >
                {textAnalyzing ? <div className="spinner" style={{ width: '16px', height: '16px', borderTopColor: 'transparent', borderWidth: '2px' }} /> : <Search size={16} />} 
                {textAnalyzing ? 'Analyzing...' : 'Run Analysis'}
              </button>
            </div>
          </div>

          {/* Results column */}
          <div className="stagger">
            {sentimentResult && (
              <div className="card animate-slide" style={{ marginBottom: '16px' }}>
                <div className="card-header">
                  <div className="card-title"><Brain size={16} className="icon" /> Sentiment Prediction</div>
                  <span className={`sentiment-badge ${sentimentResult.label}`}>{sentimentResult.label}</span>
                </div>
                <div className="card-body">
                   <div style={{ display: 'flex', gap: '16px', fontSize: '12px' }}>
                      <div style={{ flex: 1 }}>Pos: {(sentimentResult.positive * 100).toFixed(1)}%</div>
                      <div style={{ flex: 1 }}>Neu: {(sentimentResult.neutral * 100).toFixed(1)}%</div>
                      <div style={{ flex: 1 }}>Neg: {(sentimentResult.negative * 100).toFixed(1)}%</div>
                   </div>
                   <div style={{ marginTop: '8px', fontSize: '11px', color: 'var(--text-muted)' }}>
                     Compound Score: {sentimentResult.compound > 0 ? '+' : ''}{sentimentResult.compound.toFixed(3)}
                   </div>
                </div>
              </div>
            )}

            {fakeNewsResult && (
              <div className="card animate-slide">
                <div className="card-header">
                  <div className="card-title"><AlertTriangle size={16} className="icon" style={{ color: fakeNewsResult.is_fake ? 'var(--accent-red)' : '' }} /> Fake News Verification</div>
                  <span className={`threat-badge ${fakeNewsResult.is_fake ? 'critical' : 'none'}`}>
                     {fakeNewsResult.is_fake ? 'FLAGGED FAKE' : 'AUTHENTIC'}
                  </span>
                </div>
                <div className="card-body">
                   <div style={{ marginBottom: '10px' }}>
                      <div className="score-label">
                        <span>Credibility Score</span>
                        <span>{(fakeNewsResult.credibility_score * 100).toFixed(0)}%</span>
                      </div>
                      <div className="score-bar-bg">
                        <div className={`score-bar-fill ${fakeNewsResult.credibility_score > 0.7 ? 'green' : fakeNewsResult.credibility_score > 0.4 ? 'amber' : 'red'}`} 
                          style={{ width: `${fakeNewsResult.credibility_score * 100}%` }} />
                      </div>
                   </div>

                   <div style={{ fontSize: '13px', color: 'var(--text-secondary)', marginBottom: '10px' }}>
                     {fakeNewsResult.reasoning}
                   </div>

                   {fakeNewsResult.signals?.length > 0 && (
                     <div style={{ display: 'flex', gap: '6px', flexWrap: 'wrap' }}>
                        {fakeNewsResult.signals.map((s, i) => (
                           <div key={i} style={{ fontSize: '10px', background: 'var(--bg-main)', border: '1px solid var(--border-subtle)', borderRadius: '4px', padding: '2px 6px', color: 'var(--text-muted)' }}>
                             {s.signal} ({(s.score * 100).toFixed(0)}%)
                           </div>
                        ))}
                     </div>
                   )}
                </div>
              </div>
            )}

            {!sentimentResult && !fakeNewsResult && !textAnalyzing && (
              <div className="empty-state">Submit text to view analysis results.</div>
            )}
          </div>
        </div>
      )}

      {tab === 'profile' && (
        <div className="grid-2">
         {/* Input column */}
         <div className="card">
            <div className="card-header">
              <div className="card-title">Profile Parameters</div>
            </div>
            <div className="card-body">
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px', marginBottom: '12px' }}>
                <div>
                  <label style={{ display: 'block', fontSize: '11px', color: 'var(--text-muted)', marginBottom: '4px' }}>Username</label>
                  <input type="text" value={profileInput.username} onChange={e => setProfileInput({...profileInput, username: e.target.value})} 
                    style={{ width: '100%', padding: '8px', background: 'var(--bg-card)', border: '1px solid var(--border-subtle)', borderRadius: '4px', color: 'white' }} placeholder="@johndoe" />
                </div>
                <div>
                  <label style={{ display: 'block', fontSize: '11px', color: 'var(--text-muted)', marginBottom: '4px' }}>Platform</label>
                  <select value={profileInput.platform} onChange={e => setProfileInput({...profileInput, platform: e.target.value})}
                    style={{ width: '100%', padding: '8px', background: 'var(--bg-card)', border: '1px solid var(--border-subtle)', borderRadius: '4px', color: 'white' }}>
                    <option value="twitter">Twitter</option>
                    <option value="facebook">Facebook</option>
                    <option value="instagram">Instagram</option>
                    <option value="reddit">Reddit</option>
                  </select>
                </div>
              </div>

              <div style={{ marginBottom: '12px' }}>
                 <label style={{ display: 'block', fontSize: '11px', color: 'var(--text-muted)', marginBottom: '4px' }}>Bio</label>
                 <textarea value={profileInput.bio} onChange={e => setProfileInput({...profileInput, bio: e.target.value})}
                    style={{ width: '100%', height: '60px', padding: '8px', background: 'var(--bg-card)', border: '1px solid var(--border-subtle)', borderRadius: '4px', color: 'white', resize: 'none' }} placeholder="Profile bio..." />
              </div>

              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '12px', marginBottom: '16px' }}>
                <div>
                  <label style={{ display: 'block', fontSize: '11px', color: 'var(--text-muted)', marginBottom: '4px' }}>Followers</label>
                  <input type="number" min="0" value={profileInput.followers_count} onChange={e => setProfileInput({...profileInput, followers_count: parseInt(e.target.value) || 0})} style={{ width: '100%', padding: '8px', background: 'var(--bg-card)', border: '1px solid var(--border-subtle)', borderRadius: '4px', color: 'white' }} />
                </div>
                <div>
                  <label style={{ display: 'block', fontSize: '11px', color: 'var(--text-muted)', marginBottom: '4px' }}>Following</label>
                  <input type="number" min="0" value={profileInput.following_count} onChange={e => setProfileInput({...profileInput, following_count: parseInt(e.target.value) || 0})} style={{ width: '100%', padding: '8px', background: 'var(--bg-card)', border: '1px solid var(--border-subtle)', borderRadius: '4px', color: 'white' }} />
                </div>
                <div>
                  <label style={{ display: 'block', fontSize: '11px', color: 'var(--text-muted)', marginBottom: '4px' }}>Total Posts</label>
                  <input type="number" min="0" value={profileInput.posts_count} onChange={e => setProfileInput({...profileInput, posts_count: parseInt(e.target.value) || 0})} style={{ width: '100%', padding: '8px', background: 'var(--bg-card)', border: '1px solid var(--border-subtle)', borderRadius: '4px', color: 'white' }} />
                </div>
              </div>

              <button onClick={handleProfileAnalysis} className="tab-btn active" style={{ width: '100%', display: 'flex', justifyContent: 'center', gap: '8px', padding: '10px' }} disabled={profileAnalyzing || !profileInput.username.trim()}>
                {profileAnalyzing ? <div className="spinner" style={{ width: '16px', height: '16px', borderTopColor: 'transparent', borderWidth: '2px' }} /> : <Bot size={16} />} 
                {profileAnalyzing ? 'Scanning Profile...' : 'Scan Profile'}
              </button>
            </div>
         </div>

         {/* Results */}
         <div>
           {botResult ? (
              <div className="card animate-slide">
                <div className="card-header">
                  <div className="card-title"><Bot size={16} className="icon" /> Bot Classification Result</div>
                  <span className={`threat-badge ${botResult.is_bot ? 'critical' : 'none'}`}>
                     {botResult.is_bot ? 'AUTOMATED BOT' : 'HUMAN USER'}
                  </span>
                </div>
                <div className="card-body">
                   <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
                     <span className="username">@{botResult.username}</span>
                     <div>
                       <span style={{ fontSize: '11px', color: 'var(--text-muted)', marginRight: '6px' }}>Bot Probability:</span>
                       <span style={{ fontSize: '18px', fontWeight: 'bold', color: botResult.is_bot ? 'var(--accent-red)' : 'var(--accent-green)' }}>{(botResult.bot_score * 100).toFixed(1)}%</span>
                     </div>
                   </div>

                   <hr style={{ border: 'none', borderTop: '1px solid var(--border-subtle)', margin: '12px 0' }} />

                   <div style={{ fontSize: '12px', color: 'var(--text-muted)', marginBottom: '8px' }}>Individual Signal Analysis:</div>
                   <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '10px', marginBottom: '16px' }}>
                     {Object.entries(botResult.signals || {}).map(([key, val]) => (
                        <div key={key}>
                           <div style={{ fontSize: '10px', display: 'flex', justifyContent: 'space-between', textTransform: 'capitalize' }}>
                             <span>{key.replace('_', ' ')}</span>
                             <span style={{ color: val > 0.6 ? 'var(--accent-red)' : 'var(--text-muted)' }}>{(val * 100).toFixed(0)}%</span>
                           </div>
                           <div className="score-bar-bg" style={{ height: '4px', marginTop: '3px' }}>
                              <div className={`score-bar-fill ${val > 0.6 ? 'red' : val > 0.3 ? 'amber' : 'green'}`} style={{ width: `${val * 100}%` }} />
                           </div>
                        </div>
                     ))}
                   </div>

                   {botResult.behavioral_flags?.length > 0 ? (
                     <div style={{ display: 'flex', gap: '6px', flexWrap: 'wrap' }}>
                        {botResult.behavioral_flags.map((flag, i) => (
                           <span key={i} style={{ fontSize: '10px', background: 'rgba(239,68,68,0.1)', color: 'var(--accent-red)', border: '1px solid rgba(239,68,68,0.2)', padding: '2px 6px', borderRadius: '4px' }}>
                             {flag.replace(/_/g, ' ')}
                           </span>
                        ))}
                     </div>
                   ) : (
                     <div style={{ fontSize: '11px', color: 'var(--accent-green)', display: 'flex', alignItems: 'center', gap: '4px' }}><CheckCircle size={12} /> No suspicious behavior flags detected.</div>
                   )}
                </div>
              </div>
           ) : (
              !profileAnalyzing && <div className="empty-state">Enter profile parameters and scan to determine bot probability.</div>
           )}
         </div>
        </div>
      )}
    </div>
  );
}
