#!/usr/bin/env python3
"""Test script for the /api/v1/analyze/batch endpoint - whole repository analysis."""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent))

import requests
import json
import os

# Get test files directory
TEST_DIR = Path(__file__).resolve().parent / "test_files"
CODE_DIR = TEST_DIR / "code"
DOC_DIR = TEST_DIR / "docs"


def test_batch_endpoint():
    """Test the /api/v1/analyze/batch endpoint with multiple files."""
    base_url = "http://localhost:8000"
    endpoint = f"{base_url}/api/v1/analyze/batch"
    
    print("=" * 70)
    print("TESTING BATCH ENDPOINT - Whole Repository Analysis")
    print("=" * 70)
    
    # Read code files
    code_files_list = []
    code_file_paths = list(CODE_DIR.glob("*.py"))
    
    if not code_file_paths:
        print(f"❌ No code files found in {CODE_DIR}")
        return
    
    for file_path in code_file_paths:
        try:
            with open(file_path, "rb") as f:
                content = f.read()
                code_files_list.append(
                    ("code_files", (file_path.name, content, "text/x-python"))
                )
        except Exception as e:
            print(f"⚠️  Error reading {file_path}: {e}")
            continue
    
    # Read doc files
    doc_files_list = []
    doc_file_paths = list(DOC_DIR.glob("*.md"))
    
    if not doc_file_paths:
        print(f"❌ No doc files found in {DOC_DIR}")
        return
    
    for file_path in doc_file_paths:
        try:
            with open(file_path, "rb") as f:
                content = f.read()
                doc_files_list.append(
                    ("doc_files", (file_path.name, content, "text/markdown"))
                )
        except Exception as e:
            print(f"⚠️  Error reading {file_path}: {e}")
            continue
    
    # Combine all files
    files = code_files_list + doc_files_list
    
    print(f"\n📁 Uploading files:")
    code_names = [f[1][0] for f in code_files_list]
    doc_names = [f[1][0] for f in doc_files_list]
    print(f"   Code files: {', '.join(code_names)} ({len(code_files_list)} files)")
    print(f"   Doc files: {', '.join(doc_names)} ({len(doc_files_list)} files)")
    print(f"\n📡 Sending request to: {endpoint}")
    
    try:
        response = requests.post(
            endpoint,
            files=files,
            timeout=120  # Allow more time for batch processing
        )
        
        print(f"\n✅ Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            
            print("\n" + "=" * 70)
            print("RESULTS:")
            print("=" * 70)
            
            print(f"\n📊 Summary:")
            print(f"   Status: {result.get('status')}")
            print(f"   Summary: {result.get('summary')}")
            
            metadata = result.get('metadata', {})
            print(f"\n📈 Statistics:")
            print(f"   Trust Score: {metadata.get('trust_score')}%")
            print(f"   Total Functions: {metadata.get('total_functions')}")
            print(f"   Verified: {metadata.get('verified')}")
            print(f"   Average Confidence: {metadata.get('average_confidence', 0)}%")
            
            print(f"\n📁 Files Analyzed:")
            print(f"   Code Files: {metadata.get('code_files_analyzed', 0)}")
            print(f"      - {', '.join(metadata.get('code_file_names', []))}")
            print(f"   Doc Files: {metadata.get('doc_files_analyzed', 0)}")
            print(f"      - {', '.join(metadata.get('doc_file_names', []))}")
            
            print(f"\n🔧 Functions Found:")
            print(f"   Code Functions: {metadata.get('code_functions_count', 0)}")
            print(f"   Doc Functions: {metadata.get('doc_functions_count', 0)}")
            
            method_stats = metadata.get('method_stats', {})
            if method_stats:
                print(f"\n🤖 ML Methods Used:")
                for method, count in method_stats.items():
                    print(f"   - {method}: {count} functions")
            
            discrepancies = result.get('discrepancies', [])
            print(f"\n⚠️  Discrepancies: {len(discrepancies)}")
            
            if discrepancies:
                print(f"\n📋 Issue Details:")
                for i, disc in enumerate(discrepancies[:10], 1):  # Show first 10
                    severity = disc.get('severity', 'unknown').upper()
                    desc = disc.get('description', 'No description')
                    func = disc.get('location', 'unknown')
                    code_snip = disc.get('code_snippet', 'N/A')
                    doc_snip = disc.get('doc_snippet', 'N/A')
                    
                    print(f"   {i}. [{severity}] {desc}")
                    if code_snip and code_snip != 'N/A':
                        print(f"      Code: {code_snip[:60]}")
                    if doc_snip and doc_snip != 'N/A':
                        print(f"      Docs: {doc_snip[:60]}")
                
                if len(discrepancies) > 10:
                    print(f"   ... and {len(discrepancies) - 10} more")
            else:
                print("\n✨ No discrepancies found - all documentation matches code!")
            
            print("\n" + "=" * 70)
            print("✅ Batch analysis completed successfully!")
            print("=" * 70)
            
        else:
            print(f"\n❌ ERROR: Status {response.status_code}")
            print(response.text)
            
    except requests.exceptions.ConnectionError:
        print("\n❌ ERROR: Could not connect to server.")
        print("   Make sure the FastAPI server is running:")
        print("   cd backend && uvicorn app.main:app --reload")
    except Exception as e:
        print(f"\n❌ ERROR: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    test_batch_endpoint()
