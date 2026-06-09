# Eyeogotchi DNS Quick Start Guide  
Simple Setup • Automatic Protection • Real‑Time Visibility

The DNS extension adds basic DNS security and visibility to your Eyeogotchi device. It blocks malicious domains, logs DNS activity, and shows you what’s happening on your network in real time.

This guide explains how to enable DNS protection and understand the information shown in the Portal.

---

# 🚀 1. Enable the DNS Extension

Open the Portal and navigate to:

```
DNS Security
```

If the extension is enabled, you’ll see the DNS Overview panel.  
If it’s disabled, enable it in your configuration file:

```yaml
extensions:
  dns:
    enabled: true
```

Restart Eyeogotchi after making changes.

---

# 🛡 2. What DNS Does Automatically

Once enabled, the DNS extension:

- Resolves DNS queries for your network  
- Blocks known malicious domains  
- Detects suspicious DNS behavior  
- Logs all DNS activity  
- Reports events to the Portal  

No extra configuration is required.

---

# 📊 3. Understanding the DNS Overview

The DNS Overview panel shows:

### **Status**
Whether the DNS engine is running correctly.

### **Total Queries**
How many DNS requests Eyeogotchi has processed.

### **Blocked**
How many requests were blocked due to:
- Threat feeds  
- Policy rules  
- Security detections  

### **Suspicious**
Queries flagged by the DNS IPS engine (e.g., DGA‑like domains).

---

# 🗂 4. Top Categories

This section shows which domain categories are most frequently queried.

Examples:
- Ads  
- Trackers  
- Malware  
- Telemetry  

If no queries have occurred yet, this section will be empty.

---

# 🚫 5. Blocked Categories

Shows which categories were blocked the most.

Examples:
- Malware  
- Adult  
- Phishing  

This section also remains empty until DNS activity occurs.

---

# 👥 6. Top Clients

Lists the devices making the most DNS queries.

You’ll see:
- Client IP  
- Number of queries  

This helps identify noisy or suspicious devices.

---

# 🕒 7. Recent DNS Events

A real‑time feed of DNS activity.

Each event shows:
- Domain  
- Client IP  
- Action (allowed, blocked, suspicious)  
- Category (if known)  
- Timestamp  

This is the best place to confirm DNS is working.

---

# 🧪 8. How to Verify DNS Is Working

You should see:

- **Status: ok**  
- **Total Queries** increasing as devices make requests  
- **Recent DNS Events** populating  
- **Blocked** increasing when threats are detected  

If everything stays at zero, check:

- Your network is using Eyeogotchi as its DNS server  
- The DNS extension is enabled  
- The service is running without errors  

---

# 🛠 9. Troubleshooting

### **No DNS events appear**
- Ensure clients are pointed at Eyeogotchi for DNS  
- Check firewall rules  
- Verify the DNS service is running  

### **Everything shows zero**
- The device may not be receiving traffic  
- Try visiting a few websites to generate DNS queries  

### **Blocked count is always zero**
- Your network may not be hitting known malicious domains  
- This is normal for clean traffic  

---

# 🎯 Summary

The DNS extension provides:

- Basic DNS security  
- Threat blocking  
- Suspicious query detection  
- Real‑time DNS visibility  

The current Portal UI is intentionally simple — it focuses on clarity and reliability. More advanced features (category toggles, rewrite rules, per‑client drill‑downs, gravity management) may be added in future versions.
