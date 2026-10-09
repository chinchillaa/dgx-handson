"""単語ベクトルの足し算・引き算で「王様 − 男性 + 女性 ≈ 女王」になる様子を 2 次元で見せるアニメーション

4 単語の位置は supplement_transformer.html の「単語埋め込み（Word Embedding）の考え方」の SVG と同じ配置
（SVG 座標 (cx, cy) を、原点 (20, 180) からの距離 ÷ 20 で dim₁, dim₂ に換算）。
女王だけは、計算結果と「ほぼ一致」することを示すため、SVG の位置からわずかにずらしている。
"""
import numpy as np
from manim import *

from theme import *

SVG_ORIGIN = np.array([20.0, 180.0])
SVG_POS = {"王様": (70, 60), "女王": (130, 60), "男性": (70, 130), "女性": (130, 130)}
VEC = {w: np.array([(cx - SVG_ORIGIN[0]) / 20, (SVG_ORIGIN[1] - cy) / 20]) for w, (cx, cy) in SVG_POS.items()}
VEC["女王"] = VEC["女王"] + np.array([0.2, 0.2])  # 実際の埋め込みでは完全には一致しない
RESULT = VEC["王様"] - VEC["男性"] + VEC["女性"]
NEAREST = min(VEC, key=lambda w: np.linalg.norm(VEC[w] - RESULT))


class EmbeddingScene(Scene):
    def construct(self):
        head = title("単語ベクトルの足し算・引き算で、意味を計算する")
        self.play(FadeIn(head))

        ax = Axes(x_range=[0, 7, 1], y_range=[0, 7, 1], x_length=5.2, y_length=5.2, tips=False,
                  axis_config={"stroke_color": MUTED, "stroke_width": 2.5, "include_ticks": False})
        ax.move_to([-3.2, 0.0, 0])
        grid = VGroup(*[Line(ax.c2p(v, 0), ax.c2p(v, 7)) for v in range(1, 8)],
                      *[Line(ax.c2p(0, v), ax.c2p(7, v)) for v in range(1, 8)]).set_stroke(BORDER, 1.5)
        ax_lbl = VGroup(jp("dim₁", 22, TEXT_SUB).next_to(ax.c2p(7, 0), RIGHT, buff=0.15),
                        jp("dim₂", 22, TEXT_SUB).next_to(ax.c2p(0, 7), LEFT, buff=0.15))

        def p(v):
            return ax.c2p(*v)

        dots, names = {}, VGroup()
        side = {"王様": UP, "女王": RIGHT, "男性": LEFT, "女性": RIGHT}
        for w, v in VEC.items():
            royal = w in ("王様", "女王")
            color = GREEN if royal else TEXT_SUB
            dots[w] = Dot(p(v), radius=0.09, color=GREEN if royal else MUTED)
            names.add(jp(w, 26, color, "BOLD" if royal else "NORMAL").next_to(dots[w], side[w], buff=0.15))
        cap = caption("単語は数値ベクトル、つまり空間の 1 点になる（ここでは 2 次元のイメージ）")
        self.play(Create(grid), Create(ax), FadeIn(ax_lbl), FadeIn(cap))
        self.play(LaggedStart(*[GrowFromCenter(d) for d in dots.values()], lag_ratio=0.15), FadeIn(names))
        self.wait(1.5)

        # ── 1. 平行な「方向」 ─────────────────────────────
        def dashed(a, b, color):
            line = DashedLine(p(VEC[a]), p(VEC[b]), buff=0.16, color=color, stroke_width=4, dash_length=0.12)
            return line.add_tip(tip_length=0.2, tip_width=0.2)

        gender = VGroup(dashed("男性", "女性", AMBER), dashed("王様", "女王", AMBER))
        rank = VGroup(dashed("男性", "王様", GREEN_MID), dashed("女性", "女王", GREEN_MID))
        g_lbl = jp("「性別」方向", 22, AMBER, "BOLD").next_to(gender[0], DOWN, buff=0.2)
        r_lbl = jp("「地位」方向", 22, GREEN_MID, "BOLD").rotate(PI / 2).next_to(rank[0], LEFT, buff=0.2)
        cap2 = caption("「男性→女性」と「王様→女王」は、ほぼ同じ向きと長さの矢印になる")
        self.play(LaggedStart(*[Create(a) for a in gender], lag_ratio=0.3), FadeIn(g_lbl), Transform(cap, cap2))
        self.wait(1)
        self.play(LaggedStart(*[Create(a) for a in rank], lag_ratio=0.3), FadeIn(r_lbl))
        self.wait(1.5)
        self.play(VGroup(gender, rank, g_lbl, r_lbl).animate.set_opacity(0.18))

        # ── 2. 王様 − 男性 + 女性 を矢印でつなぐ ─────────────────
        eq = VGroup(
            jp("v(王様)", 30, GREEN_MID, "BOLD"),
            jp("− v(男性)", 30, RED, "BOLD"),
            jp("+ v(女性)", 30, AMBER, "BOLD"),
            jp(f"≈ v({NEAREST})", 30, GREEN, "BOLD"),
        ).arrange(DOWN, buff=0.45, aligned_edge=LEFT).move_to([3.6, 0.6, 0])
        eq[3].shift(RIGHT * 0.3)
        mid = VEC["王様"] - VEC["男性"]
        steps = [
            (Arrow(p((0, 0)), p(VEC["王様"]), buff=0, color=GREEN_MID, stroke_width=6), eq[0],
             "原点から「王様」のベクトルへ"),
            (Arrow(p(VEC["王様"]), p(mid), buff=0, color=RED, stroke_width=6), eq[1],
             "「男性」のベクトルを引く（逆向きにたどる）"),
            (Arrow(p(mid), p(RESULT), buff=0, color=AMBER, stroke_width=6), eq[2],
             "「女性」のベクトルを足す（矢印を先端につなぐ）"),
        ]
        for arrow, term, text in steps:
            self.play(GrowArrow(arrow), FadeIn(term, shift=RIGHT * 0.2), Transform(cap, caption(text)), run_time=1.3)
            self.wait(1)
        res_dot = Dot(p(RESULT), radius=0.1, color=AMBER).set_z_index(3)
        res_lbl = jp("計算結果", 20, AMBER, "BOLD").next_to(res_dot, DOWN, buff=0.45).shift(RIGHT * 0.75)
        ring = Circle(radius=0.42, color=GREEN, stroke_width=4).move_to(p((RESULT + VEC[NEAREST]) / 2))
        cap4 = caption(f"着地点にいちばん近い単語は「{NEAREST}」。意味の計算がベクトルの演算でできる", GREEN)
        self.play(FadeIn(res_dot, scale=1.5), FadeIn(res_lbl))
        self.play(Create(ring), FadeIn(eq[3], shift=RIGHT * 0.2), Transform(cap, cap4))
        self.wait(2.5)

        # ── 3. −男性 + 女性 ＝「性別」方向 ─────────────────────
        net = Arrow(p(VEC["王様"]), p(RESULT), buff=0.12, color=AMBER, stroke_width=7)
        note = VGroup(jp("− v(男性) + v(女性)", 24, AMBER, "BOLD"), jp("＝「性別」方向の矢印", 24, AMBER)) \
            .arrange(DOWN, buff=0.15, aligned_edge=LEFT).next_to(eq, DOWN, buff=0.6, aligned_edge=LEFT)
        cap5 = caption("引いて足した分は「男性→女性」と同じ矢印。王様をその方向へ動かした")
        self.play(gender.animate.set_opacity(1), g_lbl.animate.set_opacity(1), GrowArrow(net),
                  FadeIn(note), Transform(cap, cap5))
        self.wait(2.5)
        cap6 = caption("実際の埋め込みは数百〜数千次元。この図は 2 次元に描いたイメージ")
        self.play(Transform(cap, cap6))
        self.wait(3)
