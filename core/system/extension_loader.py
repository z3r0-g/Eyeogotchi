from __future__ import annotations

import os
import yaml
import importlib
import logging
from flask import send_from_directory


class ExtensionLoader:
    """
    Unified Extension Loader for Eyeogotchi.
    Responsible for:
      - discovering extensions
      - reading extension.yaml
      - normalizing config/settings
      - instantiating extensions (runtime only)
      - registering static + API routes
    """

    def __init__(self, runtime, extension_path: str = "extensions"):
        self.runtime = runtime
        self.extension_path = extension_path
        self.log = logging.getLogger("eyeogotchi.extension_loader")

        self.extension_meta: dict[str, dict] = {}
        self.extension_paths: dict[str, str] = {}

    # ------------------------------------------------------------
    # DISCOVERY
    # ------------------------------------------------------------
    def discover(self) -> dict[str, dict]:
        if not os.path.isdir(self.extension_path):
            self.log.error(f"Extension path not found: {self.extension_path}")
            return {}

        base = os.path.abspath(self.extension_path)
        self.log.info(f"Discovering extensions under: {base}")

        for name in os.listdir(self.extension_path):
            extension_dir = os.path.join(self.extension_path, name)
            manifest = os.path.join(extension_dir, "extension.yaml")

            if not os.path.isfile(manifest):
                continue

            try:
                with open(manifest, "r") as f:
                    meta = yaml.safe_load(f) or {}
            except Exception as e:
                self.log.error(f"Failed to read {manifest}: {e}")
                continue

            meta.setdefault("name", name)
            meta.setdefault("label", meta["name"].replace("_", " ").title())
            meta.setdefault("enabled", False)
            meta.setdefault("version", "0.0.0")
            meta.setdefault("description", "No description provided")

            # Normalize config/settings
            cfg = meta.get("config")
            if cfg is None:
                cfg = meta.get("settings", {})
            meta["config"] = cfg or {}

            self.extension_meta[name] = meta
            self.extension_paths[name] = os.path.abspath(extension_dir)

            self.log.info(f"Discovered extension: {name} ({meta['version']})")

        return self.extension_meta

    # ------------------------------------------------------------
    # LOADING ENTRYPOINTS
    # ------------------------------------------------------------
    def load_enabled(self) -> None:
        pm = self.runtime.extension_manager

        for name, meta in self.extension_meta.items():
            if not meta.get("enabled", False):
                self.log.info(f"Extension disabled: {name}")
                continue

            entry = meta.get("entrypoint")
            if not entry:
                self.log.error(f"Extension {name} missing entrypoint")
                continue

            try:
                module_path, symbol = entry.split(":")
            except ValueError:
                self.log.error(f"Invalid entrypoint format for {name}: '{entry}'")
                continue

            try:
                mod = importlib.import_module(module_path)
                obj = getattr(mod, symbol)
            except Exception as e:
                self.log.error(f"Failed to import entrypoint for {name}: {e}")
                continue

            try:
                # Plugins expect: __init__(self, runtime)
                extension = obj(self.runtime)
            except Exception as e:
                self.log.error(f"Failed to instantiate extension {name}: {e}")
                continue

            pm.register_extension(name, extension)
            pm.start_extension(name)

    # ------------------------------------------------------------
    # API + STATIC AUTO-REGISTRATION
    # ------------------------------------------------------------
    def register_api(self, app) -> None:
        for name, path in self.extension_paths.items():

            # STATIC FILES
            static_dir = os.path.join(path, "static")
            if os.path.isdir(static_dir):
                static_dir_abs = os.path.abspath(static_dir)
                self.log.info(
                    f"Registering static route for extension '{name}' "
                    f"from {static_dir_abs}"
                )

                def _serve(filename, static_dir=static_dir_abs):
                    full_path = os.path.join(static_dir, filename)
                    if not os.path.isfile(full_path):
                        self.log.error(
                            f"[STATIC] {name}: requested '{filename}' "
                            f"not found in {static_dir}"
                        )
                    return send_from_directory(static_dir, filename)

                app.add_url_rule(
                    f"/extensions/{name}/static/<path:filename>",
                    endpoint=f"{name}_static",
                    view_func=_serve,
                )

                self.log.info(f"Registered static route for extension: {name}")

            # API BLUEPRINT
            api_path = os.path.join(path, "api", "routes.py")
            if os.path.isfile(api_path):
                try:
                    ext_api = importlib.import_module(f"extensions.{name}.api.routes")
                    if hasattr(ext_api, "bp"):
                        app.register_blueprint(ext_api.bp, url_prefix=f"/api/{name}")
                        self.log.info(f"Registered API for extension: {name}")
                    else:
                        self.log.warning(
                            f"Extension {name} api.routes has no 'bp' blueprint"
                        )
                except Exception as e:
                    self.log.error(f"Failed to register API for {name}: {e}")
