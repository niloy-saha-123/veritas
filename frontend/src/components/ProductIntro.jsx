import React, { useState, useEffect, useRef } from 'react';
import { COLORS } from '../constants/constants';

// Product Introduction Section
export const ProductIntro = () => {
  const [count, setCount] = useState(0);
  const [hasAnimated, setHasAnimated] = useState(false);
  const targetValue = 85; // 85 billion
  const duration = 2000; // 2 seconds
  const countRef = useRef(null);

  useEffect(() => {
    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting && !hasAnimated) {
            setHasAnimated(true);
            animateCount();
          }
        });
      },
      { threshold: 0.3 }
    );

    if (countRef.current) {
      observer.observe(countRef.current);
    }

    return () => {
      if (countRef.current) {
        observer.unobserve(countRef.current);
      }
    };
  }, [hasAnimated]);

  const animateCount = () => {
    const startTime = Date.now();
    const startValue = 0;

    const updateCount = () => {
      const now = Date.now();
      const elapsed = now - startTime;
      const progress = Math.min(elapsed / duration, 1);
      
      // Easing function for smooth animation
      const easeOutCubic = 1 - Math.pow(1 - progress, 3);
      const currentValue = startValue + (targetValue - startValue) * easeOutCubic;
      
      setCount(Math.floor(currentValue));

      if (progress < 1) {
        requestAnimationFrame(updateCount);
      } else {
        setCount(targetValue);
      }
    };

    requestAnimationFrame(updateCount);
  };

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
        <div 
          ref={countRef}
          style={{
            textAlign: 'left'
          }}>
          <div style={{
            fontFamily: 'Space Grotesk, sans-serif',
            fontSize: 'clamp(48px, 7vw, 72px)',
            fontWeight: 700,
            color: COLORS.ink,
            lineHeight: '1',
            marginBottom: '8px',
            transition: 'transform 0.3s ease'
          }}>
            ${count}B
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
        }
      `}</style>
    </section>
  );
};

