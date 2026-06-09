# Eyeogotchi DNS Quick Start Guide  
Fast Setup • Instant Protection • Zero Configuration Required

The DNS extension gives your Eyeogotchi device powerful network protection with almost no setup. This guide walks you through enabling DNS security, checking that it works, and understanding the basics.

---

# 🚀 1. Enable the DNS Extension

Open the Web Portal (http://localhost:8080) and go to:

```
DNS Security
```

If DNS is disabled, click:

```
Enable DNS
```

Eyeogotchi will immediately begin filtering and monitoring DNS traffic.

---

# 🛡 2. What Happens Automatically

Once enabled, Eyeogotchi:

- Blocks malware, phishing, and tracking domains  
- Filters ads and telemetry (optional)  
- Updates threat feeds daily  
- Monitors all DNS activity on your network  
- Shows real‑time events in the Portal  

No configuration is required — it works out of the box.

---

# 🔍 3. Verify DNS Is Working

Go to:

```
Security → DNS → Overview
```

You should see:

- **DNS Status: Running**  
- **Blocked Today:** increasing over time  
- **Last Gravity Update:** recent  

If you see blocked queries appearing, DNS protection is active.

---

# 🕒 4. View Recent DNS Activity

Open:

```
Security → DNS → Recent Events
```

You’ll see a live feed of:

- Allowed domains  
- Blocked threats  
- Rewrites  
- Suspicious activity  

Each entry shows the domain, device, action, and reason.

---

# 👥 5. See What Each Device Is Doing

Go to:

```
Security → DNS → Clients
```

This shows:

- Which devices are making the most queries  
- How many were blocked  
- What categories they accessed  
- Any suspicious behavior  

Click a device for a detailed history.

---

# 🗂 6. Optional: Enable/Disable Categories

If you want to block or allow certain types of content:

```
Security → DNS → Categories
```

You can toggle:

- Ads  
- Trackers  
- Adult  
- Social  
- Telemetry  
- Gambling  
- Malware (always recommended ON)

Changes apply instantly.

---

# 🧲 7. Update Threat Feeds (Gravity)

Eyeogotchi updates threat feeds automatically every day.

To update manually:

```
Security → DNS → Gravity → Update Now
```

This refreshes all blocklists and threat intelligence sources.

---

# 🏠 8. Optional: Local Hostname Rewrites

If you want to access devices by name:

```
nas.lan → 192.168.4.10
printer.lan → 192.168.4.20
```

Add these under:

```
Security → DNS → Settings → Rewrite Rules
```

---

# 🧪 9. Troubleshooting

### A website won’t load  
Check **Recent Events** — it may be blocked by category or threat feed.

### Local devices don’t resolve  
Add a rewrite rule for the hostname.

### DNS feels slow  
Try switching upstream resolvers in **Settings**.

### Gravity update failed  
Check your internet connection and try again.

---

# 🎯 Summary

With DNS enabled, Eyeogotchi provides:

- Automatic threat blocking  
- Privacy filtering  
- Real‑time monitoring  
- Local hostname support  
- Daily threat feed updates  

You get strong network protection with almost no setup — just enable it and let Eyeogotchi handle the rest.
