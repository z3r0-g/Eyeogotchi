// web/static/eyeogotchi.js

// ---------------------------
// FETCH HELPERS
// ---------------------------
async function fetchJSON(url) {
    try {
        const res = await fetch(url);
        if (!res.ok) return null;
        return await res.json();
    } catch (e) {
        console.error("Fetch failed:", url, e);
        return null;
    }
}

// EXTENSION ICONS
const extension_ICONS = {
    display: "🖥️",
    extensions: "⚙️",
    dns: "🛡️",
    monitor_map: "🗺️",
    monitor_vul: "🔎",
    logs: "📜"
};

// ---------------------------
// BUILD PORTAL TABS
// ---------------------------
async function buildPortal() {
    const state = await fetchJSON("/api/extensions/");
    if (!state) {
        console.error("Failed to load extension state");
        return;
    }

    const enabledList = state.extensions;
    const tabs = document.getElementById("dynamic-tabs");
    const pages = document.getElementById("dynamic-pages");

    tabs.innerHTML = "";
    pages.innerHTML = "";

    let firstTab = null;

    for (const ext of enabledList) {
        const name = ext.name;
        if (!ext.enabled) continue;

        const label =
            ext.label ||
            name.replace(/_/g, " ").replace(/\b\w/g, c => c.toUpperCase());

        // ---------------------------
        // LOAD EXTENSION JS HERE
        // ---------------------------
        const script = document.createElement("script");
        script.src = `/extensions/${name}/static/${name}.js`;
        script.onerror = () => console.warn(`No JS for extension: ${name}`);
        document.body.appendChild(script);

        // Tab button
        const btn = document.createElement("button");
        btn.className = "tab-btn";
        btn.dataset.tab = name;
        btn.innerHTML = `${extension_ICONS[name] || "📦"} ${label}`;
        tabs.appendChild(btn);

        // Page container
        const page = document.createElement("section");
        page.id = `page-${name}`;
        page.className = "page";
        page.innerHTML = `<h2>${label}</h2><div id="${name}-content"></div>`;
        pages.appendChild(page);

        if (!firstTab) firstTab = name;
    }

    if (firstTab) activateTab(firstTab);

    document.querySelectorAll(".tab-btn").forEach(btn => {
        btn.addEventListener("click", () => activateTab(btn.dataset.tab));
    });
}

function activateTab(tabName) {
    document.querySelectorAll(".tab-btn").forEach(b => {
        b.classList.toggle("active", b.dataset.tab === tabName);
    });

    document.querySelectorAll(".page").forEach(p => {
        p.classList.toggle("active", p.id === `page-${tabName}`);
    });
}

// ---------------------------
// EXTENSION RENDERERS
// ---------------------------

// DISPLAY extension
function update_display() {
    const container = document.getElementById("display-content");
    if (!container) return;

    // Build UI once
    if (!container.innerHTML.trim()) {
        container.innerHTML = `
            <div class="display-controls">
                <button class="btn tap" id="btnDoubleTap">Double Tap</button>
                <button class="btn tap" id="btnTripleTap">Triple Tap</button>
            </div>
            <img id="display-frame"
                 src="/api/display/frame"
                 style="width:250px; image-rendering: pixelated; border:1px solid #ccc;">
            <br>
            <div class="display-controls">
                <button class="btn warn" id="btnReboot">Reboot</button>
                <button class="btn danger" id="btnShutdown">Shutdown</button>
            </div>
        `;

        document.getElementById("btnDoubleTap").onclick = () => {
            fetch("/api/display/simulate_double_tap", { method: "POST" });
        };

        document.getElementById("btnTripleTap").onclick = () => {
            fetch("/api/display/simulate_triple_tap", { method: "POST" });
        };

        document.getElementById("btnReboot").onclick = () => {
            fetch("/api/display/reboot", { method: "POST" });
        };

        document.getElementById("btnShutdown").onclick = () => {
            fetch("/api/display/shutdown", { method: "POST" });
        };
    }

    const img = document.getElementById("display-frame");
    img.src = "/api/display/frame?ts=" + Date.now();
}

// EXTENSIONS extension
async function update_extensions() {
    const container = document.getElementById("extensions-content");
    if (!container) return;

    const state = await fetchJSON("/api/extensions/");
    if (!state) return;

    container.innerHTML = `
        <table>
            <thead><tr><th>Extension</th><th>Enabled</th><th>Health</th></tr></thead>
            <tbody>
                ${state.extensions.map(ext => `
                    <tr>
                        <td>${ext.label || ext.name}</td>
                        <td>${ext.enabled}</td>
                        <td class="status-${ext.status || "unknown"}">
                            ${ext.status || "unknown"}
                        </td>
                    </tr>
                `).join("")}
            </tbody>
        </table>
    `;
}

// LOGS extension
async function update_logs() {
    const container = document.getElementById("logs-content");
    if (!container) return;

    try {
        const logs = await fetch("/api/logs/").then(r => r.text());
        container.textContent = logs;
        container.scrollTop = container.scrollHeight;
    } catch (e) {
        console.error("Failed to load logs", e);
    }
}

// ---------------------------
// MAIN POLLING LOOP
// ---------------------------
async function pollingLoop() {
    const state = await fetchJSON("/api/extensions/");
    if (!state) return;

    for (const ext of state.extensions) {
        if (!ext.enabled) continue;

        const fn = window[`update_${ext.name}`];
        if (typeof fn === "function") fn();
    }
}

setInterval(pollingLoop, 2000);

// ---------------------------
// DARK MODE
// ---------------------------
document.getElementById("dark-toggle").addEventListener("click", () => {
    document.body.classList.toggle("dark");
});

// ---------------------------
// SWIPE GESTURES
// ---------------------------
let touchStartX = 0;

document.addEventListener("touchstart", e => {
    touchStartX = e.changedTouches[0].screenX;
});

document.addEventListener("touchend", e => {
    const dx = e.changedTouches[0].screenX - touchStartX;
    if (Math.abs(dx) < 50) return;

    const tabs = [...document.querySelectorAll(".tab-btn")];
    const activeIndex = tabs.findIndex(t => t.classList.contains("active"));

    if (dx < 0 && activeIndex < tabs.length - 1) {
        tabs[activeIndex + 1].click();
    } else if (dx > 0 && activeIndex > 0) {
        tabs[activeIndex - 1].click();
    }
});

// ---------------------------
// INITIALIZE PORTAL
// ---------------------------
buildPortal();
