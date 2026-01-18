import React, { useState, useEffect, useRef } from 'react';
import { COLORS, WORKFLOW_NODES, WORKFLOW_EDGES, TOOLTIP_CONTENT } from '../constants/constants';

// Workflow Diagram Component
export const WorkflowDiagram = () => {
  const [hoveredNode, setHoveredNode] = useState(null);
  const [selectedNode, setSelectedNode] = useState(null);
  const [isAnimating, setIsAnimating] = useState(false);
  const svgRef = useRef(null);

  useEffect(() => {
    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting && !isAnimating) {
          setIsAnimating(true);
        }
      },
      { threshold: 0.3 }
    );

    if (svgRef.current) {
      observer.observe(svgRef.current);
    }

    return () => observer.disconnect();
  }, [isAnimating]);

  // Close modal on ESC key
  useEffect(() => {
    const handleEscape = (e) => {
      if (e.key === 'Escape') {
        setSelectedNode(null);
      }
    };
    window.addEventListener('keydown', handleEscape);
    return () => window.removeEventListener('keydown', handleEscape);
  }, []);

  // Calculate hexagon points
  const getHexagonPoints = (cx, cy, size = 40) => {
    const points = [];
    for (let i = 0; i < 6; i++) {
      const angle = (Math.PI / 3) * i - Math.PI / 2;
      points.push([
        cx + size * Math.cos(angle),
        cy + size * Math.sin(angle)
      ]);
    }
    return points.map(p => p.join(',')).join(' ');
  };

  // Calculate connection points on hexagon edge
  const getHexAnchor = (fromNode, toNode) => {
    const dx = toNode.x - fromNode.x;
    const dy = toNode.y - fromNode.y;
    const angle = Math.atan2(dy, dx);
    const distance = 40;
    
    return {
      x1: fromNode.x + Math.cos(angle) * distance,
      y1: fromNode.y + Math.sin(angle) * distance,
      x2: toNode.x - Math.cos(angle) * distance,
      y2: toNode.y - Math.sin(angle) * distance
    };
  };

  const connectedEdges = hoveredNode 
    ? WORKFLOW_EDGES.filter(e => e.from === hoveredNode || e.to === hoveredNode)
    : [];

  return (
    <section style={{
      padding: '80px 32px',
      backgroundColor: COLORS.canvas,
      position: 'relative'
    }} id="how-it-works">
      <div style={{
        maxWidth: '1280px',
        margin: '0 auto'
      }}>
        <div style={{ textAlign: 'center', marginBottom: '48px' }}>
          <div style={{
            fontSize: '13px',
            textTransform: 'uppercase',
            letterSpacing: '0.1em',
            color: COLORS.muted,
            fontFamily: 'IBM Plex Sans, sans-serif',
            marginBottom: '16px'
          }}>
            HOW IT WORKS
          </div>
          <h2 style={{
            fontFamily: 'Space Grotesk, sans-serif',
            fontSize: 'clamp(32px, 5vw, 40px)',
            lineHeight: '1.2',
            fontWeight: 700,
            color: COLORS.ink,
            margin: 0
          }}>
            Automatic Verification Pipeline
          </h2>
        </div>

        <div ref={svgRef} style={{ position: 'relative', padding: '40px 0' }}>
          <svg 
            viewBox="0 0 1000 850" 
            style={{ 
              width: '100%', 
              height: 'auto',
              maxWidth: '1000px',
              margin: '0 auto',
              display: 'block',
              overflow: 'visible'
            }}
          >
            {/* Edges */}
            <g>
              {WORKFLOW_EDGES.map((edge, idx) => {
                const fromNode = WORKFLOW_NODES.find(n => n.id === edge.from);
                const toNode = WORKFLOW_NODES.find(n => n.id === edge.to);
                const { x1, y1, x2, y2 } = getHexAnchor(fromNode, toNode);
                const pathLength = Math.sqrt(Math.pow(x2 - x1, 2) + Math.pow(y2 - y1, 2));
                const isHighlighted = connectedEdges.some(e => e.from === edge.from && e.to === edge.to);

                return (
                  <g key={`edge-${idx}`}>
                    <line
                      x1={x1}
                      y1={y1}
                      x2={x2}
                      y2={y2}
                      stroke={COLORS.muted}
                      strokeWidth={isHighlighted ? 3 : 2}
                      strokeDasharray={pathLength}
                      strokeDashoffset={isAnimating ? 0 : pathLength}
                      style={{
                        transition: 'stroke-width 0.2s ease, stroke-dashoffset 0.8s ease',
                        transitionDelay: isAnimating ? '0s' : '0s',
                        opacity: isHighlighted || !hoveredNode ? 1 : 0.3
                      }}
                    />
                    {/* Particle */}
                    {isAnimating && (
                      <circle r="6" fill={COLORS.accentActive}>
                        <animateMotion
                          dur={isHighlighted ? "1.0s" : "2.0s"}
                          repeatCount="indefinite"
                          begin={`${0.8 + idx * 0.1}s`}
                        >
                          <mpath href={`#path-${idx}`} />
                        </animateMotion>
                      </circle>
                    )}
                    <path
                      id={`path-${idx}`}
                      d={`M ${x1} ${y1} L ${x2} ${y2}`}
                      fill="none"
                      stroke="none"
                    />
                  </g>
                );
              })}
            </g>

            {/* Nodes */}
            <g>
              {WORKFLOW_NODES.map((node, idx) => {
                const Icon = node.icon;
                const isHovered = hoveredNode === node.id;
                const scale = isHovered ? 1.05 : 1;
                
                return (
                  <g 
                    key={node.id}
                    style={{
                      cursor: 'pointer',
                      transform: `scale(${scale})`,
                      transformOrigin: `${node.x}px ${node.y}px`,
                      transition: 'transform 0.2s ease',
                      opacity: isAnimating ? 1 : 0,
                      animation: isAnimating ? `fadeIn 0.4s ease-out ${0.3 + idx * 0.1}s forwards` : 'none'
                    }}
                    onMouseEnter={() => setHoveredNode(node.id)}
                    onMouseLeave={() => setHoveredNode(null)}
                    onClick={() => setSelectedNode(node.id)}
                  >
                    <polygon
                      points={getHexagonPoints(node.x, node.y)}
                      fill={COLORS.canvas}
                      stroke={COLORS.ink}
                      strokeWidth="2"
                    />
                    <Icon 
                      x={node.x - 12}
                      y={node.y - 12}
                      size={24}
                      color={COLORS.ink}
                    />
                    {/* Number Badge */}
                    <circle
                      cx={node.x + 30}
                      cy={node.y - 30}
                      r="12"
                      fill={COLORS.accentAlert}
                    />
                    <text
                      x={node.x + 30}
                      y={node.y - 30}
                      textAnchor="middle"
                      dominantBaseline="central"
                      fill={COLORS.canvas}
                      fontSize="12"
                      fontWeight="600"
                      fontFamily="IBM Plex Sans, sans-serif"
                    >
                      {node.number}
                    </text>
                    {/* Label */}
                    <text
                      x={node.x}
                      y={node.y + 60}
                      textAnchor="middle"
                      fill={COLORS.ink}
                      fontSize="14"
                      fontWeight="500"
                      fontFamily="IBM Plex Sans, sans-serif"
                    >
                      {node.label}
                    </text>

                    {/* Tooltip - Better positioning */}
                    {isHovered && TOOLTIP_CONTENT[node.id] && (
                      <g>
                        {/* Tooltip pointer/arrow */}
                        <path
                          d={`M ${node.x} ${node.y - 50} L ${node.x - 8} ${node.y - 60} L ${node.x + 8} ${node.y - 60} Z`}
                          fill={COLORS.canvas}
                          stroke={COLORS.ink}
                          strokeWidth="1"
                        />
                        {/* Tooltip box */}
                        <rect
                          x={node.x - 150}
                          y={node.y - 190}
                          width="300"
                          height="130"
                          fill={COLORS.canvas}
                          stroke={COLORS.ink}
                          strokeWidth="2"
                          rx="8"
                          filter="drop-shadow(0 4px 12px rgba(0, 0, 0, 0.15))"
                        />
                        {/* Title */}
                        <text
                          x={node.x - 135}
                          y={node.y - 160}
                          fill={COLORS.ink}
                          fontSize="16"
                          fontWeight="700"
                          fontFamily="IBM Plex Sans, sans-serif"
                        >
                          {TOOLTIP_CONTENT[node.id].title}
                        </text>
                        {/* Description */}
                        <foreignObject
                          x={node.x - 135}
                          y={node.y - 140}
                          width="270"
                          height="110"
                        >
                          <div style={{
                            fontSize: '13px',
                            lineHeight: '1.5',
                            fontFamily: 'IBM Plex Sans, sans-serif',
                            color: COLORS.ink
                          }}>
                            <p style={{ margin: '0 0 12px 0' }}>
                              {TOOLTIP_CONTENT[node.id].description}
                            </p>
                            <p style={{ 
                              margin: 0, 
                              fontFamily: 'JetBrains Mono, monospace',
                              fontSize: '11px',
                              color: COLORS.muted,
                              padding: '8px',
                              backgroundColor: COLORS.panelLight,
                              borderRadius: '4px',
                              wordBreak: 'break-all'
                            }}>
                              {TOOLTIP_CONTENT[node.id].technical}
                            </p>
                          </div>
                        </foreignObject>
                      </g>
                    )}
                  </g>
                );
              })}
            </g>
          </svg>
        </div>
      </div>

      {/* Modal */}
      {selectedNode && TOOLTIP_CONTENT[selectedNode] && (
        <div 
          style={{
            position: 'fixed',
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            backgroundColor: 'rgba(0, 0, 0, 0.6)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            zIndex: 2000,
            padding: '32px',
            animation: 'fadeIn 0.2s ease-out'
          }}
          onClick={() => setSelectedNode(null)}
        >
          <div 
            style={{
              backgroundColor: COLORS.canvas,
              borderRadius: '16px',
              padding: '48px',
              maxWidth: '600px',
              width: '100%',
              position: 'relative',
              border: `2px solid ${COLORS.ink}`,
              animation: 'scaleIn 0.3s ease-out'
            }}
            onClick={(e) => e.stopPropagation()}
          >
            <button
              onClick={() => setSelectedNode(null)}
              style={{
                position: 'absolute',
                top: '16px',
                right: '16px',
                background: 'none',
                border: 'none',
                fontSize: '24px',
                cursor: 'pointer',
                color: COLORS.muted,
                padding: '8px',
                lineHeight: 1
              }}
              aria-label="Close"
            >
              ×
            </button>
            
            <h3 style={{
              fontFamily: 'Space Grotesk, sans-serif',
              fontSize: '32px',
              fontWeight: 700,
              color: COLORS.ink,
              margin: '0 0 24px 0'
            }}>
              {TOOLTIP_CONTENT[selectedNode].title}
            </h3>
            
            <p style={{
              fontFamily: 'IBM Plex Sans, sans-serif',
              fontSize: '16px',
              lineHeight: '1.6',
              color: COLORS.ink,
              margin: '0 0 24px 0'
            }}>
              {TOOLTIP_CONTENT[selectedNode].description}
            </p>
            
            <div style={{
              backgroundColor: COLORS.panelLight,
              padding: '16px',
              borderRadius: '8px',
              fontFamily: 'JetBrains Mono, monospace',
              fontSize: '13px',
              color: COLORS.muted,
              lineHeight: '1.6',
              wordBreak: 'break-all'
            }}>
              {TOOLTIP_CONTENT[selectedNode].technical}
            </div>
          </div>
        </div>
      )}

      <style>{`
        @keyframes fadeIn {
          from {
            opacity: 0;
            transform: translateY(12px);
          }
          to {
            opacity: 1;
            transform: translateY(0);
          }
        }

        @keyframes scaleIn {
          from {
            opacity: 0;
            transform: scale(0.9);
          }
          to {
            opacity: 1;
            transform: scale(1);
          }
        }
      `}</style>
    </section>
  );
};

