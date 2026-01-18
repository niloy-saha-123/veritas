import { 
  Shield, Zap, FileCode, FileText, Minimize, Brain, 
  Gauge, MessageSquare, Code, GitPullRequest, TrendingUp, 
  Eye, Menu, X, Github
} from 'lucide-react';

// Design System Constants
export const COLORS = {
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
export const WORKFLOW_NODES = [
  { id: 'webhook', x: 500, y: 100, label: 'GitHub Webhook', icon: Zap, number: 1 },
  { id: 'code', x: 300, y: 250, label: 'Fetch Code', icon: FileCode, number: 2 },
  { id: 'docs', x: 700, y: 250, label: 'Fetch Docs', icon: FileText, number: 3 },
  { id: 'compress', x: 500, y: 400, label: 'Bear-1 Compress', icon: Minimize, number: 4 },
  { id: 'analyze', x: 500, y: 550, label: 'Claude Analysis', icon: Brain, number: 5 },
  { id: 'score', x: 300, y: 700, label: 'Trust Score', icon: Gauge, number: 6 },
  { id: 'comment', x: 700, y: 700, label: 'PR Comment', icon: MessageSquare, number: 7 }
];

export const WORKFLOW_EDGES = [
  { from: 'webhook', to: 'code' },
  { from: 'webhook', to: 'docs' },
  { from: 'code', to: 'compress' },
  { from: 'docs', to: 'compress' },
  { from: 'compress', to: 'analyze' },
  { from: 'analyze', to: 'score' },
  { from: 'analyze', to: 'comment' }
];

export const TOOLTIP_CONTENT = {
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

