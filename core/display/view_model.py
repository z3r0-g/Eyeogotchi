# core/display/view_model.py
from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class GridCell:
    text: str = ""
    value: str = ""
    icon: Optional[str] = None
    enabled: bool = True
    span: int = 1


@dataclass
class ViewModel:
    title: str
    mascot_state: Optional[dict] = None

    left_grid: List[GridCell] = field(default_factory=list)
    right_grid: List[GridCell] = field(default_factory=list)

    banner_text: Optional[str] = None

    # CASE FILE mode
    case_text: Optional[str] = None
    case_layout: Optional[str] = None
