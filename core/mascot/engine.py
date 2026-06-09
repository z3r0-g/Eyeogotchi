#core/mascot/engine.py
import time
import random
import logging


class MascotEngine:
    def __init__(self, runtime):
        self.runtime = runtime
        self.log = logging.getLogger("eyeogotchi.mascot")

        cfg = runtime.config.get("mascot", {})

        # personality traits
        self.enabled = cfg.get("enabled", True)
        self.default_state = cfg.get("default_state", "happy")
        self.state_decay_seconds = cfg.get("state_decay_seconds", 120)

        self.curiosity = cfg.get("curiosity", 0.8)
        self.patience = cfg.get("patience", 0.4)
        self.pride = cfg.get("pride", 0.9)
        self.sensitivity = cfg.get("sensitivity", 0.6)
        self.expressiveness = cfg.get("expressiveness", 0.7)

        # runtime state
        self.state = self.default_state
        self.last_state_change = time.time()

    # ------------------------------------------------------------
    # State Management
    # ------------------------------------------------------------
    def set_state(self, new_state):
        if new_state != self.state:
            self.log.info(f"[MASCOT] State change: {self.state} ---> {new_state}")
            self.state = new_state
            self.last_state_change = time.time()

            # force display refresh
            display = getattr(self.runtime, "display", None)
            if display:
                display.render_active_view()

    def decay_state(self):
        """Return to default state after inactivity."""
        if time.time() - self.last_state_change >= self.state_decay_seconds:
            self.set_state(self.default_state)

    # ------------------------------------------------------------
    # Event Hooks
    # ------------------------------------------------------------
    def on_user_interaction(self):
        self.set_state("excited")

    def on_new_ap(self):
        if random.random() < self.curiosity:
            self.set_state("curious")

    def on_handshake_captured(self):
        if random.random() < self.pride:
            self.set_state("proud")

    def on_system_health(self, health_score):
        """health_score: 0.0 (bad) ---> 1.0 (perfect)"""
        if health_score < (1 - self.sensitivity):
            self.set_state("annoyed")

    def on_idle(self):
        if random.random() > self.patience:
            self.set_state("bored")

    # ------------------------------------------------------------
    # Called every heartbeat
    # ------------------------------------------------------------
    def tick(self):
        if not self.enabled:
            return

        self.decay_state()

    # ------------------------------------------------------------
    # Rendering hook
    # ------------------------------------------------------------
    def get_sprite_for_state(self):
        """
        Returns the sprite/state name for the current state.
        The DisplayRenderer will load:
        extensions/display/assets/mascot/<state>.png
        """
        return self.state
