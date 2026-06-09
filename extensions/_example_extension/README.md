# Eyeogotchi Extension Development Guide

Eyeogotchi is a modular platform. Every feature is implemented as a standalone **extension** that the runtime auto‑discovers, auto‑loads, and auto‑registers.

This guide explains how to build, structure, and publish your own extensions.

---

## 📦 Extension Structure

Each extension lives inside `extensions/<name>/` and is fully self‑contained:

```
extensions/
  <extension_name>/
    extension.yaml
    service/
      main.py
    api/              (optional)
      routes.py
    static/           (optional)
    assets/           (optional)
    scripts/          (optional)
    rules/            (optional)
```

This structure keeps extensions isolated, portable, and easy to distribute.

---

## 🧩 extension.yaml (Manifest)

Every extension must include an `extension.yaml` file describing its metadata, entrypoint, and default configuration.

Example:

```yaml
name: example
version: 1.0.0
description: "A minimal example extension"
enabled: true

entrypoint: "extensions.example.service.main:get_plugin"

config:
  message: "Hello!"
```

### Manifest Fields

| Field        | Description |
|--------------|-------------|
| `name`       | Extension name (must match folder name) |
| `version`    | Semantic version |
| `description`| Human‑readable description |
| `enabled`    | Whether the extension loads at runtime |
| `entrypoint` | Python import path to the extension’s plugin factory |
| `config`     | Default extension configuration |

---

## 🧠 Plugin Factory (`get_plugin`)

Extensions must expose a `get_plugin(bus)` function that returns a `Plugin` instance.

Example:

```python
from core.system.plugin_interface import Plugin
import logging

class ExampleExtension(Plugin):
    def __init__(self, bus, config):
        self.bus = bus
        self.config = config
        self.log = logging.getLogger("eyeogotchi.example")

    def start(self):
        self.log.info("ExampleExtension started")

    def stop(self):
        self.log.info("ExampleExtension stopped")

    def health(self):
        return {"status": "ok"}

def get_plugin(bus):
    config = bus.runtime.config.get("example", {})
    return ExampleExtension(bus, config)
```

The PluginManager handles lifecycle events automatically.

---

## 🌐 Optional API Endpoints

If your extension needs HTTP endpoints, create:

```
extensions/<name>/api/routes.py
```

Example:

```python
from flask import Blueprint, jsonify

bp = Blueprint("example_api", __name__)

@bp.get("/ping")
def ping():
    return jsonify({"example": "pong"})
```

The core mounts this under:

```
/api/<extension_name>/*
```

---

## 🎨 Optional Static Assets

Extensions may include:

- JavaScript  
- CSS  
- Icons  
- Images  

Place them in:

```
extensions/<name>/static/
extensions/<name>/assets/
```

The Portal automatically exposes these under:

```
/static/<extension_name>/*
```

---

## ⚙️ Configuration

Extension configuration is merged from:

1. `extensions/<name>/extension.yaml` (defaults)  
2. `config.yaml` (user overrides)

Example override:

```yaml
extensions:
  example:
    enabled: true

example:
  message: "Custom message"
```

The merged config is injected into your plugin via `get_plugin`.

---

## 🌍 Publishing Extensions from Git

Extensions can be installed from Git repositories by adding them to:

```yaml
extension_sources:
  - https://github.com/yourorg/eyeogotchi-example.git
```

Then run:

```
eyeogotchi extensions update
```

The CLI will clone or update extensions automatically.

---

## 🚀 Summary

Eyeogotchi extensions are:

- Self‑contained  
- Auto‑discovered  
- Auto‑loaded  
- API‑aware  
- Configurable  
- Installable from Git  
- Easy to extend with UI, scripts, rules, or assets  

Build cleanly, and your extension will plug into the platform with zero core changes.
