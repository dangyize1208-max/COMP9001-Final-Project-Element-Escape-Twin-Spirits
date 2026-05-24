#!/bin/bash
# Launch script for Element Escape: Twin Spirits
# This shell script provides an easy way to start the game
# Date: May 2026

# Function to display the menu
show_menu() {
    echo ""
    echo "=================================================="
    echo "Element Escape: Twin Spirits"
    echo "=================================================="
    echo ""
    echo "Select an option:"
    echo ""
    echo "1. Play the Game"
    echo "2. Run Unit Tests"
    echo "3. View README"
    echo "4. Exit"
    echo ""
    echo "=================================================="
}

# Check if Python 3 is available
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed or not in PATH"
    exit 1
fi

# Main loop
while true; do
    show_menu
    read -p "Enter your choice (1-4): " choice

    case $choice in
        1)
            echo ""
            echo "Starting the game..."
            echo ""
            python3 main.py
            ;;
        2)
            echo ""
            echo "Running unit tests..."
            echo ""
            python3 -m unittest test_main.py -v
            ;;
        3)
            if [ -f "README.md" ]; then
                cat README.md
            else
                echo "README.md not found!"
            fi
            ;;
        4)
            echo ""
            echo "Thank you for playing Element Escape: Twin Spirits!"
            exit 0
            ;;
        *)
            echo ""
            echo "Invalid choice. Please try again."
            ;;
    esac
done
