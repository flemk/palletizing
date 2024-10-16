"""
handle all the communication and interaction
with the robot
"""
from enum import Enum
from typing import Tuple, List

from cri.cri.abb.abb_client import ABBClient
import numpy as np

from util import Vec2
from box import Box

SAFETY_HEIGHT: float = 650  # todo: adapt this once everything is calibrated
DROP_OFF_ORIGIN: Vec2 = Vec2(0, 0)  # FIXME!!! Use some reasonable coordinates
LOCATION_ANGLE: float = 90  # how many degrees difference between pickup and drop off
LIN_SPEED: float = 80  # mm/s
ANG_SPEED: float = 20  # deg/s


class CurrentPostion(Enum):
    PICK_UP = 0
    DROP_OFF = 1
    UNKNOWN = 2


class RobotInteractor:
    def __init__(self, ip: str = "192.168.136.44", port: int = 5000):
        self.client = ABBClient(ip, port)
        self.position: CurrentPostion = CurrentPostion.UNKNOWN

    def close(self):
        self.client.close()

    def rotate_base_joint(self, deg: float):
        """
        rotates the first joint (z-Axis of robot), by the given amount of degrees
        :param deg:
        :return:
        """
        current_angles = self.client.get_joint_angles()
        transition = np.array([deg, 0, 0, 0, 0, 0])
        self.client.move_joints(current_angles + transition)

    def go_to_home_position(self):
        angles = self.client.get_joint_angles()
        angles[0] = 0
        self.client.move_joints(angles)
        current_pos = self.client.get_pose()

        # orient gripper to look vertically from above
        current_pos[0] = 250
        current_pos[1] = 40
        current_pos[2] = 300
        current_pos[3] = 0
        current_pos[4] = 0
        current_pos[5] = 0

        self.client.move_linear(current_pos)
        self.position = CurrentPostion.PICK_UP

    def move_to_pickup(self):
        if self.position == CurrentPostion.PICK_UP:
            return
        else:
            # raise to safety height
            current_pos = self.client.get_pose()
            current_pos[2] = SAFETY_HEIGHT
            self.client.move_linear(current_pos)
            self.rotate_base_joint(-LOCATION_ANGLE)
            self.position = CurrentPostion.PICK_UP

    def move_to_dropoff(self):
        if self.position == CurrentPostion.DROP_OFF:
            return
        else:
            # raise to safety height
            current_pos = self.client.get_pose()
            current_pos[2] = SAFETY_HEIGHT
            self.client.move_linear(current_pos)
            self.rotate_base_joint(LOCATION_ANGLE)
            self.position = CurrentPostion.DROP_OFF

    def go_to(self, x: float = None,
              y: float = None,
              z: float = None,
              a: float = None,
              b: float = None,
              c: float = None):
        """
        changes only the given parameters, all None parameters will remain unchanged
        :param x:
        :param y:
        :param z:
        :param a:
        :param b:
        :param c:
        :return:
        """
        current_pos = self.client.get_pose()
        if x is not None:
            current_pos[0] = x
        if y is not None:
            current_pos[1] = y
        if z is not None:
            current_pos[2] = z
        if a is not None:
            current_pos[3] = a
        if b is not None:
            current_pos[4] = b
        if c is not None:
            current_pos[5] = c
        self.client.move_linear(current_pos)

    def move_box_to_target(self, box: Box, target_pos: Vec2):
        """
        starting at safety height, approach the box, grab it, move to the dropoff location and
        place the box qat it's desired location
        :param box: the box to grab
        :param target_pos: target postion to place it
        :return:
        """
        assert self.position == CurrentPostion.PICK_UP, "needs to be at pickup location for picking up packet"
        print(f"approaching box at X:{box.center.x} Y: {box.center.y}")
        print(f"target height is: {box.height}")
        self.client.open_gripper()  # todo: check if we need to wait here
        self.go_to(x=box.center.x, y=box.center.y, z=box.height)
        self.client.close_gripper()
        self.go_to(z=SAFETY_HEIGHT)
        print(f"gripped box, moving to dropoff, dropping at X:{target_pos.x} Y:{target_pos.y}")
        self.move_to_dropoff()
        self.go_to(x=target_pos.x, y=target_pos.y)
        self.go_to(z=box.height)
        self.client.open_gripper()
        self.go_to(z=SAFETY_HEIGHT)
        self.move_to_pickup()
