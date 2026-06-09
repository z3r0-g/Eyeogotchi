# Eyeogotchi DNS User Guide  
Protective DNS • Threat Blocking • Privacy Filtering • Real‑Time Visibility

The DNS extension adds a powerful security and privacy layer to your Eyeogotchi device. It blocks malicious domains, filters unwanted categories (ads, trackers, adult content, etc.), rewrites local hostnames, and gives you real‑time visibility into DNS activity on your network.

This guide explains how to use the DNS feature from the Portal and what each section means.

---

# 🛡 What the DNS Extension Does

Eyeogotchi’s DNS engine provides:

### ✔ Threat Blocking  
Automatically blocks:
- Malware domains  
- Phishing sites  
- Command‑and‑control servers  
- Known trackers  

### ✔ Privacy Filtering  
Optionally blocks:
- Ads  
- Telemetry  
- Analytics  
- Adult content  
- Social media categories  

### ✔ Local Network Rewrites  
Lets you map hostnames like:

```
nas.lan → 192.168.4.10
printer.lan → 192.168.4.20
```

### ✔ Real‑Time Monitoring  
See:
- Which devices are making DNS queries  
- What was blocked  
- Why it was blocked  
- Suspicious or abnormal behavior  

### ✔ Automatic Threat Feed Updates  
Eyeogotchi downloads and merges threat intelligence lists daily.

---

# 📍 Accessing the DNS Dashboard

Open the Portal and click:

```
Security → DNS
```

You’ll see several panels:

- **Overview**
- **Recent Events**
- **Clients**
- **Categories**
- **Gravity (Threat Feeds)**
- **Settings**

Each section is explained below.

---

# 📊 Overview Panel

Shows the current status of the DNS engine:

- **DNS Status** — Running / Stopped  
- **Blocked Today** — Number of blocked queries  
- **Top Categories** — Ads, Malware, Trackers, etc.  
- **Top Clients** — Devices generating the most queries  
- **Last Gravity Update** — When threat feeds were refreshed  

This is your quick “health check” for DNS security.

---

# 🕒 Recent Events

A real‑time feed of DNS activity.

Each entry shows:

| Field | Meaning |
|-------|---------|
| Domain | The domain that was queried |
| Client | The device that made the request |
| Action | Allowed / Blocked / Rewritten |
| Reason | Category, policy, or threat feed |
| Timestamp | When it happened |

You can click an event to see more details.

---

# 👥 Clients View

Shows all devices that have made DNS queries.

For each device you’ll see:

- Total queries  
- Blocked queries  
- Categories accessed  
- Suspicious activity (if any)  

Clicking a device shows a detailed history of its DNS behavior.

---

# 🗂 Categories

Displays the categories Eyeogotchi uses to classify domains:

- Ads  
- Trackers  
- Malware  
- Adult  
- Social  
- Telemetry  
- Gambling  
- And more  

You can enable or disable categories depending on your preferences.

---

# 🧲 Gravity (Threat Feeds)

Gravity is the system that downloads and compiles threat intelligence.

This panel shows:

- When the last update occurred  
- How many rules were loaded  
- Which feeds are active  
- Whether updates succeeded or failed  

You can also manually trigger an update:

```
Update Gravity Now
```

---

# ⚙ Settings

User‑configurable DNS options:

### **Upstream Resolver**
Choose where Eyeogotchi forwards allowed DNS queries:
- Cloudflare (1.1.1.1)  
- Quad9 (9.9.9.9)  
- Google (8.8.8.8)  
- Custom resolver  

### **Category Filtering**
Toggle categories on/off.

### **Rewrite Rules**
Add custom hostname → IP mappings.

### **IPS Mode**
Enable DNS‑layer intrusion detection:
- DGA detection  
- Suspicious patterns  
- Excessive NXDOMAIN  
- Rapid‑fire queries  

---

# 🧪 Understanding DNS Actions

Eyeogotchi may take several actions on a DNS query:

### **Allowed**
The domain is safe or permitted by policy.

### **Blocked**
The domain matched:
- A threat feed  
- A blocklist  
- A blocked category  
- A policy rule  

### **Rewritten**
The domain was replaced with a custom IP (useful for `.lan` devices).

### **Suspicious**
The domain looks abnormal or risky (IPS detection).

---

# 🔍 Troubleshooting

### **A device can’t reach a website**
Check:
- Recent Events  
- Category settings  
- Blocklist  
- IPS alerts  

### **DNS feels slow**
Try switching upstream resolvers.

### **Local hostnames don’t resolve**
Add a rewrite rule:
```
mydevice.lan → 192.168.4.50
```

### **Gravity update failed**
Check your internet connection or try again later.

---

# 🎯 Summary

The DNS extension gives Eyeogotchi:

- Strong security  
- Better privacy  
- Real‑time visibility  
- Customizable filtering  
- Automatic threat intelligence  

It’s one of the most powerful protections your device provides — and it works automatically once enabled.

