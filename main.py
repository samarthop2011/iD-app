#!/usr/bin/env python3
"""
iDRAC Mass Exploiter Launcher
Checks dependencies and launches GUI
"""

import sys
import subprocess
import os

def check_dependencies():
    """Check and install required packages"""
    required = ['requests', 'aiohttp', 'urllib3', 'tkinter']
    
    try:
        import tkinter
        print("[✓] tkinter available")
    except ImportError:
        print("[!] tkinter not found. Install with: sudo apt-get install python3-tk")
        return False
    
    for package in ['requests', 'aiohttp', 'urllib3']:
        try:
            __import__(package)
            print(f"[✓] {package} available")
        except ImportError:
            print(f"[!] Installing {package}...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])
    
    return True

def main():
    print("""
╔══════════════════════════════════════════════════════════════════════════════╗
║  iDRAC 7/8 Mass Exploiter v14.0 - Launcher                                   ║
╚══════════════════════════════════════════════════════════════════════════════╝
    """)
    
    if not check_dependencies():
        print("[!] Missing dependencies. Please install manually.")
        sys.exit(1)
    
    print("[✓] All dependencies ready")
    print("[*] Launching GUI...\n")
    
    # Launch GUI
    from gui import main as gui_main
    gui_main()

if __name__ == "__main__":
    main()