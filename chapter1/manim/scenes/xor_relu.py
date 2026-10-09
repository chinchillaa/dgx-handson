"""隠れ層（線形変換 + ReLU）が平面を曲げ、XOR を 1 本の直線で分けられるようにするアニメーション

h = ReLU(W x + b)、W = [[2, -1], [-1, 2]]、b = [-0.5, -0.5]
変換後は ○ が (1.5, 0) と (0, 1.5)、× が (0, 0) と (0.5, 0.5) に移り、
直線 h1 + h2 = 1.25 で分けられる。
"""
import numpy as np
from manim import *

from theme import *

U = 1.5  # 平面の 1 目盛りの長さ
O = np.array([-0.75, -0.55, 0.0])  # 平面の原点の画面上の位置（4 点が中央に来るように）
W = np.array([[2.0, -1.0], [-1.0, 2.0]])
B = np.array([-0.5, -0.5])
POINTS = [((0, 0), 0), ((0, 1), 1), ((1, 0), 1), ((1, 1), 0)]  # (x1, x2), XOR の答え


def to_scene(p):
    return O + np.array([p[0] * U, p[1] * U, 0.0])


def marker(label):
    if label == 1:
        return Circle(radius=0.17, stroke_color=GREEN_MID, stroke_width=7).set_fill(BG, 1)
    d = 0.15
    return VGroup(Line([-d, -d, 0], [d, d, 0]), Line([-d, d, 0], [d, -d, 0])).set_stroke(RED, 7)


def relu_scene(p):
    """画面上の点 p に、平面の原点 O を基準とした ReLU を適用する"""
    d = p - O
    return O + np.array([max(d[0], 0.0), max(d[1], 0.0), 0.0])


class XorReluScene(Scene):
    def construct(self):
        plane = NumberPlane(
            x_range=[-6, 6, 1], y_range=[-5, 5, 1], x_length=12 * U, y_length=10 * U,
            background_line_style={"stroke_color": BORDER, "stroke_width": 2},
            axis_config={"stroke_color": MUTED, "stroke_width": 3},
        ).move_to(O)
        plane.prepare_for_nonlinear_transform(60)
        self.add(plane)

        head = title("隠れ層は平面を曲げて、XOR を直線で分けられるようにする")
        head.add_background_rectangle(color=BG, opacity=0.92, buff=0.12)
        ax_lbl = VGroup(jp("x₁", 26, TEXT_SUB).move_to(to_scene((1.9, -0.22))),
                        jp("x₂", 26, TEXT_SUB).move_to(to_scene((-0.22, 1.9))))
        marks = VGroup()
        for (p, y) in POINTS:
            m = marker(y).move_to(to_scene(p))
            m.data_point = np.array(p, dtype=float)
            marks.add(m)
        self.play(FadeIn(head), FadeIn(ax_lbl), LaggedStart(*[GrowFromCenter(m) for m in marks], lag_ratio=0.2))

        cap = caption("XOR：入力が異なると 1（○）、同じだと 0（×）。1 本の直線では分けられない")
        cap.add_background_rectangle(color=BG, opacity=0.92, buff=0.1)
        self.play(FadeIn(cap))

        # 直線を回して、どの向きでも分けられないことを見せる
        pivot = to_scene((0.5, 0.5))
        trial = DashedLine(pivot + LEFT * 3.6, pivot + RIGHT * 3.6, color=AMBER, stroke_width=5)
        self.play(Create(trial))
        self.play(Rotate(trial, PI, about_point=pivot), run_time=3, rate_func=linear)
        self.play(FadeOut(trial))
        self.wait(0.5)

        # ① 線形変換 W x + b
        cap1 = caption("① 線形変換 Wx + b：平面が伸びて傾くだけ。まだ直線では分けられない")
        cap1.add_background_rectangle(color=BG, opacity=0.92, buff=0.1)
        self.play(Transform(cap, cap1), FadeOut(ax_lbl))
        lin = [W @ m.data_point for m in marks]
        self.play(ApplyMatrix(W, plane, about_point=O),
                  *[m.animate.move_to(to_scene(p)) for m, p in zip(marks, lin)], run_time=2.5)
        shifted = [p + B for p in lin]
        self.play(plane.animate.shift(to_scene(B) - O),
                  *[m.animate.move_to(to_scene(p)) for m, p in zip(marks, shifted)], run_time=1.5)
        self.wait(1.5)

        # ② ReLU で負の部分を 0 に折りたたむ
        cap2 = caption("② ReLU：負の値を 0 に折りたたむ。○ が外側、× が内側に集まる", GREEN)
        cap2.add_background_rectangle(color=BG, opacity=0.92, buff=0.1)
        self.play(Transform(cap, cap2))
        self.play(plane.animate.apply_function(relu_scene),
                  *[m.animate.move_to(relu_scene(to_scene(p))) for m, p in zip(marks, shifted)],
                  run_time=3)
        h_lbl = VGroup(jp("h₁", 26, TEXT_SUB).move_to(to_scene((1.9, -0.22))),
                       jp("h₂", 26, TEXT_SUB).move_to(to_scene((-0.22, 1.9))))
        self.play(FadeIn(h_lbl))
        self.wait(1)

        # ③ 1 本の直線で分けられる
        c = 1.25
        sep = DashedLine(to_scene((c + 0.6, -0.6)), to_scene((-0.6, c + 0.6)), color=AMBER, stroke_width=6)
        cap3 = caption("③ 直線 h₁ + h₂ = 1.25 で ○ と × を分けられるようになった", GREEN)
        cap3.add_background_rectangle(color=BG, opacity=0.92, buff=0.1)
        self.play(Create(sep), Transform(cap, cap3))
        self.wait(2)
        cap4 = caption("線形変換だけなら何層重ねても①のまま。活性化関数が「曲げる」ことで解ける")
        cap4.add_background_rectangle(color=BG, opacity=0.92, buff=0.1)
        self.play(Transform(cap, cap4))
        self.wait(3)
