# cli/eyeogotchi.py

import click
import subprocess
import yaml
import os
import sys
import time
import logging

CONFIG_PATH = "config.yaml"
MODULES_DIR = "modules"

@click.group()
def cli():
    """Eyeogotchi command-line interface."""
    pass


# ------------------------------------------------------------
# CONFIG COMMAND
# ------------------------------------------------------------
@cli.command()
def config():
    """Open config.yaml in nano for editing."""
    if not os.path.exists(CONFIG_PATH):
        click.echo("config.yaml not found.")
        sys.exit(1)

    os.system(f"sudo nano {CONFIG_PATH}")


# ------------------------------------------------------------
# MODULE COMMAND GROUP
# ------------------------------------------------------------
@cli.group()
def modules():
    """Manage Eyeogotchi modules."""
    pass


# ------------------------------------------------------------
# MODULES: LIST
# ------------------------------------------------------------
@modules.command("list")
def list_modules():
    """List discovered modules and their metadata."""
    from core.system.extension_loader import ModuleLoader
    from core.system.runtime import EyeogotchiRuntime

    runtime = EyeogotchiRuntime()
    loader = runtime.module_loader

    click.echo("Discovered Modules:\n")
    for name, meta in loader.modules_meta.items():
        status = "ENABLED" if meta.get("enabled") else "disabled"
        click.echo(f"- {name} ({meta.get('version')}) [{status}]")
        click.echo(f"  {meta.get('description')}")
        click.echo("")


# ------------------------------------------------------------
# MODULES: UPDATE (GIT SOURCES)
# ------------------------------------------------------------
@modules.command("update")
def update_modules():
    """Clone or update modules from Git sources defined in config.yaml."""
    if not os.path.exists(CONFIG_PATH):
        click.echo("config.yaml not found.")
        sys.exit(1)

    with open(CONFIG_PATH) as f:
        cfg = yaml.safe_load(f)

    sources = cfg.get("module_sources", [])
    if not sources:
        click.echo("No module_sources defined in config.yaml.")
        return

    os.makedirs(MODULES_DIR, exist_ok=True)

    for url in sources:
        name = url.split("/")[-1].replace(".git", "")
        path = os.path.join(MODULES_DIR, name)

        if os.path.exists(path):
            click.echo(f"Updating {name}...")
            subprocess.run(["git", "-C", path, "pull"])
        else:
            click.echo(f"Cloning {name}...")
            subprocess.run(["git", "clone", url, path])

    click.echo("\nModule update complete.")


# ------------------------------------------------------------
# MODULES: ENABLE / DISABLE
# ------------------------------------------------------------
@modules.command("enable")
@click.argument("name")
def enable_module(name):
    """Enable a module in config.yaml."""
    _set_module_enabled(name, True)


@modules.command("disable")
@click.argument("name")
def disable_module(name):
    """Disable a module in config.yaml."""
    _set_module_enabled(name, False)


def _set_module_enabled(name, enabled):
    if not os.path.exists(CONFIG_PATH):
        click.echo("config.yaml not found.")
        sys.exit(1)

    with open(CONFIG_PATH) as f:
        cfg = yaml.safe_load(f)

    if "modules" not in cfg:
        cfg["modules"] = {}

    cfg["modules"][name] = enabled

    with open(CONFIG_PATH, "w") as f:
        yaml.safe_dump(cfg, f)

    click.echo(f"Module '{name}' set to enabled={enabled}")


# ------------------------------------------------------------
# LOGS COMMAND
# ------------------------------------------------------------
@cli.command()
def logs():
    """Tail the Eyeogotchi log file."""
    logfile = "/var/log/eyeogotchi/eyeogotchi.log"

    if not os.path.exists(logfile):
        click.echo("Log file not found.")
        sys.exit(1)

    click.echo("Tailing logs... (Ctrl+C to exit)\n")

    try:
        subprocess.run(["tail", "-f", logfile])
    except KeyboardInterrupt:
        click.echo("\nStopped.")


# ------------------------------------------------------------
# RESTART COMMAND
# ------------------------------------------------------------
@cli.command()
def restart():
    """Restart the Eyeogotchi runtime (systemd or local)."""
    click.echo("Restarting Eyeogotchi...")

    # If running under systemd
    if os.path.exists("/bin/systemctl"):
        subprocess.run(["sudo", "systemctl", "restart", "eyeogotchi"])
        return

    # Fallback: kill + restart local process
    click.echo("Local restart not implemented yet.")


# ------------------------------------------------------------
# ENTRYPOINT
# ------------------------------------------------------------
if __name__ == "__main__":
    cli()
