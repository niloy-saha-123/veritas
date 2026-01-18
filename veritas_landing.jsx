import React, { useState, useEffect, useRef } from 'react';
import { 
  Shield, Zap, FileCode, FileText, Minimize, Brain, 
  Gauge, MessageSquare, Code, GitPullRequest, TrendingUp, 
  Eye, Menu, X, Github
} from 'lucide-react';

// Design System Constants
const COLORS = {
  canvas: '#F2F2F0',
  ink: '#0E0F12',
  muted: '#5B5F6A',
  border: '#D5D7DD',
  panelLight: '#E6E7EB',
  panelMid: '#C9CCD3',
  accentAlert: '#FF6B35',
  accentActive: '#00D9FF',
  accentWarm: '#FFE66D'
};

// Workflow Diagram Data
const WORKFLOW_NODES = [
  { id: 'webhook', x: 500, y: 100, label: 'GitHub Webhook', icon: Zap, number: 1 },
  { id: 'code', x: 300, y: 250, label: 'Fetch Code', icon: FileCode, number: 2 },
  { id: 'docs', x: 700, y: 250, label: 'Fetch Docs', icon: FileText, number: 3 },
  { id: 'compress', x: 500, y: 400, label: 'Bear-1 Compress', icon: Minimize, number: 4 },
  { id: 'analyze', x: 500, y: 550, label: 'Claude Analysis', icon: Brain, number: 5 },
  { id: 'score', x: 300, y: 700, label: 'Trust Score', icon: Gauge, number: 6 },
  { id: 'comment', x: 700, y: 700, label: 'PR Comment', icon: MessageSquare, number: 7 }
];

const WORKFLOW_EDGES = [
  { from: 'webhook', to: 'code' },
  { from: 'webhook', to: 'docs' },
  { from: 'code', to: 'compress' },
  { from: 'docs', to: 'compress' },
  { from: 'compress', to: 'analyze' },
  { from: 'analyze', to: 'score' },
  { from: 'analyze', to: 'comment' }
];

const TOOLTIP_CONTENT = {
  webhook: {
    title: 'GitHub Webhook',
    description: 'Triggered automatically when a pull request is created or updated.',
    technical: 'POST /webhook endpoint with PR payload'
  },
  code: {
    title: 'Fetch Code',
    description: 'Retrieves all changed files from the pull request diff.',
    technical: 'GitHub API v3 - GET /repos/:owner/:repo/pulls/:number/files'
  },
  docs: {
    title: 'Fetch Documentation',
    description: 'Locates and retrieves all related documentation files.',
    technical: 'Pattern matching: README.md, docs/**, *.md in repo root'
  },
  compress: {
    title: 'Bear-1 Compression',
    description: 'Reduces token count by 60% while preserving semantic meaning.',
    technical: 'Anthropic Bear-1 model - context compression'
  },
  analyze: {
    title: 'Claude Analysis',
    description: 'Compares compressed code against documentation for mismatches.',
    technical: 'Claude Sonnet 4.5 with custom verification prompt'
  },
  score: {
    title: 'Trust Score',
    description: 'Calculates documentation accuracy score from 0-100%.',
    technical: 'Weighted scoring: accuracy 50%, completeness 30%, clarity 20%'
  },
  comment: {
    title: 'PR Comment',
    description: 'Posts detailed findings as a GitHub comment with suggestions.',
    technical: 'GitHub API - POST /repos/:owner/:repo/issues/:number/comments'
  }
};

// Header Component
const Header = () => {
  const [isScrolled, setIsScrolled] = useState(false);
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);

  useEffect(() => {
    const handleScroll = () => {
      setIsScrolled(window.scrollY > 0);
    };
    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  return (
    <header 
      style={{
        position: 'sticky',
        top: 0,
        height: '72px',
        backgroundColor: COLORS.canvas,
        borderBottom: `1px solid ${isScrolled ? COLORS.border : 'transparent'}`,
        transition: 'border-color 0.2s ease',
        zIndex: 1000,
        padding: '0'
      }}
    >
      <div style={{
        maxWidth: '1400px',
        margin: '0 auto',
        padding: '0 32px',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        height: '100%'
      }}>
        {/* Logo */}
        <div style={{ display: 'flex', alignItems: 'center' }}>
          <span style={{ 
            fontFamily: 'Space Grotesk, sans-serif', 
            fontSize: '24px', 
            fontWeight: 700,
            color: COLORS.ink 
          }}>
            Veritas
          </span>
        </div>

        {/* Desktop Nav */}
        <nav style={{ 
          display: 'flex', 
          gap: '40px',
          fontSize: '15px',
          fontFamily: 'IBM Plex Sans, sans-serif'
        }} className="desktop-nav">
          {['Features', 'How it Works', 'Pricing', 'Docs'].map(item => (
            <a 
              key={item}
              href={`#${item.toLowerCase().replace(/\s/g, '-')}`}
              style={{
                color: COLORS.muted,
                textDecoration: 'none',
                transition: 'color 0.2s ease'
              }}
              onMouseEnter={(e) => {
                e.target.style.color = COLORS.ink;
              }}
              onMouseLeave={(e) => {
                e.target.style.color = COLORS.muted;
              }}
            >
              {item}
            </a>
          ))}
        </nav>

        {/* Desktop Right */}
        <div style={{ display: 'flex', gap: '16px', alignItems: 'center' }} className="desktop-nav">
          <a href="#signin" style={{ 
            color: COLORS.muted, 
            textDecoration: 'none',
            fontSize: '15px',
            fontFamily: 'IBM Plex Sans, sans-serif',
            transition: 'color 0.2s ease'
          }}
          onMouseEnter={(e) => e.target.style.color = COLORS.ink}
          onMouseLeave={(e) => e.target.style.color = COLORS.muted}
          >
            Sign in
          </a>
          <button style={{
            backgroundColor: COLORS.ink,
            color: COLORS.canvas,
            border: 'none',
            borderRadius: '8px',
            padding: '10px 20px',
            fontSize: '15px',
            fontFamily: 'IBM Plex Sans, sans-serif',
            fontWeight: 500,
            cursor: 'pointer',
            transition: 'transform 0.1s ease'
          }}
          onMouseDown={(e) => e.target.style.transform = 'scale(0.98)'}
          onMouseUp={(e) => e.target.style.transform = 'scale(1)'}
          onMouseLeave={(e) => e.target.style.transform = 'scale(1)'}
          >
            Get Started
          </button>
        </div>

        {/* Mobile Menu Button */}
        <button 
          className="mobile-menu-btn"
          onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
          style={{
            display: 'none',
            background: 'none',
            border: 'none',
            cursor: 'pointer',
            padding: '8px'
          }}
        >
          {isMobileMenuOpen ? <X size={24} color={COLORS.ink} /> : <Menu size={24} color={COLORS.ink} />}
        </button>
      </div>

      {/* Mobile Menu */}
      {isMobileMenuOpen && (
        <div className="mobile-menu" style={{
          position: 'absolute',
          top: '72px',
          left: 0,
          right: 0,
          backgroundColor: COLORS.canvas,
          borderBottom: `1px solid ${COLORS.border}`,
          padding: '24px 32px',
          display: 'none',
          flexDirection: 'column',
          gap: '24px'
        }}>
          {['Features', 'How it Works', 'Pricing', 'Docs'].map(item => (
            <a 
              key={item}
              href={`#${item.toLowerCase().replace(/\s/g, '-')}`}
              style={{
                color: COLORS.ink,
                textDecoration: 'none',
                fontSize: '16px',
                fontFamily: 'IBM Plex Sans, sans-serif'
              }}
              onClick={() => setIsMobileMenuOpen(false)}
            >
              {item}
            </a>
          ))}
          <button style={{
            backgroundColor: COLORS.ink,
            color: COLORS.canvas,
            border: 'none',
            borderRadius: '8px',
            padding: '12px 24px',
            fontSize: '16px',
            fontFamily: 'IBM Plex Sans, sans-serif',
            fontWeight: 500,
            cursor: 'pointer',
            marginTop: '8px'
          }}>
            Get Started
          </button>
        </div>
      )}

      <style>{`
        @media (max-width: 1024px) {
          .desktop-nav {
            display: none !important;
          }
          .mobile-menu-btn {
            display: block !important;
          }
          .mobile-menu {
            display: flex !important;
          }
        }
      `}</style>
    </header>
  );
};

// Hero Section
const Hero = () => {
  const [isVisible, setIsVisible] = useState(false);

  useEffect(() => {
    setTimeout(() => setIsVisible(true), 100);
  }, []);

  return (
    <section style={{
      backgroundColor: COLORS.canvas,
      minHeight: '85vh',
      padding: '40px 32px 80px',
      position: 'relative',
      overflow: 'hidden'
    }}>
      <div style={{
        maxWidth: '1400px',
        margin: '0 auto',
        display: 'grid',
        gridTemplateColumns: '1fr 1fr',
        gap: '80px',
        alignItems: 'center',
        position: 'relative'
      }} className="hero-grid">
        {/* Left Column - Headline */}
        <div style={{
          opacity: isVisible ? 1 : 0,
          transform: isVisible ? 'translateY(0)' : 'translateY(12px)',
          transition: 'all 0.4s ease-out',
          position: 'relative',
          zIndex: 1
        }}>
          <h1 style={{
            fontFamily: 'Space Grotesk, sans-serif',
            fontSize: 'clamp(48px, 6vw, 80px)',
            lineHeight: '1.1',
            fontWeight: 800,
            color: COLORS.ink,
            margin: '0 0 32px 0',
            letterSpacing: '-0.02em'
          }}>
            Documentation<br />
            that never<br />
            lies.
          </h1>

          <p style={{
            fontFamily: 'IBM Plex Sans, sans-serif',
            fontSize: '18px',
            lineHeight: '1.6',
            color: COLORS.muted,
            margin: '0 0 40px 0',
            maxWidth: '520px'
          }}>
            AI-powered verification ensures your docs match your code—automatically. No more wasted hours on outdated examples.
          </p>

          {/* CTAs */}
          <div style={{
            display: 'flex',
            gap: '16px',
            flexWrap: 'wrap',
            opacity: isVisible ? 1 : 0,
            transform: isVisible ? 'translateY(0)' : 'translateY(12px)',
            transition: 'all 0.4s ease-out 0.1s',
            marginBottom: '32px'
          }}>
            <button style={{
              backgroundColor: COLORS.ink,
              color: COLORS.canvas,
              border: 'none',
              borderRadius: '8px',
              padding: '16px 32px',
              fontSize: '16px',
              fontFamily: 'IBM Plex Sans, sans-serif',
              fontWeight: 500,
              cursor: 'pointer',
              transition: 'transform 0.1s ease'
            }}
            onMouseDown={(e) => e.target.style.transform = 'scale(0.98)'}
            onMouseUp={(e) => e.target.style.transform = 'scale(1)'}
            onMouseLeave={(e) => e.target.style.transform = 'scale(1)'}
            >
              Install GitHub App
            </button>
          </div>

          <div style={{
            fontFamily: 'IBM Plex Sans, sans-serif',
            fontSize: '14px',
            color: COLORS.muted,
            opacity: isVisible ? 1 : 0,
            transition: 'opacity 0.4s ease-out 0.2s'
          }}>
            Free for open source • 5 min setup
          </div>
        </div>

        {/* Right Column - Code Preview */}
        <div style={{
          opacity: isVisible ? 1 : 0,
          transform: isVisible ? 'translateY(0)' : 'translateY(12px)',
          transition: 'all 0.4s ease-out 0.2s',
          position: 'relative',
          zIndex: 2
        }}>
          <div style={{
            backgroundColor: '#FFFFFF',
            border: `1px solid ${COLORS.border}`,
            borderRadius: '12px',
            overflow: 'hidden',
            boxShadow: '0 4px 24px rgba(0, 0, 0, 0.06)'
          }}>
            {/* Window Header */}
            <div style={{
              backgroundColor: '#F6F8FA',
              padding: '12px 16px',
              display: 'flex',
              alignItems: 'center',
              gap: '8px',
              borderBottom: `1px solid ${COLORS.border}`
            }}>
              <div style={{ display: 'flex', gap: '6px' }}>
                <div style={{ width: '12px', height: '12px', borderRadius: '50%', backgroundColor: '#FC605C' }} />
                <div style={{ width: '12px', height: '12px', borderRadius: '50%', backgroundColor: '#FDBC40' }} />
                <div style={{ width: '12px', height: '12px', borderRadius: '50%', backgroundColor: '#34C749' }} />
              </div>
              <span style={{
                marginLeft: '8px',
                fontFamily: 'JetBrains Mono, monospace',
                fontSize: '13px',
                color: COLORS.muted
              }}>
                auth.py
              </span>
            </div>

            {/* Code Content */}
            <div style={{
              padding: '24px',
              backgroundColor: '#FFFFFF'
            }}>
              <div style={{
                fontFamily: 'JetBrains Mono, monospace',
                fontSize: '15px',
                lineHeight: '1.8',
                color: COLORS.ink
              }}>
                <div style={{ display: 'flex' }}>
                  <span style={{ width: '40px', color: COLORS.muted, textAlign: 'right', marginRight: '24px', userSelect: 'none' }}>1</span>
                  <span><span style={{ color: '#0550AE' }}>def</span> <span style={{ color: '#8250DF' }}>login</span>(email, password, <span style={{ color: '#CF222E' }}>mfa_token</span>):</span>
                </div>
                <div style={{ display: 'flex' }}>
                  <span style={{ width: '40px', color: COLORS.muted, textAlign: 'right', marginRight: '24px', userSelect: 'none' }}>2</span>
                  <span style={{ paddingLeft: '32px', color: '#0A3069' }}>"""Authenticate user with MFA"""</span>
                </div>
                <div style={{ display: 'flex' }}>
                  <span style={{ width: '40px', color: COLORS.muted, textAlign: 'right', marginRight: '24px', userSelect: 'none' }}>3</span>
                  <span style={{ paddingLeft: '32px' }}>user = validate_credentials(email, password)</span>
                </div>
                <div style={{ display: 'flex' }}>
                  <span style={{ width: '40px', color: COLORS.muted, textAlign: 'right', marginRight: '24px', userSelect: 'none' }}>4</span>
                  <span style={{ paddingLeft: '32px' }}><span style={{ color: '#0550AE' }}>return</span> verify_mfa(user, mfa_token)</span>
                </div>
              </div>
            </div>

            {/* Verification Badge */}
            <div style={{
              backgroundColor: '#F6F8FA',
              padding: '16px 24px',
              borderTop: `1px solid ${COLORS.border}`,
              display: 'flex',
              alignItems: 'center',
              gap: '12px'
            }}>
              <div style={{
                width: '24px',
                height: '24px',
                borderRadius: '50%',
                backgroundColor: '#1A7F37',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center'
              }}>
                <svg width="14" height="14" viewBox="0 0 16 16" fill="white">
                  <path d="M13.78 4.22a.75.75 0 0 1 0 1.06l-7.25 7.25a.75.75 0 0 1-1.06 0L2.22 9.28a.751.751 0 0 1 .018-1.042.751.751 0 0 1 1.042-.018L6 10.94l6.72-6.72a.75.75 0 0 1 1.06 0Z" />
                </svg>
              </div>
              <span style={{
                fontFamily: 'IBM Plex Sans, sans-serif',
                fontSize: '14px',
                fontWeight: 600,
                color: '#1A7F37'
              }}>
                Documentation verified
              </span>
            </div>
          </div>
        </div>
      </div>

      <style>{`
        @media (max-width: 1024px) {
          .hero-grid {
            grid-template-columns: 1fr !important;
            gap: 64px !important;
          }
        }
      `}</style>
    </section>
  );
};

// Workflow Diagram Component
const WorkflowDiagram = () => {
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

// Product Introduction Section
const ProductIntro = () => {
  return (
    <section style={{
      padding: '64px 32px',
      backgroundColor: COLORS.canvas
    }}>
      <div style={{
        maxWidth: '1280px',
        margin: '0 auto',
        display: 'grid',
        gridTemplateColumns: '65% 35%',
        gap: '64px',
        alignItems: 'center'
      }} className="product-intro-grid">
        <div>
          <h2 style={{
            fontFamily: 'Space Grotesk, sans-serif',
            fontSize: 'clamp(28px, 4vw, 40px)',
            lineHeight: '1.2',
            fontWeight: 700,
            color: COLORS.ink,
            margin: '0 0 24px 0'
          }}>
            Automatic documentation verification
          </h2>
          <p style={{
            fontFamily: 'IBM Plex Sans, sans-serif',
            fontSize: '16px',
            lineHeight: '1.5',
            color: COLORS.ink,
            margin: 0
          }}>
            Veritas monitors every pull request and compares code changes against your documentation. When mismatches are detected, we automatically create fix PRs with corrected docs. No manual reviews. No context switching. Just accurate documentation that stays in sync with your codebase.
          </p>
        </div>
        <div style={{
          textAlign: 'right'
        }}>
          <div style={{
            fontFamily: 'Space Grotesk, sans-serif',
            fontSize: 'clamp(48px, 7vw, 72px)',
            fontWeight: 700,
            color: COLORS.ink,
            lineHeight: '1',
            marginBottom: '8px'
          }}>
            $85B
          </div>
          <div style={{
            fontFamily: 'IBM Plex Sans, sans-serif',
            fontSize: '13px',
            color: COLORS.muted,
            lineHeight: '1.5'
          }}>
            lost annually to<br />broken documentation
          </div>
        </div>
      </div>

      <style>{`
        @media (max-width: 768px) {
          .product-intro-grid {
            grid-template-columns: 1fr !important;
            gap: 40px !important;
          }
          .product-intro-grid > div:last-child {
            text-align: left !important;
          }
        }
      `}</style>
    </section>
  );
};

// Split Section Component with Animations
const SplitSection = () => {
  const [isVisible, setIsVisible] = useState(false);
  const sectionRef = useRef(null);

  useEffect(() => {
    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          setIsVisible(true);
        }
      },
      { threshold: 0.3 }
    );

    if (sectionRef.current) {
      observer.observe(sectionRef.current);
    }

    return () => observer.disconnect();
  }, []);

  return (
    <section ref={sectionRef} style={{
      display: 'grid',
      gridTemplateColumns: '1fr 1fr',
      minHeight: '500px'
    }} className="split-section" id="features">
      {/* Left Panel */}
      <div style={{
        backgroundColor: COLORS.panelLight,
        padding: '80px 64px',
        opacity: isVisible ? 1 : 0,
        transform: isVisible ? 'translateX(0)' : 'translateX(-50px)',
        transition: 'all 0.8s ease-out'
      }}>
        <div style={{
          fontSize: '12px',
          textTransform: 'uppercase',
          letterSpacing: '0.15em',
          color: COLORS.muted,
          fontFamily: 'IBM Plex Sans, sans-serif',
          marginBottom: '24px'
        }}>
          DETECTION
        </div>
        <h2 style={{
          fontFamily: 'Space Grotesk, sans-serif',
          fontSize: 'clamp(32px, 4vw, 48px)',
          lineHeight: '1.1',
          fontWeight: 700,
          color: COLORS.ink,
          margin: '0 0 48px 0'
        }}>
          Monitors Every<br />Change
        </h2>
        <div style={{
          display: 'flex',
          flexDirection: 'column',
          gap: '32px'
        }}>
          {[
            'Monitors every PR automatically',
            'Analyzes code vs docs in real-time',
            'Detects mismatches instantly'
          ].map((item, idx) => (
            <div 
              key={idx} 
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '16px',
                opacity: isVisible ? 1 : 0,
                transform: isVisible ? 'translateX(0)' : 'translateX(-20px)',
                transition: `all 0.6s ease-out ${0.2 + idx * 0.1}s`
              }}
            >
              <div style={{
                width: '10px',
                height: '10px',
                borderRadius: '50%',
                backgroundColor: COLORS.accentAlert,
                flexShrink: 0,
                animation: isVisible ? `pulse 2s ease-in-out infinite ${idx * 0.3}s` : 'none'
              }} />
              <span style={{
                fontFamily: 'IBM Plex Sans, sans-serif',
                fontSize: '17px',
                lineHeight: '1.6',
                color: COLORS.ink
              }}>
                {item}
              </span>
            </div>
          ))}
        </div>
      </div>

      {/* Right Panel */}
      <div style={{
        backgroundColor: COLORS.panelMid,
        padding: '80px 64px',
        opacity: isVisible ? 1 : 0,
        transform: isVisible ? 'translateX(0)' : 'translateX(50px)',
        transition: 'all 0.8s ease-out'
      }}>
        <div style={{
          fontSize: '12px',
          textTransform: 'uppercase',
          letterSpacing: '0.15em',
          color: COLORS.muted,
          fontFamily: 'IBM Plex Sans, sans-serif',
          marginBottom: '24px'
        }}>
          AUTOMATION
        </div>
        <h2 style={{
          fontFamily: 'Space Grotesk, sans-serif',
          fontSize: 'clamp(32px, 4vw, 48px)',
          lineHeight: '1.1',
          fontWeight: 700,
          color: COLORS.ink,
          margin: '0 0 48px 0'
        }}>
          Fixes Before You<br />Merge
        </h2>
        <div style={{
          display: 'flex',
          flexDirection: 'column',
          gap: '32px'
        }}>
          {[
            'Creates fix PRs automatically',
            'Provides detailed explanations',
            'Maintains trust score analytics'
          ].map((item, idx) => (
            <div 
              key={idx} 
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '16px',
                opacity: isVisible ? 1 : 0,
                transform: isVisible ? 'translateX(0)' : 'translateX(20px)',
                transition: `all 0.6s ease-out ${0.2 + idx * 0.1}s`
              }}
            >
              <div style={{
                width: '10px',
                height: '10px',
                borderRadius: '50%',
                backgroundColor: COLORS.accentActive,
                flexShrink: 0,
                animation: isVisible ? `pulse 2s ease-in-out infinite ${idx * 0.3}s` : 'none'
              }} />
              <span style={{
                fontFamily: 'IBM Plex Sans, sans-serif',
                fontSize: '17px',
                lineHeight: '1.6',
                color: COLORS.ink
              }}>
                {item}
              </span>
            </div>
          ))}
        </div>
      </div>

      <style>{`
        @keyframes pulse {
          0%, 100% {
            transform: scale(1);
            opacity: 1;
          }
          50% {
            transform: scale(1.3);
            opacity: 0.7;
          }
        }

        @media (max-width: 768px) {
          .split-section {
            grid-template-columns: 1fr !important;
          }
        }
      `}</style>
    </section>
  );
};

// Live Example Section with Animations
const LiveExample = () => {
  const [trustScore, setTrustScore] = useState(92);
  const [isAnimated, setIsAnimated] = useState(false);
  const [showContent, setShowContent] = useState(false);

  useEffect(() => {
    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting && !isAnimated) {
          setIsAnimated(true);
          setTimeout(() => setShowContent(true), 300);
          
          const duration = 1500;
          const start = 92;
          const end = 75;
          const startTime = Date.now();

          const animate = () => {
            const elapsed = Date.now() - startTime;
            const progress = Math.min(elapsed / duration, 1);
            const current = Math.floor(start - (start - end) * progress);
            setTrustScore(current);

            if (progress < 1) {
              requestAnimationFrame(animate);
            }
          };
          
          setTimeout(() => animate(), 800);
        }
      },
      { threshold: 0.4 }
    );

    const element = document.getElementById('live-example');
    if (element) observer.observe(element);

    return () => observer.disconnect();
  }, [isAnimated]);

  return (
    <section id="live-example" style={{
      padding: '80px 32px',
      backgroundColor: COLORS.canvas
    }}>
      <div style={{
        maxWidth: '1000px',
        margin: '0 auto'
      }}>
        <div style={{
          backgroundColor: '#1C2128',
          borderRadius: '16px',
          padding: '48px',
          border: `1px solid #30363D`,
          boxShadow: '0 8px 32px rgba(0, 0, 0, 0.12)',
          opacity: isAnimated ? 1 : 0,
          transform: isAnimated ? 'translateY(0) scale(1)' : 'translateY(30px) scale(0.95)',
          transition: 'all 0.8s ease-out'
        }} className="live-example-content">
          <div style={{ 
            display: 'flex', 
            alignItems: 'flex-start', 
            gap: '16px', 
            marginBottom: '32px',
            opacity: showContent ? 1 : 0,
            transform: showContent ? 'translateY(0)' : 'translateY(-10px)',
            transition: 'all 0.5s ease-out 0.2s'
          }}>
            <div style={{
              width: '48px',
              height: '48px',
              borderRadius: '50%',
              backgroundColor: COLORS.canvas,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              flexShrink: 0
            }}>
              <Shield size={24} color={COLORS.ink} />
            </div>
            <div style={{ flex: 1 }}>
              <div style={{
                fontFamily: 'IBM Plex Sans, sans-serif',
                fontSize: '16px',
                fontWeight: 600,
                color: '#E6EDF3',
                marginBottom: '4px'
              }}>
                Veritas Bot
              </div>
              <div style={{
                fontFamily: 'IBM Plex Sans, sans-serif',
                fontSize: '13px',
                color: '#8B949E'
              }}>
                2 minutes ago
              </div>
            </div>
          </div>

          <div style={{
            fontFamily: 'IBM Plex Sans, sans-serif',
            fontSize: '18px',
            color: '#E6EDF3',
            lineHeight: '1.6',
            marginBottom: '32px',
            opacity: showContent ? 1 : 0,
            transform: showContent ? 'translateY(0)' : 'translateY(-10px)',
            transition: 'all 0.5s ease-out 0.3s'
          }}>
            <div style={{ marginBottom: '24px', fontSize: '17px', fontWeight: 600, display: 'flex', alignItems: 'center', gap: '8px' }}>
              ⚠️ Documentation Update Required
            </div>
            <div style={{ marginBottom: '24px', color: '#C9D1D9', fontSize: '15px' }}>
              Your code changes require doc updates:
            </div>
            <div style={{
              backgroundColor: '#0D1117',
              padding: '24px',
              borderRadius: '8px',
              marginBottom: '24px',
              border: '1px solid #30363D',
              opacity: showContent ? 1 : 0,
              transform: showContent ? 'translateX(0)' : 'translateX(-20px)',
              transition: 'all 0.6s ease-out 0.4s'
            }}>
              <div style={{
                fontFamily: 'JetBrains Mono, monospace',
                fontSize: '14px',
                lineHeight: '1.8',
                color: '#C9D1D9'
              }}>
                <div style={{ marginBottom: '12px' }}>
                  <span style={{ color: '#8B949E' }}>Function:</span> <span style={{ color: '#79C0FF' }}>login()</span>
                </div>
                <div style={{ marginBottom: '20px' }}>
                  <span style={{ color: '#8B949E' }}>File:</span> <span style={{ color: '#E6EDF3' }}>backend/auth.py</span>
                </div>
                <div style={{ color: '#8B949E', marginBottom: '12px' }}>
                  Issue: Added parameter <span style={{ color: '#79C0FF' }}>mfa_token</span> but:
                </div>
                <div style={{ paddingLeft: '16px', lineHeight: '1.8' }}>
                  <div>• README.md doesn't mention it</div>
                  <div>• docs/api.md missing parameter</div>
                </div>
              </div>
            </div>
            <div style={{
              display: 'inline-flex',
              alignItems: 'center',
              gap: '12px',
              backgroundColor: COLORS.accentAlert + '20',
              padding: '12px 20px',
              borderRadius: '8px',
              fontFamily: 'JetBrains Mono, monospace',
              fontSize: '15px',
              fontWeight: 600,
              color: COLORS.accentAlert,
              border: `1px solid ${COLORS.accentAlert}40`,
              opacity: showContent ? 1 : 0,
              transform: showContent ? 'scale(1)' : 'scale(0.9)',
              transition: 'all 0.6s ease-out 0.6s'
            }}>
              Trust Score: {trustScore}% 
              <span style={{ color: '#8B949E', fontSize: '13px', fontWeight: 400 }}>
                (down from 92%)
              </span>
            </div>
          </div>

          <button style={{
            backgroundColor: 'transparent',
            color: COLORS.accentActive,
            border: `2px solid ${COLORS.accentActive}`,
            borderRadius: '8px',
            padding: '12px 24px',
            fontSize: '15px',
            fontFamily: 'IBM Plex Sans, sans-serif',
            fontWeight: 500,
            cursor: 'pointer',
            transition: 'all 0.2s ease',
            opacity: showContent ? 1 : 0,
            transform: showContent ? 'translateY(0)' : 'translateY(10px)',
            transitionDelay: '0.7s'
          }}
          onMouseEnter={(e) => {
            e.target.style.backgroundColor = COLORS.accentActive;
            e.target.style.color = COLORS.ink;
            e.target.style.transform = 'translateX(4px)';
          }}
          onMouseLeave={(e) => {
            e.target.style.backgroundColor = 'transparent';
            e.target.style.color = COLORS.accentActive;
            e.target.style.transform = 'translateX(0)';
          }}
          >
            View Fix PR →
          </button>
        </div>
      </div>

      <style>{`
        @media (max-width: 768px) {
          .live-example-content {
            padding: 32px !important;
          }
        }
      `}</style>
    </section>
  );
};

// Built for Modern Teams Section
const ModernTeamsSection = () => {
  const [selectedLanguage, setSelectedLanguage] = useState('Java');
  const [isVisible, setIsVisible] = useState(false);
  const sectionRef = useRef(null);

  const languages = {
    Python: 'def authenticate(username, password):\n    return validate_user(username, password)',
    TypeScript: 'function authenticate(username: string, password: string) {\n    return validateUser(username, password);\n}',
    Java: 'public static void main(String[] args)',
    Markdown: '# Authentication\n\nUse the `authenticate()` function to verify users.'
  };

  useEffect(() => {
    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          setIsVisible(true);
        }
      },
      { threshold: 0.2 }
    );

    if (sectionRef.current) {
      observer.observe(sectionRef.current);
    }

    return () => observer.disconnect();
  }, []);

  return (
    <section ref={sectionRef} style={{
      padding: '80px 32px',
      backgroundColor: COLORS.canvas
    }}>
      <div style={{
        maxWidth: '1400px',
        margin: '0 auto'
      }}>
        <h2 style={{
          fontFamily: 'Space Grotesk, sans-serif',
          fontSize: 'clamp(32px, 5vw, 48px)',
          lineHeight: '1.2',
          fontWeight: 700,
          color: COLORS.ink,
          textAlign: 'center',
          margin: '0 0 64px 0'
        }}>
          Built for Modern Teams
        </h2>

        <div style={{
          display: 'grid',
          gridTemplateColumns: '1.2fr 0.8fr',
          gap: '48px',
          alignItems: 'start'
        }} className="modern-teams-grid">
          {/* Left: Multi-Language Support */}
          <div style={{
            backgroundColor: '#FFFFFF',
            border: `1px solid ${COLORS.border}`,
            borderRadius: '12px',
            padding: '40px',
            opacity: isVisible ? 1 : 0,
            transform: isVisible ? 'translateX(0)' : 'translateX(-30px)',
            transition: 'all 0.6s ease-out'
          }}>
            <h3 style={{
              fontFamily: 'Space Grotesk, sans-serif',
              fontSize: '28px',
              fontWeight: 700,
              color: COLORS.ink,
              margin: '0 0 32px 0'
            }}>
              Multi-Language Support
            </h3>

            {/* Language Tabs */}
            <div style={{
              display: 'flex',
              gap: '12px',
              marginBottom: '24px',
              flexWrap: 'wrap'
            }}>
              {Object.keys(languages).map((lang) => (
                <button
                  key={lang}
                  onClick={() => setSelectedLanguage(lang)}
                  style={{
                    padding: '10px 20px',
                    fontSize: '14px',
                    fontFamily: 'IBM Plex Sans, sans-serif',
                    fontWeight: 500,
                    border: 'none',
                    borderRadius: '6px',
                    cursor: 'pointer',
                    backgroundColor: selectedLanguage === lang ? COLORS.ink : COLORS.panelLight,
                    color: selectedLanguage === lang ? COLORS.canvas : COLORS.muted,
                    transition: 'all 0.2s ease'
                  }}
                  onMouseEnter={(e) => {
                    if (selectedLanguage !== lang) {
                      e.target.style.backgroundColor = COLORS.panelMid;
                    }
                  }}
                  onMouseLeave={(e) => {
                    if (selectedLanguage !== lang) {
                      e.target.style.backgroundColor = COLORS.panelLight;
                    }
                  }}
                >
                  {lang}
                </button>
              ))}
            </div>

            {/* Code Preview */}
            <div style={{
              backgroundColor: COLORS.canvas,
              border: `1px solid ${COLORS.border}`,
              borderRadius: '8px',
              padding: '24px',
              minHeight: '150px'
            }}>
              <div style={{
                display: 'flex',
                gap: '12px',
                marginBottom: '16px',
                fontSize: '13px',
                fontFamily: 'JetBrains Mono, monospace',
                color: COLORS.muted
              }}>
                <span>config.py</span>
                <span>types.ts</span>
                <span style={{ 
                  borderBottom: `2px solid ${COLORS.ink}`,
                  color: COLORS.ink,
                  paddingBottom: '4px'
                }}>
                  Main.java
                </span>
              </div>
              <pre style={{
                fontFamily: 'JetBrains Mono, monospace',
                fontSize: '14px',
                color: COLORS.ink,
                margin: 0,
                whiteSpace: 'pre-wrap',
                opacity: 1,
                animation: 'fadeInCode 0.3s ease-out'
              }}>
                {languages[selectedLanguage]}
              </pre>
            </div>
          </div>

          {/* Right: Stats Cards */}
          <div style={{
            display: 'flex',
            flexDirection: 'column',
            gap: '24px'
          }}>
            {/* Trust Score Card */}
            <div style={{
              backgroundColor: '#FFFFFF',
              border: `1px solid ${COLORS.border}`,
              borderRadius: '12px',
              padding: '32px',
              textAlign: 'center',
              opacity: isVisible ? 1 : 0,
              transform: isVisible ? 'translateY(0)' : 'translateY(30px)',
              transition: 'all 0.6s ease-out 0.2s'
            }}>
              <div style={{
                width: '100px',
                height: '100px',
                margin: '0 auto 16px',
                position: 'relative'
              }}>
                <svg width="100" height="100" viewBox="0 0 100 100">
                  <circle
                    cx="50"
                    cy="50"
                    r="45"
                    fill="none"
                    stroke={COLORS.panelLight}
                    strokeWidth="8"
                  />
                  <circle
                    cx="50"
                    cy="50"
                    r="45"
                    fill="none"
                    stroke={COLORS.ink}
                    strokeWidth="8"
                    strokeDasharray="283"
                    strokeDashoffset={isVisible ? 283 * (1 - 0.92) : 283}
                    strokeLinecap="round"
                    transform="rotate(-90 50 50)"
                    style={{
                      transition: 'stroke-dashoffset 1.5s ease-out 0.5s'
                    }}
                  />
                </svg>
                <div style={{
                  position: 'absolute',
                  top: '50%',
                  left: '50%',
                  transform: 'translate(-50%, -50%)',
                  fontFamily: 'Space Grotesk, sans-serif',
                  fontSize: '32px',
                  fontWeight: 700,
                  color: COLORS.ink
                }}>
                  92%
                </div>
              </div>
              <div style={{
                fontFamily: 'IBM Plex Sans, sans-serif',
                fontSize: '16px',
                color: COLORS.muted
              }}>
                Trust Score
              </div>
            </div>

            {/* IDE Integration Card */}
            <div style={{
              backgroundColor: '#FFFFFF',
              border: `1px solid ${COLORS.border}`,
              borderRadius: '12px',
              padding: '32px',
              textAlign: 'center',
              opacity: isVisible ? 1 : 0,
              transform: isVisible ? 'translateY(0)' : 'translateY(30px)',
              transition: 'all 0.6s ease-out 0.3s'
            }}>
              <div style={{
                fontSize: '40px',
                marginBottom: '16px'
              }}>
                ⌘
              </div>
              <div style={{
                fontFamily: 'IBM Plex Sans, sans-serif',
                fontSize: '16px',
                fontWeight: 600,
                color: COLORS.ink,
                marginBottom: '8px'
              }}>
                Works in your IDE
              </div>
              <div style={{
                fontFamily: 'IBM Plex Sans, sans-serif',
                fontSize: '13px',
                color: COLORS.muted
              }}>
                via LeanMCP
              </div>
            </div>

            {/* Speed Card */}
            <div style={{
              backgroundColor: '#FFFFFF',
              border: `1px solid ${COLORS.border}`,
              borderRadius: '12px',
              padding: '32px',
              textAlign: 'center',
              opacity: isVisible ? 1 : 0,
              transform: isVisible ? 'translateY(0)' : 'translateY(30px)',
              transition: 'all 0.6s ease-out 0.4s'
            }}>
              <div style={{
                width: '60px',
                height: '60px',
                margin: '0 auto 16px',
                position: 'relative'
              }}>
                <svg width="60" height="60" viewBox="0 0 60 60">
                  <circle
                    cx="30"
                    cy="30"
                    r="25"
                    fill="none"
                    stroke={COLORS.panelLight}
                    strokeWidth="4"
                  />
                  <path
                    d="M 30 30 L 30 10"
                    stroke={COLORS.ink}
                    strokeWidth="3"
                    strokeLinecap="round"
                    style={{
                      transformOrigin: '30px 30px',
                      animation: isVisible ? 'rotateClock 2s ease-out' : 'none'
                    }}
                  />
                </svg>
              </div>
              <div style={{
                fontFamily: 'Space Grotesk, sans-serif',
                fontSize: '36px',
                fontWeight: 700,
                color: COLORS.ink,
                marginBottom: '8px'
              }}>
                30s
              </div>
              <div style={{
                fontFamily: 'IBM Plex Sans, sans-serif',
                fontSize: '14px',
                color: COLORS.muted
              }}>
                Average analysis time
              </div>
            </div>
          </div>
        </div>
      </div>

      <style>{`
        @keyframes fadeInCode {
          from {
            opacity: 0;
            transform: translateY(10px);
          }
          to {
            opacity: 1;
            transform: translateY(0);
          }
        }

        @keyframes rotateClock {
          from {
            transform: rotate(0deg);
          }
          to {
            transform: rotate(270deg);
          }
        }

        @media (max-width: 1024px) {
          .modern-teams-grid {
            grid-template-columns: 1fr !important;
          }
        }
      `}</style>
    </section>
  );
};

// Trust Score Over Time Chart
const TrustScoreChart = () => {
  const [isVisible, setIsVisible] = useState(false);
  const [animatedPoints, setAnimatedPoints] = useState([]);
  const sectionRef = useRef(null);

  const points = [
    { week: 'Week 1', score: 65, x: 60, y: 190 },
    { week: 'Week 2', score: 75, x: 200, y: 175 },
    { week: 'Week 3', score: 85, x: 340, y: 145 },
    { week: 'Week 4', score: 92, x: 480, y: 120 }
  ];

  useEffect(() => {
    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          setIsVisible(true);
          // Animate points sequentially
          points.forEach((point, idx) => {
            setTimeout(() => {
              setAnimatedPoints(prev => [...prev, point]);
            }, idx * 300);
          });
        }
      },
      { threshold: 0.5 }
    );

    if (sectionRef.current) {
      observer.observe(sectionRef.current);
    }

    return () => observer.disconnect();
  }, []);

  return (
    <section ref={sectionRef} style={{
      padding: '64px 32px',
      backgroundColor: COLORS.canvas
    }}>
      <div style={{
        maxWidth: '600px',
        margin: '0 auto',
        backgroundColor: '#FFFFFF',
        border: `1px solid ${COLORS.border}`,
        borderRadius: '12px',
        padding: '40px',
        opacity: isVisible ? 1 : 0,
        transform: isVisible ? 'scale(1)' : 'scale(0.95)',
        transition: 'all 0.6s ease-out'
      }}>
        <h3 style={{
          fontFamily: 'IBM Plex Sans, sans-serif',
          fontSize: '18px',
          fontWeight: 600,
          color: COLORS.ink,
          margin: '0 0 32px 0'
        }}>
          Trust Score Over Time
        </h3>

        <svg width="100%" height="250" viewBox="0 0 540 250" style={{ overflow: 'visible' }}>
          {/* Grid lines */}
          <line x1="60" y1="200" x2="480" y2="200" stroke={COLORS.border} strokeWidth="1" />
          
          {/* Animated line */}
          {animatedPoints.length > 1 && (
            <path
              d={`M ${animatedPoints.map(p => `${p.x},${p.y}`).join(' L ')}`}
              fill="none"
              stroke={COLORS.ink}
              strokeWidth="3"
              style={{
                strokeDasharray: 1000,
                strokeDashoffset: isVisible ? 0 : 1000,
                transition: 'stroke-dashoffset 1.5s ease-out'
              }}
            />
          )}

          {/* Animated points */}
          {animatedPoints.map((point, idx) => (
            <g key={idx}>
              <circle
                cx={point.x}
                cy={point.y}
                r="6"
                fill={COLORS.ink}
                style={{
                  animation: 'popIn 0.3s ease-out',
                  transformOrigin: `${point.x}px ${point.y}px`
                }}
              />
              <circle
                cx={point.x}
                cy={point.y}
                r="10"
                fill="none"
                stroke={COLORS.ink}
                strokeWidth="2"
                opacity="0"
                style={{
                  animation: 'ripple 1s ease-out infinite',
                  animationDelay: `${idx * 0.3}s`
                }}
              />
            </g>
          ))}

          {/* Labels */}
          <text x="60" y="225" fontSize="13" fill={COLORS.muted} fontFamily="IBM Plex Sans">Week 1</text>
          <text x="460" y="225" fontSize="13" fill={COLORS.muted} fontFamily="IBM Plex Sans">Week 4</text>
        </svg>
      </div>

      <style>{`
        @keyframes popIn {
          0% {
            transform: scale(0);
            opacity: 0;
          }
          50% {
            transform: scale(1.2);
          }
          100% {
            transform: scale(1);
            opacity: 1;
          }
        }

        @keyframes ripple {
          0% {
            r: 6;
            opacity: 0.5;
          }
          100% {
            r: 20;
            opacity: 0;
          }
        }
      `}</style>
    </section>
  );
};

// Pricing Section with Animation
const PricingSection = () => {
  const [isVisible, setIsVisible] = useState(false);
  const sectionRef = useRef(null);

  useEffect(() => {
    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          setIsVisible(true);
        }
      },
      { threshold: 0.5 }
    );

    if (sectionRef.current) {
      observer.observe(sectionRef.current);
    }

    return () => observer.disconnect();
  }, []);

  return (
    <section ref={sectionRef} style={{
      padding: '80px 32px 96px',
      backgroundColor: COLORS.canvas,
      textAlign: 'center'
    }} id="pricing">
      <div style={{
        maxWidth: '700px',
        margin: '0 auto'
      }}>
        <h2 style={{
          fontFamily: 'Space Grotesk, sans-serif',
          fontSize: 'clamp(36px, 6vw, 56px)',
          lineHeight: '1.2',
          fontWeight: 700,
          color: COLORS.ink,
          margin: '0 0 24px 0',
          opacity: isVisible ? 1 : 0,
          transform: isVisible ? 'translateY(0)' : 'translateY(20px)',
          transition: 'all 0.6s ease-out'
        }}>
          Pay per analysis: $0.006
        </h2>
        <p style={{
          fontFamily: 'IBM Plex Sans, sans-serif',
          fontSize: '18px',
          color: COLORS.muted,
          marginBottom: '40px',
          opacity: isVisible ? 1 : 0,
          transform: isVisible ? 'translateY(0)' : 'translateY(20px)',
          transition: 'all 0.6s ease-out 0.1s'
        }}>
          No monthly fees. No surprises.
        </p>
        <button style={{
          backgroundColor: COLORS.ink,
          color: COLORS.canvas,
          border: 'none',
          borderRadius: '8px',
          padding: '18px 48px',
          fontSize: '17px',
          fontFamily: 'IBM Plex Sans, sans-serif',
          fontWeight: 600,
          cursor: 'pointer',
          transition: 'all 0.3s ease',
          opacity: isVisible ? 1 : 0,
          transform: isVisible ? 'scale(1)' : 'scale(0.9)',
          transitionDelay: '0.2s',
          boxShadow: isVisible ? '0 4px 12px rgba(14, 15, 18, 0.2)' : 'none'
        }}
        onMouseEnter={(e) => {
          e.target.style.transform = 'scale(1.05)';
          e.target.style.boxShadow = '0 8px 24px rgba(14, 15, 18, 0.3)';
        }}
        onMouseLeave={(e) => {
          e.target.style.transform = 'scale(1)';
          e.target.style.boxShadow = '0 4px 12px rgba(14, 15, 18, 0.2)';
        }}
        onMouseDown={(e) => e.target.style.transform = 'scale(0.98)'}
        onMouseUp={(e) => e.target.style.transform = 'scale(1.05)'}
        >
          Start Free
        </button>
      </div>
    </section>
  );
};

// Footer Component
const Footer = () => {
  const currentYear = new Date().getFullYear();

  return (
    <footer style={{
      borderTop: `1px solid ${COLORS.border}`,
      padding: '40px 32px',
      backgroundColor: COLORS.canvas
    }}>
      <div style={{
        maxWidth: '1400px',
        margin: '0 auto',
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        flexWrap: 'wrap',
        gap: '32px'
      }} className="footer-content">
        <div style={{
          fontFamily: 'IBM Plex Sans, sans-serif',
          fontSize: '14px',
          color: COLORS.muted
        }}>
          © {currentYear} Veritas.dev. All rights reserved.
        </div>

        <nav style={{
          display: 'flex',
          gap: '32px',
          alignItems: 'center',
          fontFamily: 'IBM Plex Sans, sans-serif',
          fontSize: '14px',
          flexWrap: 'wrap'
        }}>
          {['How it Works', 'Features', 'Pricing', 'Docs', 'GitHub'].map((item) => (
            <a 
              key={item}
              href={`#${item.toLowerCase().replace(/\s/g, '-')}`}
              style={{
                color: COLORS.muted,
                textDecoration: 'none',
                transition: 'color 0.2s ease'
              }}
              onMouseEnter={(e) => e.target.style.color = COLORS.ink}
              onMouseLeave={(e) => e.target.style.color = COLORS.muted}
            >
              {item}
            </a>
          ))}
        </nav>

        <div style={{ display: 'flex', gap: '20px', alignItems: 'center' }}>
          <a 
            href="#twitter" 
            aria-label="Twitter" 
            style={{ 
              color: COLORS.muted, 
              transition: 'all 0.2s',
              display: 'flex',
              alignItems: 'center'
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.color = COLORS.ink;
              e.currentTarget.style.transform = 'translateY(-2px)';
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.color = COLORS.muted;
              e.currentTarget.style.transform = 'translateY(0)';
            }}
          >
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M4 4l11.733 16h4.267l-11.733 -16z" />
              <path d="M4 20l6.768 -6.768m2.46 -2.46l6.772 -6.772" />
            </svg>
          </a>
          <a 
            href="#github" 
            aria-label="GitHub" 
            style={{ 
              color: COLORS.muted, 
              transition: 'all 0.2s',
              display: 'flex',
              alignItems: 'center'
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.color = COLORS.ink;
              e.currentTarget.style.transform = 'translateY(-2px)';
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.color = COLORS.muted;
              e.currentTarget.style.transform = 'translateY(0)';
            }}
          >
            <Github size={20} />
          </a>
          <a 
            href="#discord" 
            aria-label="Discord" 
            style={{ 
              color: COLORS.muted, 
              transition: 'all 0.2s',
              display: 'flex',
              alignItems: 'center'
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.color = COLORS.ink;
              e.currentTarget.style.transform = 'translateY(-2px)';
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.color = COLORS.muted;
              e.currentTarget.style.transform = 'translateY(0)';
            }}
          >
            <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor">
              <path d="M20.317 4.37a19.791 19.791 0 0 0-4.885-1.515a.074.074 0 0 0-.079.037c-.21.375-.444.864-.608 1.25a18.27 18.27 0 0 0-5.487 0a12.64 12.64 0 0 0-.617-1.25a.077.077 0 0 0-.079-.037A19.736 19.736 0 0 0 3.677 4.37a.07.07 0 0 0-.032.027C.533 9.046-.32 13.58.099 18.057a.082.082 0 0 0 .031.057a19.9 19.9 0 0 0 5.993 3.03a.078.078 0 0 0 .084-.028a14.09 14.09 0 0 0 1.226-1.994a.076.076 0 0 0-.041-.106a13.107 13.107 0 0 1-1.872-.892a.077.077 0 0 1-.008-.128a10.2 10.2 0 0 0 .372-.292a.074.074 0 0 1 .077-.01c3.928 1.793 8.18 1.793 12.062 0a.074.074 0 0 1 .078.01c.12.098.246.198.373.292a.077.077 0 0 1-.006.127a12.299 12.299 0 0 1-1.873.892a.077.077 0 0 0-.041.107c.36.698.772 1.362 1.225 1.993a.076.076 0 0 0 .084.028a19.839 19.839 0 0 0 6.002-3.03a.077.077 0 0 0 .032-.054c.5-5.177-.838-9.674-3.549-13.66a.061.061 0 0 0-.031-.03zM8.02 15.33c-1.183 0-2.157-1.085-2.157-2.419c0-1.333.956-2.419 2.157-2.419c1.21 0 2.176 1.096 2.157 2.42c0 1.333-.956 2.418-2.157 2.418zm7.975 0c-1.183 0-2.157-1.085-2.157-2.419c0-1.333.955-2.419 2.157-2.419c1.21 0 2.176 1.096 2.157 2.42c0 1.333-.946 2.418-2.157 2.418z"/>
            </svg>
          </a>
        </div>
      </div>

      <style>{`
        @media (max-width: 768px) {
          .footer-content {
            flex-direction: column;
            text-align: center;
            gap: 24px !important;
          }
          .footer-content nav {
            flex-direction: column;
            gap: 16px !important;
          }
        }
      `}</style>
    </footer>
  );
};

// Main App Component
export default function VeritasLanding() {
  return (
    <div style={{
      fontFamily: 'IBM Plex Sans, sans-serif',
      backgroundColor: COLORS.canvas,
      minHeight: '100vh',
      position: 'relative'
    }}>
      {/* Fixed Grid Background */}
      <div style={{
        position: 'fixed',
        top: 0,
        left: 0,
        width: '100%',
        height: '100%',
        backgroundImage: `
          linear-gradient(rgba(91, 95, 106, 0.2) 1px, transparent 1px),
          linear-gradient(90deg, rgba(91, 95, 106, 0.2) 1px, transparent 1px)
        `,
        backgroundSize: '32px 32px',
        pointerEvents: 'none',
        zIndex: 0
      }} />

      {/* Gradient Overlays */}
      <div style={{
        position: 'fixed',
        top: 0,
        left: 0,
        width: '100%',
        height: '100%',
        background: `
          radial-gradient(circle 1000px at 20% 20%, rgba(0, 217, 255, 0.08), transparent),
          radial-gradient(circle 900px at 80% 80%, rgba(255, 107, 53, 0.06), transparent),
          radial-gradient(circle 700px at 50% 50%, rgba(255, 230, 109, 0.04), transparent)
        `,
        pointerEvents: 'none',
        zIndex: 0
      }} />

      <style>{`
        @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@700;800&family=IBM Plex+Sans:wght@400;500;600&family=JetBrains+Mono:wght@400;500&display=swap');
        
        * {
          box-sizing: border-box;
        }
        
        body {
          margin: 0;
          padding: 0;
          -webkit-font-smoothing: antialiased;
          -moz-osx-font-smoothing: grayscale;
        }
        
        @media (prefers-reduced-motion: reduce) {
          * {
            animation-duration: 0.01ms !important;
            transition-duration: 0.01ms !important;
          }
        }
      `}</style>

      <div style={{ position: 'relative', zIndex: 1 }}>
        <Header />
        <Hero />
        <WorkflowDiagram />
        <ProductIntro />
        <ModernTeamsSection />
        <TrustScoreChart />
        <SplitSection />
        <LiveExample />
        <PricingSection />
        <Footer />
      </div>
    </div>
  );
}
