import React, { useState, useEffect, useRef } from 'react';
import { COLORS } from '../constants/constants';

// Split Section Component with Animations
export const SplitSection = () => {
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

