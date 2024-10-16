"""
file containing a class for defining a box alonsgside
with it's dimensions
"""
from typing import Tuple, List
from enum import Enum

from util import Vec2, Vec3

class Box:
    def __init__(self,
                 center: Vec2,
                 dimensions: Vec2,
                 z_height: float,
                 rotation: float) -> None:
        """
        creates a new Box using the given parameters
        :param center: the calculated center coordinates of the box in the format (x, y)
        :param dimensions: width and height of the box measured from the camera
        :param z_height: height of the surface of the box over ground
        :param rotation: rotation in degrees of the box
        """

        self.center = center
        self.dimensions = dimensions
        self.z_height = z_height
        self.rotation = rotation

    def get_area(self) -> float:
        """
        returns the area of the box
        :return:
        """
        return self.dimensions.x * self.dimensions.y

    def get_volume(self) -> float:
        """
        returns the volume of the box
        :return:
        """
        return self.dimensions.x * self.dimensions.y * self.z_height

    def get_gripping_position(self) -> Tuple[float, float, float]:
        """
        get an (x,y,z) position for the robot to grip the box
        :return: coordinate of the gripping position
        """
        raise NotImplementedError

    @property
    def width(self):
        return self.dimensions.x

    @property
    def height(self):
        """
        This is not the z height of the package, but rather it's y dimension!
        :return:
        """
        return self.dimensions.y

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

def determine_positions_easy(target_area: Tuple[Vec2, Vec2],
                             boxes: List[Box]) -> List[Tuple[Vec2, BoxAction]]:
    """
    given a set of boxes, determine the positions to put the boxes to

    Basic algorithm:
    1. Take the largest box from the list and place it in the top left corner
    2. Take next box place it right to the first box, if there is no space in the row, place it in the next one
       Check that there is space and make sure, that to remember the highest box during placement
       to determine the starting point of the next row
    3. repeat until all boxes are placed

    :param target_area: (x1, y1, x2, y2) of a rectangular area to put the boxes into
    :param boxes: The boxes to place into the target area
    :return: List of (x,y, action) positions of the Boxes to be placed to. Position is the center
    """

    MARGIN_INTER: int = 10  # distance of the boxes to each other and to the border of the area

    target_coords = []

    # ta := target_area#
    ta_origin = target_area[0] # origin is top left corner
    ta_height = target_area[1].y - ta_origin.y
    ta_width = target_area[1].x - ta_origin.x
    ta_center = Vec2(ta_origin.x + ta_width // 2, ta_origin.y + ta_height // 2)

    # borders where to align boxes currently
    current_x_border: float = ta_origin.x
    current_y_border: float = ta_origin.y

    max_y_offset: float = 0  #  store highest package to determine where to put next row of packets

    for i, box in enumerate(boxes):

        if ta_origin.x + ta_width - current_x_border - MARGIN_INTER - box.width > 0: # there is space for another package
            # package fits normally
            action = BoxAction.PLACE
        else:
            #  try rotating it by 90 deg to see if it fits
            if ta_origin.x + ta_width - current_x_border - MARGIN_INTER - box.height > 0:
                #  fits rotated
                action = BoxAction.ROTATE_90
            else:
                # we have to start a new column to fit package
                current_x_border = 0
                current_y_border = max_y_offset
                max_y_offset = 0
                action = BoxAction.PLACE


        target_center_of_box = Vec2(current_x_border + MARGIN_INTER + box.width // 2,
                                    current_y_border + MARGIN_INTER + box.height // 2)

        target_coords.append((target_center_of_box, action))

        current_x_border = target_center_of_box.x
        max_y_offset = max(max_y_offset, target_center_of_box.y + box.height // 2)

    return target_coords

if __name__ == '__main__':
    from tkinter import Toplevel, PhotoImage, Canvas
    import tkinter as tk

    # define some sample boxes and check if the stacking works
    target_area = (Vec2(0,0), Vec2(200, 400))

    b1 = Box(Vec2(20, 20), Vec2(60, 60), 20,32.8)
    b2 = Box(Vec2(50, 20), Vec2(30, 40), 20, 10.6)
    b3 = Box(Vec2(50, 80), Vec2(10, 60), 20, 45)
    b4 = Box(Vec2(20, 20), Vec2(60, 60), 20,32.8)
    b5 = Box(Vec2(20, 20), Vec2(60, 60), 20,32.8)
    b6 = Box(Vec2(20, 20), Vec2(60, 60), 20,32.8)



    boxes = sort_by_size([b1, b2, b3, b4, b5, b6], descending=True)

    target = determine_positions_easy(target_area, boxes)

    for i, box in enumerate(target):
        print(f"Box {i+1}: X: {box[0].x}, Y:{box[0].y}, action: {box[1]}")

    root = tk.Tk()
    root.title("Debug placement")
    root.geometry(f"{target_area[1].x-target_area[0].x}x{target_area[1].y-target_area[0].y}")  # Set window size

    # Create a canvas widget
    canvas = tk.Canvas(root, bg="white")
    canvas.pack(fill=tk.BOTH, expand=True)

    for i, box in enumerate(target):
        canvas.create_rectangle(box[0].x- boxes[i].width//2, box[0].y - boxes[i].height//2, box[0].x + boxes[i].width//2, box[0].y + boxes[i].height//2)

    # Start the Tkinter event loop
    root.mainloop()