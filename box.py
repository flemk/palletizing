"""
file containing a class for defining a box alonsgside
with it's dimensions
"""
from typing import Tuple, List


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

    def get_volume(self) -> float:
        """
        returns the volume of the box
        :return:
        """
        return self.dimensions[0] * self.dimensions[1] * self.dimensions[2]

    def get_gripping_position(self) -> Tuple[float, float, float]:
        """
        get an (x,y,z) position for the robot to grip the box
        :return: coordinate of the gripping position
        """
        raise NotImplementedError

def sort_by_size(boxes: List[Box], descending: bool = True) -> List[Box]:
    """
    sorts the given boxes by their size in descending order.
    Returns a new list
    :param boxes:
    :param descending: whether to sort the boxes descending
    :return:
    """
    return sorted(boxes, key=lambda box: box.get_volume(), reverse=descending)