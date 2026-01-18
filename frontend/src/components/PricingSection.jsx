import React, { useState, useEffect, useRef } from 'react';
import { COLORS } from '../constants/constants';

// Pricing Section with Animation
export const PricingSection = () => {
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

