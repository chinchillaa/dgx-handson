"""因果マスクで後ろの単語を参考にする割合を 0 にし、生成時に三角形が 1 行ずつ伸びる様子を見せるアニメーション

例文と K は self_attention.py と同じ（「太郎はリンゴを食べた。それは甘かった。」の前半 7 トークン）。
Q は「食べた」と「それ」だけが食べ物を探し (0, 3)、ほかは (0, 0)。
"""
import math

import numpy as np
from manim import *

from theme import *

RED_BG = ManimColor("#FEF2F2")  # web-theme.css の --red-bg

TOKENS = ["太郎", "は", "リンゴ", "を", "食べた", "。", "それ"]
T = len(TOKENS)
TARO, HA, APPLE, SORE = 0, 1, 2, 6
Q = np.zeros((T, 2))
Q[4] = [0, 3]                   # 食べた：食べ物を探す
Q[SORE] = [0, 3]                # それ：食べ物を探す
K = np.zeros((T, 2))
K[TARO] = [3, 0]
K[APPLE] = [0, 3]


def softmax(s):
    e = np.exp(s - s.max(axis=1, keepdims=True))
    return e / e.sum(axis=1, keepdims=True)


FIT = Q @ K.T / math.sqrt(2)                          # 合い具合
FUTURE = np.triu(np.ones((T, T), dtype=bool), k=1)    # j > i（自分より後ろ）
W_FULL = softmax(FIT)
W_CAUSAL = softmax(np.where(FUTURE, -np.inf, FIT))

CELL = 0.68
SMALL = dict(cell=CELL, font_size=16, label_size=16)


def masked_cell(cell, text, size=17):
    """セル cell と同じ位置・大きさの「参考にできない」セル"""
    sq = Square(side_length=cell[0].width, stroke_color=RED_BORDER, stroke_width=1.5)
    sq.set_fill(RED_BG, opacity=1).move_to(cell)
    return VGroup(sq, jp(text, size, RED, "BOLD").move_to(sq))


def lines(*texts, size=22, color=TEXT_SUB, weight="NORMAL"):
    """複数行の文字列（Text の改行は行間が詰まるため、1 行ずつ並べる）"""
    return VGroup(*[jp(t, size, color, weight) for t in texts]).arrange(DOWN, buff=0.16, aligned_edge=LEFT)


class CausalMaskScene(Scene):
    def construct(self):
        head = title("因果マスク：自分より後ろの単語は参考にしない")
        self.play(FadeIn(head))

        # ── 1. 合い具合の表 ────────────────────────────
        s_grid = matrix_grid(FIT, TOKENS, TOKENS, fmt="{:.2f}", vmax=FIT.max(), **SMALL)
        s_name = jp("合い具合 = Q Kᵀ / √2", 22, GREEN, "BOLD")
        s_block = VGroup(s_name, s_grid).arrange(DOWN, buff=0.25).to_edge(LEFT, buff=1.0).shift(UP * 0.05)
        side_r = jp("参考にする側", 16, MUTED).rotate(PI / 2).next_to(s_grid.row_labels, LEFT, buff=0.12)
        cap = caption("各行が「その行の単語が、どの単語とどれだけ合うか」です")
        self.play(FadeIn(s_block), FadeIn(side_r), FadeIn(cap))
        self.wait(1.5)

        # ── 2. 上三角を −∞ に ──────────────────────────
        masks = VGroup(*[masked_cell(s_grid.cells[i][j], "−∞", 15)
                         for i in range(T) for j in range(T) if FUTURE[i, j]])
        cap2 = caption("自分より後ろの単語との合い具合を、softmax の前に −∞ に置き換えます", RED)
        self.play(Transform(cap, cap2))
        self.play(LaggedStart(*[FadeIn(m, scale=1.2) for m in masks], lag_ratio=0.04), run_time=1.6)
        self.wait(1.5)

        # ── 3. 行ごとに softmax ─────────────────────────
        w_grid = matrix_grid(W_CAUSAL, TOKENS, TOKENS, **SMALL)
        w_name = jp("参考にする割合 = softmax（行ごと）", 22, GREEN, "BOLD")
        w_block = VGroup(w_name, w_grid).arrange(DOWN, buff=0.25).to_edge(RIGHT, buff=0.6)
        w_block.align_to(s_block, UP)
        zeros = VGroup(*[masked_cell(w_grid.cells[i][j], "0")
                         for i in range(T) for j in range(T) if FUTURE[i, j]])
        arrow = Arrow(s_grid.get_right(), w_grid.row_labels.get_left(), color=MUTED, buff=0.2)
        cap3 = caption("e の −∞ 乗は 0 なので、後ろの単語を参考にする割合はちょうど 0 になります", GREEN)
        self.play(GrowArrow(arrow), FadeIn(w_name), FadeIn(w_grid.col_labels), FadeIn(w_grid.row_labels),
                  Transform(cap, cap3))
        self.play(LaggedStart(*[TransformFromCopy(s_grid.cells[i][j], w_grid.cells[i][j])
                                for i in range(T) for j in range(T) if not FUTURE[i, j]], lag_ratio=0.03),
                  LaggedStart(*[TransformFromCopy(m, z) for m, z in zip(masks, zeros)], lag_ratio=0.03),
                  run_time=2.2)
        self.wait(1)
        cap3b = caption("表は左下の三角形になります。前の単語（と自分）だけを参考にできます")
        self.play(Transform(cap, cap3b))
        self.wait(1.5)

        # ── 4. 「は」の行：マスクの前後を比べる ──────────────────
        self.play(FadeOut(VGroup(s_block, side_r, masks, arrow)),
                  VGroup(w_name, w_grid, zeros).animate.to_edge(LEFT, buff=1.0))
        box = row_box(w_grid, HA)
        rows = VGroup()
        for label, vals, color in (("マスクなし", W_FULL[HA], RED), ("マスクあり", W_CAUSAL[HA], GREEN)):
            g = matrix_grid([vals], ["「は」の行"], TOKENS, cell=0.62, font_size=16, label_size=15)
            for j in range(T):
                if FUTURE[HA, j] and color == GREEN:
                    g.cells[0][j].become(masked_cell(g.cells[0][j], "0"))
            name = jp(label, 20, color, "BOLD").next_to(g, UP, buff=0.15).align_to(g, LEFT)
            rows.add(VGroup(name, g))
        rows.arrange(DOWN, buff=0.5, aligned_edge=LEFT).to_edge(RIGHT, buff=0.6).shift(DOWN * 0.1)
        cap4 = caption(f"「は」は 7 単語を約 {W_FULL[HA, 0]:.2f} ずつ → 前の 2 単語を {W_CAUSAL[HA, 0]:.2f} ずつ参考にします")
        self.play(Create(box), FadeIn(rows[0]), Transform(cap, cap4))
        self.wait(1)
        self.play(TransformFromCopy(rows[0], rows[1]), run_time=1.3)
        self.wait(2.5)

        # ── 5. 「太郎」と「それ」の行 ─────────────────────
        self.play(FadeOut(rows), FadeOut(box))
        b1 = row_box(w_grid, TARO)
        cap5 = caption(f"文の最初の「太郎」は、自分自身しか参考にできません（{W_CAUSAL[TARO, TARO]:.2f}）")
        self.play(Create(b1), Create(cell_box(w_grid, TARO, TARO, GREEN_MID)), Transform(cap, cap5))
        self.wait(2)
        b2 = row_box(w_grid, SORE)
        cap6 = caption(f"「それ」はリンゴより後ろにあるので、マスクありでもリンゴを {W_CAUSAL[SORE, APPLE]:.2f} 参考にします", GREEN)
        self.play(FadeOut(b1), Create(b2), Create(cell_box(w_grid, SORE, APPLE, GREEN_MID)), Transform(cap, cap6))
        self.wait(2.5)

        # ── 6. 生成時：1 単語ずつ三角形が伸びる ───────────────
        self.play(*[FadeOut(m) for m in self.mobjects if m not in (head, cap)])
        g_grid = matrix_grid(W_CAUSAL, TOKENS, TOKENS, cell=0.62, font_size=15, label_size=16)
        g_grid.move_to(LEFT * 3.0 + DOWN * 0.35)
        ghost = VGroup(*[Square(side_length=0.62, stroke_color=BORDER, stroke_width=1.5).move_to(c)
                         for row in g_grid.cells for c in row])
        side = VGroup(jp("生成した文", 22, TEXT_SUB))
        sentence = VGroup(*[jp(t, 28, TEXT, "BOLD") for t in TOKENS]).arrange(RIGHT, buff=0.16)
        sentence.next_to(side, DOWN, buff=0.3, aligned_edge=LEFT)
        note = lines("新しい単語の行は", "自分と前の単語だけを参考にします", color=GREEN, weight="BOLD")
        note2 = lines("前の行は、あとから単語が", "増えても変わりません")
        panel = VGroup(side, sentence, note, note2).arrange(DOWN, buff=0.5, aligned_edge=LEFT)
        sentence.shift(RIGHT * 0.2)
        panel.next_to(g_grid, RIGHT, buff=0.8).align_to(g_grid.grid, UP)
        cap7 = caption("文章を生成するときは 1 単語ずつ。行が 1 本ずつ増え、三角形が伸びます")
        self.play(FadeIn(ghost), FadeIn(side), Transform(cap, cap7))
        for t in range(T):
            anims = [FadeIn(sentence[t], shift=RIGHT * 0.2), FadeIn(g_grid.row_labels[t]),
                     FadeIn(g_grid.col_labels[t])]
            anims += [FadeIn(g_grid.cells[t][j], scale=0.8) for j in range(t + 1)]
            if t == 0:
                anims.append(FadeIn(note))
            if t == 3:
                anims.append(FadeIn(note2))
            self.play(*anims, run_time=0.7)
            self.wait(0.35)
        self.wait(1)
        cap8 = caption("まだ書いていない単語は参考にできません。だから LLM は左から右へ書きます", GREEN)
        self.play(Transform(cap, cap8), Create(row_box(g_grid, T - 1)))
        self.wait(3)
