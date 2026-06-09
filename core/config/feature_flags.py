#Allows enabling/disabling modules via config.yaml:
from typing import Dict

class FeatureFlags:
    def __init__(self, module_flags: Dict[str, bool] | None = None):
        self.flags = module_flags or {}

    def enabled(self, module_name: str) -> bool:
        """Return True if the module is enabled."""
        return self.flags.get(module_name, False)

    def all(self) -> Dict[str, bool]:
        """Return all module flags."""
        return self.flags
