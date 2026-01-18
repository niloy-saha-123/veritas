"""
Intelligent Repository Agent

Discovers code and documentation files, maps them intelligently,
and extracts context for analysis.
"""

import re
import tempfile
import shutil
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass

try:
    from git import Repo, InvalidGitRepositoryError, GitCommandError
    GIT_AVAILABLE = True
except ImportError:
    GIT_AVAILABLE = False
    print("Warning: GitPython not installed. Repository cloning will not work.")


@dataclass
class FileCategory:
    """Represents a categorized file."""
    path: Path
    category: str  # 'code', 'doc', 'config', 'test', 'other'
    language: Optional[str] = None
    confidence: float = 1.0


class RepoScanner:
    """Intelligent file discovery and categorization agent."""
    
    # Code file extensions
    CODE_EXTENSIONS = {
        '.py': 'python',
        '.js': 'javascript',
        '.jsx': 'javascript',
        '.ts': 'typescript',
        '.tsx': 'typescript',
        '.java': 'java',
        '.go': 'go',
        '.rs': 'rust',
        '.cpp': 'cpp',
        '.c': 'c',
        '.cs': 'csharp',
    }
    
    # Documentation extensions
    DOC_EXTENSIONS = {
        '.md': 'markdown',
        '.markdown': 'markdown',
        '.rst': 'restructuredtext',
        '.txt': 'text',
        '.adoc': 'asciidoc',
        '.org': 'org',
    }
    
    # Code directory patterns (higher priority)
    CODE_DIRS = ['src', 'app', 'lib', 'packages', 'srcs', 'source', 'core', 'api']
    
    # Documentation directory patterns
    DOC_DIRS = ['docs', 'documentation', 'doc', 'wiki', 'guides', 'manual']
    
    # Documentation filename patterns
    DOC_PATTERNS = [
        'readme', 'api', 'changelog', 'contributing', 'license', 
        'guide', 'tutorial', 'docs', 'reference', 'spec'
    ]
    
    # Config/test patterns to skip
    CONFIG_PATTERNS = [
        '.git', '.github', 
        'node_modules', 'venv', '__pycache__', '.idea', '.vscode',
        # Test directories
        'test', 'tests', '__tests__', 'test_', 'tests_', 'spec', 'specs',
        'test/', '/test/', 'tests/', '/tests/',
        # Build/vendor directories
        'dist', 'build', '.tox', '.pytest_cache', '.mypy_cache',
        'vendor', 'vendored', 'third_party', 'third-party',
        # Coverage/reports
        '.coverage', 'coverage', 'htmlcov', '.pytest_cache',
        # Other common excludes
        '.eggs', 'eggs', '.env', '.cache'
    ]
    
    def discover_files(self, repo_path: Path) -> Dict[str, List[FileCategory]]:
        """
        Discover and categorize all files in repository.
        
        Returns:
            Dict with 'code', 'doc', and 'other' file lists
        """
        categorized = {
            'code': [],
            'doc': [],
            'other': []
        }
        
        if not repo_path.exists():
            return categorized
        
        # Walk through repository
        for file_path in repo_path.rglob('*'):
            # Skip hidden files, config dirs, and non-files
            if file_path.is_dir():
                continue
            
            if self._should_skip(file_path):
                continue
            
            # Categorize file
            category = self._categorize_file(file_path)
            
            if category.category == 'code':
                categorized['code'].append(category)
            elif category.category == 'doc':
                categorized['doc'].append(category)
            else:
                categorized['other'].append(category)
        
        return categorized
    
    def _should_skip(self, file_path: Path) -> bool:
        """Check if file/directory should be skipped."""
        path_str = str(file_path).lower()
        path_parts = path_str.split('/')
        path_parts.extend(path_str.split('\\'))  # Windows paths
        
        # Skip hidden files (but allow .github workflows, etc.)
        if file_path.name.startswith('.') and file_path.name not in ['.md', '.json', '.txt']:
            # Allow specific hidden files that are documentation
            if file_path.suffix not in ['.md', '.txt'] and not file_path.name.startswith('.github'):
                return True
        
        # Skip config/test directories - check if any path part matches
        for part in path_parts:
            for pattern in self.CONFIG_PATTERNS:
                # More precise matching - exact directory name or contains pattern
                if part == pattern or (pattern in part and len(pattern) > 3):
                    return True
        
        # Skip test files by name pattern
        filename_lower = file_path.name.lower()
        if filename_lower.startswith('test_') or filename_lower.startswith('tests_'):
            if file_path.suffix in self.CODE_EXTENSIONS:
                return True
        
        # Skip binary files
        if file_path.suffix in ['.png', '.jpg', '.jpeg', '.gif', '.ico', '.svg', '.pdf', '.zip', '.tar', '.gz', '.pyc', '.pyo']:
            return True
        
        return False
    
    def _categorize_file(self, file_path: Path) -> FileCategory:
        """
        Categorize a file using multiple heuristics.
        
        Priority:
        1. File extension (most reliable)
        2. Directory location
        3. Filename patterns
        4. Default to 'other'
        """
        filename_lower = file_path.name.lower()
        path_str = str(file_path).lower()
        suffix = file_path.suffix.lower()
        parent_dirs = [p.name.lower() for p in file_path.parents]
        
        # Check code extensions
        if suffix in self.CODE_EXTENSIONS:
            return FileCategory(
                path=file_path,
                category='code',
                language=self.CODE_EXTENSIONS[suffix],
                confidence=1.0
            )
        
        # Check doc extensions
        if suffix in self.DOC_EXTENSIONS:
            # If in code directory, might be docstring/code comment file
            # But .md files are usually documentation
            if suffix == '.md':
                return FileCategory(
                    path=file_path,
                    category='doc',
                    language='markdown',
                    confidence=0.95
                )
            else:
                return FileCategory(
                    path=file_path,
                    category='doc',
                    language=self.DOC_EXTENSIONS[suffix],
                    confidence=0.9
                )
        
        # Check directory location
        for doc_dir in self.DOC_DIRS:
            if doc_dir in parent_dirs:
                return FileCategory(
                    path=file_path,
                    category='doc',
                    confidence=0.8
                )
        
        # Check filename patterns
        for pattern in self.DOC_PATTERNS:
            if pattern in filename_lower:
                return FileCategory(
                    path=file_path,
                    category='doc',
                    confidence=0.7
                )
        
        # Default to other
        return FileCategory(
            path=file_path,
            category='other',
            confidence=0.5
        )


class DocCodeMapper:
    """Intelligent mapping between documentation and code files."""
    
    def map_docs_to_code(
        self,
        code_files: List[FileCategory],
        doc_files: List[FileCategory]
    ) -> Dict[Path, List[Path]]:
        """
        Map documentation files to their corresponding code files.
        
        Strategies:
        1. Exact name matching
        2. Path similarity
        3. Module-level docs
        4. Global documentation (README, API.md)
        """
        mappings: Dict[Path, List[Path]] = {}
        
        # Get code file paths
        code_paths = [cf.path for cf in code_files]
        doc_paths = [df.path for df in doc_files]
        
        # Global documentation files
        global_docs = self._find_global_docs(doc_paths)
        
        for code_file in code_paths:
            matches = []
            
            # Strategy 1: Exact name match (without extension)
            name_match = self._find_by_name(code_file, doc_paths)
            if name_match:
                matches.extend(name_match)
            
            # Strategy 2: Path similarity
            path_match = self._find_by_path(code_file, doc_paths)
            if path_match:
                matches.extend(path_match)
            
            # Strategy 3: Module-level docs (docs in same directory)
            module_match = self._find_module_docs(code_file, doc_paths)
            if module_match:
                matches.extend(module_match)
            
            # Strategy 4: Always include global docs
            matches.extend(global_docs)
            
            # Remove duplicates while preserving order
            seen = set()
            unique_matches = []
            for match in matches:
                if match not in seen:
                    seen.add(match)
                    unique_matches.append(match)
            
            mappings[code_file] = unique_matches
        
        return mappings
    
    def _find_by_name(self, code_file: Path, doc_files: List[Path]) -> List[Path]:
        """Find docs with same name as code file."""
        code_stem = code_file.stem.lower()
        matches = []
        
        for doc_file in doc_files:
            doc_stem = doc_file.stem.lower()
            # Exact match or code name is prefix of doc name
            if doc_stem == code_stem or doc_stem.startswith(code_stem + '_'):
                matches.append(doc_file)
        
        return matches
    
    def _find_by_path(self, code_file: Path, doc_files: List[Path]) -> List[Path]:
        """Find docs with similar path structure."""
        matches = []
        code_parts = code_file.parts
        
        for doc_file in doc_files:
            doc_parts = doc_file.parts
            
            # Check if paths overlap significantly
            # e.g., src/api/user.py → docs/api/user.md
            code_rel = code_file.relative_to(code_file.parents[2] if len(code_file.parts) > 2 else code_file.parent)
            doc_rel = doc_file.relative_to(doc_file.parents[2] if len(doc_file.parts) > 2 else doc_file.parent)
            
            # Simple heuristic: if they share parent directory name
            if code_file.parent.name == doc_file.parent.name:
                matches.append(doc_file)
        
        return matches
    
    def _find_module_docs(self, code_file: Path, doc_files: List[Path]) -> List[Path]:
        """Find documentation in same directory or parent."""
        matches = []
        code_dir = code_file.parent
        
        for doc_file in doc_files:
            doc_dir = doc_file.parent
            # Same directory or parent directory
            if doc_dir == code_dir or doc_dir == code_dir.parent:
                matches.append(doc_file)
        
        return matches
    
    def _find_global_docs(self, doc_files: List[Path]) -> List[Path]:
        """Find global documentation files (README, API.md, etc.)."""
        global_patterns = ['readme', 'api', 'changelog', 'contributing']
        global_docs = []
        
        for doc_file in doc_files:
            filename_lower = doc_file.name.lower()
            # Check if it's in root or docs/ directory
            depth = len(doc_file.parts)
            if depth <= 2:  # Root level or one level deep
                for pattern in global_patterns:
                    if pattern in filename_lower:
                        global_docs.append(doc_file)
                        break
        
        return global_docs


class RepoAgent:
    """Main agent orchestrating repository analysis."""
    
    def __init__(self):
        self.scanner = RepoScanner()
        self.mapper = DocCodeMapper()
        self.temp_dirs: List[Path] = []
    
    def clone_and_analyze(
        self,
        repo_url: str,
        branch: str = "main",
        use_token_company: bool = True
    ) -> Dict:
        """
        Clone repository, discover files, and prepare for analysis.
        
        Returns:
            Dict with discovered files and mappings
        """
        if not GIT_AVAILABLE:
            raise RuntimeError("GitPython not available. Install with: pip install gitpython")
        
        # Clone repository to temp directory
        temp_dir = Path(tempfile.mkdtemp(prefix="veritas_repo_"))
        self.temp_dirs.append(temp_dir)
        
        try:
            # Clone repo with branch fallback logic
            print(f"📥 Cloning repository: {repo_url}")
            
            # Try to clone with specified branch, fallback to detecting default branch
            repo = None
            try:
                repo = Repo.clone_from(repo_url, temp_dir, branch=branch, depth=1)
                print(f"✅ Cloned branch '{branch}' to: {temp_dir}")
            except GitCommandError as e:
                # If branch doesn't exist, try to detect default branch
                if "not found" in str(e).lower() or "exit code(128)" in str(e):
                    print(f"⚠️  Branch '{branch}' not found. Trying alternative branches...")
                    
                    # Try 'master' branch (common default for older repos)
                    try:
                        repo = Repo.clone_from(repo_url, temp_dir, branch="master", depth=1)
                        print(f"✅ Cloned branch 'master' to: {temp_dir}")
                    except GitCommandError:
                        # Last resort: clone without specifying branch (gets default)
                        print(f"⚠️  Trying default branch...")
                        try:
                            repo = Repo.clone_from(repo_url, temp_dir, depth=1)
                            # Get the branch that was checked out
                            if hasattr(repo, 'active_branch'):
                                default_branch = repo.active_branch.name
                                print(f"✅ Cloned default branch '{default_branch}' to: {temp_dir}")
                            else:
                                # If no active branch, try to get from remote
                                remote_refs = repo.remote().refs
                                for ref in remote_refs:
                                    if 'HEAD' in str(ref) or 'main' in str(ref) or 'master' in str(ref):
                                        print(f"✅ Cloned repository to: {temp_dir}")
                                        break
                                else:
                                    print(f"✅ Cloned repository to: {temp_dir}")
                        except Exception as e3:
                            raise RuntimeError(f"Failed to clone repository. Tried branches: {branch}, master, and default. Error: {str(e3)}")
                else:
                    raise  # Re-raise if it's a different error
            
            # Discover files
            print("🔍 Discovering files...")
            categorized = self.scanner.discover_files(temp_dir)
            
            code_count = len(categorized['code'])
            doc_count = len(categorized['doc'])
            print(f"📁 Found {code_count} code files and {doc_count} doc files")
            
            # Map docs to code
            print("🗺️  Mapping documentation to code...")
            mappings = self.mapper.map_docs_to_code(
                categorized['code'],
                categorized['doc']
            )
            
            # Prepare file contents
            # Note: Token Company compression happens in comparison engine during LLM calls
            code_files_dict = {}
            doc_files_dict = {}
            
            # Read code files
            for file_cat in categorized['code']:
                try:
                    content = file_cat.path.read_text(encoding='utf-8', errors='ignore')
                    # Use relative path as key
                    rel_path = file_cat.path.relative_to(temp_dir)
                    code_files_dict[str(rel_path)] = content
                except Exception as e:
                    print(f"⚠️  Error reading {file_cat.path}: {e}")
                    continue
            
            # Read doc files
            for file_cat in categorized['doc']:
                try:
                    content = file_cat.path.read_text(encoding='utf-8', errors='ignore')
                    rel_path = file_cat.path.relative_to(temp_dir)
                    doc_files_dict[str(rel_path)] = content
                except Exception as e:
                    print(f"⚠️  Error reading {file_cat.path}: {e}")
                    continue
            
            return {
                'temp_dir': temp_dir,
                'code_files': code_files_dict,
                'doc_files': doc_files_dict,
                'mappings': {str(k): [str(v) for v in vs] for k, vs in mappings.items()},
                'file_categories': {
                    'code': [(str(cf.path.relative_to(temp_dir)), cf.language) for cf in categorized['code']],
                    'doc': [(str(df.path.relative_to(temp_dir)), df.language) for df in categorized['doc']]
                }
            }
            
        except GitCommandError as e:
            # Cleanup on error
            self.cleanup()
            raise RuntimeError(f"Git clone failed: {str(e)}")
        except Exception as e:
            self.cleanup()
            raise
    
    def cleanup(self):
        """Clean up temporary directories."""
        for temp_dir in self.temp_dirs:
            if temp_dir.exists():
                try:
                    shutil.rmtree(temp_dir)
                    print(f"🧹 Cleaned up: {temp_dir}")
                except Exception as e:
                    print(f"⚠️  Error cleaning up {temp_dir}: {e}")
        self.temp_dirs.clear()
