// extensions/dns/static/dns.js

// ------------------------------------------------------------
// GLOBAL UI STATE
// ------------------------------------------------------------
window.DNS_UI_STATE = {
    dns_setup_mode: null,
    dns_setup_command: "",
    dns_setup_description: "",
    client_drilldown_ip: null,
    client_drilldown_data: null,
    scroll_position: 0
};

// ------------------------------------------------------------
// FETCH HELPERS WITH ERROR HANDLING
// ------------------------------------------------------------
async function fetchJSON(url) {
    try {
        const r = await fetch(url, { cache: "no-store" });
        if (!r.ok) throw new Error(`HTTP ${r.status}`);
        return await r.json();
    } catch (e) {
        console.error("DNS fetch failed:", url, e);
        return { __error: true, message: e.message };
    }
}

// ------------------------------------------------------------
// SPINNER GENERATOR
// ------------------------------------------------------------
function spinnerHTML() {
    return `
        <div class="dns-spinner">
            <div class="dns-spinner-dot"></div>
            <div class="dns-spinner-dot"></div>
            <div class="dns-spinner-dot"></div>
        </div>
    `;
}

// ------------------------------------------------------------
// OS DETECTION + COMMAND GENERATION
// ------------------------------------------------------------
function detectOS() {
    const ua = navigator.userAgent;
    if (/Windows/i.test(ua)) return "windows";
    if (/Macintosh|Mac OS X/i.test(ua)) return "mac";
    if (/Linux/i.test(ua)) return "linux";
    if (/Android/i.test(ua)) return "android";
    if (/iPhone|iPad/i.test(ua)) return "ios";
    return "unknown";
}

function getSetDNSCommand(os, dnsServer) {
    switch (os) {
        case "mac":
            return {
                desc: "Run this command in Terminal:",
                cmd: `networksetup -setdnsservers Wi-Fi ${dnsServer}`
            };
        case "linux":
            return {
                desc: "Run this command in your shell:",
                cmd: `sudo resolvectl dns eth0 ${dnsServer}`
            };
        case "windows":
            return {
                desc: "Run this in PowerShell (as Administrator):",
                cmd: `Set-DnsClientServerAddress -InterfaceAlias "Ethernet" -ServerAddresses ${dnsServer}`
            };
        case "android":
        case "ios":
            return {
                desc: "Mobile OSes require manual DNS configuration in Wi-Fi settings:",
                cmd: `${dnsServer}`
            };
        default:
            return {
                desc: "Set your DNS server to:",
                cmd: dnsServer
            };
    }
}

function getRestoreDNSCommand(os, previous) {
    if (!previous) {
        return {
            desc: "No previous DNS settings were recorded.",
            cmd: "N/A"
        };
    }
    switch (os) {
        case "mac":
            return {
                desc: "Restore your previous DNS settings:",
                cmd: `networksetup -setdnsservers Wi-Fi ${previous}`
            };
        case "linux":
            return {
                desc: "Restore your previous DNS settings:",
                cmd: `sudo resolvectl dns eth0 ${previous}`
            };
        case "windows":
            return {
                desc: "Restore your previous DNS settings:",
                cmd: `Set-DnsClientServerAddress -InterfaceAlias "Ethernet" -ServerAddresses ${previous}`
            };
        case "android":
        case "ios":
            return {
                desc: "Restore DNS manually in Wi-Fi settings:",
                cmd: previous
            };
        default:
            return {
                desc: "Restore DNS to:",
                cmd: previous
            };
    }
}

// ------------------------------------------------------------
// INLINE DNS SETUP SECTION
// ------------------------------------------------------------
function renderInlineDNSSection() {
    const box = document.getElementById("dns-inline-section");
    if (!box) return;

    if (!window.DNS_UI_STATE.dns_setup_mode) {
        box.innerHTML = "";
        return;
    }

    box.innerHTML = `
        <div class="dns-inline-box fade-in">
            <p>${window.DNS_UI_STATE.dns_setup_description}</p>
            <pre class="dns-inline-command">${window.DNS_UI_STATE.dns_setup_command}</pre>
            <button class="btn btn-secondary dns-inline-copy">Copy</button>
            <button class="btn dns-inline-clear">Close</button>
        </div>
    `;

    const copyBtn = box.querySelector(".dns-inline-copy");
    const clearBtn = box.querySelector(".dns-inline-clear");
    const cmd = box.querySelector(".dns-inline-command");

    copyBtn.onclick = () => {
        navigator.clipboard.writeText(cmd.textContent);
        copyBtn.textContent = "Copied!";
        setTimeout(() => (copyBtn.textContent = "Copy"), 1500);
    };

    clearBtn.onclick = () => {
        window.DNS_UI_STATE.dns_setup_mode = null;
        renderInlineDNSSection();
    };
}

function setupInlineDNSHandlers(dnsServer) {
    const setBtn = document.getElementById("dns-set-btn");
    const restoreBtn = document.getElementById("dns-restore-btn");
    const os = detectOS();

    setBtn.onclick = () => {
        if (!localStorage.getItem("eyeogotchi_previous_dns")) {
            localStorage.setItem("eyeogotchi_previous_dns", "Automatic");
        }
        const info = getSetDNSCommand(os, dnsServer);
        window.DNS_UI_STATE.dns_setup_mode = "set";
        window.DNS_UI_STATE.dns_setup_command = info.cmd;
        window.DNS_UI_STATE.dns_setup_description = info.desc;
        renderInlineDNSSection();
    };

    restoreBtn.onclick = () => {
        const previous = localStorage.getItem("eyeogotchi_previous_dns") || "Automatic";
        const info = getRestoreDNSCommand(os, previous);
        window.DNS_UI_STATE.dns_setup_mode = "restore";
        window.DNS_UI_STATE.dns_setup_command = info.cmd;
        window.DNS_UI_STATE.dns_setup_description = info.desc;
        renderInlineDNSSection();
    };
}

// ------------------------------------------------------------
// CLIENT DRILL-DOWN (ANIMATED)
// ------------------------------------------------------------
function renderClientDrilldown(container) {
    const ip = window.DNS_UI_STATE.client_drilldown_ip;
    const data = window.DNS_UI_STATE.client_drilldown_data;

    if (!ip || !data) {
        container.innerHTML = "";
        container.classList.remove("open");
        return;
    }

    container.innerHTML = `
        <div class="client-drill-card fade-in">
            <h4>Client Details: ${ip}</h4>
            <p><strong>Queries:</strong> ${data.totals.queries}</p>
            <p><strong>Blocked:</strong> ${data.totals.blocked}</p>
            <p><strong>Suspicious:</strong> ${data.totals.suspicious}</p>

            <h5>Top Domains</h5>
            <ul>
                ${data.top_domains.map(([d, c]) => `<li>${d} (${c})</li>`).join("")}
            </ul>

            <h5>Top Categories</h5>
            <ul>
                ${data.top_categories.map(([c, n]) => `<li>${c} (${n})</li>`).join("")}
            </ul>

            <h5>Recent Events</h5>
            <table class="dns-events-table small">
                <thead>
                    <tr><th>Time</th><th>Domain</th><th>Action</th><th>Reason</th></tr>
                </thead>
                <tbody>
                    ${data.recent_events.map(e => `
                        <tr>
                            <td>${new Date(e.timestamp * 1000).toLocaleTimeString()}</td>
                            <td>${e.query}</td>
                            <td>${e.action}</td>
                            <td>${e.reason || ""}</td>
                        </tr>
                    `).join("")}
                </tbody>
            </table>
        </div>
    `;

    container.classList.add("open");
}

// ------------------------------------------------------------
// RENDER PANELS
// ------------------------------------------------------------
function dns_renderOverview(container, overview) {
    if (!overview || overview.__error || overview.status === "disabled") {
        container.innerHTML = `<div class="card"><p class="muted">DNS extension is disabled or unavailable.</p></div>`;
        return;
    }

    const totals = overview.totals || {};
    const blockRate = totals.queries ? ((totals.blocked / totals.queries) * 100).toFixed(1) : "0.0";
    const suspiciousRate = totals.queries ? ((totals.suspicious / totals.queries) * 100).toFixed(1) : "0.0";

    container.innerHTML = `
        <div class="card fade-in">
            <h3>DNS Overview</h3>
            <p>Status: <strong>${overview.status}</strong></p>
            <p>Total queries: <strong>${totals.queries}</strong></p>
            <p>Blocked: <strong>${totals.blocked}</strong> (${blockRate}%)</p>
            <p>Suspicious: <strong>${totals.suspicious}</strong> (${suspiciousRate}%)</p>

            <button id="dns-set-btn" class="btn btn-primary dns-btn">Set My DNS</button>
            <button id="dns-restore-btn" class="btn btn-secondary dns-btn">Restore DNS</button>

            <div id="dns-inline-section"></div>
        </div>
    `;

    setupInlineDNSHandlers("192.168.4.1");
    renderInlineDNSSection();
}

function dns_renderClients(container, clients) {
    const drill = document.getElementById("dns-client-drilldown");

    if (!clients || clients.__error) {
        container.innerHTML = `<div class="card"><p class="muted">Failed to load clients.</p></div>`;
        return;
    }

    container.innerHTML = `
        <div class="card fade-in">
            <h3>Clients</h3>
            <table class="dns-table">
                <thead>
                    <tr><th>IP</th><th>Queries</th><th>Blocked</th><th>Suspicious</th></tr>
                </thead>
                <tbody>
                    ${clients.length === 0 ? `
                        <tr><td colspan="4" class="muted">No client data available.</td></tr>
                    ` : clients.map(c => `
                        <tr class="client-row" data-ip="${c.ip}">
                            <td>${c.ip}</td>
                            <td>${c.queries}</td>
                            <td>${c.blocked}</td>
                            <td>${c.suspicious}</td>
                        </tr>
                    `).join("")}
                </tbody>
            </table>
        </div>
    `;

    container.querySelectorAll(".client-row").forEach(row => {
        row.onclick = async () => {
            const ip = row.dataset.ip;

            if (window.DNS_UI_STATE.client_drilldown_ip === ip) {
                window.DNS_UI_STATE.client_drilldown_ip = null;
                window.DNS_UI_STATE.client_drilldown_data = null;
                renderClientDrilldown(drill);
                return;
            }

            const data = await fetchJSON(`/api/dns/client/${ip}`);
            window.DNS_UI_STATE.client_drilldown_ip = ip;
            window.DNS_UI_STATE.client_drilldown_data = data;
            renderClientDrilldown(drill);
        };
    });

    renderClientDrilldown(drill);
}

function dns_renderCategories(container, categories) {
    if (!categories || categories.__error) {
        container.innerHTML = `<div class="card"><p class="muted">Failed to load categories.</p></div>`;
        return;
    }

    container.innerHTML = `
        <div class="card fade-in">
            <h3>Categories</h3>
            <table class="dns-table">
                <thead>
                    <tr><th>Category</th><th>Count</th><th>Blocked</th></tr>
                </thead>
                <tbody>
                    ${categories.length === 0 ? `
                        <tr><td colspan="3" class="muted">No category data available.</td></tr>
                    ` : categories.map(c => `
                        <tr>
                            <td>${c.category}</td>
                            <td>${c.count}</td>
                            <td>${c.blocked}</td>
                        </tr>
                    `).join("")}
                </tbody>
            </table>
        </div>
    `;
}

function dns_renderGravity(container, gravity) {
    if (!gravity || gravity.__error) {
        container.innerHTML = `<div class="card"><p class="muted">Failed to load gravity data.</p></div>`;
        return;
    }

    container.innerHTML = `
        <div class="card fade-in">
            <h3>Gravity</h3>
            <p>Status: <strong>${gravity.status}</strong></p>
            <p>Last update: <strong>${gravity.last_update ? new Date(gravity.last_update * 1000).toLocaleString() : "Never"}</strong></p>
            <p>Rule count: <strong>${gravity.rule_count}</strong></p>
            <p>Sources:</p>
            <ul>${gravity.sources.map(s => `<li>${s.name} — ${s.url}</li>`).join("")}</ul>

            <button id="gravity-update-btn" class="btn btn-primary">Update Gravity</button>
        </div>
    `;

    document.getElementById("gravity-update-btn").onclick = async () => {
        await fetch("/api/dns/gravity/update", { method: "POST" });

    };
}

function dns_renderSettings(container, settings) {
    if (!settings || settings.__error) {
        container.innerHTML = `<div class="card"><p class="muted">Failed to load settings.</p></div>`;
        return;
    }

    container.innerHTML = `
        <div class="card fade-in">
            <h3>Settings</h3>
            <p><strong>Upstream resolver:</strong> ${settings.upstream}</p>
            <p><strong>IPS enabled:</strong> ${settings.ips_enabled}</p>
            <p><strong>Category engine:</strong> ${settings.categories_enabled}</p>
            <p><strong>Rewrite engine:</strong> ${settings.rewrites_enabled}</p>
        </div>
    `;
}

function dns_renderEvents(container, events) {
    if (!events || events.__error) {
        container.innerHTML = `<div class="card"><p class="muted">Failed to load events.</p></div>`;
        return;
    }

    if (!events.length) {
        container.innerHTML = `<div class="card"><p class="muted">No recent DNS events.</p></div>`;
        return;
    }

    container.innerHTML = `
        <div class="card fade-in">
            <h3>Recent Events</h3>
            <table class="dns-events-table">
                <thead>
                    <tr>
                        <th>Time</th>
                        <th>Client</th>
                        <th>Domain</th>
                        <th>Action</th>
                        <th>Reason</th>
                        <th>Categories</th>
                    </tr>
                </thead>
                <tbody>
                    ${events.map(e => `
                        <tr>
                            <td>${new Date(e.timestamp * 1000).toLocaleTimeString()}</td>
                            <td>${e.client}</td>
                            <td>${e.query}</td>
                            <td>${e.action}</td>
                            <td>${e.reason || ""}</td>
                            <td>${(e.categories || []).join(", ")}</td>
                        </tr>
                    `).join("")}
                </tbody>
            </table>
        </div>
    `;
}

// ------------------------------------------------------------
// MAIN UPDATE LOOP
// ------------------------------------------------------------
window.update_dns = async function () {
    const container = document.getElementById("dns-content");
    if (!container) return;

    // Save scroll position
    window.DNS_UI_STATE.scroll_position = window.scrollY;

    if (!container.dataset.initialized) {
        container.innerHTML = `
            <div class="dns-layout">
                <section><div id="dns-overview-panel">${spinnerHTML()}</div></section>
                <section>
                    <div id="dns-clients-panel">${spinnerHTML()}</div>
                    <div id="dns-client-drilldown" class="client-drilldown"></div>
                </section>
                <section><div id="dns-categories-panel">${spinnerHTML()}</div></section>
                <section><div id="dns-gravity-panel">${spinnerHTML()}</div></section>
                <section><div id="dns-settings-panel">${spinnerHTML()}</div></section>
                <section><div id="dns-events-panel">${spinnerHTML()}</div></section>
            </div>
        `;
        container.dataset.initialized = "1";
    }

    const [
        overview,
        clients,
        categories,
        gravity,
        settings,
        events
    ] = await Promise.all([
        fetchJSON("/api/dns/overview"),
        fetchJSON("/api/dns/clients"),
        fetchJSON("/api/dns/categories"),
        fetchJSON("/api/dns/gravity"),
        fetchJSON("/api/dns/settings"),
        fetchJSON("/api/dns/events?limit=100")
    ]);

    dns_renderOverview(document.getElementById("dns-overview-panel"), overview);
    dns_renderClients(document.getElementById("dns-clients-panel"), clients);
    dns_renderCategories(document.getElementById("dns-categories-panel"), categories);
    dns_renderGravity(document.getElementById("dns-gravity-panel"), gravity);
    dns_renderSettings(document.getElementById("dns-settings-panel"), settings);
    dns_renderEvents(document.getElementById("dns-events-panel"), events);

    // Restore scroll position
    window.scrollTo(0, window.DNS_UI_STATE.scroll_position || 0);
};
