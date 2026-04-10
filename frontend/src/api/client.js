const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

async function fetchApi(endpoint) {
  try {
    const res = await fetch(`${API_BASE}${endpoint}`);
    if (!res.ok) throw new Error(`API Error: ${res.status}`);
    return await res.json();
  } catch (err) {
    console.error(`Failed to fetch ${endpoint}:`, err);
    throw err;
  }
}

export const api = {
  getDashboardOverview: () => fetchApi('/dashboard/overview'),
  getSentiments: () => fetchApi('/dashboard/sentiments'),
  getTopics: () => fetchApi('/dashboard/topics'),
  getFakeNews: () => fetchApi('/dashboard/fake-news'),
  getBots: () => fetchApi('/dashboard/bots'),
  getPosts: () => fetchApi('/dashboard/posts'),
  getProfiles: () => fetchApi('/dashboard/profiles'),
  getTimeline: () => fetchApi('/dashboard/timeline'),
  getCorrelations: () => fetchApi('/dashboard/correlations'),
  getEvidence: () => fetchApi('/dashboard/evidence'),
  getSocialGraph: () => fetchApi('/dashboard/social-graph'),

  // Manual Analysis Endpoints
  analyzeSentiment: async (text) => {
    const res = await fetch(`${API_BASE}/analytics/sentiment`, {
      method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ text, id: 'manual' })
    });
    return res.json();
  },
  detectFakeNews: async (text) => {
    const res = await fetch(`${API_BASE}/analytics/fake-news`, {
      method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ text, post_id: 'manual', urls: [] })
    });
    return res.json();
  },
  detectBot: async (profileRaw) => {
    const res = await fetch(`${API_BASE}/analytics/bot-detection`, {
      method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(profileRaw)
    });
    return res.json();
  }
};
