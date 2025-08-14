#!/usr/bin/env python3
"""
Script to review frontend styling compliance with PICO CSS + Shad4FastHTML rules
"""

import re
import os

def analyze_file(filepath):
    """Analyze a file for styling compliance"""
    with open(filepath, 'r') as f:
        content = f.read()
    
    issues = []
    
    # Check for PICO violations (using Shad4FastHTML where PICO should be used)
    pico_violations = [
        (r'cls="container-\w+"', 'Use PICO .container instead of custom container classes'),
        (r'cls="grid-\w+"', 'Use PICO .grid instead of custom grid classes'),
        (r'<H[1-6][^>]*cls="[^"]*text-\w+', 'Use PICO typography, not custom text classes for headings'),
        (r'<P[^>]*cls="[^"]*text-\w+', 'Use PICO typography, not custom text classes for paragraphs'),
    ]
    
    # Check for Shad4FastHTML violations (using custom styling where Shad4FastHTML should be used)
    shadcn_violations = [
        (r'Button\([^)]*cls="[^"]*bg-\w+[^"]*"[^)]*\)', 'Button should use Shad4FastHTML styling, not custom bg classes'),
        (r'Input\([^)]*cls="[^"]*btn[^"]*"', 'Input should not use btn classes'),
        (r'cls="[^"]*button-\w+', 'Use Shad4FastHTML Button component instead of custom button classes'),
        (r'style="[^"]*background:\s*#[^"]*"', 'Use Shad4FastHTML variants instead of inline background styles'),
    ]
    
    # Check for proper PICO usage
    pico_good = [
        (r'cls="container"', 'Good: Using PICO container'),
        (r'cls="grid"', 'Good: Using PICO grid'),
        (r'<H[1-6](?![^>]*cls=)', 'Good: Using PICO typography for headings'),
        (r'<P(?![^>]*cls=)', 'Good: Using PICO typography for paragraphs'),
    ]
    
    # Check for proper Shad4FastHTML usage
    shadcn_good = [
        (r'Button\([^)]*cls="[^"]*inline-flex[^"]*"', 'Good: Using Shad4FastHTML Button styling'),
        (r'Input\([^)]*cls="[^"]*border border-input[^"]*"', 'Good: Using Shad4FastHTML Input styling'),
        (r'Card\(', 'Good: Using Shad4FastHTML Card component'),
    ]
    
    line_num = 0
    for line in content.split('\n'):
        line_num += 1
        
        # Check for violations
        for pattern, message in pico_violations + shadcn_violations:
            if re.search(pattern, line, re.IGNORECASE):
                issues.append({
                    'line': line_num,
                    'type': 'violation',
                    'message': message,
                    'code': line.strip()[:100]
                })
    
    return issues

def main():
    files_to_check = [
        'app.py',
        'components/layout.py',
        'components/navbar.py',
        'components/metrics_page.py',
        'components/ui.py'
    ]
    
    print("=== FRONTEND STYLING COMPLIANCE REVIEW ===\n")
    
    all_issues = []
    
    for filepath in files_to_check:
        if os.path.exists(filepath):
            print(f"📁 Analyzing {filepath}...")
            issues = analyze_file(filepath)
            
            if issues:
                print(f"  ❌ Found {len(issues)} styling issues:")
                for issue in issues:
                    print(f"    Line {issue['line']}: {issue['message']}")
                    print(f"      Code: {issue['code']}")
                all_issues.extend([(filepath, issue) for issue in issues])
            else:
                print(f"  ✅ No styling violations found")
            print()
    
    print(f"📊 SUMMARY:")
    print(f"  Total files checked: {len(files_to_check)}")
    print(f"  Total styling issues: {len(all_issues)}")
    
    if all_issues:
        print(f"\n🔧 ISSUES TO FIX:")
        for filepath, issue in all_issues:
            print(f"  {filepath}:{issue['line']} - {issue['message']}")

if __name__ == "__main__":
    main()
