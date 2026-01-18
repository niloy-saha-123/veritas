import React, { useState, useEffect } from 'react';
import { COLORS } from '../constants/constants';

// Hero Section
export const Hero = () => {
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

