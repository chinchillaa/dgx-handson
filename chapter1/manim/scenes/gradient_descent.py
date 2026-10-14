"""勾配降下法で直線がデータに近づく様子と、損失の等高線上の軌跡を同時に見せるアニメーション

データと学習の設定は supplement_linear_regression.html のコード例と同じ
（np.random.seed(42)、x = linspace(0, 10, 50)、y = 2x + 1 + noise×2、alpha = 0.01、300 エポック）。
"""
import numpy as np
from manim import *

from theme import *

np.random.seed(42)
XS = np.linspace(0, 10, 50)
YS = 2 * XS + 1 + np.random.randn(50) * 2
ALPHA, EPOCHS = 0.01, 300


def loss(w, b):
    return float(np.mean((YS - (w * XS + b)) ** 2))


def run_gd():
    w, b = 0.0, 0.0
    hist = [(w, b, loss(w, b))]
    n = len(XS)
    for _ in range(EPOCHS):
        pred = w * XS + b
        dw = -2 / n * np.sum(XS * (YS - pred))
        db = -2 / n * np.sum(YS - pred)
        w, b = w - ALPHA * dw, b - ALPHA * db
        hist.append((w, b, loss(w, b)))
    return hist


HIST = run_gd()
# 最小二乗解（損失が最小になる w, b）
A = np.vstack([XS, np.ones_like(XS)]).T
W_OPT, B_OPT = np.linalg.lstsq(A, YS, rcond=None)[0]
L_OPT = loss(W_OPT, B_OPT)
H = np.array([[np.mean(XS ** 2), np.mean(XS)], [np.mean(XS), 1.0]])  # L = L_OPT + d^T H d


def state(t):
    """エポック t（小数可）の (w, b, loss) を線形補間で返す"""
    i = int(np.clip(np.floor(t), 0, EPOCHS - 1))
    f = float(np.clip(t - i, 0, 1))
    a, c = np.array(HIST[i]), np.array(HIST[i + 1])
    return a + (c - a) * f


class GradientDescentScene(Scene):
    def construct(self):
        head = title("勾配降下法：坂を下るほど、直線がデータに合っていく")
        self.add(head)

        # ── 左：データと予測直線 ────────────────
        data_ax = Axes(x_range=[0, 10, 2], y_range=[-5, 25, 5], x_length=5.6, y_length=4.1,
                       axis_config={"color": MUTED, "include_tip": False})
        data_ax.to_edge(LEFT, buff=0.9).shift(DOWN * 0.55)
        data_ax.add(tick_labels(data_ax, [0, 2, 4, 6, 8, 10], [-5, 0, 5, 10, 15, 20, 25]))
        dl = VGroup(jp("x", 22, TEXT_SUB).next_to(data_ax.x_axis, DOWN, buff=0.45),
                    jp("y", 22, TEXT_SUB).next_to(data_ax.y_axis, LEFT, buff=0.75))
        dots = VGroup(*[Dot(data_ax.c2p(x, y), radius=0.045, color=TEXT_SUB) for x, y in zip(XS, YS)])
        left_title = jp("データと予測直線 y = wx + b", 22, GREEN, "BOLD").next_to(data_ax, UP, buff=0.25)

        # ── 右：損失の等高線 ────────────────────
        loss_ax = Axes(x_range=[-0.2, 2.6, 0.5], y_range=[-0.6, 2.2, 0.5], x_length=5.4, y_length=4.1,
                       axis_config={"color": MUTED, "include_tip": False})
        loss_ax.to_edge(RIGHT, buff=0.7).shift(DOWN * 0.55)
        loss_ax.add(tick_labels(loss_ax, [0, 0.5, 1, 1.5, 2, 2.5], [-0.5, 0, 0.5, 1, 1.5, 2]))
        ll = VGroup(jp("w", 22, TEXT_SUB).next_to(loss_ax.x_axis, DOWN, buff=0.45),
                    jp("b", 22, TEXT_SUB).next_to(loss_ax.y_axis, LEFT, buff=0.75))
        right_title = jp("損失 L(w, b) の等高線（お椀を真上から見た図）", 22, GREEN, "BOLD").next_to(loss_ax, UP, buff=0.25)

        evals, evecs = np.linalg.eigh(H)
        contours = VGroup()
        for k, level in enumerate([0.5, 3, 15, 60, 160]):
            r = np.sqrt(level / evals)

            def pt(s, r=r):
                d = evecs @ np.array([r[0] * np.cos(s), r[1] * np.sin(s)])
                return loss_ax.c2p(W_OPT + d[0], B_OPT + d[1])

            curve = ParametricFunction(pt, t_range=[0, TAU, TAU / 400],
                                       color=interpolate_color(GREEN_MID, GREEN_BG, k / 5), stroke_width=3)
            contours.add(curve)
        # 軸の範囲外にはみ出す部分を隠す
        frame = Rectangle(width=loss_ax.x_length, height=loss_ax.y_length).move_to(loss_ax.c2p(1.2, 0.8))
        mask = Difference(Rectangle(width=30, height=30), frame, fill_color=BG, fill_opacity=1, stroke_width=0)
        best = Star(n=5, outer_radius=0.14, color=AMBER, fill_opacity=1).move_to(loss_ax.c2p(W_OPT, B_OPT))

        cap = caption("左はデータと直線、右は損失の地形。初期値は w = 0, b = 0")
        self.play(FadeIn(data_ax), FadeIn(dl), FadeIn(dots), FadeIn(left_title),
                  FadeIn(loss_ax), FadeIn(ll), Create(contours), FadeIn(right_title), FadeIn(cap))
        self.add(mask, loss_ax, ll, right_title, data_ax, dl, dots, left_title, head, cap)
        self.play(FadeIn(best))

        # ── 学習の進行 ────────────────────────────
        t = ValueTracker(0)
        line = always_redraw(lambda: data_ax.plot(
            lambda x: state(t.get_value())[0] * x + state(t.get_value())[1],
            x_range=[0, 10], color=GREEN_MID, stroke_width=5))
        ball = always_redraw(lambda: Dot(loss_ax.c2p(*state(t.get_value())[:2]), radius=0.09, color=RED))
        trail = TracedPath(ball.get_center, stroke_color=RED, stroke_width=3)
        info = always_redraw(lambda: jp(
            "エポック {:>3d}　w = {:.2f}　b = {:.2f}　損失 = {:.2f}".format(
                int(t.get_value()), *state(t.get_value())), 22, TEXT).next_to(head, DOWN, buff=0.15))
        self.play(Create(line), FadeIn(ball), FadeIn(info))
        self.add(trail)

        cap1 = caption("勾配の反対方向（坂を下る方向）に、学習率 α = 0.01 の歩幅で進む")
        self.play(Transform(cap, cap1))
        self.play(t.animate.set_value(10), run_time=4, rate_func=linear)
        cap2 = caption("まず急な斜面を一気に下り、直線の傾き w がすぐデータに合う")
        self.play(Transform(cap, cap2))
        self.play(t.animate.set_value(60), run_time=4, rate_func=linear)
        cap3 = caption("その後は細長い谷底をゆっくり進み、切片 b が少しずつ調整される")
        self.play(Transform(cap, cap3))
        self.play(t.animate.set_value(EPOCHS), run_time=6, rate_func=linear)
        cap4 = caption("300 エポック後：w = 1.91, b = 0.95。★（損失が最小の w = 1.88, b = 1.13）に近づいている", GREEN)
        self.play(Transform(cap, cap4))
        self.wait(3)
