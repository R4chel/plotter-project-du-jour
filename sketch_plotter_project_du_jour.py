import vsketch
from shapely.geometry import Point, LinearRing
from shapely import affinity
import numpy as np
from point2d import Point2D


def f(x, y):
    # return (x**2 - y**3 + 0.1 * x * x * y, y - x + .2 * x**4)
    # return (x**2 + y**2 + 3 * x - 2 * x * y + x**2 * y - 0.1 * y**2 * x - x**2,
    #         2 * x * y * y + .0001 * x**2 - .02 * (y)**3)
    return (x**2 + y**2 + 3 * x - 2 * x * y + x**2 * y - 0.1 * y**2 * x - x**2,
            2 * x * y * y + .3 * x**2 - .02 * (y)**3)


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

    def random_point(self, vsk: vsketch.Vsketch):
        return Point(vsk.random(0, self.width), vsk.random(0, self.height))

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
        mapping = [f(x, y) for (x, y) in circle]
        # mapping = [f(x, y) for (x, y) in mapping]
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
