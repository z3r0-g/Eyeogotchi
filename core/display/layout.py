#core/display/layout.py
from dataclasses import dataclass

@dataclass
class GridSpec:
    x: int
    y: int
    width: int
    height: int
    cols: int
    rows: int


class ThreeColumnLayout:
    """
    3‑region layout with a dedicated bottom banner strip.
    """

    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height

        # Reserved bottom banner height
        self.banner_h = 16

        # Margins
        self.margin = 4
        self.col_gap = 6

        # Column widths
        total_gap = self.col_gap * 2
        col_width = (self.width - total_gap - (self.margin * 2)) // 3

        self.left_x = self.margin
        self.center_x = self.left_x + col_width + self.col_gap
        self.right_x = self.center_x + col_width + self.col_gap

        self.col_width = col_width

    # ------------------------------------------------------------ #
    # Left grid: 2 columns × 3 rows
    # ------------------------------------------------------------ #
    def left_grid_spec(self) -> GridSpec:
        usable_h = self.height - self.banner_h - 10
        return GridSpec(
            x=self.left_x,
            y=0,
            width=self.col_width,
            height=usable_h,
            cols=2,
            rows=3,
        )

    # ------------------------------------------------------------ #
    # Right grid: 2 columns × 3 rows
    # ------------------------------------------------------------ #
    def right_grid_spec(self) -> GridSpec:
        usable_h = self.height - self.banner_h - 10
        return GridSpec(
            x=self.right_x,
            y=0,
            width=self.col_width,
            height=usable_h,
            cols=2,
            rows=3,
        )

    # ------------------------------------------------------------ #
    # Center mascot region
    # ------------------------------------------------------------ #
    def center_region(self):
        usable_h = self.height - self.banner_h - 20
        return (
            self.center_x,
            20,
            self.col_width,
            usable_h,
        )

    # ------------------------------------------------------------ #
    # Banner region (full width)
    # ------------------------------------------------------------ #
    def banner_region(self):
        return (
            0,
            self.height - self.banner_h,
            self.width,
            self.banner_h,
        )
