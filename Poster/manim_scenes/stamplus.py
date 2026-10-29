"""Original explanatory animations, based on STAMPlus Figs. 2, 4, 5.

These are conceptual animations, not model inference or measured timings.
Manim Community 0.19.0; Text avoids a system LaTeX dependency.
"""
from manim import *

BG = "#142E38"
INK = "#F5F3EB"
TEAL = "#6AD5BF"
GOLD = "#F1C46D"
BLUE = "#7CAFF0"
MUTED = "#9EB6BD"


def label(text, size=26, color=INK):
    return Text(text, font="Arial", font_size=size, color=color)


def grid(rows=4, cols=7):
    return VGroup(*[
        Square(side_length=.42, stroke_color=MUTED, stroke_width=1,
               fill_color=BG, fill_opacity=1)
        for _ in range(rows * cols)
    ]).arrange_in_grid(rows=rows, cols=cols, buff=.065)


class AllMaskPrediction(Scene):
    def construct(self):
        self.camera.background_color = BG
        title = label("Dense masks, without a long token-by-token decode", 32).to_edge(UP, .55)
        left = grid().move_to(LEFT * 3.4)
        right = grid().move_to(RIGHT * 3.4)
        headers = VGroup(label("NEXT-TOKEN MASK", 24, GOLD).next_to(left, UP, .6),
                         label("ALL-MASK PREDICTION", 24, TEAL).next_to(right, UP, .6))
        caption = label("Conceptual animation / time is not a benchmark", 19, MUTED).to_edge(DOWN, .35)
        self.play(FadeIn(title), FadeIn(headers), Create(left), Create(right), FadeIn(caption))
        step = label("Sequential patch labels", 23, GOLD).next_to(left, DOWN, .4)
        self.play(FadeIn(step))
        for i, cell in enumerate(left):
            color = GOLD if i in [2,3,9,10,15,16,17,18,22,23,24,25] else "#37515B"
            self.play(cell.animate.set_fill(color), run_time=.11)
        context = label("Image + text context + <SEG>", 22, TEAL).next_to(right, UP, 1.25)
        self.play(FadeIn(context))
        dots = VGroup(*[Dot(c.get_center(), radius=.035, color=TEAL) for c in right])
        self.play(FadeIn(dots))
        self.wait(.6)
        self.play(*[cell.animate.set_fill(TEAL if i in [2,3,9,10,15,16,17,18,22,23,24,25] else "#37515B")
                    for i,cell in enumerate(right)], FadeOut(dots), run_time=1.2)
        done = label("One parallel mask pass", 23, TEAL).next_to(right, DOWN, .4)
        self.play(FadeIn(done))
        note = label("Text stays autoregressive. Mask tokens attend bidirectionally.", 25).move_to(DOWN * 2.5)
        self.play(FadeIn(note))
        self.wait(3)


class StructuredIDs(Scene):
    def construct(self):
        self.camera.background_color = BG
        self.add(label("First define the IDs. Then predict the map.", 36).to_edge(UP, .55))
        rows = VGroup(*[
            label(t, 26, c) for t,c in [
                ('1 : curtain A', BLUE), ('2 : curtain B', TEAL), ('3 : bed', GOLD)]
        ]).arrange(DOWN, aligned_edge=LEFT, buff=.5).move_to(LEFT * 3.8)
        h1 = label("PHASE 1 / STRUCTURED TARGET LIST", 21, MUTED).next_to(rows, UP, .7)
        self.play(FadeIn(h1))
        for row in rows:
            self.play(Write(row), run_time=.8)
        seg = label("<SEG>", 30, TEAL).move_to(LEFT*.3)
        self.play(FadeIn(seg))
        board = grid(6,9).move_to(RIGHT * 3.4 + DOWN*.2)
        self.play(Create(board))
        self.add(label("PHASE 2 / SHARED ID MAP", 21, MUTED).next_to(board, UP, .7))
        colors = [BLUE,TEAL,GOLD]
        ids=[]
        for i in range(54):
            r,c=divmod(i,9)
            ids.append(1 if c in [1,2] and r<4 else 2 if c in [6,7] and r<4 else 3 if r>=4 and 2<=c<=7 else 0)
        self.play(*[cell.animate.set_fill(colors[k-1] if k else "#37515B") for cell,k in zip(board,ids)],run_time=1.5)
        digits = VGroup(*[label(str(k),16,BG if k else MUTED).move_to(cell) for cell,k in zip(board,ids)])
        self.play(FadeIn(digits))
        self.play(FadeIn(label("0 = background / positive IDs belong to this instruction",23).move_to(DOWN*2.65)))
        self.add(label("Illustrative grid, not an output from the model",19,MUTED).to_edge(DOWN,.3))
        self.wait(3)
