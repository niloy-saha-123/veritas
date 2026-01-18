"""
PR Analysis Service

Analyzes GitHub Pull Requests to detect documentation issues
in changed code files.
"""

import re
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from pathlib import Path

try:
    from github import Github, GithubException
    GITHUB_AVAILABLE = True
except ImportError:
    GITHUB_AVAILABLE = False
    print("Warning: PyGithub not installed. PR analysis will not work.")

from app.parsers.parser_factory import parse_code
from app.comparison.scorer import analyze_repository
from app.models.function_signature import FunctionSignature
from app.models.schemas import DiscrepancyReport, DiscrepancyType


@dataclass
class PRFileChange:
    """Represents a file change in a PR."""
    filename: str
    status: str  # 'added', 'modified', 'removed', 'renamed'
    additions: int
    deletions: int
    patch: Optional[str] = None
    content: Optional[str] = None


@dataclass
class PRAnalysisResult:
    """Result of PR analysis."""
    pr_number: int
    repo_url: str
    total_changes: int
    files_analyzed: int
    new_functions: List[Dict]
    modified_functions: List[Dict]
    missing_docs: List[Dict]
    outdated_docs: List[Dict]
    discrepancies: List[DiscrepancyReport]
    trust_score: int
    summary: str


class PRAnalyzer:
    """Analyzes GitHub Pull Requests for documentation issues."""
    
    def __init__(self, github_token: str):
        """
        Initialize PR Analyzer.
        
        Args:
            github_token: GitHub personal access token or fine-grained token
        """
        if not GITHUB_AVAILABLE:
            raise ImportError("PyGithub is required for PR analysis")
        
        self.github = Github(github_token)
    
    def _parse_repo_url(self, repo_url: str) -> Tuple[str, str]:
        """
        Parse repository URL to extract owner and repo name.
        
        Args:
            repo_url: GitHub repository URL (e.g., https://github.com/owner/repo)
            
        Returns:
            Tuple of (owner, repo_name)
        """
        # Handle various URL formats
        patterns = [
            r'github\.com[:/]([^/]+)/([^/]+?)(?:\.git)?/?$',
            r'github\.com/([^/]+)/([^/]+?)(?:\.git)?/?$',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, repo_url)
            if match:
                owner = match.group(1)
                repo_name = match.group(2).rstrip('/')
                return owner, repo_name
        
        raise ValueError(f"Invalid GitHub repository URL: {repo_url}")
    
    def _extract_functions_from_patch(self, patch: str, filename: str) -> List[FunctionSignature]:
        """
        Extract function signatures from a git patch/diff.
        
        Args:
            patch: Git patch content
            filename: Name of the file
            
        Returns:
            List of function signatures found in the patch
        """
        if not patch:
            return []
        
        # Extract only added lines (lines starting with +)
        added_lines = []
        current_hunk = []
        
        for line in patch.split('\n'):
            if line.startswith('@@'):
                # New hunk - process previous one
                if current_hunk:
                    added_lines.extend(current_hunk)
                    current_hunk = []
            elif line.startswith('+') and not line.startswith('+++'):
                # Added line (remove the + prefix)
                code_line = line[1:]
                if code_line.strip() and not code_line.strip().startswith('//'):
                    current_hunk.append(code_line)
            elif line.startswith(' ') or line.startswith('-'):
                # Context or removed line - keep context for better parsing
                if line.startswith(' '):
                    current_hunk.append(line[1:])
        
        # Process last hunk
        if current_hunk:
            added_lines.extend(current_hunk)
        
        # Combine lines into code content
        code_content = '\n'.join(added_lines)
        
        if not code_content.strip():
            return []
        
        # Parse the code to extract functions
        try:
            functions = parse_code(filename, code_content)
            return functions
        except Exception as e:
            print(f"Error parsing functions from patch for {filename}: {e}")
            return []
    
    def _get_file_content(self, repo, file_path: str, ref: str) -> Optional[str]:
        """
        Get file content from repository at a specific ref.
        
        Args:
            repo: PyGithub Repository object
            file_path: Path to the file
            ref: Git reference (branch, commit, etc.)
            
        Returns:
            File content as string, or None if not found
        """
        try:
            file = repo.get_contents(file_path, ref=ref)
            if file.encoding == 'base64':
                import base64
                return base64.b64decode(file.content).decode('utf-8', errors='ignore')
            return file.decoded_content.decode('utf-8', errors='ignore')
        except GithubException as e:
            if e.status == 404:
                return None
            raise
    
    def _find_documentation_file(self, repo, code_file_path: str, base_ref: str) -> Optional[str]:
        """
        Find corresponding documentation file for a code file.
        
        Args:
            repo: PyGithub Repository object
            code_file_path: Path to the code file
            base_ref: Base branch reference
            
        Returns:
            Documentation file content, or None if not found
        """
        code_path = Path(code_file_path)
        code_name = code_path.stem
        
        # Common documentation patterns
        doc_patterns = [
            f"docs/{code_name}.md",
            f"docs/{code_path.name}.md",
            f"documentation/{code_name}.md",
            f"{code_path.parent}/README.md",
            f"README.md",
        ]
        
        # Also check for docstrings in the same file
        try:
            file_content = self._get_file_content(repo, code_file_path, base_ref)
            if file_content:
                # Check if file has docstrings (for Python)
                if code_file_path.endswith('.py'):
                    return file_content
        except:
            pass
        
        # Try to find separate documentation file
        for pattern in doc_patterns:
            try:
                doc_content = self._get_file_content(repo, pattern, base_ref)
                if doc_content:
                    return doc_content
            except:
                continue
        
        return None
    
    def analyze_pr(self, repo_url: str, pr_number: int) -> PRAnalysisResult:
        """
        Analyze a GitHub Pull Request for documentation issues.
        
        Args:
            repo_url: GitHub repository URL
            pr_number: Pull request number
            
        Returns:
            PRAnalysisResult with analysis findings
        """
        owner, repo_name = self._parse_repo_url(repo_url)
        repo = self.github.get_repo(f"{owner}/{repo_name}")
        pr = repo.get_pull(pr_number)
        
        # Get PR details
        base_ref = pr.base.ref
        head_ref = pr.head.ref
        
        # Get changed files
        files = pr.get_files()
        
        new_functions = []
        modified_functions = []
        missing_docs = []
        outdated_docs = []
        all_code_functions = []
        all_doc_functions = []
        
        files_analyzed = 0
        
        for file in files:
            # Only analyze code files
            if not any(file.filename.endswith(ext) for ext in ['.py', '.js', '.jsx', '.ts', '.tsx', '.java', '.go', '.rs']):
                continue
            
            files_analyzed += 1
            
            # Extract functions from PR changes
            pr_functions = []
            if file.patch:
                pr_functions = self._extract_functions_from_patch(file.patch, file.filename)
            
            # Get base file content for comparison
            base_content = self._get_file_content(repo, file.filename, base_ref)
            base_functions = []
            if base_content:
                base_functions = parse_code(file.filename, base_content)
            
            # Get head file content
            head_content = self._get_file_content(repo, file.filename, head_ref)
            head_functions = []
            if head_content:
                head_functions = parse_code(file.filename, head_content)
            
            # Identify new functions (in head but not in base)
            base_func_names = {f.name for f in base_functions}
            for func in head_functions:
                if func.name not in base_func_names:
                    new_functions.append({
                        'name': func.name,
                        'file': file.filename,
                        'signature': str(func),
                        'status': file.status
                    })
            
            # Identify modified functions (changed signatures)
            for head_func in head_functions:
                base_func = next((f for f in base_functions if f.name == head_func.name), None)
                if base_func and str(head_func) != str(base_func):
                    modified_functions.append({
                        'name': head_func.name,
                        'file': file.filename,
                        'old_signature': str(base_func),
                        'new_signature': str(head_func),
                        'status': file.status
                    })
            
            # Check for documentation
            doc_content = self._find_documentation_file(repo, file.filename, base_ref)
            doc_functions = []
            if doc_content:
                doc_functions = parse_code(file.filename.replace('.py', '.md').replace('.js', '.md'), doc_content)
            
            # Collect functions for analysis
            all_code_functions.extend(head_functions)
            all_doc_functions.extend(doc_functions)
            
            # Check for missing documentation
            for func in pr_functions:
                # Check if function has documentation
                has_doc = any(
                    doc_func.name.lower() == func.name.lower() 
                    for doc_func in doc_functions
                )
                
                if not has_doc:
                    missing_docs.append({
                        'function': func.name,
                        'file': file.filename,
                        'signature': str(func),
                        'status': file.status
                    })
        
        # Analyze repository for discrepancies
        discrepancies = []
        trust_score = 100
        
        if all_code_functions and all_doc_functions:
            try:
                result = analyze_repository(all_code_functions, all_doc_functions, use_hybrid=True)
                trust_score = result.get('trust_score', 100)
                
                # Convert issues to discrepancies
                issues = result.get('issues', [])
                for issue in issues:
                    if isinstance(issue, dict):
                        discrepancies.append(
                            DiscrepancyReport(
                                type=DiscrepancyType.FUNCTION_SIGNATURE,
                                severity=issue.get("severity", "medium"),
                                location=issue.get("location", "unknown"),
                                description=issue.get("issue", ""),
                                code_snippet=issue.get("code_has"),
                                doc_snippet=issue.get("docs_say"),
                                suggestion=issue.get("suggested_fix"),
                            )
                        )
            except Exception as e:
                print(f"Error during repository analysis: {e}")
        
        # Build summary
        total_issues = len(missing_docs) + len(outdated_docs) + len(discrepancies)
        summary_parts = []
        
        if new_functions:
            summary_parts.append(f"{len(new_functions)} new function(s)")
        if modified_functions:
            summary_parts.append(f"{len(modified_functions)} modified function(s)")
        if missing_docs:
            summary_parts.append(f"{len(missing_docs)} missing documentation")
        if discrepancies:
            summary_parts.append(f"{len(discrepancies)} discrepancy/discrepancies")
        
        summary = f"PR #{pr_number}: {', '.join(summary_parts) if summary_parts else 'No issues found'}. Trust score: {trust_score}%"
        
        return PRAnalysisResult(
            pr_number=pr_number,
            repo_url=repo_url,
            total_changes=len(list(files)),
            files_analyzed=files_analyzed,
            new_functions=new_functions,
            modified_functions=modified_functions,
            missing_docs=missing_docs,
            outdated_docs=outdated_docs,
            discrepancies=discrepancies,
            trust_score=trust_score,
            summary=summary
        )
    
    def post_pr_comment(self, repo_url: str, pr_number: int, analysis_result: PRAnalysisResult) -> str:
        """
        Post analysis results as a comment on the PR.
        
        Args:
            repo_url: GitHub repository URL
            pr_number: Pull request number
            analysis_result: Results from PR analysis
            
        Returns:
            URL of the created comment
        """
        owner, repo_name = self._parse_repo_url(repo_url)
        repo = self.github.get_repo(f"{owner}/{repo_name}")
        pr = repo.get_pull(pr_number)
        
        # Build comment body
        comment_lines = [
            "## 🔍 Veritas PR Analysis",
            "",
            f"**Trust Score:** {analysis_result.trust_score}%",
            f"**Files Analyzed:** {analysis_result.files_analyzed}",
            "",
        ]
        
        if analysis_result.new_functions:
            comment_lines.extend([
                f"### ✨ New Functions ({len(analysis_result.new_functions)})",
                ""
            ])
            for func in analysis_result.new_functions[:10]:  # Limit to 10
                comment_lines.append(f"- `{func['name']}` in `{func['file']}`")
            if len(analysis_result.new_functions) > 10:
                comment_lines.append(f"- ... and {len(analysis_result.new_functions) - 10} more")
            comment_lines.append("")
        
        if analysis_result.missing_docs:
            comment_lines.extend([
                f"### ⚠️ Missing Documentation ({len(analysis_result.missing_docs)})",
                ""
            ])
            for doc in analysis_result.missing_docs[:10]:  # Limit to 10
                comment_lines.append(f"- `{doc['function']}` in `{doc['file']}` - needs documentation")
            if len(analysis_result.missing_docs) > 10:
                comment_lines.append(f"- ... and {len(analysis_result.missing_docs) - 10} more")
            comment_lines.append("")
        
        if analysis_result.discrepancies:
            comment_lines.extend([
                f"### 🔴 Documentation Discrepancies ({len(analysis_result.discrepancies)})",
                ""
            ])
            for disc in analysis_result.discrepancies[:5]:  # Limit to 5
                comment_lines.extend([
                    f"**{disc.description}**",
                    f"- Severity: {disc.severity}",
                    ""
                ])
            if len(analysis_result.discrepancies) > 5:
                comment_lines.append(f"- ... and {len(analysis_result.discrepancies) - 5} more discrepancies")
            comment_lines.append("")
        
        if not (analysis_result.new_functions or analysis_result.missing_docs or analysis_result.discrepancies):
            comment_lines.append("✅ **No documentation issues found!** Great job! 🎉")
        
        comment_body = "\n".join(comment_lines)
        
        # Post comment
        comment = pr.create_issue_comment(comment_body)
        return comment.html_url
