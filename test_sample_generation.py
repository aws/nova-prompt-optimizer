#!/usr/bin/env python3
"""
Test script to verify the GeneratedSample fix works with complex output structures
"""

import json
import sys
import os

# Add frontend to path
sys.path.insert(0, 'frontend')

from sample_generator import GeneratedSample

def test_complex_output():
    """Test that GeneratedSample can handle complex output structures"""
    
    # Test data similar to what the LLM is returning
    test_data = {
        "input": "I'm having trouble printing documents from my laptop. It says the printer is offline, but I've checked all the connections and they seem fine. What should I do?",
        "output": {
            "interaction": {
                "user_question": "I'm having trouble printing documents from my laptop. It says the printer is offline, but I've checked all the connections and they seem fine. What should I do?",
                "support_response": "Let's work through this together. First, let's ensure that the printer is properly connected to your laptop. Since you've checked the physical connections, let's try a few more steps. On your laptop, go to the 'Devices and Printers' section in the Control Panel. Find your printer in the list, right-click on it, and select 'See what's printing.' If there are any pending print jobs, cancel them. Then, right-click on the printer again and select 'Use Printer Online' to ensure it's set to online status. If the issue persists, we might need to restart both your laptop and the printer. Would you like me to guide you through these steps?",
                "classification": {
                    "category": "hardware",
                    "subcategory": "printer_issues",
                    "confidence_score": 0.95
                },
                "reasoning": {
                    "user_issue_description": "The user reports that their printer is showing as offline despite checking physical connections.",
                    "support_approach": "The support specialist suggests checking the printer's status in the 'Devices and Printers' section, clearing any pending print jobs, and ensuring the printer is set to online. Additional steps like restarting the devices are proposed if necessary.",
                    "confidence_justification": "The classification is highly confident because the issue is clearly related to hardware (printer) and the suggested steps are standard troubleshooting for such problems."
                }
            }
        }
    }
    
    print("🧪 Testing GeneratedSample with complex output structure...")
    
    try:
        # Test the original method (should work now)
        sample1 = GeneratedSample(**test_data)
        print("✅ Direct instantiation works!")
        print(f"   Input: {sample1.input[:50]}...")
        print(f"   Output type: {type(sample1.output)}")
        
        # Test the factory method
        sample2 = GeneratedSample.from_llm_response(test_data)
        print("✅ Factory method works!")
        
        # Test string conversion
        output_string = sample2.get_output_as_string()
        print("✅ String conversion works!")
        print(f"   String length: {len(output_string)} characters")
        
        # Test dict conversion
        sample_dict = sample2.model_dump()
        print("✅ Dict conversion works!")
        print(f"   Dict keys: {list(sample_dict.keys())}")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_simple_output():
    """Test that GeneratedSample still works with simple string outputs"""
    
    test_data = {
        "input": "How do I reset my password?",
        "output": "To reset your password, go to the login page and click 'Forgot Password'."
    }
    
    print("\n🧪 Testing GeneratedSample with simple string output...")
    
    try:
        sample = GeneratedSample(**test_data)
        print("✅ Simple string output works!")
        print(f"   Output: {sample.output}")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Testing GeneratedSample fixes...\n")
    
    success1 = test_complex_output()
    success2 = test_simple_output()
    
    if success1 and success2:
        print("\n🎉 All tests passed! The fix should resolve the validation error.")
    else:
        print("\n💥 Some tests failed. Check the implementation.")