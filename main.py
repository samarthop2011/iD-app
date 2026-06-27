#!/usr/bin/env python3
"""
iDRAC Mass Exploiter Launcher
"""

import sys

def check_modules():
    try:
        import tkinter
        print("[✓] tkinter OK")
    except:
        print("[!] Install tkinter: sudo apt-get install python3-tk")
        return False
    
    try:
        import aiohttp
        print("[✓] aiohttp OK")
    except:
        print("[!] Install: pip install aiohttp")
        return False
    
    try:
        import config
        print("[✓] config.py OK")
    except Exception as e:
        print(f"[!] config.py error: {e}")
        return False
    
    return True

def main():
    print(f"""
╔══════════════════════════════════════════════════════════════════════════════╗
║  iDRAC 7/8 Mass Exploiter v14.0 - Launcher                                   ║
╚══════════════════════════════════════════════════════════════════════════════╝
    """)
    
    if not check_modules():
        sys.exit(1)
    
    print("[*] Starting GUI...\n")
    
    from gui import main as gui_main
    gui_main()

if __name__ == "__main__":
    main()
