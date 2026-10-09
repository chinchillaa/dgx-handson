"""RNN の逐次処理と Self-Attention の一括処理を上下に並べて比べるアニメーション

トークンと注目度は supplement_transformer.html の図と同じ
（「私・は・昨日・食べた・寿司」、「食べた」の注目度 私 0.15・は 0.05・昨日 0.28・食べた 0.07・寿司 0.45）。
RNN の隠れ状態に占める「私」の割合は、薄れていく様子を示すためのイメージで、実測値ではない。
"""
import numpy as np
from manim import *

from theme import *

GREEN_BORDER = ManimColor("#A7CBB9")  # web-theme.css の --green-border
TOKENS = ["私", "は", "昨日", "食べた", "寿司"]
WEIGHTS = np.array([0.15, 0.05, 0.28, 0.07, 0.45])  # 資料の図の値（合計 1.00）
EAT = 3  # 「食べた」
XS = [-4.6, -2.3, 0.0, 2.3, 4.6]
DECAY = 0.62  # イメージ用：1 ステップごとに古い情報の比重が下がる割合
BAR_W = 1.5


def share_bar(t):
    """t ステップ目の隠れ状態に、各トークンの情報がどれだけ残っているかのイメージ"""
    w = DECAY ** (t - np.arange(t + 1))
    w = w / w.sum()
    segs = VGroup()
    for k, wk in enumerate(w):
        color = AMBER_BORDER if k == 0 else GREEN_BORDER
        segs.add(Rectangle(width=BAR_W * wk, height=0.26, stroke_color=BG, stroke_width=2).set_fill(color, 1))
    segs.arrange(RIGHT, buff=0)
    frame = Rectangle(width=BAR_W, height=0.26, stroke_color=MUTED, stroke_width=1.2)
    segs.move_to(frame, aligned_edge=LEFT)
    return VGroup(segs, frame)


class RnnVsAttentionScene(Scene):
    def construct(self):
        head = title("RNN は順番に、Self-Attention は一度に")
        self.play(FadeIn(head))

        # ── 上段：RNN ───────────────────────────────
        top_lbl = jp("RNN：1 語ずつ順番に処理する", 26, GREEN, "BOLD").move_to([-6.6, 2.7, 0], aligned_edge=LEFT)
        legend = VGroup(
            Square(0.22, stroke_width=0).set_fill(AMBER_BORDER, 1), jp("「私」の情報", 18, TEXT_SUB),
            Square(0.22, stroke_width=0).set_fill(GREEN_BORDER, 1), jp("ほかの語の情報（割合はイメージ）", 18, TEXT_SUB),
        ).arrange(RIGHT, buff=0.12)
        legend[2].shift(RIGHT * 0.25)
        legend[3].shift(RIGHT * 0.25)
        legend.move_to([6.6, 2.7, 0], aligned_edge=RIGHT)
        boxes, hs, toks, ups = VGroup(), VGroup(), VGroup(), VGroup()
        for i, (x, t) in enumerate(zip(XS, TOKENS)):
            b = RoundedRectangle(corner_radius=0.12, width=1.8, height=1.05, stroke_color=GREEN_BORDER,
                                 stroke_width=2).set_fill(BG, 1).move_to([x, 1.45, 0])
            boxes.add(b)
            hs.add(jp(f"h{'₁₂₃₄₅'[i]}", 22, GREEN, "BOLD").move_to(b.get_top() + DOWN * 0.27))
            toks.add(jp(f"「{t}」", 22, TEXT_SUB).move_to([x, 0.45, 0]))
            ups.add(Arrow([x, 0.65, 0], b.get_bottom(), buff=0.04, color=MUTED, stroke_width=3,
                          max_tip_length_to_length_ratio=0.35))
        self.play(FadeIn(top_lbl), FadeIn(legend), FadeIn(boxes), FadeIn(hs), FadeIn(toks), FadeIn(ups))
        cap = caption("h₂ は h₁ が、h₃ は h₂ ができるまで計算できない。1 ステップずつ進む")
        self.play(FadeIn(cap))
        self.wait(0.5)

        bars = VGroup()
        for t in range(len(TOKENS)):
            anims = []
            if t > 0:
                anims.append(GrowArrow(Arrow(boxes[t - 1].get_right(), boxes[t].get_left(), buff=0.05,
                                             color=GREEN_MID, stroke_width=4)))
            bar = share_bar(t).move_to(boxes[t].get_center() + DOWN * 0.17)
            bars.add(bar)
            anims += [boxes[t].animate.set_fill(GREEN_BG, 0.5), toks[t].animate.set_color(TEXT),
                      FadeIn(bar)]
            self.play(*anims, run_time=1.0)
            self.wait(0.2)
        fade = DashedLine([XS[0] - 0.8, 2.15, 0], [XS[-1] + 0.8, 2.15, 0], color=AMBER_BORDER, stroke_width=3)
        fade.add_tip(tip_length=0.18, tip_width=0.18)
        cap2 = caption("先頭の「私」の情報は、運ばれるうちに薄れていく（イメージ）", AMBER)
        self.play(Create(fade), Transform(cap, cap2),
                  *[Indicate(b[0][0], color=AMBER, scale_factor=1.15) for b in bars])
        self.wait(2)

        # ── 下段：Self-Attention ───────────────────────────
        sep = Line([-6.8, 0.1, 0], [6.8, 0.1, 0], color=BORDER, stroke_width=2)
        bot_lbl = jp("Self-Attention：全トークンを一度に見る", 26, GREEN, "BOLD").move_to([-6.6, -0.35, 0],
                                                                                          aligned_edge=LEFT)
        tboxes = VGroup()
        for i, (x, t) in enumerate(zip(XS, TOKENS)):
            hl = i == EAT
            b = RoundedRectangle(corner_radius=0.12, width=1.6, height=0.7,
                                 stroke_color=GREEN_MID if hl else BORDER, stroke_width=3 if hl else 2)
            b.set_fill(GREEN_BG if hl else BG, 1).move_to([x, -2.55, 0])
            tboxes.add(VGroup(b, jp(t, 26, GREEN if hl else TEXT_SUB, "BOLD" if hl else "NORMAL").move_to(b)))
        cap3 = caption("「食べた」から全トークンへ直接つなぐ。どれだけ離れていても 1 ステップ")
        self.play(Create(sep), FadeIn(bot_lbl), FadeIn(tboxes), Transform(cap, cap3))

        src = tboxes[EAT][0].get_top()
        arcs, labels = VGroup(), VGroup()
        for i, w in enumerate(WEIGHTS):
            color = GREEN_MID if w == WEIGHTS.max() else (AMBER if w >= 0.15 else MUTED)
            if i == EAT:
                arc = Arc(radius=0.22, start_angle=-PI / 6, angle=PI * 4 / 3, color=color, stroke_width=3)
                arc.move_to(src + UP * 0.24)
                lbl_pos = src + UP * 0.75
            else:
                side = np.sign(XS[i] - XS[EAT])
                start = src + RIGHT * (0.25 + 0.12 * abs(i - EAT)) * side
                end = tboxes[i][0].get_top() + UP * 0.02
                chord = abs(end[0] - start[0])
                sag = 0.25 + 0.14 * chord  # 弧の高さ（遠いトークンほど高く）
                arc = ArcBetweenPoints(start, end, angle=-4 * np.arctan(2 * sag / chord) * side,
                                       color=color, stroke_width=2 + 18 * w)
                lbl_pos = arc.point_from_proportion(0.85) + RIGHT * 0.5 * side + UP * 0.25
            arcs.add(arc)
            labels.add(jp(f"{w:.2f}", 22, color, "BOLD").move_to(lbl_pos))
        self.play(*[Create(a) for a in arcs], *[FadeIn(lb) for lb in labels], run_time=1.6)
        self.wait(1.5)
        cap4 = caption("5 本を同時に計算する。離れた「私」にも 0.15 で直接届き、合計は 1.00", GREEN)
        self.play(Transform(cap, cap4), Indicate(labels[0], color=AMBER), Indicate(labels[4], color=GREEN_MID))
        self.wait(2.5)

        cap5 = caption("RNN の「薄れる」「順番待ち」を、Transformer は Attention だけで解決した", GREEN)
        self.play(Transform(cap, cap5))
        self.wait(3)
