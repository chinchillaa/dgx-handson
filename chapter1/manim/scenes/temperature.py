"""Temperature を変えると、softmax 後の確率分布の形が変わる様子を見せるアニメーション

値は supplement_inference_params.html の Section 1 の図と同じ
（トークン「猫」「犬」「鳥」「魚」「虫」、logits = [3.0, 2.0, 1.5, 0.8, 0.2]、確率 = softmax(logits / T)）。
T = 0.5 / 1.0 / 2.0 のときの確率は、図のコメントの値（0.83 / 0.57 / 0.38 …）と一致する。
推奨範囲（0.0 – 0.3、1.5 を超えると破綻しやすい）も同ページの表と注意書きに合わせている。
"""
import numpy as np
from manim import *

from theme import *

TOKENS = ["猫", "犬", "鳥", "魚", "虫"]
LOGITS = np.array([3.0, 2.0, 1.5, 0.8, 0.2])


def probs(t):
    z = LOGITS / t
    e = np.exp(z - z.max())
    return e / e.sum()


class TemperatureScene(Scene):
    def construct(self):
        head = title("Temperature：logit を T で割ってから softmax にかける")
        self.add(head)

        # ── 棒グラフ（左） ─────────────────────────
        ax = Axes(x_range=[0, 5, 1], y_range=[0, 1, 0.25], x_length=7.0, y_length=3.6,
                  axis_config={"color": MUTED, "include_tip": False},
                  x_axis_config={"include_ticks": False})
        ax.to_edge(LEFT, buff=1.9).shift(UP * 0.35)
        ax.add(tick_labels(ax, [], [0, 0.25, 0.5, 0.75, 1]))
        ylab = jp("確率", 20, TEXT_SUB).next_to(ax.y_axis, UP, buff=0.3)
        xs = [ax.c2p(i + 0.5, 0)[0] for i in range(5)]
        tok_labels = VGroup(*[jp(f"「{t}」", 24, TEXT).move_to([x, ax.c2p(0, 0)[1] - 0.32, 0])
                              for x, t in zip(xs, TOKENS)])

        # logit と logit ÷ T の行
        row_y1 = tok_labels.get_bottom()[1] - 0.38
        row_y2 = row_y1 - 0.48
        name_x = xs[0] - 0.75
        name1 = jp("logit", 20, TEXT_SUB).move_to([0, row_y1, 0]).align_to([name_x, 0, 0], RIGHT)
        name2 = jp("logit ÷ T", 20, AMBER, "BOLD").move_to([0, row_y2, 0]).align_to([name_x, 0, 0], RIGHT)
        logit_row = VGroup(*[jp(f"{v:.1f}", 22, TEXT_SUB).move_to([x, row_y1, 0])
                             for x, v in zip(xs, LOGITS)])

        t = ValueTracker(1.0)

        def bars():
            p = probs(t.get_value())
            g = VGroup()
            for i, v in enumerate(p):
                h = max(ax.y_length * v, 0.02)
                r = Rectangle(width=0.95, height=h, stroke_width=0,
                              fill_color=GREEN if i == 0 else GREEN_MID,
                              fill_opacity=0.9 if i == 0 else 0.55)
                r.move_to([xs[i], ax.c2p(0, 0)[1], 0], aligned_edge=DOWN)
                g.add(r, jp(f"{v:.2f}", 22, TEXT).next_to(r, UP, buff=0.08))
            return g

        def div_row():
            return VGroup(*[jp(f"{v / t.get_value():.1f}", 22, AMBER).move_to([x, row_y2, 0])
                            for x, v in zip(xs, LOGITS)])

        bar_group = always_redraw(bars)
        divided = always_redraw(div_row)

        # ── 右：T の表示と計算の流れ ──────────────────
        t_box = RoundedRectangle(corner_radius=0.15, width=3.6, height=1.3,
                                 stroke_color=AMBER_BORDER, stroke_width=3,
                                 fill_color=BG, fill_opacity=1)
        t_box.to_edge(RIGHT, buff=0.8).shift(UP * 1.5)
        t_val = always_redraw(lambda: jp(f"T = {t.get_value():.2f}", 44, AMBER, "BOLD").move_to(t_box))
        flow = VGroup(
            jp("logit", 24, TEXT),
            jp("↓ ÷ T", 24, AMBER, "BOLD"),
            jp("softmax", 24, TEXT),
            jp("↓", 24, TEXT_SUB),
            jp("確率（棒の高さ）", 24, GREEN, "BOLD"),
        ).arrange(DOWN, buff=0.18).next_to(t_box, DOWN, buff=0.5)

        cap = caption("同じ logit でも、T で割ってから softmax にかけるので分布の形が変わる")
        self.play(FadeIn(ax), FadeIn(ylab), FadeIn(tok_labels), FadeIn(name1), FadeIn(logit_row),
                  FadeIn(cap))
        self.play(FadeIn(bar_group), FadeIn(name2), FadeIn(divided), FadeIn(t_box), FadeIn(t_val),
                  FadeIn(flow))
        self.wait(2)

        # ── T を下げる ──────────────────────────────
        self.play(Transform(cap, caption("T を下げると logit の差が広がり、1 位の「猫」に確率が集中する", GREEN)))
        self.play(t.animate.set_value(0.5), run_time=2.5)
        self.wait(1)
        self.play(t.animate.set_value(0.3), run_time=2)
        self.play(Transform(cap, caption("T = 0.3：「猫」が 0.96。確実・単調（コード生成や分類に向く 0.0 – 0.3）", GREEN)))
        self.wait(2.5)

        # ── T を上げる ──────────────────────────────
        self.play(Transform(cap, caption("T を上げると logit の差が縮み、分布が平らになる", AMBER)))
        self.play(t.animate.set_value(2.0), run_time=3.5)
        self.play(Transform(cap, caption("T = 2.0：「猫」は 0.38。多様だがばらつき大（1.5 を超えると破綻しやすい）", AMBER)))
        self.wait(2.5)

        # ── 標準に戻す ──────────────────────────────
        self.play(t.animate.set_value(1.0), run_time=2)
        self.play(Transform(cap, caption("T = 1.0 は logit をそのまま softmax にかける標準の動作")))
        self.wait(2.5)
