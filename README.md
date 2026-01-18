<<<<<<< HEAD
# veritas
=======
# Veritas.dev

---

## Project Structure

```
nexhacks/
├── backend/                    # FastAPI Backend
│   ├── app/
│   │   ├── main.py            # Application entry point
│   │   ├── api/               # API routes
│   │   │   └── routes/
│   │   │       ├── health.py  # Health check endpoints
│   │   │       └── analysis.py # Analysis endpoints
│   │   ├── core/              # Core functionality
│   │   │   └── config.py      # Configuration management
│   │   ├── services/          # Business logic
│   │   │   ├── code_parser.py # Code parsing service
│   │   │   ├── doc_parser.py  # Documentation parsing
│   │   │   ├── comparator.py  # Comparison logic
│   │   │   └── integrations/  # Sponsor API integrations
│   │   ├── parsers/           # Language parsers
│   │   │   ├── parser_factory.py
│   │   │   ├── java_parser.py
│   │   │   ├── markdown_parser.py
│   │   │   └── json_parser.py
│   │   ├── models/            # Data models
│   │   │   └── schemas.py     # Pydantic schemas
│   │   └── utils/             # Utilities
│   │       └── helpers.py
│   ├── tests/                 # Test suite
│   ├── requirements.txt       # Python dependencies
│   └── .env.example          # Environment template
│
├── frontend/                  # React Frontend
│   ├── public/
│   └── src/
│
├── browser-extension/         # Chrome/Firefox Extension
│   ├── manifest.json
│   ├── popup/
│   ├── content/
│   └── background/
│
├── github-action/            # GitHub Action
│   ├── action.yml
│   └── src/
│
├── docs/
├── .gitignore
└── README.md
```

---

## Technology Stack

### Backend
- FastAPI - Web framework
- Pydantic - Data validation
- Python AST - Code parsing
- Uvicorn - ASGI server

### Frontend
- React
- Vite

### Browser Extension
- Vanilla JavaScript
- Chrome Extension API v3

### Integrations
- Token Company
- DevSwarm
- Arize
- LeanMCP

---

## Setup & Commands

### Backend

```bash
cd /Users/niloysaha/IdeaProjects/veritas/nexhacks

pip install -r backend/requirements.txt

cp backend/.env.example backend/.env

cd backend
python -m uvicorn app.main:app --reload
```

### Endpoints

- Root: http://localhost:8000
- Health: http://localhost:8000/api/v1/health
- Status: http://localhost:8000/api/v1/status
- Docs: http://localhost:8000/api/docs

### Testing

```bash
cd backend
pytest tests/ -v
```

### Browser Extension

1. Open `chrome://extensions/`
2. Enable "Developer mode"
3. Click "Load unpacked"
4. Select `browser-extension` directory

### GitHub Action

```yaml
- uses: ./github-action
  with:
    code-path: './src'
    docs-path: './docs'
    language: 'python'
```

---

## API Examples

```bash
curl http://localhost:8000/api/v1/health

curl -X POST http://localhost:8000/api/v1/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "code_content": "def hello():\n    pass",
    "doc_content": "# hello()\nSays hello",
    "language": "python"
  }'
```

---

**NexHacks**
>>>>>>> 1cae8de6781e5207cb454ff0ad898dcc7c2cc3d3
