#!/usr/bin/env python3
import os
import shutil
import sys


def main():
    print("Building Netlify site...")

    # Create output directory
    os.makedirs("output", exist_ok=True)

    # Copy main HTML files
    html_files = ["index.html", "chatbot.html"]
    for html_file in html_files:
        if os.path.exists(html_file):
            shutil.copy(html_file, f"output/{html_file}")
            print(f"Copied {html_file} to output")

    # Copy static assets
    static_files = [
        "sookmyoung.svg",
        "img-logo01.png",
        "screenshot_today.png",
        "screenshot.png",
        "knowledge_base.js",
        "emblem-1_Color.png",
    ]
    for static_file in static_files:
        if os.path.exists(static_file):
            shutil.copy(static_file, f"output/{static_file}")
            print(f"Copied {static_file} to output")

    # Copy functions directory
    if os.path.exists("functions"):
        shutil.copytree("functions", "output/functions", dirs_exist_ok=True)
        print("Copied functions directory to output")

    print("Build completed successfully!")
    return 0


if __name__ == "__main__":
    sys.exit(main())
