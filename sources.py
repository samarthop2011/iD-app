#!/usr/bin/env python3
"""
iDRAC IP Sources Module - 32+ Sources
Synced with config.py
"""

import asyncio
import aiohttp
import re
import ipaddress
from typing import List, Set, Dict
from urllib.parse import quote_plus

# Import from config
from config import SOURCE_CONFIG, get_user_agent

class IPSourceManager:
    def __init__(self):
        self.session = None
        self.known_ips: Set[str] = set()
        
    async def init_session(self):
        connector = aiohttp.TCPConnector(limit=50, ssl=False)
        timeout = aiohttp.ClientTimeout(total=SOURCE_CONFIG['timeout'])
        self.session = aiohttp.ClientSession(connector=connector, timeout=timeout)
        
    async def close(self):
        if self.session:
            await self.session.close()
    
    def is_new(self, ip: str) -> bool:
        return ip not in self.known_ips
    
    async def mark(self, ip: str):
        self.known_ips.add(ip)
    
    def extract_ips(self, text: str) -> List[str]:
        if not text:
            return []
        pattern = r'\b(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\b'
        ips = []
        for match in re.finditer(pattern, text):
            ip = match.group()
            try:
                ip_obj = ipaddress.ip_address(ip)
                if not ip_obj.is_private and not ip_obj.is_loopback:
                    if self.is_new(ip):
                        ips.append(ip)
                        self.known_ips.add(ip)
            except:
                pass
        return ips
    
    async def fetch(self, url: str) -> str:
        try:
            headers = {'User-Agent': get_user_agent()}
            await asyncio.sleep(SOURCE_CONFIG['delay_between'])
            async with self.session.get(url, headers=headers, 
                                      timeout=aiohttp.ClientTimeout(total=10)) as resp:
                if resp.status == 200:
                    return await resp.text()
        except:
            pass
        return ""
    
    # ═══════════════════════════════════════════════════════════════════════════
    # 32+ SOURCES
    # ═══════════════════════════════════════════════════════════════════════════
    
    async def source_shodan_idrac7(self) -> List[str]:
        text = await self.fetch("https://www.shodan.io/search?query=title%3A%22iDRAC7%22")
        return self.extract_ips(text)
    
    async def source_shodan_idrac8(self) -> List[str]:
        text = await self.fetch("https://www.shodan.io/search?query=title%3A%22iDRAC8%22")
        return self.extract_ips(text)
    
    async def source_censys_idrac(self) -> List[str]:
        text = await self.fetch("https://search.censys.io/search?resource=hosts&q=iDRAC")
        return self.extract_ips(text)
    
    async def source_fofa_idrac7(self) -> List[str]:
        text = await self.fetch("https://en.fofa.info/result?qbase64=dGl0bGU9ImlEUkFDNyI=")
        return self.extract_ips(text)
    
    async def source_fofa_idrac8(self) -> List[str]:
        text = await self.fetch("https://en.fofa.info/result?qbase64=dGl0bGU9ImlEUkFDOCI=")
        return self.extract_ips(text)
    
    async def source_zoomeye(self) -> List[str]:
        text = await self.fetch("https://www.zoomeye.org/searchResult?q=iDRAC")
        return self.extract_ips(text)
    
    async def source_onyphe(self) -> List[str]:
        text = await self.fetch("https://www.onyphe.io/search?q=iDRAC")
        return self.extract_ips(text)
    
    async def source_netlas(self) -> List[str]:
        text = await self.fetch("https://app.netlas.io/responses/?q=iDRAC")
        return self.extract_ips(text)
    
    async def source_spyse(self) -> List[str]:
        text = await self.fetch("https://spyse.com/search?q=iDRAC")
        return self.extract_ips(text)
    
    async def source_greynoise(self) -> List[str]:
        text = await self.fetch("https://viz.greynoise.io/query?gnql=iDRAC")
        return self.extract_ips(text)
    
    async def source_binaryedge(self) -> List[str]:
        text = await self.fetch("https://app.binaryedge.io/services/query?query=iDRAC")
        return self.extract_ips(text)
    
    async def source_crt_sh(self) -> List[str]:
        all_ips = []
        for kw in ['idrac7', 'idrac8', 'dell-idrac']:
            text = await self.fetch(f"https://crt.sh/?q={kw}")
            if text:
                all_ips.extend(self.extract_ips(text))
        return all_ips
    
    async def source_pastebin(self) -> List[str]:
        text = await self.fetch("https://pastebin.com/search?q=iDRAC")
        return self.extract_ips(text)
    
    async def source_github_gist(self) -> List[str]:
        text = await self.fetch("https://gist.github.com/search?q=iDRAC")
        return self.extract_ips(text)
    
    async def source_github_code(self) -> List[str]:
        text = await self.fetch("https://github.com/search?q=iDRAC&type=code")
        return self.extract_ips(text)
    
    async def source_reddit(self) -> List[str]:
        text = await self.fetch("https://www.reddit.com/search/?q=iDRAC&type=posts")
        return self.extract_ips(text)
    
    async def source_stackoverflow(self) -> List[str]:
        text = await self.fetch("https://stackoverflow.com/search?q=iDRAC")
        return self.extract_ips(text)
    
    async def source_hackernews(self) -> List[str]:
        text = await self.fetch("https://hn.algolia.com/?q=iDRAC")
        return self.extract_ips(text)
    
    async def source_exploitdb(self) -> List[str]:
        text = await self.fetch("https://www.exploit-db.com/?q=iDRAC")
        return self.extract_ips(text)
    
    async def source_packetstorm(self) -> List[str]:
        text = await self.fetch("https://packetstormsecurity.com/search/?q=iDRAC")
        return self.extract_ips(text)
    
    async def source_bing_idrac7(self) -> List[str]:
        text = await self.fetch("https://www.bing.com/search?q=title%3A%22iDRAC7%22")
        return self.extract_ips(text)
    
    async def source_bing_idrac8(self) -> List[str]:
        text = await self.fetch("https://www.bing.com/search?q=title%3A%22iDRAC8%22")
        return self.extract_ips(text)
    
    async def source_duckduckgo(self) -> List[str]:
        text = await self.fetch("https://html.duckduckgo.com/html/?q=iDRAC+7+8")
        return self.extract_ips(text)
    
    async def source_yahoo(self) -> List[str]:
        text = await self.fetch("https://search.yahoo.com/search?p=iDRAC+7+8")
        return self.extract_ips(text)
    
    async def source_startpage(self) -> List[str]:
        text = await self.fetch("https://www.startpage.com/sp/search?query=iDRAC+login")
        return self.extract_ips(text)
    
    async def source_ecosia(self) -> List[str]:
        text = await self.fetch("https://www.ecosia.org/search?q=iDRAC+7")
        return self.extract_ips(text)
    
    async def source_qwant(self) -> List[str]:
        text = await self.fetch("https://www.qwant.com/?q=iDRAC+8")
        return self.extract_ips(text)
    
    async def source_vulners(self) -> List[str]:
        text = await self.fetch("https://vulners.com/search?query=iDRAC")
        return self.extract_ips(text)
    
    async def source_rapid7(self) -> List[str]:
        text = await self.fetch("https://www.rapid7.com/db/?q=iDRAC")
        return self.extract_ips(text)
    
    async def source_metasploit(self) -> List[str]:
        text = await self.fetch("https://www.rapid7.com/db/?q=iDRAC&type=metasploit")
        return self.extract_ips(text)
    
    async def source_nmap_scripts(self) -> List[str]:
        text = await self.fetch("https://seclists.org/nmap-dev/")
        return self.extract_ips(text)
    
    async def source_securityfocus(self) -> List[str]:
        text = await self.fetch("https://www.securityfocus.com/search")
        return self.extract_ips(text)
    
    async def source_seebug(self) -> List[str]:
        text = await self.fetch("https://seebug.org/search/iDRAC")
        return self.extract_ips(text)
    
    async def source_twitter_nitter(self) -> List[str]:
        text = await self.fetch("https://nitter.net/search?f=tweets&q=iDRAC")
        return self.extract_ips(text)
    
    # ═══════════════════════════════════════════════════════════════════════════
    # RUN ALL SOURCES
    # ═══════════════════════════════════════════════════════════════════════════
    
    async def scrape_all(self, callback=None) -> List[Dict]:
        """Run all 32 sources"""
        sources = [
            self.source_shodan_idrac7, self.source_shodan_idrac8,
            self.source_censys_idrac, self.source_fofa_idrac7, self.source_fofa_idrac8,
            self.source_zoomeye, self.source_onyphe, self.source_netlas,
            self.source_spyse, self.source_greynoise, self.source_binaryedge,
            self.source_crt_sh, self.source_pastebin, self.source_github_gist,
            self.source_github_code, self.source_reddit, self.source_stackoverflow,
            self.source_hackernews, self.source_exploitdb, self.source_packetstorm,
            self.source_bing_idrac7, self.source_bing_idrac8, self.source_duckduckgo,
            self.source_yahoo, self.source_startpage, self.source_ecosia,
            self.source_qwant, self.source_vulners, self.source_rapid7,
            self.source_metasploit, self.source_nmap_scripts, self.source_securityfocus,
        ]
        
        all_ips = []
        batch_size = SOURCE_CONFIG.get('batch_size', 5)
        
        for i in range(0, len(sources), batch_size):
            batch = sources[i:i+batch_size]
            results = await asyncio.gather(*[s() for s in batch], return_exceptions=True)
            for result in results:
                if isinstance(result, list):
                    for ip in result:
                        if self.is_new(ip):
                            all_ips.append(ip)
                            await self.mark(ip)
                    if callback:
                        callback(len(result))
            await asyncio.sleep(SOURCE_CONFIG['delay_between'])
        
        return [{'ip': ip, 'port': 443} for ip in all_ips]
