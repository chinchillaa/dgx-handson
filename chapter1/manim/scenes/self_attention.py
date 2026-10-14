"""Attention の計算を 1 ステップずつ追うアニメーション

値は supplement_transformer.html の Section 2「計算してみましょう」と同じ。
例文「太郎はリンゴを食べた。それは甘かった。」の前半 7 トークンで、「それ」の行を計算する。
Q・K・V は「人か」「食べ物か」の 2 つの数字だけで表す（d_k = 2）。
"""
import math

import numpy as np
from manim import *

from theme import *

TOKENS = ["太郎", "は", "リンゴ", "を", "食べた", "。", "それ"]
COLS = ["人か", "食べ物か"]
APPLE, TARO = 2, 0
Q_SORE = np.array([0.0, 3.0])          # 「それ」は食べ物を探している
# Multi-Head の例：「食べた」の 2 つのヘッド（因果マスクに合わせ、食べたより前の 5 単語だけ）
N_EAT = 5                              # 太郎・は・リンゴ・を・食べた
Q_WHO = np.array([3.0, 0.0])           # 「誰が食べた？」のヘッド：人を探す
Q_WHAT = np.array([0.0, 3.0])          # 「何を食べた？」のヘッド：食べ物を探す
K = np.zeros((7, 2))
K[TARO] = [3, 0]                       # 太郎は人である
K[APPLE] = [0, 3]                      # リンゴは食べ物である
V = np.zeros((7, 2))
V[TARO] = [1, 0]
V[APPLE] = [0, 1]


def softmax(s):
    e = np.exp(s - s.max())
    return e / e.sum()


RAW = K @ Q_SORE                       # 内積（合い具合）: リンゴ 9、ほか 0
SCALED = RAW / math.sqrt(2)            # √2 で割る: リンゴ 6.36
WEIGHTS = softmax(SCALED)              # 参考にする割合: リンゴ 0.99、ほか 0.002
OUT = WEIGHTS @ V                      # 混ぜた結果: (0.00, 0.99)
W_WHO = softmax(K[:N_EAT] @ Q_WHO / math.sqrt(2))     # 太郎 0.99、ほか 0.002
W_WHAT = softmax(K[:N_EAT] @ Q_WHAT / math.sqrt(2))   # リンゴ 0.99、ほか 0.002


def ratio(v):
    """割合の表示。0.01 未満は 0.002 のように 3 桁で見せる"""
    return f"{v:.3f}" if v < 0.01 else f"{v:.2f}"


def col_box(mgrid, j, color=AMBER_BORDER):
    """行列の j 列目を囲む枠"""
    col = VGroup(*[row[j] for row in mgrid.cells])
    return Rectangle(width=col.width + 0.12, height=col.height + 0.12,
                     stroke_color=color, stroke_width=5).move_to(col)


def lines(*texts, size=22, color=TEXT_SUB, weight="NORMAL"):
    return VGroup(*[jp(t, size, color, weight) for t in texts]).arrange(DOWN, buff=0.16, aligned_edge=LEFT)


class SelfAttentionScene(Scene):
    def construct(self):
        head = title("Attention の計算を 1 ステップずつ追う")
        self.play(FadeIn(head))

        # ── 0. 例文 ───────────────────────────────
        words = TOKENS + ["は", "甘かった", "。"]
        sent = VGroup(*[jp(w, 34, TEXT, "BOLD") for w in words]).arrange(RIGHT, buff=0.22).shift(UP * 0.4)
        sent[6].set_color(GREEN)
        mark = SurroundingRectangle(sent[6], color=GREEN_MID, buff=0.12, stroke_width=4)
        apple = SurroundingRectangle(sent[APPLE], color=AMBER_BORDER, buff=0.12, stroke_width=4)
        arrow = CurvedArrow(sent[6].get_top() + UP * 0.2, sent[APPLE].get_top() + UP * 0.2,
                            angle=PI / 3, color=AMBER, stroke_width=4)
        q = jp("？", 34, AMBER, "BOLD").next_to(arrow, UP, buff=0.1)
        cap = caption("「それ」が何を指すかを、計算で確かめます")
        self.play(FadeIn(sent), FadeIn(cap))
        self.play(Create(mark))
        self.play(Create(arrow), FadeIn(q), Create(apple))
        self.wait(1.5)
        self.play(FadeOut(VGroup(sent, mark, apple, arrow, q)))

        # ── 1. Q と K ─────────────────────────────
        q_grid = matrix_grid([Q_SORE], ["それ"], COLS, fmt="{:.0f}", vmax=3, cell=1.0, label_size=18)
        q_block = VGroup(jp("Q：探しているもの", 24, GREEN, "BOLD"), q_grid).arrange(DOWN, buff=0.3)
        k_grid = matrix_grid(K.T, COLS, TOKENS, fmt="{:.0f}", vmax=3, cell=0.9, label_size=18)
        k_block = VGroup(jp("K：自分が何者か", 24, GREEN, "BOLD"), k_grid).arrange(DOWN, buff=0.3)
        VGroup(q_block, k_block).arrange(DOWN, buff=0.6).shift(DOWN * 0.2)
        cap1 = caption("「それ」は食べ物を探しています（Q）。各単語は自分が何者かを示します（K）")
        self.play(FadeIn(q_block, shift=DOWN), FadeIn(k_block, shift=UP), Transform(cap, cap1))
        self.wait(1)
        self.play(Create(row_box(q_grid, 0)), Create(col_box(k_grid, APPLE, GREEN_MID)),
                  Create(col_box(k_grid, TARO, MUTED)))
        cap1b = caption("リンゴは「食べ物」(0, 3)、太郎は「人」(3, 0) です")
        self.play(Transform(cap, cap1b))
        self.wait(2)
        self.play(*[FadeOut(m) for m in self.mobjects if m not in (head, cap)])

        # ── 2. 合い具合（内積）と √2 ─────────────────────
        raw = matrix_grid([RAW], ["内積"], TOKENS, fmt="{:.0f}", vmax=9, cell=1.0, label_size=18)
        sc = matrix_grid([SCALED], ["÷ √2"], fmt="{:.2f}", vmax=SCALED.max(), cell=1.0, label_size=18)
        name = jp("合い具合：「それ」の Q と各単語の K の内積", 24, GREEN, "BOLD")
        stack = VGroup(name, raw, sc).arrange(DOWN, buff=0.45).shift(UP * 0.3)
        sc.shift(RIGHT * (raw.grid.get_left()[0] - sc.grid.get_left()[0]))
        calc = jp("リンゴ：0 × 0 + 3 × 3 = 9　　太郎：0 × 3 + 3 × 0 = 0", 24, TEXT_SUB).next_to(stack, DOWN, buff=0.45)
        cap2 = caption("向きがそろうほど内積は大きくなります。合うのはリンゴだけです")
        self.play(FadeIn(name), FadeIn(raw), Transform(cap, cap2))
        self.play(Create(cell_box(raw, 0, APPLE)), FadeIn(calc))
        self.wait(2)
        cap2b = caption("√2（約 1.41）で割って、大きくなりすぎないようにします。9 ÷ 1.41 ≈ 6.36")
        self.play(TransformFromCopy(raw.grid, sc.grid), FadeIn(sc.row_labels), Transform(cap, cap2b), run_time=1.5)
        self.wait(2)

        # ── 3. softmax で割合に ───────────────────────
        w = matrix_grid([WEIGHTS], ["割合"], fmt=ratio, cell=1.0, label_size=18).move_to(sc, aligned_edge=LEFT)
        w.shift(DOWN * (sc.height + 0.45))
        cap3 = caption("softmax で合計 1 の割合に直します。「それ」はリンゴを 0.99 参考にします", GREEN)
        self.play(FadeOut(calc))
        self.play(TransformFromCopy(sc.grid, w.grid), FadeIn(w.row_labels), Transform(cap, cap3), run_time=1.6)
        self.play(Create(cell_box(w, 0, APPLE, GREEN_MID)))
        total = jp(f"合計 {WEIGHTS.sum():.2f}", 22, TEXT_SUB).next_to(w.grid, RIGHT, buff=0.3)
        self.play(FadeIn(total))
        self.wait(2.5)
        self.play(*[FadeOut(m) for m in self.mobjects if m not in (head, cap)])

        # ── 4. V を混ぜる ────────────────────────────
        w_row = matrix_grid([WEIGHTS], ["割合"], TOKENS, fmt=ratio, cell=0.9, font_size=19, label_size=18)
        v_grid = matrix_grid(V.T, ["V：人か", "V：食べ物か"], fmt="{:.0f}", cell=0.9, label_size=18)
        v_grid.next_to(w_row, DOWN, buff=0.35).align_to(w_row.grid, RIGHT)
        v_grid.shift(RIGHT * (w_row.grid.get_left()[0] - v_grid.grid.get_left()[0]))
        left = VGroup(jp("割合 × V（相手へ渡す情報）", 24, GREEN, "BOLD"), VGroup(w_row, v_grid))
        left.arrange(DOWN, buff=0.3).to_edge(LEFT, buff=0.6).shift(UP * 0.4)
        out = matrix_grid([OUT], ["それ"], COLS, fmt="{:.2f}", cell=1.0, label_size=20)
        out_block = VGroup(jp("混ぜた結果", 24, GREEN, "BOLD"), out).arrange(DOWN, buff=0.3)
        out_block.to_edge(RIGHT, buff=0.7).align_to(v_grid, DOWN)
        eq = jp("0.002 × (1, 0) + 0.99 × (0, 1) + …  ≈ (0.00, 0.99)", 24, TEXT_SUB)
        eq.next_to(left, DOWN, buff=0.45).align_to(left, LEFT)
        cap4 = caption("割合に応じて、各単語の V を掛けて足し合わせます")
        self.play(FadeIn(left), Transform(cap, cap4))
        self.play(Create(col_box(w_row, APPLE, GREEN_MID)), Create(col_box(v_grid, APPLE, GREEN_MID)))
        self.wait(1)
        arrow = Arrow(v_grid.get_right(), out_block.get_left(), color=MUTED, buff=0.3)
        self.play(GrowArrow(arrow), FadeIn(out_block), FadeIn(eq))
        self.play(Create(cell_box(out, 0, 1, AMBER_BORDER)))
        cap4b = caption("「それ」に、リンゴの「食べ物である」という情報が入りました", GREEN)
        self.play(Transform(cap, cap4b))
        self.wait(2.5)
        self.play(*[FadeOut(m) for m in self.mobjects if m not in (head, cap)])

        # ── 5. Multi-Head：観点ごとに参考にする単語が変わる ──────────
        h1 = matrix_grid([W_WHO], ["誰が食べた？"], TOKENS[:N_EAT], fmt=ratio, cell=1.05, font_size=20, label_size=18)
        h2 = matrix_grid([W_WHAT], ["何を食べた？"], fmt=ratio, cell=1.05, font_size=20, label_size=18)
        q1 = jp("「食べた」の Q = (3, 0)", 20, TEXT_SUB).next_to(h1.grid, RIGHT, buff=0.3)
        q2 = jp("「食べた」の Q = (0, 3)", 20, TEXT_SUB).next_to(h2.grid, RIGHT, buff=0.3)
        heads = VGroup(VGroup(h1, q1), VGroup(h2, q2)).arrange(DOWN, buff=0.35, aligned_edge=RIGHT)
        heads[1].shift(RIGHT * (h1.grid.get_left()[0] - h2.grid.get_left()[0]))  # 2 段の表の列をそろえる
        name = jp("Multi-Head Attention：観点の違うヘッドを並べる", 24, GREEN, "BOLD")
        note = lines("※ 各ヘッドの役割は説明用の例です。実際には役割が人間に分かる形で",
                     "　 明確に分かれているとは限りません。", size=20, color=MUTED)
        VGroup(name, heads, note).arrange(DOWN, buff=0.5).shift(UP * 0.25)
        cap5 = caption("「誰が食べた？」のヘッドは太郎を、「何を食べた？」のヘッドはリンゴを参考にします")
        self.play(FadeIn(name), FadeIn(heads[0]), Transform(cap, cap5))
        self.play(Create(cell_box(h1, 0, TARO, GREEN_MID)))
        self.play(FadeIn(heads[1]))
        self.play(Create(cell_box(h2, 0, APPLE, GREEN_MID)))
        self.wait(1)
        self.play(FadeIn(note))
        self.wait(3.5)
