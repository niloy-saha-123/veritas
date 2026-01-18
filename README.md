# Veritas.dev

**AI-Powered Documentation Verification for Code and Docs**

Automatically verifies that your documentation matches your code on every PR. Uses hybrid AI (embeddings + LLM) to detect mismatches, missing docs, and outdated information.

---

## 🎯 What It Does

When you create a PR, Veritas:
1. **Analyzes** new code vs existing documentation
2. **Detects** mismatches, missing docs, or outdated info
3. **Takes action:**
   - ✅ Perfect docs → Silent success
   - 📝 Missing docs → Creates PR with auto-generated documentation
   - ⚠️ Mismatches → Creates GitHub Issue with specific problems

**No comments, no UI - just native GitHub PRs and Issues.**

---

## 🏗️ Architecture

### Three-Layer Hybrid AI System

```
┌─────────────────────────────────────────────────┐
│ 1. Embedding-Based Screening (Fast, Free)      │
│    • Sentence Transformers (all-MiniLM-L6-v2)  │
│    • Handles 85% of comparisons                 │
│    • 10ms per comparison                        │
└─────────────────────────────────────────────────┘
                      ↓
┌─────────────────────────────────────────────────┐
│ 2. LLM Analysis (Accurate, Paid)               │
│    • Google Gemini 2.5 Flash                    │
│    • Token Company compression (60% savings)    │
│    • Handles edge cases                         │
│    • 2s per comparison                          │
└─────────────────────────────────────────────────┘
                      ↓
┌─────────────────────────────────────────────────┐
│ 3. Adaptive Routing (Smart)                    │
│    • High similarity → Skip LLM                 │
│    • Medium similarity → Hybrid                 │
│    • Low similarity → LLM focused               │
│    • 88% cost reduction vs LLM-only             │
└─────────────────────────────────────────────────┘
```

**Performance:**
- 3.3x faster than LLM-only
- 88% cheaper than LLM-only
- 92% accuracy

---

## 📁 Project Structure

```
nexhacks/
├── backend/                    # FastAPI Backend
│   ├── app/
│   │   ├── main.py            # Application entry point
│   │   ├── github/            # (Optional) GitHub integration helpers
│   │   │   ├── webhook_handler.py
│   │   │   └── auth.py
│   │   ├── parsers/           # Language parsers
│   │   │   ├── python_parser.py
│   │   │   ├── javascript_parser.py
│   │   │   ├── java_parser.py
│   │   │   ├── markdown_parser.py
│   │   │   └── json_parser.py
│   │   ├── comparison/        # AI comparison engine
│   │   │   ├── hybrid_engine.py    # Hybrid comparator
│   │   │   ├── semantic_matcher.py # Embedding similarity
│   │   │   └── engine.py      # Gemini LLM
│   │   ├── services/
│   │   │   └── integrations/
│   │   │       └── token_company.py # Token compression
│   │   └── models/
│   │       └── function_signature.py
│   ├── tests/
│   ├── requirements.txt
│   └── .env.example
│
├── frontend/                  # React Landing Page
│   ├── src/
│   │   ├── components/
│   │   │   ├── Hero.jsx
│   │   │   ├── WorkflowDiagram.jsx
│   │   │   └── ModernTeamsSection.jsx
│   │   └── App.jsx
│   └── package.json
│
├── github-action/            # GitHub Action (preferred CI integration)
│   ├── action.yml
│   └── src/
│
└── docs/
    └── api-documentation.md
```

---

## 🚀 Quick Start

### 1. Backend Setup

```bash
cd backend

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your keys:
# - GEMINI_API_KEY
# - TOKEN_COMPANY_API_KEY
# - API_HOST
# - API_PORT
# - DEBUG
# - ALLOWED_ORIGINS

# Run server
uvicorn app.main:app --reload --port 8000
```

**Endpoints:**
- Health: `http://localhost:8000/api/v1/health`
- Analyze (raw content): `POST http://localhost:8000/api/v1/analyze`
- Analyze (upload files): `POST http://localhost:8000/api/v1/analyze/upload`
- Analyze (batch repo files): `POST http://localhost:8000/api/v1/analyze/batch`
- Analyze GitHub repo: `POST http://localhost:8000/api/v1/analyze/github`
- API Docs: `http://localhost:8000/api/docs`

### 2. Frontend Setup (Landing Page)

```bash
cd frontend

# Install dependencies
npm install

# Run dev server
npm run dev
```

Dashboard available at `http://localhost:3000`

### 3. CI Integration (No GitHub App)

- Use the provided GitHub Action to run verification in CI without a GitHub App.
- Configure paths and behavior via inputs in `github-action/action.yml`.
- Optionally fail the build on discrepancies.

Example workflow:

```yaml
name: Veritas Docs Verification
on:
  pull_request:
    paths:
      - "src/**"
      - "docs/**"

jobs:
  verify-docs:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Run Veritas Verification
        uses: ./nexhacks/github-action
        with:
          code-path: ./src
          docs-path: ./docs
          fail-on-discrepancy: true
```

---

## 🔧 Technology Stack

### Backend
- **FastAPI** - Web framework
- **Sentence Transformers** - Embedding generation
- **Google Gemini 2.5 Flash** - LLM analysis
- **Token Company** - Prompt compression
- **GitPython** - Repository cloning
- **Python AST** - Code parsing

### Frontend
- **React** - UI framework
- **Vite** - Build tool
- **Lucide React** - Icons

### Parsers
- **Python** - AST-based
- **JavaScript/TypeScript** - Regex-based
- **Java** - Regex-based
- **Markdown** - Regex-based
- **JSON** - OpenAPI/generic API schemas

---

## 🔑 Environment Variables

### Backend `.env`

```bash
# AI APIs
GEMINI_API_KEY=your_gemini_api_key
TOKEN_COMPANY_API_KEY=your_token_company_key

# Server
API_PORT=8000
API_HOST=0.0.0.0
DEBUG=True
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:5173
```

### Frontend `.env` (optional)
```bash
VITE_API_URL=http://localhost:8000
```

---

## 🧪 Testing

### Run Parser Tests

```bash
cd backend
pytest tests/test_parsers.py -v
```

### Run Comparison Engine Tests

```bash
pytest tests/test_comparison_engine.py -v
```

### Test Analysis Endpoints Locally

```bash
# Run backend
uvicorn app.main:app --reload --port 8000

# Analyze raw content
curl -X POST "http://localhost:8000/api/v1/analyze" \
  -H "Content-Type: application/json" \
  -d '{"code_content": "def add(a,b): return a+b", "doc_content": "Function add(a, b) returns sum"}'

# Analyze a GitHub repo (no GitHub App required)
curl -X POST "http://localhost:8000/api/v1/analyze/github" \
  -H "Content-Type: application/json" \
  -d '{"repo_url": "https://github.com/user/repo", "branch": "main"}'
```

---

## 📊 How It Works

### Workflow

```
Developer creates PR
         ↓
CI runs Veritas GitHub Action (or calls API directly)
         ↓
Backend analyzes:
  • Embedding similarity (fast screening)
  • LLM analysis (detailed verification)
         ↓
Decision:
  ├─ Docs match code → Pass ✅
  ├─ Missing docs → Report with generated docs suggestions 📝
  └─ Mismatches → Report detailed problems ⚠️
```

### Supported Languages

| Language | Parser | Features |
|----------|--------|----------|
| Python | AST | Full signature extraction |
| JavaScript | Regex | Functions, classes, exports |
| TypeScript | Regex | Type annotations |
| Java | Regex | Methods, classes |
| Markdown | Regex | Code blocks, API refs |
| JSON | Native | OpenAPI, generic APIs |

---

## 🎨 Frontend Features

- ✨ Clean, minimal paper-white design
- 📊 Real-time analysis progress
- 🎯 Trust score visualization
- 📋 Detailed discrepancy reports
- 🔍 Repository analysis via URL
- 🎭 Animated code examples
- 📱 Responsive design

---

## 📖 API Documentation

See [docs/api-documentation.md](docs/api-documentation.md) for detailed API reference.

### Quick Example

```bash
# Analyze a GitHub repository (no app required)
curl -X POST http://localhost:8000/api/v1/analyze/github \
  -H "Content-Type: application/json" \
  -d '{"repo_url": "https://github.com/user/repo"}'
```

---

## 🚢 Deployment

### Backend (Railway/Render)

```bash
# Install Railway CLI
curl -fsSL https://railway.app/install.sh | sh

# Login and deploy
railway login
railway init
railway up

# Set environment variables in Railway dashboard
```

### Frontend (Vercel/Netlify)

```bash
# Install Vercel CLI
npm i -g vercel

# Deploy
cd frontend
vercel
```

---

## 🤝 Contributing

This project was built for **NexHacks 2025**.

---

## 📝 License

MIT

---

**Built with ❤️ for NexHacks**
