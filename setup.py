import os
import subprocess
import sys

# List of required libraries
required_libraries = [
    "pandas",
    "openpyxl",
    "playwright",
    "g4f",
    "playwright-stealth",  # Added playwright-stealth
]

# Install libraries
def install_libraries():
    print("Installing required libraries...")
    for library in required_libraries:
        subprocess.check_call([sys.executable, "-m", "pip", "install", library])

# Install Playwright browsers
def install_playwright_browsers():
    print("Installing Playwright browsers...")
    subprocess.check_call([sys.executable, "-m", "playwright", "install"])

# Validate installation
def validate_installation():
    print("\nValidating installations...\n")
    try:
        # Check if libraries are installed
        for library in required_libraries[:-1]:
            __import__(library)

        # Check playwright-stealth specifically
        from playwright_stealth import stealth_sync
        print("All required libraries, including stealth_sync, are successfully installed.")
    except ImportError as e:
        print(f"Error during validation: {e}")
        sys.exit(1)

# Main setup function
def main():
    install_libraries()
    install_playwright_browsers()
    validate_installation()

if __name__ == "__main__":
    main()
