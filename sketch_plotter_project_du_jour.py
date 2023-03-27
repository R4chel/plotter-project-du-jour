import vsketch
from shapely.geometry import Point, LinearRing
from shapely import affinity
import numpy as np
from point2d import Point2D
from functools import reduce
from itertools import accumulate


def f(x, y):
    # return (x**2 - y**3 + 0.1 * x * x * y, y - x + .2 * x**4)
    # return (x**2 + y**2 + 3 * x - 2 * x * y + x**2 * y - 0.1 * y**2 * x - x**2,
    #         2 * x * y * y + .0001 * x**2 - .02 * (y)**3)
    return (x**2 + y**2 + 3 * x - 2 * x * y + x**2 * y - 0.1 * y**2 * x - x**2,
            2 * x * y * y + .3 * x**2 - .02 * (y)**3)


def powers(x, n):
    return accumulate(range(n), lambda acc, i: acc * x, initial=1)


def compute(f, x, y):
    xpow, ypow = f.shape
    xs = powers(x, xpow)
    ys = powers(y, ypow)

    # def term(coef, x_degree, y_degree):
    #     return coef * xs[x_degree] * ys[y_degree]

    # def apply_f(acc, index_and_value):
    #     ((x_degree, y_degree), coef) = index_and_value
    #     if coef is None:
    #         return acc
    #     return acc + term(coef, x_degree, y_degree)
    # return reduce(lambda acc, index_and_value: apply_f(acc, index_and_value),
    #               np.ndenumerate(f), 0)

    sum = 0
    for row, y_pow in zip(f, ys):
        for coef, x_pow in zip(row, xs):
            if coef is not None:
                sum += coef * x_pow * y_pow

    return sum


def func_str(f):
    str = " + ".join([
        f"{coeff}x^{degrees[0]}y^{degrees[1]}"
        for (degrees, coeff) in np.ndenumerate(f) if coeff is not None
    ])
    return str


class PlotterProjectDuJourSketch(vsketch.SketchClass):
    # Sketch parameters:
    debug = vsketch.Param(False)
    width = vsketch.Param(5., decimals=2, unit="in")
    height = vsketch.Param(3., decimals=2, unit="in")
    margin = vsketch.Param(0.1, decimals=3, unit="in")
    landscape = vsketch.Param(True)
    pen_width = vsketch.Param(0.7, decimals=3, min_value=1e-10, unit="mm")
    num_layers = vsketch.Param(1)
    num_points = vsketch.Param(360)
    radius = vsketch.Param(1.0, decimals=3, unit="in")
    max_degree = vsketch.Param(3)
    max_coefficient = vsketch.Param(0.2)
    inclusion_probability = vsketch.Param(0.1)
    precision = vsketch.Param(3)

    def random_point(self, vsk: vsketch.Vsketch):
        return Point(vsk.random(0, self.width), vsk.random(0, self.height))

    def random_function(self, vsk: vsketch.Vsketch):
        f = np.array([[
            np.around(vsk.random(-self.max_coefficient, self.max_coefficient),
                      self.precision)
            if vsk.random(0, 1) <= self.inclusion_probability else None
            for _ in range(self.max_degree + 1)
        ] for _ in range(self.max_degree + 1)])
        if np.any(f):
            return f
        self.inclusion_probability += 0.05
        return self.random_function(vsk)

    def draw(self, vsk: vsketch.Vsketch) -> None:
        vsk.size(f"{self.height}x{self.width}",
                 landscape=self.landscape,
                 center=False)
        self.width = self.width - 2 * self.margin
        self.height = self.height - 2 * self.margin
        vsk.translate(self.margin, self.margin)
        vsk.penWidth(f"{self.pen_width}")

        cx = self.width / 2
        cy = self.height / 2
        thetas = np.linspace(0, 2 * np.pi, self.num_points)
        circle = [Point2D(a=theta, r=1).cartesian() for theta in thetas]
        # mapping = [(x**2 + y**2 + 3 * x - 2 * x * y - np.sin(x * y) +
        #             x**2 * y - 0.1 * y**2 * x - x**4,
        #             2 * x * y * y + .0001 * x**2 - .02 * (y)**3)
        #            for (x, y) in circle]

        # mapping = [(x * y - x + x**3, 0.1 * x**3 * y**2 - x * y + .3 * y)
        #            for (x, y) in circle]
        # mapping = [f(x, y) for (x, y) in circle]
        # mapping = [f(x, y) for (x, y) in mapping]
        func1 = self.random_function(vsk)
        func2 = self.random_function(vsk)
        print(f"x func: {func_str(func1)}")
        print(f"y func: {func_str(func2)}")
        mapping = [(compute(func1, x, y), compute(func2, x, y))
                   for (x, y) in circle]
        shape = LinearRing(mapping)

        shape = affinity.scale(shape, self.radius, self.radius)
        shape = affinity.translate(shape, cx, cy)
        shape2 = affinity.scale(LinearRing(mapping), self.radius / 2,
                                self.radius / 2)
        shape2 = affinity.translate(shape2, cx, cy)
        vsk.geometry(shape)
        # vsk.stroke(2)
        # vsk.geometry(shape2)

    def finalize(self, vsk: vsketch.Vsketch) -> None:
        vsk.vpype("linemerge linesimplify reloop linesort")


if __name__ == "__main__":
    PlotterProjectDuJourSketch.display()
