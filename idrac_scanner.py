#!/usr/bin/env python3
"""
iDRAC 7/8 Mass Scanner Module
Phase 1: IP Discovery & Validation
"""

import asyncio
import aiohttp
import ipaddress
import re
import json
from typing import Dict, List, Optional, Set
from dataclasses import dataclass
from datetime import datetime

@dataclass
class iDRACTarget:
    ip: str
    port: int = 443
    idrac_version: Optional[str] = None
    firmware_version: Optional[str] = None
    is_vulnerable: bool = False
    cve_list: List[str] = None
    country: Optional[str] = None
    city: Optional[str] = None
    org: Optional[str] = None
    discovered_at: Optional[str] = None
    
    def __post_init__(self):
        if self.cve_list is None:
            self.cve_list = []
        if self.discovered_at is None:
            self.discovered_at = datetime.now().isoformat()

class iDRACScanner:
    def __init__(self, max_concurrent: int = 100):
        self.max_concurrent = max_concurrent
        self.session = None
        self.semaphore = None
        
    async def init_session(self):
        connector = aiohttp.TCPConnector(limit=max_concurrent, ssl=False)
        timeout = aiohttp.ClientTimeout(total=15)
        self.session = aiohttp.ClientSession(connector=connector, timeout=timeout)
        self.semaphore = asyncio.Semaphore(max_concurrent)
        
    async def close(self):
        if self.session:
            await self.session.close()
            
    async def check_idrac(self, ip: str, port: int = 443) -> Optional[iDRACTarget]:
        """Check if target is iDRAC 7/8"""
        async with self.semaphore:
            try:
                url = f"https://{ip}:{port}/login.html"
                async with self.session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as resp:
                    if resp.status not in [200, 401, 403]:
                        return None
                    
                    text = await resp.text()
                    text_lower = text.lower()
                    
                    if 'idrac' not in text_lower:
                        return None
                    
                    target = iDRACTarget(ip=ip, port=port)
                    
                    # Detect version
                    if 'idrac 7' in text_lower or 'idrac7' in text_lower:
                        target.idrac_version = '7'
                    elif 'idrac 8' in text_lower or 'idrac8' in text_lower:
                        target.idrac_version = '8'
                    else:
                        return None  # Not 7 or 8
                    
                    # Get firmware version
                    fw_match = re.search(r'FirmwareVersion["\']?\s*[:=]\s*["\']?([\d.]+)', text, re.I)
                    if fw_match:
                        target.firmware_version = fw_match.group(1)
                    
                    # Check vulnerability
                    target = await self._check_vulnerability(target)
                    
                    # Get geolocation
                    geo = await self._get_geolocation(ip)
                    target.country = geo.get('country')
                    target.city = geo.get('city')
                    target.org = geo.get('org')
                    
                    return target
                    
            except Exception as e:
                return None
    
    async def _check_vulnerability(self, target: iDRACTarget) -> iDRACTarget:
        """Check for CVE-2018-1207"""
        VULNERABLE_FIRMWARE = {
            '7': ['1.30.', '1.40.', '1.50.', '1.57.', '1.60.', '1.65.', '1.66.', '1.70.', '1.75.', '1.80.'],
            '8': ['2.00.', '2.10.', '2.21.', '2.30.', '2.40.', '2.50.', '2.52.', '2.60.', '2.61.', '2.70.']
        }
        
        try:
            # Check putfile endpoint
            async with self.session.get(f"https://{target.ip}:{target.port}/cgi-bin/putfile", 
                                      timeout=aiohttp.ClientTimeout(total=5)) as resp:
                if resp.status in [200, 405, 500, 403]:
                    target.is_vulnerable = True
                    target.cve_list.append('CVE-2018-1207')
        except:
            pass
        
        # Check firmware version
        if target.firmware_version and target.idrac_version:
            for prefix in VULNERABLE_FIRMWARE.get(target.idrac_version, []):
                if target.firmware_version.startswith(prefix):
                    target.is_vulnerable = True
                    if 'CVE-2018-1207' not in target.cve_list:
                        target.cve_list.append('CVE-2018-1207')
                    break
        
        return target
    
    async def _get_geolocation(self, ip: str) -> Dict:
        """Get IP geolocation"""
        try:
            async with self.session.get(f"http://ip-api.com/json/{ip}?fields=country,city,org", 
                                      timeout=aiohttp.ClientTimeout(total=5)) as resp:
                if resp.status == 200:
                    return await resp.json()
        except:
            pass
        return {}
    
    async def scan_ip_list(self, ip_list: List[str], callback=None) -> List[iDRACTarget]:
        """Scan list of IPs"""
        tasks = [self.check_idrac(ip) for ip in ip_list]
        results = []
        
        for task in asyncio.as_completed(tasks):
            result = await task
            if result:
                results.append(result)
                if callback:
                    callback(result)
        
        return results
    
    async def scan_cidr(self, cidr: str, callback=None) -> List[iDRACTarget]:
        """Scan CIDR range"""
        try:
            network = ipaddress.ip_network(cidr, strict=False)
            hosts = [str(ip) for ip in network.hosts()]
            if len(hosts) > 256:  # Limit /24
                hosts = hosts[:256]
            return await self.scan_ip_list(hosts, callback)
        except:
            return []
