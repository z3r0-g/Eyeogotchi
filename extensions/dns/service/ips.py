from __future__ import annotations
import math
from dataclasses import dataclass
from typing import Optional


@dataclass
class IPSDecision:
    suspicious: bool
    reason: str


class DNSIPS:
    def __init__(self, config: dict):
        self.config = config

    def analyze(self, qname: str) -> Optional[IPSDecision]:
        labels = qname.split(".")
        longest = max(labels, key=len, default="")
        entropy = self._shannon_entropy(longest)

        # Long, high-entropy label → possible DNS tunnel
        if len(longest) > 40 and entropy > 3.5:
            return IPSDecision(
                suspicious=True,
                reason="high_entropy_long_label_possible_tunnel",
            )

        # Too many subdomains → possible tunnel or beaconing
        if len(labels) > 6:
            return IPSDecision(
                suspicious=True,
                reason="many_subdomains_possible_tunnel",
            )

        return None

    def _shannon_entropy(self, s: str) -> float:
        if not s:
            return 0.0
        from collections import Counter

        counts = Counter(s)
        length = len(s)
        return -sum((c / length) * math.log2(c / length) for c in counts.values())
