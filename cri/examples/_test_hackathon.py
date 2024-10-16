with AsyncRobot(SyncRobot(ABBController(ip='192.168.136.44', port=5000))) as robot:
    # For testing in RobotStudio simulator
    #    with AsyncRobot(SyncRobot(ABBController(ip='127.0.0.1', port=5000))) as robot:
    # Set TCP, linear speed,  angular speed and coordinate frame
    robot.tcp = (0, 0, 89.1, 0, 0, 0)
    robot.linear_speed = 20  # mm/s
    robot.angular_speed = 10
    robot.coord_frame = work_frame

    # Display robot info
    print("Robot info: {}".format(robot.info))

    # Display initial joint angles
    print("Initial joint angles: {}".format(robot.joint_angles))

    # Display initial pose in work frame
    print("Initial pose in work frame: {}".format(robot.pose))