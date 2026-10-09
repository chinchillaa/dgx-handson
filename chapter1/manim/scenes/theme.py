"""第1章の Web 資料（assets/web-theme.css）に合わせた manim の配色とヘルパー"""
from manim import (
    BLACK, DOWN, LEFT, RIGHT, UP, ManimColor, Rectangle, Square, Text, VGroup, config,
    interpolate_color,
)

# web-theme.css の CSS 変数と同じ値
BG = ManimColor("#FFFFFF")          # --surface（資料のカード背景）
TEXT = ManimColor("#201C18")        # --text
TEXT_SUB = ManimColor("#57534E")    # --text-sub
MUTED = ManimColor("#A39C92")       # --text-muted
BORDER = ManimColor("#E0DACE")      # --border
GREEN = ManimColor("#0D4A38")       # --green
GREEN_MID = ManimColor("#1A6B52")   # --green-mid
GREEN_BG = ManimColor("#EAF3EF")    # --green-bg
AMBER = ManimColor("#7C5C00")       # --amber
AMBER_BORDER = ManimColor("#E8C96A")
RED = ManimColor("#991B1B")         # --red
RED_BORDER = ManimColor("#FCA5A5")

FONT = "Noto Sans CJK JP"

config.background_color = BG


def jp(text, size=28, color=TEXT, weight="NORMAL"):
    """日本語を含む文字列。数値もこのフォントでそろえる"""
    return Text(text, font=FONT, font_size=size, color=color, weight=weight)


def title(text):
    return jp(text, size=34, color=GREEN, weight="BOLD").to_edge(UP, buff=0.4)


def caption(text, color=TEXT_SUB):
    return jp(text, size=24, color=color).to_edge(DOWN, buff=0.35)


def heat(v, vmax=1.0, low=GREEN_BG, high=GREEN_MID):
    t = max(0.0, min(1.0, float(v) / vmax))
    return interpolate_color(low, high, t)


def matrix_grid(values, row_labels=None, col_labels=None, fmt="{:.2f}", cell=0.9,
                vmax=1.0, colored=True, font_size=24, label_size=17):
    """値を色の濃さで示す行列。返り値の .cells[i][j] で各セル（四角と数値）を参照できる"""
    rows, cols = len(values), len(values[0])
    grid = VGroup()
    cells = []
    for i in range(rows):
        row = []
        for j in range(cols):
            v = float(values[i][j])
            sq = Square(side_length=cell, stroke_color=BORDER, stroke_width=1.5)
            sq.set_fill(heat(v, vmax) if colored else BG, opacity=1)
            sq.move_to(RIGHT * j * cell + DOWN * i * cell)
            dark = colored and v / vmax > 0.55
            num = jp(fmt.format(v), size=font_size, color=BG if dark else TEXT).move_to(sq)
            g = VGroup(sq, num)
            row.append(g)
            grid.add(g)
        cells.append(row)
    out = VGroup(grid)
    if row_labels:
        rl = VGroup(*[jp(t, size=label_size, color=TEXT_SUB).next_to(cells[i][0], LEFT, buff=0.15)
                      for i, t in enumerate(row_labels)])
        out.add(rl)
        out.row_labels = rl
    if col_labels:
        cl = VGroup(*[jp(t, size=label_size, color=TEXT_SUB).next_to(cells[0][j], UP, buff=0.12)
                      for j, t in enumerate(col_labels)])
        out.add(cl)
        out.col_labels = cl
    out.cells = cells
    out.grid = grid
    return out


def row_box(mgrid, i, color=AMBER_BORDER):
    """行列の i 行目を囲む枠"""
    row = VGroup(*mgrid.cells[i])
    return Rectangle(width=row.width + 0.12, height=row.height + 0.12,
                     stroke_color=color, stroke_width=5).move_to(row)


def cell_box(mgrid, i, j, color=AMBER_BORDER):
    c = mgrid.cells[i][j]
    return Rectangle(width=c.width + 0.08, height=c.height + 0.08,
                     stroke_color=color, stroke_width=5).move_to(c)


def tick_labels(ax, xs, ys, fmt="{:g}", size=18):
    """LaTeX を使わずに軸の目盛りの数字を付ける（Axes.add_coordinates は LaTeX が必要なため）"""
    g = VGroup()
    for x in xs:
        g.add(jp(fmt.format(x), size, TEXT_SUB).next_to(ax.c2p(x, ax.y_range[0]), DOWN, buff=0.15))
    for y in ys:
        g.add(jp(fmt.format(y), size, TEXT_SUB).next_to(ax.c2p(ax.x_range[0], y), LEFT, buff=0.15))
    return g


__all__ = [n for n in dir() if not n.startswith("_")] + ["BLACK"]
