from __future__ import annotations
from dataclasses import dataclass
from typing import Optional, Dict, List, Set
import datetime
import fnmatch
import ipaddress
import yaml
import pathlib
from .categories import CategoryResolver


@dataclass
class PolicyDecision:
  action: str              # "allow", "block", "rewrite"
  reason: str
  rewrite_ip: Optional[str] = None


class PolicyEngine:
  def __init__(self, config: dict, categories: CategoryResolver):
      self.config = config
      self.categories = categories
      self.rules_path = pathlib.Path(
          config.get("policy", {}).get("rules_path", "")
      )
      self.rules = {}
      self._load_rules()

  def _load_rules(self):
      if not self.rules_path.exists():
          print("[DNS][policy] No policy.yaml found")
          self.rules = {}
          return
      try:
          self.rules = yaml.safe_load(self.rules_path.read_text()) or {}
          print("[DNS][policy] Loaded policy rules")
      except Exception as e:
          print("[DNS][policy] Failed to load policy.yaml:", e)
          self.rules = {}

  def evaluate(self, client_ip: str, qname: str) -> Optional[PolicyDecision]:
      # 1. Client-specific rules (allow/block/rewrite + categories)
      decision = self._evaluate_client_rules(client_ip, qname)
      if decision:
          return decision

      # 2. Time-based schedules
      decision = self._evaluate_schedules(qname)
      if decision:
          return decision

      # 3. Global rules (SafeSearch + categories)
      decision = self._evaluate_global(qname)
      if decision:
          return decision

      return None

  def _evaluate_client_rules(self, client_ip: str, qname: str) -> Optional[PolicyDecision]:
      clients = self.rules.get("clients", {})
      if not clients:
          return None

      try:
          ip = ipaddress.ip_address(client_ip)
      except ValueError:
          return None

      cats = self.categories.get_categories(qname)

      for rule_ip, rule in clients.items():
          try:
              if ip == ipaddress.ip_address(rule_ip):
                  for pattern in rule.get("allow", []):
                      if fnmatch.fnmatch(qname, pattern):
                          return PolicyDecision("allow", f"client_allow:{pattern}")

                  for pattern in rule.get("block", []):
                      if fnmatch.fnmatch(qname, pattern):
                          return PolicyDecision("block", f"client_block:{pattern}")

                  rewrites = rule.get("rewrite", {})
                  if qname in rewrites:
                      return PolicyDecision(
                          "rewrite",
                          f"client_rewrite:{qname}",
                          rewrite_ip=rewrites[qname],
                      )

                  block_cats = set(rule.get("block_categories", []))
                  if block_cats and cats & block_cats:
                      return PolicyDecision(
                          "block",
                          f"client_block_categories:{','.join(sorted(cats & block_cats))}",
                      )
          except Exception:
              continue

      return None

  def _evaluate_schedules(self, qname: str) -> Optional[PolicyDecision]:
      schedules = self.rules.get("schedules", {})
      if not schedules:
          return None

      now = datetime.datetime.now().time()

      for name, sched in schedules.items():
          try:
              start = datetime.datetime.strptime(sched["start"], "%H:%M").time()
              end = datetime.datetime.strptime(sched["end"], "%H:%M").time()

              in_window = (
                  start <= now <= end
                  if start < end
                  else now >= start or now <= end
              )

              if not in_window:
                  continue

              for pattern in sched.get("block", []):
                  if fnmatch.fnmatch(qname, pattern):
                      return PolicyDecision("block", f"schedule_block:{name}")

              for pattern in sched.get("allow", []):
                  if fnmatch.fnmatch(qname, pattern):
                      return PolicyDecision("allow", f"schedule_allow:{name}")

          except Exception:
              continue

      return None

  def _evaluate_global(self, qname: str) -> Optional[PolicyDecision]:
      global_rules = self.rules.get("global", {})

      if global_rules.get("enforce_safe_search", False):
          if qname in ("google.com", "www.google.com"):
              return PolicyDecision(
                  "rewrite",
                  "safe_search_google",
                  rewrite_ip="216.239.38.120",
              )
          if qname in ("youtube.com", "www.youtube.com"):
              return PolicyDecision(
                  "rewrite",
                  "safe_search_youtube",
                  rewrite_ip="216.239.38.120",
              )

      block_cats = set(global_rules.get("block_categories", []))
      if block_cats:
          cats = self.categories.get_categories(qname)
          if cats & block_cats:
              return PolicyDecision(
                  "block",
                  f"global_block_categories:{','.join(sorted(cats & block_cats))}",
              )

      return None
