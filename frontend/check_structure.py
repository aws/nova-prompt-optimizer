#!/usr/bin/env python3
"""
Structure Compliance Checker
Validates that the codebase follows development rules
"""

import os
import glob

# Legacy files that are exempt from the 700-line rule
LEGACY_EXEMPT_FILES = {
    'components/layout.py',
    'database.py', 
    'sample_generator.py',
    'sdk_worker.py'
}

def check_file_sizes():
    """Check file sizes against 700-line rule (with legacy exemptions)"""
    violations = []
    compliant = []
    exempt = []
    
    # Check all Python files (except __init__.py and .venv)
    all_files = []
    for pattern in ['*.py', 'routes/*.py', 'components/*.py', 'services/*.py']:
        all_files.extend(glob.glob(pattern))
    
    # Remove duplicates and filter out __init__.py
    all_files = list(set(f for f in all_files if not f.endswith('__init__.py')))
    
    for file_path in sorted(all_files):
        try:
            lines = sum(1 for line in open(file_path))
            
            if file_path in LEGACY_EXEMPT_FILES:
                exempt.append(f"✅ {file_path}: {lines} lines (LEGACY EXEMPT)")
            elif lines > 700:
                violations.append(f"❌ {file_path}: {lines} lines (limit: 700)")
            else:
                compliant.append(f"✅ {file_path}: {lines} lines (limit: 700)")
        except Exception as e:
            print(f"⚠️  Could not read {file_path}: {e}")
    
    # Print results in order: compliant, exempt, violations
    for msg in compliant:
        print(msg)
    
    if exempt:
        print(f"\n📋 LEGACY EXEMPT FILES ({len(exempt)}):")
        for msg in exempt:
            print(f"  {msg}")
    
    return violations

def main():
    """Main compliance check"""
    print("🔍 Checking Nova Prompt Optimizer structure compliance...\n")
    print("📏 Rule: NEW files must be under 700 lines")
    print("📋 Legacy files are exempt from the rule\n")
    
    violations = check_file_sizes()
    
    if violations:
        print(f"\n🚨 NEW FILE VIOLATIONS FOUND ({len(violations)}):")
        for violation in violations:
            print(f"  {violation}")
        print("\n📖 See DEVELOPMENT_RULES.md for guidelines")
        print("💡 Extract code to new files to fix violations")
        return 1
    else:
        print(f"\n🎉 All NEW files comply with the 700-line rule!")
        print("📋 Legacy files are grandfathered and exempt")
        return 0

if __name__ == "__main__":
    exit(main())
