import tempfile
import shutil
from git import Repo
import os

def clone_repo(github_url: str) -> str:
    """Clone GitHub repo to temp directory."""
    temp_dir = tempfile.mkdtemp()
    print(f"📦 Cloning {github_url}...")
    Repo.clone_from(github_url, temp_dir)
    return temp_dir

def cleanup_repo(path: str):
    """Delete cloned repo."""
    shutil.rmtree(path, ignore_errors=True)
    print(f"🗑️ Cleaned up {path}")

def discover_files(repo_path: str) -> dict:
    """Find code and doc files (supports Python, JS, TS)."""
    code_files = []
    doc_files = []
    
    skip_dirs = {'.git', 'node_modules', 'venv', '__pycache__', 'dist', 'build'}
    
    for root, dirs, files in os.walk(repo_path):
        dirs[:] = [d for d in dirs if d not in skip_dirs]
        
        for file in files:
            path = os.path.join(root, file)
            # Multi-language support
            if file.endswith(('.py', '.js', '.ts', '.tsx', '.jsx')):
                code_files.append(path)
            elif file.endswith('.md'):
                doc_files.append(path)
    
    return {"code": code_files, "docs": doc_files}

# Test function
if __name__ == "__main__":
    print("Testing git_utils...")
    url = "https://github.com/bentoml/BentoML"
    
    path = clone_repo(url)
    files = discover_files(path)
    
    print(f"✅ Found {len(files['code'])} code files")
    print(f"✅ Found {len(files['docs'])} doc files")
    print(f"\nFirst 3 code files:")
    for f in files['code'][:3]:
        print(f"  - {f}")
    
    cleanup_repo(path)
    print("✅ Test complete!")