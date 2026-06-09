from __future__ import annotations
import time
from collections import Counter
from typing import Dict, Iterable


class DNSTelemetry:
  def __init__(self):
      self.total_queries = 0
      self.blocked_queries = 0
      self.suspicious_queries = 0
      self.by_domain: Counter[str] = Counter()
      self.by_client: Counter[str] = Counter()
      self.by_category: Counter[str] = Counter()
      self.blocked_by_category: Counter[str] = Counter()

  def record_query(self, qname: str, client: str, categories: Iterable[str]):
      self.total_queries += 1
      self.by_domain[qname] += 1
      self.by_client[client] += 1
      for c in categories:
          self.by_category[c] += 1

  def record_block(self, categories: Iterable[str]):
      self.blocked_queries += 1
      for c in categories:
          self.blocked_by_category[c] += 1

  def record_suspicious(self):
      self.suspicious_queries += 1

  def snapshot(self) -> Dict:
      return {
          "timestamp": time.time(),
          "total_queries": self.total_queries,
          "blocked_queries": self.blocked_queries,
          "suspicious_queries": self.suspicious_queries,
          "top_domains": self.by_domain.most_common(10),
          "top_clients": self.by_client.most_common(10),
          "top_categories": self.by_category.most_common(10),
          "blocked_categories": self.blocked_by_category.most_common(10),
      }
