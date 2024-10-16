"""
file containing a class for defining a box alonsgside
with it's dimensions
"""
from typing import Tuple


class Box:
    def __init__(self,
                 center: Tuple[float, float],
                 dimensions: tuple[float, float],
                 height: float,
                 rotation: float) -> None:
        """
        creates a new Box using the given parameters
        :param center: the calculated center coordinates of the box in the format (x, y)
        :param dimensions: width and height of the box measured from the camera
        :param height: height of the surface of the box over ground
        :param rotation: rotation in degrees of the box
        """

        self.center = center
        self.dimensions = dimensions
        self.height = height
        self.rotation = rotation

    def get_area(self) -> float:
        """
        returns the area of the box
        :return:
        """
        return self.dimensions[0] * self.dimensions[1]
