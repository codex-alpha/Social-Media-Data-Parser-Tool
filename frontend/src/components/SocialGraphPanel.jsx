import { useEffect, useRef, useState } from 'react';
import { useApi } from '../hooks/useApi';
import { api } from '../api/client';
import * as d3 from 'd3';
import { Network } from 'lucide-react';

export function SocialGraphPanel() {
  const { data, loading } = useApi(api.getSocialGraph);
  const svgRef = useRef(null);
  const containerRef = useRef(null);
  const [tooltip, setTooltip] = useState(null);

  useEffect(() => {
    if (!data || !svgRef.current || !containerRef.current) return;

    const container = containerRef.current;
    const width = container.offsetWidth;
    const height = 520;
    const svg = d3.select(svgRef.current);
    svg.selectAll('*').remove();

    svg.attr('viewBox', `0 0 ${width} ${height}`);

    // Platform colors
    const platformColor = {
      twitter: '#DD9E59',
      instagram: '#A47251',
      facebook: '#DD9E59',
      reddit: '#A47251',
      unknown: '#64748b',
    };

    // Deep-copy data to not mutate
    const nodes = data.nodes.map(n => ({ ...n }));
    const links = data.links.map(l => ({
      source: typeof l.source === 'object' ? l.source.id : l.source,
      target: typeof l.target === 'object' ? l.target.id : l.target,
      type: l.type,
      weight: l.weight,
    }));

    // Filter valid links
    const nodeIds = new Set(nodes.map(n => n.id));
    const validLinks = links.filter(l => nodeIds.has(l.source) && nodeIds.has(l.target));

    const g = svg.append('g');

    // Zoom
    const zoom = d3.zoom()
      .scaleExtent([0.3, 4])
      .on('zoom', (event) => g.attr('transform', event.transform));
    svg.call(zoom);

    // Simulation
    const simulation = d3.forceSimulation(nodes)
      .force('link', d3.forceLink(validLinks).id(d => d.id).distance(100).strength(0.3))
      .force('charge', d3.forceManyBody().strength(-200))
      .force('center', d3.forceCenter(width / 2, height / 2))
      .force('collision', d3.forceCollide().radius(25));

    // Glow filter
    const defs = svg.append('defs');
    const filter = defs.append('filter').attr('id', 'glow');
    filter.append('feGaussianBlur').attr('stdDeviation', '3').attr('result', 'coloredBlur');
    const feMerge = filter.append('feMerge');
    feMerge.append('feMergeNode').attr('in', 'coloredBlur');
    feMerge.append('feMergeNode').attr('in', 'SourceGraphic');

    // Links
    const link = g.append('g')
      .selectAll('line')
      .data(validLinks)
      .join('line')
      .attr('stroke', d => d.type === 'correlation' ? '#A47251' : 'rgba(255,255,255,0.1)')
      .attr('stroke-width', d => d.type === 'correlation' ? Math.max(1, d.weight * 3) : 1)
      .attr('stroke-dasharray', d => d.type === 'correlation' ? '6,3' : 'none')
      .attr('opacity', 0.6);

    // Nodes
    const node = g.append('g')
      .selectAll('g')
      .data(nodes)
      .join('g')
      .call(d3.drag()
        .on('start', (event, d) => {
          if (!event.active) simulation.alphaTarget(0.3).restart();
          d.fx = d.x; d.fy = d.y;
        })
        .on('drag', (event, d) => { d.fx = event.x; d.fy = event.y; })
        .on('end', (event, d) => {
          if (!event.active) simulation.alphaTarget(0);
          d.fx = null; d.fy = null;
        }));

    // Node circles
    node.append('circle')
      .attr('r', d => d.is_bot ? 12 : (d.verified ? 10 : 8))
      .attr('fill', d => platformColor[d.platform] || platformColor.unknown)
      .attr('stroke', d => d.is_bot ? '#A47251' : 'rgba(255,255,255,0.2)')
      .attr('stroke-width', d => d.is_bot ? 3 : 1.5)
      .attr('filter', d => d.is_bot ? 'url(#glow)' : 'none')
      .style('cursor', 'pointer')
      .on('mouseover', (event, d) => {
        const rect = container.getBoundingClientRect();
        setTooltip({
          x: event.clientX - rect.left + 15,
          y: event.clientY - rect.top - 10,
          data: d,
        });
        d3.select(event.target).transition().duration(200).attr('r', d.is_bot ? 16 : 12);
      })
      .on('mouseout', (event, d) => {
        setTooltip(null);
        d3.select(event.target).transition().duration(200).attr('r', d.is_bot ? 12 : (d.verified ? 10 : 8));
      });

    // Node labels
    node.append('text')
      .text(d => `@${d.label}`)
      .attr('class', 'graph-node-label')
      .attr('dx', 14)
      .attr('dy', 4);

    // Bot indicator
    node.filter(d => d.is_bot).append('text')
      .text('🤖')
      .attr('dx', -6)
      .attr('dy', 5)
      .style('font-size', '12px')
      .style('pointer-events', 'none');

    simulation.on('tick', () => {
      link
        .attr('x1', d => d.source.x)
        .attr('y1', d => d.source.y)
        .attr('x2', d => d.target.x)
        .attr('y2', d => d.target.y);
      node.attr('transform', d => `translate(${d.x},${d.y})`);
    });

    return () => simulation.stop();
  }, [data]);

  if (loading) return <div className="loading-container"><div className="spinner" /><div className="loading-text">Building social graph...</div></div>;

  return (
    <div className="animate-in">
      <div className="page-header">
        <h1 className="page-title">Social Graph Analysis</h1>
        <p className="page-subtitle">Interactive D3.js force-directed graph showing user relationships, mentions, and correlations</p>
      </div>

      <div className="card">
        <div className="card-header">
          <div className="card-title"><Network size={16} className="icon" /> Network Visualization</div>
          <div style={{ display: 'flex', gap: '12px', fontSize: '11px', color: 'var(--text-muted)' }}>
            <span>🔵 Twitter</span>
            <span style={{ color: '#A47251' }}>● Instagram</span>
            <span style={{ color: '#DD9E59' }}>● Facebook</span>
            <span style={{ color: '#A47251' }}>● Reddit</span>
            <span>🤖 Bot</span>
            <span style={{ color: '#A47251' }}>- - Correlation</span>
          </div>
        </div>
        <div className="card-body" style={{ padding: 0, position: 'relative' }} ref={containerRef}>
          <div className="graph-container">
            <svg ref={svgRef} />
          </div>
          {tooltip && (
            <div className="graph-tooltip" style={{ left: tooltip.x, top: tooltip.y }}>
              <div style={{ fontWeight: 600, marginBottom: '4px' }}>@{tooltip.data.label}</div>
              <div style={{ fontSize: '11px', color: 'var(--text-muted)' }}>
                <div>Platform: {tooltip.data.platform}</div>
                <div>Followers: {tooltip.data.followers?.toLocaleString()}</div>
                {tooltip.data.is_bot && <div style={{ color: 'var(--accent-red)', fontWeight: 600 }}>⚠ Bot Score: {(tooltip.data.bot_score * 100).toFixed(0)}%</div>}
                {tooltip.data.verified && <div style={{ color: 'var(--accent-blue)' }}>✓ Verified</div>}
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Graph Stats */}
      {data && (
        <div className="stats-grid stagger" style={{ marginTop: '20px', gridTemplateColumns: 'repeat(4, 1fr)' }}>
          <div className="stat-card blue">
            <div className="stat-value">{data.nodes?.length || 0}</div>
            <div className="stat-label">Nodes</div>
          </div>
          <div className="stat-card purple">
            <div className="stat-value">{data.links?.length || 0}</div>
            <div className="stat-label">Connections</div>
          </div>
          <div className="stat-card red">
            <div className="stat-value">{data.nodes?.filter(n => n.is_bot).length || 0}</div>
            <div className="stat-label">Bots in Network</div>
          </div>
          <div className="stat-card green">
            <div className="stat-value">{data.links?.filter(l => l.type === 'correlation').length || 0}</div>
            <div className="stat-label">Correlation Links</div>
          </div>
        </div>
      )}
    </div>
  );
}
