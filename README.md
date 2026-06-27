# 💀 iDRAC 7/8 Mass 3Xpl01t3r v1.0

Complete iDRAC exploitation toolkit with GUI, featuring CVE-2018-1207 mass exploitation.

## Features

- **Phase 1**: IP Discovery from 32+ sources (Shodan, Censys, Fofa, etc.)
- **Phase 2**: Real-time iDRAC 7/8 validation with firmware detection
- **Phase 3**: Mass exploitation using CVE-2018-1207 buffer overflow
- **Export**: Save results filtered by type (all/vulnerable/idrac7/idrac8)

## Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Run
python3 main.py
