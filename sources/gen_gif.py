from manim import *

'''
Function to generate example gif
Usage: manim -pqh -r 1080,1080 gen_gif.py RotationAroundCommonCenter
'''

class RotationAroundCommonCenter(Scene):
    def construct(self):
        red_square = Square(side_length=1.5, color=RED, fill_opacity=1)
        yellow_square = Square(side_length=1.5, color=YELLOW, fill_opacity=1)
        yellow_square.next_to(red_square, UP, buff=0.05)
        purple_square = Square(side_length=1.5, color=PURPLE, fill_opacity=1)
        purple_square.next_to(red_square, LEFT, buff=0.05)

        all_shapes = VGroup(red_square, yellow_square, purple_square)

        all_shapes.move_to(ORIGIN)

        self.add(all_shapes)
        self.wait(1)

        self.play(
            Rotate(
                all_shapes,
                angle=-90 * DEGREES,
            ),
            run_time=2,
            rate_func=smooth
        )

        self.wait(1.5)
