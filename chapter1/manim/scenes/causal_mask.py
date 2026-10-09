"""因果マスクで未来のトークンへの注目を 0 にし、生成時に三角形が 1 行ずつ伸びる様子を見せるアニメーション

値はハンズオン③ Part 3（notebooks/ch1_03_llm_inference.ipynb）の causal_self_attention() と同じ。
入力は Part 2 の「ネコ・が・サカナ・食べた」の X、W_Q、W_K（self_attention.py と同じ）。
"""
import math

import numpy as np
from manim import *

from theme import *

RED_BG = ManimColor("#FEF2F2")  # web-theme.css の --red-bg

TOKENS = ["ネコ", "が", "サカナ", "食べた"]
X = np.array([
    [1.0, 0.0, 1.0, 0.0],
    [0.2, 0.0, 0.0, 0.0],
    [1.0, 0.0, 0.5, 1.0],
    [0.0, 1.0, 0.0, 0.0],
])
W_Q = np.array([[0, 0], [0, 3], [3, 0], [0, 0]], dtype=float)
W_K = np.array([[0, 0], [0, 0], [3, 0], [0, 3]], dtype=float)
T = len(TOKENS)
GA = 1  # 「が」の行（マスクの前後で値が大きく変わる）


def softmax(s):
    e = np.exp(s - s.max(axis=1, keepdims=True))
    return e / e.sum(axis=1, keepdims=True)


Q, K = X @ W_Q, X @ W_K
SCORES = Q @ K.T / math.sqrt(2)
FUTURE = np.triu(np.ones((T, T), dtype=bool), k=1)  # j > i
W_FULL = softmax(SCORES)
W_CAUSAL = softmax(np.where(FUTURE, -np.inf, SCORES))


def masked_cell(cell, text, size=24):
    """セル cell と同じ位置・大きさの「禁止」セル"""
    sq = Square(side_length=cell[0].width, stroke_color=RED_BORDER, stroke_width=1.5)
    sq.set_fill(RED_BG, opacity=1).move_to(cell)
    return VGroup(sq, jp(text, size, RED, "BOLD").move_to(sq))


def lines(*texts, size=24, color=TEXT_SUB, weight="NORMAL"):
    """複数行の文字列（Text の改行は行間が詰まるため、1 行ずつ並べる）"""
    return VGroup(*[jp(t, size, color, weight) for t in texts]).arrange(DOWN, buff=0.18, aligned_edge=LEFT)


class CausalMaskScene(Scene):
    def construct(self):
        head = title("因果マスク：自分より後ろのトークンは見せない")
        self.play(FadeIn(head))

        # ── 1. スコア行列 ────────────────────────────
        s_grid = matrix_grid(SCORES, TOKENS, TOKENS, vmax=SCORES.max())
        s_name = jp("スコア = Q Kᵀ / √2", 24, GREEN, "BOLD")
        s_block = VGroup(s_name, s_grid).arrange(DOWN, buff=0.3).to_edge(LEFT, buff=1.0).shift(DOWN * 0.15)
        side_r = jp("見る側", 18, MUTED).rotate(PI / 2).next_to(s_grid.row_labels, LEFT, buff=0.15)
        cap = caption("ハンズオン③ Part 2 の 4 トークン。各行が「その行のトークンがどこを見るか」")
        self.play(FadeIn(s_block), FadeIn(side_r), FadeIn(cap))
        self.wait(1.5)

        # ── 2. 上三角を −∞ に ──────────────────────────
        masks = VGroup(*[masked_cell(s_grid.cells[i][j], "−∞")
                         for i in range(T) for j in range(T) if FUTURE[i, j]])
        cap2 = caption("自分より後ろ（j > i）のスコアを、softmax の前に −∞ に置き換える", RED)
        self.play(Transform(cap, cap2))
        self.play(LaggedStart(*[FadeIn(m, scale=1.2) for m in masks], lag_ratio=0.15), run_time=1.5)
        self.wait(1.5)

        # ── 3. 行ごとに softmax ─────────────────────────
        w_grid = matrix_grid(W_CAUSAL, TOKENS, TOKENS)
        w_name = jp("注目度 = softmax（行ごと）", 24, GREEN, "BOLD")
        w_block = VGroup(w_name, w_grid).arrange(DOWN, buff=0.3).to_edge(RIGHT, buff=1.0)
        w_block.align_to(s_block, UP)
        zeros = VGroup(*[masked_cell(w_grid.cells[i][j], "0", 26)
                         for i in range(T) for j in range(T) if FUTURE[i, j]])
        arrow = Arrow(s_grid.get_right(), w_grid.row_labels.get_left(), color=MUTED, buff=0.25)
        cap3 = caption("e^(−∞) = 0 なので、未来への注目度はちょうど 0 になる", GREEN)
        self.play(GrowArrow(arrow), FadeIn(w_name), FadeIn(w_grid.col_labels), FadeIn(w_grid.row_labels),
                  Transform(cap, cap3))
        self.play(LaggedStart(*[TransformFromCopy(s_grid.cells[i][j], w_grid.cells[i][j])
                                for i in range(T) for j in range(T) if not FUTURE[i, j]], lag_ratio=0.08),
                  LaggedStart(*[TransformFromCopy(m, z) for m, z in zip(masks, zeros)], lag_ratio=0.08),
                  run_time=2)
        self.wait(1.5)

        # ── 4. 1 行を取り出して前後を比べる ──────────────────
        self.play(FadeOut(VGroup(s_block, side_r, masks, arrow)),
                  VGroup(w_name, w_grid, zeros).animate.to_edge(LEFT, buff=1.0))
        box = row_box(w_grid, GA)
        rows = VGroup()
        for label, vals, color in (("マスクなし", W_FULL[GA], RED), ("マスクあり", W_CAUSAL[GA], GREEN)):
            g = matrix_grid([vals], ["「が」の行"], TOKENS, cell=0.9, label_size=17)
            for j in range(T):
                if FUTURE[GA, j] and color == GREEN:
                    g.cells[0][j].become(masked_cell(g.cells[0][j], "0", 26))
            total = jp(f"合計 {vals.sum():.2f}", 22, TEXT_SUB).next_to(g.grid, RIGHT, buff=0.3)
            name = jp(label, 22, color, "BOLD").next_to(g, UP, buff=0.2).align_to(g, LEFT)
            rows.add(VGroup(name, g, total))
        rows.arrange(DOWN, buff=0.6, aligned_edge=LEFT).to_edge(RIGHT, buff=0.7).shift(DOWN * 0.1)
        cap4 = caption(f"「が」は 4 つに {W_FULL[GA, 0]:.2f} ずつ → 過去の 2 つに {W_CAUSAL[GA, 0]:.2f} ずつ。合計は 1 のまま")
        self.play(Create(box), FadeIn(rows[0]), Transform(cap, cap4))
        self.wait(1)
        self.play(TransformFromCopy(rows[0], rows[1]), run_time=1.3)
        self.wait(2.5)

        # ── 5. 生成時：1 トークンずつ三角形が伸びる ───────────────
        self.play(*[FadeOut(m) for m in self.mobjects if m not in (head, cap)])
        g_grid = matrix_grid(W_CAUSAL, TOKENS, TOKENS, cell=0.95)
        g_grid.move_to(LEFT * 2.6 + DOWN * 0.35)
        ghost = VGroup(*[Square(side_length=0.95, stroke_color=BORDER, stroke_width=1.5).move_to(c)
                         for row in g_grid.cells for c in row])
        side = VGroup(jp("生成した文", 22, TEXT_SUB))
        sentence = VGroup(*[jp(t, 30, TEXT, "BOLD") for t in TOKENS]).arrange(RIGHT, buff=0.3)
        sentence.next_to(side, DOWN, buff=0.35, aligned_edge=LEFT)
        note = lines("新しいトークンの行は", "自分と前のトークンだけを見る", color=GREEN, weight="BOLD")
        note2 = lines("前の行は、後から", "トークンが増えても変わらない")
        panel = VGroup(side, sentence, note, note2).arrange(DOWN, buff=0.55, aligned_edge=LEFT)
        sentence.shift(RIGHT * 0.2)
        panel.next_to(g_grid, RIGHT, buff=1.1).align_to(g_grid.grid, UP)
        cap5 = caption("生成するときは 1 トークンずつ。行が 1 本ずつ増え、三角形が伸びる")
        self.play(FadeIn(ghost), FadeIn(side), Transform(cap, cap5))
        for t in range(T):
            anims = [FadeIn(sentence[t], shift=RIGHT * 0.2), FadeIn(g_grid.row_labels[t]),
                     FadeIn(g_grid.col_labels[t])]
            anims += [FadeIn(g_grid.cells[t][j], scale=0.8) for j in range(t + 1)]
            if t == 0:
                anims.append(FadeIn(note))
            if t == 2:
                anims.append(FadeIn(note2))
            self.play(*anims, run_time=0.9)
            self.wait(0.6)
        self.wait(1)
        cap6 = caption("未来のトークンは計算に使えない。これが LLM が左から右にしか書けない理由", GREEN)
        self.play(Transform(cap, cap6), Create(row_box(g_grid, T - 1)))
        self.wait(3)
