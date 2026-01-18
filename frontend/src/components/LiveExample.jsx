import React, { useState, useEffect } from 'react';
import { Shield } from 'lucide-react';
import { COLORS } from '../constants/constants';

// Live Example Section with Animations
export const LiveExample = () => {
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

