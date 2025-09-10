#!/usr/bin/env python3
"""
Test script to verify screenshot.py functionality without a real device.
This creates a mock scenario to test the logic.
"""

import sys
import os
import tempfile
import shutil
from unittest.mock import Mock, patch

# Add current directory to path to import screenshot module
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from screenshot import extract_model_from_idn, generate_filename

def test_model_extraction():
    """Test model name extraction from various IDN strings."""
    
    test_cases = [
        ("KEYSIGHT TECHNOLOGIES,MSOX4254A,MY56310625,06.50.0001", "MSOX4254A"),
        ("AGILENT TECHNOLOGIES,DSO-X 3034A,MY53210234,02.50.2014", "DSO-X_3034A"),
        ("RIGOL TECHNOLOGIES,DS1054Z,DS1ZA123456789,00.04.04.SP3", "DS1054Z"),
        ("KEYSIGHT,MXR058A,MY12345678,02.04.05", "MXR058A"),
        ("", "UNKNOWN"),
        ("Incomplete string", "UNKNOWN"),
    ]
    
    print("Testing model extraction...")
    all_passed = True
    
    for idn, expected in test_cases:
        result = extract_model_from_idn(idn)
        if result == expected:
            print(f"✓ '{idn}' -> '{result}'")
        else:
            print(f"✗ '{idn}' -> '{result}' (expected '{expected}')")
            all_passed = False
    
    return all_passed

def test_filename_generation():
    """Test filename generation with different paths."""
    
    print("\nTesting filename generation...")
    
    # Create a temporary directory for testing
    with tempfile.TemporaryDirectory() as temp_dir:
        test_cases = [
            ("MSOX4254A", temp_dir, True),  # Directory path
            ("MSOX4254A", os.path.join(temp_dir, "subdir"), True),  # Non-existent directory path  
            ("MSOX4254A", ".", True),  # Current directory
            ("MSOX4254A", "", True),  # Empty path
        ]
        
        all_passed = True
        import re
        
        for model, path, should_pass in test_cases:
            try:
                filename = generate_filename(model, path)
                
                # Check filename format
                basename = os.path.basename(filename)
                pattern = rf'^{re.escape(model)}_screenshot_\d{{8}}_\d{{4}}\.png$'
                
                if re.match(pattern, basename):
                    print(f"✓ Model: '{model}', Path: '{path}' -> '{filename}'")
                else:
                    print(f"✗ Invalid filename format: '{basename}'")
                    all_passed = False
                    
            except Exception as e:
                if should_pass:
                    print(f"✗ Model: '{model}', Path: '{path}' -> Error: {e}")
                    all_passed = False
                else:
                    print(f"✓ Model: '{model}', Path: '{path}' -> Expected error: {e}")
        
        return all_passed

def test_command_line_interface():
    """Test command line interface parsing."""
    
    print("\nTesting command line interface...")
    
    # Test help functionality
    try:
        import subprocess
        result = subprocess.run([
            sys.executable, "screenshot.py", "--help"
        ], capture_output=True, text=True, cwd=os.path.dirname(os.path.abspath(__file__)))
        
        if result.returncode == 0 and "device_address" in result.stdout:
            print("✓ Help functionality works")
            return True
        else:
            print("✗ Help functionality failed")
            return False
            
    except Exception as e:
        print(f"✗ Command line test failed: {e}")
        return False

def main():
    """Run all tests."""
    
    print("Running screenshot.py tests...\n")
    
    tests = [
        test_model_extraction,
        test_filename_generation,
        test_command_line_interface,
    ]
    
    results = []
    for test in tests:
        try:
            results.append(test())
        except Exception as e:
            print(f"✗ Test {test.__name__} failed with exception: {e}")
            results.append(False)
    
    # Summary
    passed = sum(results)
    total = len(results)
    
    print(f"\n{'='*50}")
    print(f"Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("✓ All tests passed!")
        return 0
    else:
        print("✗ Some tests failed!")
        return 1

if __name__ == "__main__":
    sys.exit(main())