"""
PR Creation Service

Automatically creates GitHub Pull Requests with documentation fixes
based on analysis discrepancies.
"""

import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass

try:
    from github import Github, GithubException, InputGitAuthor
    from git import Repo as GitRepo, GitCommandError
    GITHUB_AVAILABLE = True
except ImportError:
    GITHUB_AVAILABLE = False
    print("Warning: PyGithub not installed. PR creation will not work.")

from app.core.config import settings
from app.models.schemas import DiscrepancyReport


@dataclass
class PRResult:
    """Result of PR creation."""
    success: bool
    pr_url: Optional[str] = None
    branch_name: Optional[str] = None
    error: Optional[str] = None
    files_changed: int = 0


class DocumentationGenerator:
    """Generates documentation fixes from discrepancies."""
    
    def generate_doc_content(
        self, 
        function_name: str,
        discrepancy: DiscrepancyReport,
        code_snippet: Optional[str] = None
    ) -> str:
        """
        Generate documentation content for a function based on discrepancy.
        
        Args:
            function_name: Name of the function
            discrepancy: Discrepancy report with details
            code_snippet: Code snippet if available
            
        Returns:
            Generated markdown documentation
        """
        doc_lines = []
        
        # Function header
        doc_lines.append(f"# {function_name}\n")
        
        # Description
        if discrepancy.description:
            doc_lines.append(f"{discrepancy.description}\n")
        
        # Parameters section
        if discrepancy.code_snippet:
            # Extract parameters from code snippet
            params = self._extract_params_from_code(discrepancy.code_snippet)
            if params:
                doc_lines.append("## Parameters\n")
                for param in params:
                    doc_lines.append(f"- `{param['name']}`: {param.get('type', 'Any')} - {param.get('description', '')}")
                doc_lines.append("")
        
        # Return type
        if discrepancy.code_snippet:
            return_type = self._extract_return_type(discrepancy.code_snippet)
            if return_type:
                doc_lines.append(f"## Returns\n")
                doc_lines.append(f"`{return_type}` - {discrepancy.suggestion or 'Function return value'}\n")
        
        # Example/Usage
        if code_snippet:
            doc_lines.append("## Example\n")
            doc_lines.append("```python")
            doc_lines.append(code_snippet)
            doc_lines.append("```\n")
        
        # Suggestion
        if discrepancy.suggestion:
            doc_lines.append("## Notes\n")
            doc_lines.append(f"> {discrepancy.suggestion}\n")
        
        return "\n".join(doc_lines)
    
    def _extract_params_from_code(self, code_snippet: str) -> List[Dict[str, str]]:
        """Extract parameters from code snippet."""
        params = []
        # Simple regex to find function parameters
        match = re.search(r'def\s+\w+\s*\((.*?)\)', code_snippet)
        if match:
            param_str = match.group(1)
            for param in param_str.split(','):
                param = param.strip()
                if param:
                    parts = param.split(':')
                    name = parts[0].strip()
                    param_type = parts[1].strip() if len(parts) > 1 else None
                    params.append({
                        'name': name,
                        'type': param_type or 'Any',
                        'description': ''
                    })
        return params
    
    def _extract_return_type(self, code_snippet: str) -> Optional[str]:
        """Extract return type from code snippet."""
        match = re.search(r'->\s*(\w+)', code_snippet)
        if match:
            return match.group(1)
        return None
    
    def generate_fix_summary(self, discrepancies: List[DiscrepancyReport]) -> Dict[str, List[DiscrepancyReport]]:
        """
        Group discrepancies by function for organized documentation generation.
        
        Returns:
            Dict mapping function names to their discrepancies
        """
        grouped = {}
        for disc in discrepancies:
            # Extract function name from location or description
            func_name = self._extract_function_name(disc)
            if func_name:
                if func_name not in grouped:
                    grouped[func_name] = []
                grouped[func_name].append(disc)
        return grouped
    
    def _extract_function_name(self, discrepancy: DiscrepancyReport) -> Optional[str]:
        """Extract function name from discrepancy."""
        # Try to extract from description
        match = re.search(r"function\s+['\"]?(\w+)['\"]?", discrepancy.description, re.IGNORECASE)
        if match:
            return match.group(1)
        
        # Try to extract from code snippet
        if discrepancy.code_snippet:
            match = re.search(r'def\s+(\w+)', discrepancy.code_snippet)
            if match:
                return match.group(1)
        
        # Try location
        if discrepancy.location and discrepancy.location != "unknown":
            parts = discrepancy.location.split(':')
            if len(parts) > 0:
                # Last part might be function name
                return parts[-1].split('.')[-1]
        
        return None


class PRService:
    """Service for creating GitHub Pull Requests with documentation fixes."""
    
    def __init__(self, github_token: Optional[str] = None):
        """
        Initialize PR service.
        
        Args:
            github_token: GitHub Personal Access Token (or use from settings)
        """
        self.token = github_token or settings.GITHUB_TOKEN
        if not self.token:
            raise ValueError("GitHub token is required. Set GITHUB_TOKEN environment variable.")
        
        if not GITHUB_AVAILABLE:
            raise ImportError("PyGithub not installed. Install with: pip install PyGithub")
        
        self.github = Github(self.token)
        self.doc_generator = DocumentationGenerator()
    
    def create_pr_for_discrepancies(
        self,
        repo_url: str,
        branch: str,
        discrepancies: List[DiscrepancyReport],
        metadata: Dict,
        pr_title: Optional[str] = None,
        pr_body: Optional[str] = None
    ) -> PRResult:
        """
        Create a GitHub PR with documentation fixes.
        
        Args:
            repo_url: GitHub repository URL (e.g., https://github.com/user/repo)
            branch: Base branch name (e.g., 'main')
            discrepancies: List of discrepancies to fix
            metadata: Analysis metadata (trust_score, etc.)
            pr_title: Custom PR title (optional)
            pr_body: Custom PR body (optional)
            
        Returns:
            PRResult with PR URL and status
        """
        try:
            # Parse repository info
            repo_info = self._parse_repo_url(repo_url)
            if not repo_info:
                return PRResult(
                    success=False,
                    error=f"Invalid repository URL: {repo_url}"
                )
            
            owner, repo_name = repo_info
            
            # Get repository (this will fail with 404/403 if token lacks access)
            try:
                github_repo = self.github.get_repo(f"{owner}/{repo_name}")
            except GithubException as e:
                if e.status == 404 or "Resource not accessible" in str(e):
                    return PRResult(
                        success=False,
                        error=f"❌ Cannot access repository '{owner}/{repo_name}'\n\n"
                              f"🔐 Required Token Permissions:\n"
                              f"   - 'repo' scope (Full control of private repositories)\n\n"
                              f"📋 How to fix:\n"
                              f"   1. Go to GitHub → Settings → Developer settings → Personal access tokens\n"
                              f"   2. Edit your token or create a new one\n"
                              f"   3. Select 'repo' scope (or all 'repo' permissions)\n"
                              f"   4. If repository is in an organization, you may need:\n"
                              f"      - Organization approval\n"
                              f"      - SSO authorization (enable SSO for the token)\n\n"
                              f"💡 For public repositories, basic 'public_repo' scope may work.\n"
                              f"   For private repositories, you MUST have 'repo' scope.\n\n"
                              f"Error details: {e.data.get('message', str(e)) if hasattr(e, 'data') else str(e)}"
                    )
                raise
            
            # Generate branch name
            branch_name = f"veritas/docs-fix-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
            
            # Create branch from base branch
            try:
                base_ref = github_repo.get_git_ref(f"heads/{branch}")
                github_repo.create_git_ref(
                    ref=f"refs/heads/{branch_name}",
                    sha=base_ref.object.sha
                )
            except GithubException as e:
                # Branch might already exist, try with different suffix
                if e.status == 422:  # Unprocessable Entity
                    branch_name = f"{branch_name}-{hash(repr(discrepancies))[:8]}"
                    base_ref = github_repo.get_git_ref(f"heads/{branch}")
                    github_repo.create_git_ref(
                        ref=f"refs/heads/{branch_name}",
                        sha=base_ref.object.sha
                    )
                else:
                    raise
            
            # Generate documentation files
            files_to_create = self._generate_doc_files(discrepancies, github_repo, branch_name)
            
            if not files_to_create:
                # Delete branch if no files to create
                try:
                    github_repo.get_git_ref(f"heads/{branch_name}").delete()
                except:
                    pass
                return PRResult(
                    success=False,
                    error="No documentation files could be generated from discrepancies"
                )
            
            # Commit files to the new branch
            self._commit_files(github_repo, branch_name, files_to_create)
            
            # Create PR
            pr_title = pr_title or self._generate_pr_title(metadata, len(discrepancies))
            pr_body = pr_body or self._generate_pr_body(discrepancies, metadata)
            
            pr = github_repo.create_pull(
                title=pr_title,
                body=pr_body,
                head=branch_name,
                base=branch
            )
            
            return PRResult(
                success=True,
                pr_url=pr.html_url,
                branch_name=branch_name,
                files_changed=len(files_to_create)
            )
            
        except GithubException as e:
            error_msg = e.data.get('message', str(e)) if hasattr(e, 'data') else str(e)
            
            # Provide more helpful error messages
            if e.status == 404:
                if "not found" in error_msg.lower() or "Resource not accessible" in error_msg:
                    return PRResult(
                        success=False,
                        error=f"Repository not accessible. Possible reasons:\n"
                              f"1. Token doesn't have 'repo' scope (needed for private repos)\n"
                              f"2. Repository is private and token lacks access\n"
                              f"3. Repository belongs to an organization requiring SSO authentication\n"
                              f"Error: {error_msg}"
                    )
                else:
                    return PRResult(
                        success=False,
                        error=f"Repository or branch not found: {error_msg}"
                    )
            elif e.status == 403:
                return PRResult(
                    success=False,
                    error=f"Permission denied. Token may lack required scopes:\n"
                          f"Required: 'repo' scope (full control of private repositories)\n"
                          f"Error: {error_msg}"
                )
            elif e.status == 401:
                return PRResult(
                    success=False,
                    error=f"Authentication failed. Please check your GitHub token.\n"
                          f"Error: {error_msg}"
                )
            else:
                return PRResult(
                    success=False,
                    error=f"GitHub API error ({e.status}): {error_msg}"
                )
        except Exception as e:
            return PRResult(
                success=False,
                error=f"Failed to create PR: {str(e)}"
            )
    
    def _parse_repo_url(self, repo_url: str) -> Optional[Tuple[str, str]]:
        """Parse GitHub repository URL to extract owner and repo name."""
        # Handle various URL formats
        patterns = [
            r'github\.com[/:]([\w-]+)/([\w.-]+)',
            r'github\.com[/:]([\w-]+)/([\w.-]+)\.git',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, repo_url)
            if match:
                return match.group(1), match.group(2).rstrip('.git')
        
        return None
    
    def _generate_doc_files(
        self,
        discrepancies: List[DiscrepancyReport],
        github_repo,
        branch_name: str
    ) -> List[Dict[str, str]]:
        """
        Generate documentation files from discrepancies.
        
        Returns:
            List of dicts with 'path' and 'content' for files to create
        """
        files = []
        
        # Group discrepancies by function
        grouped = self.doc_generator.generate_fix_summary(discrepancies)
        
        for func_name, func_discrepancies in grouped.items():
            # Use the first discrepancy as primary source
            primary_disc = func_discrepancies[0]
            
            # Generate documentation content
            doc_content = self.doc_generator.generate_doc_content(
                func_name,
                primary_disc,
                primary_disc.code_snippet
            )
            
            # Determine file path
            doc_path = f"docs/{func_name}.md"
            
            # Check if file already exists in the repo
            existing_sha = None
            try:
                existing_file = github_repo.get_contents(doc_path, ref=branch_name)
                # Append to existing file
                existing_content = existing_file.decoded_content.decode('utf-8')
                doc_content = f"{existing_content}\n\n---\n\n{doc_content}"
                existing_sha = existing_file.sha
            except:
                # File doesn't exist, create new
                pass
            
            files.append({
                'path': doc_path,
                'content': doc_content,
                'message': f"Add documentation for {func_name}",
                'sha': existing_sha  # For updates
            })
        
        return files
    
    def _commit_files(
        self,
        github_repo,
        branch_name: str,
        files: List[Dict[str, str]]
    ):
        """
        Commit multiple files to the repository.
        
        Uses GitHub API create_file/update_file methods.
        """
        for file_info in files:
            path = file_info['path']
            content = file_info['content']
            existing_sha = file_info.get('sha')
            message = file_info.get('message', f"Update {path}")
            
            try:
                if existing_sha:
                    # Update existing file
                    existing_file = github_repo.get_contents(path, ref=branch_name)
                    github_repo.update_file(
                        path=path,
                        message=message,
                        content=content,
                        sha=existing_sha,
                        branch=branch_name
                    )
                else:
                    # Create new file
                    github_repo.create_file(
                        path=path,
                        message=message,
                        content=content,
                        branch=branch_name
                    )
            except Exception as e:
                # Log error but continue with other files
                print(f"Warning: Failed to create/update {path}: {e}")
                continue
    
    def _generate_pr_title(self, metadata: Dict, discrepancy_count: int) -> str:
        """Generate PR title from metadata."""
        trust_score = metadata.get('trust_score', 0)
        return f"📚 Documentation Fixes (Trust Score: {trust_score}%)"
    
    def _generate_pr_body(
        self,
        discrepancies: List[DiscrepancyReport],
        metadata: Dict
    ) -> str:
        """Generate PR body with summary and details."""
        lines = []
        
        # Header
        lines.append("## 📋 Documentation Fixes by Veritas.dev\n")
        lines.append("This PR contains automated documentation fixes based on code-documentation analysis.\n")
        
        # Summary
        trust_score = metadata.get('trust_score', 0)
        total_functions = metadata.get('total_functions', 0)
        verified = metadata.get('verified', 0)
        
        lines.append("### 📊 Analysis Summary\n")
        lines.append(f"- **Trust Score**: {trust_score}%")
        lines.append(f"- **Total Functions**: {total_functions}")
        lines.append(f"- **Verified**: {verified}")
        lines.append(f"- **Issues Found**: {len(discrepancies)}\n")
        
        # Issues breakdown
        severity_counts = {}
        for disc in discrepancies:
            severity = disc.severity
            severity_counts[severity] = severity_counts.get(severity, 0) + 1
        
        if severity_counts:
            lines.append("### 🔍 Issues Breakdown\n")
            for severity in ['high', 'medium', 'low']:
                count = severity_counts.get(severity, 0)
                if count > 0:
                    lines.append(f"- **{severity.capitalize()}**: {count}")
            lines.append("")
        
        # Discrepancies list
        lines.append("### 📝 Fixed Discrepancies\n")
        for i, disc in enumerate(discrepancies[:20], 1):  # Limit to first 20
            lines.append(f"{i}. **{disc.type.value}** ({disc.severity})")
            lines.append(f"   - {disc.description}")
            if disc.suggestion:
                lines.append(f"   - 💡 {disc.suggestion}")
            lines.append("")
        
        if len(discrepancies) > 20:
            lines.append(f"\n*... and {len(discrepancies) - 20} more issues.*\n")
        
        # Footer
        lines.append("---\n")
        lines.append("*This PR was automatically created by [Veritas.dev](https://veritas.dev) - Automated Documentation Verification*")
        
        return "\n".join(lines)
