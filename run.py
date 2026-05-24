#!/usr/bin/env python3
# Launch script for Element Escape: Twin Spirits
# This script provides an easy way to start the game or run tests.
# Date: May 2026

import subprocess
import sys
import os

def print_menu():
    """Display the main menu."""
    print("\n" + "=" * 50)
    print("Element Escape: Twin Spirits")
    print("=" * 50)
    print("\nSelect an option:\n")
    print("1. Play the Game")
    print("2. Run Unit Tests")
    print("3. View README")
    print("4. Exit")
    print("\n" + "=" * 50)

def run_game():
    """Run the game."""
    print("\nStarting the game...\n")
    subprocess.run([sys.executable, "main.py"])

def run_tests():
    """Run the unit tests."""
    print("\nRunning unit tests...\n")
    result = subprocess.run([sys.executable, "-m", "unittest", "test_main.py", "-v"])
    if result.returncode == 0:
        print("\n✓ All tests passed!")
    else:
        print("\n✗ Some tests failed. Check the output above.")

def view_readme():
    """Display the README file."""
    readme_path = "README.md"
    if os.path.exists(readme_path):
        with open(readme_path, 'r') as f:
            print(f.read())
    else:
        print("README.md not found!")

def main():
    """Main launch menu."""
    while True:
        print_menu()
        choice = input("Enter your choice (1-4): ").strip()

        if choice == '1':
            run_game()
        elif choice == '2':
            run_tests()
        elif choice == '3':
            view_readme()
        elif choice == '4':
            print("\nThank you for playing Element Escape: Twin Spirits!")
            break
        else:
            print("\nInvalid choice. Please try again.")

if __name__ == "__main__":
    main()
