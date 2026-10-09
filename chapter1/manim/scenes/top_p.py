"""Top-p（Nucleus）サンプリングで候補を絞り、残った候補から 1 つ選ぶまでを見せるアニメーション

値は supplement_inference_params.html の Section 2「Top-p サンプリング（Nucleus）」の図と同じ
（確率 = [0.50, 0.25, 0.17, 0.05, 0.03]、累積 = [0.50, 0.75, 0.92, 0.97, 1.00]、p = 0.9）。
transformers と同じく、累積確率が初めて p 以上になったトークン（3 位）までを残す。
再正規化は残った確率の合計 0.92 で割る。サンプリングの乱数 0.62 は説明用に固定した値。
最後に Top-k（同ページの図と同じ k = 3）と対比する。
"""
import numpy as np
from manim import *

from theme import *

RANKS = ["1位", "2位", "3位", "4位", "5位"]
P = np.array([0.50, 0.25, 0.17, 0.05, 0.03])
TOP_P = 0.9
CUM = np.cumsum(P)
KEEP = int(np.argmax(CUM >= TOP_P - 1e-9)) + 1  # 累積が初めて p 以上になった順位まで残す（= 3）
KEPT_SUM = P[:KEEP].sum()                          # 0.92
NEW_P = P[:KEEP] / KEPT_SUM                        # [0.54, 0.27, 0.18]
DRAW = 0.62                                        # 説明用に固定した乱数
PICK = int(np.searchsorted(np.cumsum(NEW_P), DRAW))  # 0.62 は 2 位の区間（0.54 – 0.82）


class TopPScene(Scene):
    def construct(self):
        head = title("Top-p（p = 0.9）：累積確率で候補を絞ってから選ぶ")
        self.add(head)

        # ── 棒グラフ（左） ─────────────────────────
        ax = Axes(x_range=[0, 5, 1], y_range=[0, 1, 0.25], x_length=6.0, y_length=3.3,
                  axis_config={"color": MUTED, "include_tip": False},
                  x_axis_config={"include_ticks": False})
        ax.to_edge(LEFT, buff=1.9).shift(UP * 0.7)
        ax.add(tick_labels(ax, [], [0, 0.25, 0.5, 0.75, 1]))
        y0 = ax.c2p(0, 0)[1]
        xs = [ax.c2p(i + 0.5, 0)[0] for i in range(5)]
        rank_labels = VGroup(*[jp(r, 22, TEXT).move_to([x, y0 - 0.3, 0]) for x, r in zip(xs, RANKS)])

        def bar(i, v, color=GREEN_MID, opacity=0.6):
            r = Rectangle(width=0.8, height=max(ax.y_length * v, 0.02), stroke_width=0,
                          fill_color=color, fill_opacity=opacity)
            return r.move_to([xs[i], y0, 0], aligned_edge=DOWN)

        bars = VGroup(*[bar(i, v, GREEN if i == 0 else GREEN_MID, 0.9 if i == 0 else 0.6)
                        for i, v in enumerate(P)])

        # 表の行：確率 / 累積 / 再正規化
        row_ys = [y0 - 0.75, y0 - 1.2, y0 - 1.65]
        name_x = xs[0] - 0.7

        def row_name(text, k, color):
            return jp(text, 20, color, "BOLD").move_to([0, row_ys[k], 0]).align_to([name_x, 0, 0], RIGHT)

        def cell(v, k, i, color):
            return jp(f"{v:.2f}", 22, color).move_to([xs[i], row_ys[k], 0])

        p_name = row_name("確率", 0, TEXT_SUB)
        p_row = VGroup(*[cell(v, 0, i, TEXT_SUB) for i, v in enumerate(P)])

        # p = 0.9 の線
        p_line = DashedLine(ax.c2p(0, TOP_P), ax.c2p(5, TOP_P), color=RED_BORDER, stroke_width=4,
                            dash_length=0.12)
        p_lab = jp("p = 0.9", 22, RED, "BOLD").next_to(p_line.get_end(), UP, buff=0.12).align_to(p_line, RIGHT)

        # 右のルール説明
        rule = VGroup(
            jp("Top-p のルール", 24, GREEN, "BOLD"),
            jp("確率の高い順に足していき、", 22, TEXT),
            jp("累積が初めて p 以上になった", 22, TEXT),
            jp("トークンまでを残す", 22, TEXT),
        ).arrange(DOWN, buff=0.16, aligned_edge=LEFT)
        rule_box = SurroundingRectangle(rule, buff=0.3, corner_radius=0.12, color=BORDER,
                                        stroke_width=2, fill_color=GREEN_BG, fill_opacity=1)
        rule_g = VGroup(rule_box, rule).to_edge(RIGHT, buff=0.6).shift(UP * 1.4)

        cap = caption("確率の高い順に並べた 5 トークン（資料の Top-p の図と同じ値）")
        self.play(FadeIn(ax), FadeIn(rank_labels), FadeIn(bars), FadeIn(p_name), FadeIn(p_row),
                  FadeIn(cap))
        self.play(Create(p_line), FadeIn(p_lab), FadeIn(rule_g))
        self.wait(1)

        # ── 累積確率を 1 つずつ足す ───────────────────
        c_name = row_name("累積", 1, AMBER)
        self.play(Transform(cap, caption("上位から確率を足して、累積確率が 0.9 に届くまで進む", AMBER)),
                  FadeIn(c_name))
        dots, segs, c_cells, steps = VGroup(), VGroup(), VGroup(), VGroup()
        for i in range(KEEP):
            hl = SurroundingRectangle(VGroup(bars[i], p_row[i]), buff=0.08, color=AMBER_BORDER,
                                      stroke_width=4)
            d = Dot(ax.c2p(i + 0.5, CUM[i]), radius=0.08, color=AMBER)
            c = cell(CUM[i], 1, i, AMBER)
            anims = [Create(hl), FadeIn(d, scale=0.5), FadeIn(c, shift=DOWN * 0.1)]
            if i > 0:
                s = Line(dots[-1].get_center(), d.get_center(), color=AMBER, stroke_width=4)
                segs.add(s)
                anims.append(Create(s))
            self.play(*anims, run_time=0.9)
            dots.add(d)
            c_cells.add(c)
            self.play(FadeOut(hl), run_time=0.4)

        stop = SurroundingRectangle(c_cells[-1], buff=0.08, color=RED, stroke_width=4)
        self.play(Create(stop), Flash(dots[-1], color=RED, flash_radius=0.3),
                  Transform(cap, caption("3 位で累積 0.92 ≥ 0.9。ここで止め、0.9 を超えた 3 位も残す", RED)))
        self.wait(1.5)

        # ── 4 位以降を除外 ─────────────────────────
        out_idx = range(KEEP, 5)
        excl = jp("除外", 24, RED, "BOLD").move_to([(xs[3] + xs[4]) / 2, ax.c2p(0, 0.3)[1], 0])
        cross = VGroup(*[Line(p_row[i].get_left(), p_row[i].get_right(), color=RED, stroke_width=3)
                         for i in out_idx])
        self.play(*[bars[i].animate.set_fill(MUTED, opacity=0.35) for i in out_idx],
                  *[rank_labels[i].animate.set_color(MUTED) for i in out_idx],
                  *[p_row[i].animate.set_color(MUTED) for i in out_idx],
                  Create(cross), FadeIn(excl),
                  Transform(cap, caption("4 位と 5 位は候補から除外する。もう選ばれることはない", RED)))
        self.wait(1.5)

        # ── 再正規化 ──────────────────────────────
        n_name = row_name("÷ 0.92", 2, GREEN)
        n_cells = VGroup(*[cell(v, 2, i, GREEN) for i, v in enumerate(NEW_P)])
        self.play(FadeOut(dots), FadeOut(segs), FadeOut(stop), FadeOut(p_line), FadeOut(p_lab),
                  Transform(cap, caption("残った 3 つを合計 0.92 で割り、合計が 1 になるようにそろえる（再正規化）", GREEN)))
        self.play(*[Transform(bars[i], bar(i, NEW_P[i], GREEN if i == 0 else GREEN_MID,
                                           0.9 if i == 0 else 0.6)) for i in range(KEEP)],
                  FadeIn(n_name), FadeIn(n_cells, shift=DOWN * 0.1), run_time=1.5)
        self.wait(1.5)

        # ── 1 回サンプリングする ─────────────────────
        seg_w = 4.6
        seg_colors = [GREEN, GREEN_MID, interpolate_color(GREEN_MID, GREEN_BG, 0.45)]
        strip = VGroup()
        left = 0.0
        for i, v in enumerate(NEW_P):
            r = Rectangle(width=seg_w * v, height=0.8, stroke_color=BG, stroke_width=3,
                          fill_color=seg_colors[i], fill_opacity=1)
            r.move_to(RIGHT * (left + v / 2) * seg_w)
            left += v
            strip.add(VGroup(r, jp(RANKS[i], 20, BG if i < 2 else TEXT, "BOLD").move_to(r)))
        strip_title = jp("残った 3 つから確率に比例して選ぶ", 22, GREEN, "BOLD")
        ends = VGroup(jp("0", 18, TEXT_SUB).next_to(strip, DOWN, buff=0.12).align_to(strip, LEFT),
                      jp("1", 18, TEXT_SUB).next_to(strip, DOWN, buff=0.12).align_to(strip, RIGHT))
        draw_g = VGroup(strip_title, VGroup(strip, ends)).arrange(DOWN, buff=1.0)
        draw_g.to_edge(RIGHT, buff=0.6).shift(UP * 1.0)
        x_left = strip.get_left()[0]
        strip_top = strip.get_top()[1]

        r_val = ValueTracker(0.0)
        pointer = always_redraw(lambda: Triangle(color=RED, fill_opacity=1, stroke_width=0)
                                .scale(0.14).rotate(PI)
                                .move_to([x_left + r_val.get_value() * seg_w, strip_top + 0.17, 0]))
        r_text = always_redraw(lambda: jp(f"乱数 {r_val.get_value():.2f}", 20, RED, "BOLD")
                               .next_to(pointer, UP, buff=0.08))
        self.play(FadeOut(rule_g), FadeIn(draw_g),
                  Transform(cap, caption("0〜1 の乱数が入った区間のトークンを出力する")))
        self.play(FadeIn(pointer), FadeIn(r_text))
        self.play(r_val.animate.set_value(1.0), run_time=1.2, rate_func=linear)
        self.play(r_val.animate.set_value(DRAW), run_time=1.3, rate_func=rate_functions.ease_out_cubic)
        picked = SurroundingRectangle(strip[PICK], buff=0.05, color=AMBER_BORDER, stroke_width=6)
        picked_bar = SurroundingRectangle(VGroup(bars[PICK], rank_labels[PICK]), buff=0.1,
                                          color=AMBER_BORDER, stroke_width=5)
        result = jp(f"→ {RANKS[PICK]} を出力", 26, AMBER, "BOLD").next_to(ends, DOWN, buff=0.35)
        self.play(Create(picked), Create(picked_bar), FadeIn(result),
                  Transform(cap, caption("今回は乱数 0.62 が 2 位の区間（0.54 〜 0.82）に入ったので 2 位を出力", AMBER)))
        self.wait(2)

        # ── Top-k との対比 ─────────────────────────
        topk = VGroup(
            jp("Top-k（k = 3）との違い", 22, GREEN, "BOLD"),
            jp("Top-k：確率に関係なく常に上位 3 個", 20, TEXT),
            jp("Top-p：分布の形で候補数が変わる", 20, TEXT),
        ).arrange(DOWN, buff=0.14, aligned_edge=LEFT)
        topk_box = SurroundingRectangle(topk, buff=0.22, corner_radius=0.12, color=BORDER,
                                        stroke_width=2, fill_color=GREEN_BG, fill_opacity=1)
        topk_g = VGroup(topk_box, topk).next_to(result, DOWN, buff=0.35).align_to(draw_g, RIGHT)
        self.play(FadeIn(topk_g),
                  Transform(cap, caption("この分布ではどちらも同じ 3 個が残る。平たい分布なら Top-p は候補が増える")))
        self.wait(3)
