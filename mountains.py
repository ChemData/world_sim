import numpy as np
from PyQt5.QtChart import QChart, QChartView, QLineSeries
from PyQt5.QtGui import QPolygonF, QPainter
from PyQt5.QtWidgets import QMainWindow
from matplotlib import cm
import matplotlib.pyplot as plt


class World:

    def __init__(self, x_dim, y_dim):
        self._gen_world(x_dim, y_dim)

    def show(self, path=None):
        plt.imshow(self._height_image())
        if path is not None:
            plt.plot(*zip(*path))
        plt.show()

    def _gen_world(self, x_dim, y_dim):
        self.height_map = np.zeros((x_dim, y_dim))
        self.height_map += 10

    def add_mountains(self, number):
        """Add a certain number of mountain peaks to the world."""
        for i in range(number):
            x_pos = np.random.randint(0, self.height_map.shape[0])
            y_pos = np.random.randint(0, self.height_map.shape[1])
            mountain_height = np.random.exponential(20)
            spread = np.random.normal(2, .2)
            coords = np.indices(self.height_map.shape).transpose((1, 2, 0))
            new_height = np.exp(-((coords[:, :, 0]-x_pos)/(spread*mountain_height))**2) * \
                         np.exp(-((coords[:, :, 1]-y_pos) / (spread*mountain_height))**2)
            new_height *= mountain_height
            self.height_map += new_height

    def add_tilt(self, x_slope, y_slope):
        """Add a slope to the terrain."""
        coords = self._coords()
        self.height_map += coords[:, :, 0] * x_slope
        self.height_map += coords[:, :, 1] * y_slope

    def _coords(self):
        return np.indices(self.height_map.shape).transpose((1, 2, 0))

    def _height_image(self):
        image = cm.cool(self._normalize(self.height_map))
        return image

    def _normalize(self, array):
        """Normalize an array to be between 0 and 1."""
        array = array.copy()
        max_val = array.max()
        min_val = array.min()
        if max_val == min_val:
            array = np.ones(array.shape) * .5
        else:
            array -= min_val
            array /= (max_val-min_val)
        return array

    def add_noise(self, scale=30):
        self.height_map += np.random.normal(0, scale, self.height_map.shape)

    def erode(self, times, move_amount, position=None):
        """Erode the world by running water across the surface.

        Args:
            times (int): Number of times to repeat erosion.
            move_amount (float): Amount of material to move during each repeat.
            position (None, tuple, list): If None, will use a randomly selected position
                for each repeat. If tuple, will repeatedly use that position.
        """
        for t in range(times):
            pos = position
            if position is None:
                pos = (np.random.randint(0, self.height_map.shape[0]),
                       np.random.randint(0, self.height_map.shape[1]))
            w = WaterPath(self.height_map.copy())
            w.add_water(*pos)
            m = w.move_until_done()
            self.height_map[pos] -= move_amount
            if m == 'sink':
                self.height_map[w.water_path[-1]] += move_amount



class WaterPath:
    """Follows a unit of water as it makes its way, downhill, across the world."""

    def __init__(self, height_map, diag_movement=True):
        self.height_map = height_map
        self.diag_movement = diag_movement

    def add_water(self, x, y):
        """Add a unit of water to the specified location."""
        self.water_x = x
        self.water_y = y
        self.water_path = [(self.water_x, self.water_y)]

    def _move(self):
        """Move the water in the most downward direction. Return 'sink', if all directions
        are uphill. Return 'edge' if the edge is reached."""
        if self._at_edge:
            self.water_x = None
            self.water_y = None
            return 'edge'
        neighbors = self.height_map[self.water_x-1:self.water_x+2,
                    self.water_y-1:self.water_y+2]

        min_pos = np.where(neighbors == neighbors.min())
        if 1 in min_pos[0]*min_pos[1]:
            self.water_x = None
            self.water_y = None
            return 'sink'
        x_move = min_pos[0][0]
        y_move = min_pos[1][0]
        self.water_x += x_move - 1
        self.water_y += y_move - 1
        self.water_path += [(self.water_x, self.water_y)]

    def move_until_done(self):
        while True:
            outcome = self._move()
            if outcome is not None:
                return outcome

    @property
    def _at_edge(self):
        """Return True, if the water position is at the edge."""
        if 0 == self.water_x or 0 == self.water_y:
            return True
        if self.water_x == self.height_map.shape[0]-1:
            return True
        if self.water_y == self.height_map.shape[1]-1:
            return True
        return False




x = World(1000, 1500)
x.add_tilt(.02, .02)
#x.add_mountains(10)
#x.add_noise(.5)

#x.erode(10, .1, (50, 120))