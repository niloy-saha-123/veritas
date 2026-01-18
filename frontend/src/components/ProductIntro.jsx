import React from 'react';
import { COLORS } from '../constants/constants';

// Product Introduction Section
export const ProductIntro = () => {
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

