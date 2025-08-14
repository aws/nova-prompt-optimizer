#!/usr/bin/env python3
"""
Script to find and fix all buttons to use proper shadcn styling
"""

import re
import os

# Shadcn button classes
SHADCN_PRIMARY = "inline-flex items-center justify-center whitespace-nowrap rounded-md text-sm font-medium ring-offset-background transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 bg-primary text-primary-foreground hover:bg-primary/90 h-10 px-4 py-2"
SHADCN_OUTLINE = "inline-flex items-center justify-center whitespace-nowrap rounded-md text-sm font-medium ring-offset-background transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 border border-input bg-background hover:bg-accent hover:text-accent-foreground h-10 px-4 py-2"
SHADCN_DESTRUCTIVE = "inline-flex items-center justify-center whitespace-nowrap rounded-md text-sm font-medium ring-offset-background transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 bg-destructive text-destructive-foreground hover:bg-destructive/90 h-10 px-4 py-2"

def find_buttons_in_file(filepath):
    """Find all Button() calls in a file"""
    with open(filepath, 'r') as f:
        content = f.read()
    
    # Find Button( patterns
    button_pattern = r'Button\([^)]*\)'
    matches = re.finditer(button_pattern, content, re.MULTILINE | re.DOTALL)
    
    buttons = []
    for match in matches:
        start_line = content[:match.start()].count('\n') + 1
        button_text = match.group()
        buttons.append((start_line, button_text))
    
    return buttons

def analyze_button(button_text):
    """Analyze if button has proper shadcn styling"""
    # Check if it has shadcn classes
    has_shadcn = "inline-flex items-center justify-center" in button_text
    
    # Check for old patterns that need fixing
    needs_fix = any([
        'variant="primary"' in button_text,
        'variant="outline"' in button_text,
        'variant="destructive"' in button_text,
        'style="background:' in button_text,
        'cls="w-full"' in button_text and not has_shadcn,
        'cls="btn' in button_text,
        'cls="button-' in button_text
    ])
    
    return has_shadcn, needs_fix

def main():
    files_to_check = [
        'app.py',
        'components/layout.py',
        'components/navbar.py', 
        'components/metrics_page.py'
    ]
    
    all_buttons = []
    
    for filepath in files_to_check:
        if os.path.exists(filepath):
            buttons = find_buttons_in_file(filepath)
            for line_num, button_text in buttons:
                has_shadcn, needs_fix = analyze_button(button_text)
                all_buttons.append({
                    'file': filepath,
                    'line': line_num,
                    'text': button_text[:100] + '...' if len(button_text) > 100 else button_text,
                    'has_shadcn': has_shadcn,
                    'needs_fix': needs_fix
                })
    
    print("=== BUTTON ANALYSIS REPORT ===\n")
    
    print("✅ BUTTONS WITH PROPER SHADCN STYLING:")
    for btn in all_buttons:
        if btn['has_shadcn']:
            print(f"  {btn['file']}:{btn['line']} - {btn['text']}")
    
    print("\n❌ BUTTONS THAT NEED FIXING:")
    for btn in all_buttons:
        if btn['needs_fix'] and not btn['has_shadcn']:
            print(f"  {btn['file']}:{btn['line']} - {btn['text']}")
    
    print(f"\n📊 SUMMARY:")
    print(f"  Total buttons found: {len(all_buttons)}")
    print(f"  With shadcn styling: {sum(1 for b in all_buttons if b['has_shadcn'])}")
    print(f"  Need fixing: {sum(1 for b in all_buttons if b['needs_fix'] and not b['has_shadcn'])}")

if __name__ == "__main__":
    main()
