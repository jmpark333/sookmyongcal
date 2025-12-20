#!/usr/bin/env python3
import os
import shutil
import sys

def main():
    print("Building Netlify site...")

    # Create output directory
    os.makedirs("output", exist_ok=True)

    # Copy templates to output
    if os.path.exists("templates"):
        shutil.copytree("templates", "output/templates", dirs_exist_ok=True)
        print("Copied templates to output")

    # Copy index.html to output root
    if os.path.exists("templates/index.html"):
        shutil.copy("templates/index.html", "output/index.html")
        print("Copied index.html to output")

    # Copy rag_system.py to netlify/functions
    os.makedirs("netlify/functions", exist_ok=True)
    if os.path.exists("rag_system.py"):
        shutil.copy("rag_system.py", "netlify/functions/rag_system.py")
        print("Copied rag_system.py to netlify/functions")

    # Copy data directory if it exists
    if os.path.exists("data"):
        shutil.copytree("data", "netlify/functions/data", dirs_exist_ok=True)
        print("Copied data directory to netlify/functions")

    print("Build completed successfully!")
    return 0

if __name__ == "__main__":
    sys.exit(main())