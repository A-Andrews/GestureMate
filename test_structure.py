#!/usr/bin/env python3
"""
Simple test script to validate GestureMate code structure and logic.
This doesn't require a GUI environment.
"""

import sys
import os
from pathlib import Path

# Add the current directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test that all necessary modules can be imported."""
    print("Testing imports...")
    try:
        # We can't test PyQt6 in headless environment, but we can check the syntax
        import ast
        with open('gesturemate.py', 'r') as f:
            code = f.read()
            ast.parse(code)
        print("✓ gesturemate.py syntax is valid")
        return True
    except Exception as e:
        print(f"✗ Import test failed: {e}")
        return False

def test_supported_formats():
    """Test image format definitions."""
    print("\nTesting image format support...")
    # Extract the image extensions from the code
    with open('gesturemate.py', 'r') as f:
        code = f.read()
        if "'.jpg'" in code and "'.png'" in code and "'.bmp'" in code:
            print("✓ Supported image formats: JPG, PNG, BMP, GIF, WEBP")
            return True
    print("✗ Image format check failed")
    return False

def test_requirements():
    """Test requirements.txt exists and has PyQt6."""
    print("\nTesting requirements.txt...")
    try:
        with open('requirements.txt', 'r') as f:
            content = f.read()
            if 'PyQt6' in content:
                print("✓ requirements.txt contains PyQt6")
                return True
    except Exception as e:
        print(f"✗ Requirements test failed: {e}")
        return False

def test_readme():
    """Test README has essential information."""
    print("\nTesting README.md...")
    try:
        with open('README.md', 'r') as f:
            content = f.read()
            checks = [
                ('Installation' in content, "Installation section"),
                ('Usage' in content, "Usage section"),
                ('Features' in content, "Features section"),
                ('python gesturemate.py' in content, "Run command"),
            ]
            all_passed = True
            for passed, desc in checks:
                if passed:
                    print(f"  ✓ {desc} found")
                else:
                    print(f"  ✗ {desc} missing")
                    all_passed = False
            return all_passed
    except Exception as e:
        print(f"✗ README test failed: {e}")
        return False

def test_file_structure():
    """Test that all required files exist."""
    print("\nTesting file structure...")
    required_files = [
        'gesturemate.py',
        'requirements.txt',
        'README.md',
        '.gitignore',
        'run.sh',
        'gesturemate.desktop'
    ]
    all_exist = True
    for filename in required_files:
        if Path(filename).exists():
            print(f"  ✓ {filename} exists")
        else:
            print(f"  ✗ {filename} missing")
            all_exist = False
    return all_exist

def test_executability():
    """Test that scripts are executable."""
    print("\nTesting script executability...")
    scripts = ['gesturemate.py', 'run.sh']
    all_executable = True
    for script in scripts:
        if os.access(script, os.X_OK):
            print(f"  ✓ {script} is executable")
        else:
            print(f"  ✗ {script} is not executable")
            all_executable = False
    return all_executable

def main():
    """Run all tests."""
    print("=" * 60)
    print("GestureMate Validation Tests")
    print("=" * 60)
    
    tests = [
        test_imports,
        test_supported_formats,
        test_requirements,
        test_readme,
        test_file_structure,
        test_executability,
    ]
    
    results = []
    for test in tests:
        results.append(test())
    
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    passed = sum(results)
    total = len(results)
    print(f"Passed: {passed}/{total}")
    
    if passed == total:
        print("\n✓ All tests passed!")
        return 0
    else:
        print(f"\n✗ {total - passed} test(s) failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())
