#!/usr/bin/env python3
"""
iDRAC 7/8 Mass Scanner Module - SYNCED with config.py
Phase 1: IP Discovery & Validation
"""

import asyncio
import aiohttp
import re
import ipaddress
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime

# Import from config
from config import (
    SCANNER_CONFIG,
    CVE20181207Payload,
    VULNERABLE_FIRMWARE,
    is_vulnerable_firmware,
    get_user_agent
)

@dataclass
class iDRACTarget:
    ip: str
    port: int = 443
    idrac_version: Optional[str] = None
    firmware_version: Optional[str] = None
    is_vulnerable: bool = False
    cve_list: List[str] = field(default_factory=list)
    country: Optional[str] = None
    city: Optional[str] = None
    org: Optional[str] = None
    isp: Optional[str] = None
    discovered_at: Optional[str] = field(default_factory=lambda: datetime.now().isoformat())

class iDRACScanner:
    def __init__(self, max_concurrent: int = None):
        self.max_concurrent = max_concurrent or SCANNER_CONFIG['max_concurrent']
        self.session = None
        self.semaphore = None
        self.timeout = SCANNER_CONFIG['timeout']
        
    async def init_session(self):
        connector = aiohttp.TCPConnector(limit=self.max_concurrent, ssl=False)
        timeout = aiohttp.ClientTimeout(total=self.timeout)
        self.session = aiohttp.ClientSession(connector=connector, timeout=timeout)
        self.semaphore = asyncio.Semaphore(self.max_concurrent)
        
    async def close(self):
        if self.session:
            await self.session.close()
            
    async def check_idrac(self, ip: str, port: int = 443) -> Optional[iDRACTarget]:
        """Check if target is iDRAC 7/8 using config signatures"""
        async with self.semaphore:
            try:
                # Try endpoints from config
                for endpoint in SCANNER_CONFIG['endpoints']:
                    url = f"https://{ip}:{port}{endpoint}"
                    async with self.session.get(
                        url, 
                        timeout=aiohttp.ClientTimeout(total=self.timeout),
                        headers={'User-Agent': get_user_agent()}
                    ) as resp:
                        
                        if resp.status not in [200, 401, 403]:
                            continue
                        
                        text = await resp.text()
                        text_lower = text.lower()
                        
                        # Check general iDRAC signature from config
                        if not any(sig.lower() in text_lower for sig in SCANNER_CONFIG['signatures']['general']):
                            continue
                        
                        target = iDRACTarget(ip=ip, port=port)
                        
                        # Detect version using config signatures
                        for ver, sigs in SCANNER_CONFIG['signatures'].items():
                            if ver == 'general':
                                continue
                            if any(sig.lower() in text_lower for sig in sigs):
                                target.idrac_version = ver[-1]  # '7' or '8'
                                break
                        
                        if not target.idrac_version:
                            return None  # Not iDRAC 7 or 8
                        
                        # Get firmware using config patterns
                        for pattern in SCANNER_CONFIG['firmware_patterns']:
                            match = re.search(pattern, text, re.I)
                            if match:
                                target.firmware_version = match.group(1)
                                break
                        
                        # Check vulnerability using config
                        target = await self._check_vulnerability(target)
                        
                        # Get geolocation
                        geo = await self._get_geolocation(ip)
                        target.country = geo.get('country')
                        target.city = geo.get('city')
                        target.org = geo.get('org')
                        target.isp = geo.get('isp')
                        
                        return target
                        
            except Exception as e:
                return None
    
    async def _check_vulnerability(self, target: iDRACTarget) -> iDRACTarget:
        """Check CVE-2018-1207 vulnerability using config"""
        # Check endpoints from config
        for endpoint in SCANNER_CONFIG['vuln_endpoints']:
            try:
                async with self.session.get(
                    f"https://{target.ip}:{target.port}{endpoint}",
                    timeout=aiohttp.ClientTimeout(total=5)
                ) as resp:
                    if resp.status in [200, 405, 500, 403]:
                        target.is_vulnerable = True
                        target.cve_list.append('CVE-2018-1207')
                        break
            except:
                pass
        
        # Check firmware version from config
        if target.firmware_version and target.idrac_version:
            if is_vulnerable_firmware(target.firmware_version, target.idrac_version):
                target.is_vulnerable = True
                if 'CVE-2018-1207' not in target.cve_list:
                    target.cve_list.append('CVE-2018-1207')
        
        return target
    
    async def _get_geolocation(self, ip: str) -> Dict:
        """Get IP geolocation"""
        try:
            async with self.session.get(
                f"http://ip-api.com/json/{ip}?fields=country,city,org,isp",
                timeout=aiohttp.ClientTimeout(total=5)
            ) as resp:
                if resp.status == 200:
                    return await resp.json()
        except:
            pass
        return {}
    
    async def scan_cidr(self, cidr: str, callback=None) -> List[iDRACTarget]:
        """Scan CIDR range with limit from config"""
        try:
            network = ipaddress.ip_network(cidr, strict=False)
            hosts = [str(ip) for ip in network.hosts()]
            
            # Limit from config
            limit = SCANNER_CONFIG['cidr_limit']
            if len(hosts) > limit:
                hosts = hosts[:limit]
            
            return await self.scan_ip_list(hosts, callback)
        except Exception as e:
            return []
    
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
    
    async def validate_single(self, ip: str, port: int = 443) -> Optional[iDRACTarget]:
        """Validate single IP"""
        return await self.check_idrac(ip, port)
    
    def get_stats(self, targets: List[iDRACTarget]) -> Dict:
        """Get statistics from targets"""
        stats = {
            'total': len(targets),
            'idrac7': len([t for t in targets if t.idrac_version == '7']),
            'idrac8': len([t for t in targets if t.idrac_version == '8']),
            'vulnerable': len([t for t in targets if t.is_vulnerable]),
            'with_firmware': len([t for t in targets if t.firmware_version]),
        }
        return stats

# Standalone test
if __name__ == "__main__":
    async def test():
        scanner = iDRACScanner()
        await scanner.init_session()
        print(f"[+] Scanner initialized with config:")
        print(f"    Max concurrent: {scanner.max_concurrent}")
        print(f"    Timeout: {scanner.timeout}")
        print(f"    CIDR limit: {SCANNER_CONFIG['cidr_limit']}")
        await scanner.close()
    
    asyncio.run(test())
