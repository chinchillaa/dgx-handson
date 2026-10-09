"""Self-Attention の計算を 1 ステップずつ追うアニメーション

値はハンズオン③ Part 2（notebooks/ch1_03_llm_inference.ipynb）の
「ネコ・が・サカナ・食べた」の例と同じ。
"""
import math

import numpy as np
from manim import *

from theme import *

TOKENS = ["ネコ", "が", "サカナ", "食べた"]
FEATURES = ["名詞性", "動詞性", "生き物性", "食べ物性"]
X = np.array([
    [1.0, 0.0, 1.0, 0.0],
    [0.2, 0.0, 0.0, 0.0],
    [1.0, 0.0, 0.5, 1.0],
    [0.0, 1.0, 0.0, 0.0],
])
W_Q = np.array([[0, 0], [0, 3], [3, 0], [0, 0]], dtype=float)
W_K = np.array([[0, 0], [0, 0], [3, 0], [0, 3]], dtype=float)
EAT = 3  # 「食べた」の行
FISH = 2  # 「サカナ」の列


def softmax(s):
    e = np.exp(s - s.max(axis=1, keepdims=True))
    return e / e.sum(axis=1, keepdims=True)


class SelfAttentionScene(Scene):
    def construct(self):
        head = title("Self-Attention の計算を 1 ステップずつ追う")
        self.play(FadeIn(head))

        # ── 1. 入力 X ─────────────────────────────
        x_grid = matrix_grid(X, TOKENS, FEATURES, fmt="{:.1f}", label_size=15)
        x_name = jp("X（埋め込み）", 24, GREEN, "BOLD")
        x_block = VGroup(x_name, x_grid).arrange(DOWN, buff=0.3).to_edge(LEFT, buff=0.7).shift(DOWN * 0.2)
        cap = caption("4 トークンの埋め込み X（ハンズオン③ Part 2 と同じ値）")
        self.play(FadeIn(x_block), FadeIn(cap))
        self.wait(1.5)

        # ── 2. 重み行列なし（Q = K = X）────────────
        naive = softmax(X @ X.T / math.sqrt(4))
        n_grid = matrix_grid(naive, TOKENS, TOKENS)
        n_name = jp("softmax(X Xᵀ / √4)", 24, RED, "BOLD")
        n_block = VGroup(n_name, n_grid).arrange(DOWN, buff=0.3).to_edge(RIGHT, buff=0.9).shift(DOWN * 0.2)
        arrow = Arrow(x_block.get_right(), n_block.get_left(), color=MUTED, buff=0.3)
        cap2 = caption("重み行列なし（Q = K = X）：「食べた」は自分自身（0.35）を一番見てしまう", RED)
        self.play(GrowArrow(arrow), FadeIn(n_block), Transform(cap, cap2))
        self.play(Create(row_box(n_grid, EAT)), Create(cell_box(n_grid, EAT, EAT, RED)))
        self.wait(2.5)
        self.play(*[FadeOut(m) for m in self.mobjects if m not in (head, x_block, cap)])

        # ── 3. Q = X W_Q, K = X W_K ──────────────────
        Q, K = X @ W_Q, X @ W_K
        q_grid = matrix_grid(Q, TOKENS, ["生き物を\n探す", "食べ物を\n探す"], fmt="{:.1f}", vmax=3, label_size=15)
        k_grid = matrix_grid(K, TOKENS, ["生き物\nです", "食べ物\nです"], fmt="{:.1f}", vmax=3, label_size=15)
        q_block = VGroup(jp("Q = X W_Q", 24, GREEN, "BOLD"), q_grid).arrange(DOWN, buff=0.3)
        k_block = VGroup(jp("K = X W_K", 24, GREEN, "BOLD"), k_grid).arrange(DOWN, buff=0.3)
        qk = VGroup(q_block, k_block).arrange(RIGHT, buff=0.9).shift(RIGHT * 1.6 + DOWN * 0.2)
        cap3 = caption("W_Q で「何を探すか」、W_K で「自分は何者か」に変換する")
        self.play(x_block.animate.scale(0.85).to_edge(LEFT, buff=0.5),
                  FadeIn(q_block, shift=RIGHT), FadeIn(k_block, shift=RIGHT), Transform(cap, cap3))
        self.wait(1)
        self.play(Create(row_box(q_grid, EAT)), Create(row_box(k_grid, FISH, GREEN_MID)))
        cap3b = caption("「食べた」は食べ物を探し（0, 3）、「サカナ」は食べ物だと名乗る（1.5, 3）")
        self.play(Transform(cap, cap3b))
        self.wait(2.5)

        # ── 4. スコア Q Kᵀ / √d_k ───────────────────
        scores = Q @ K.T / math.sqrt(2)
        s_grid = matrix_grid(scores, TOKENS, TOKENS, vmax=scores.max())
        s_name = jp("スコア = Q Kᵀ / √2", 24, GREEN, "BOLD")
        s_block = VGroup(s_name, s_grid).arrange(DOWN, buff=0.3).to_edge(RIGHT, buff=0.9).shift(DOWN * 0.2)
        self.play(FadeOut(x_block), *[FadeOut(m) for m in self.mobjects if isinstance(m, Rectangle)])
        self.play(VGroup(q_block, k_block).animate.scale(0.85).to_edge(LEFT, buff=0.6))
        self.play(FadeIn(s_block, shift=LEFT))
        hl = cell_box(s_grid, EAT, FISH)
        cap4 = caption("内積 0×1.5 + 3×3 = 9 を √2 で割って 6.36。似ている組ほどスコアが大きい")
        self.play(Create(hl), Transform(cap, cap4))
        self.wait(2.5)

        # ── 5. 行ごとに softmax ───────────────────────
        weights = softmax(scores)
        w_grid = matrix_grid(weights, TOKENS, TOKENS).move_to(s_grid, aligned_edge=UP)
        w_name = jp("注目度 = softmax（行ごと）", 24, GREEN, "BOLD").move_to(s_name)
        cap5 = caption("各行を合計 1 の注目度に変換：「食べた」は「サカナ」に 0.99 注目する", GREEN)
        self.play(FadeOut(hl))
        self.play(Transform(s_grid.grid, w_grid.grid), Transform(s_name, w_name), Transform(cap, cap5),
                  run_time=1.8)
        self.play(Create(row_box(w_grid, EAT)), Create(cell_box(w_grid, EAT, FISH, GREEN_MID)))
        self.wait(2.5)

        # ── 6. Value の加重平均 ───────────────────────
        out = weights @ X  # W_V は単位行列なので V = X
        self.play(*[FadeOut(m) for m in self.mobjects if m not in (head, cap)])
        eq = jp("「食べた」の出力 = 注目度で重み付けした V の和 ≈ 0.99 ×「サカナ」の V", 26, TEXT).shift(UP * 2.5)
        before = matrix_grid(X[EAT:EAT + 1], ["入力"], FEATURES, fmt="{:.2f}", cell=1.2, label_size=18)
        after = matrix_grid(out[EAT:EAT + 1], ["出力"], fmt="{:.2f}", cell=1.2, label_size=18)
        rows = VGroup(before, after).arrange(DOWN, buff=0.7).shift(DOWN * 0.1)
        after.shift(RIGHT * (before.grid.get_left()[0] - after.grid.get_left()[0]))
        self.play(FadeIn(eq), FadeIn(before))
        self.play(TransformFromCopy(before.grid, after.grid), FadeIn(after.row_labels), run_time=1.5)
        self.play(Create(cell_box(after, 0, 3, AMBER_BORDER)))
        cap6 = caption("動詞「食べた」のベクトルに、目的語「サカナ」の特徴（食べ物性 0.99 など）が入った", GREEN)
        self.play(Transform(cap, cap6))
        self.wait(3)
