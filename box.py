"""
file containing a class for defining a box alonsgside
with it's dimensions
"""
from typing import Tuple, List
from enum import Enum

from docutils.nodes import target


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

class BoxAction(Enum):
    """
    Enum determining actions to do with packets
    """
    PLACE = 0  # just place the package to the target coordinates
    ROTATE_90 = 1  # rotate the package by 90 degrees before placing it down

def sort_by_size(boxes: List[Box], descending: bool = True) -> List[Box]:
    """
    sorts the given boxes by their size in descending order.
    Returns a new list
    :param boxes:
    :param descending: whether to sort the boxes descending
    :return:
    """
    return sorted(boxes, key=lambda box: box.get_volume(), reverse=descending)

def determine_positions_easy(target_area: Tuple[int, int, int, int],
                       boxes: List[Box]) -> List[Tuple[int, int, BoxAction]]:
    """
    given a set of boxes, determine the positions to put the boxes to

    Basic algorithm:
    1. Take largest box from the list and place it in the top left corner
    2. Take next box place it right to the first box, if there is no space in the row, place it in the next one
       Check that there is space and make sure, that to remember the highest box during placement
       to determine the starting point of the next row
    3. repeat until all boxes are placed

    :param target_area: (x1, y1, x2, y2) of a rectangular area to put the boxes into
    :param boxes: The boxes to place into the target area
    :return: List of (x,y, action) positions of the Boxes to be placed to. Position is the center
    """

    MARGIN_TO_EDGE: int = 10  # distance of the boxes to the edges of the placement area
    MARGIN_INTER: int = 10  # distance of the boxes to each other

    target_coords = []

    for i, box in enumerate(boxes):
        if i == 0:


    raise NotImplementedError
