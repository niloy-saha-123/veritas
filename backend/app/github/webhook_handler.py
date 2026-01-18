# backend/app/github/webhook_handler.py
"""
GitHub App webhook handler
- Triggers when PR is created/updated
- Compares NEW code (from PR) vs EXISTING docs (on remote)
- Creates fix PR or Issue if needed
- No comments, no UI, just direct GitHub actions
"""

from fastapi import Request, HTTPException
import hmac
import hashlib
import os
import requests
from dotenv import load_dotenv

load_dotenv()

GITHUB_WEBHOOK_SECRET = os.getenv("GITHUB_WEBHOOK_SECRET", "")


def verify_webhook_signature(payload: bytes, signature: str) -> bool:
    """Verify webhook is from GitHub."""
    if not signature or not GITHUB_WEBHOOK_SECRET:
        return True  # Allow in dev mode
    
    expected = hmac.new(
        GITHUB_WEBHOOK_SECRET.encode(),
        payload,
        hashlib.sha256
    ).hexdigest()
    
    return hmac.compare_digest(f"sha256={expected}", signature)


async def handle_webhook(request: Request):
    """Handle GitHub webhook events."""
    
    payload = await request.body()
    signature = request.headers.get("X-Hub-Signature-256", "")
    
    if not verify_webhook_signature(payload, signature):
        raise HTTPException(status_code=401, detail="Invalid signature")
    
    event = request.headers.get("X-GitHub-Event", "")
    data = await request.json()
    
    if event == "pull_request":
        return await handle_pull_request(data)
    elif event == "installation":
        return {"status": "ok", "action": data.get("action")}
    
    return {"status": "ignored"}


async def handle_pull_request(data: dict):
    """
    Handle PR webhook:
    1. Get files changed in PR (new code from local)
    2. Get existing docs from base branch (remote)
    3. Compare: Does existing docs match new code?
    4. If mismatch → Create fix PR or Issue
    5. If perfect → Do nothing
    """
    
    action = data.get("action", "")
    if action not in ["opened", "synchronize"]:
        return {"status": "ignored", "action": action}
    
    repo = data["repository"]["full_name"]
    pr_number = data["pull_request"]["number"]
    installation_id = data["installation"]["id"]
    base_branch = data["pull_request"]["base"]["ref"]
    head_branch = data["pull_request"]["head"]["ref"]
    head_sha = data["pull_request"]["head"]["sha"]
    
    print(f"PR #{pr_number}: {head_branch} → {base_branch}")
    
    try:
        from app.github.auth import get_installation_token, create_fix_pr, create_issue
        from app.parsers.parser_factory import parse_code
        from app.parsers.markdown_parser import parse_markdown
        from app.comparison.hybrid_engine import HybridComparator
        
        token = get_installation_token(installation_id)
        headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json"
        }
        
        # =============================================
        # 1. GET FILES CHANGED IN THIS PR (from local)
        # =============================================
        pr_files_resp = requests.get(
            f"https://api.github.com/repos/{repo}/pulls/{pr_number}/files",
            headers=headers
        )
        changed_files = pr_files_resp.json()
        
        # Filter to code files only
        code_extensions = ['.py', '.js', '.ts', '.jsx', '.tsx', '.java']
        changed_code_files = [
            f for f in changed_files
            if any(f['filename'].endswith(ext) for ext in code_extensions)
        ]
        
        if not changed_code_files:
            print("No code files changed")
            return {"status": "ok", "action": "no_code_changes"}
        
        # =============================================
        # 2. PARSE NEW CODE FROM PR BRANCH
        # =============================================
        new_functions = []
        
        for file_info in changed_code_files:
            filename = file_info['filename']
            
            # Get file content from PR branch
            content_resp = requests.get(
                f"https://api.github.com/repos/{repo}/contents/{filename}",
                headers=headers,
                params={"ref": head_sha}
            )
            
            if content_resp.status_code == 200:
                import base64
                content = base64.b64decode(content_resp.json()['content']).decode('utf-8')
                functions = parse_code(filename, content)
                new_functions.extend(functions)
        
        print(f"Parsed {len(new_functions)} functions from PR")
        
        # =============================================
        # 3. GET EXISTING DOCS FROM BASE BRANCH (remote)
        # =============================================
        doc_functions = []
        doc_extensions = ['.md', '.markdown']
        
        # Get tree of base branch to find doc files
        tree_resp = requests.get(
            f"https://api.github.com/repos/{repo}/git/trees/{base_branch}",
            headers=headers,
            params={"recursive": "1"}
        )
        
        if tree_resp.status_code == 200:
            tree = tree_resp.json().get('tree', [])
            doc_files = [
                item['path'] for item in tree
                if item['type'] == 'blob' and 
                any(item['path'].endswith(ext) for ext in doc_extensions)
            ]
            
            # Parse each doc file
            for doc_path in doc_files[:20]:  # Limit for speed
                content_resp = requests.get(
                    f"https://api.github.com/repos/{repo}/contents/{doc_path}",
                    headers=headers,
                    params={"ref": base_branch}
                )
                
                if content_resp.status_code == 200:
                    import base64
                    content = base64.b64decode(content_resp.json()['content']).decode('utf-8')
                    docs = parse_markdown(content, doc_path)
                    doc_functions.extend(docs)
        
        print(f"Found {len(doc_functions)} documented functions on {base_branch}")
        
        # =============================================
        # 4. COMPARE: NEW CODE vs EXISTING DOCS
        # =============================================
        comparator = HybridComparator()
        issues = []
        undocumented = []
        matched = 0
        
        new_func_map = {f.name.lower(): f for f in new_functions}
        doc_func_map = {f.name.lower(): f for f in doc_functions}
        
        for name, func in new_func_map.items():
            if name in doc_func_map:
                # Function exists in docs - compare
                result = comparator.compare(func, doc_func_map[name])
                if result.matches:
                    matched += 1
                else:
                    issues.extend(result.issues)
            else:
                # Function NOT in docs - undocumented
                undocumented.append(func)
        
        print(f"Matched: {matched}, Undocumented: {len(undocumented)}, Issues: {len(issues)}")
        
        # =============================================
        # 5. TAKE ACTION
        # =============================================
        
        # Perfect - do nothing
        if len(undocumented) == 0 and len(issues) == 0:
            print("Documentation is up to date")
            return {"status": "ok", "action": "none"}
        
        # Missing docs - create fix PR
        if len(undocumented) > 0:
            print(f"Creating docs PR for {len(undocumented)} functions")
            
            docs_content = generate_docs(undocumented)
            
            fix_pr = create_fix_pr(
                repo=repo,
                token=token,
                base_branch=base_branch,
                title=f"docs: Document {len(undocumented)} new functions",
                body=generate_pr_body(undocumented, pr_number),
                files={"docs/API.md": docs_content}
            )
            
            return {"status": "ok", "action": "created_pr", "pr": fix_pr}
        
        # Mismatches - create issue
        if len(issues) > 0:
            print(f"Creating issue for {len(issues)} mismatches")
            
            issue_num = create_issue(
                repo=repo,
                token=token,
                title=f"Docs out of sync with code (PR #{pr_number})",
                body=generate_issue_body(issues, pr_number),
                labels=["documentation"]
            )
            
            return {"status": "ok", "action": "created_issue", "issue": issue_num}
        
        return {"status": "ok"}
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return {"status": "error", "error": str(e)}


def generate_docs(functions: list) -> str:
    """Generate markdown documentation."""
    
    content = "# API Documentation\n\n"
    
    for func in functions:
        content += f"## {func.name}\n\n"
        
        if func.parameters:
            content += "**Parameters:**\n"
            for p in func.parameters:
                ptype = f" ({p.type})" if p.type else ""
                content += f"- `{p.name}`{ptype}\n"
            content += "\n"
        
        if func.return_type:
            content += f"**Returns:** `{func.return_type}`\n\n"
        
        if func.docstring:
            content += f"{func.docstring}\n\n"
        
        content += "---\n\n"
    
    return content


def generate_pr_body(functions: list, related_pr: int) -> str:
    """Generate PR description."""
    
    return f"""Adds documentation for new functions introduced in PR #{related_pr}.

**Functions documented:**
{chr(10).join(f'- `{f.name}()`' for f in functions[:15])}

---
*Auto-generated by Veritas*
"""


def generate_issue_body(issues: list, related_pr: int) -> str:
    """Generate issue description."""
    
    body = f"""Documentation needs to be updated to match code changes in PR #{related_pr}.

**Issues found:**

"""
    
    for issue in issues[:10]:
        body += f"### `{issue.function}`\n"
        body += f"- **Problem:** {issue.issue}\n"
        body += f"- **Code:** `{issue.code_has}`\n"
        body += f"- **Docs:** `{issue.docs_say}`\n"
        body += f"- **Fix:** {issue.suggested_fix}\n\n"
    
    if len(issues) > 10:
        body += f"*...and {len(issues) - 10} more issues*\n"
    
    body += "\n---\n*Generated by Veritas*"
    
    return body