# backend/app/github/webhook_handler.py
"""
GitHub App webhook handler - Posts comments on PRs
"""

from fastapi import Request, HTTPException
import hmac
import hashlib
import os
from dotenv import load_dotenv

load_dotenv()

GITHUB_WEBHOOK_SECRET = os.getenv("GITHUB_WEBHOOK_SECRET", "")

def verify_webhook_signature(payload: bytes, signature: str) -> bool:
    """Verify that webhook is from GitHub."""
    if not signature or not GITHUB_WEBHOOK_SECRET:
        return False
    
    expected = hmac.new(
        GITHUB_WEBHOOK_SECRET.encode(),
        payload,
        hashlib.sha256
    ).hexdigest()
    
    return hmac.compare_digest(f"sha256={expected}", signature)

async def handle_webhook(request: Request):
    """Handle GitHub webhook events."""
    
    # Get payload and signature
    payload = await request.body()
    signature = request.headers.get("X-Hub-Signature-256", "")
    
    # Verify signature
    if not verify_webhook_signature(payload, signature):
        raise HTTPException(status_code=401, detail="Invalid signature")
    
    # Get event type
    event = request.headers.get("X-GitHub-Event", "")
    data = await request.json()
    
    # Handle different events
    if event == "pull_request":
        return await handle_pull_request(data)
    elif event == "installation":
        return await handle_installation(data)
    
    return {"status": "ignored", "event": event}

async def handle_installation(data: dict):
    """Handle app installation events."""
    action = data.get("action", "")
    print(f"✅ Installation {action}")
    return {"status": "processed", "action": action}

async def handle_pull_request(data: dict):
    """Handle PR events - analyze and comment!"""
    
    action = data.get("action", "")
    
    # Only process opened/synchronize
    if action not in ["opened", "synchronize"]:
        return {"status": "ignored", "action": action}
    
    # Get PR details
    repo = data["repository"]["full_name"]
    pr_number = data["pull_request"]["number"]
    installation_id = data["installation"]["id"]
    github_url = data["repository"]["clone_url"]
    
    print(f"📝 Processing PR #{pr_number} in {repo}")
    
    try:
        # Import analysis pipeline
        from app.github.auth import get_installation_token, post_pr_comment
        import asyncio
        
        # Run analysis (reuse your existing pipeline!)
        print(f"🔍 Analyzing {github_url}...")
        
        # Import and run your analysis
        from app.utils.git_utils import clone_repo, discover_files, cleanup_repo
        from app.parsers.parser_factory import parse_code
        from app.parsers.markdown_parser import parse_markdown
        from app.comparison.hybrid_engine import HybridComparator
        
        # Quick analysis
        repo_path = clone_repo(github_url)
        files = discover_files(repo_path)
        
        # Parse (simplified for speed)
        code_functions = []
        for code_file in files['code'][:50]:  # Limit to 50 files for speed
            try:
                with open(code_file, 'r', encoding='utf-8') as f:
                    functions = parse_code(code_file, f.read())
                    code_functions.extend(functions)
            except:
                pass
        
        doc_functions = []
        for doc_file in files['docs']:
            try:
                with open(doc_file, 'r', encoding='utf-8') as f:
                    docs = parse_markdown(f.read())
                    doc_functions.extend(docs)
            except:
                pass
        
        # Compare
        comparator = HybridComparator()
        all_issues = []
        verified = 0
        total = 0
        
        code_func_map = {f.name.lower(): f for f in code_functions}
        doc_func_map = {f.name.lower(): f for f in doc_functions}
        
        for func_name in list(code_func_map.keys())[:20]:  # Check first 20
            if func_name in doc_func_map:
                total += 1
                result = comparator.compare(code_func_map[func_name], doc_func_map[func_name])
                if result.matches:
                    verified += 1
                all_issues.extend(result.issues)
        
        trust_score = int((verified / total) * 100) if total > 0 else 0
        
        cleanup_repo(repo_path)
        
        # Generate comment
        comment = generate_comment(trust_score, len(all_issues), all_issues[:5])
        
        # Get auth token and post comment
        token = get_installation_token(installation_id)
        post_pr_comment(repo, pr_number, token, comment)
        
        print(f"✅ Posted comment on PR #{pr_number}")
        
        return {
            "status": "success",
            "repo": repo,
            "pr": pr_number,
            "trust_score": trust_score
        }
        
    except Exception as e:
        print(f"❌ Error processing PR: {e}")
        import traceback
        traceback.print_exc()
        return {"status": "error", "error": str(e)}

def generate_comment(trust_score: int, issue_count: int, top_issues: list) -> str:
    """Generate markdown comment for PR."""
    
    if trust_score >= 80:
        emoji = "✅"
        status = "PASSED"
    elif trust_score >= 60:
        emoji = "⚠️"
        status = "WARNING"
    else:
        emoji = "❌"
        status = "NEEDS ATTENTION"
    
    comment = f"""## {emoji} Veritas Documentation Check: {status}

**Trust Score:** {trust_score}%

### Summary
- Issues Found: {issue_count}

"""
    
    if top_issues:
        comment += "### Top Issues\n\n"
        for issue in top_issues:
            comment += f"**{issue.function}()** - {issue.issue}\n"
            comment += f"- Code has: `{issue.code_has}`\n"
            comment += f"- Docs say: `{issue.docs_say}`\n\n"
    
    comment += "\n---\n*Powered by [Veritas](https://github.com/niloy-saha-123/veritas)*"
    
    return comment