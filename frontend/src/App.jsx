import { useState } from 'react';
import './index.css';
import { Sidebar } from './components/Sidebar';
import { DashboardOverview } from './components/DashboardOverview';
import { SentimentPanel } from './components/SentimentPanel';
import { ThreatPanel } from './components/ThreatPanel';
import { ForensicsPanel } from './components/ForensicsPanel';
import { SocialGraphPanel } from './components/SocialGraphPanel';
import { TimelinePanel } from './components/TimelinePanel';
import { ManualAnalysisPanel } from './components/ManualAnalysisPanel';

const PAGES = {
  overview: { label: 'Dashboard', component: DashboardOverview },
  manual: { label: 'Manual Analysis', component: ManualAnalysisPanel },
  sentiment: { label: 'Sentiment Analysis', component: SentimentPanel },
  threats: { label: 'Threat Detection', component: ThreatPanel },
  forensics: { label: 'Digital Forensics', component: ForensicsPanel },
  graph: { label: 'Social Graph', component: SocialGraphPanel },
  timeline: { label: 'Event Timeline', component: TimelinePanel },
};

export default function App() {
  const [activePage, setActivePage] = useState('overview');
  const ActiveComponent = PAGES[activePage]?.component || DashboardOverview;

  return (
    <div className="app-layout">
      <Sidebar activePage={activePage} onNavigate={setActivePage} />
      <main className="main-content">
        <ActiveComponent />
      </main>
    </div>
  );
}
