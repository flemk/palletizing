# Description: This script demonstrates how to connect to PALLOC via a network socket and fetch data.
#              It serves as a template for users to implement their own processing code.
#              The script is designed to minimize dependencies.
import tkinter as tk
from tkinter import Toplevel, PhotoImage, Canvas
import base64
import socket
import time
import math
import select
import json
from threading import Thread, current_thread
# If the Pillow library is not installed, run the following command: "pip install pillow"
from PIL import Image, ImageDraw, ImageTk, ImageColor

# Configuration
DEFAULT_IP_ADDRESS = '192.168.136.160'  # IP address
PORT = 14158  # Port
JOB = 1  # Job number
ADJUST_EXPOSURE_MESSAGE = f'{{"name": "Job.Image.Acquire", "job": {JOB}}}'
ADJUST_EXPOSURE_ON = True  # Call AdjustExposure before Locate call
LOCATE_FIRST_MESSAGE = f'{{"name": "Run.Locate", "job": {JOB}}}'
LOCATE_NEXT_MESSAGE = f'{{"name": "Run.Locate", "job": {JOB}, "match": "next"}}'

DISABLE_CHECK_WITHIN_TOP_LAYER_MESSAGE = f'{{"name": "Job.Property.Set", "key": "locators[{JOB}].check_within_top_layer", "value": 0}}'
DISABLE_CHECK_COMMON_BOX_DIMENSIONS_MESSAGE = f'{{"name": "Job.Property.Set", "key": "locators[{JOB}].allow_mixed_box_dimensions", "value": 1}}'
DISABLE_CHECK_OVERLAP_MESSAGE = f'{{"name": "Job.Property.Set", "key": "locators[{JOB}].check_overlap", "value": 0}}'
DISABLE_GENERAL_ROTATION_MESSAGE = f'{{"name": "Job.Property.Set", "key": "locators[{JOB}].top_layer_rotation_mode", "value": 0}}'

GET_MATCH_DATA_MESSAGE = f'{{"name": "Run.Property.Get", "key": "current_match"}}'
GET_COLOR_IMAGE_MESSAGE = f'{{"name": "Run.Property.Get", "key": "color_image"}}'
GET_DEPTH_IMAGE_MESSAGE = f'{{"name": "Run.Property.Get", "key": "depth_image"}}'
TIME_OUT = 60  # Timeout in seconds
DELAY = 100  # Delay in milliseconds between each Locate call
BUFFER_SIZE = 1024  # Buffer size for socket communication


# Actual Program
class App:
    def __init__(self, master):
        
        # GUI configuration
        self.master = master
        self.image_window = None
        self.image_label = None
        self.first_run = True
        self.master.title("Run PALLOC")

        self.run = tk.BooleanVar()
        self.frame = tk.Frame(self.master)
        self.frame.pack(fill=tk.BOTH, expand=True)

        self.bottom_frame = tk.Frame(self.frame)
        self.bottom_frame.pack(side=tk.BOTTOM, fill=tk.X)

        self.toggle_switch = tk.Checkbutton(self.bottom_frame, text="", variable=self.run, command=self.toggle_run)
        self.toggle_switch.pack(side=tk.LEFT)

        self.run_once_button = tk.Button(self.bottom_frame, text="Run", command=self.run_once)
        self.run_once_button.pack(side=tk.LEFT)

        self.ip_entry = tk.Entry(self.bottom_frame)
        self.ip_entry.insert(0, DEFAULT_IP_ADDRESS)
        self.ip_entry.pack(side=tk.RIGHT)

        self.ip_label = tk.Label(self.bottom_frame, text="IP Address:")
        self.ip_label.pack(side=tk.RIGHT)

        self.text_box = tk.Text(self.frame)
        self.text_box.pack(fill=tk.BOTH, expand=True, side=tk.TOP)
        
    def toggle_run(self):
        # Called when Run toggle is pressed
        if self.run.get():
            ip = self.ip_entry.get()
            self.thread = Thread(target=self.run_loop, args=(ip,))
            self.thread.start()

    def run_once(self):
        # Called when Run Once button is pressed
        ip = self.ip_entry.get()
        self.thread = Thread(target=self.run_loop, args=(ip, True))
        self.thread.start()

    def print_to_text_box(self, text):
        # Print text to GUI
        self.text_box.insert(tk.END, text + '\n')
        self.text_box.see(tk.END)  # Auto-scroll to the bottom

    def connect(self, ip):
        # Make a connection to PALLOC via network socket
        my_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        my_socket.settimeout(TIME_OUT)
        self.print_to_text_box("")  # Blank row
        self.print_to_text_box("Attempting to establish connection...")
        my_socket.connect((ip, PORT))
        self.print_to_text_box("Connection established.")
        return my_socket

    def disconnect(self, my_socket):
        # Disconnect the network socket
        if my_socket:
            my_socket.close()
            self.print_to_text_box("Connection closed.")
            my_socket = None

    def setup_palloc(self, my_socket):
        # Perform any setup needed for PALLOC
        self.print_to_text_box("Fist image acquisition, do setup..")
        self.send_and_receive(my_socket, DISABLE_CHECK_WITHIN_TOP_LAYER_MESSAGE)
        self.send_and_receive(my_socket, DISABLE_CHECK_COMMON_BOX_DIMENSIONS_MESSAGE)
        self.send_and_receive(my_socket, DISABLE_CHECK_OVERLAP_MESSAGE)
        self.send_and_receive(my_socket, DISABLE_GENERAL_ROTATION_MESSAGE)
        self.print_to_text_box("")  # Blank row


    def run_loop(self, ip, run_once=False):
        # Thread running as long as the Run toggle is set.
        my_socket = None
        try:
            # Continuously sending messages to PALLOC
            while self.run.get() and current_thread() == self.thread or run_once:
                self.run_once_button.config(state=tk.DISABLED)
                try:
                    if my_socket is None:
                        my_socket = self.connect(ip)

                    self.print_to_text_box("")  # Blank row
                    if self.first_run:
                        self.setup_palloc(my_socket)
                        self.first_run = False
                    self.print_to_text_box("Acquiring image and fetching data...")
                    if ADJUST_EXPOSURE_ON:
                        self.send_and_receive(my_socket, ADJUST_EXPOSURE_MESSAGE)
                    self.fetch_palloc_data(my_socket)
                except socket.timeout:
                    self.print_to_text_box("Connection attempt abandoned due to timeout")
                    self.disconnect(my_socket)
                except (ConnectionRefusedError, ConnectionError):
                    self.print_to_text_box("Connection failed. Retrying...")
                    self.disconnect(my_socket)
                    time.sleep(1)
                else:
                    if run_once:
                        break
                    time.sleep(max(100, DELAY) / 1000)  # converting delay to seconds
            else:
                self.disconnect(my_socket)
        except (RuntimeError):
            # This exception might come after the window is closed...
            # Cleanup and exit
            if my_socket:
                my_socket.close()
                
        self.run_once_button.config(state=tk.NORMAL)


    def receive_data(self, my_socket):
        data = b''
        while True:
            # Use select to check if data is available to read
            ready = select.select([my_socket], [], [], 0.05)
            if ready[0] or not data:
                chunk = my_socket.recv(BUFFER_SIZE)
                if not chunk:
                    break
                data += chunk
            else:
                break  # No data available, exit the loop
        return data

    def send_and_receive(self, my_socket, message, truncate_length=65):
        self.print_to_text_box(f'Sending: {message}')
        my_socket.sendall(message.encode())
        feedback = self.receive_data(my_socket)
        feedback_str = feedback.decode('latin-1')  # Using 'latin-1' to avoid UnicodeDecodeError
        truncated_feedback = feedback_str if len(feedback_str) <= truncate_length else feedback_str[:truncate_length] + '...'
        self.print_to_text_box(f"Received: {truncated_feedback}")
        feedback_dict = json.loads(feedback_str)
        return feedback_dict
    

    def draw_rotated_rectangle(self, draw, x, y, width, height, rotation, outline="red", width_line=1):
        # Calculate the coordinates of the corners based on the center point
        corners = [
            (x - width / 2, y - height / 2),  # Top-left corner
            (x + width / 2, y - height / 2),  # Top-right corner
            (x + width / 2, y + height / 2),  # Bottom-right corner
            (x - width / 2, y + height / 2)   # Bottom-left corner
        ]
        
        # Apply rotation to each corner
        rotated_corners = []
        for corner in corners:
            dx = corner[0] - x
            dy = corner[1] - y
            new_x = x + (dx * math.cos(rotation) - dy * math.sin(rotation))
            new_y = y + (dx * math.sin(rotation) + dy * math.cos(rotation))
            rotated_corners.append((new_x, new_y))

        # Draw the rotated rectangle as a polygon without filling
        draw.polygon(rotated_corners, outline=outline, width=width_line)
    

    def show_image(self, match_data, base64_image_data):
        # Decode the base64 image data
        image_data = base64.b64decode(base64_image_data)
        
        # Create a PhotoImage object
        photo = PhotoImage(data=base64_image_data)

        if self.image_window is None or not self.image_window.winfo_exists():
            # Create a new window if it doesn't exist
            self.image_window = Toplevel(self.master)
            self.image_window.title("PALLOC Image")

            # Create a Canvas to display the image and draw rectangles
            self.canvas = Canvas(self.image_window, width=photo.width(), height=photo.height())
            self.canvas.pack()

        # Display the image on the Canvas
        self.canvas.create_image(0, 0, anchor=tk.NW, image=photo)
        self.canvas.image = photo  # Keep a reference to avoid garbage collection

        # Define a list of colors to cycle through
        colors = ["red", "green", "blue", "orange", "purple", "cyan", "magenta", "yellow", "brown", "pink"]
        
        # Create a new image with the same size as the canvas
        canvas_image = Image.new("RGBA", (photo.width(), photo.height()), (0, 0, 0, 0))

        # Draw rectangles and regions for each match
        for match_id, match_info in match_data.items():
            # Create a temporary image for blending each region
            temp_image = Image.new("RGBA", (photo.width(), photo.height()), (0, 0, 0, 0))
            temp_draw = ImageDraw.Draw(temp_image, "RGBA")

            # Select a color based on the match_id
            color = colors[(match_id - 1) % len(colors)]
            rgba_color = ImageColor.getrgb(color) + (100,)  # Convert to RGBA with alpha

            bbox = match_info["bbox"]["rectangle"]
            x = bbox["x"]
            y = bbox["y"]
            width = bbox["width"]
            height = bbox["height"]
            rotation = bbox["rotation"]
            self.draw_rotated_rectangle(temp_draw, x, y, width, height, rotation, outline=color)

            # Draw regions for each match
            region = match_info["bbox"]["region"]
            segmentsXStart = region["segmentsXStart"]
            segmentsXStop = region["segmentsXStop"]
            segmentsY = region["segmentsY"]
            for start, stop, y in zip(segmentsXStart, segmentsXStop, segmentsY):
                for i in range(start, stop):
                    # Draw the line with transparency on the temporary image
                    temp_draw.line((i, y, i + 1, y), fill=rgba_color, width=1)

            # Composite the temporary image onto the canvas image
            canvas_image = Image.alpha_composite(canvas_image, temp_image)

        # Convert the canvas image to PhotoImage and display it
        overlay_image = ImageTk.PhotoImage(canvas_image)
        self.canvas.create_image(0, 0, anchor=tk.NW, image=overlay_image)
        self.canvas.overlay_image = overlay_image  # Keep a reference to avoid garbage collection

    def fetch_palloc_data(self, my_socket):
        # Fetch data from PALLOC
        first = True
        match_data = dict()

        while True:
            try:
                if first:
                    locate_message = LOCATE_FIRST_MESSAGE
                else:
                    locate_message = LOCATE_NEXT_MESSAGE

                # Fetch data from PALLOC
                locate_response = self.send_and_receive(my_socket, locate_message)
                replay = locate_response["name"]

                if replay == "Run.Locate.Error":
                    self.print_to_text_box(f"Could not locate any objects in the image!")
                    return

                match = locate_response["match"]
                matches = locate_response["matches"]

                if first:
                    first = False
                    color_image_response = self.send_and_receive(my_socket, GET_COLOR_IMAGE_MESSAGE)
                    color_image = color_image_response.get("value", None)
                    if color_image is None or color_image == "":
                        self.print_to_text_box(f"Failed to fetch color image from PALLOC")
                        return
                    
                feedback_dict = self.send_and_receive(my_socket, GET_MATCH_DATA_MESSAGE)
                match_data[match] = feedback_dict.get("value", None)

                if match == matches:
                    break
                
            except json.JSONDecodeError:
                self.print_to_text_box(f"Failed to fetch data from PALLOC")
                return

        self.print_to_text_box(f"Image and match data fetched!")

        # Process the match data
        self.process_match_data(match_data, color_image)

    
    def process_match_data(self, match_data, color_image):
        # Put your processing code here...
        
        # Task 1:
        # For each match, find its real world top side coverage represented as a new
        # rectangle with position, size, and rotation. Suggested data to use is:
        #   * 2D bounding box from deep neural network provided at: match_data[1..n]["bbox"]["rectangle"]
        #   * Region given as (run length encoded segments) pixels in 3D space that
        #     lie within the match plane estimate and are confined by the bounding box.
        #     Region is provided at: match_data[1..n]["bbox"]["region"]
        #
        # Note:
        # The bounding box and the region may overlap, making it challenging to
        # identify the pixels that belong to the top side of each match.
        
        # Task 2:
        # Correlate the derived 2D rectangles with the 3D bounding
        # boxes and prepare for providing correctly rotated pick positions.

        # Task 3:
        # Implement a placement algorithm that places the boxes in a 
        # packing pattern.

        # Task 4:
        # ...
        
        self.show_image(match_data, color_image)

if __name__ == '__main__':
    # Construct GUI and run
    root = tk.Tk()
    app = App(root)
    root.mainloop()