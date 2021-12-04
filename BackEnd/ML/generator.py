import os
import random
import sys

import numpy as np
import cv2


class Shape:
    def __init__(self, n_gen, shape_name):
        self.to_generate = n_gen
        self.canvas = None
        self.shape_name = shape_name

        self.base_dir = os.path.join(os.getcwd(), "gen", shape_name)
        self.curr_id = 0

    def _generator(self):
        raise NotImplementedError

    def generate(self):
        for i in range(self.to_generate):
            self.__clear_canvas()
            self._generator()
            self.__write()
            self.curr_id += 1

    def __clear_canvas(self):
        self.canvas = np.full((200, 200), 255, dtype=np.uint8)

    def __write(self):
        cv2.imwrite(os.path.join(self.base_dir, "{}.png".format(self.curr_id)), self.canvas)


class Rectangle(Shape):
    def __init__(self, n_gen):
        super(Rectangle, self).__init__(n_gen, 'rectangle')

    def _generator(self):
        x1, y1 = (random.randint(15, 50), random.randint(10, 50))
        x2, y2 = (x1 + (random.randint(80, 140)), y1 + (random.randint(-15, 15)))
        x3, y3 = (x2 + (random.randint(-15, 15)), y2 + (random.randint(80, 110)))
        x4, y4 = (x1 + (random.randint(-15, 15)), y3 + (random.randint(-15, 15)))

        cv2.fillPoly(self.canvas, pts=np.int32([[[x1, y1], [x2, y2], [x3, y3], [x4, y4]]]), color=0)


class Triangle(Shape):
    def __init__(self, n_gen):
        super(Triangle, self).__init__(n_gen, 'triangle')

    def _generator(self):
        random_points = [
            [random.randint(0, 199), random.randint(0, 199)],
            [random.randint(0, 199), random.randint(0, 199)],
            [random.randint(0, 199), random.randint(0, 199)],
        ]
        contours = np.array(random_points, dtype=np.uint8)
        cv2.fillPoly(self.canvas, pts=np.int32([contours]), color=0)


class Circle(Shape):
    def __init__(self, n_gen):
        super(Circle, self).__init__(n_gen, 'circle')

    def _generator(self):
        xy = (random.randint(50, 149), random.randint(70, 129))
        along_x = random.randint(30, 50)
        along_y = along_x + (random.randint(-20, 20))
        axes_lengths = (along_x, along_y)

        self.canvas = cv2.ellipse(self.canvas, xy, axes_lengths, random.randint(0, 45), 0, 360, 0, -1)


if __name__ == "__main__":
    shape = sys.argv[1]
    to_generate = int(sys.argv[2])

    if shape == 'rectangle':
        Rectangle(to_generate).generate()
    elif shape == 'triangle':
        Triangle(to_generate).generate()
    elif shape == 'circle':
        Circle(to_generate).generate()
    else:
        print("Invalid shape input")
