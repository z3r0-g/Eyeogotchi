#extensions/dns/api/routes.py
from __future__ import annotations

import asyncio
import threading
import time

from flask import Blueprint, jsonify, current_app, request

from extensions.dns.api.events import get_dns_events

bp = Blueprint("dns_api", __name__)

# ------------------------------------------------------------
# OVERVIEW
# ------------------------------------------------------------

@bp.get("/overview")
def dns_overview():
    runtime = current_app.runtime
    dns_plugin = runtime.extension_manager.extensions.get("dns")

    if not dns_plugin:
        return jsonify({"status": "disabled"}), 404

    health = dns_plugin.health()
    telemetry = health.get("telemetry", {})

    return jsonify({
        "status": health.get("status", "unknown"),
        "totals": {
            "queries": telemetry.get("total_queries", 0),
            "blocked": telemetry.get("blocked_queries", 0),
            "suspicious": telemetry.get("suspicious_queries", 0),
        },
        "top": {
            "domains": telemetry.get("top_domains", []),
            "clients": telemetry.get("top_clients", []),
            "categories": telemetry.get("top_categories", []),
            "blocked_categories": telemetry.get("blocked_categories", []),
        },
    })


# ------------------------------------------------------------
# EVENTS (cached)
# ------------------------------------------------------------

_last_events = {"ts": 0.0, "data": []}

@bp.get("/events")
def dns_events():
    global _last_events

    try:
        limit = int(request.args.get("limit", 100))
    except ValueError:
        limit = 100

    now = time.time()

    if now - _last_events["ts"] < 1:
        return jsonify(_last_events["data"][:limit])

    events = get_dns_events(limit)
    _last_events["ts"] = now
    _last_events["data"] = events

    return jsonify(events)


# ------------------------------------------------------------
# CLIENT LIST
# ------------------------------------------------------------

@bp.get("/clients")
def dns_clients():
    runtime = current_app.runtime
    dns_plugin = runtime.extension_manager.extensions.get("dns")

    if not dns_plugin:
        return jsonify([])

    health = dns_plugin.health()
    telemetry = health.get("telemetry", {})

    top_clients = telemetry.get("top_clients", [])
    blocked_by_client = dict(telemetry.get("blocked_by_client", []))
    suspicious_by_client = dict(telemetry.get("suspicious_by_client", []))

    clients = []
    for ip, total in top_clients:
        clients.append({
            "ip": ip,
            "queries": total,
            "blocked": blocked_by_client.get(ip, 0),
            "suspicious": suspicious_by_client.get(ip, 0),
        })

    return jsonify(clients)


# ------------------------------------------------------------
# CLIENT DETAIL
# ------------------------------------------------------------

@bp.get("/client/<ip>")
def dns_client_summary(ip):
    runtime = current_app.runtime
    dns_plugin = runtime.extension_manager.extensions.get("dns")

    if not dns_plugin:
        return jsonify({"error": "dns extension not available"}), 404

    health = dns_plugin.health()
    telemetry = health.get("telemetry", {})

    top_clients = dict(telemetry.get("top_clients", []))
    total_for_client = top_clients.get(ip, 0)

    events = get_dns_events(200)
    client_events = [e for e in events if e.get("client") == ip]

    from collections import Counter
    dom_counter = Counter()
    cat_counter = Counter()

    for e in client_events:
        q = e.get("query")
        if q:
            dom_counter[q] += 1
        for c in e.get("categories") or []:
            cat_counter[c] += 1

    return jsonify({
        "client": ip,
        "totals": {
            "queries": total_for_client,
            "blocked": sum(1 for e in client_events if e.get("action") == "block"),
            "suspicious": sum(1 for e in client_events if e.get("action") == "suspicious"),
        },
        "top_domains": dom_counter.most_common(10),
        "top_categories": cat_counter.most_common(10),
        "recent_events": client_events,
    })


# ------------------------------------------------------------
# CATEGORIES
# ------------------------------------------------------------

@bp.get("/categories")
def dns_categories():
    runtime = current_app.runtime
    dns_plugin = runtime.extension_manager.extensions.get("dns")

    if not dns_plugin:
        return jsonify([])

    health = dns_plugin.health()
    telemetry = health.get("telemetry", {})

    top_categories = telemetry.get("top_categories", [])
    blocked_categories = dict(telemetry.get("blocked_categories", []))

    categories = []
    for cat, count in top_categories:
        categories.append({
            "category": cat,
            "count": count,
            "blocked": blocked_categories.get(cat, 0),
        })

    return jsonify(categories)


# ------------------------------------------------------------
# GRAVITY STATUS
# ------------------------------------------------------------

@bp.get("/gravity")
def dns_gravity_status():
    runtime = current_app.runtime
    dns_plugin = runtime.extension_manager.extensions.get("dns")

    if not dns_plugin or not getattr(dns_plugin, "gravity", None):
        return jsonify({"error": "dns extension not available"}), 404

    health = dns_plugin.health()
    g = dns_plugin.gravity

    return jsonify({
        "status": health.get("status", "unknown"),
        "last_update": getattr(g, "last_update_ts", None),
        "rule_count": getattr(g, "rule_count", 0),
        "threat_rule_count": getattr(g, "threat_rule_count", 0),
        "sources": getattr(g, "sources", []),
    })


# ------------------------------------------------------------
# SETTINGS
# ------------------------------------------------------------

@bp.get("/settings")
def dns_settings():
    runtime = current_app.runtime
    dns_plugin = runtime.extension_manager.extensions.get("dns")

    if not dns_plugin:
        return jsonify({"error": "dns extension not available"}), 404

    cfg = getattr(dns_plugin, "config", {}) or {}

    return jsonify({
        "upstream": cfg.get("upstream_resolver", "system"),
        "ips_enabled": bool(cfg.get("ips", {}).get("enabled", False)),
        "categories_enabled": bool(cfg.get("categories", {}).get("enabled", True)),
        "rewrites_enabled": bool(cfg.get("rewrites", {}).get("enabled", True)),
    })


# ------------------------------------------------------------
# GRAVITY UPDATE
# ------------------------------------------------------------

@bp.post("/gravity/update")
def dns_gravity_update():
    runtime = current_app.runtime
    dns_plugin = runtime.extension_manager.extensions.get("dns")

    if not dns_plugin or not getattr(dns_plugin, "gravity", None):
        return jsonify({"error": "dns extension not available"}), 404

    gravity = dns_plugin.gravity

    def _runner():
        try:
            asyncio.run(gravity.update_once())
        except Exception as e:
            print("[DNS][api] gravity update failed:", e)

    threading.Thread(target=_runner, daemon=True).start()

    return jsonify({"status": "ok", "message": "gravity update started"})
