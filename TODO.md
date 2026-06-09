# Setup Network Map Extension (monitor_map)
- [ ] Base Extension on NMAP
- [ ] Implement Scheduled Scan with Config in Extension.YAML  
- [ ] Store Results as Extension Asset File  
- [ ] Expose Results via NMAP Extension API Route
- [ ] Publish Events
- [ ] Add to UI Tab with monitor_map.js + monitor_map.css

---

# Setup Vulnerability Monitoring (monitor_vul)
- [ ] Select Tool to Base Extension On
- [ ] Require 'monitor_map' Enabled as Depedency
- [ ] Source NMAP Results from NMAP API to find Neighbors
- [ ] Inventory Firmware/OS Versions to Extension Asset File
- [ ] Map Results to Advisories (using CVE Feeds, Common IoT Vendor Feeds)  
- [ ] Generate Actionable Recommendations 
- [ ] Publish Events
- [ ] Add to UI Tab with monitor_vul.js + monitor_vul.css

---

# Perform Portal Improvements with Github Copilot
- [ ] Rename 'Extensions' extension to 'Settings'
- [ ] Add a top pane to UI above Tabs that has 'Settings' and 'Logs' as Icons with Text Hints, instead of part of the main Tabs feed with Extensions. These extensions cannot be disabled.
- [ ] Update 'Settings' Tab to view and enable updating extension.yaml settings for each extension. Showing itself and Logs Extensions to edit settings but disallowing enable/disable.

---

# Perform Code Review to Publish v1
- [ ] Manually Review Code and Sanitize All Comments
- [ ] Move all Display, Logs, Settings Code to Extensions directories for each (standarize extensions)
