# core/display/render.py
from __future__ import annotations

import io
import logging
import os
from typing import Optional

from PIL import Image, ImageDraw, ImageFont, ImageEnhance

from core.display.layout import ThreeColumnLayout
from core.display.view_model import ViewModel, GridCell


class DisplayRenderer:
    def __init__(self):
        self.log = logging.getLogger("eyeogotchi.display.renderer")

        self.log.info("Initializing e-ink display...")
        self.width = 250
        self.height = 122

        # Local framebuffer
        self.image = Image.new("1", (self.width, self.height), 255)
        self.draw = ImageDraw.Draw(self.image)

        # Fonts
        self.font = ImageFont.load_default()
        self.font_small = self.font

        # Case file typewriter state
        self.casefile_text: str = ""
        self.casefile_cursor: int = 0

        # Typewriter speed (CRT‑style)
        self.typewriter_step = 256

        # Blinking cursor state
        self.cursor_visible = True
        self.cursor_tick = 0
        self.cursor_rate = 20  # slow blink to avoid PNG churn

    # ------------------------------------------------------------------ #
    # Core buffer helpers
    # ------------------------------------------------------------------ #

    def clear(self) -> None:
        self.image = Image.new("1", (self.width, self.height), 255)
        self.draw = ImageDraw.Draw(self.image)

    def render(self) -> None:
        pass

    def get_png_bytes(self) -> bytes:
        buf = io.BytesIO()
        self.image.save(buf, format="PNG")
        return buf.getvalue()

    # ------------------------------------------------------------------ #
    # Text helpers
    # ------------------------------------------------------------------ #

    def draw_text(self, x: int, y: int, text: str, font=None) -> None:
        if font is None:
            font = self.font
        self.draw.text((x, y), text, font=font, fill=0)

    def draw_text_centered(self, text: str, y: int, font=None) -> None:
        if font is None:
            font = self.font
        bbox = self.draw.textbbox((0, 0), text, font=font)
        w = bbox[2] - bbox[0]
        x = (self.width - w) // 2
        self.draw.text((x, y), text, font=font, fill=0)

    def draw_multiline_text(self, x: int, y: int, w: int, h: int, text: str, font=None) -> None:
        if font is None:
            font = self.font_small

        lines: list[str] = []
        for raw_line in text.split("\n"):
            words = raw_line.split(" ")
            current = ""
            for word in words:
                test = word if not current else current + " " + word
                bbox = self.draw.textbbox((0, 0), test, font=font)
                tw = bbox[2] - bbox[0]
                if tw <= w:
                    current = test
                else:
                    if current:
                        lines.append(current)
                    current = word
            if current:
                lines.append(current)

        line_height = self.draw.textbbox((0, 0), "A", font=font)[3]
        max_lines = h // line_height if line_height > 0 else len(lines)

        for i, line in enumerate(lines[:max_lines]):
            self.draw.text((x, y + i * line_height), line, font=font, fill=0)

    # ------------------------------------------------------------------ #
    # Mascot Rendering
    # ------------------------------------------------------------------ #

    def _load_mascot_sprite(self, state_name: str) -> Optional[Image.Image]:
        sprite_path = os.path.join(
            "extensions", "display", "assets", "mascot", f"{state_name}.png"
        )
        if not os.path.isfile(sprite_path):
            self.log.warning(f"[DISPLAY] Missing mascot sprite: {sprite_path}")
            return None

        try:
            return Image.open(sprite_path).convert("RGBA")
        except Exception as e:
            self.log.warning(f"[DISPLAY] Failed to load mascot sprite '{state_name}': {e}")
            return None

    def draw_mascot_centered(self, state_name: str, region: tuple[int, int, int, int]) -> None:
        sprite = self._load_mascot_sprite(state_name)
        if sprite is None:
            return

        x, y, w, h = region

        # Shrink mascot slightly
        target_h = int(h * 0.80)
        scale = target_h / sprite.height
        target_w = int(sprite.width * scale)

        sprite_resized = sprite.resize((target_w, target_h), Image.NEAREST)

        mx = x + (w - target_w) // 2
        my = y + (h - target_h) // 2

        if sprite_resized.mode == "RGBA":
            self.image.paste(sprite_resized, (mx, my), sprite_resized)
        else:
            self.image.paste(sprite_resized, (mx, my))

    # ------------------------------------------------------------------ #
    # Icon helpers
    # ------------------------------------------------------------------ #

    def _load_icon(self, name: str) -> Optional[Image.Image]:
        path = f"extensions/display/assets/icons/{name}.png"
        if not os.path.isfile(path):
            return None
        return Image.open(path).convert("L")

    def _apply_disabled_overlay(self, icon: Image.Image) -> Image.Image:
        enhancer = ImageEnhance.Brightness(icon)
        return enhancer.enhance(2.0)

    # ------------------------------------------------------------------ #
    # Grid rendering (system_status‑style)
    # ------------------------------------------------------------------ #

    def _draw_grid_cell(
        self,
        cell: GridCell,
        x: int,
        y: int,
        w: int,
        h: int,
        is_banner: bool = False,
    ) -> None:

        ICON_TOP = 2
        LABEL_GAP = 2
        VALUE_GAP = 1

        cursor_y = y + ICON_TOP

        # ICON
        if getattr(cell, "icon", None):
            icon = self._load_icon(cell.icon)
            if icon:
                target = min(w, h) - 12
                icon = icon.resize((target, target), Image.NEAREST)

                if getattr(cell, "enabled", True) is False:
                    icon = self._apply_disabled_overlay(icon)

                ix = x + (w - target) // 2
                self.image.paste(icon, (ix, cursor_y))

                cursor_y += target + LABEL_GAP

        # LABEL
        if cell.text:
            bbox = self.draw.textbbox((0, 0), cell.text, font=self.font_small)
            tw = bbox[2] - bbox[0]
            tx = x + (w - tw) // 2
            self.draw.text((tx, cursor_y), cell.text, font=self.font_small, fill=0)

            cursor_y += (bbox[3] - bbox[1]) + VALUE_GAP

        # VALUE
        if cell.value:
            bbox = self.draw.textbbox((0, 0), cell.value, font=self.font_small)
            vw = bbox[2] - bbox[0]
            vx = x + (w - vw) // 2
            self.draw.text((vx, cursor_y), cell.value, font=self.font_small, fill=0)

    def draw_grid(self, cells: list[GridCell], cols: int, rows: int, x: int, y: int, width: int, height: int) -> None:
        if not cells:
            return

        cell_w = width // cols
        cell_h = int((height // rows))

        idx = 0
        for row in range(rows):
            cx = x
            for col in range(cols):
                if idx >= len(cells):
                    return
                cell = cells[idx]
                span = max(1, getattr(cell, "span", 1))
                span_w = cell_w * span
                self._draw_grid_cell(cell, cx, y + row * cell_h, span_w, cell_h)
                cx += span_w
                idx += 1

    # ------------------------------------------------------------------ #
    # CASE FILE rendering (noir layout)
    # ------------------------------------------------------------------ #

    def _render_case_file(self, view: ViewModel) -> None:
        self.clear()

        width, height = self.width, self.height

        # Title
        title_h = 12
        if view.title:
            self.draw_text_centered(view.title, y=2, font=self.font_small)

        # Layout constants
        left_w = width // 3
        right_x = left_w + 4
        right_w = width - right_x - 4

        text_top = title_h + 4
        text_bottom = height - 28  # leave room for 2×2 grid

        # Mascot region
        if view.mascot_state:
            sprite_name = view.mascot_state
            mascot_region = (
                0,
                title_h + 4,
                left_w,
                height - title_h - 12,
            )
            self.draw_mascot_centered(sprite_name, mascot_region)

        # Typewriter text
        full_text = view.case_text or ""

        # Only reset when RAW text changes
        if full_text != self.casefile_text:
            self.casefile_text = full_text
            self.casefile_cursor = 0

        # Advance typewriter
        if self.casefile_cursor < len(self.casefile_text):
            self.casefile_cursor += self.typewriter_step

        # Build visible text (cursor added AFTER slicing)
        visible = self.casefile_text[: self.casefile_cursor]

        # Cursor behavior:
        # - Solid during typing
        # - Blink AFTER typing finishes
        if self.casefile_cursor < len(self.casefile_text):
            # Solid cursor during typing
            visible = visible + "_"
        else:
            # Blinking cursor after typing completes
            self.cursor_tick += 1
            if self.cursor_tick >= self.cursor_rate:
                self.cursor_tick = 0
                self.cursor_visible = not self.cursor_visible

            if self.cursor_visible:
                visible = visible + "_"

        self.draw_multiline_text(
            x=right_x,
            y=text_top,
            w=right_w,
            h=text_bottom - text_top,
            text=visible,
            font=self.font_small,
        )

        # Bottom-right 2×2 grid
        if view.right_grid:
            self.draw_grid(
                view.right_grid,
                cols=2,
                rows=2,
                x=right_x,
                y=height - 24,
                width=right_w,
                height=22,
            )

        self.render()

    # ------------------------------------------------------------------ #
    # High-level view rendering
    # ------------------------------------------------------------------ #

    def render_view(self, view: ViewModel) -> None:
        if getattr(view, "case_layout", None) == "case_file" and getattr(view, "case_text", None):
            self._render_case_file(view)
            return

        self.clear()

        layout = ThreeColumnLayout(self.width, self.height)

        if view.title:
            self.draw_text_centered(view.title, y=2, font=self.font_small)

        left_spec = layout.left_grid_spec()
        right_spec = layout.right_grid_spec()
        cx, cy, cw, ch = layout.center_region()

        top_offset = 20 if view.title else 4
        left_spec.y = top_offset
        right_spec.y = top_offset

        center_region = (
            cx,
            cy + 6,
            cw,
            ch - 12,
        )

        if view.mascot_state:
            sprite_name = view.mascot_state
            self.draw_mascot_centered(sprite_name, center_region)

        if view.left_grid:
            self.draw_grid(
                view.left_grid,
                cols=left_spec.cols,
                rows=left_spec.rows,
                x=left_spec.x,
                y=left_spec.y,
                width=left_spec.width,
                height=left_spec.height,
            )

        if view.right_grid:
            self.draw_grid(
                view.right_grid,
                cols=right_spec.cols,
                rows=right_spec.rows,
                x=right_spec.x,
                y=right_spec.y,
                width=right_spec.width,
                height=right_spec.height,
            )

        bx, by, bw, bh = layout.banner_region()
        if getattr(view, "banner_text", None):
            self.draw_text_centered(view.banner_text, by + 2, font=self.font_small)

        self.render()
