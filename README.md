# Team Ctrl + Alt + Elite at the SICK Solution Hackathon 2024
In this repository the code produced by the Team "Ctrl + Alt + Elite" at the SICK Solution Hackathon 2024 is collected.

The team members were:
- Andi, aka anp369
- Carl, aka Leesment
- Franz, aka flemk
- Jonatan, aka Lophtix8

This README aims to give a brief overview of the algorithm for corner detection and rectangle fitting.

You can find the slides of the pitch in `doc/slides.pdf`.

Also since the code was created during a Hackathon, the code quality is relatable messy - sorry.

> This repository contains the [cri](https://github.com/jloyd237/cri) repository by jloyd237 in `/cri` and was used to establish a communication to the ABB robot.

## Algorithm idea
1. Find the intersections (overlapping) of the (given) bounding boxes (given by the neural network on the SICK Visionary S camera)
2. Find the corners of the (rotated) box:
    - Top and bottom corners X coordinates equal the average (center) on the minimal or maximal Y line
    - Left and right corners equal to the left / right-most pixel found
3. Do not use areas where overlapping occurs. If there are corners detected, calculate / reconstruct them from other "valid" / good corner coordinates using trigonometry
4. Since the four detected corner points do not construct a perfect rectangle (angles do not equal 90 deg) the algorithm needs creates a bounding rectangle which is perfect:
    - This is the rectangle with minimal area that contains all calculated corner points
    - Extension of this idea could be: The minimal rectangle that contains all pixel points
5. Using affine transforms to draw the rotated rectangle on the image

## Other discussed ideas
- Another idea we discussed was using a gradient descent procedure:
    - Start with the original (neural network) bounding box
    - Find the smallest possible rectangle that contains all pixel points (colors) by rotating
        - "Smallest" meaning here: Minimizing the area which is not colored / detected as box
    - Tackling overlapping:
        - Eiter: Omitting overlapped areas entirely (gradient descent should still find optimal solution)
        - Or: Introducing weights, where pixels inside overlapping areas are not weighted / considered as much as "clear cases"

## Additional features
- We added a checkpoint functionality to save images / data from the camera locally, to not always connect to the camera and fetch new data. Decreasing testing time.

## File overview
- `box.py`: Interface for defining a box and sorting a list of boxes by size  
- `robot_interaction.py`: Code for interacting with the robot   
- `run_palloc.py`: Code for interacting with the camera and doing box detection
