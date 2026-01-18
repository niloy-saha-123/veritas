#!/usr/bin/env python3
"""Test script for the intelligent GitHub repository agent."""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent))

import requests
import json

def test_github_agent():
    """Test the /api/v1/analyze/github endpoint."""
    base_url = "http://localhost:8000"
    endpoint = f"{base_url}/api/v1/analyze/github"
    
    print("=" * 80)
    print("🤖 TESTING INTELLIGENT GITHUB REPOSITORY AGENT")
    print("=" * 80)
    
    # Test with your test repo
    test_repo = "https://github.com/niloy-saha-123/test_repo"
    # Or use another test repo:
    # test_repo = "https://github.com/fastapi/fastapi"
    
    print(f"\n📦 Repository: {test_repo}")
    print(f"📡 Endpoint: {endpoint}")
    
    payload = {
        "repo_url": test_repo,
        "branch": "main",  # Agent will auto-detect if this branch doesn't exist
        "use_token_company": True
    }
    
    print("\n🚀 Starting analysis...")
    print("   (This may take a few minutes for large repositories)")
    
    try:
        response = requests.post(
            endpoint,
            json=payload,
            timeout=600  # 10 minutes for large repos
        )
        
        print(f"\n✅ Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            
            print("\n" + "=" * 80)
            print("📊 ANALYSIS RESULTS")
            print("=" * 80)
            
            print(f"\n📈 Summary:")
            print(f"   Status: {result.get('status')}")
            print(f"   Summary: {result.get('summary')}")
            
            metadata = result.get('metadata', {})
            
            print(f"\n🎯 Trust Score & Statistics:")
            print(f"   Trust Score: {metadata.get('trust_score')}%")
            print(f"   Total Functions: {metadata.get('total_functions')}")
            print(f"   Verified: {metadata.get('verified')}")
            print(f"   Average Confidence: {metadata.get('average_confidence', 0):.1f}%")
            
            print(f"\n📁 Files Analyzed:")
            print(f"   Code Files: {metadata.get('code_files_analyzed', 0)}")
            code_names = metadata.get('code_file_names', [])
            if code_names:
                print(f"      Sample: {', '.join(code_names[:5])}")
                if len(code_names) > 5:
                    print(f"      ... and {len(code_names) - 5} more")
            
            print(f"   Doc Files: {metadata.get('doc_files_analyzed', 0)}")
            doc_names = metadata.get('doc_file_names', [])
            if doc_names:
                print(f"      Sample: {', '.join(doc_names[:5])}")
                if len(doc_names) > 5:
                    print(f"      ... and {len(doc_names) - 5} more")
            
            print(f"\n🔧 Functions Discovered:")
            print(f"   Code Functions: {metadata.get('code_functions_count', 0)}")
            print(f"   Doc Functions: {metadata.get('doc_functions_count', 0)}")
            
            method_stats = metadata.get('method_stats', {})
            if method_stats:
                print(f"\n🤖 ML Methods Used:")
                for method, count in method_stats.items():
                    print(f"   - {method}: {count} functions")
            
            discrepancies = result.get('discrepancies', [])
            print(f"\n⚠️  Discrepancies Found: {len(discrepancies)}")
            
            if discrepancies:
                print(f"\n📋 Issue Details (showing first 10):")
                for i, disc in enumerate(discrepancies[:10], 1):
                    severity = disc.get('severity', 'unknown').upper()
                    desc = disc.get('description', 'No description')
                    location = disc.get('location', 'unknown')
                    code_snip = disc.get('code_snippet', '')[:60] if disc.get('code_snippet') else ''
                    doc_snip = disc.get('doc_snippet', '')[:60] if disc.get('doc_snippet') else ''
                    
                    print(f"\n   {i}. [{severity}] {desc}")
                    if location != 'unknown':
                        print(f"      Location: {location}")
                    if code_snip:
                        print(f"      Code: {code_snip}...")
                    if doc_snip:
                        print(f"      Docs: {doc_snip}...")
                
                if len(discrepancies) > 10:
                    print(f"\n   ... and {len(discrepancies) - 10} more issues")
            else:
                print("\n✨ No discrepancies found - documentation perfectly matches code!")
            
            # Show file mappings sample
            mappings = metadata.get('file_mappings', {})
            if mappings:
                print(f"\n🗺️  File Mappings (sample):")
                for code_file, doc_files in list(mappings.items())[:5]:
                    print(f"   {code_file}:")
                    for doc_file in doc_files[:3]:
                        print(f"      → {doc_file}")
            
            print("\n" + "=" * 80)
            print("✅ Repository analysis completed successfully!")
            print("=" * 80)
            
        else:
            print(f"\n❌ ERROR: Status {response.status_code}")
            try:
                error_detail = response.json()
                print(f"   Detail: {error_detail.get('detail', response.text)}")
            except:
                print(f"   Response: {response.text[:500]}")
            
    except requests.exceptions.ConnectionError:
        print("\n❌ ERROR: Could not connect to server.")
        print("   Make sure the FastAPI server is running:")
        print("   cd backend && uvicorn app.main:app --reload")
    except requests.exceptions.Timeout:
        print("\n❌ ERROR: Request timed out.")
        print("   The repository may be too large. Try a smaller repository.")
    except Exception as e:
        print(f"\n❌ ERROR: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    # For testing, you can use a small repo like:
    # test_github_agent_small_repo = "https://github.com/your-username/small-test-repo"
    
    test_github_agent()
