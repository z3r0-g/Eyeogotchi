# Eyeogotchi DNS Extension  
Advanced DNS Sinkhole • Policy Engine • Threat Intelligence • Telemetry

The DNS extension provides Eyeogotchi with a full DNS security layer: sinkholing, threat‑feed ingestion, category‑based filtering, IPS‑style detections, rewrite rules, telemetry, and a Portal UI for real‑time visibility.

This document explains the architecture, configuration, API, UI, and extension layout.

---

# 📁 Directory Structure

```
extensions/dns/
  extension.yaml
  requirements.txt

  service/
    main.py
    gravity.py
    categories.py
    policy.py
    ips.py
    telemetry.py

  api/
    routes.py
    events.py

  rules/
    allowlist.txt
    blocklist.txt
    rewrites.yaml
    categories.yaml
    policy.yaml
    sources.yaml
    threat_feeds.yaml

  static/
    dns.js

  scripts/
```

---

# 🚀 Features

### ✔ DNS Sinkhole  
Blocks malicious, tracking, advertising, and policy‑violating domains.

### ✔ Gravity Updater  
Downloads, merges, deduplicates, and compiles threat feeds.

### ✔ Category Engine  
Maps domains to categories (ads, malware, adult, telemetry, etc.).

### ✔ Policy Engine  
Allows/blocks categories, enforces per‑device rules, and supports wildcard rewrites.

### ✔ IPS‑Style DNS Detection  
Detects suspicious behavior such as:
- DGA‑like domains  
- Excessive NXDOMAIN  
- Rapid‑fire queries  
- Known C2 patterns  

### ✔ Telemetry  
Real‑time event publishing to the Eyeogotchi event bus.

### ✔ Portal UI  
A dedicated DNS tab showing:
- Overview  
- Recent events  
- Per‑client activity  
- Gravity status  
- Category breakdown  

---

# 🧩 extension.yaml

```yaml
name: dns
version: 1.0.0
description: "DNS Sinkhole, Threat Intelligence, and DNS Security Layer"
enabled: true

entrypoint: "extensions.dns.service.main:get_plugin"

config:
  gravity_update_interval: 86400
  upstream_resolver: "1.1.1.1"
  enable_ips: true
  enable_categories: true
  enable_rewrites: true
```

---

# 🧠 Core Components

## `service/main.py`
The main plugin entrypoint. Responsibilities:

- Start/stop DNS server  
- Load rules + categories  
- Register event bus hooks  
- Schedule gravity updates  
- Expose health status  

## `gravity.py`
Handles:

- Downloading threat feeds  
- Merging allow/block lists  
- Deduplication  
- Compiling final sinkhole list  

## `categories.py`
Loads category definitions from `rules/categories.yaml` and maps domains to categories.

## `policy.py`
Evaluates:

- Allowlist  
- Blocklist  
- Category rules  
- Rewrite rules  
- Per‑client policies  

## `ips.py`
Performs DNS‑layer intrusion detection:

- Suspicious patterns  
- DGA heuristics  
- Query‑rate anomalies  

## `telemetry.py`
Publishes events to the Eyeogotchi event bus:

- `dns.block`  
- `dns.policy`  
- `dns.rewrite`  
- `dns.suspicious`  

---

# 📜 Rules Directory

The `rules/` folder defines all DNS behavior.

| File | Purpose |
|------|---------|
| `allowlist.txt` | Domains that bypass all blocking |
| `blocklist.txt` | Domains that are always blocked |
| `rewrites.yaml` | Wildcard rewrites (e.g., `*.lan → 192.168.4.1`) |
| `categories.yaml` | Category → domain mappings |
| `policy.yaml` | Category allow/block rules |
| `sources.yaml` | Gravity feed URLs |
| `threat_feeds.yaml` | Additional threat intelligence sources |

---

# 🌐 API Endpoints

Mounted automatically at:

```
/api/dns/*
```

### **GET /api/dns/overview**
Returns high‑level DNS security status.

### **GET /api/dns/events?limit=100**
Returns recent DNS events.

### **GET /api/dns/client/<ip>**
Returns DNS activity for a specific client.

### **POST /api/dns/gravity/update**
Triggers a gravity update.

---

# 🎨 Portal UI

The DNS tab is powered by:

```
extensions/dns/static/dns.js
```

It renders:

- DNS Security Overview  
- Recent DNS Events  
- Per‑client activity  
- Gravity update button  
- Category breakdown  

The UI polls:

```
/api/dns/overview
/api/dns/events
```

---

# ⚙️ Configuration Overrides

Users may override defaults in `config.yaml`:

```yaml
extensions:
  dns:
    enabled: true

dns:
  upstream_resolver: "9.9.9.9"
  enable_ips: true
  gravity_update_interval: 43200
```

---

# 🧪 Health Check

The DNS extension exposes a health report via:

```python
plugin.health()
```

Returns:

```json
{
  "status": "ok",
  "gravity": "updated",
  "rules": 123456,
  "ips": "enabled"
}
```

---

# 🛠 Development Notes

- The DNS server is async and runs inside the Eyeogotchi runtime loop.  
- All events are published to the global event bus.  
- The Portal UI is fully modular and lives inside the extension.  
- No core modifications are required — everything is auto‑discovered.  

---

# 📦 Summary

The DNS extension provides:

- A full DNS sinkhole  
- Threat intelligence ingestion  
- Category filtering  
- IPS‑style detections  
- Rewrite rules  
- Real‑time telemetry  
- A complete Portal UI  

It is one of the most powerful components of the Eyeogotchi platform and is designed to be fully extensible, maintainable, and community‑friendly.
